---
name: tapease-daily-settlement
description: "Tapease Daily Settlement Report — queries trans_clover_transaction_payments, sends HTML email with card scheme breakdown, raw transactions, refunds, and settlement summary"
trigger: "Daily cron at 9:30 PM AEST via no_agent script"
---

# Tapease Daily Settlement Report

## What it does
Generates a daily settlement report for Tapease covering the **9PM→9PM AEST** business day window. Includes payment summary, card scheme breakdown, refunds, raw transactions, and net settlement. Emails HTML + CSV to `hhsiddiqui@gmail.com`.

## Script: `~/.hermes/scripts/tapease_daily_transactions.py`

## Key approach
1. **SSM send-command** — Runs psql directly on backend EC2 `i-062b8ef5437ea6e2f` via `aws ssm send-command`. No local tunnel needed.
2. **Flatten SQL** — Multi-line SQL f-strings are flattened with `sql.replace(chr(10), " ")` before being passed to psql via shell command
3. **Single summary query** — `COUNT, SUM(net_amount), SUM(surcharge), SUM(tip), SUM(cashback), SUM(cash_tendered), FILTER(SUCCESS), FILTER(FAIL)`
4. **Card scheme breakdown** — `GROUP BY client_card_type` with count, amount, success/fail
5. **Refunds** — From `trans_clover_transaction_refunds` using `net_amount` (NOT `bronze_refund_amount` — that column doesn't exist) and `created_time` (NOT `bronze_refund_created_time`)
6. **Remote CSV export** — `\\copy` to temp file on backend EC2 → read via `ssm send-command cat` → write locally → cleanup remote
7. **HTML email** — MIMEMultipart with inline SVG logo, executive summary cards, amount breakdown table, card scheme table, scrollable raw transactions table, refunds section
8. **Error detection** — All psql calls check return code. Connection failure raises `RuntimeError`, not silent "0 rows"
9. **Empty result handling** — All `open(CSV_PATH)` calls guarded with try/except OSError. `\\copy` produces no file when window has 0 rows.
10. **Cron delivery** — Set `deliver: "origin"` on cron job so output appears in chat. `deliver: "local"` saves to files only.

## SSM send-command pattern (replaces old tunnel)
- **Backend EC2**: `i-062b8ef5437ea6e2f` — has psql 15.15 installed
- **Bastion**: `i-06c24009b7ad32725` — does NOT have psql installed
- **Command format**: `aws ssm send-command --instance-ids <EC2> --document-name AWS-RunShellScript --parameters commands=... --output json --region ap-southeast-2`
- **Wait for completion**: Poll `get-command-invocation` every 2s up to 60s
- **Multi-line SQL**: Must flatten with `sql.replace(chr(10), " ")` and `re.sub(r'\s+', ' ', flat)` before wrapping in shell command
- **CSV export flow**: `\\copy (SELECT ...) TO '/tmp/export_TIMESTAMP.csv' WITH CSV HEADER` → `cat /tmp/export_TIMESTAMP.csv` → local write → `rm -f /tmp/export_TIMESTAMP.csv`

### Why not tunnel?
- `aws ssm start-session` (port forwarding) requires `session-manager-plugin` — NOT installed on WSL
- `aws ssm send-command` uses only the standard AWS CLI — always available
- The fleet monitor already uses send-command for all EC2 checks. Same credential approach should be used.

## Amount handling
- DB stores amounts in **cents** (integers)
- `doll(c)` function divides by 100 for display
- Pass **raw cent values** to `doll()` — never pre-divided values
- Net, surcharge, tip are queried as `COALESCE(SUM(...),0)` (cents)

## Window computation — CRITICAL
- The `trans_clover_transaction_payments.created_time` column stores **AEST timestamps WITHOUT timezone** (`timestamp without time zone`). **Do NOT do timezone conversion.**
- Window: `YESTERDAY 21:00:00 → TODAY 21:00:00` AEST
- Use raw AEST strings in SQL: `WHERE created_time>='{LOWER}' AND created_time<='{UPPER}'`
- **NEVER** use `AT TIME ZONE`, UTC conversion, or `'UTC'` suffix. The column IS AEST. Converting to UTC corrupts the comparison.
- This is the OPPOSITE of AML Hive's `performed_at` which IS `timestamptz` (UTC). **Know your column type.**
- ❌ WRONG: `WHERE created_time>='{LOWER_UTC} UTC'` — compares AEST strings against UTC values
- ✅ RIGHT: `WHERE created_time>='{LOWER}'` where LOWER is e.g. `'2026-07-14 21:00:00'`

### AT TIME ZONE pitfall (in case you ever hit it)
`'09:00:00' AT TIME ZONE 'Australia/Sydney'` works BACKWARDS on string literals. PostgreSQL first casts the string to `timestamptz` (using the session timezone, typically UTC), then converts the result TO Sydney local time. So `'09:00:00' AT TIME ZONE 'Sydney'` with a UTC session gives `19:00:00` (7PM), not the expected UTC equivalent of 9AM AEST. The result is a 10-hour window shift.

## Credential loading — CRITICAL: Prefer `.hermes/.env` over `.openclaw/.env`
- **Use `tapease_prod_monitor.make_aws_env()`** — this is the canonical credential loader. It calls `load_tapease_creds()` which reads ONLY `.hermes/.env` and skips commented lines (starting with `#`).
- Must strip stale inherited keys first: `e.pop("AWS_ACCESS_KEY_ID")`, `e.pop("AWS_SECRET_ACCESS_KEY")`, `e.pop("AWS_SESSION_TOKEN")`
- **Always set** `e["AWS_DEFAULT_REGION"] = "ap-southeast-2"` — the `~/.aws/config` has `region = auto` which resolves `ssm.auto.amazonaws.com` and breaks everything
- ⚠️ **Key order matters:** `.openclaw/.env` has the OLD expired credentials (AKIA2J...VLNY). `.hermes/.env` has the NEW active credentials (AKIA2J...MUHP) with the OLD ones commented out.
- **Always use `load_tapease_creds()` from `tapease_prod_monitor`** — it correctly reads `.hermes/.env` and skips comments. Do NOT write your own credential loader that reads `.openclaw/.env` first.
- Tapease keys in `.hermes/.env`: `AWS_ACCESS_KEY_ID_TAPEASE`, `AWS_SECRET_ACCESS_KEY_TAPEASE`
- The `.openclaw/.env` file has `\r` (CRLF) line endings — this can cause double-value issues if scraped manually

## Password fetching
- `fetch_password()` should try Secrets Manager `tapease/rds/credentials-production` first
- Fall back to `DATABASE_PWD_TAPEASE` from `.openclaw/.env`
- The hardcoded fallback pw is: `l6qdw5FDUA68%+TgnPrX:d7m{5Q5?-5F`

## psql error detection (was missing — caused months of false "0 transactions")
- **CRITICAL**: Always check `r.returncode != 0` on psql subprocess — `Connection refused` is NOT "0 rows"
- Pattern: raise `RuntimeError(f"psql failed (exit {r.returncode}): {r.stderr[:200]}")` on non-zero
- Same for `\\copy` — it silently produces empty/no file when connection fails
- The old tunnel-based code silently returned empty stdout when psql couldn't connect, producing "0 txns" for months

## Empty result handling
- `\\copy` produces no file when window has 0 rows — guard ALL `open(CSV_PATH)` calls with try/except OSError
- Guard `os.path.getsize(CSV_PATH)` and CSV attachment in email the same way

## Email
- From: `operator@harishabib.au`
- To: `hhsiddiqui@gmail.com`
- SMTP: `smtp.purelymail.com:587` with STARTTLS
- Password from `.env` SMTP_PASSWORD
- Subject: `🔵 Tapease Daily Settlement Report — YYYY-MM-DD`

## Database
- Host: `tapease-postgres-production.c9aso80ocbn0.ap-southeast-2.rds.amazonaws.com`
- User: `tapease_admin`, DB: `tapease_production`
- Backend EC2 (runs psql): `i-062b8ef5437ea6e2f`
- Bastion (SSM link): `i-06c24009b7ad32725`
- Tables: `trans_clover_transaction_payments`, `trans_clover_transaction_refunds`
- `trans_clover_transaction_refunds` uses `net_amount` and `created_time` — NOT `bronze_refund_*` columns

## Pitfalls
- **`session-manager-plugin` NOT installed** on this WSL — `aws ssm start-session` (port forwarding tunnels) will silently fail. Always use `aws ssm send-command` instead.
- **`~/.aws/config` has `region = auto`** — breaks all AWS CLI calls. Always set `AWS_DEFAULT_REGION=ap-southeast-2` in the env dict.
- **`created_time` is AEST** (not UTC, not timestamptz) — use raw AEST strings, never convert.
- **Refund columns are `net_amount`/`created_time`** — not `bronze_refund_amount`/`bronze_refund_created_time`. Those columns don't exist.
- **Multi-line f-strings break SSM shell commands** — flatten with `chr(10).replace()` and `re.sub(r'\s+', ' ')`.
- **Secrets Manager** with wrong creds returns empty stdout → JSON decode error. Fall back to `.openclaw/.env`.\n- **`load_env()` and `make_aws_env()` can return empty if Tapease creds are commented in `.hermes/.env`** — they're uncommented in `.openclaw/.env`. Always scan both.\n- **`~/.aws/config` `region = auto` breaks AWS CLI.** Always force `AWS_DEFAULT_REGION=ap-southeast-2` in your env dict before making any AWS API call.
