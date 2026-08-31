---
name: date-gated-crons
description: "Use when a cron must fire only on a calendar condition."
version: 1.0.0
---

# Date-Gated Crons (monitor-gated scheduling)

## When to Use
- A cron must fire only on a calendar condition cron syntax can't express directly: **last day of the month**, first/last weekday, Nth Monday, etc.
- Example: Month-End Review (`09d6d950544f`, fires only on the last calendar day at 12:00).

## The Pattern: deterministic monitor script + daily schedule
Cron can express `1-7` day-of-month ranges but not "last day of month". Instead of hand-computing dates or running wasted agent ticks, use the cron **monitor** feature:

1. **Daily schedule** (`0 12 * * *`) — the job checks every day at the target time.
2. **Monitor script** (`monitor: <name>.py`, relative to `~/.hermes/scripts/`) — prints STABLE output every tick EXCEPT on the real trigger date, where it prints a DIFFERENT stable string.
3. The scheduler hashes the monitor output: unchanged → silent skip (no agent run); changed → agent runs with a `MONITOR CHANGE DETECTED` diff injected.
4. **First tick always runs as baseline** — for an already-past trigger, use `cronjob(action='run')` to fire manually.

## The month-end detector (reference implementation)
`~/.hermes/scripts/month_end_check.py` (created 2026-08-31):

```python
import datetime
today = datetime.date.today()
if today.month == 12:
    last = datetime.date(today.year, 12, 31)
else:
    last = datetime.date(today.year, today.month + 1, 1) - datetime.timedelta(days=1)
print(f"MONTH_END {today.isoformat()}" if today == last else "NOT_MONTH_END")
```

Handles Dec 31 and Feb 28/29 via next-month-minus-one-day arithmetic. No timestamps → deterministic (critical: the monitor output MUST be byte-stable or every tick looks changed and the agent fires daily).

## Completion-gated chain (Month-End → Start-of-Month, 31 Aug 2026)

For "run B once A finishes, whatever time it takes" — schedule B every 15 min in a
window and gate it on a completion file the agent writes at the end of A:

- **Job A — Month-End Review** (`09d6d950544f`): `1 0 1 * *` (1st 00:01, no monitor
  needed — day-of-month 1 is expressible). Reviews the just-ended month and MUST
  save a dated copy to `~/.hermes/research_outputs/month-end-YYYY-MM.md` (YYYY-MM =
  the ended month) so downstream jobs can detect completion.
- **Job B — Start-of-Month Rule Refresh** (`2f4e89762abb`): `*/15 0-3 1 * *` +
  `monitor: month_end_complete_check.py` + `context_from: [09d6d950544f]`.
  The monitor prints `NOT_FIRST_DAY` (not the 1st), `NOT_COMPLETE` (1st, output
  file missing), or `MONTH_END_COMPLETE YYYY-MM` (1st, file present). B fires only
  when that string changes → within 15 min of A finishing. `context_from` injects
  A's output into B's prompt.

Reference monitor: `~/.hermes/scripts/month_end_complete_check.py`.

```python
today = datetime.date.today()
if today.day != 1: print("NOT_FIRST_DAY"); raise SystemExit(0)
ym = f"{today.year}-{today.month-1:02d}" if today.month > 1 else f"{today.year-1}-12"
out = Path.home() / ".hermes" / "research_outputs" / f"month-end-{ym}.md"
print(f"MONTH_END_COMPLETE {ym}" if out.is_file() else "NOT_COMPLETE")
```

Pitfall: the first monitor tick always runs as baseline (agent fires once even if
not complete) — the Start-of-Month prompt must handle a missing/stale input by
deferring honestly, never fabricating.

## Creating one
```
cronjob(action='create', schedule='0 12 * * *', monitor='month_end_check.py',
        prompt='<full self-contained brief; final response is delivered>',
        deliver='telegram:<chat_id>', skills=[...])
```
- `monitor` takes a bare filename (script lives in `~/.hermes/scripts/`); absolute/home-relative paths are rejected.
- The prompt must be SELF-CONTAINED (fresh session, no chat context). It should open with "The monitor confirms today is the last calendar day of the month (or this is a manual fire)."
- Skills array loads the operating contract so the run behaves like the fleet's other crons.

## Pitfalls
- **Stable output is mandatory** — never embed `datetime.now()` time in the monitor's common path. Only the trigger string varies.
- **Baseline first tick** fires the agent even if the date isn't the trigger — if that's wrong for the job, create it on the day BEFORE the trigger, or accept one baseline run.
- **Manual fire for backfill**: `cronjob(action='run', job_id=..., prompt='...')` runs immediately in background; outcome re-enters the conversation.
- **Delivery**: `deliver` without `:thread_id` lands in the main chat on thread platforms.
- Generalize the detector to other conditions (first weekday of month = `today.day <= 7 and today.weekday() < 5`; Nth Monday = `(today.day - 1) // 7 == N-1 and today.weekday() == 0`) — same pattern, new script.
