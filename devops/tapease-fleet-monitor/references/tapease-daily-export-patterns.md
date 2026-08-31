# Tapease Daily Transaction Export Patterns

## Overview

Daily settlement report for Tapease — queries `trans_clover_transaction_payments` and `trans_clover_transaction_refunds` for the business day window (9PM AEST yesterday → 9PM AEST today), generates a professional HTML email with full analysis, and emails it to stakeholders.

**Cron:** Daily at 9:30 PM AEST (`30 21 * * *`)
**Script:** `~/.hermes/scripts/tapease_daily_transactions.py`
**Job:** `114039a7ff9b`
**Delivery:** Professional HTML email + CSV to `hhsiddiqui@gmail.com` from `operator@harishabib.au`

## Architecture: SSM Tunnel + Local psql (Preferred)

The RDS is in a private subnet. The bastion EC2 (`i-06c24009b7ad32725`) tunnels traffic:

```
WSL (psql) -> localhost:5434 -> SSM -> Bastion -> RDS:5432
```

### Install SSM Plugin (one-time)
```bash
curl -sO "https://s3.amazonaws.com/session-manager-downloads/plugin/latest/ubuntu_64bit/session-manager-plugin.deb"
mkdir -p /tmp/ssm-extract && dpkg-deb -x /tmp/ssm-plugin.deb /tmp/ssm-extract/
export PATH="/tmp/ssm-extract/usr/local/sessionmanagerplugin/bin:$PATH"
```

### Tunnel Script
```bash
#!/bin/bash
export PATH="/tmp/ssm-extract/usr/local/sessionmanagerplugin/bin:$PATH"
export AWS_ACCESS_KEY_ID=<TAPEASE access key>
export AWS_SECRET_ACCESS_KEY=<TAPEASE secret key>
aws ssm start-session \
    --region ap-southeast-2 \
    --target i-06c24009b7ad32725 \
    --document-name AWS-StartPortForwardingSessionToRemoteHost \
    --parameters '{"host":["tapease-postgres-production.c9aso80ocbn0.ap-southeast-2.rds.amazonaws.com"],"portNumber":["5432"],"localPortNumber":["5434"]}'
```

### Credential Loading
```python
def fetch_password():
    e = os.environ.copy()
    # Credentials from .env lines starting with AWS_ACCESS_KEY_ID_TAPEASE=
    c = ["aws","secretsmanager","get-secret-value","--region","ap-southeast-2",
         "--secret-id","tapease/rds/credentials-production","--output","json"]
    r = subprocess.run(c, env=e, capture_output=True, text=True, timeout=15)
    return json.loads(json.loads(r.stdout)["SecretString"])["password"]
```

## Timezone Rules — CRITICAL

**RDS session timezone is UTC.** Stored timestamps have `+00` offset. Business queries target AEST (UTC+10).

**WRONG** — string interpreted as UTC:
```sql
WHERE created_time > '2026-07-13 21:00:00'
```

**RIGHT** — declares AEST explicitly:
```sql
WHERE created_time >= ('2026-07-13 21:00:00' AT TIME ZONE 'Australia/Sydney')
  AND created_time < ('2026-07-14 21:00:00' AT TIME ZONE 'Australia/Sydney')
```

Without `AT TIME ZONE`, the 9PM window shifts 10 hours and captures wrong transactions.

## SQL Queries

### 1. Payment Summary
Returns: COUNT, SUM(net_amount), SUM(surcharge), SUM(tip), SUM(cashback), SUM(cash_tendered), passed, failed, unknown.

```sql
SELECT COUNT(*),COALESCE(SUM(net_amount),0),COALESCE(SUM(surcharge_amount),0),
  COALESCE(SUM(payment_tip_amount),0),COALESCE(SUM(cashback_amount),0),COALESCE(SUM(cash_tendered),0),
  COUNT(*) FILTER (WHERE payment_result='SUCCESS'),
  COUNT(*) FILTER (WHERE payment_result='FAIL'),
  COUNT(*) FILTER (WHERE payment_result IS NULL OR payment_result='')
FROM trans_clover_transaction_payments
WHERE created_time>=('{LOWER}' AT TIME ZONE 'Australia/Sydney')
  AND created_time<('{UPPER}' AT TIME ZONE 'Australia/Sydney')
```

### 2. Card Scheme Breakdown
Groups by `client_card_type` (VISA, MASTERCARD, AMEX, etc.).

```sql
SELECT COALESCE(NULLIF(client_card_type,''),'UNKNOWN'),COUNT(*),
  COALESCE(SUM(net_amount),0),
  COUNT(*) FILTER (WHERE payment_result='SUCCESS'),
  COUNT(*) FILTER (WHERE payment_result='FAIL')
FROM trans_clover_transaction_payments
WHERE created_time>=('{LOWER}' AT TIME ZONE 'Australia/Sydney')
  AND created_time<('{UPPER}' AT TIME ZONE 'Australia/Sydney')
GROUP BY 1 ORDER BY 2 DESC
```

### 3. Refund Summary
```sql
SELECT COALESCE(COUNT(*),0),COALESCE(SUM(bronze_refund_amount),0)
FROM trans_clover_transaction_refunds
WHERE bronze_refund_created_time>=('{LOWER}' AT TIME ZONE 'Australia/Sydney')
  AND bronze_refund_created_time<('{UPPER}' AT TIME ZONE 'Australia/Sydney')
  AND (bronze_refund_voided IS NULL OR bronze_refund_voided=0)
```

Note: Refunds use `bronze_` prefixed columns — different structure from payments.

### 4. Full CSV Export
```sql
\copy (SELECT * FROM trans_clover_transaction_payments
WHERE created_time>=('{LOWER}' AT TIME ZONE 'Australia/Sydney')
  AND created_time<('{UPPER}' AT TIME ZONE 'Australia/Sydney')
ORDER BY created_time) TO '/tmp/tapease_export.csv' WITH CSV HEADER
```

## Currency Display — Double-Division Pitfall

Amounts stored as cents (bigint):

```python
def doll(c): return f"${int(c)/100:,.2f}"  # c is in cents
```

**⚠️ NEVER pass dollar-converted values to `doll()`.** If you've already divided by 100 (e.g. `net_d = t_net/100.0`), `doll(net_d)` will divide by 100 again → $6,397.53 becomes $63.97.

**RIGHT — pass raw cents:**
```python
doll(t_net)       # t_net is raw cents from SUM(net_amount)
doll(t_sur)       # raw cents
doll(t_net + t_sur)  # raw cent sum
```

**WRONG — double division:**
```python
net_d = t_net / 100.0
doll(net_d)       # divides by 100 AGAIN → $63 instead of $6,397
```

**Safe pattern:** Keep ALL arithmetic in cents. Only call `doll()` once — with the raw cent value. The `doll()` input should always be a bigint directly from the database SUM, not a float you've already divided.

## Professional HTML Email Format
```python
def doll(c): return f"${int(c)/100:,.2f}"
```

## Professional HTML Email Format

### Color Scheme
- **Primary:** #1a237e (deep navy), **Accent:** #00bcd4 (teal)
- **Success:** #4caf50, **Danger:** #f44336, **Warning:** #ff9800
- **Background:** #f0f2f5

### Structure
1. **Header** — Navy-teal gradient banner with Pluto SVG logo, date, business window, status indicator
2. **Executive Summary** — 5 stat cards (Total, Approved, Failed, Gross, Net) + success rate progress bar
3. **Amount Breakdown** — Net, Surcharge, Tips, Cashback, Gross, minus Refunds, Net Settlement
4. **Card Scheme Breakdown** — Per-scheme table: count, amount, OK/fail, success rate %
5. **Raw Transactions** — ALL rows in scrollable HTML table: ID, Time (AEST), Result, Net, Sur, Card, Method, Last4
6. **Refunds** — Count + amount
7. **Footer** — Pluto logo, generated timestamp, "Powered by Pluto Automation", "Confidential"

### Key Rules
- **ALL raw transaction rows in HTML body** — never "see attached CSV" only
- **Inline CSS only** — email clients strip external stylesheets
- **Pluto SVG logo embedded inline** — no external image URLs
- **Success/fail color-coded** — green bold for SUCCESS, red bold for FAIL
- **Times in AEST** — convert UTC `created_time` by adding 10 hours
- **Success bar** — green/red floating divs for visual ratio
- **CSV always attached** as base64 application/octet-stream

## SMTP Configuration
```python
SERVER = "smtp.purelymail.com"
PORT = 587
FROM = "operator@harishabib.au"
TO = ["hhsiddiqui@gmail.com"]
# Password from .env: SMTP_PASSWORD=
```

## Tables Reference

### trans_clover_transaction_payments (tctp)
Key columns: `id`, `tran_type`, `payment_result`, `created_time` (timestamptz), `net_amount` (bigint, cents), `surcharge_amount`, `payment_tip_amount`, `cashback_amount`, `cash_tendered`, `client_card_type` (VARCHAR — VISA, MASTERCARD, AMEX), `card_last4`, `payment_method`, `card_entry_type`, `order_id`, `payment_status`, `state`, `status`

### trans_clover_transaction_refunds
Key columns: `bronze_refund_id`, `bronze_refund_amount` (bigint, cents), `bronze_refund_created_time` (timestamptz), `bronze_refund_status`, `bronze_refund_voided` (int, 1=voided), `bronze_transaction_id`, `bronze_order_ref_id`
