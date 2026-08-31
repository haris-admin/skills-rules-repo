# AML Hive Daily Business Report

## Cron
- Schedule: `15 21 * * *` (9:15 PM AEST)
- Job ID: `3ebed4e59ee3`
- Script: `~/.hermes/scripts/amlhive_daily_report.py`
- Delivery: Email to `shoaib@amlhive.com.au, tech@amlhive.com.au` from `operator@harishabib.au`

## Data Window
- 9AM → 9PM AEST (12-hour business day)
- Timestamps stored in UTC (`timestamptz`). Compute UTC window bounds in Python.

## Database Connection
- RDS: `amlhive-prod.ch4ykiy82n3q.ap-southeast-2.rds.amazonaws.com`
- DB: `amlhive`, User: `amlhive`
- Password: AWS Secrets Manager `amlhive/prod/rds`
- Tunnel: SSM via backend `i-02276d537152046d9`, local port 5435
- psql NOT pre-installed on backend — run `sudo yum install -y postgresql15`
- Query via SSM `send-command` with SQL file (base64 encode → write to remote → psql -f)

## Single-Query Pattern
Batch all metrics into one SQL file with `###`-prefixed labeled SELECTs:
```python
sql = """
SELECT '###AGENCIES' as lbl,
  (SELECT COUNT(*) FROM agencies WHERE ...) as col1,
  (SELECT COUNT(*) FROM agencies) as total;
SELECT '###USERS' as lbl, ...;
"""
encoded = base64.b64encode(sql.encode()).decode()
ssm(f"echo '{encoded}' | base64 -d > /tmp/q.sql")
output = ssm(f"{PSQL} -At -f /tmp/q.sql")
```

Parse via `line[3:].split("|")` after stripping `###`.

## Key Tables & Metrics
| Table | Metric | Timestamp Column |
|-------|--------|-----------------|
| `agencies` | Created today, total, active, trial, onboarding, cancelled | `created_at` |
| `users` | Created today, total, active | `created_at` |
| `platform_users` | Total count (last_login always NULL) | `last_login` (unpopulated) |
| `screening_results` | Total, CLEAN, HIT | `performed_at` |
| `employee_screening_records` | Count | `performed_at` |
| `kyc_identities` | Created, verified, pending, expired/failed | `created_at` |
| `clients` | Created today, total | `created_at` |
| `matters` | Created today, OPEN, ACTIVE | `created_at` |
| `cdd_checklists` | Created, signed off | `created_at` |
| `onboarding_progress` | Completed | `completed_at` |
| `audit_entries` | Entries today | `performed_at` |
| `kyb_records` | Not verified | `created_at` |

## Important Gotchas
- `platform_users.last_login` is NULL for ALL records — cannot track logins
- `platform_audit_log` has only ~29 records — not useful for activity tracking
- `audit_entries` has 1,900+ records and IS populated (use for activity tracking)
- Agencies status: `lifecycle_status` — trial/active/onboarding/cancelled + `is_active` boolean
