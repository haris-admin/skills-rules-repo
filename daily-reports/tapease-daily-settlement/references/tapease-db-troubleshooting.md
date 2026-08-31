# Tapease DB Troubleshooting: False-Zero Transactions

## Root cause chain (July 2026)

1. **Wrong column type assumption**: `created_time` in `trans_clover_transaction_payments` is `timestamp without time zone` storing AEST timestamps. The code assumed UTC or `timestamptz` and applied timezone conversion.

2. **AT TIME ZONE backwards**: `'09:00:00' AT TIME ZONE 'Australia/Sydney'` on string literals treats the string as UTC and converts TO Sydney time (9AM → 7PM). The window was shifted 10h.

3. **UTC pre-compute also wrong**: "Fixing" AT TIME ZONE by pre-computing UTC in Python (`LOWER_UTC = ...astimezone(utc)`) made it WORSE — comparing AEST-stored strings against UTC values.

4. **Silent psql failure**: `run_psql()` returned `r.stdout` without checking `r.returncode`. When the tunnel failed, psql returned "Connection refused" on stderr, stdout was empty, and the script treated it as "0 rows."

5. **Stale AWS credentials**: The Tapease access keys were deactivated/rotated. The `env()` function inherited old ones from the terminal environment and didn't strip them.

6. **Wrong region**: `~/.aws/config` had `region = auto` which resolved `ssm.auto.amazonaws.com` — an invalid endpoint.

## The fix chain

| Layer | Problem | Fix |
|-------|---------|-----|
| Timezone | Column stores AEST, code treated as UTC | Compare raw AEST strings: `WHERE created_time>='{LOWER}'` |
| psql errors | Returned empty stdout silently on failure | Check `r.returncode != 0` → raise RuntimeError |
| AWS creds | Inherited stale keys; `setdefault` didn't override | `pop()` all AWS_* keys, then re-set from .env files |
| Region | `~/.aws/config` had `region = auto` | Force `AWS_DEFAULT_REGION=ap-southeast-2` in `env()` |
| Env file order | Tapease creds commented in `.hermes/.env` | Read `.openclaw/.env` first (uncommented there) |
| Tunnel startup | Fixed sleep didn't wait for port | Poll `ss -tlnp | grep 5434` in loop up to 30s |
| Password fetch | AMLHive creds can't read Tapease Secrets Manager | Fallback to `DATABASE_PWD_TAPEASE` from `.openclaw/.env` |

## How to prevent

1. **Always check column data type** before writing queries: `SELECT data_type FROM information_schema.columns WHERE table_name='...' AND column_name='...'`
2. **Test with raw strings first**: Before adding any timezone logic, run `WHERE col>='YYYY-MM-DD HH:MM:SS'` with the user's expected values.
3. **Never trust zero results** — add a total-count sanity check: `SELECT MIN(created_time), MAX(created_time), COUNT(*) FROM table` to verify the connection and data range.
4. **Credentials should be verified** at startup: `aws sts get-caller-identity` to confirm they're valid.
5. **Tunnel should be verified** by checking the port is actually listening before running psql.
