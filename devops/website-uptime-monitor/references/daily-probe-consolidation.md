# Daily Probe Consolidation Pattern (21:45 Summary)

Discovered/verified Jul 30 2026. When hourly HTTP probes deliver to origin 24x/day,
the user gets flooded. Consolidate into ONE end-of-day table at 21:45 AEST.

## Architecture

```
hourly probe scripts (no_agent, existing):
  :00  hourly_version_check.py     → appends .version_check/history.jsonl
  :30  hourly_attribution_probe.py → appends .attribution_probe/probe_history.jsonl

21:45  daily_probe_summary.py (no_agent, deliver: origin)
       reads BOTH JSONL files, filters to today (AEST), prints one table
```

Cron job: `eca044f22146` ★ AMLHive Daily Probe Summary — 21:45
Script: `~/.hermes/scripts/daily_probe_summary.py`

## Rule: EVERY hourly probe gets a JSONL history file

The attribution probe already logged history; the version check originally
printed-only (no state file) — added `log_result(status, detail)` that appends
`{"ts": <UTC iso>, "status": "PASS"|"FAIL", "detail": <truncated 300>}` to a
`~/.hermes/research_outputs/.<name>/history.jsonl`.

Key details:
- History dir: `~/.hermes/research_outputs/.<probe_name>/` (dot-prefixed)
- Timestamps stored in **UTC** (datetime.now(timezone.utc).isoformat()); the
  summary converts to AEST for the day-window filter
- Each exit point (PASS, FAIL, error branch) must call log_result — do not
  only log the happy path

## Output Contract (user preference, Jul 30 2026 — CRITICAL)

User directive: **"if there is a failure/mismatch then raise it immediately.
Otherwise, just holdoff till the 09:45 PM."** This is the governing contract
for every hourly probe:

| Condition | Hourly delivery | 21:45 summary |
|-----------|----------------|---------------|
| All probes pass | **SILENT** — empty stdout, exit 0 | Consolidated table |
| Any probe fails / mismatch | **Immediate** — print + `send_alert()` email + exit 1 | Still appears in table |

Implementation notes (applied to both `hourly_version_check.py` and
`hourly_attribution_probe.py`):
- **Remove ALL informational prints on the success path.** Not just the
  summary line — also `api_version=...`, `local_version=...`, and per-probe
  `✅/❌` lines. Any stdout on success gets delivered hourly by the no_agent
  cron, which defeats the whole point.
- **Treat every mismatch as a failure.** REPO_LAG (repo .version behind API),
  version-not-found, any single attribution check failing — all raise
  immediately, not just threshold-triggered alerts (the attribution probe's
  old "3+ failures in 15min" threshold was replaced by ANY-failure alerts).
- Keep `log_result()` calls even on the silent success path — the JSONL
  history is what feeds the 21:45 table. Silence ≠ no logging.
- Exit 0 on success even though stdout is empty — empty stdout is the
  signal, not exit code (no_agent cron delivers nothing on empty stdout).

This pattern generalizes: any recurring watchdog that used to deliver every
tick should instead be silent-on-success + raise-on-failure, with a
consolidated digest job for the "everything fine" picture.

## Summary Script Behavior

- Filter both histories to `NOW.date()` in AEST
- Merge rows by hour (`HH:MM`), render table columns: Hour | Version Check | Attribution Probe
- Empty cells show `· —`; missing data shows `· —` (probe not yet run that hour)
- Print latest version detail line
- Print failure details only if any FAIL rows exist; else "✅ All hourly probes passed today"
- Totals row: `TOTAL: ok/total probes OK`

## When adding a new hourly probe

1. Give it a JSONL history file + `log_result()` at every exit point
2. Add a column to `daily_probe_summary.py` (merge dict + table header + row render)
3. The 21:45 cron picks it up automatically (reads by directory, no cron change needed)

## Pitfall: first-run column shows empty

When a probe's JSONL logging is first added, the 21:45 summary shows `· —` for
that column for earlier hours of the same day. This is expected — history only
accumulates from the moment logging was added. It self-heals next day.
