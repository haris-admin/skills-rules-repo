# Tapease Daily Transaction Export

## Cron
- Schedule: `30 21 * * *` (9:30 PM AEST)
- Job ID: `114039a7ff9b`
- Script: `~/.hermes/scripts/tapease_daily_transactions.py`
- Delivery: Email to `hhsiddiqui@gmail.com` from `operator@harishabib.au`

## Data Window
- 9PM previous day → 9PM current day AEST (24 hours)
- Timestamps stored in UTC with timezone (`timestamptz`)

## Timezone Handling
PostgreSQL `AT TIME ZONE` on bare strings works BACKWARDS (casts to timestamptz/UTC first). Compute UTC equivalents in Python and use as `'YYYY-MM-DD HH:MM:SS UTC'` in SQL.

## Database Connection
- RDS: `tapease-postgres-production.c9aso80ocbn0.ap-southeast-2.rds.amazonaws.com`
- DB: `tapease_production`
- User: `tapease_admin`
- Password: AWS Secrets Manager `tapease/rds/credentials-production`
- Tunnel: SSM via bastion `i-06c24009b7ad32725`, local port 5434
- Query via local psql through tunnel (avoids 3000-char SSM truncation)

## Tables
- `trans_clover_transaction_payments` — payments with `created_time` (timestamptz), `amount` fields in CENTS
- `trans_clover_transaction_refunds` — refunds with `bronze_refund_created_time`, `bronze_refund_amount`
- Card type: `client_card_type`, status: `payment_result` (SUCCESS/FAIL/null)

## Key Queries
- Summary: COUNT, SUM(net_amount), SUM(surcharge_amount), SUM(payment_tip_amount), SUM(cashback_amount), success/fail counts
- Card scheme: GROUP BY `client_card_type` with counts and amounts
- Refunds: COUNT, SUM(bronze_refund_amount) WHERE bronze_refund_voided IS NULL OR 0

## Amount Formatting
All amounts stored in CENTS. Use `doll(cents)` → `f"${int(cents)/100:,.2f}"`. NEVER pass pre-converted dollar values to `doll()` — that double-divides.
