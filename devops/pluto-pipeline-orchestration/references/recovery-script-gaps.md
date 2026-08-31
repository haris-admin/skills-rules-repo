# Startup Recovery Script Gaps

## Background
WSL suspends all cron processes when the Windows host sleeps. Cron has no catch-up mechanism — jobs scheduled during the suspension window are permanently lost. A `@reboot` recovery script (`~/.hermes/scripts/startup-recovery.sh`) exists to re-dispatch critical morning jobs after WSL resumes.

## v2 Fix (June 14, 2026) — Also Dispatches Hermes Cron Jobs

The original v1 script only dispatched pipeline tasks via `dispatch_pipeline.sh`. It did NOT dispatch any Hermes cron jobs — missing the Saturday Weekly Review and other weekend-specific work.

**v2 changes:**
- Added `hermes cron run --accept-hooks <job_id>` for all 27 Hermes cron jobs
- Includes: daily pipeline (Chamber Refresh, Morning Research, Synthesis, Action Bridge, Feedback, Moonshots, LinkedIn, Insights, Improver, Gmail, Competitor Intel, Vercel Monitor)
- Weekend-specific: Saturday Weekly Review, Weekly Improvements, Weekly Review (Fri), Sunday Adversarial + Portfolio Pulse
- Day-of-week awareness: only dispatches Mon-Fri briefing on weekdays
- Gap-length detection: if gap spans multiple days (24h+), dispatches ALL missed weekend jobs
- Uses `hermes cron run --accept-hooks` with the full path `/home/habib/.local/bin/hermes cron run`

### What v2 Catches That v1 Missed

| Job | ID | Schedule | v1 | v2 |
|-----|-----|----------|----|----|
| Saturday Weekly Review | 7d24b37a03f2 | Sat 6AM | ❌ | ✅ |
| Sunday Adversarial + Portfolio | f8756a2b8403 | Sun 6AM | ❌ | ✅ |
| Weekly Improvements | 159702fe072c | Sat 12AM | ❌ | ✅ |
| Weekly Review (Fri) | cc5ca5690d05 | Fri 11:05PM | ❌ | ✅ |
| All 12 daily pipeline jobs | various | 4-6AM | ❌ | ✅ |
| Morning Briefing (Mon-Fri) | c527fed4a1da | 6AM weekdays | ❌ | ✅ |

### How the Gap Detection Works

```bash
# Time-based gap detection
if system boot time > 6AM → check gap since last pipeline task
if gap >= 6 hours → system was likely suspended → dispatch recovery

# Day-specific logic
GAP_START = NOW - GAP_HOURS * 3600  # When the gap began
GAP_START_DOW = day of week at gap start

if GAP_START covers Saturday area (gap >= 24h from Saturday):
    → dispatch ALL weekend jobs (Friday review + Saturday + Sunday)
elif TODAY is Saturday:
    → dispatch Saturday jobs only
elif TODAY is Sunday:
    → dispatch Sunday job + Saturday if gap >= 24h
```

### Cron Worker Pattern
The script uses `hermes cron run --accept-hooks` which queues the job for the next scheduler tick. Each job runs asynchronously — the recovery script just queues and exits. The scheduler processes the queue on its next 5-minute tick cycle.

### Logging
All dispatches logged to `~/.hermes/logs/startup-recovery.log`:
```
[2026-06-14 14:39:33 AEST] Startup recovery check
[2026-06-14 14:39:33 AEST] ✓ Saturday Weekly Review queued
[2026-06-14 14:39:33 AEST] ✓ Chamber Refresh queued
```

## Discovered Gap (June 13, 2026) — v1 Failure
The original v1 recovery script missed the Saturday Weekly Review (`7d24b37a03f2`, 6AM Sat).

### What Ran vs. What Was Missed (v1)

| Job | Schedule | Actual Time | Status |
|-----|----------|-------------|--------|
| Weekly Improvements (159702fe072c) | Sat 12AM | Sat 11:14 AM (late) | ✅ Caught by dispatch_pipeline |
| Weekly Review (cc5ca5690d05) | Fri 11:05PM | Sat 11:14 AM (late) | ✅ Caught by dispatch_pipeline |
| **★ Saturday Weekly Review (7d24b37a03f2)** | **Sat 6AM** | **Never** | **❌ MISSED** |

### Root Cause (v1)
The original recovery script relied on `dispatch_pipeline.sh` which dispatches a different task system, NOT Hermes cron jobs. `7d24b37a03f2` was a Hermes cron job with no corresponding pipeline task — the script had no way to reach it.

### Detection
- `cronjob list` shows `last_run_at: null` for the missed cron
- No output directory at `~/.hermes/cron/output/<ID>/`
- The cron was created, enabled, and scheduled but **never executed once**

### Mitigation
After any WSL resume, check for all `deliver: origin` crons with `last_run_at: null`:

```bash
cat ~/.hermes/cron/jobs.json | python3 -c "
import json, sys
data = json.load(sys.stdin)
for j in data.get('jobs', []):
    if j.get('deliver') == 'origin' and j.get('last_run_at') is None and j.get('enabled', False):
        print(f'NEVER RAN: {j.get(\"name\",\"?\")} ({j.get(\"id\",\"?\")}) — schedule: {j.get(\"schedule\",{}).get(\"expr\",\"?\")} — created: {j.get(\"created_at\",\"?\")}')
"
```

If the cron is long-overdue, force-run it:
```bash
hermes cron run --accept-hooks <JOB_ID>
```

Note: `hermes cron run` queues the job for the next scheduler tick (every ~30-60s). It does NOT run synchronously. For immediate execution, use `hermes cron tick --accept-hooks` which processes ALL due + queued jobs synchronously (but blocks until all complete, including LLM-driven jobs which can take 5+ minutes).
