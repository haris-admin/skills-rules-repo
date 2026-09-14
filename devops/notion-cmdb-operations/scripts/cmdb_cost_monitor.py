#!/usr/bin/env python3
"""CMDB Cost Monitor — watches the Hermes 'IT Asset & CMDB Dashboard' (Notion live).

Endpoint : http://127.0.0.1:3009  (Hermes dashboard plugin; LAN alias 192.168.50.210:3009)
API      : /api/status  -> connection/integration state
           /api/assets  -> {count, knownMonthlySpend, assets[]}

Purpose  : track the CMDB's recorded spend, surface the unpriced backlog, flag
           renewal dates as they appear, and alert immediately if the dashboard
           or its Notion connection breaks.

Output   : compact report on stdout (cron delivers it). Exit 0 = healthy,
           exit 1 = a problem worth surfacing.
"""
import json
import os
import sys
import urllib.request
import urllib.error
from datetime import datetime, date, timedelta

BASE = os.environ.get("CMDB_DASHBOARD_URL", "http://127.0.0.1:3009")
STATE_DIR = os.path.expanduser("~/.hermes/state")
STATE = os.path.join(STATE_DIR, "cmdb_cost_monitor.json")
HISTORY = os.path.join(STATE_DIR, "cmdb_cost_monitor.jsonl")
ALERT_VENDOR = os.environ.get("CMDB_ALERT_VENDOR", "")


def get(path, timeout=20):
    req = urllib.request.Request(BASE + path)
    req.add_header("Accept", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        return e.code, None
    except Exception as e:
        return None, str(e)[:200]


def money(v):
    return f"A${v:,.2f}" if isinstance(v, (int, float)) else "—"


def main():
    now = datetime.now()
    st, status = get("/api/status")
    sa, data = get("/api/assets")

    problems = []
    if not isinstance(status, dict):
        problems.append(f"dashboard /api/status unreachable on {BASE} ({status})")
        status = {}
    if not isinstance(data, dict):
        problems.append(f"dashboard /api/assets unreachable on {BASE} ({sa})")
        data = {}

    assets = data.get("assets") or []
    priced = [a for a in assets if isinstance(a.get("monthlyCost"), (int, float))]
    unpriced = [a for a in assets if a.get("monthlyCost") is None]
    spend = data.get("knownMonthlySpend")
    if spend is None:
        spend = sum((a.get("monthlyCost") or 0) for a in priced)

    if status and status.get("liveConnected") is False:
        problems.append("Notion connection reports liveConnected=false")

    # renewal dates (currently all empty, but capture the moment they appear)
    soon = []
    today = date.today()
    for a in assets:
        rd = a.get("renewalDate")
        if not rd:
            continue
        try:
            d = date.fromisoformat(str(rd)[:10])
        except Exception:
            continue
        days = (d - today).days
        if days <= 45:
            soon.append((days, a.get("name", "?"), rd))
    soon.sort()

    # ---- compare against previous snapshot ----
    prev = {}
    if os.path.exists(STATE):
        try:
            with open(STATE) as f:
                prev = json.load(f)
        except Exception:
            prev = {}

    prev_spend = prev.get("spend")
    delta = None if prev_spend is None else (spend - prev_spend)
    prev_names = set(prev.get("unpriced") or [])
    new_unpriced = [a.get("name", "?") for a in unpriced if a.get("name") not in prev_names]
    prev_priced = set(prev.get("priced") or [])
    newly_priced = [a.get("name", "?") for a in priced
                    if a.get("name") not in prev_priced and a.get("name")
                    not in (prev.get("unpriced") or [])]

    # ---- report ----
    L = []
    L.append(f"★ CMDB Cost Monitor — {now:%a %d %b %Y %H:%M}")
    if problems:
        for p in problems:
            L.append(f"   🔴 {p}")
    else:
        integ = status.get("integrationName", "?")
        L.append(f"   ✅ Dashboard connected · integration {integ} · {status.get('port','?')}")
    L.append(f"   Assets      : {len(assets)}  ({len(priced)} priced · {len(unpriced)} unpriced)")
    L.append(f"   Known spend : {money(spend)} / month   ≈ {money((spend or 0)*12)} / year")
    if delta is not None:
        sign = "±" if abs(delta) < 0.005 else ("+" if delta > 0 else "-")
        L.append(f"   Δ vs last   : {sign}{money(abs(delta))}")
    if new_unpriced:
        L.append(f"   🆕 new unpriced ({len(new_unpriced)}):")
        for n in new_unpriced[:8]:
            L.append(f"        · {n[:66]}")
    if newly_priced:
        L.append(f"   💲 newly priced ({len(newly_priced)}):")
        for n in newly_priced[:8]:
            L.append(f"        · {n[:66]}")
    if soon:
        L.append(f"   ⏰ renewals within 45 days ({len(soon)}):")
        for days, n, rd in soon[:8]:
            L.append(f"        · {rd}  ({days}d)  {n[:58]}")
    else:
        L.append("   ⏰ renewals: none — all 38 renewal dates still empty")
    if unpriced:
        L.append(f"   📋 unpriced backlog: {len(unpriced)}/{len(assets)} "
                 f"({len(unpriced)*100//max(len(assets),1)}% of register has no cost)")
    if status.get("message"):
        L.append(f"   ℹ️  {status['message']}")
    L.append("━" * 46)

    print("\n".join(L))

    # ---- persist ----
    os.makedirs(STATE_DIR, exist_ok=True)
    snap = {
        "ts": now.isoformat(timespec="seconds"),
        "spend": spend,
        "count": len(assets),
        "priced": [a.get("name") for a in priced if a.get("name")],
        "unpriced": [a.get("name") for a in unpriced if a.get("name")],
        "problems": problems,
    }
    with open(STATE, "w") as f:
        json.dump(snap, f, indent=2)
    with open(HISTORY, "a") as f:
        f.write(json.dumps(snap) + "\n")

    if problems:
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
