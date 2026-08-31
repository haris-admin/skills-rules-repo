---
name: hourly-version-check
description: Use when diagnosing the hourly AML Hive version check.
---

# Hourly Production Version Check

Cron `4689311b6ad0` (hourly, `0 * * * *`, no_agent) → `~/.hermes/scripts/hourly_version_check.py`.

**Purpose:** Detect silent-stale-build regressions (issue-151 class). Fetches
`https://api.amlhive.com.au/version` and compares against the repo `.version`
file. Alerts ONLY when the API is behind the repo (a build that looks deployed
but isn't the latest).

**Exit codes:** 0 = pass (version current), 1 = stale build (sends alert via
`alert_email.send_alert`).

**State:** history appended to
`~/.hermes/research_outputs/.version_check/history.jsonl` — consumed by the
21:45 Daily Probe Summary cron (`eca044f22146`, `daily_probe_summary.py`).

## Pitfalls
- This cron and `hourly_attribution_probe.py` (`b705c3ee3882`) are the two
  half-hour-offset hourly probes (version at :00, attribution at :30). Keep
  them from colliding with the 5/11/17/23 fleet monitors.
- The alert fires on a genuine stale build, not on API-down (that's the fleet
  monitor's job). Don't mute it without checking the actual version drift.
