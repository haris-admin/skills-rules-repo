# Cron Health Diagnostic Patterns

Discovered and refined across multiple weekly reviews. These patterns help identify cron failures from `~/.hermes/cron/jobs.json` — the canonical data source for structured parsing. The `hermes cron list` CLI IS available inside the agent session and is the preferred first-pass tool for a quick overview of all cron jobs with their last_run_at and last_status.

## Pattern 1: Never-Executed Crons (jobs.json)

**Signal:** `last_run_at: null` AND `completed: 0` on a cron created days ago.

**Example (June 12, 2026):**
```json
{
  "id": "6c1e5ffb89d9",
  "name": "A2Square + AML Hive Git Sync (Thu 2 AM)",
  "schedule": {"kind": "cron", "expr": "0 2 * * 4"},
  "completed": 0,
  "enabled": true,
  "state": "scheduled",
  "created_at": "2026-06-08T18:56:32+10:00",
  "last_run_at": null,
  "last_status": null
}
```
Created Jun 8, should have run Thu Jun 12 at 2 AM. Never fired. Four crons found in this state on Jun 12.

**Root causes:**
- Gateway not running when cron was created → scheduler never picked it up
- Schedule syntax error
- Script path doesn't exist or isn't executable
- Cron created but scheduler not reloaded

**Diagnosis steps:**
1. Verify gateway is running: `ps aux | grep "hermes gateway"`
2. Check schedule is valid cron syntax
3. Check script exists (for script-based crons)
4. Check if cron was created after gateway started

## Pattern 2: Stale Stream / Broken Pipe (DeepSeek-specific)

**Signal:** `last_error` contains `RuntimeError: [Errno 32] Broken pipe`

**Context:** deepseek-v4 API stops sending chunks mid-stream after 180-240s of silence. Hermes detects stale stream, kills the connection, and auto-retries.

**Example (June 9-12, 2026):**
- Morning Research (`b0de180cec84`): 4 consecutive days of Broken pipe. Retry usually succeeds but Jun 9-10 lost research JSON.
- Feedback Loop (`59f18c4d557c`): Broken pipe Jun 12.
- Skill Extractor (`2d33c8f9a89c`): Broken pipe Jun 12.
- Podcast KB (`fabab82f804a`): Compounded with 401/timeout errors.

**Retry behavior:** Hermes auto-creates new client with 2-3s exponential backoff. Most crons recover, but some fail permanently when combined with a second error (401, timeout).

**Mitigation strategies:**
- Reduce context size for affected crons
- Increase stream timeout threshold
- Switch to different provider for high-context jobs
- This pattern is documented for `pluto-stale-stream-recovery` skill creation

## Pattern 3: Vercel Monitor False Positive

**Signal:** `last_status: "error"` on `vercel_monitor.py` with stdout containing "No deployments in 12 hours"

**Root cause:** The script exits with code 1 for the "no deployments" warning — which is normal for static/seldom-deployed projects like AML Hive. Hermes correctly records exit code 1 as error, but this is expected behavior.

**Diagnosis:** Always read the actual `last_error` content (stdout/stderr), not just the status code. If the output says "No deployments in 12 hours — project may be idle" and emails were sent, the monitor is working correctly. Real errors are API connection failures or authentication issues.

**Fix:** Script should exit 0 for expected "idle" state, exit 1 only for actual system errors.

## Pattern 4: Script-Based Cron Output Location

**Signal:** Script-based crons (`no_agent: true`) with `deliver: local` — where is the output?

**Answer:** Output is captured in the `last_error` field in jobs.json. Even for "error" status, the field contains the full stdout from the script run. There is NO separate log file for most script crons.

**Example:** The `git_sync.py` cron stores its full sync report (37 repos, per-repo status) in `last_error`. The `vercel_monitor.py` stores its alert content there. There is no `~/.hermes/git_sync_output.log`.

## Pattern 5: Cron State `paused`

**Signal:** `state: "paused"` + `paused_at` timestamp

**Example (June 12, 2026):**
```json
{
  "id": "bcbe9b21e0ab",
  "name": "Pluto Voice & Task Processor",
  "state": "paused",
  "paused_at": "2026-06-12T15:27:30+10:00",
  "completed": 11154,
  "last_status": "ok"
}
```
Had 11,154 successful runs before being paused. Check: was this intentional? Who paused it? Re-enable if safe.

## Pattern 6: Podcast Ingestion Failure Modes

Three distinct failure modes observed for podcast ingestion (`fabab82f804a`):

1. **IP Block:** Transcript download logs show "5 consecutive transcript failures — likely IP blocked. Stopping." (YouTube rate-limiting)
2. **401 Unauthorized:** Supabase auth failure — credential expired or rotated
3. **Timeout:** Script exceeds 120s default timeout processing 16 podcasts

Check `~/.hermes/research_outputs/podcast_ingestion_*.log` for the specific failure mode.

## Pattern 7: False-Negative Cron Error — Script Works But Exceeds Timeout

**Signal:** `last_status: "error"` with `last_error: "Script timed out after 120s"`, but actual data landed in the target system.

**Example (June 12-13, 2026):**
- Podcast KB Ingestion (`fabab82f804a`) shows `last_status: error` every run
- `last_error` contains: "Script timed out after 120s: /home/habib/.hermes/scripts/podcast_ingestor.py"
- Yet Supabase `podcast_kb.episodes` shows 45 new episodes with `created_at` in the last 7 days (3 on Jun 6, 26 on Jun 7, 16 on Jun 12)
- The script successfully ingested episodes but hit the 120s wall before completing its full run

**Root cause:** The script's workload (16 podcasts, YouTube transcript downloads, Supabase inserts) exceeds the 120s default timeout. Hermes kills the process at timeout, recording it as error, but the data written before the kill survives.

**Diagnosis:** Always cross-check the actual data destination, not just the cron status:
```bash
PGPASSWORD='...' PGSSLMODE=require psql -h aws-1-ap-southeast-2.pooler.supabase.com -p 6543 \
  -U postgres.vyqagemgwxfscppkfswq -d postgres \
  -c "SELECT count(*), date(created_at) FROM podcast_kb.episodes WHERE date(created_at) >= 'DATE_START' GROUP BY date(created_at) ORDER BY date(created_at);"
```

**Fix:** Increase the cron job's timeout in `jobs.json` from 120 to 300 (or higher). This is a 1-line config change, not a code change.

**Also affects:** Podcast Chunking cron (`podcast_chunker.py`) — same 120s timeout, same false-negative pattern. Jun 12-13 review: 45 new episodes ingested but zero new chunks created because the chunker times out before processing them.

## Pattern 8: `read_file` Line-Number Prefixes Break JSON Parsing

**Signal:** `json.loads()` fails with `Extra data`, `Invalid control character`, or `Expecting value` when parsing output from `read_file()`.

**Root cause:** `read_file()` returns content prefixed with line numbers (`1|`, `2|`, `3|`, etc.). These prefixes are NOT valid JSON and break `json.loads()`:
```
1|{
2|  "jobs": [
3|    {
4|      "id": "b0de180cec84",
...
```

**Workaround (regex stripping):** Use `re.sub(r'^\s*\d+\|', '', content, flags=re.MULTILINE)` to strip prefixes before parsing. This works but is fragile for large files.

**Preferred approach (terminal + Python):** Skip `read_file` entirely for JSON files. Use `terminal()` with a Python one-liner:
```python
terminal("python3 -c \"import json; data=json.load(open('$HOME/.hermes/cron/jobs.json')); jobs=data['jobs']; [print(f'{j[\\\"name\\\"][:50]} | status={j.get(\\\"last_status\\\")}') for j in jobs]\"")
```
Or use `execute_code` with `terminal()` for more complex processing. This avoids the line-number problem entirely and is faster for large files.

**Fallback:** Use `execute_code` block with `read_file()` + regex stripping if you need the full JSON structure in Python for analysis. Only strip when the file is under 2000 lines (read_file limit).

## Pattern 9: Saturday Auto-Improvement Loop Produces Diagnostics, Not Fixes

**Signal:** The Saturday DREAM MODE cron (`159702fe072c`) runs successfully and produces `improvements-YYYY-MM-DD.md` and `dreams-YYYY-MM-DD.md` reports, but the actual fixes listed in those reports were not implemented. Skills remain uncreated, cron timeouts unchanged, retrospective runs not executed.

**Example (June 13, 2026 improvements report):**
- Report correctly identified: 45 episodes ingested, 0 stale Supabase rows, 1 stale skill reference patched
- Report proposed 4 dreams (YouTube proxy rotation, cron scheduler health monitor, automated skill creation, DeepSeek alternative provider)
- BUT did NOT: create the 4 pending skills (9 days debt), increase podcast ingestion timeout, run retrospective research, debug A2Square never-executed crons

**Root cause:** The Saturday cron's prompt instructs it to ANALYZE and REPORT, not to EXECUTE. It reads the Friday review, validates the findings, produces its own analysis, and stops. The `auto_improvements_saturday` section of the Friday JSON report is treated as suggestions for the report, not as a work queue to execute.

**Fix options:**
1. **Expand Saturday cron prompt:** Add explicit instruction to execute `skill_manage(action='create')` for pending skills and `patch` for config changes
2. **Create a separate "Sunday Execution" cron:** Reads the Saturday reports and EXECUTES the fixes, separate from analysis
3. **Shift responsibilities:** Friday review produces BOTH analysis AND a concrete bash/Python script of fixes for Saturday to run blindly

**Current status (Jun 13):** Loop broken. Friday identifies problems → Saturday analyzes them again → no fixes happen → problems persist next Friday.
