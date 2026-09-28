# Scheduler timezone must be an IANA zone, never a captured offset

In-process schedulers must run on an explicit IANA timezone so hour-anchored jobs keep firing at
the intended local time across daylight-saving changes. Applies to every agent writing or reviewing
scheduler configuration or hour-anchored cron jobs.

**Scope:** any in-process scheduler (ARQ, APScheduler, Celery beat, or equivalent) and every
hour-anchored job it runs.

---

## Core Directives

1. **Set an explicit `ZoneInfo("<IANA zone>")` on every in-process scheduler** (ARQ
   `WorkerSettings.timezone`, APScheduler, Celery beat). Never rely on the library default: ARQ
   0.25.0 defaults to `datetime.now().astimezone().tzinfo`, a fixed offset read once at worker
   start, so hour-anchored crons drift one hour after a DST change until restart.
2. **A config guard test asserts the scheduler timezone is a `ZoneInfo` with the intended key.**
3. **Test schedule computation across both DST transitions** (spring gap, autumn overlap) for each
   hour-anchored job, and check that startup catch-up covers a restart inside the transition
   window.
4. **A job that would do harm if skipped or doubled must be idempotent or guarded on its own.**

Origin: AMLHive issue-406, 28 Sep 2026.

---

## Patterns to Follow

```python
from zoneinfo import ZoneInfo

class WorkerSettings:
    timezone = ZoneInfo("Australia/Sydney")

def test_worker_timezone_is_iana_zone():
    assert isinstance(WorkerSettings.timezone, ZoneInfo)
    assert WorkerSettings.timezone.key == "Australia/Sydney"
```

---

## Patterns to Avoid

```python
class WorkerSettings:
    pass  # no timezone: ARQ captures the host's current fixed offset at start

timezone = datetime.timezone(datetime.timedelta(hours=10))  # fixed offset ignores DST
```

---

## Verification & Guardrails

- The config guard test from directive 2 runs in the normal test suite.
- DST-transition schedule tests exist for every hour-anchored job.

## Related

- `rules/scheduled-automation-placement.md`: where scheduled automation should run.
- `rules/pos-datetime-utc-normalization.md`: storing and comparing datetimes as UTC with IANA zones.
