# PostgreSQL AT TIME ZONE Pitfall

## The bug
`'09:00:00' AT TIME ZONE 'Australia/Sydney'` does NOT do what you think.

## What actually happens
1. PostgreSQL casts the string `'09:00:00'` to `timestamp with time zone` using the **session timezone** (typically UTC)
2. Then `AT TIME ZONE 'Australia/Sydney'` converts that `timestamptz` **TO** Sydney local time

So: `'09:00:00' AT TIME ZONE 'Sydney'` with UTC session → `19:00:00` (7PM AEST)

## What you wanted
Treat `09:00:00` as 9AM AEST, convert to UTC → `23:00:00` (11PM) the **previous day**
(str -> timestamptz direction, interpreting the string in the specified timezone)

## Why direction matters
- `timestamp without tz AT TIME ZONE 'tz'` → `timestamptz` (interprets as local time, converts to UTC)
- `timestamptz AT TIME ZONE 'tz'` → `timestamp without tz` (converts UTC to local time)
- A bare string `'...'` is first implicitly cast to which type?
  - PostgreSQL defaults to `timestamptz` when used with `AT TIME ZONE` on a string
  - So a **bare string** gets the SECOND behavior (timestamptz → local), not the first

## The fix
**Never use `AT TIME ZONE` for time windows in SQL.** Always pre-compute in Python:

```python
_aest = timezone(timedelta(hours=10))
_lower = datetime(2026, 7, 14, 9, 0, 0, tzinfo=_aest)
LOWER_UTC = _lower.astimezone(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
# Use: WHERE col >= '{LOWER_UTC} UTC'
```

## When to use UTC vs raw AEST strings

| Column type | Store pattern | Query with |
|-------------|---------------|------------|
| `timestamptz` (e.g. AML Hive `performed_at`) | UTC internally | `'{LOWER_UTC} UTC'` — pre-computed UTC strings |
| `timestamp without tz` (e.g. Tapease `created_time`) | AEST natively | `'{LOWER_AEST}'` — raw AEST strings, no suffix |

**Know your column type first.** Choosing wrong shifts results by 10 hours.

## Discovery
This bug was discovered July 2026 after months of reports showing ~40% fewer transactions. Both Tapease and AMLHive reports were affected. The symptom was always "0 entries" or "fewer entries than expected" — never an error.
