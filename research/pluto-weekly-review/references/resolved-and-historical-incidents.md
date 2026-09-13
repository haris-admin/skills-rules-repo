# Resolved and Historical Cron Incidents

A chronological log of specific cron/pipeline incidents diagnosed across weekly reviews — some resolved, some recurring patterns to recognize on sight. Check this before flagging a "new" issue; it may already be a known, resolved, or by-design pattern. For the week-specific diagnostic logs (W28, W29, W31), see [w28-diagnostic-findings.md](w28-diagnostic-findings.md), [w29-diagnostic-findings.md](w29-diagnostic-findings.md), and [w31-diagnostic-findings.md](w31-diagnostic-findings.md). For general (non-dated) cron health patterns, see [cron-diagnostics.md](cron-diagnostics.md).

## Contents

- [Podcast Ingestion False-Positive Error — RESOLVED (July 4, 2026)](#podcast-ingestion-false-positive-error--resolved-july-4-2026)
- [Podcast Ingestion — Venv Evaporation (WSL Restart)](#podcast-ingestion--venv-evaporation-wsl-restart)
- [TapEase Bridge HTML Error Page (All 4 Monitors)](#tapease-bridge-html-error-page-all-4-monitors--updated-july-3-2026)
- [AMLHive 11PM Fleet Monitor — Exit Code 1 Is BY DESIGN](#amlhive-11pm-fleet-monitor--exit-code-1-is-by-design-added-july-10-2026-verified-july-11)
- [Daily Learning — False Negative (Output Exists, Wrong Location)](#daily-learning--false-negative-output-exists-wrong-location-added-july-17-2026)
- [Cron Output Misrouting — General Pattern](#cron-output-misrouting--general-pattern-added-july-17-2026)
- [Competitor Intel — Empty Output Pattern (187 Bytes)](#competitor-intel--empty-output-pattern-187-bytes-added-july-10-2026)
- [Pluto Fleet Monitor — AML Hive 5PM Venv Missing](#pluto-fleet-monitor--aml-hive-5pm-venv-missing)
- [Saturday Auto-Improvement Pipeline: Reports ≠ Action](#saturday-auto-improvement-pipeline-reports--action)
- [Skill Extractor "All Matched" False Negative](#skill-extractor-all-matched-false-negative)
- [Gateway Shutdown — Simultaneous Cron Kills](#gateway-shutdown--simultaneous-cron-kills-added-july-24-2026)
- [AML Hive Daily Business Report — DB Password Auth Failure — RESOLVED](#aml-hive-daily-business-report--db-password-auth-failure-added-july-24-2026-resolved-aug-6-2026)
- [Git Index Lock on /mnt/c/ Filesystem](#git-index-lock-on-mntc-filesystem-added-july-24-2026)
- [Test Suite Exit Code 1 With 838+ Passing Tests](#test-suite-exit-code-1-with-838-passing-tests-added-july-24-2026)
- [ASIC Intentionally Disabled — Should Exit 0](#asic-intentionally-disabled--should-exit-0-added-july-24-2026)
- [Honcho Bridge State File — Unbounded Growth](#honcho-bridge-state-file--unbounded-growth-added-july-24-2026)
- [Security Scan Cron — Never Executed](#security-scan-cron--never-executed-added-aug-7-2026)

## Podcast Ingestion False-Positive Error — ✅ RESOLVED (July 4, 2026)

**Root cause:** `run_sql()` passed SQL via `psql -c "<sql>"` — a command-line argument. When a podcast transcript exceeded ~128KB, the total `argv` size exceeded the OS ARG_MAX limit, causing `[Errno 7] Argument list too long: 'psql'`. The script successfully ingested 6-10 episodes before hitting the long transcript and crashing with exit code 1.

**Fix:** Changed `run_sql()` in `podcast_ingestor.py` to pipe SQL via stdin using `subprocess.run(..., input=sql)` instead of `psql -c`. Deployed July 4, 2026.

**Verification:** Cron `d4d77c41f6c0` now shows `last_status: ok` daily. All 7 runs Jul 4-10 show `ok`. This was the #1 cron error for 3+ weeks.

**Pitfall:** If the error ever returns, check whether `/tmp/podcast_venv/` still exists (WSL restarts clear /tmp). If it's an ARG_MAX on a new command, the stdin-piping pattern generalizes.

## Podcast Ingestion — Venv Evaporation (WSL Restart)

**Symptom:** Podcast ingestion cron shows `last_status: error` with ~500-byte error output containing `No such file or directory` for yt-dlp or the podcast venv. All 16 podcasts fail because the venv is gone.

**Root cause:** `/tmp/podcast_venv/` is cleared on WSL restart or `/tmp` cleanup. The venv with yt-dlp and its dependencies evaporates.

**Detection:** Check `ls /tmp/podcast_venv/bin/yt-dlp`. If missing, the venv needs rebuilding. Also check cron output size — ~500 bytes = venv missing (quick failure), 2,000-4,000 bytes = partial success with ARG_MAX or timeout (fixed July 4).

**Fix:** Rebuild venv: `python3 -m venv /tmp/podcast_venv && /tmp/podcast_venv/bin/pip install yt-dlp`. Long-term: move to persistent location like `~/.hermes/venvs/podcast/`.

## TapEase Bridge HTML Error Page (All 4 Monitors) — Updated July 3, 2026

**Symptom:** Cron `e5675447ed37` shows `last_status: error` with `imaplib.IMAP4.error: b'[AUTHENTICATIONFAILED] Invalid credentials (Failure)'` on every run. The `.gmail_ingestor_state.json` file stops updating.

**Root cause:** The Gmail app password has expired or been revoked. Google app passwords expire periodically and must be regenerated.

**Detection:** `grep 'AUTHENTICATIONFAILED'` on the cron output for `e5675447ed37`. If it appears on every run for multiple days, the password is dead.

**Impact:** The Gmail→Perplexity signal pipeline goes completely dark. Zero external intelligence enters Pluto's research pipeline from this source. Morning briefings operate from a shrinking information base.

**Fix:** Haris must generate a new Gmail app password at https://myaccount.google.com/apppasswords and update the credential in the script or environment variable. Pluto cannot fix this — it requires human Google account access.

**Reporting:** When this failure is detected, flag as CRITICAL in both the Friday review and the Saturday user-facing review. Include: how many days it's been failing, what intelligence sources are affected, and the exact human action needed.

Separately, note: all TapEase Fleet Monitors (`dbd3cb1b5bd3`, `582bd225ddd1`, `1086e6405da1`, `be81c61778a8`) can show `last_status: error` with `JSONDecodeError: Expecting value: line 1 column 1 (char 0)`. Root cause: the Windows bridge at port 18796 returns HTTP 200 on `/health` but the `/tapease/monitor` endpoint returns an HTML error page instead of JSON — the Express route handler is either missing or throwing an unhandled error. Detection: `grep 'JSONDecodeError.*Expecting value'` on the cron output for any TapEase monitor (bridge is alive but the monitor route is broken — NOT a bridge-down situation, which would give "No response from bridge" instead). Fix: debug the Windows-side Express route handler for `/tapease/monitor` — see the `windows-bridge-management` skill. **Impact on weekly review:** when all 4 TapEase monitors show identical JSONDecodeError, report as a single bridge issue (1 root cause, 4 affected crons), not 4 separate cron failures.

**Self-heal note:** the TapEase monitors self-healed in Week 26 (Jun 27-Jul 3) — all 4 monitors went from 0/28 to 28/28 without an explicit code fix. The root cause (bridge returning HTML) may have been resolved by a bridge restart, WSL restart, or environmental change, and the pattern can recur if the underlying bridge code issue isn't fixed. If all 4 monitors transition from `JSONDecodeError` → `status: ok` simultaneously, report as "recovered — environmental, root cause unknown, may recur."

## AMLHive 11PM Fleet Monitor — Exit Code 1 Is BY DESIGN (Added July 10, 2026, Verified July 11)

**Symptom:** Cron `be5061d19a5a` shows `last_status: error` with `Script exited with code 1`. But stderr shows `✅ Email sent to 1 recipients` and the stdout contains a complete, detailed fleet monitor report.

**Root cause:** `amlhive_prod_monitor.py` intentionally exits with code 1 when P0 alerts exist OR >2 P1 alerts exist (lines 1314-1321: `if p0_count > 0: return 1; if p1_count > 2: return 1`). This is documented in the `pluto-fleet-monitor` skill: "Script must exit 0 for healthy, 1 for issues — but email is the alert mechanism, not exit code."

**The 11PM run is the most likely to exit 1** because it catches the accumulated day's errors. PII encryption errors, Redis connection refused, and Application startup failures all generate P0/P1 alerts that push the count above the threshold. This is NOT a cron failure — the script is working exactly as designed.

**Detection:** Check whether stderr contains `✅ Email sent` and stdout contains complete report sections. If so, the monitor ran successfully and found real issues. Count the P1/P0 alerts from the report body, not from the exit code.

**Reporting:** Do NOT report this as a cron failure. The exit code is a signal, not an error. Instead, report the actual alerts found (Sentry errors, CloudWatch alarms, etc.). If the 11PM run consistently exits 1 and the other 3 runs exit 0, check whether the issues are time-specific (e.g., batch jobs triggering at midnight).

## Daily Learning — False Negative (Output Exists, Wrong Location) (Added July 17, 2026)

**Pattern discovered W28:** The Moonshots Daily Learning cron (`0fb6bf47f704`) runs successfully every day (7/7, producing 60-68KB of real LLM output) but the output is saved ONLY to `cron/output/0fb6bf47f704/` — NOT to `research_outputs/daily-learning-*.md`. This creates a 100% false negative in the weekly review.

**Detection:**
```bash
# Check BOTH locations:
ls ~/.hermes/research_outputs/daily-learning-2026-07-1*.md  # Expected: 7 files
ls ~/.hermes/cron/output/0fb6bf47f704/2026-07-1*.md        # Actual: 7 files (60-68KB)
```

**Root cause:** The cron prompt for `0fb6bf47f704` doesn't include instructions to save output to `research_outputs/`. The cron produces content but the agent doesn't know to write it to the expected location.

**Reporting:** Do NOT report "0/7 daily learning" without checking `cron/output/0fb6bf47f704/` first. If cron/output/ has 7 files (60-68KB each) but research_outputs/ has 0, the pipeline is WORKING — output is just misrouted. Report as "7/7 in cron/output/ (misrouted — not in research_outputs/)". Flag the cron prompt for fixing.

**Fix:** Update cron `0fb6bf47f704` prompt to include: "After completing your learning synthesis, save the output to `~/.hermes/research_outputs/daily-learning-YYYY-MM-DD.md`." This is a 15-minute fix.

## Cron Output Misrouting — General Pattern (Added July 17, 2026)

**Generalization of the daily learning pattern:** Any cron can produce real output that goes to the wrong location. The `cron/output/<job_id>/` directory captures all output from that cron, but the scripts/prompts may not save to the expected `research_outputs/` path. This creates silent false negatives in pipeline completeness checks.

**Detection in Phase 1 (research outputs check):** After listing `research_outputs/` files, cross-reference against `cron/output/` for any pipeline cron that shows "0 files" but is known to run. Key crons with expected research_outputs paths:
- `0fb6bf47f704` (Daily Learning) → expected: `research_outputs/daily-learning-*.md`
- `d4d77c41f6c0` (Podcast Ingestion) → expected: `research_outputs/podcast_insights.md`
- `2d33c8f9a89c` (Skill Extractor) → expected: `research_outputs/skill-proposals_*.md`

**Pattern:** `ls -la ~/.hermes/cron/output/<job_id>/ | grep $(date +%Y-%m)` — if files exist here but NOT in research_outputs/, output is misrouted.

## Competitor Intel — Empty Output Pattern (187 Bytes) (Added July 10, 2026)

**⚠️ Dependency chain (W32, Aug 15):** `competitor_intel.py` output is consumed by `briefing_improver.py` at 5:20 AM (`competitor_intel_{today}.json`). Do NOT schedule competitor intel after 5:20 — a W32 suggestion to move it to 5:25 would have permanently suppressed the competitor section from the briefing. Correct fix: keep it before 5:20 (moved 5:07 → 5:12), plus a poll/fallback inside the script for slow Morning Research. Also: the Chamber Refresh cron can show `last_status: ok` while feeding 0 items (chromadb import failure) — always check the feed footer (`Fed N new item(s)`), not just `last_status`.

**Symptom:** `competitor_intel_*.json` files are exactly 187 bytes on some days. These contain essentially empty JSON (`{"results": [], ...}` or similar placeholder structure).

**Detection:** `wc -c ~/.hermes/research_outputs/competitor_intel_2026-07-*.json | grep '187 '`. If more than 50% of files in a week are 187 bytes, the competitor intel source is degraded.

**Root cause (suspected):** Rate limiting on the competitor data source, source format change, or scraping targets returning empty results. The `competitor_intel.py` script lacks debug logging — no way to determine cause from cron output alone.

**Reporting:** Count "meaningful" vs "empty" runs. If <50% of runs produce real output, flag as MEDIUM degradation and recommend adding debug logging to the script.

## Pluto Fleet Monitor — AML Hive 5PM Venv Missing

**Symptom:** `a0b1f0f642af` (5PM run) fails with `No such file or directory: '/home/habib/.hermes/repo/venv/bin/python'`. The 11AM and 11PM runs succeed.

**Root cause:** The 5PM run script references a different Python venv path. The 11AM/11PM runs use a different venv (likely `~/.hermes/venv/bin/python3` which exists).

**Detection:** Compare the venv path in the cron's script field against the 11AM/11PM runs. Different paths = partial failure.

**Fix:** Either create `~/.hermes/repo/venv/` with required deps, or change the 5PM run to use the same venv as the 11AM/11PM runs.

## Saturday Auto-Improvement Pipeline: Reports ≠ Action

**Pattern confirmed (June 20, June 26, June 27):** The Saturday auto-improvement cron (`159702fe072c`) produces comprehensive Phase 1-5 reports with "fixes deployed" claims, but the actual code changes are rarely applied.
- **Week 23 (Jun 13):** 0/8 directives implemented.
- **Week 24 (Jun 20):** 1/4 (25%) — only Performance Tracker fix applied.
- **Week 25 (Jun 26):** 3/8 (37.5%) — podcast venv rebuilt, git-sync skill created, performance-tracker skill created. Still missed: SKIP_REPOS, vercel monitor, Daily Maintenance patch, Saturday pipeline fix.
- **Week 26 (Jun 27):** Saturday report claimed Phase 3 "2 Skills Created" (verified: git-sync at Jun 27 00:07, performance-tracker at Jun 27). Phase 4 "1 Unfixable" (TapEase bridge — environmental recovery occurred independently later in the week). SKIP_REPOS still not added.

**Trend:** Implementation rate is slowly improving (0% → 25% → 37.5%) but still below 50%. The Saturday cron consistently creates skills (Phase 3) but skips code patches (Phase 4) and structural fixes. (For the original June 13 discovery of this pattern, see [cron-diagnostics.md](cron-diagnostics.md#pattern-9-saturday-auto-improvement-loop-produces-diagnostics-not-fixes).)

**Detection in weekly review:** Cross-reference the Saturday improvements report's "fixes deployed" claims against the actual files:
```bash
# After reading Saturday improvements report, verify claimed fixes:
grep "SKIP_REPOS" ~/.hermes/scripts/git_sync.py          # Should exist if fixed
grep "No deployments" ~/.hermes/scripts/vercel_monitor.py # Should NOT alert if fixed
```

**Fix for Saturday cron:** The prompt must explicitly say "EXECUTE these actions, then VERIFY each one. Use read_file/grep to confirm the change was written before claiming it as done." The current prompt allows the LLM to write a report about fixes without applying them.

**Impact on weekly review:** The `auto_improvements_saturday` section in the JSON report must use ACTION language (not "consider" or "review"). Each item must include a verification command. The Saturday cron must be directed to stop after each action to verify.

## Skill Extractor "All Matched" False Negative

**Pattern:** The Skill Extractor (`2d33c8f9a89c`) produces 0 proposals for 5+ consecutive days (Jun 22-26) claiming "none — all recent scripts have matching skills." But 2 proposals from Jun 20 (`git-sync` and `pluto-performance-tracker`) remain PENDING — the skills were never actually created.

**Detection:** In the weekly review, cross-reference `skill-proposals_*.md` files against `skills_list`:
```bash
# Check if proposed skills actually exist
skill_manage(action='list') | grep -i "git-sync\|performance-tracker"
```

**Root cause:** The extractor tracks proposal existence (a file was generated) but NOT creation (a skill was actually registered). After generating a proposal, if it's not acted on, the extractor considers the script "matched" on subsequent runs because it sees the proposal file exists — even though the skill doesn't.

**Fix for weekly review:** Always cross-check the "Still Pending" list from the latest skill-proposals file against actual registered skills. Flag any proposal that exists on disk but not in the skill registry.

## Gateway Shutdown — Simultaneous Cron Kills (Added July 24, 2026)

**Pattern discovered W29:** When the Hermes gateway shuts down for maintenance or restart, it sends `final-cleanup` signals that kill ALL running tool subprocesses simultaneously. Multiple crons that happen to be running at the same timestamp will all show `last_status: error` with identical `last_run_at` values and the same error: "Gateway shutdown (final-cleanup) killed the job's tool subprocess before the run finished."

**Detection:** Look for crons sharing the same `last_run_at` timestamp with the gateway-shutdown error. In W29, `4eef20ef0e25` (Hermes Update Check) and `d4d77c41f6c0` (Podcast KB Ingestion) were both killed at `2026-07-24T04:04:42`.

**Reporting:** Group these together. Count them as "transient — gateway restart" in the error tally, NOT as separate cron-specific failures. Do not escalate. These are infrastructure events, not script bugs.

## AML Hive Daily Business Report — DB Password Auth Failure (Added July 24, 2026; RESOLVED Aug 6, 2026)

**Status: RESOLVED.** Fixed by switching from AWS Secrets Manager to SSM Run Command for RDS password retrieval. The cron (`3ebed4e59ee3`) resumed producing output on Aug 6 after a 7-day outage.

**Original pattern:** `psql: FATAL: password authentication failed for user "amlhive"` on `amlhive-prod.ch4ykiy82n3q.ap-southeast-2.rds.amazonaws.com`. The `amlhive_daily_report.py` script fetches the RDS password via AWS SSM — when the SSM parameter changes or the IAM role loses access, the script crashes.

**Detection:** `RuntimeError: SSM: psql: error: ... FATAL: password authentication failed` in `3ebed4e59ee3` output.

**Impact when failing:** Daily business report goes dark for all affected days.

**Fix applied:** Switched from Secrets Manager lookup to SSM Run Command approach. If the error returns, check SSM Run Command IAM permissions or RDS password rotation status.

## Git Index Lock on /mnt/c/ Filesystem (Added July 24, 2026)

**Pattern discovered W29:** `fatal: Unable to create '.git/index.lock': File exists.` on repos under `/mnt/c/Code/github/`. Another git process on the Windows side (VS Code, GitHub Desktop) holds a stale lock that blocks WSL git operations.

**Detection:** `GIT_RESET_FAILED` in `0dbba3db3116` output. The lock is on `/mnt/c/Code/github/almhive-tech/amlhive1/.git/index.lock`.

**Fix:** Add `rm -f` retry logic before git operations on /mnt/c/ repos. The lock is almost always stale.

## Test Suite Exit Code 1 With 838+ Passing Tests (Added July 24, 2026)

**Pattern discovered W29:** `044c0bc41e31` (AMLHive Daily Test Suite) exits code 1 despite 838 tests passing. A few tests are failing but the cron output is truncated — specific failures are invisible.

**Detection:** `Script exited with code 1` + `838 passed` visible in stdout. The failing test names are not captured in the cron output.

**Fix:** Either increase truncation limit or have the script write test failures to a dedicated file for diagnostic access.

## ASIC Intentionally Disabled — Should Exit 0 (Added July 24, 2026)

**Pattern discovered W29:** User's standing order (from memory) is "no asic trying for now." The ASIC Ref-DB sync script exits code 1 when `CSV URL for asic-registered-schemes is not configured`. The `acnc-charities` portion works fine independently.

**Detection:** `HTTP 503 — "CSV URL for asic-registered-schemes is not configured (set the env var)"` in `937bb914c497` output.

**Fix:** Script should check if ASIC is intentionally disabled (missing env var = disabled) and exit 0. Only exit 1 on actual connection/auth failures.

## Honcho Bridge State File — Unbounded Growth (Added July 24, 2026)

**Pattern:** `.honcho_bridge_state.json` accumulates every pushed file since inception (85+ entries in the `pushed_files` array). The array grows without bound.

**Detection:** `wc -l ~/.hermes/research_outputs/.honcho_bridge_state.json` — if above 100 lines, the array is growing.

**Fix:** Either rotate weekly (keep last 14 days) or use a hash set for deduplication.

## Security Scan Cron — Never Executed (Added Aug 7, 2026)

**Pattern:** Cron `7059cc6796d6` (🛡️ Pluto Weekly Security Scan, Fri 5PM) exists in `jobs.json` with `last_run_at: null`, `completed: 0`, and `enabled: true` despite being created. Classic never-executed anti-pattern.

**Detection:** `last_run_at: null` + `enabled: true` + cron was created days/weeks ago. The scheduler never triggered it.

**Root cause (suspected):** Gateway may not have been running when the cron was created, or a schedule parsing bug. The schedule `0 17 * * 5` is syntactically correct.

**Fix:** Verify gateway is running, then delete and recreate the cron. Check `last_run_at` within 5 minutes to confirm scheduler picked it up.

**Prevention:** After creating any new cron, wait one cycle and verify `last_run_at` is populated. A cron with `last_run_at: null` after its first scheduled time has never executed and needs investigation.
