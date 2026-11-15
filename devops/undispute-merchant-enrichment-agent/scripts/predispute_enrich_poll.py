#!/usr/bin/env python3
"""Pre-Dispute merchant-enrichment — worker poll tick (claim only).

Spec: docs/hermes-agent-instructions.md (haris-admin/undispute-scheme-neutral-resolution)
+ skill `undispute-merchant-enrichment-agent` (platform rebranded to Pre-Dispute, v0.200.x).

This script performs ONLY the cheap, idempotent half of the loop: it claims at
most one job and reports it. It never researches, never completes, never fails a
job, and never contacts the merchant. The agent does that, guided by the skill.

Configuration (all three PLUTO_HERMES_PREDISPUTE_* come from the Hermes env file;
the backend holds the same secret as HERMES_AGENT_API_KEY):

  PLUTO_HERMES_PREDISPUTE_BASE_URL        API origin, no trailing slash, no /api/v1
                                          (HTTPS in production; private http:// allowed in non-production)
  PLUTO_HERMES_PREDISPUTE_AGENT_API_KEY   scoped Hermes credential
  PLUTO_HERMES_PREDISPUTE_INTERVAL        positive whole-number seconds

Contract gate: the worker REFUSES TO START (exit 3) unless all three validate -
no default values, no direct database access. A refusal is a configuration state,
not a scheduler fault: the shell wrapper maps exit 3 to 0 so it cannot alert-storm.

NON-PRODUCTION EXCEPTION (owner-directed 2026-09-22; widened to match the amended
contract 2026-09-28). Plaintext http:// is allowed ONLY with an explicit operator
opt-in AND only when the host is PRIVATE - never over a public network:

    PLUTO_HERMES_PREDISPUTE_ALLOW_INSECURE_LOCAL=1

"Private" means loopback (127.0.0.1 / localhost / ::1), an RFC1918 or link-local
address (e.g. http://192.168.50.210:8008), an IPv6 ULA, or a private-only TLD
(.local / .internal / .lan). Production always requires HTTPS, and any PUBLIC host
on http:// is still refused, so the flag can never silently permit plaintext over a
public network. The override is logged (`insecure_override`) and reported as an FYI
by the 12h report. Unset it in production.

Logging contract: never log headers, the API key, the lease token, the request
body, or the response body - only status/category and opaque run/job identifiers.

Flags
  --quiet   watchdog mode for a no_agent cron: print NOTHING when there is no
            work (or when a job is already in flight); still prints a claim or a
            claim failure. Empty stdout means the cron delivers nothing.

Exit codes:  0 = no work (HTTP 204) / busy / claim failed / transport error
            10 = a job was claimed (job + lease written to the state file)
             3 = refused to start (configuration is not contract-valid)
"""
from __future__ import annotations

import ipaddress
import json
import os
import pathlib
import sys
import urllib.error
import urllib.request
import uuid
from datetime import datetime, timedelta, timezone

ENV_FILE = pathlib.Path("/mnt/c/Users/habib/.hermes/.env")
STAGING_STATE_FILE = pathlib.Path("/home/habib/.hermes/cache/scratch/predispute_worker_state.json")
STAGING_LOG_FILE = pathlib.Path("/home/habib/.hermes/state/predispute_worker_log.jsonl")  # append-only, feeds the 12h report
PROD_STATE_FILE = pathlib.Path("/home/habib/.hermes/cache/scratch/predispute_prod_worker_state.json")
PROD_LOG_FILE = pathlib.Path("/home/habib/.hermes/state/predispute_prod_worker_log.jsonl")
STATE_FILE = STAGING_STATE_FILE
LOG_FILE = STAGING_LOG_FILE

CLAIM_PATH = "/api/v1/agent/merchant-enrichment/claim"
BASE_VAR = "PLUTO_HERMES_PREDISPUTE_BASE_URL"
KEY_NAMES = ("PLUTO_HERMES_HANDLEDISPUTE_AGENT_API_KEY",
             "PLUTO_HERMES_PREDISPUTE_AGENT_API_KEY",
             "PREDISPUTE_AGENT_API_KEY",
             "HERMES_AGENT_API_KEY")
PROD_BASE_DEFAULT = "https://api.handledispute.com.au"
INTERVAL_VAR = "PLUTO_HERMES_PREDISPUTE_INTERVAL"
ALLOW_INSECURE_VAR = "PLUTO_HERMES_PREDISPUTE_ALLOW_INSECURE_LOCAL"

# The owner renamed the lane variables PREDISPUTE -> HANDLEDISPUTE. The code below
# keeps the original names as canonical keys; each new name is aliased onto its
# predecessor at env-load time so either spelling (or both) resolves identically.
_ENV_ALIASES = (
    ("PLUTO_HERMES_PREDISPUTE_BASE_URL", "PLUTO_HERMES_HANDLEDISPUTE_BASE_URL"),
    ("PLUTO_HERMES_PREDISPUTE_AGENT_API_KEY", "PLUTO_HERMES_HANDLEDISPUTE_AGENT_API_KEY"),
    ("PLUTO_HERMES_PREDISPUTE_INTERVAL", "PLUTO_HERMES_HANDLEDISPUTE_INTERVAL"),
    ("PLUTO_HERMES_PREDISPUTE_ALLOW_INSECURE_LOCAL", "PLUTO_HERMES_HANDLEDISPUTE_ALLOW_INSECURE_LOCAL"),
)
LOOPBACK_HOSTS = {"127.0.0.1", "localhost", "::1", "[::1]"}
PRIVATE_HOST_SUFFIXES = (".local", ".internal", ".lan", ".home", ".test", ".localhost")


def is_private_host(host: str) -> bool:
    """True when the origin cannot be reached over a public network: loopback, an
    RFC1918 / link-local / IPv6-ULA address, or a private-only TLD. A public DNS
    name is never private. Guards the non-production plaintext exception."""
    h = (host or "").strip().strip("[]").lower()
    if not h:
        return False
    if h in LOOPBACK_HOSTS or h.endswith(PRIVATE_HOST_SUFFIXES):
        return True
    try:
        ip = ipaddress.ip_address(h)
    except ValueError:
        return False
    return ip.is_loopback or ip.is_private or ip.is_link_local
TRUTHY = {"1", "true", "yes", "on"}
STALE_AFTER = timedelta(minutes=12)  # lease is 10 min; heartbeat every ~4 min
OVERRIDE_MARKER = pathlib.Path("/home/habib/.hermes/state/.predispute_insecure_override_day")

# The runbook's exact empty-queue info log. The --quiet watchdog stays silent
# on an empty queue by design (an empty stdout delivers nothing), so this line
# is emitted only in full (non-quiet) mode.
EMPTY_QUEUE_LOG = "Pluto Hermes: job queue is empty; sleeping until next configured interval"


def _clean(value: str | None) -> str:
    """Strip CRLF/BOM/whitespace/quotes - the Windows .env is CRLF-terminated."""
    if value is None:
        return ""
    return value.replace("\r", "").replace("\ufeff", "").strip().strip('"').strip("'")


def load_env() -> dict[str, str]:
    """Resolve configuration: the process environment is authoritative (that is
    what "the Pluto runtime must have all three variables before it starts"
    means); the Hermes .env file fills in anything the runtime did not export."""
    out: dict[str, str] = {}
    if ENV_FILE.exists():
        for line in ENV_FILE.read_text(errors="replace").splitlines():
            s = line.strip().lstrip("\ufeff")
            if s and not s.startswith("#") and "=" in s:
                k, v = s.split("=", 1)
                out[k.strip()] = _clean(v)
    wanted = (*KEY_NAMES, BASE_VAR, INTERVAL_VAR, ALLOW_INSECURE_VAR,
              "PLUTO_HERMES_ACMA_BASE_URL", *(new for _, new in _ENV_ALIASES))
    for name in wanted:
        value = _clean(os.environ.get(name))
        if value:
            out[name] = value
    for old, new in _ENV_ALIASES:          # PREDISPUTE <- HANDLEDISPUTE rename
        if not out.get(old) and out.get(new):
            out[old] = out[new]
    return out


def agent_key(env: dict[str, str]) -> tuple[str, str]:
    for name in KEY_NAMES:
        if env.get(name):
            return name, env[name]
    return KEY_NAMES[0], ""


def host_of(base: str) -> str:
    """Host component of an origin, without credentials or port."""
    if "://" not in base:
        return ""
    netloc = base.split("://", 1)[1].split("/", 1)[0]
    netloc = netloc.split("@")[-1]
    if netloc.startswith("["):           # bracketed IPv6
        return netloc.split("]")[0].lower() + "]"
    return netloc.split(":")[0].lower()


def validate_config(env: dict[str, str]) -> tuple[str, str, int, str, bool]:
    """Contract validation. Returns (base, key, interval, "", insecure) or
    ("", "", 0, reason, False).

    Refusal conditions (contract): any variable missing, base URL not HTTPS, or
    interval not a positive whole number. The ONLY exception is the explicit,
    operator-set non-production opt-in that allows a plaintext PRIVATE origin
    (`PLUTO_HERMES_PREDISPUTE_ALLOW_INSECURE_LOCAL=1`) - loopback, RFC1918,
    link-local/ULA, or a private-only TLD. It never applies to a public host, so it
    cannot silently permit plaintext over a public network.
    """
    base = env.get(BASE_VAR, "")
    key_name, key = agent_key(env)
    interval_raw = env.get(INTERVAL_VAR, "")

    missing = [n for n, v in ((BASE_VAR, base), (key_name, key), (INTERVAL_VAR, interval_raw)) if not v]
    if missing:
        return "", "", 0, "missing required variable(s): " + ", ".join(missing), False

    insecure = False
    if not base.lower().startswith("https://"):
        scheme = base.split("://", 1)[0] if "://" in base else "none"
        opted_in = env.get(ALLOW_INSECURE_VAR, "").lower() in TRUTHY
        if opted_in and is_private_host(host_of(base)):
            insecure = True
        else:
            hint = "" if opted_in else f" (or set {ALLOW_INSECURE_VAR}=1 to allow a PRIVATE non-production origin)"
            return "", "", 0, (
                f"{BASE_VAR} must be an HTTPS origin (got scheme '{scheme}'); plaintext http:// is permitted in "
                f"non-production only for private local/development/staging infrastructure, never over a public "
                f"network{hint}"
            ), False
    if base.endswith("/"):
        return "", "", 0, f"{BASE_VAR} must not have a trailing slash", False
    if "/api/v1" in base:
        return "", "", 0, f"{BASE_VAR} must be the API origin only (must not include /api/v1)", False
    if not base.split("://", 1)[1].split("/", 1)[0]:
        return "", "", 0, f"{BASE_VAR} has no host", False
    if not interval_raw.isdigit() or int(interval_raw) <= 0:
        return "", "", 0, f"{INTERVAL_VAR} must be a positive whole number of seconds", False
    if any(ch.isspace() for ch in key):
        return "", "", 0, f"{key_name} must not contain whitespace", False

    return base, key, int(interval_raw), "", insecure


def resolve_acma_base(env: dict[str, str]) -> tuple[str, bool]:
    """ACMA is a separate service with its own local origin; the runbook's HTTPS
    rule governs PLUTO_HERMES_PREDISPUTE_BASE_URL and submitted result URLs."""
    configured = env.get("PLUTO_HERMES_ACMA_BASE_URL", "http://localhost:8009").rstrip("/")
    for candidate in (configured, "http://localhost:8009"):
        if _healthy(candidate):
            return candidate, True
    return configured, False


def _healthy(base: str) -> bool:
    try:
        with urllib.request.urlopen(base.rstrip("/") + "/health", timeout=5) as r:
            return r.status == 200
    except Exception:
        return False


def open_claim() -> dict | None:
    """A claim still inside its lease blocks a new one: exactly one job in flight."""
    if not STATE_FILE.exists():
        return None
    try:
        rec = json.loads(STATE_FILE.read_text())
    except Exception:
        return None
    if rec.get("status") != "job_claimed":
        return None
    stamp = rec.get("last_heartbeat_at") or rec.get("claimed_at") or ""
    try:
        age = datetime.now(timezone.utc) - datetime.fromisoformat(stamp)
    except Exception:
        return None
    return None if age > STALE_AFTER else rec


def post(url: str, payload: dict, headers: dict) -> tuple[int | str, str]:
    """POST and return (status, body). The response body is returned ONLY for a
    successful claim; error bodies and headers are drained and discarded so they
    can never reach a log line or a delivered message.

    A real User-Agent is mandatory: Cloudflare in front of the production API
    answers 403 to the default `Python-urllib/x.y` UA (same trap as CF error 1010),
    which looks exactly like an authentication failure.
    """
    body = json.dumps(payload).encode()
    req = urllib.request.Request(
        url, data=body,
        headers={"Content-Type": "application/json", "User-Agent": "HermesPreDisputeWorker/1.0", **headers},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return r.status, r.read().decode(errors="replace")
    except urllib.error.HTTPError as e:
        e.read()  # drain; never logged, never reported
        return e.code, ""
    except Exception as e:  # transport: never treated as success
        return "ERR", type(e).__name__


def classify(status: int | str) -> str:
    """Log-safe failure vocabulary (runbook few-shot scenario 3)."""
    if status == "ERR":
        return "transport_error"
    if status == 401:
        return "auth"
    if status == 409:
        return "conflict"
    if status == 422:
        return "validation"
    if status == 503:
        return "service_unavailable"
    if isinstance(status, int) and 500 <= status < 600:
        return "server_error"
    return f"http_{status}"


def _marker_read(path: pathlib.Path) -> str:
    try:
        return path.read_text().strip()
    except Exception:
        return ""


def _marker_write(path: pathlib.Path, value: str) -> None:
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(value)
    except Exception:
        pass


def log_event(event: str, **fields) -> None:
    """Append-only activity log that feeds the 12-hour report cron (state/ is not pruned)."""
    try:
        LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
        with LOG_FILE.open("a") as fh:
            fh.write(json.dumps({"ts": datetime.now(timezone.utc).isoformat(), "event": event, **fields}) + "\n")
    except Exception:
        pass


def human(obj: dict) -> str:
    """Telegram-ready rendering for the no_agent cron (stdout is delivered verbatim).

    Never echoes a response body, header, key or lease token."""
    s = obj.get("status")
    if s == "job_claimed":
        return ("\u263f Pre-Dispute queue \u2014 JOB CLAIMED\n"
                f"   merchant: {obj.get('merchant_name')} (ABN {obj.get('abn')})\n"
                f"   job: {obj.get('job_id')}\n"
                f"   lease expires: {obj.get('lease_expires_at')}\n"
                "   \u2192 enrichment worker is taking it now.")
    if s == "claim_failed":
        return ("\U0001f534 Pre-Dispute queue \u2014 CLAIM FAILED\n"
                f"   http {obj.get('http_status')} \u00b7 category {obj.get('category')} \u00b7 backend {obj.get('backend_base')}")
    if s == "refused":
        return ("\U0001f534 Pre-Dispute worker \u2014 REFUSED TO START (contract)\n"
                f"   {obj.get('reason')}")
    if s == "error":
        return f"\U0001f534 Pre-Dispute worker \u2014 {obj.get('reason')}"
    return ""


def apply_lane(lane: str) -> None:
    """Point the worker at a lane. `staging` (default) is unchanged behaviour.

    `prod` talks HTTPS-only to the public HandleDispute API with the production
    agent credential (HANDLEDISPUTE_AGENT_KEY) and keeps its claim state and
    activity log in separate files, so the two lanes can never share a lease or
    be mistaken for each other in a report.
    """
    global STATE_FILE, LOG_FILE, BASE_VAR, KEY_NAMES, ALLOW_INSECURE_VAR
    if lane != "prod":
        return
    STATE_FILE = PROD_STATE_FILE
    LOG_FILE = PROD_LOG_FILE
    BASE_VAR = "PLUTO_HERMES_PREDISPUTE_PROD_BASE_URL"
    KEY_NAMES = ("HANDLEDISPUTE_AGENT_KEY",)
    ALLOW_INSECURE_VAR = "PLUTO_HERMES_PREDISPUTE_PROD_ALLOW_INSECURE_LOCAL"  # must never be set for prod


def main() -> int:
    quiet = "--quiet" in sys.argv
    force = "--force" in sys.argv
    lane = "prod" if ("--prod" in sys.argv or "--lane=prod" in sys.argv) else "staging"
    apply_lane(lane)

    def emit(obj: dict, always: bool = False) -> None:
        if quiet:
            line = human(obj)
            if line:
                print(line)
            return
        print(json.dumps(obj, indent=2))

    env = load_env()
    if lane == "prod" and not env.get(BASE_VAR):
        # The production origin is a fixed public constant; a staging-style default
        # would silently point a prod worker at localhost, which is worse.
        env[BASE_VAR] = PROD_BASE_DEFAULT

    # ── Contract gate: refuse to start unless the configuration is valid ──────
    base, key, interval, reason, insecure = validate_config(env)
    if reason:
        # Record it (the 12h report surfaces refusals) and stay SILENT in
        # --quiet mode: this runs every 60s, so a printed banner would be an
        # alert storm. Nothing is printed -> the no_agent cron delivers nothing.
        log_event("refused", reason=reason)
        if not quiet:
            print(json.dumps({"status": "refused", "reason": reason}, indent=2))
        return 3

    if insecure:
        # Explicit non-production opt-in. Recorded at most ONCE PER UTC DAY: this
        # runs every 60s, and a per-tick event bloated the log to ~1,440 identical
        # rows/day (compacted 2026-09-23). The 12h report reads the opt-in from the
        # env file, so the state is still surfaced every run.
        day = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        if _marker_read(OVERRIDE_MARKER) != day:
            log_event("insecure_override", origin=f"http://{host_of(base)}", var=ALLOW_INSECURE_VAR, day=day)
            _marker_write(OVERRIDE_MARKER, day)
        if not quiet:
            print(f"Pluto Hermes: WARNING insecure non-prod override active ({ALLOW_INSECURE_VAR}=1, private origin http://{host_of(base)})")

    held = open_claim()
    if held and not force:
        emit({"status": "busy", "job_id": held.get("job", {}).get("job_id"), "claimed_at": held.get("claimed_at")})
        return 0

    worker_run_id = "mercury-predispute-" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "-" + uuid.uuid4().hex[:8]
    status, body = post(base + CLAIM_PATH, {"worker_run_id": worker_run_id}, {"X-Hermes-Agent-Key": key})

    if status == 204:
        if quiet:
            emit({"status": "no_work"})
        else:
            print(EMPTY_QUEUE_LOG)
        return 0
    if status != 200:
        # 401 / 409 / 422 / 5xx / transport: report the category and stop.
        # Never research or complete on a bad claim; never retry inside the cycle.
        category = classify(status)
        log_event("claim_failed", category=category, http_status=status, backend_base=base, run_id=worker_run_id)
        if quiet:
            emit({"status": "claim_failed", "http_status": status, "category": category, "backend_base": base, "worker_run_id": worker_run_id}, always=True)
        else:
            print(f"Pluto Hermes: claim failed; category={category}; run_id={worker_run_id}")
        return 0

    job = json.loads(body)
    acma_base, acma_ok = resolve_acma_base(env)
    now = datetime.now(timezone.utc)
    record = {
        "status": "job_claimed",
        "claimed_at": now.isoformat(),
        "last_heartbeat_at": now.isoformat(),
        "lease_expires_at": job.get("lease_expires_at"),
        "backend_base": base,
        "worker_run_id": worker_run_id,
        "key_name": KEY_NAMES[0],
        "job": job,
        "acma_base_usable": acma_base,
        "acma_reachable_from_wsl": acma_ok,
        "note": "submit acma_expires_at as null; heartbeat every ~4 min (lease = 10 min)",
    }
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps(record, indent=2))
    log_event("claimed", job_id=job.get("job_id"), merchant_name=job.get("merchant_name"), abn=job.get("abn"), origin_case_id=job.get("origin_case_id"), worker_run_id=worker_run_id)
    emit({"status": "job_claimed", "job_id": job.get("job_id"), "merchant_name": job.get("merchant_name"), "abn": job.get("abn"), "origin_case_id": job.get("origin_case_id"), "worker_run_id": worker_run_id, "lease_expires_at": job.get("lease_expires_at"), "state_file": str(STATE_FILE)}, always=True)
    return 10


if __name__ == "__main__":
    sys.exit(main())
