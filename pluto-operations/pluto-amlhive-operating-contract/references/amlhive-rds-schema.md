# AMLHive RDS Schema Reference

Discovered during July 2026 RDS migration (new endpoint: `amlhive-prod.ch4ykiy82n3q.ap-southeast-2.rds.amazonaws.com`).

## Key Schema Quirks

### All Status Values are UPPERCASE
Unlike the old schema, all status columns in the new RDS use UPPERCASE values:

| Table | Column | Example Values |
|-------|--------|---------------|
| `kyc_identities` | `verification_status` | `VERIFIED`, `PENDING`, `FAILED`, `EXPIRED`, `REFER` |
| `employee_screening_records` | `outcome` | `CLEAN`, `HIT` |
| `cdd_checklists` | `status` | `IN_PROGRESS`, `SIGNED_OFF` |
| `kyb_records` | `status` | `Active` |
| `matters` | `status` | `OPEN`, `ACTIVE` |

**⚠️ Always use UPPERCASE in WHERE clauses. Do NOT use lowercase.**

### Key Table Name Changes (vs old schema)

| Old Name | New Name |
|----------|----------|
| `screenings` | `employee_screening_records` |
| `kyc` | `kyc_identities` |
| `kyb` | `kyb_records` |
| `user_sessions` | `platform_audit_log` |
| `cdd` | `cdd_checklists` |
| `audit_entries` | `audit_entries` (unchanged) |

### Column Name Quirks

- `clients` uses `is_archived` (BOOLEAN), NOT `is_active`. Active clients = `is_archived=false OR is_archived IS NULL`
- `employee_screening_records` uses `performed_at` for timestamps, not `created_at`
- `platform_audit_log` uses `performed_at` for timestamps, not `created_at`
- `cdd_checklists` uses `created_at` for timestamps
- `matters` has `is_archived` column (BOOLEAN)
- `agencies` has both `is_active` (BOOLEAN) and `lifecycle_status` (TEXT: `trial`, `active`, `onboarding`, `cancelled`)

### Timestamps
All timestamps are stored with UTC timezone (`+00`). When comparing, use `'YYYY-MM-DD HH:MM:SS UTC'` syntax — PostgreSQL accepts this correctly.

### psql -At Output Format
When using `psql -At` (aligned tuples, no header):
- Multiple columns from one SELECT → values on ONE line, pipe-separated: `val1|val2|val3`
- Multiple SELECT statements → separated by newlines
- **PARSING PITFALL:** Do NOT split by `\n` to get individual values. Split the first line by `|` to extract columns. The old approach of `lines[1:]` fails when everything is on one line.

### Data Counts (as of July 2026)
- `agencies`: 28 (10 active, 14 trial, 2 onboarding, 2 cancelled)
- `users`: 43 (29 active)
- `platform_users`: 1
- `clients`: 42
- `employee_screening_records`: 20
- `kyc_identities`: 33 (21 VERIFIED, 5 PENDING, 3 EXPIRED, 2 FAILED, 1 REFER)
- `kyb_records`: 5 (all Active)
- `matters`: 15 (13 OPEN, 2 ACTIVE)
- `cdd_checklists`: 16 (9 IN_PROGRESS, 7 SIGNED_OFF)
- `platform_audit_log`: 29
- `audit_entries`: variable

### Connection
- Host: `amlhive-prod.ch4ykiy82n3q.ap-southeast-2.rds.amazonaws.com`
- DB: `amlhive` (was `amlhive_prod` in old schema — use `amlhive`, NOT `amlhive_prod`)
- User: `amlhive`
- Password: From Secrets Manager (`amlhive/prod/rds`), fetched dynamically
- SSL: Required (`PGSSLMODE=require`)
- Instance connection: Via SSM send-command on backend EC2 (not port forwarding)
