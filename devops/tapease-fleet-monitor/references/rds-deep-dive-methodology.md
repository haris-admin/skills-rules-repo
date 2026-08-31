# RDS Error Deep-Dive Methodology

A repeatable process for tracing RDS ERROR events back to their source code path and root cause, developed during the Jul 8, 2026 TapEase investigation.

## The 4-Step Trace

### Step 1: Extract Raw Logs with Full Context

Pull the last 24h of ERROR/FATAL events from the RDS log group with enough limit to see the full pattern:

```bash
aws logs filter-log-events \
  --log-group-name /aws/rds/instance/tapease-postgres-production/postgresql \
  --start-time $(python3 -c "import time; print(int((time.time() - 86400)*1000))") \
  --end-time $(python3 -c "import time; print(int(time.time()*1000))") \
  --filter-pattern '?ERROR ?FATAL ?PANIC' \
  --limit 100 --output json
```

### Step 2: Classify by Error Type + Source IP

Group events by error type and originating IP. Every Postgres ERROR log line contains the client IP in a standard format:

```
2026-07-07 13:20:40 UTC:10.0.2.43(25478):tapease_admin@tapease_production:[22251]:ERROR:  duplicate key ...
                 ^^^^^^^^^ source IP
```

Common error types and their typical sources:

| Error Type | Typical Source | What to Check |
|------------|---------------|---------------|
| `duplicate key` | Clover sync worker / ECS task | Lambda logs, code INSERT pattern |
| `column ... does not exist` | Backend API | View definition, migration history |
| `syntax error` | Ad-hoc dev queries | Monitoring tool, data team access |
| `relation ... does not exist` | Deploy timing | Alembic migration order |
| `SSL` / `connection refused` | Network | Security group, RDS proxy |

### Step 3: Map IP to Source

| IP Range | TapEase Component | Code Location |
|----------|------------------|---------------|
| 10.0.2.161 | Backend API (uvicorn) | `app/routers/`, `app/services/` |
| 10.0.2.43 | Clover sync worker | Lambda `tapease-clover-sync-production` |
| 10.0.1.42 | Unknown / dev tool | Likely ad-hoc queries |

For the backend (10.0.2.161), use SSM to check the uvicorn process and journal logs:

```python
# Check what query was executing during the error window
ssm_out = ssm_shell(env, BACKEND_INSTANCE_ID, 
    f'journalctl -u tapease-backend --since "ERROR_TIME - 5min" --until "ERROR_TIME + 5min" --no-pager -n 30')

# Check the backend code for the failing query pattern
ssm_out = ssm_shell(env, BACKEND_INSTANCE_ID,
    'grep -rn "trans_device_users\|tphv\|duplicate" /home/ec2-user/app/backend/app/ --include="*.py"')
```

### Step 4: Trace the SQL to Source Code

Once you identify the SQL pattern (e.g., `column tphv.commission does not exist`):

1. **Search the codebase** for the alias or table name:
   ```bash
   grep -rn "tphv" /home/ec2-user/app/backend/app/ --include="*.py"
   ```

2. **Find the actual SQL query** that references the missing column:
   ```bash
   sed -n "790,810p" /home/ec2-user/app/backend/app/services/shared_payouts.py
   ```

3. **Check if the object is a view** (not a table) — views drift:
   ```bash
   grep -rn "CREATE.*VIEW\|trans_payouts_with_history" /home/ec2-user/app/backend/app/ --include="*.py"
   ```

4. **Trace migration history** — find when the column was added vs when the view was last updated:
   ```bash
   cat /home/ec2-user/app/backend/migrations/053_add_commission_and_total_payout_to_trans_payouts.sql
   cat /home/ec2-user/app/backend/migrations/033_recreate_trans_payouts_with_history.sql
   ```

## View Drift Pattern (Common)

This is the most common RDS schema error pattern on TapEase:

1. Migration A creates a view (e.g., `trans_payouts_with_history`) — covers current columns
2. Migration B adds a new column to the underlying table (`trans_payouts`) — says "updates view" in comments
3. Migration B forgets to actually `CREATE OR REPLACE VIEW` with the new column
4. Application code references `tphv.new_column` → column does not exist
5. Only fixed when the view is recreated (app restart with `asgi.py` startup code)

**Diagnostic:** If the error happens in a burst and then stops, it self-resolved via a process restart that triggered `CREATE OR REPLACE VIEW` at startup.

**Fix:** Verify the view definition includes all table columns. Add a startup health check that queries the view's column list and compares it against the model's expected columns.

## Duplicate Key Pattern

The `duplicate key value violates unique constraint "trans_device_users_pkey"` pattern:

1. The INSERT comes from the Clover sync worker (IP 10.0.2.43), not the backend API
2. Frequency: every ~5 minutes (matches Clover sync cycle)
3. Root cause: plain INSERT without `ON CONFLICT DO UPDATE / NOTHING`
4. The admin API endpoint has a pre-check (`if existing_link:`) but the Clover sync uses a different code path that skips this

**Fix:**
```sql
INSERT INTO trans_device_users (user_id, device_id, external_device_id, merchant_id_clover, ...)
VALUES ($1, $2, $3, $4, ...)
ON CONFLICT (user_id, device_id, merchant_id_clover) 
DO UPDATE SET last_modification_date = NOW(), status = EXCLUDED.status, assigned_date = EXCLUDED.assigned_date
```

## Lambda Log False Positive Trap

When investigating Lambda errors via `filter-log-events`, always cross-check against the CloudWatch `Errors` metric:

```python
cw = aws_cli(env, "cloudwatch", "get-metric-statistics",
    "--namespace", "AWS/Lambda",
    "--metric-name", "Errors",
    "--dimensions", f"Name=FunctionName,Value={func_name}",
    "--start-time", (NOW - timedelta(hours=1)).isoformat(),
    "--end-time", NOW.isoformat(),
    "--period", "3600", "--statistics", "Sum", "--output", "json")
```

The log filter `?FAILED` matches status messages like `"Found 2 bronze orders to transform (unprocessed or FAILED)"` which are INFO-level, not errors. If `Errors` metric shows 0 but log filter shows hits, it's a false positive — tighten the filter pattern.
