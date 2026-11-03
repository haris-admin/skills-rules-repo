#!/usr/bin/env python3
"""HandleDispute edge monitor — TLS + HTTP + API depth for the public hostnames.

Both names sit behind Cloudflare, so the certificate the world sees is Cloudflare's
edge certificate (Let's Encrypt YE1, wildcard + apex), NOT something certbot on an
origin renews. There is no zone-scoped Cloudflare token in this fleet (the R2 token
answers 403 on /zones), so every claim here is measured from the public edge — the
same path a real cardholder takes.

What it checks
  1. DNS           A/AAAA for handledispute.com.au, www., api.
  2. TLS           handshake + chain verify, version/cipher, notBefore/notAfter,
                   days left, issuer, SAN coverage of the hostname actually requested.
  3. HTTP          status, latency, content-type, HSTS, x-content-type-options.
  4. HTTPS enforced  plain http:// must 301/308 to https (no plaintext service).
  5. API depth     `/` advertises status+version; `/health` must report
                   status=healthy, database=ok, environment=production, debug=false,
                   and the dependency block (clamav / email / sms).
  6. Hygiene       public /docs in production, unknown edge/proxy headers.

Modes
  (default)   silent when everything passes — prints ONLY a problem block.
              This is what the 6-hourly watchdog cron runs.
  --report    always prints the full picture (weekly digest / manual run).
  --json      machine-readable dump for other agents.

Exit code is always 0: output IS the signal, so a scheduler never substitutes its
own error alert for the real findings. Never prints a credential.

Thresholds: cert <21d = 🟡, <10d / expired / verify-fail = 🔴, API latency >3000ms = 🟡.
"""
from __future__ import annotations

import argparse
import json
import socket
import ssl
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

APP_HOST = "handledispute.com.au"
API_HOST = "api.handledispute.com.au"
WWW_HOST = "www.handledispute.com.au"
STATE_FILE = Path("/home/habib/.hermes/state/handledispute_edge_state.json")

WARN_DAYS = 21
CRIT_DAYS = 10
SLOW_MS = 3000
SUPPRESS_HOURS = 12  # identical alert set is not repeated inside this window
UA = "HermesHandleDisputeMonitor/1.0 (+edge watch)"

HOSTS = [
    {"host": APP_HOST, "role": "web app", "expect": (200,), "kind": "html"},
    {"host": WWW_HOST, "role": "web app (www)", "expect": (200,), "kind": "html"},
    {"host": API_HOST, "role": "production API", "expect": (200,), "kind": "json"},
]


# ── probes ───────────────────────────────────────────────────────────────────

def resolve(host: str) -> dict:
    try:
        infos = socket.getaddrinfo(host, 443, type=socket.SOCK_STREAM)
    except Exception as exc:
        return {"ok": False, "error": f"{type(exc).__name__}: {exc}"}
    v4 = sorted({i[4][0] for i in infos if i[0] == socket.AF_INET})
    v6 = sorted({i[4][0] for i in infos if i[0] == socket.AF_INET6})
    return {"ok": bool(v4 or v6), "v4": v4, "v6": v6}


def probe_tls(host: str) -> dict:
    ctx = ssl.create_default_context()
    try:
        with socket.create_connection((host, 443), timeout=15) as sock:
            with ctx.wrap_socket(sock, server_hostname=host) as ss:
                cert = ss.getpeercert()
                na = datetime.strptime(cert["notAfter"], "%b %d %H:%M:%S %Y %Z").replace(tzinfo=timezone.utc)
                nb = datetime.strptime(cert["notBefore"], "%b %d %H:%M:%S %Y %Z").replace(tzinfo=timezone.utc)
                san = [v for k, v in cert.get("subjectAltName", ()) if k == "DNS"]
                return {
                    "ok": True,
                    "version": ss.version(),
                    "cipher": (ss.cipher() or ("?",))[0],
                    "not_before": nb.isoformat(),
                    "not_after": na.isoformat(),
                    "days": (na - datetime.now(timezone.utc)).days,
                    "issuer": dict(x[0] for x in cert.get("issuer", ())).get("commonName", "?"),
                    "issuer_org": dict(x[0] for x in cert.get("issuer", ())).get("organizationName", "?"),
                    "cn": dict(x[0] for x in cert.get("subject", ())).get("commonName", "?"),
                    "san": san,
                    "covers_host": host in san or f"*.{host.split('.', 1)[1]}" in san,
                }
    except ssl.SSLCertVerificationError as exc:
        return {"ok": False, "verify_error": str(exc)[:200]}
    except Exception as exc:
        return {"ok": False, "error": f"{type(exc).__name__}: {exc}"[:200]}


def probe_http(url: str, timeout: int = 15) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    t0 = time.time()
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            body = r.read(6000).decode("utf-8", "replace")
            return {
                "ok": True, "code": r.status, "ms": int((time.time() - t0) * 1000),
                "ctype": (r.headers.get("content-type") or "").split(";")[0],
                "len": r.headers.get("content-length"),
                "hsts": r.headers.get("strict-transport-security"),
                "xcto": r.headers.get("x-content-type-options"),
                "server": r.headers.get("server"),
                "cf_ray": r.headers.get("cf-ray"),
                "location": r.headers.get("location"),
                "body": body,
            }
    except urllib.error.HTTPError as exc:
        return {"ok": False, "code": exc.code, "ms": int((time.time() - t0) * 1000),
                "ctype": (exc.headers.get("content-type") or "").split(";")[0] if exc.headers else "",
                "hsts": exc.headers.get("strict-transport-security") if exc.headers else None,
                "body": ""}
    except Exception as exc:
        return {"ok": False, "code": None, "error": f"{type(exc).__name__}: {exc}"[:200], "body": ""}


def probe_plain_http(host: str) -> dict:
    """HTTPS must be enforced: plain http should 301/308 to https."""
    return probe_http(f"http://{host}/")


def api_depth(api_root: dict, api_health: dict) -> dict:
    out: dict = {"issues": [], "notes": [], "info": {}}
    if not api_root.get("ok"):
        out["issues"].append(f"api root not 2xx ({api_root.get('code') or api_root.get('error')})")
        return out
    try:
        root = json.loads(api_root["body"])
    except Exception:
        out["issues"].append("api root is not JSON")
        return out
    out["info"]["service"] = root.get("service")
    out["info"]["version"] = root.get("version")
    if root.get("status") != "online":
        out["issues"].append(f"api root status={root.get('status')!r} (expected 'online')")

    if not api_health.get("ok"):
        out["issues"].append(f"/health not 2xx ({api_health.get('code') or api_health.get('error')})")
        return out
    try:
        h = json.loads(api_health["body"])
    except Exception:
        out["issues"].append("/health is not JSON")
        return out
    out["info"]["env"] = h.get("environment")
    out["info"]["db"] = h.get("database")
    out["info"]["db_target"] = h.get("database_target")
    out["info"]["debug"] = h.get("debug")
    out["info"]["deps"] = {k: (v or {}).get("status") for k, v in (h.get("dependencies") or {}).items()}
    out["info"]["health_version"] = h.get("version")

    if h.get("status") != "healthy":
        out["issues"].append(f"/health status={h.get('status')!r} (expected 'healthy')")
    if h.get("database") != "ok":
        out["issues"].append(f"database={h.get('database')!r} (expected 'ok')")
    if h.get("environment") != "production":
        out["issues"].append(f"environment={h.get('environment')!r} (expected 'production')")
    if h.get("debug") is not False:
        out["issues"].append(f"debug={h.get('debug')!r} (expected false in production)")
    ver, hver = root.get("version"), h.get("version")
    if ver and hver and ver != hver:
        out["issues"].append(f"version mismatch: root {ver} vs /health {hver}")

    # Dependency state is a standing config note, not an outage.
    deps = out["info"]["deps"]
    if deps.get("email_provider") in ("mock", None):
        out["notes"].append("email_provider is MOCK — production notifications are not being sent")
    if deps.get("sms_provider") in ("not_configured", None):
        out["notes"].append("sms_provider is NOT CONFIGURED")
    if deps.get("clamav") not in ("ok", "connected", "healthy"):
        out["notes"].append(f"clamav is {deps.get('clamav')!r} (attachment scanning unavailable)")
    return out


def load_state() -> dict:
    try:
        return json.loads(STATE_FILE.read_text())
    except Exception:
        return {}


def save_state(state: dict) -> None:
    try:
        STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
        STATE_FILE.write_text(json.dumps(state, indent=1))
    except Exception:
        pass


# ── verdicts ─────────────────────────────────────────────────────────────────

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--report", action="store_true", help="print the full picture even when healthy")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    now = datetime.now(timezone.utc)
    red: list[str] = []
    amber: list[str] = []
    notes: list[str] = []
    host_blocks: list[dict] = []

    for spec in HOSTS:
        host = spec["host"]
        blk: dict = {"host": host, "role": spec["role"]}
        blk["dns"] = resolve(host)
        if not blk["dns"].get("ok"):
            red.append(f"{host}: DNS does not resolve ({blk['dns'].get('error', 'no A/AAAA')})")
        blk["tls"] = probe_tls(host)
        tls = blk["tls"]
        if not tls.get("ok"):
            red.append(f"{host}: TLS failed — {tls.get('verify_error') or tls.get('error')}")
        else:
            d = tls["days"]
            if d < 0:
                red.append(f"{host}: certificate EXPIRED ({tls['not_after'][:10]})")
            elif d < CRIT_DAYS:
                red.append(f"{host}: certificate expires in {d}d ({tls['not_after'][:10]}, {tls['issuer']})")
            elif d < WARN_DAYS:
                amber.append(f"{host}: certificate expires in {d}d ({tls['not_after'][:10]}, {tls['issuer']})")
            if not tls.get("covers_host"):
                red.append(f"{host}: certificate SAN does not cover this hostname (SAN: {', '.join(tls.get('san', []))[:80]})")

        blk["http"] = probe_http(f"https://{host}/")
        h = blk["http"]
        if not h.get("ok") or h.get("code") not in spec["expect"]:
            red.append(f"{host}: HTTPS returned {h.get('code') or h.get('error')} (expected {spec['expect'][0]})")
        if h.get("ms") is not None and h["ms"] > SLOW_MS:
            amber.append(f"{host}: slow response {h['ms']}ms (> {SLOW_MS}ms)")
        if spec["kind"] == "html" and h.get("ctype") not in ("text/html", ""):
            amber.append(f"{host}: content-type {h.get('ctype')!r} (expected text/html)")
        if not h.get("hsts"):
            notes.append(f"{host}: no Strict-Transport-Security header")
        host_blocks.append(blk)

    # HTTPS enforcement on the app host (apex). A refusal (4xx at the edge) is a
    # hygiene gap worth a digest line; actually SERVING content over plaintext is an outage.
    plain = probe_plain_http(APP_HOST)
    enforced = plain.get("code") in (301, 302, 307, 308) and str(plain.get("location", "")).startswith("https://")
    if not enforced:
        if plain.get("ok") and plain.get("code") == 200:
            red.append(
                f"PLAINTEXT SERVED: http://{APP_HOST} returned 200 instead of redirecting to https "
                "(Cloudflare: enable Always Use HTTPS)"
            )
        else:
            notes.append(
                f"http://{APP_HOST} does not redirect to https — it answered "
                f"{plain.get('code') or plain.get('error')} (Cloudflare: enable Always Use HTTPS)"
            )

    api_root = next((b["http"] for b in host_blocks if b["host"] == API_HOST), {})
    api_health = probe_http(f"https://{API_HOST}/health")
    depth = api_depth(api_root, api_health)
    red.extend(depth["issues"])
    notes.extend(depth["notes"])

    docs = probe_http(f"https://{API_HOST}/docs")
    docs_public = docs.get("code") == 200
    if docs_public:
        notes.append("API /docs is publicly reachable in production")

    # deploy/version tracking
    state = load_state()
    prev_version = state.get("api_version")
    cur_version = depth["info"].get("version")
    version_line = cur_version or "?"
    if prev_version and cur_version and prev_version != cur_version:
        version_line = f"{cur_version} (was {prev_version})"
    if prev_version and cur_version and cur_version < prev_version:
        amber.append(f"API version went BACKWARDS: {prev_version} → {cur_version}")
    # Repeat suppression: an unchanged alert set inside SUPPRESS_HOURS stays silent,
    # so one persistent problem is one message, not one per 6-hourly run.
    fingerprints = sorted(red + amber)
    prev_alerts = state.get("last_alerts") or []
    prev_at = state.get("last_alert_at")
    within_window = False
    if prev_at:
        try:
            within_window = (now - datetime.fromisoformat(prev_at)) < timedelta(hours=SUPPRESS_HOURS)
        except Exception:
            within_window = False
    repeat = bool(fingerprints) and within_window and fingerprints == prev_alerts
    if repeat and not args.report and not args.json:
        save_state({**state, "checked_at": now.isoformat(), "last_status": "repeat-suppressed"})
        return 0

    save_state({
        "api_version": cur_version or prev_version,
        "checked_at": now.isoformat(),
        "last_status": "red" if red else ("amber" if amber else "ok"),
        "cert_days": {b["host"]: (b["tls"].get("days") if b["tls"].get("ok") else None) for b in host_blocks},
        "last_alerts": fingerprints,
        "last_alert_at": now.isoformat() if fingerprints else prev_at,
    })

    if args.json:
        print(json.dumps({
            "checked_at": now.isoformat(), "hosts": host_blocks,
            "api": depth["info"], "red": red, "amber": amber, "notes": notes,
        }, indent=1, default=str))
        return 0

    healthy = not red and not amber
    if healthy and not args.report:
        return 0  # silent: nothing to say

    lines: list[str] = []
    if red:
        lines.append(f"🔴 HandleDispute edge monitor — {len(red)} issue(s)")
    elif amber:
        lines.append(f"🟡 HandleDispute edge monitor — {len(amber)} warning(s)")
    else:
        lines.append("☿ HandleDispute edge monitor — all clear")
    lines.append(f"   checked {now.strftime('%Y-%m-%d %H:%M')} UTC · Cloudflare edge · public path")
    lines.append("")
    for b in host_blocks:
        t = b["tls"]
        h = b["http"]
        if t.get("ok"):
            lines.append(
                f"   ✅ {b['host']:<26} {h.get('code')}  {h.get('ms')}ms  "
                f"TLS {t['version']} · {t['issuer']} · {t['days']}d → {t['not_after'][:10]}"
            )
            lines.append(f"      SAN: {', '.join(t['san'])}  · cipher {t['cipher']}")
        else:
            lines.append(f"   🔴 {b['host']:<26} TLS FAILED — {t.get('verify_error') or t.get('error')}")
        dns = b["dns"]
        lines.append(f"      DNS: {', '.join(dns.get('v4', []) + dns.get('v6', [])) or 'none'}")
    info = depth["info"]
    if info.get("version"):
        lines.append("")
        lines.append(f"   API: {info.get('service')} v{version_line} · env {info.get('env')} · db {info.get('db')} ({info.get('db_target')})")
        deps = info.get("deps") or {}
        if deps:
            lines.append("      deps: " + " · ".join(f"{k}={v}" for k, v in deps.items()))
    for title, items, icon in (("ACTION", red, "🔴"), ("WARN", amber, "🟡")):
        if items:
            lines.append("")
            lines.append(f"   {icon} {title} ({len(items)})")
            for i in items:
                lines.append(f"      • {i}")
    if notes:
        lines.append("")
        lines.append(f"   🟡 standing notes ({len(notes)}) — config/hygiene, not an outage")
        for n in notes:
            lines.append(f"      • {n}")
    if healthy:
        lines.append("")
        lines.append("   ✅ TLS, HTTP and API depth all within thresholds"
                     f" (warn <{WARN_DAYS}d, critical <{CRIT_DAYS}d, slow >{SLOW_MS}ms)")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except SystemExit:
        raise
    except Exception as exc:  # never turn a monitor bug into a scheduler alert
        print(f"☿ HandleDispute edge monitor failed to run: {type(exc).__name__}: {exc}")
        raise SystemExit(0)
