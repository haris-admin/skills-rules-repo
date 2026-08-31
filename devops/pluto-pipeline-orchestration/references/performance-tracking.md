# Performance Tracking Pipeline

**Created:** June 13, 2026 | **Parent Skill:** pluto-pipeline-orchestration

## Purpose

Daily snapshots of cron health, error rates, and output volumes are accumulated into a weekly JSON file. The Saturday Weekly Review consumes this data to produce performance trend analysis.

## Architecture

```
pluto_performance_tracker.py (11:30 PM daily, no_agent)
        │
        ▼
~/.hermes/research_outputs/.performance_tracker/{week_id}.json
        │
        ▼
★ Saturday Weekly Review cron (7d24b37a03f2, 6:00 AM Sat)
  - Reads performance tracker JSON
  - Reads cron job statuses
  - Reads research_outputs/ for weekly production
  - Reads errors.log for patterns
  - Produces comprehensive weekly report
```

## Data Collected Per Day

```json
{
  "date": "2026-06-13",
  "crons": {
    "total": 30,
    "enabled": 29,
    "ok": 25,
    "error": 4,
    "never_run": 1
  },
  "errors": {
    "total_today": 194,
    "broken_pipe_today": 180
  },
  "output": {
    "total": 12,
    "jobs": {
      "c527fed4a1da": 1,
      "b0de180cec84": 1
    }
  }
}
```

## Weekly Summary Computed

```json
{
  "days_tracked": 7,
  "avg_cron_health": "24/3",
  "total_errors": 845,
  "total_broken_pipe": 720,
  "total_output_files": 84,
  "trend": "declining"
}
```

## Script Location

`~/.hermes/scripts/pluto_performance_tracker.py`

## Cron

`28bf484caedd` — "Pluto Daily Performance Tracker (11:30 PM)" — `30 23 * * *` — `no_agent: true`

## Key Design Decisions

- **Uses ISO week ID** (`2026-W24`) so data accumulates Mon-Sun
- **Idempotent** — if run twice on the same day, it overwrites that day's entry (not append)
- **No external dependencies** — stdlib only (json, sqlite3, subprocess, datetime)
- **Hermes state DB** (`cron/state.db`) is queried directly via sqlite3 for cron statuses
- **Errors counted** from `errors.log` by date prefix and "Broken pipe" pattern
- **Output files counted** by checking `cron/output/<id>/` for today's files
- **Trend logic:** `improving` if error count < 2 × days, else `declining`

## Pitfalls

- The tracker runs at 11:30 PM, so it captures the day's full activity including the evening crons (MemPalace cleanup at 11:55 PM won't be captured — runs after the tracker)
- First run was June 13 (Saturday), so Week 23 will only have 1 day of data. Full weeks start from Week 24 (June 14-20)
- If the cron scheduler restarts mid-day, the tracker only records what it sees at 11:30 PM
- The `avoid_git_sync_errors` metric only exists in the tracker, not in the Saturday review — the review must compute its own repo health check
