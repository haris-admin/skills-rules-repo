# POS / transaction datetimes are stored and compared as UTC (Tap-Ease backend)

Applies to any code in `tapease_portal_fastapi_a2square` that reads, writes, or
filters a `TIMESTAMP WITHOUT TIME ZONE` column (`trans_clover_transaction_refunds.
modified_time`, `trans_clover_transaction_payments.modified_time`,
`trans_transactions.tran_date_time`, …), or that accepts a datetime from the POS
terminal partner (`start_time`, `shift_start`, `shift_end`, `from_date`, `to_date`),
or that writes seed / fixture rows for those tables.

## Why this exists

**2026-09-02 (v4.2.25 → v4.2.26).** Three production-derived `REFUND` fixtures
were seeded for `user_id 4` with `modified_time` set to the driver's local
wall-clock — `2026-09-02 13:15:00` for "1:15pm Sydney". The POS partner then
called `GET /v1/pos/devices/{serial}/refunds/summary` with the shift window in
UTC (`from_date=…T03:14:47+00:00`), and `get_device_refunds_summary` normalised
that to naive UTC before comparing against `modified_time`. `13:15:00` is not in
`[03:14:47, 03:26:29]`, so the endpoint returned `total_amount_cents: 0` — an
empty refund amount for refunds that were genuinely inside the shift. The bug was
purely the fixture's timezone; the stored convention has always been UTC
(`app/routers/transactions.py` explicitly converts Sydney-local search input to
UTC before touching `modified_time`, with a `# treating as UTC` fallback).

Separately, `start_driver_shift` and the refund endpoints assumed a **naive**
inbound datetime was already UTC — silently wrong by the local offset if a
partner ever sends offset-less local time.

## Rules

1. **Stored `modified_time` / `tran_date_time` / shift bounds are naive UTC.**
   When you write one (fixture, backfill, ingestion, test), it must be UTC. Never
   store local wall-clock.
2. **Normalise every inbound datetime before use** via
   `app.utils.to_naive_utc(dt, *, assume_tz)`:
   - tz-aware input (`Z`, `+00:00`, `+10:00`, `+09:30`, …) → converted to UTC, `assume_tz` ignored.
   - naive input → interpreted in `assume_tz`, then UTC. `assume_tz` comes from
     the request's `timezone` field / query param → the device's shift timezone →
     `Australia/Sydney` (`resolve_iana_tz`, `pos_service._resolve_query_tz`).
   Do not write a bespoke `if dt.tzinfo: dt.astimezone(utc) else dt` — that is the
   exact shape that treated naive as UTC.
3. **Never use a fixed offset for Sydney.** AEST = UTC+10 (Apr–Oct), AEDT = UTC+11
   (Oct–Apr). Use `zoneinfo.ZoneInfo("Australia/Sydney")` so DST is handled per
   date. Same for `Australia/Adelaide` (+9:30 / +10:30).
4. **Fixtures for shift-scoped tables anchor to the shift, not a clock.**
   `scripts/seed_shift_refund_testcases.py` places rows at `shift.in_time + Δ`
   (UTC) so they land inside whatever shift is currently open. Re-run it per test
   cycle rather than hardcoding a time.
5. **A new POS datetime field gets model-level normalisation.** Add it to the
   `model_validator(mode="after")` on `ShiftStartRequest` / `ShiftCloseRequest`
   (or the equivalent) so downstream code always sees a tz-aware / UTC value.
6. **Recommend, but do not require, an offset from the partner.** Ask them to send
   ISO-8601 with a UTC offset; the endpoints must still accept offset-less local +
   an IANA `timezone`.

## Patterns to Follow

```python
from app.utils import to_naive_utc, resolve_iana_tz

# refund-window bound: param -> device shift tz -> Australia/Sydney
assume_tz = await _resolve_query_tz(conn, device_id, tz_param)
from_clean = to_naive_utc(from_date, assume_tz=assume_tz)   # naive UTC, for the WHERE

# request model
@model_validator(mode="after")
def _normalise(self):
    return _localise_naive_datetimes(self, ("shift_start", "shift_end"), self.timezone)
```

## Patterns to Avoid

```python
# WRONG — treats a naive local datetime as UTC
clean = from_date.astimezone(timezone.utc).replace(tzinfo=None) if from_date.tzinfo else from_date

# WRONG — fixed offset ignores DST
syd = dt.replace(tzinfo=timezone(timedelta(hours=10)))

# WRONG — fixture stored in local wall-clock; falls outside a UTC shift window
INSERT ... modified_time = '2026-09-02 13:15:00'   -- should be 03:15:00 UTC
```

## Related

- Skills: `tapease-pos-clover-shift-sync` (datetime handling section),
  `tapease-db-access` (fixture / convention), `tapease-backend-deploy`.
- OpenSpec: `openspec/changes/pos-partner-datetime-normalization/` (v4.2.26).
- `rules/no-hardcoded-current-state-literals.md` — the fixture-time-vs-shift-window
  version of the same anti-pattern.
