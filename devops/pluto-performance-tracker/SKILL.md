---
name: pluto-performance-tracker
description: Pluto Daily Performance Tracker — collects cron health, pipeline output counts, error rates, and repo status into weekly JSON snapshots for the Saturday briefing. Use when debugging the tracker, understanding its metrics, or adding new data sources.
---

# Pluto Performance Tracker

## When to Use
- Debugging why the Saturday weekly review shows wrong metrics
- Understanding what the tracker measures (and what it doesn't)
- Adding new data sources to the weekly snapshot
- Interpreting tracker numbers in context

## Architecture

**Script:** `~/.hermes/scripts/pluto_performance_tracker.py`
**Cron:** `28bf484caedd` — Daily 11:30 PM AEST (`30 23 * * *`), `no_agent: true`, `deliver: local`
**Output:** `~/.hermes/research_outputs/.performance_tracker/{week_id}.json`
**Consumer:** Saturday Weekly Review (`7d24b37a03f2`) reads cumulative data

## What It Collects

### Daily Snapshot (every 11:30 PM)
1. **Cron health** — reads `cron/jobs.json` directly (NOT `state.db`):
   - Total crons, ok/error/never counts
   - Per-cron: id, name, schedule, last_run_at, last_status, enabled
2. **Error counts** — parses `logs/errors.log`:
   - `total_errors` — ERROR-level entries (cron execution failures)
   - `tool_warnings_today` — WARNING-level entries (tool noise, NOT real failures)
   - `broken_pipe` — Broken pipe occurrences
3. **Pipeline output** — counts files in `research_outputs/`:
   - `research_*.json`, `synthesis_*.json`, `actions_*.json`, `morning-briefing-*.md`
   - `linkedin-ideas_*.md`, `feedback/*.json`
4. **Git repo status** — runs `git_sync.py` with `--status` flag

### Weekly Cumulative
The Saturday review reads all daily snapshots for the week and computes:
- Sum of all errors, tool warnings, broken pipes
- Average output file counts
- Week-over-week comparison

## Critical Distinctions

### Error vs Tool Warning
```python
def count_errors_today() -> int:
    """Count ERROR entries — cron execution failures only."""
    return grep_count("ERROR")

def count_tool_warnings_today() -> int:
    """Count WARNING entries — tool noise, NOT real failures."""
    return grep_count("WARNING")
```

**The tracker's error count does NOT mean cron failures.** Tool-level WARNING entries from `errors.log` (e.g., psql auth retries, yt-dlp fallback attempts) are counted separately as `tool_warnings_today`. Only ERROR-level entries count as real errors.

**Historical context:** Before June 20, 2026, all WARNING entries were counted as errors. A week showing "136 errors" was really 136 tool warnings with 0 cron failures. The fix separates these.

### Cron Health ≠ Tracker Errors
The tracker reads `errors.log` which contains WARNING-level tool execution entries. These are NOT cron execution errors. When the tracker shows 26 entries and all crons show `last_status: ok`, the 26 are tool warnings, not cron failures. Trust `cron/jobs.json` for cron health, the tracker for tool-warning trends.

## Verification

```bash
# Run manually
python3 ~/.hermes/scripts/pluto_performance_tracker.py

# View this week's cumulative data
cat ~/.hermes/research_outputs/.performance_tracker/$(python3 -c "from datetime import datetime; print(datetime.now().strftime('%Y-W%W'))").json | python3 -m json.tool

# Check when it last ran
stat ~/.hermes/research_outputs/.performance_tracker/*.json
```

## Pitfalls

- **The error count is tool warnings, not cron failures.** Cross-reference with `cron/jobs.json` before escalating.
- **Week ID uses ISO weeks** (`%Y-W%W`). A new week starts Monday midnight UTC.
- **Data resets each week** — each `{week_id}.json` is cumulative within the week only.
- **Missing days** means the tracker didn't run that day — not that there were zero errors.
- **Cron list reads jobs.json** (not state.db). State.db is always empty — ignore it.
