---
name: pluto-skill-extraction
description: Pluto's daily skill extraction engine — scans session history, research outputs, and scripts for reusable patterns, then proposes new skills. Use when running the skill-extractor cron job or when manually analyzing Pluto's activity for patterns worth capturing.
allowed-tools: [search_files, read_file, write_file, terminal, skill_manage, skill_view]
---

# Pluto Skill Extraction

## When to Use
- Running the daily `Pluto Skill Extractor` cron job (11:00 AM AEST) — now a `no_agent` script, not LLM-driven
- Manually analyzing recent activity for reusable patterns
- Post-mortem after a complex multi-session task: "what should I save from this?"
- Haris asks "what have you learned this week that should become a skill?"

**Reference:** `references/data-sources.md` — documents the key JSON files (cron/jobs.json, tasks manifests, sessions/sessions.json, reviews/) with their schemas and query patterns. Load this when you need the exact field names and query strategies.

## Pipeline

### Phase 0: Load Existing Skills for Cross-Reference
Always start with `skills_list` — you need to know what already exists before you can identify what's new. This prevents proposing duplicate skills and helps you spot when new activity is just an iteration of an existing pattern.

### Phase 1: Gather Execution Data (Two Paths)

**Path A (fast, preferred): Filesystem + cron state.** This approach is more reliable than log scanning and works even when the log file is large, rotated, or has inconsistent formatting. Use this first unless the log is specifically needed.

1. **Read cron/jobs.json** — reveals all 22+ cron jobs with last_run, last_status, last_error, and schedule:
   ```
   read_file(path="~/.hermes/cron/jobs.json")
   ```
   This is the fastest way to see what ran, what failed, and what never fired. The `last_status` field is authoritative — "ok", "error", or null (never run).

2. **Read sessions/sessions.json** — shows active session state, last activity timestamps, platform:
   ```
   read_file(path="~/.hermes/sessions/sessions.json")
   ```

3. **Check task manifests** for execution evidence:
   ```
   search_files(pattern="DATE", path="~/.hermes/tasks", target="files")
   ```
   Each task manifest (`tasks/PIPELINE/DATE-HHMM.json`) records dispatch time, status, and result path. These are created regardless of whether the cron actually fired — they confirm what was queued.

4. **Check reviews directory** for cross-session findings:
   ```
   search_files(pattern="*DATE*", path="~/.hermes/reviews", target="files")
   ```
   Weekly reviews (`weekly-review-*.md`), improvement reports (`improvements-*.md`), and dreams (`dreams-*.md`) capture operational findings that span multiple sessions.

5. **Cross-reference cron/jobs.json `last_run` timestamps with task manifests** to distinguish "cron fired but errored" from "cron never fired at all". A cron with a populated `last_run` but `last_status: "error"` is a different class of bug from one with no `last_run` at all.

**Path B (fallback): Agent log scanning.** Use when Path A is insufficient or when you need turn-level detail.

1. **Identify all unique cron sessions that ran today:**
   ```
   terminal: grep "cron.*YYYY-MM-DD" ~/.hermes/logs/agent.log | grep -oP "session=\S+" | sort -u
   ```
   CRITICAL: The log uses `YYYY-MM-DD` format (e.g., `2026-06-04`), NOT `YYYYMMDD`. Using the wrong format silently returns zero results — no error, just empty output. If you get empty results from this step, double-check that your date string includes hyphens.
   
   The session IDs map to known jobs:
   - `b0de180cec84` = Pluto Morning Research
   - `ddceef1f9e5b` = Pluto Cross-Chamber Synthesis
   - `38c1aa80a5b8` = Pluto Action Bridge
   - `59f18c4d557c` = Pluto Feedback Loop
   - `5678a363ce3b` = Mempalace Inbox Watcher
   - `2d33c8f9a89c` = Skill Extractor (self)
   - `79c8ad5b9465` = Podcast Chunking (2:00 AM AEST) — [PRUNED June 13, 2026]
   - `1a13a2d49682` = Competitor Intel (5:12 AM AEST)
   - `7cc81d64613a` = Briefing Improver (5:20 AM AEST)
   - `ee4e48300826` = LinkedIn Ideas (6:45 AM AEST)
   - `67319a9b2606` = Podcast Insight Extractor (5:02 AM AEST)

2. **Count turn completions per session type to understand activity depth:**
   ```
   terminal: grep "Turn ended\|API call" ~/.hermes/logs/agent.log | grep "YYYY-MM-DD" | grep -oP "session=cron_\w+" | sort | uniq -c | sort -rn
   ```
   Research sessions typically show 2 turn endings (they run longer). Watcher sessions show exactly 1 (they check and exit).

3. **Extract tool-call pattern distribution — this is your richest signal for identifying reusable workflows:**
   ```
   terminal: grep "tool_executor\|tool " ~/.hermes/logs/agent.log | grep "YYYY-MM-DD" | grep -oP "tool \w+ (completed|invoked)" | sort | uniq -c | sort -rn | head -60
   ```
   Look for: `skill_manage` usage (self-improvement), `execute_code` in research sessions (Python-based data processing), new tool combinations that appear across multiple sessions.

4. **Isolate tool usage for specific pipeline stages** to see what each stage did:
   ```
   terminal: grep "SESSIONID" ~/.hermes/logs/agent.log | grep "YYYY-MM-DD" | grep -oP "tool \w+ (completed|invoked)" | sort | uniq -c | sort -rn
   ```
   This reveals whether the research session used `execute_code` for RSS parsing, whether `skill_manage` was used mid-flight, etc.
   
   **Fallback:** If the above returns empty (common for Telegram/interactive sessions where tool calls are logged via `tool_executor` instead), try:
   ```
   terminal: grep "SESSIONID" ~/.hermes/logs/agent.log | grep "tool_" | grep -oP "tool_\w+" | sort | uniq -c | sort -rn
   ```
   This broader pattern catches all tool-related log lines regardless of format.

5. Check the tail of agent.log for the most recent entries:
   ```
   read_file(path="~/.hermes/logs/agent.log", offset=<last 200 lines>)
   ```

### Phase 2: Check Research Outputs + Reviews + State Files
1. List today's files (use wildcards — `search_files(target='files')` does glob matching, not substring):
   ```
   search_files(pattern="*YYYY-MM-DD*", path="~/.hermes/research_outputs", target="files")
   ```
   **Fallback if empty:** `ls -lt ~/.hermes/research_outputs/ | head -25`
2. Read the key pipeline outputs: `research_DATE.json`, `synthesis_DATE.md`, `actions_DATE.json`, `feedback/feedback_DATE.md`
3. **Check reviews directory for cross-session context:**
   ```
   search_files(pattern="*DATE*", path="~/.hermes/reviews", target="files")
   ```
   Read `reviews/weekly/improvements-*.md` (DREAM MODE self-improvement reports), `reviews/weekly/dreams-*.md` (speculative proposals), `reviews/vercel/` (deployment monitoring). These often contain discoveries that inform skill proposals.
4. **Check task manifests** for execution evidence from crons that may not have produced research outputs:
   ```
   search_files(pattern="DATE", path="~/.hermes/tasks", target="files")
   ```
   Task manifests in `tasks/PIPELINE/DATE-HHMM.json` show what was queued even if the cron never fired.
5. Verify timestamps with `stat -c '%Y %y %n'` to distinguish late-night files from current-day files. The human-readable `%y` includes the timezone label which helps resolve AEST vs UTC confusion. For files that may have been created by different sessions with different timezone settings, cross-reference with log session timestamps (which are always UTC).
6. **Inspect state files for execution truth AND health trends.** State files reveal what actually executed vs what the log shows. They also surface **inter-day trends** — a state file going from empty to populated (or vice versa) is a signal:
   - `.honcho_bridge_state.json` — tracks which files were pushed to Honcho, last run time. Empty → populated = previously-broken pipeline component now working.
   - `.gmail_ingestor_state.json` — tracks processed email IDs, last run. Empty → populated = ingestor now writing state correctly.
   - `.podcast_monitor_state.json` — tracks last ingestion run, episodes processed. Growing = pipeline healthy.
   - `.cleanup_state.json` — tracks archived count. Growing = cleanup cron running.
   - `.briefing_feedback.json` — tracks user responses to briefing improvement prompts (A/B/C choices, applied status). NEW as of Jun 2026.
   - `.briefing_improvements.json` — tracks briefing improvement history (signal counts, checklist counts, files used, feedback streak). NEW as of Jun 2026.
   **Health trend check:** `find ~/.hermes/research_outputs/ -maxdepth 1 -name '.json' -newer <previous_extraction_report> -printf '%T+ %p %s\\n' | sort -r` — this one-liner shows all state files modified since the last extraction, with sizes. Use it to detect newly-populated files (previously 0 bytes) and track growth rates.
7. **Detect mid-flight skill modifications.** A skill file modified during pipeline execution (within 1-2 minutes of a pipeline output file) is evidence of autonomous self-improvement. Check with:
   ```
   stat --format='%Y %y %n' ~/.hermes/skills/research/pluto-autonomous-research/SKILL.md
   ```
   Compare the modification timestamp against research output timestamps (e.g., `research_DATE.json`). If a skill was modified ≤2 minutes after a pipeline output, the agent autonomously patched itself during execution — a qualifying pattern after 2+ occurrences.
8. Look at the previous day's extraction report (`skill-proposals_PREVIOUS_DATE.md`) for context on what was already identified and what was forecast to qualify today.

### Phase 3: Scan Scripts for Modifications
1. Get modification timestamps (simplest approach):
   ```
   terminal: ls -lt ~/.hermes/scripts/*.py ~/.hermes/scripts/*.sh | head -20
   ```
2. Alternative with epoch timestamps for precise age calculation:
   ```
   terminal: stat -c '%Y %n' ~/.hermes/scripts/*.py ~/.hermes/scripts/*.sh | sort -rn | head -10
   ```
3. Read any script modified in the last 48 hours to understand new functionality.
4. Cross-reference with existing skills — is the new script covered by an existing skill?
5. Check for entirely NEW scripts (created today) vs MODIFIED scripts — new scripts represent nascent capabilities that may qualify as patterns after a few production runs.

### Phase 4: Identify Patterns
A pattern qualifies when:
- It appears **at least twice** across different sessions/days
- It is **not a variant** of an existing skill
- It represents a **reusable workflow**, not a one-off task

Pattern categories to watch for:
- **Pipeline stages:** New cron jobs that feed into the 5-stage pipeline
- **Communication channels:** New ways Pluto ↔ Gumby exchange data
- **Tool usage patterns:** Novel combinations of tools that solved a non-trivial problem
- **Script evolution:** New scripts that enable a new class of operation
- **Mid-flight autonomous skill modification:** Agent detects gaps in its own skill docs during pipeline execution and patches them without user instruction. Detect by checking skill file mtimes vs pipeline output mtimes — ≤2 minute gap is evidence. Qualifies after 2+ pipeline sessions show this behavior.
- **State file health trends:** State files transitioning from empty → populated (resolved bugs) or shrinking → empty (regressions). These are inter-day signals — track them across consecutive extraction reports.
- **Dual-consumer patterns:** A single pipeline component feeding two downstream consumers (e.g., podcast insights → research enrichment AND LinkedIn content). These are architectural patterns worth capturing as they reveal pipeline topology.
- **Portfolio-connection mapping:** Intelligence sources that systematically map findings to Haris's 7-portfolio projects (ExitLens, PayLicence, TokenPilot, FinAI, AML Hive, CloudProof, Tapease). When 2+ sources produce this mapping, it's a reusable pattern.

### Phase 5: Look for Operational Findings
Beyond patterns, note:
- **Cron misconfigurations** that persist across runs (e.g., path concatenation bugs)
- **False negatives** (scripts reporting "nothing found" when data exists)
- **Timeout/connection issues** that are recurring
- **Model/provider upgrades** (e.g., gpt-5 → gpt-5.5) and their impact

### Phase 6: Detect Force-Run Clusters
Before writing the report, detect whether any crons ran in a batch force-run (all same timestamp, far from schedule). A force-run cluster (multiple crons with identical `last_run_at` far from their scheduled times) means the gateway batch-triggered them — often after a restart, maintenance action, or backlog clearance. Note this in the report — it affects the "on schedule" vs "force-run" classification.

### Phase 6b: Cross-Check Previous Extraction Report
Read the previous day's `skill-proposals_PREVIOUS_DATE.md` to verify its claims against current data:
- Did it say a file was "missing" that actually exists? → Note as correction/errata
- Did it forecast a pattern would qualify today? → Verify and confirm in your report
- Did it report an operational alert as resolved? → Check if it stayed resolved
- Was the pipeline health assessment accurate? → If not, correct it

### Phase 7: Write the Report
Save to `~/.hermes/research_outputs/skill-proposals_YYYY-MM-DD.md` with this structure:

```
# 🌑 Pluto Skill Extraction Report — YYYY-MM-DD

## 📊 Summary (table: metrics)

## 🔭 Activity Scan (timeline of what ran)

## 🆕 New Patterns Found Today (with occurrence counts)

## ✅ Previously Qualifying — Now Fulfilled as Skills (if any were created this cycle)

## ✅ Previously Qualifying — Deduplicated into Umbrellas (if any were absorbed)

## 📋 Previously Qualifying Patterns — Still Pending

## 🐛 Notable Operational Findings

## 📁 File Inventory (table)

## 🔮 Forecast (next 24h expectations)
```

### Phase 7: Deliver
- If any activity occurred → full report as final response (even if zero patterns qualified — the operational scan, file inventory, and forecast have value)
- If genuinely nothing ran, no files produced, no sessions active → respond with `[SILENT]`
- Never combine `[SILENT]` with content — either report findings normally, or say `[SILENT]` and nothing more
- A pattern that was identified but didn't qualify (≤1 occurrence) should be mentioned in the report under "Pattern Identified (But Not Yet Qualifying)" — it primes the next extraction run to watch for it

## Pitfalls

### Verification Discipline
- **Always verify file existence claims with ACTUAL file checks.** If you claim a research file is "missing", CONFIRM by running `search_files` or `ls -la` first. The previous extraction run may have been wrong — you are writing a CORRECTED report. Always note corrections from the previous cycle in an errata section. A claim like "research JSON not produced" that is wrong cascades into bad pipeline health assessments.
- **Prefer filesystem + cron state over agent log scanning.** `cron/jobs.json` gives you last_run, last_status, last_error, and schedule for all jobs in one read. Task manifests (`tasks/PIPELINE/DATE.json`) confirm what was queued. Reviews (`reviews/weekly/`) capture multi-session findings. These three sources together are faster and more reliable than grepping agent.log with complex regexes. Reserve log scanning for turn-level detail when you need to understand *how* a specific session unfolded.
- **Cron "ok" status does not mean the job fired.** A cron with `last_status: "ok"` may have run and succeeded — or may have been manually triggered once but the scheduler never picked it up on schedule. Always cross-reference `last_run` timestamps against the schedule to confirm regular execution.
- **A cron with NO last_run is a different class of bug** than one with errors. Null `last_run` + active status = scheduler bug (the picker drops it). Non-null `last_run` + `last_status: "error"` = the job runs but fails. Treat these separately.
- **Skills pending ≠ skills created.** The extraction report catalogs what qualifies. The Saturday 12AM auto-improvement cron (`159702fe072c`) reads the Friday weekly review (which aggregates extraction reports) and implements them. If the review cron fails or the Saturday cron doesn't read it, skill debt accumulates indefinitely. The 3-stage cycle is: **Daily extraction** → **Friday review** (catalogs all pending) → **Saturday implementation**. If any link breaks, skills stay pending.
- **Log date format MUST use hyphens.** The agent log uses `YYYY-MM-DD` (e.g., `2026-06-04`). If you accidentally use `YYYYMMDD` (no hyphens), grep will silently return empty — no error, no warning, just zero results. Always verify your date format matches the log.
- **`grep -oP` regex escaping varies by shell.** The `-P` flag enables Perl-compatible regex, but escaping rules differ. Prefer `grep -oP "session=\S+"` over `grep -oP "session=([^ ]+)"` — the `\S` (non-whitespace) pattern is simpler and avoids unescaped paren issues. If a grep returns empty when you expect results, try simplifying the regex.
- **Tool extraction patterns are session-format dependent.** Cron sessions log tools as `tool terminal completed`; Telegram/interactive sessions may log through `tool_executor` or `tool_turns` instead. If `grep "tool \w+ (completed|invoked)"` returns empty for a specific session, fall back to `grep "tool_"` for a broader match.
- **State files reveal execution truth.** When the log is silent about a cron job (e.g., Honcho bridge not appearing), check state files (`.honcho_bridge_state.json`, `.gmail_ingestor_state.json`) — they often track what actually ran even when the cron itself failed or ran through a different mechanism.
- **Don't over-claim patterns.** The portfolio ideation dev queue pattern was established May 29 and is covered by the `pluto-portfolio-ideation` skill. Just because a new run uses gpt-5.5 instead of gpt-5 doesn't make it a new pattern.
- **Distinguish late-night from current-day files.** `dev_queue_june2_2026.json` created at 23:10 UTC on June 1 is really June 1 activity with a June 2 filename (AEST timezone). Check timestamps, not filenames. Always use `stat -c '%Y %y %n'` for precise timestamp verification — the `%y` includes the timezone label.
- **The weekly digest is Sunday-only.** Don't flag it as "missing" on weekdays.
- **Check skills_list before proposing.** The existing `pluto-portfolio-ideation` skill already covers the dev queue push pattern, the Codex context template, and the 1000-point assessment framework. Don't propose duplicate skills.
- **A qualifying pattern from a previous forecast should be tracked explicitly.** Yesterday's extraction report forecast that `podcast-insight-extractor` would qualify today if the 05:02 cron ran — check the forecast section of the previous report and verify before declaring a pattern "new." This prevents duplicate proposals and gives credit to yesterday's foresight.
- **State file health is a multi-day signal.** A state file going from empty (yesterday) to populated (today) = resolved operational bug. Track this across reports — it's as valuable as finding a new pattern. Conversely, a state file going from populated to empty = regression.
- **`find ... -newer` is the fastest way to detect mid-flight skill modifications.** Use it to find all files modified since the last extraction report: `find ~/.hermes/skills/ -name 'SKILL.md' -newer ~/.hermes/research_outputs/skill-proposals_PREVIOUS_DATE.md -printf '%T+ %p\n'`. If a skill was modified within 2 minutes of a pipeline output file, that's autonomous self-improvement — track the occurrence count.
- **The report format itself evolves.** Today's extraction added: state file health status in the file inventory, a "Skills Modified Today During Pipeline" section, and dual-consumer pattern detection. These format improvements compound — each extraction run makes the next one sharper.
- **The 5-stage pipeline runs at ~19:00 UTC (may shift to ~05:00 UTC).** If the extraction runs at 11:00 UTC, the pipeline may have already fired today. Check the actual log timestamps rather than assuming the schedule.
- **Honcho bridge is an ongoing operational issue.** The cron misconfiguration (doubled `scripts/` path) has persisted across 3+ runs. Note it but don't re-propose the skill until the bridge actually works.
- **`grep "Job '"` is unreliable for identifying cron activity.** The log format for job names varies. Use `grep "cron.*YYYY-MM-DD"` with `grep -oP "session=\S+"` instead — session IDs are a stable identifier.
- **New scripts ≠ qualifying patterns.** A new script created today (e.g., `voice_poller.py`) is a signal to watch, not a pattern to propose. It needs ≥2 production runs before qualifying. Mention it under "Pattern Identified (But Not Yet Qualifying)" to prime the next run.
- **Check for voice/interaction activity separately.** Voice messages and Telegram DMs appear in gateway logs, not cron sessions. Search for `voice\|POLLER\|whisper\|Telegram.*Cached` in agent.log to detect cross-modal interaction patterns.
- **Honcho session activity is a separate signal.** Active Honcho sessions (Codex-Portfolio-Ideation, agent-main-telegram) indicate user interaction that happened outside the cron pipeline.
- **Stale-stream / Broken pipe is now a recurring runtime pattern, not an operational alert.** After 3+ consecutive days across 3+ crons, escalate to a pattern. The error signature is: `Stream stale for Ns — no chunks received. Killing connection.` followed by `[Errno 32] Broken pipe`. Hermes auto-retry (3 attempts, exponential backoff) recovers ~2/3 of cases. Document the detection → retry-outcome-verification → escalation workflow. See `pluto-pipeline-orchestration` skill's "Stale Stream Recovery" section for the full diagnostic pattern.
- **`search_files(target='files')` uses glob matching, NOT substring matching.** The pattern `2026-06-07` only matches a file literally named `2026-06-07` — it won't match `research_2026-06-07.json` or `synthesis_2026-06-07.md`. Always use wildcards: `*2026-06-07*` or `*06-07*`. If you get zero results, fall back to `ls -lt ~/.hermes/research_outputs/ | head -25` and scan visually.
- **Pipeline agent sessions are OFTEN COMPLETELY ABSENT from agent.log.** Morning pipeline jobs (`b0de180cec84` Research, `ddceef1f9e5b` Synthesis, `38c1aa80a5b8` Action Bridge, `59f18c4d557c` Feedback, `67319a9b2606` Podcast Extract, `ee4e48300826` LinkedIn) are `no_agent: false` agent sessions — yet they produce ZERO log entries in agent.log. This is NOT a grep issue (no pattern will find what isn't there). Only the Mempalace Watcher (`5678a363ce3b`, every 5m) and Skill Extractor (`2d33c8f9a89c`) reliably appear. **`cron/jobs.json` `last_run`/`last_status` fields are the sole authoritative source for pipeline session confirmation.** The log is useful ONLY for watcher sessions and for turn-level detail on interactive Telegram sessions — never rely on it to confirm pipeline stages ran.
- **"All matched" can be a false negative when proposals are PENDING but not created.** (Fixed July 4, 2026 in `skill_extractor.py`.) The original `propose_new_skills()` only checks scripts modified in the last 48 hours against skill names — if a script was proposed 7+ days ago and the proposal file (`skill-proposals_*.md`) still exists on disk but no skill was registered, the extractor says "none — all matched." `briefing-improver` sat in this limbo for 14 days. **Fix:** The extractor now scans existing `skill-proposals_*.md` files and cross-references against registered skills. Any proposal file where the skill name doesn't exist in `skills/` appears as "📋 Pending proposals (not yet created)." When using the extractor manually, run `skill_manage(action='list')` and compare against `ls ~/.hermes/research_outputs/skill-proposals_*.md` to catch stale proposals.
- **Morning pipeline sessions appear on the PREVIOUS day in UTC logs.** Pipeline runs at 05:00 AEST = 19:00 UTC the day before. If you grep agent.log for `YYYY-MM-DD` (UTC dates) looking for pipeline sessions, use the PREVIOUS day's date. Example: pipeline ran at 05:10 AEST on June 9 → look for `2026-06-08` in the UTC log. If you grep for June 9, you'll get empty results even if the pipeline actually ran. But even with the correct date, pipeline sessions are often absent entirely — prefer `cron/jobs.json`.
- **`grep "cron.*DATE"` can be a false negative even for sessions that DO appear.** Some log lines have the date at the very start of the line (before `cron` appears), so the anchored `cron.*` prefix drops them. Fall back to a bare `grep "DATE"` and extract session IDs with `grep -oP "session=\S+"`.
- **🔴 Variable scope trap in skill_extractor.py main try block.** The variable `skill_names` (a set) is defined inside `propose_new_skills()` (line 91) — it is NOT in scope in the main try block where the pending-proposals loop runs (line ~154). When adding code to the main block that needs to check whether a suggested skill already exists, you must derive the set from the `existing` variable (which IS in scope — set at line 111). **Pattern:** `registered_skills = set(existing)` before the loop. **Hit July 4, 2026:** `NameError: name 'skill_names' is not defined` crashed the cron. This is easy to reintroduce when extending the extractor — every new developer hits it once.