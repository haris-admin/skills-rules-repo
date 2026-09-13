# Pipeline Audit Checklist (Full 7-Phase Procedure)

The complete phase-by-phase audit to run when Haris reports missing output, silent failures, or "Hermes is a disappointment." For a quick same-day status check instead of a full audit, use the "Quick Daily Status" procedure in the main skill.

## Contents
- [Phase 1: Surface Status](#phase-1-surface-status)
- [Phase 2: Error Investigation](#phase-2-error-investigation)
- [Phase 3: Script Verification](#phase-3-script-verification)
- [Phase 4: Cross-Platform Path Audit](#phase-4-cross-platform-path-audit)
- [Phase 5: Delivery Target Check](#phase-5-delivery-target-check)
- [Phase 6: Cross-Cron Error Pattern Detection (Systemic Failures)](#phase-6-cross-cron-error-pattern-detection-systemic-failures)
- [Phase 7: Triage → Classify → Auto-Recovery Assessment](#phase-7-triage-classify-auto-recovery-assessment)
- [Never-Executed Cron Detection (Created But Never Fired)](#never-executed-cron-detection-created-but-never-fired)
- [Force-Run / Auto-Retry Detection](#force-run-auto-retry-detection)

When Haris reports missing output, silent failures, or "Hermes is a disappointment," run this systematic audit:

### Phase 1: Surface Status
```bash
hermes cron list                          # All jobs + last_status
crontab -l                                # System crontab (should be just gateway + reboot)
```

### Phase 2: Error Investigation
For each job with `last_status: error`, check its output:

```bash
# View last n outputs
ls -lt ~/.hermes/cron/output/<JOB_ID>/ 2>/dev/null | head -5

# Read the most recent error output
cat ~/.hermes/cron/output/<JOB_ID>/$(ls -t ~/.hermes/cron/output/<JOB_ID>/ | head -1) | tail -30
```

**Classify the error:**
- **"Broken pipe"** → LLM-driven cron shelling out to a script → fix: convert to `no_agent: true`
  - **FIRST CHECK — Is the cron already `no_agent: true`?** If `no_agent: true`, the `model` field shown in `cronjob list` output is **cosmetic** — it has zero effect on execution. The broken pipe is NOT from LLM invocation. Look inside the script itself for `subprocess.run()`, pipe-to-subprocess, or stdout-flush-at-exit patterns that could fail. Changing the model field on a `no_agent` cron does nothing. This is a common trap because `cronjob list` always renders the model column regardless of `no_agent` status — it is dead weight on those jobs.
  - **Cross-check error reports against actual output:** Before acting on a second-hand error report (Saturday review, error log, or Haris flagging it), verify the actual cron output. Check `cron/output/<JOB_ID>/` for the latest `.md` file. If the cron shows `last_status: ok` and produces clean output, the error report is either stale (pre-fix) or misattributed (wrong cron ID). The Saturday review attribution of 396+ broken pipe errors to the Mempalace Watcher was inaccurate — the job was already `no_agent: true` with zero errors and clean `[]` output every 5 minutes.
- **"401 Unauthorized"** → credential expiry → 3+ crons with same error = systemic
- **"timeout"** → script too slow → increase timeout or optimize script
- **"exit code 1" (vercel_monitor.py)** → intentional alert → fix: change to exit 0 (see pitfall above)
- **"merge failed" (git_sync)** → divergent branches → cosmetic, script exits 0

### Phase 3: Script Verification
Run the actual script manually to separate script bugs from cron infrastructure issues:

```bash
python3 ~/.hermes/scripts/<script_name>.py 2>&1; echo "EXIT: $?"
```

If the script succeeds manually (exit 0, produces output) but the cron shows "error", the issue is in **cron configuration** (delivery target, timeout, no_agent flag), not the script itself.

### Phase 4: Cross-Platform Path Audit
Verify all scripts that reference shared data (ChromaDB, git repos) use the correct **Windows path**:

```bash
grep -n "/mnt/c/\|Windows\|palace\|CHROMA" ~/.hermes/scripts/<script>.py
```

Key path rules:
- **ChromaDB** lives at `/mnt/c/Users/habib/.mempalace/palace/` — WSL-side path `~/.hermes/mempalace/chromadb/` is EMPTY
- **Git repos** at `/mnt/c/Code/gitlab/` — NOT in WSL homedir
- **Windows .env** at `/mnt/c/Users/habib/.hermes/.env` — NOT `~/.hermes/.env`
- **Python venv** is WSL-side: `~/.hermes/venv/bin/python3`

### Phase 5: Delivery Target Check
A pipeline that runs perfectly but delivers nothing to the user is the worst failure mode:

```bash
# Find all crons delivering to origin (user-facing) vs local (file-only)
cat ~/.hermes/cron/jobs.json | python3 -c "
import json, sys
data = json.load(sys.stdin)
for j in data.get('jobs', []):
    name = j.get('name', '?')[:50]
    deliver = j.get('deliver', '?')
    status = j.get('last_status', 'never run')
    print(f'{deliver:10s} {status:10s} {name}')
" | sort
```

**Rule:** One Telegram delivery at 6:00 AM Mon-Fri (daily briefing). Saturday delivers a separate weekly review at 6:00 AM (`7d24b37a03f2`). Sunday delivers a system improvement report at 6:00 AM (proposed — pending Haris confirmation). All other jobs stay `deliver: local`.

### Phase 6: Cross-Cron Error Pattern Detection (Systemic Failures)

```bash
# Find ALL crons that failed on a given day — detects systemic failures
cat ~/.hermes/cron/jobs.json | python3 -c "
import json, sys
data = json.load(sys.stdin)
jobs = data.get('jobs', [])
for j in jobs:
    lr = j.get('last_run_at', '')
    ls = j.get('last_status', '')
    if 'YYYY-MM-DD' in lr and ls == 'error':
        print(f'{j.get(\"name\",\"?\")}: {lr} — {ls} — {str(j.get(\"last_error\",\"\"))[:120]}')
"
```
If 3+ crons show the SAME error string on the same day, it's a **systemic credential/app failure**, not individual cron bugs. Escalate to provider-level investigation.

### Phase 7: Triage → Classify → Auto-Recovery Assessment

After investigating all error jobs, classify them into categories to determine next steps:

```bash
# Quick triage: for each error job, manually run the script and check exit code
python3 ~/.hermes/scripts/<script_name>.py 2>&1; echo "EXIT: $?"
```

**Category A — Stale Error (will auto-recover on next run):**
- Script exits 0 when run manually
- Root cause was already fixed (converted to no_agent, changed exit code, added known-dead-repo filter)
- **Action:** Note it, move on. Next cron run will show `ok`.

**Category B — Needs Permanent Fix:**
- Script fails when run manually (broken pipe, 401, timeout)
- Root cause is in the script itself or cron configuration
- **Action:** Fix the script or cron config NOW, then re-verify exit 0

**Category C — Needs Pipeline Change:**
- The job's purpose requires an LLM (skill extraction, synthesis) but it's configured as LLM-driven and hitting broken pipe
- **Action:** Convert to `no_agent: true` with a deterministic script that does the data collection. Accept some loss of reasoning quality for reliability.

**Category D — Systemic/Credential Failure:**
- 3+ jobs with same error (e.g., 401, timeout)
- **Action:** Check shared credentials, provider status, gateway health. Don't debug individual crons.

**After fixing all Category B/C/D jobs, list the Category A auto-recoveries** so the user knows which errors are stale and which were actively fixed:

```bash
# Show which crons still show "error" but are actually fixed
echo "== Auto-Recovery Candidates (stale error, next run fixes) =="
cat ~/.hermes/cron/jobs.json | python3 -c "
import json, sys
data = json.load(sys.stdin)
for j in data.get('jobs', []):
    if j.get('no_agent') and j.get('last_status') == 'error' and j.get('script'):
        print(f'{j.get(\"id\",\"?\")} — {j.get(\"name\",\"?\")[:50]}')
        print(f'  no_agent={j.get(\"no_agent\")} script={j.get(\"script\")} — will auto-recover next run')
"
```

### Never-Executed Cron Detection (Created But Never Fired)

```bash
# Find crons that have NEVER executed — different class from 'errored'
cat ~/.hermes/cron/jobs.json | python3 -c "
import json, sys
data = json.load(sys.stdin)
jobs = data.get('jobs', [])
found = False
for j in jobs:
    lr = j.get('last_run_at')
    if lr is None:
        created = j.get('created_at', '?')[:10]
        schedule = j.get('schedule', {}).get('expr', '?')
        next_run = j.get('next_run_at', '?')[:10] if j.get('next_run_at') else '?'
        print(f'{j.get(\"name\",\"?\")} ({j.get(\"id\",\"?\")})')
        print(f'  Created: {created}  Schedule: {schedule}  Next: {next_run}')
        found = True
if not found:
    print('All crons have executed at least once.')
"
```

A cron with `last_run_at: null` and `enabled: true` is a **scheduler bug**, not a timeout or failure. It means the Hermes cron scheduler never picked up the job. Compare `created_at` to today's date — if a cron has gone 3+ days without firing and its schedule should have triggered it (e.g., a weekly cron created 11 days ago), escalate as a scheduler-level defect.

**Cross-check with output directories** — even if `jobs.json` is ambiguous, the presence or absence of a cron output directory in `~/.hermes/cron/output/<id>/` is definitive proof of execution:

```bash
# List all crons that have NO output directory = never produced any output
for j in $(cat ~/.hermes/cron/jobs.json | python3 -c "
import json, sys
jobs = json.load(sys.stdin).get('jobs', [])
for j in jobs:
    print(j['id'])
"); do
  [ -d ~/.hermes/cron/output/$j ] && echo "HAS_OUTPUT: $j" || echo "NEVER_RAN: $j"
done
```

**Scheduler‑bug signature:** A cron showing `next_run_at` that skips the very next valid execution window (e.g., a weekly Thursday cron created June 8 showing next_run June 18 when June 11 is a Thursday) suggests the scheduler's day‑of‑week calculation is off. This affects weekly crons (`0 2 * * 4`) more than daily crons, since the offset can push the first fire date a full week.

**Stale display name detection** — compare each cron's `name` field against its schedule `display` value:

```bash
cat ~/.hermes/cron/jobs.json | python3 -c "
import json, sys
data = json.load(sys.stdin)
for j in data.get('jobs', []):
    name = j.get('name', '?')
    sched = j.get('schedule_display', '?')
    time_parts = sched.split()
    if len(time_parts) >= 2:
        h, m = int(time_parts[0]), int(time_parts[1])
        display_time = f'{h:02d}:{m:02d}'
        if display_time not in name and display_time.replace(':', '') not in name:
            print(f'NAME/SCHEDULE MISMATCH: {j.get(\"id\",\"?\")}')
            print(f'  Name:     {name}')
            print(f'  Schedule: {sched} ({display_time})')
            print(f'  Source:   cron name field stale — update to match actual schedule')
"
```

Cron names containing a time that doesn't match the job's `schedule_display` cause confusion during auditing. Fix by editing the cron: `hermes cron edit <id> --name "New Name with Correct Time"`. On June 11, 2026, `pluto_honcho_bridge_daily` was named "Pluto Honcho Signal Bridge (5:20 PM AEST)" but ran at `0 6 * * *` (6:00 AM AEST).

### Force-Run / Auto-Retry Detection
```bash
# Find crons with near-identical last_run_at far from schedule
cat ~/.hermes/cron/jobs.json | python3 -c "
import json, sys
from collections import Counter
data = json.load(sys.stdin)
jobs = data.get('jobs', [])
timestamps = [j['last_run_at'][:16] for j in jobs if j.get('last_run_at')]
dupes = {t: c for t, c in Counter(timestamps).items() if c >= 3}
if dupes:
    for ts, count in sorted(dupes.items()):
        print(f'{count} crons ran at {ts} (same timestamp — likely force-run/batch-trigger)')
else:
    print('No force-run clusters detected')
"
```
A force-run cluster (multiple crons with identical last_run_at far from their scheduled times) means the gateway batch-triggered them — often after a maintenance action, restart, or backlog clearance. Correlate with the scheduled times to distinguish batch-triggers from normal execution.
