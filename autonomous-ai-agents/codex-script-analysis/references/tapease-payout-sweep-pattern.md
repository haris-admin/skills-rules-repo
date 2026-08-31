# Tapease Payout Sweep — SSM + OpenRouter Pattern

Daily cron at 03:45 AEST checking trans_payouts for negative available_payout. Script: tapease_payout_sweep.py, Cron: 77f0402cb1de.

## Key Details
- RDS: tapease-postgres-production in account 707843605914, region ap-southeast-2
- Secret: tapease/rds/credentials-production in AWS Secrets Manager
- SSM target: Backend EC2 i-062b8ef5437ea6e2f (has psql 15.15)
- Query: SELECT user_id, available_payout... WHERE available_payout < 0 ORDER BY available_payout ASC
- Column last_modification_date NOT updated_at