# RDS Secret Name Change — July 2026

## What changed

The AMLHive RDS secret `amlhive/prod/rds` was deleted from AWS Secrets Manager. The AMLHive backend `.env` now points to `tapease/rds/credentials-production` via `RDS_SECRET_NAME=tapease/rds/credentials-production`.

## Affected scripts

| Script | Previous secret | Current secret | Status |
|--------|----------------|----------------|--------|
| `amlhive_daily_report.py` | `amlhive/prod/rds` | `tapease/rds/credentials-production` | ✅ Fixed Jul 30 2026 |
| `amlhive_prod_monitor.py` | Not affected (doesn't query RDS) | N/A | ✅ |

## Password format

The `tapease/rds/credentials-production` secret returns:

```json
{
  "password": "...",
  "username": "tapease_admin",
  "engine": "postgres",
  "host": "tapease-postgres-production...",
  "port": 5432,
  "dbname": "tapease_production"
}
```

Extract with: `s.get("password") or s.get("Password")`

## Notes

- All 4 existing secrets in the account: `portal/clover-sync/dev`, `portal/clover-sync/prod`, `monoova/integration/dev`, `tapease/rds/credentials-production`
- No AMLHive-specific secrets remain
- If a new `amlhive/prod/rds` secret needs to be created, the current password can be extracted from the backend EC2's `.env` file
