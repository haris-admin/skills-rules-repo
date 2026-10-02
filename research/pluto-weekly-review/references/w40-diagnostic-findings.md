# W40 (Sep 25, 2026) — Diagnostic Findings

## 🔴 A Dead Loopback Listener Is a Missing Service, Not a Script Bug — Probe It Before Reporting

The Pre-Dispute worker (`ff18d93e2d10` / `e3cc72366dd7` / `92e8ab1f5102`) emitted `CLAIM FAILED · http ERR · transport_error · backend http://127.0.0.1:8008`
on every 60-second tick, and the 12h report read `163 rejected call(s): claim_failed:ERR; endpoint health backend=DOWN acma=DOWN`.

**Never report this as a script bug or an app outage without probing the listener first:**
```bash
ss -ltnp 2>/dev/null | grep 8008 || echo "NOTHING listening on 8008"
timeout 6 curl -s -o /dev/null -w 'http_code=%{http_code}\n' http://127.0.0.1:8008/health   # 000 = connection refused
```
W40: `http_code=000` and no `ss` listener → the local backend process was simply not running (09:55 report was `backend ok`, so it died mid-day). That is a Haris-owned action, not a Pluto fix.

**Two extra rules:**
- A report that prints one line per rejected call (W40: 163 identical lines) is unreadable — report the aggregation gap as its own finding.
- The `🟡 non-prod loopback override ACTIVE` banner is the *correct* named opt-in exception, not a defect. Do not flag it; do flag a silent bypass if you ever see one.

## 🔴 State the Retention Window Before Drawing Week-Level Conclusions

`executions.db` retained **only the current day** (1,001 rows, earliest `15:20:06` — a ~1,000-row ceiling) and `errors.log` held only the current day too. Consequences: no `source='direct'` catch-up analysis for the window, no stream-stall comparison, no errors baseline.

**Check retention first, then scope the claim:**
```bash
python3 -c "import sqlite3;c=sqlite3.connect('/home/habib/.hermes/cron/executions.db');print(c.execute('SELECT min(started_at),max(started_at),count(*) FROM executions').fetchone())"
```
If min == today, say so explicitly and fall back to cron-output inspection for anything earlier. Do not silently present a one-day sample as a week's measurement. Also report the retention cap itself as a finding — it blinds the next review.

## 🟡 Measure the Prior Review's Implementation Rate as a First-Class Metric

W40: **2 of 11 W39 recommendations implemented (18%)** — and one of the two (A2Square) was user-driven at a keyboard, not pipeline-driven. 

Parse the prior JSON's `improvements` map, then verify each item by grep/probe rather than trusting the claim:
```bash
python3 -c "import json;d=json.load(open('/home/habib/.hermes/reviews/weekly/weekly-review-<PRIOR>.json'));print(json.dumps(d['improvements'],indent=1))"
```
Put the rate in BOTH the trend table and the numbers — it is the honest headline when volume is up but blockers are flat.

## 🟡 Verify a Claimed Code Fix by Importing the Module, Not by Reading the Report

The A2Square `NameError: ensure_test_db` bug (entrypoint above its own helpers) was fixed mid-day. Structural proof beat narrative:
```bash
python3 - <<'PY'
import importlib.util, inspect
p='/home/habib/.hermes/scripts/<runner>.py'
spec=importlib.util.spec_from_file_location('m',p); m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)               # NameError at import would surface here
print(hasattr(m,'ensure_test_db'), hasattr(m,'main'))
src=open(p).read().split('\n')
print('guard after helper:', [i+1 for i,l in enumerate(src) if l.startswith('if __name__')][0]
      > [i+1 for i,l in enumerate(src) if l.startswith('def ensure_test_db')][0])
PY
```
A fix that lands after the failure but before its next scheduled run is **"applied, not yet verified"** — count the failed run against the current week and name the next real test date.

## 🟡 Diagnostic Focus Is Not Rigidity — Sweep the Newest Crons Too

W40's biggest live finding was in a pipeline created only three days earlier (Pre-Dispute, built 22 Sep). The standard list (morning chain, podcast, git_sync, monitors, feedback) all looked routine.

**Always add: every cron whose `created_at` falls inside the review window.** A brand-new pipeline has no history to hide behind, and its first failures are exactly what the review exists to catch:
```bash
python3 -c "import json;j=json.load(open('/home/habib/.hermes/cron/jobs.json'));jobs=j if isinstance(j,list) else j.get('jobs',j);jobs=jobs.values() if isinstance(jobs,dict) else jobs;[print(x['created_at'][:16],x['id'],x.get('name')) for x in jobs if str(x.get('created_at') or '')>='<WINDOW_START>']"
```

## ✅ Verified-Healthy This Week — Do Not Re-Flag

- **`acnc-charities` HTTP 500 is RESOLVED** (product-side): failed 19–23 Sep, then `✅ Synced: 65,758 rows (Δ+59)` on 24 Sep and `NO_CHANGE` on 25 Sep. Do not carry it forward as an open Pluto issue.
- **The gateway dual-instance storm is NOT recurring.** W40: one instance, Main PID 55614, active since 03:36 AEST. The single `Another gateway instance` line was during the update window — and the never-restart-from-a-cron rule still holds.
- **A Hermes update lands ~03:04 and restarts the gateway at ~03:36.** Transient import errors in that window (W40: `cannot import name 'safe_strftime' from 'hermes_time'`) are update churn — cross-check `ls -la ~/.hermes/repo/hermes_time.py` mtime before calling it a break.
- **`error.log`/`errors.log` line counts spike to ~1,100 on the day of a gateway restart** — not a bad day.
