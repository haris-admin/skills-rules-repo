# W31 Diagnostic Findings — August 7, 2026

## ✅ RDS Password — RESOLVED (Aug 6, 2026)

**Status:** FIXED after 7-day outage.

The AML Hive Daily Business Report (`3ebed4e59ee3`) failed Aug 1-5 with `FATAL: password authentication failed`. The script was fetching the RDS password via AWS SSM — the SSM parameter was stale after a password rotation.

**Fix applied:** Switched from Secrets Manager lookup to SSM Run Command approach. The cron resumed producing output on Aug 6-7. This is a different approach than the original W29 recommendation ("update Secrets Manager secret") — the fix was architectural (fetch method change), not just credential update.

**Detection for future:** If the error returns, check whether the SSM Run Command IAM permissions are still valid, or whether the RDS password rotated again.

---

## 🟡 Error Detection False Positives — Output-File Pattern Matching

**Pattern discovered:** When scanning cron output files for errors, simple keyword matching (`error`, `fail`, `exception`) produces massive false positives. Benign patterns that trigger:
- `"errors: 0"` — reporting zero errors in fleet monitors
- `"[SILENT]"` — legitimate suppression of empty reports
- `"Script exited with code 1"` — some monitors deliberately exit 1 for alerting (see AMLHive 11PM Fleet Monitor diagnostic)
- `"No errors found"` — negative assertions

**Root cause:** `execute_code` scripts that do naive `any(w in content.lower() for w in ['error', 'fail', 'exception', 'traceback', 'fatal', 'script failed'])` will report 205+ "errors" from 445 runs when the actual error count from `jobs.json` is only 4.

**The canonical truth:** `~/.hermes/cron/jobs.json` `last_status` field. If `last_status: "ok"`, the cron is healthy regardless of what pattern-matching finds in the output. Only crons with `last_status: "error"` are real failures.

**Recommended approach:**
1. First pass: Parse `jobs.json` for `last_status: "error"` — these are the only real failures
2. Second pass: For each `last_status: "error"` cron, read the `last_error` field for root cause
3. Third pass: Read the most recent output file for additional context

Do NOT enumerate output files and pattern-match as the primary detection method. This produced 205 false positives in W31.

---

## 🟡 Competitor Intel — Debug Flag Added, Cron May Not Pass It

**Pattern:** The `--debug` flag was added to `competitor_intel.py` per W30 auto-improvement, but the cron job (`ddceef1f9e5b`) may not be passing it. Output remains 187-204B (empty JSON) for all 5 days in W31 — degraded from 20% to 0% meaningful.

**Detection:** Check the cron's `script` field in `jobs.json` — if it doesn't include `--debug`, the flag addition to the code is irrelevant. The fix needs to be in the cron config, not just in the code.

**Fix:** Update the cron job script invocation in `jobs.json` to include `--debug`:
```bash
python3 ~/.hermes/scripts/competitor_intel.py --debug
```

**Fallback investigation:** If `--debug` produces no additional output, the source endpoint may be dead. Check whether cURL to the data source from WSL succeeds.

---

## 🟡 Security Scan Cron — Never Executed

**Pattern:** Cron `7059cc6796d6` (🛡️ Pluto Weekly Security Scan, Fri 5PM) exists in `jobs.json` with `last_run_at: null` and `completed: 0` despite being created. This is the "never-executed" anti-pattern documented in the skill.

**Detection:** `last_run_at: null` + `enabled: true` + created days ago. The scheduler never triggered it.

**Fix:** Check whether the gateway was running when the cron was created (scheduler may not have picked it up). Try:
1. Verify schedule syntax: `0 17 * * 5` (5 PM Friday) should be correct
2. Check if gateway was active when cron was created
3. Delete and recreate the cron while gateway is actively running
4. After recreation, check `last_run_at` within 5 minutes to confirm scheduler picked it up

---

## 🟡 Supabase Inaccessible — Fallback to Cron Output Parsing

**Pattern:** The Supabase PostgreSQL query documented in the skill (hardcoded credentials via psql) may be stale. In W31, neither `supabase` Python module was available in any venv, and the direct psql approach wasn't attempted (credentials may be out of date).

**Successful fallback:** Parsed podcast ingestion cron output files (`d4d77c41f6c0/*.md`) with regex `New: (\d+) episodes` to count per-podcast, per-day ingestion. This produced accurate counts (96 episodes across 6 days).

**Additional fallback:** The cron output files also contain: per-podcast episode counts, transcript fetch status (✅/⏭️), and any errors at the individual episode level. This is richer than a simple Supabase count query.

**Recommendation:** When Supabase is unreachable, always fall back to parsing cron output files. The `d4d77c41f6c0` directory has one file per day with full ingestion details.

---

## 🟡 A2Square Weekly Test Suite — 31 Playwright Failures

**Pattern:** `0320d41d6d71` (Mon 2:30 AM) failed Aug 3 with `0 passed, 31 failed` on `tapease_frontend_nextjs_prod`. The backend tests were 0/0 (no tests ran). The portal_backend_lambda_eventbridge also failed due to same PAT corruption as the daily repo sync.

**Root causes (multiple):**
1. **Playwright failures (31):** Unknown — could be DNS resolution (tapease.com.au resolving to EC2 vs Vercel?), Playwright config changes, or actual app regressions
2. **Portal backend skip:** Git fetch failed — same PAT corruption as `0dbba3db3116`
3. **Backend 0/0:** Possible test discovery issue or no tests configured for tapease_portal_fastapi_a2square

**Fix priority:** Fix PAT corruption first (it cascades), then investigate Playwright failures separately.

---

## 🟡 Podcast Ingestion — Aug 3 Gap

**Pattern:** No cron output file exists for Aug 3 in `d4d77c41f6c0/`. All other days (Aug 1, 2, 4, 5, 6, 7) produced output. The cron `d4d77c41f6c0` shows `last_status: ok` in jobs.json — so the scheduler thinks it ran.

**Possible causes:**
1. Cron output file was not saved (write failure or permission issue)
2. Cron fired but produced zero output (all 16 podcasts skipped?)
3. Cron job record shows OK but execution was silent

**Recommendation:** Check `cron_jobs.db` or `executions.db` for Aug 3 execution record. If the cron did run, the output was lost. If it didn't run but jobs.json says OK, there's a state tracking bug.
