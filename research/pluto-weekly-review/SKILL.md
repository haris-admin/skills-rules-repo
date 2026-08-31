---
name: pluto-weekly-review
description: Pluto's weekly operational self-assessment — reviews cron health, pipeline performance, research quality, and produces honest report with auto-improvement directives. Use for the Friday 11:05 PM AEST cron (cc5ca5690d05).
allowed-tools: [session_search, terminal, read_file, write_file, execute_code, search_files, skill_manage, memory]
---

# Pluto Weekly Self-Review

## When to Use
- Running the Friday 11:05 PM AEST cron job (`cc5ca5690d05`)
- Manual operational audit of Pluto's pipelines
- Post-mortem after a week of autonomous operation

## Pipeline

### Phase 1: Gather Data (run in parallel where possible)

1. **Get today's date and verify review directory:**
   ```bash
   date '+%Y-%m-%d' && ls ~/.hermes/reviews/weekly/ 2>/dev/null
   ```
   Create directory if missing: `mkdir -p ~/.hermes/reviews/weekly/`

1.5. **Check performance tracker data:**
   The daily performance tracker (cron `28bf484caedd`, 11:30 PM) accumulates weekly data. Check both the cron output and any snapshot files:
   ```bash
   ls -lt ~/.hermes/cron/output/28bf484caedd/ | head -5
   # Read the latest output for this week's cumulative error/warning counts
   cat $(ls -t ~/.hermes/cron/output/28bf484caedd/*.md | head -1) | head -20
   ```
   **IMPORTANT:** The tracker counts tool-level WARNING entries from `errors.log` as errors. This number (e.g., 136) does NOT mean 136 cron failures. Cross-reference with `jobs.json` — if all crons show `last_status: ok`, the tracker's number is tool noise, not real errors.

2. **List all cron jobs and their last-run status:**
   ```bash
   read_file ~/.hermes/cron/jobs.json
   ```
   This is the canonical source for all cron job metadata. Each entry has: id, name, schedule, last_run_at, last_status, last_error, enabled, state, completed count. Key signals to watch for:
   - **`last_run_at: null` + `completed: 0` despite being days old** → cron has NEVER executed. Critical failure. Check schedule syntax, gateway loading, and whether the cron was created while gateway was down.
   - ⚠️ **`completed: 0` is ALWAYS 0 for all crons** — this field is not a per-run counter. It does NOT mean "zero completed runs." All 36 crons show `completed: 0` even when running daily for weeks. Only use `completed: 0` in combination with `last_run_at: null` to detect never-executed crons. Never cite it alone as evidence of a problem.
   - **`last_status: "error"`** → Read `last_error` for the specific failure. Script-based crons often capture stdout here even for partial failures.
   - **`state: "paused"`** → cron was manually disabled. Note when and investigate.
   - **`enabled: true` but `last_run_at` is stale** → cron is scheduled but not firing.
   Use `hermes cron list` to get a formatted overview of all cron jobs with last_run_at and last_status. This IS available inside the agent session and is the preferred first pass. For detailed structured parsing (e.g., extracting `last_error` fields for script-based crons), also read `~/.hermes/cron/jobs.json` directly with terminal+Python.

3. **List research outputs from the past 7 days:**
   ```bash
   ls -la ~/.hermes/research_outputs/
   ```
   Count files by category: research_*.json, synthesis_*.md, actions_*.json, gumby-action-brief-*.md, skill-proposals_*.md, morning-briefing-*.md, linkedin-ideas_*.md, feedback/*.md

   **🆕 Synthesis file identical-size check (added W28):** If multiple synthesis JSONs show identical byte sizes (e.g., 23,740 bytes on Jul 12-14, 23,782 on Jul 15-16), run `diff -q` to confirm they're actually different:
   ```bash
   diff -q synthesis_2026-07-12.json synthesis_2026-07-13.json
   diff -q synthesis_2026-07-13.json synthesis_2026-07-14.json
   # etc.
   ```
   Files can legitimately have identical sizes (same JSON structure with different content). Only flag if `diff -q` reports them as identical (which would mean the pipeline produced duplicate output).

   **🆕 Competitor intel size analysis (added W28):** Systematically categorize competitor intel quality:
   ```bash
   for f in competitor_intel_2026-07-1*.json; do echo -n "$f: "; wc -c < "$f"; done
   ```
   Categorize: **187B = empty** (placeholder JSON), **500-1,500B = near-empty**, **1,500-3,000B = partial**, **>3,000B = meaningful**. Report "% meaningful" as a health metric.

4. **Check podcast KB episodes ingested this week:**
   The podcast knowledge base lives in **Supabase PostgreSQL**, not local SQLite. Query it via psql:
   ```bash
   PGPASSWORD='4SIsDTYfvHjAqC7Ygp8B89q7Q743eOC!' PGSSLMODE=require psql -h aws-1-ap-southeast-2.pooler.supabase.com -p 6543 -U postgres.vyqagemgwxfscppkfswq -d postgres -c "SELECT count(*), date(published_date) FROM podcast_kb.episodes WHERE date(published_date) >= 'DATE_START' AND date(published_date) <= 'DATE_END' GROUP BY date(published_date) ORDER BY date(published_date);"
   ```
   If the query fails (no network, auth error), fall back to checking the podcast ingestion logs:
   ```bash
   ls -la ~/.hermes/research_outputs/podcast_ingestion_*.log | sort
   cat ~/.hermes/research_outputs/podcast_ingestion_YYYYMMDD_HHMM.log
   ```
   Look for: "ingested so far: N new episodes", "IP blocked", "401 Unauthorized", or timeout errors.
   The podcast ingestion cron (`d4d77c41f6c0`) now uses a 3600s timeout — the Jun 14 test completed in 872s with 12 episodes. If the cron shows `last_status: error`, verify config: `grep script_timeout_seconds ~/.hermes/config.yaml` should show `3600`. The old cron `fabab82f804a` (LLM-driven) was deleted — don't reference it.

5. **Check honcho bridge push state:**
   ```bash
   cat ~/.hermes/research_outputs/.honcho_bridge_state.json
   ```
   Count pushed files this week, verify last run timestamp.

6. **Check feedback loop health:**
   ```bash
   ls ~/.hermes/research_outputs/feedback/feedback_*.md | sort
   ```
   Read the most recent feedback file to verify bidirectionality and utilization rates.

7. **Check git sync status:**
   The git sync cron (`c23dc3f73e2d`) is script-based with `deliver: local`. Its output is captured in the cron job's `last_error` field in `~/.hermes/cron/jobs.json` — even for "error" status, the field contains the full stdout. Read the field for the git_sync entry to see sync results. Check for:
   - Fetch failures: "fetch failed"
   - Merge failures: "merge failed"  
   - Total repos synced vs total discovered
   - Any repos that fail every single day (persistent failures)
   There is NO separate `git_sync_output.log` file — output is embedded in jobs.json.

8. **Session search for user interactions:**
   Use `session_search` with sort=newest to find any direct Haris interactions (non-cron sessions).
   ```bash
   session_search(query="user haris telegram direct interaction", sort="newest", role_filter="user", limit=3)
   ```
   Zero results across the entire week = no user feedback loop. Flag as MEDIUM severity.

8.5. **🆕 AMLHive Sentry alert trend comparison (added W28):**
   The 11PM fleet monitor reports contain alert severity counts. Compare across the full week to detect trends:
   ```bash
   # Count red alerts (🔴) per day to track severity trend
   for f in ~/.hermes/reviews/fleet/amlhive-monitor_2026-07-1[1-7]_2300.md; do
     echo -n "$(basename $f): "; grep -c "🔴" "$f" 2>/dev/null || echo "0"
   done
   ```
   Also read each 11PM monitor's opening summary (first 20 lines) to extract P0/P1/P2 counts and the "overall status" line. Track the trend:
   - **Spike then recovery** (e.g., 6→1→0) = issue was resolved
   - **Deploy-day spike** (e.g., 0→7→0) = deployment restart triggered alerts that self-resolved
   - **Persistent low-level** (e.g., 1,1,1) = recurring issue needs investigation
   - **Clean week** (0,0,0) = no Sentry issues detected

   When PII decryption errors (`Failed to decrypt PII`) appear on 3+ days, flag as persistent and recommend PII_ENCRYPTION_KEYS investigation.

9. **Read the latest skill extraction report** for patterns that qualified but weren't created:
   ```bash
   read_file ~/.hermes/research_outputs/skill-proposals_YYYY-MM-DD.md
   ```
   Look for the "Still Pending" section — these are skills with ≥2 qualifying cycles that haven't been created.

### Phase 2: Analyze — What Worked

Categories to assess:
- **Pipeline reliability:** Which crons ran every day? Any gaps in the daily cycle?
- **Research quality:** Gumby utilization rates from feedback files. Signal balance audit results.
- **New capabilities:** New scripts, new pipelines, new delivery channels added this week.
- **Automations:** What previously-manual process is now automated?
- **User requests fulfilled:** Any direct Haris interactions resolved?

**Honesty rule:** Report what the data shows, not what sounds good. A 100% utilization rate is worth highlighting. So is a cron that never fired.

### Phase 3: Analyze — What Didn't Work

Look for:
- **Cron failures:** Jobs showing errors, delivery failures, or never-executed states
- **Rate-limit blocks:** YouTube transcript API 429s, IP blocks
- **WSL boundary issues:** Path problems between /mnt/c/ and Linux filesystem
- **User corrections/repeats:** Any session where Haris had to repeat or correct something
- **Missed deadlines:** Anything that should have happened but didn't
- **Skill creation debt:** Patterns in skill proposals that qualified but weren't created

**Root cause analysis:** For each failure, identify WHY it happened, not just WHAT happened. "Podcasts not ingested" is the symptom. "Cron never executed despite active status" is closer to root cause.

### Phase 4: Analyze — What Could Be Better

Focus on **actionable improvements** the Saturday 12AM auto-improvement cron can implement:
- Config changes (cron schedule adjustments, delivery target fixes)
- Code changes (script fixes, new scripts)
- Skill creation (long-pending patterns)
- Process changes (add verification steps, fix false negatives)

Prioritize by impact. What single fix would have the biggest effect next week?

### Phase 5: Write the Report

**Format — Markdown** to `~/.hermes/reviews/weekly/weekly-review-{DATE}.md`:

```markdown
# Pluto Weekly Review — Week Ending {Friday Date}

## 📊 By the Numbers
- Pipelines run: N
- Successes: N | Failures: N
- New episodes ingested: N
- Repos synced: N
- User requests handled: N

## ✅ What Worked
- Item with evidence

## ❌ What Didn't Work
- Item with root cause

## 🔧 Improvements for Next Week
- [ ] Actionable item (priority: High/Med/Low)
- [ ] ...

## 🤖 Auto-Improvements (to be implemented Sat 12AM)
- [ ] Specific code/config change
- [ ] ...

## 📈 Trend Analysis
| Metric | Last Week | This Week | Δ |

*Generated by Pluto Weekly Review (cron: cc5ca5690d05) — {DATE} 11:05 PM AEST*
```

**Format — JSON** to `~/.hermes/reviews/weekly/weekly-review-{DATE}.json`:

```json
{
  "report_date": "YYYY-MM-DD",
  "generated_by": "pluto-weekly-review",
  "cron_id": "cc5ca5690d05",
  "summary": {
    "total_crons": 18,
    "pipeline_cycles": 7,
    "podcast_episodes_ingested": 0,
    "user_interactions": 0
  },
  "what_worked": ["..."],
  "what_didnt_work": [
    {"severity": "critical|high|medium|low", "issue": "...", "root_cause": "..."}
  ],
  "improvements": {
    "critical": ["..."],
    "high": ["..."],
    "medium": ["..."],
    "low": ["..."]
  },
  "auto_improvements_saturday": ["..."],
  "trends": {
    "pipeline_cycles": {"current": 7, "previous": 7, "delta": 0}
  }
}
```

### Phase 6: Deliver

The report content becomes the cron job's final response. The system delivers it to the configured destination. Do NOT use send_message — just write the files and produce the report as your response.

If there is genuinely nothing to report (no crons ran, no files produced, no changes), respond with exactly `[SILENT]` to suppress delivery.

## New Diagnostics

### 🟡 Podcast Ingestion False-Positive Error — ✅ RESOLVED (July 4, 2026)

**Root cause:** `run_sql()` passed SQL via `psql -c "<sql>"` — a command-line argument. When a podcast transcript exceeded ~128KB, the total `argv` size exceeded the OS ARG_MAX limit, causing `[Errno 7] Argument list too long: 'psql'`. The script successfully ingested 6-10 episodes before hitting the long transcript and crashing with exit code 1.

**Fix:** Changed `run_sql()` in `podcast_ingestor.py` to pipe SQL via stdin using `subprocess.run(..., input=sql)` instead of `psql -c`. Deployed July 4, 2026.

**Verification:** Cron `d4d77c41f6c0` now shows `last_status: ok` daily. All 7 runs Jul 4-10 show `ok`. This was the #1 cron error for 3+ weeks.

**Pitfall:** If the error ever returns, check whether `/tmp/podcast_venv/` still exists (WSL restarts clear /tmp). If it's an ARG_MAX on a new command, the stdin-piping pattern generalizes.

### 🟡 Podcast Ingestion — Venv Evaporation (WSL Restart)

**Symptom:** Podcast ingestion cron shows `last_status: error` with ~500-byte error output containing `No such file or directory` for yt-dlp or the podcast venv. All 16 podcasts fail because the venv is gone.

**Root cause:** `/tmp/podcast_venv/` is cleared on WSL restart or `/tmp` cleanup. The venv with yt-dlp and its dependencies evaporates.

**Detection:** Check `ls /tmp/podcast_venv/bin/yt-dlp`. If missing, the venv needs rebuilding. Also check cron output size — ~500 bytes = venv missing (quick failure), 2,000-4,000 bytes = partial success with ARG_MAX or timeout (fixed July 4).

**Fix:** Rebuild venv: `python3 -m venv /tmp/podcast_venv && /tmp/podcast_venv/bin/pip install yt-dlp`. Long-term: move to persistent location like `~/.hermes/venvs/podcast/`.

### 🔴 TapEase Bridge HTML Error Page (All 4 Monitors) — Updated July 3, 2026

**Symptom:** Cron `e5675447ed37` shows `last_status: error` with `imaplib.IMAP4.error: b'[AUTHENTICATIONFAILED] Invalid credentials (Failure)'` on every run. The `.gmail_ingestor_state.json` file stops updating.

**Root cause:** The Gmail app password has expired or been revoked. Google app passwords expire periodically and must be regenerated.

**Detection:** `grep 'AUTHENTICATIONFAILED'` on the cron output for `e5675447ed37`. If it appears on every run for multiple days, the password is dead.

**Impact:** The Gmail→Perplexity signal pipeline goes completely dark. Zero external intelligence enters Pluto's research pipeline from this source. Morning briefings operate from a shrinking information base.

**Fix:** Haris must generate a new Gmail app password at https://myaccount.google.com/apppasswords and update the credential in the script or environment variable. Pluto cannot fix this — it requires human Google account access.

**Reporting:** When this failure is detected, flag as CRITICAL in both the Friday review and the Saturday user-facing review. Include: how many days it's been failing, what intelligence sources are affected, and the exact human action needed.

### 🟡 AMLHive 11PM Fleet Monitor — Exit Code 1 Is BY DESIGN (Added July 10, 2026, Verified July 11)

**Symptom:** Cron `be5061d19a5a` shows `last_status: error` with `Script exited with code 1`. But stderr shows `✅ Email sent to 1 recipients` and the stdout contains a complete, detailed fleet monitor report.

**Root cause:** `amlhive_prod_monitor.py` intentionally exits with code 1 when P0 alerts exist OR >2 P1 alerts exist (lines 1314-1321: `if p0_count > 0: return 1; if p1_count > 2: return 1`). This is documented in the `pluto-fleet-monitor` skill: "Script must exit 0 for healthy, 1 for issues — but email is the alert mechanism, not exit code."

**The 11PM run is the most likely to exit 1** because it catches the accumulated day's errors. PII encryption errors, Redis connection refused, and Application startup failures all generate P0/P1 alerts that push the count above the threshold. This is NOT a cron failure — the script is working exactly as designed.

**Detection:** Check whether stderr contains `✅ Email sent` and stdout contains complete report sections. If so, the monitor ran successfully and found real issues. Count the P1/P0 alerts from the report body, not from the exit code.

**Reporting:** Do NOT report this as a cron failure. The exit code is a signal, not an error. Instead, report the actual alerts found (Sentry errors, CloudWatch alarms, etc.). If the 11PM run consistently exits 1 and the other 3 runs exit 0, check whether the issues are time-specific (e.g., batch jobs triggering at midnight).

### 🔴 Daily Learning — False Negative (Output Exists, Wrong Location) (Added July 17, 2026)

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

### 🟡 Cron Output Misrouting — General Pattern (Added July 17, 2026)

**Generalization of the daily learning pattern:** Any cron can produce real output that goes to the wrong location. The `cron/output/<job_id>/` directory captures all output from that cron, but the scripts/prompts may not save to the expected `research_outputs/` path. This creates silent false negatives in pipeline completeness checks.

**Detection in Phase 1 (research outputs check):** After listing `research_outputs/` files, cross-reference against `cron/output/` for any pipeline cron that shows "0 files" but is known to run. Key crons with expected research_outputs paths:
- `0fb6bf47f704` (Daily Learning) → expected: `research_outputs/daily-learning-*.md`
- `d4d77c41f6c0` (Podcast Ingestion) → expected: `research_outputs/podcast_insights.md`
- `2d33c8f9a89c` (Skill Extractor) → expected: `research_outputs/skill-proposals_*.md`

**Pattern:** `ls -la ~/.hermes/cron/output/<job_id>/ | grep $(date +%Y-%m)` — if files exist here but NOT in research_outputs/, output is misrouted.

### 🟡 Competitor Intel — Empty Output Pattern (187 Bytes) (Added July 10, 2026)

**⚠️ Dependency chain (W32, Aug 15):** `competitor_intel.py` output is consumed by `briefing_improver.py` at 5:20 AM (`competitor_intel_{today}.json`). Do NOT schedule competitor intel after 5:20 — a W32 suggestion to move it to 5:25 would have permanently suppressed the competitor section from the briefing. Correct fix: keep it before 5:20 (moved 5:07 → 5:12), plus a poll/fallback inside the script for slow Morning Research. Also: the Chamber Refresh cron can show `last_status: ok` while feeding 0 items (chromadb import failure) — always check the feed footer (`Fed N new item(s)`), not just `last_status`.

**Symptom:** `competitor_intel_*.json` files are exactly 187 bytes on some days. These contain essentially empty JSON (`{"results": [], ...}` or similar placeholder structure).

**Detection:** `wc -c ~/.hermes/research_outputs/competitor_intel_2026-07-*.json | grep '187 '`. If more than 50% of files in a week are 187 bytes, the competitor intel source is degraded.

**Root cause (suspected):** Rate limiting on the competitor data source, source format change, or scraping targets returning empty results. The `competitor_intel.py` script lacks debug logging — no way to determine cause from cron output alone.

**Reporting:** Count "meaningful" vs "empty" runs. If <50% of runs produce real output, flag as MEDIUM degradation and recommend adding debug logging to the script.

**Note:** The TapEase monitors self-healed in Week 26 (Jun 27-Jul 3). All 4 monitors went from 0/28 to 28/28 without an explicit code fix. The root cause (Windows bridge route returning HTML instead of JSON) may have been resolved by a bridge restart, WSL restart, or environmental change. The pattern can recur if the underlying bridge code issue isn't fixed.

**Recovery detection:** If all 4 monitors transition from `JSONDecodeError` → `status: ok` simultaneously, the recovery was environmental (bridge restart). Report as "recovered — environmental, root cause unknown, may recur."

**Symptom:** All TapEase Fleet Monitors (`dbd3cb1b5bd3`, `582bd225ddd1`, `1086e6405da1`, `be81c61778a8`) show `last_status: error` with `JSONDecodeError: Expecting value: line 1 column 1 (char 0)`.

**Root cause:** The Windows bridge at port 18796 returns HTTP 200 on `/health` but the `/tapease/monitor` endpoint returns an HTML error page instead of JSON. The Express route handler is either missing or throwing an unhandled error.

**Detection:** `grep 'JSONDecodeError.*Expecting value'` on the cron output for any TapEase monitor. Bridge is alive but the monitor route is broken — NOT a bridge-down situation (which would give "No response from bridge" instead).

**Fix:** Debug the Windows-side Express route handler for `/tapease/monitor`. See `windows-bridge-management` skill. This is a bridge code issue, not a cron configuration issue.

**Impact on weekly review:** When all 4 TapEase monitors show identical JSONDecodeError, report as a single bridge issue (1 root cause, 4 affected crons), not 4 separate cron failures. Count them as 1 problem with 4 cron symptoms.

### 🔴 Pluto Fleet Monitor — AML Hive 5PM Venv Missing

**Symptom:** `a0b1f0f642af` (5PM run) fails with `No such file or directory: '/home/habib/.hermes/repo/venv/bin/python'`. The 11AM and 11PM runs succeed.

**Root cause:** The 5PM run script references a different Python venv path. The 11AM/11PM runs use a different venv (likely `~/.hermes/venv/bin/python3` which exists).

**Detection:** Compare the venv path in the cron's script field against the 11AM/11PM runs. Different paths = partial failure.

**Fix:** Either create `~/.hermes/repo/venv/` with required deps, or change the 5PM run to use the same venv as the 11AM/11PM runs.

### 🟡 Saturday Auto-Improvement Pipeline: Reports ≠ Action

**Pattern confirmed (June 20, June 26, June 27):** The Saturday auto-improvement cron (`159702fe072c`) produces comprehensive Phase 1-5 reports with "fixes deployed" claims, but the actual code changes are rarely applied.
- **Week 23 (Jun 13):** 0/8 directives implemented.
- **Week 24 (Jun 20):** 1/4 (25%) — only Performance Tracker fix applied.
- **Week 25 (Jun 26):** 3/8 (37.5%) — podcast venv rebuilt, git-sync skill created, performance-tracker skill created. Still missed: SKIP_REPOS, vercel monitor, Daily Maintenance patch, Saturday pipeline fix.
- **Week 26 (Jun 27):** Saturday report claimed Phase 3 "2 Skills Created" (verified: git-sync at Jun 27 00:07, performance-tracker at Jun 27). Phase 4 "1 Unfixable" (TapEase bridge — environmental recovery occurred independently later in the week). SKIP_REPOS still not added.

**Trend:** Implementation rate is slowly improving (0% → 25% → 37.5%) but still below 50%. The Saturday cron consistently creates skills (Phase 3) but skips code patches (Phase 4) and structural fixes.

**Detection in weekly review:** Cross-reference the Saturday improvements report's "fixes deployed" claims against the actual files:
```bash
# After reading Saturday improvements report, verify claimed fixes:
grep "SKIP_REPOS" ~/.hermes/scripts/git_sync.py          # Should exist if fixed
grep "No deployments" ~/.hermes/scripts/vercel_monitor.py # Should NOT alert if fixed
```

**Fix for Saturday cron:** The prompt must explicitly say "EXECUTE these actions, then VERIFY each one. Use read_file/grep to confirm the change was written before claiming it as done." The current prompt allows the LLM to write a report about fixes without applying them.

**Impact on weekly review:** The `auto_improvements_saturday` section in the JSON report must use ACTION language (not "consider" or "review"). Each item must include a verification command. The Saturday cron must be directed to stop after each action to verify.

### 🟡 Skill Extractor "All Matched" False Negative

**Pattern:** The Skill Extractor (`2d33c8f9a89c`) produces 0 proposals for 5+ consecutive days (Jun 22-26) claiming "none — all recent scripts have matching skills." But 2 proposals from Jun 20 (`git-sync` and `pluto-performance-tracker`) remain PENDING — the skills were never actually created.

**Detection:** In the weekly review, cross-reference `skill-proposals_*.md` files against `skills_list`:
```bash
# Check if proposed skills actually exist
skill_manage(action='list') | grep -i "git-sync\\|performance-tracker"
```

**Root cause:** The extractor tracks proposal existence (a file was generated) but NOT creation (a skill was actually registered). After generating a proposal, if it's not acted on, the extractor considers the script "matched" on subsequent runs because it sees the proposal file exists — even though the skill doesn't.

**Fix for weekly review:** Always cross-check the "Still Pending" list from the latest skill-proposals file against actual registered skills. Flag any proposal that exists on disk but not in the skill registry.

### 🔴 Gateway Shutdown — Simultaneous Cron Kills (Added July 24, 2026)

**Pattern discovered W29:** When the Hermes gateway shuts down for maintenance or restart, it sends `final-cleanup` signals that kill ALL running tool subprocesses simultaneously. Multiple crons that happen to be running at the same timestamp will all show `last_status: error` with identical `last_run_at` values and the same error: "Gateway shutdown (final-cleanup) killed the job's tool subprocess before the run finished."

**Detection:** Look for crons sharing the same `last_run_at` timestamp with the gateway-shutdown error. In W29, `4eef20ef0e25` (Hermes Update Check) and `d4d77c41f6c0` (Podcast KB Ingestion) were both killed at `2026-07-24T04:04:42`.

**Reporting:** Group these together. Count them as "transient — gateway restart" in the error tally, NOT as separate cron-specific failures. Do not escalate. These are infrastructure events, not script bugs.

### 🔴 AML Hive Daily Business Report — DB Password Auth Failure (Added July 24, 2026; RESOLVED Aug 6, 2026)

**Status: RESOLVED.** Fixed by switching from AWS Secrets Manager to SSM Run Command for RDS password retrieval. The cron (`3ebed4e59ee3`) resumed producing output on Aug 6 after a 7-day outage.

**Original pattern:** `psql: FATAL: password authentication failed for user "amlhive"` on `amlhive-prod.ch4ykiy82n3q.ap-southeast-2.rds.amazonaws.com`. The `amlhive_daily_report.py` script fetches the RDS password via AWS SSM — when the SSM parameter changes or the IAM role loses access, the script crashes.

**Detection:** `RuntimeError: SSM: psql: error: ... FATAL: password authentication failed` in `3ebed4e59ee3` output.

**Impact when failing:** Daily business report goes dark for all affected days.

**Fix applied:** Switched from Secrets Manager lookup to SSM Run Command approach. If the error returns, check SSM Run Command IAM permissions or RDS password rotation status.

### 🟡 Git Index Lock on /mnt/c/ Filesystem (Added July 24, 2026)

**Pattern discovered W29:** `fatal: Unable to create '.git/index.lock': File exists.` on repos under `/mnt/c/Code/github/`. Another git process on the Windows side (VS Code, GitHub Desktop) holds a stale lock that blocks WSL git operations.

**Detection:** `GIT_RESET_FAILED` in `0dbba3db3116` output. The lock is on `/mnt/c/Code/github/almhive-tech/amlhive1/.git/index.lock`.

**Fix:** Add `rm -f` retry logic before git operations on /mnt/c/ repos. The lock is almost always stale.

### 🟡 Test Suite Exit Code 1 With 838+ Passing Tests (Added July 24, 2026)

**Pattern discovered W29:** `044c0bc41e31` (AMLHive Daily Test Suite) exits code 1 despite 838 tests passing. A few tests are failing but the cron output is truncated — specific failures are invisible.

**Detection:** `Script exited with code 1` + `838 passed` visible in stdout. The failing test names are not captured in the cron output.

**Fix:** Either increase truncation limit or have the script write test failures to a dedicated file for diagnostic access.

### 🟡 ASIC Intentionally Disabled — Should Exit 0 (Added July 24, 2026)

**Pattern discovered W29:** User's standing order (from memory) is "no asic trying for now." The ASIC Ref-DB sync script exits code 1 when `CSV URL for asic-registered-schemes is not configured`. The `acnc-charities` portion works fine independently.

**Detection:** `HTTP 503 — "CSV URL for asic-registered-schemes is not configured (set the env var)"` in `937bb914c497` output.

**Fix:** Script should check if ASIC is intentionally disabled (missing env var = disabled) and exit 0. Only exit 1 on actual connection/auth failures.

### 🟡 Honcho Bridge State File — Unbounded Growth (Added July 24, 2026)

**Pattern:** `.honcho_bridge_state.json` accumulates every pushed file since inception (85+ entries in the `pushed_files` array). The array grows without bound.

**Detection:** `wc -l ~/.hermes/research_outputs/.honcho_bridge_state.json` — if above 100 lines, the array is growing.

**Fix:** Either rotate weekly (keep last 14 days) or use a hash set for deduplication.

### 🟡 Security Scan Cron — Never Executed (Added Aug 7, 2026)

**Pattern:** Cron `7059cc6796d6` (🛡️ Pluto Weekly Security Scan, Fri 5PM) exists in `jobs.json` with `last_run_at: null`, `completed: 0`, and `enabled: true` despite being created. Classic never-executed anti-pattern.

**Detection:** `last_run_at: null` + `enabled: true` + cron was created days/weeks ago. The scheduler never triggered it.

**Root cause (suspected):** Gateway may not have been running when the cron was created, or a schedule parsing bug. The schedule `0 17 * * 5` is syntactically correct.

**Fix:** Verify gateway is running, then delete and recreate the cron. Check `last_run_at` within 5 minutes to confirm scheduler picked it up.

**Prevention:** After creating any new cron, wait one cycle and verify `last_run_at` is populated. A cron with `last_run_at: null` after its first scheduled time has never executed and needs investigation.

## Reference Files
- `references/cron-diagnostics.md` — Cron health diagnostic patterns: never-executed crons, gateway false negatives, delivery failures
- `references/w28-diagnostic-findings.md` — W28 (Jul 17, 2026) key discoveries: daily learning false negative, synthesis size check, Sentry trend analysis, cron output misrouting, competitor intel categorization
- `references/w29-diagnostic-findings.md` — W29 (Jul 24, 2026) key discoveries: gateway shutdown simultaneous kills, DB password auth failure, git index lock on /mnt/c/, test suite exit-1 with passing tests, ASIC intentionally-disabled exit code, daily learning summary-vs-full content, honcho bridge state file unbounded growth
- `references/w31-diagnostic-findings.md` — W31 (Aug 7, 2026) key discoveries: RDS password RESOLVED (SSM approach), error detection false positives from pattern matching, competitor intel --debug flag not passed by cron, Security Scan never-executed, Supabase inaccessible fallback to cron output parsing, A2Square Playwright failures, podcast ingestion Aug 3 gap

## Cron Health Diagnostics

### Identifying Never-Executed Crons
In `~/.hermes/cron/jobs.json`, look for crons where **`last_run_at: null` AND `completed: 0`** despite being created days ago. This is a critical failure — the cron is configured in jobs.json but the scheduler has never triggered it. Common causes:
- Gateway was not running when the cron was created → scheduler never picked it up
- Cron schedule syntax error (e.g., `0 2 * * 4` when the day-of-week field is wrong)
- Cron created but scheduler not reloaded
- Script path doesn't exist or isn't executable

**Verification:** Check `last_status` — if it's also `null`, the cron has never been attempted. This is different from `last_status: "error"` which means it ran but failed.

### Gateway Running Check (False Negative Alert)
The `hermes cron list` CLI warning "⚠ Gateway is not running — jobs won't fire automatically" can be a false positive. Always verify with:
```bash
ps aux | grep "hermes gateway"
```
If the gateway process exists, the warning is stale. Ignore it but flag it for investigation. The `hermes cron list` CLI IS available inside the agent session and is the preferred first-pass tool for cron health checks.

### Delivery Failures
Check `last_delivery_error` in jobs.json. A cron showing a delivery error means the output can't reach the user. Fix by changing `deliver` to `local` or configuring a delivery target.

### Stale Stream / Broken Pipe Pattern — ✅ FIXED (June 14, 2026)
**Root cause:** `deepseek-v4-flash` streaming connection stalled after 180-240s of silence. DeepSeek kills the connection → Hermes sees `[Errno 32] Broken pipe`.
**Fix applied to ALL LLM-driven crons:** All cron jobs that use an LLM (`no_agent: false`) were upgraded from `deepseek-v4-flash` to `deepseek-v4-pro` on June 14, 2026. The pro model handles long contexts without connection drops. Jobs affected: Morning Research, Morning Briefing, Cross-Chamber Synthesis, Action Bridge, Daily Maintenance, LinkedIn Ideas, Moonshots Learning, Podcast Insight Extractor, Weekly Review, Weekly Improvements, Saturday Review, Sunday Pulse.
**Verification:** Daily Maintenance ran on pro at 19:20 Jun 14 with zero errors. Previously it failed every 2PM run with broken pipe.
**This issue is CLOSED. Do not re-flag.** If a `no_agent: false` cron still shows `model: deepseek-v4-flash`, it's running a different config than the current fleet — check `cronjob list`.

## Pitfalls

- **Cron "ok" status is not proof of execution.** A cron can report `last_status: ok` but produce zero output. Always verify output files exist and have content.
- **`last_run_at: null` + `completed: 0` on an old cron = NEVER EXECUTED.** This is a critical failure distinct from "errored." The cron was created but the scheduler never triggered it. Common causes: gateway was down when cron was created, schedule syntax error, or a bug in cron loading. The A2Square Mon/Thu crons are known examples (created Jun 8, still never ran by Jun 12).
- **Vercel Monitor "error" is usually a false positive.** `vercel_monitor.py` exits with code 1 for "no deployments in 12 hours" — which is normal for a static project. Check stdout/stderr content, not just the status code. Real errors are API failures or network issues.
**🔴 MANDATORY: Cross-reference ALL flagged issues before reporting.**

Before this review flags ANY cron issue as a real problem, run the cross-reference verifier:

```bash
python3 ~/.hermes/scripts/cross_ref_verify.py <job_id> "<claimed issue>"
```

Exit codes:
- `0` = inconclusive — investigate manually
- `1` = CONFIRMED — report with evidence
- `2` = FALSE POSITIVE — do NOT report. Suppress silently.

Then run the fleet-wide health scan:
```bash
python3 ~/.hermes/scripts/cron_verify.py --issues-only
```

This separates true issues from false flags (cosmetic model fields on no_agent jobs, old error states on healthy scripts, etc.). The cross_ref_verify.py script checks:
- Is the cron `no_agent: true`? If so, LLM-related claims (broken pipe, model issues) are false positives.
- Does `jobs.json` say status=ok and do output files look clean? Then the job is healthy.
- Does the pipeline-orchestration skill say "RESOLVED"? Then don't re-report.

## Pitfalls

- **Cron \"ok\" status is not proof of execution.** A cron can report `last_status: ok` but produce zero output. Always verify output files exist and have content.
- **`last_run_at: null` + `completed: 0` on an old cron = NEVER EXECUTED.** This is a critical failure distinct from \"errored.\" The cron was created but the scheduler never triggered it. Common causes: gateway was down when cron was created, schedule syntax error, or a bug in cron loading. The A2Square Mon/Thu crons are known examples (created Jun 8, still never ran by Jun 12).
- **Vercel Monitor \"error\" is usually a false positive.** `vercel_monitor.py` exits with code 1 for \"no deployments in 12 hours\" — which is normal for a static project. Check stdout/stderr content, not just the status code. Real errors are API failures or network issues.
- **Podcast Ingestion venv evaporates on WSL restart.** `/tmp/podcast_venv/bin/yt-dlp` disappears when WSL reboots or `/tmp` is cleaned. The cron will show `last_status: error` with \"No such file or directory.\" Fix: rebuild venv. Long-term: move to persistent location. Check during the weekly review by verifying the last 3 days of podcast cron output — if all show ~500 bytes (error), the venv is missing.
- **TapEase 4x monitors failing with identical JSONDecodeError = single bridge issue.** Don't report as 4 separate cron failures. The root cause is the Windows bridge `/tapease/monitor` route returning HTML instead of JSON. All 4 crons are healthy — the bridge code is broken.
- **Saturday auto-improvements report claiming fixes that weren't applied.** The Saturday cron (`159702fe072c`) writes reports about fixes instead of executing them. Cross-reference the Saturday report's claims against actual file contents. If the Saturday report says \"3 scripts fixed\" but grep shows the old code, flag it. This is a structural issue with the Saturday prompt, not a one-off failure.
- **Skill Extractor says \"all matched\" when proposals are pending.** The extractor tracks proposal file existence, not skill creation. If `skill-proposals_*.md` exists but no matching skill in the registry, proposals are PENDING — overwrite the extractor's \"none\" finding.
- **Performance Tracker error count is misleading.** `pluto_performance_tracker.py` reads `errors.log` which contains WARNING-level tool execution entries — not cron execution errors. When the numbers conflict, trust `jobs.json` for cron health. Use the tracker for tool-warning trends only.
- **Podcast KB is in Supabase (PostgreSQL), not local SQLite.** Query Supabase for episode counts. Local SQLite paths are stale. **Column names: use `published_date` (NOT `published_at` or `created_at`).** The table schema uses `published_date` for the episode publication date. Using `created_at` or `published_at` returns `ERROR: column does not exist`. See `pluto-pipeline-orchestration/references/supabase-stale-data-queries.md` for all correct column names.
- **Git sync output is in the cron's `last_error` field, not a log file.** Script-based crons with `deliver: local` embed stdout in `last_error`.
- **DO NOT use `read_file` to parse `jobs.json` — use `terminal` + Python instead.** `read_file` returns line-number prefixes that break `json.loads()`.
- **`session_search` can return extremely large outputs for broad queries.** Use specific queries with low `limit` values. Even targeted queries can produce 500KB-900KB of output if the matched session is a long cron execution (e.g., morning research pipelines). When searching for user interactions, use `role_filter: "user"` to filter out cron system messages. For very large results, use session_search in discovery mode first, then scroll into specific sessions by session_id + around_message_id rather than letting the full transcript flood your context.
- **🆕 Daily learning pipeline is likely running — output is just misrouted.** The cron `0fb6bf47f704` produces 60-68KB of real output daily in `cron/output/0fb6bf47f704/`. If `research_outputs/daily-learning-*.md` is empty, check the cron output directory BEFORE reporting "0/7." This has been a false negative in weekly reviews for multiple weeks. (Added W28, July 17, 2026)
- **🆕 Daily learning location fixed but files are summaries.** W29 update: the misrouting is fixed (7/7 in research_outputs/) but files are 1.6-3.4KB — only ~4% of the full 68KB cron output. The cron prompt likely writes a summary to research_outputs/ while full output goes to cron/output/. After the W28 fix, verify file sizes: compare `wc -c research_outputs/daily-learning-*.md` against `wc -c cron/output/0fb6bf47f704/*.md`. If research_outputs files are <10% of cron/output size, the prompt needs further updating to write the FULL content. (Added W29, July 24, 2026)
- **🆕 Identical synthesis file sizes don't mean identical content.** The synthesis JSONs frequently have identical byte sizes (same JSON structure, different content). Always run `diff -q` to confirm before flagging as suspicious. Only flag if they are truly identical (duplicate output). (Added W28, July 17, 2026)
- **🆕 Cron output misrouting is a general failure mode.** Any cron can produce real output that lands in `cron/output/<job_id>/` instead of `research_outputs/`. When a pipeline cron shows "0 files" but is known to run, cross-check `cron/output/<job_id>/` before reporting failure. Key crons: `0fb6bf47f704` → `research_outputs/daily-learning-*.md`, `d4d77c41f6c0` → `research_outputs/podcast_insights.md`, `2d33c8f9a89c` → `research_outputs/skill-proposals_*.md`. (Added W28, July 17, 2026)
- **🆕 Error detection by output-file pattern matching produces massive false positives.** Simple keyword matching (`error`, `fail`, `exception`) catches benign strings like "errors: 0", "No errors found", "[SILENT]", and fleet monitor reports that end with "0 errors." In W31, naive pattern matching reported 205 "errors" from 445 runs when the real error count from `jobs.json` `last_status` was only 4. **Use `jobs.json` `last_status` as the canonical truth for cron health.** Only crons with `last_status: "error"` are real failures. Read output files for context AFTER identifying failed crons from `jobs.json`, not as the primary detection method. (Added W31, Aug 7, 2026)

- **🆕 Adding a flag to source code doesn't mean the cron passes it.** The W30 auto-improvement added `--debug` to `competitor_intel.py`, but the cron job config in `jobs.json` may not include `--debug` in its script invocation. When verifying that a fix was applied, check BOTH the source code AND the cron job config. Code changes without cron config updates are invisible at runtime. (Added W31, Aug 7, 2026)

- **🆕 Supabase queries may fail — fall back to parsing cron output files.** The podcast episode count can be accurately derived from `d4d77c41f6c0/*.md` cron output using regex `New: (\d+) episodes`. This is richer than a simple count query (includes per-podcast breakdowns, transcript status, errors). When Supabase is unreachable (no module, stale credentials), this fallback is reliable and fast. (Added W31, Aug 7, 2026)

- **🆕 The "Last Week's Fixes" table can be WRONG in BOTH directions.** The Saturday improvements report may claim fixes that don't exist in code (false positive — reported but not done) OR may be silent about fixes that DO exist (false negative — done but reported as NOT DONE). **Never trust the Saturday report's claims.** Always verify both directions:
  ```bash
  # Verify a claim that a fix IS applied:
  grep "<expected_pattern>" ~/.hermes/scripts/<script>.py  # Should find it
  
  # Verify a claim that a fix is NOT applied:
  grep "<fix_pattern>" ~/.hermes/scripts/<script>.py        # May actually be there
  ```
  **Week 25 (Jun 26) example:** The Saturday report claimed Vercel Monitor and Git Sync fixes were \"NOT DONE.\" Grepping the actual code proved both were applied. The Friday review repeated the Saturday report's error instead of checking the source of truth (the scripts).
  **Week 27 (Jul 3) example:** The Friday review claimed `SKIP_REPOS` wasn't added to `git_sync.py`. In reality, `KNOWN_DEAD_REPOS = {'ideas-ndis', 'ideas-exitlens', ...}` was on line 25 and used at line 242 since June 20. The review confused the variable name (`KNOWN_DEAD_REPOS` vs `SKIP_REPOS`) and assumed absence without grepping. **Pattern:** If the Saturday report says a fix was or wasn't done, verify with grep BEFORE reporting it. The scripts are the truth; the report is hearsay.
- **🆕 Gateway shutdown errors at identical timestamps are NOT individual failures.** When multiple crons show `last_error: "Gateway shutdown (final-cleanup) killed the job's tool subprocess"` with the same `last_run_at` timestamp, they were all killed by a single gateway restart. Group them as "transient — gateway restart" and count them as 1 issue, not N separate failures. Do not escalate. In W29: `4eef20ef0e25` and `d4d77c41f6c0` both killed at `2026-07-24T04:04:42`. (Added W29, July 24, 2026)

## Relationship to Other Skills

- **`pluto-autonomous-research`** — The weekly review assesses the research pipeline's performance. Research quality metrics come from feedback files.
- **`pluto-skill-extraction`** — The weekly review reads the skill extraction reports to find long-pending skills. The auto-improvement cron then creates them.
- **`pluto-mempalace-bridge`** — The weekly review checks honcho bridge push health via `.honcho_bridge_state.json`.
- **`pluto-pipeline-orchestration`** — The Friday review is an internal diagnostic. The **Saturday Weekly Review** (`7d24b37a03f2`) is the user-facing retrospective that delivers to Telegram with performance data, repo audit, signals, 3 build options, and improvements.
- **Performance Tracker** (`pluto_performance_tracker.py`, cron `28bf484caedd`) — Runs daily at 11:30 PM, feeds cumulative weekly data to the Saturday review. The Friday review should reference the performance tracker data when available.

## Pipeline Integration

```
Fri 11PM ──► Internal Weekly Review ──► Sat 12AM Auto-Improvements
(cc5ca5690d05)   (deliver: local)        (159702fe072c) implements fixes

11:30PM Daily ──► Performance Tracker ──► Sat 6AM Weekly Review
(28bf484caedd)   (accumulates data)        (7d24b37a03f2) delivers to Telegram
```

The Friday review is **internal diagnostic**. The Saturday review is **user-facing delivery**. Both use the same data sources but different formats and audiences.
