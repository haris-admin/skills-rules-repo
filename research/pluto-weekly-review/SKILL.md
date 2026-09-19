---
name: pluto-weekly-review
description: Pluto's weekly operational self-assessment — reviews cron health, pipeline performance, research quality, and produces an honest report with auto-improvement directives. Use for the Friday 11:05 PM AEST cron (cc5ca5690d05), for a manual operational audit of Pluto's pipelines, or for a post-mortem after a week of autonomous operation.
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
   PGPASSWORD='...'' PGSSLMODE=require psql -h aws-1-ap-southeast-2.pooler.supabase.com -p 6543 -U postgres.vyqagemgwxfscppkfswq -d postgres -c "SELECT count(*), date(published_date) FROM podcast_kb.episodes WHERE date(published_date) >= 'DATE_START' AND date(published_date) <= 'DATE_END' GROUP BY date(published_date) ORDER BY date(published_date);"
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

## Resolved and Historical Incidents

Before flagging any cron issue as new, check whether it's a known pattern. This includes several BY-DESIGN non-failures (e.g. the AMLHive 11PM fleet monitor's exit code 1 is intentional, not a bug) and several RESOLVED issues that should not be re-flagged (podcast ingestion ARG_MAX crash, AML Hive DB password auth). Full write-ups — podcast ingestion false positives and venv evaporation, TapEase bridge HTML errors, the AMLHive fleet-monitor exit-code design, daily-learning output misrouting (general pattern), competitor intel empty-output detection, the Saturday auto-improvement "reports vs action" trend across multiple weeks, the skill-extractor false-negative, gateway-shutdown simultaneous kills, git index-lock on /mnt/c/, test-suite exit-1-with-passing-tests, the intentionally-disabled ASIC sync, honcho bridge state growth, and the never-executed security-scan cron — are in [references/resolved-and-historical-incidents.md](references/resolved-and-historical-incidents.md).

## Reference Files
- `references/cron-diagnostics.md` — Cron health diagnostic patterns: never-executed crons, gateway false negatives, delivery failures
- `references/w28-diagnostic-findings.md` — W28 (Jul 17, 2026) key discoveries: daily learning false negative, synthesis size check, Sentry trend analysis, cron output misrouting, competitor intel categorization
- `references/w29-diagnostic-findings.md` — W29 (Jul 24, 2026) key discoveries: gateway shutdown simultaneous kills, DB password auth failure, git index lock on /mnt/c/, test suite exit-1 with passing tests, ASIC intentionally-disabled exit code, daily learning summary-vs-full content, honcho bridge state file unbounded growth
- `references/w31-diagnostic-findings.md` — W31 (Aug 7, 2026) key discoveries: RDS password RESOLVED (SSM approach), error detection false positives from pattern matching, competitor intel --debug flag not passed by cron, Security Scan never-executed, Supabase inaccessible fallback to cron output parsing, A2Square Playwright failures, podcast ingestion Aug 3 gap

## Cron Health Diagnostics

The canonical health signals live in `~/.hermes/cron/jobs.json`: `last_run_at: null` + `completed: 0` on an old cron means it has NEVER executed (distinct from `last_status: "error"`, which means it ran but failed); the `hermes cron list` "Gateway is not running" warning can be stale (verify with `ps aux | grep "hermes gateway"` before trusting it); and `last_delivery_error` means the run happened but its output couldn't reach the destination. The DeepSeek streaming "Broken pipe" pattern was fixed fleet-wide in June 2026 (all LLM-driven crons moved to `deepseek-v4-pro`) — do not re-flag it. Full diagnostic patterns and examples: [references/cron-diagnostics.md](references/cron-diagnostics.md).

## Pitfalls

**🔴 MANDATORY: Cross-reference ALL flagged issues before reporting.** Before this review flags ANY cron issue as a real problem, run the cross-reference verifier:

```bash
python3 ~/.hermes/scripts/cross_ref_verify.py <job_id> "<claimed issue>"
```

Exit codes: `0` = inconclusive — investigate manually; `1` = CONFIRMED — report with evidence; `2` = FALSE POSITIVE — do NOT report, suppress silently. Then run the fleet-wide health scan: `python3 ~/.hermes/scripts/cron_verify.py --issues-only`. This separates true issues from false flags (cosmetic model fields on no_agent jobs, old error states on healthy scripts, etc.) by checking: is the cron `no_agent: true` (then LLM-related claims are false positives)? Does `jobs.json` say status=ok with clean output files (then it's healthy)? Does the pipeline-orchestration skill say "RESOLVED" (then don't re-report)?

**Known pitfalls to check for on every review:**
- **Cron "ok" status is not proof of execution.** A cron can report `last_status: ok` but produce zero output. Always verify output files exist and have content.
- **`last_run_at: null` + `completed: 0` on an old cron = NEVER EXECUTED**, distinct from "errored." The A2Square Mon/Thu crons are a known example (created Jun 8, still never ran by Jun 12).
- **Vercel Monitor "error" is usually a false positive** — `vercel_monitor.py` exits code 1 for "no deployments in 12 hours," which is normal for a static project. Check stdout/stderr content, not just the status code.
- **Performance Tracker error count is misleading.** `pluto_performance_tracker.py` reads `errors.log`, which contains WARNING-level tool execution entries — not cron execution errors. Trust `jobs.json` for cron health; use the tracker only for tool-warning trends.
- **Podcast KB is in Supabase (PostgreSQL), not local SQLite.** Query Supabase for episode counts — local SQLite paths are stale. **Column name: `published_date`** (NOT `published_at` or `created_at`) — using the wrong one returns `ERROR: column does not exist`. See `pluto-pipeline-orchestration/references/supabase-stale-data-queries.md` for all correct column names.
- **Git sync output is in the cron's `last_error` field, not a log file.** Script-based crons with `deliver: local` embed stdout in `last_error`.
- **DO NOT use `read_file` to parse `jobs.json` — use `terminal` + Python instead.** `read_file` returns line-number prefixes that break `json.loads()`.
- **`session_search` can return extremely large outputs for broad queries.** Use specific queries with low `limit` values — even targeted queries can produce 500KB-900KB of output if the matched session is a long cron execution. Use `role_filter: "user"` to filter out cron system messages, and for very large results, use discovery mode first, then scroll into specific sessions by session_id + around_message_id rather than letting the full transcript flood your context.
- **Error detection by output-file pattern matching produces massive false positives.** Simple keyword matching (`error`, `fail`, `exception`) catches benign strings like "errors: 0" or "[SILENT]." In W31, naive pattern matching reported 205 "errors" from 445 runs when the real count from `jobs.json` `last_status` was only 4. **Use `jobs.json` `last_status` as the canonical truth**; read output files for context only after identifying failed crons from `jobs.json`.
- **Adding a flag to source code doesn't mean the cron passes it.** A W30 auto-improvement added `--debug` to `competitor_intel.py`, but the cron job config in `jobs.json` may not include `--debug` in its invocation. Check BOTH the source code AND the cron job config before confirming a fix applied.
- **Supabase queries may fail — fall back to parsing cron output files.** The podcast episode count can be derived from `d4d77c41f6c0/*.md` cron output via regex `New: (\d+) episodes` — richer than a count query and works when Supabase is unreachable.
- **The Saturday report's "Last Week's Fixes" table can be wrong in BOTH directions** — claiming fixes that don't exist in code, or staying silent about fixes that DO exist. Never trust it; always `grep` the actual scripts to verify both a claimed-done fix and a claimed-not-done fix (Week 25: Vercel/Git Sync fixes wrongly reported "NOT DONE"; Week 27: `SKIP_REPOS` wrongly reported missing when `KNOWN_DEAD_REPOS` had shipped the same fix under a different name).
- **Gateway shutdown errors at identical timestamps are NOT individual failures.** When multiple crons share the same `last_run_at` and a "Gateway shutdown (final-cleanup)" error, they were all killed by one restart — group and count as 1 issue, not N.

The full dated history behind several of these (daily-learning misrouting discovery, synthesis-size false-alarm check, TapEase/podcast/Saturday-loop specifics) is in [references/resolved-and-historical-incidents.md](references/resolved-and-historical-incidents.md) and the weekly diagnostic logs below.

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
