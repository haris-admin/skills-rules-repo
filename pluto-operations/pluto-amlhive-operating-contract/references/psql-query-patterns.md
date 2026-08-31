# PostgreSQL Query Patterns (via SSM psql)

## Column Discovery — Always Check Schema First
Before writing queries against an unknown RDS schema, verify actual column names:
```sql
SELECT column_name FROM information_schema.columns 
WHERE table_name='tablename' ORDER BY ordinal_position;
```

## Uppercase Status Values
This database typically stores status values in **UPPERCASE**:
- `kyc_identities.verification_status`: `VERIFIED`, `PENDING`, `EXPIRED`, `FAILED`, `REFER`
- `employee_screening_records.outcome`: `CLEAN`, `HIT`
- `cdd_checklists.status`: `IN_PROGRESS`, `SIGNED_OFF`
- `matters.status`: `OPEN`, `ACTIVE`
- `kyb_records.status`: `Active`

Exception: `agencies.lifecycle_status` uses lowercase (`trial`, `active`, `onboarding`, `cancelled`)
Boolean columns use `true`/`false` (PostgreSQL native), not uppercase strings.

## Parsing psql -At Output
`psql -At` outputs all columns from one SELECT as **pipe-separated on a single line**:
```
###SUMMARY|0|28|10|2|14
```

The parsing code must handle single-line output — values are in `line.split("|")[1:]`, NOT in `lines[1:]`:
```python
secs = r.split("###")
data = {}
for s in secs:
    if not s.strip(): continue
    lines = s.strip().split("\n")
    line = lines[0].strip()
    parts = line.split("|")
    label = parts[0].strip()
    vals = []
    for p in parts[1:]:
        try: vals.append(int(p.strip()))
        except: vals.append(0)
    data[label] = vals[:5]
```

## Timestamp Comparison
Timestamps are stored with `+00` timezone offset. Compare using `'YYYY-MM-DD HH:MM:SS UTC'` suffix (PostgreSQL accepts it):
```sql
WHERE created_at >= '2026-07-14 23:00:00 UTC' 
  AND created_at <= '2026-07-16 11:00:00 UTC'
```

## Key Tables Reference
| Table | Key columns | Status column | Notes |
|-------|------------|--------------|-------|
| `agencies` | created_at, is_active, lifecycle_status | lifecycle_status (lowercase) | 28 records |
| `users` | created_at, is_active | — | 43 records |
| `employee_screening_records` | performed_at, outcome, decision | outcome (UPPERCASE) | CLEAN/HIT |
| `kyc_identities` | created_at, verification_status | verification_status (UPPERCASE) | VERIFIED/PENDING/FAILED/EXPIRED/REFER |
| `kyb_records` | created_at, status | status (Active) | 5 records |
| `matters` | created_at, status | status (UPPERCASE) | OPEN/ACTIVE |
| `clients` | created_at, is_archived | is_archived (boolean) | 42 records |
| `platform_audit_log` | performed_at, action | — | 29 records |
| `cdd_checklists` | created_at, status | status (UPPERCASE) | IN_PROGRESS/SIGNED_OFF |
