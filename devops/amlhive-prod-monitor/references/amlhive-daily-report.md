# AML Hive Daily Business Report

## Overview

Daily business operations report for AML Hive — queries the RDS for agencies, users, screenings, KYC, clients, matters, CDD, audit entries, and failures for the business day window (9AM AEST → 9PM AEST), generates a professional HTML email with key metrics, and emails stakeholders.

**Cron:** Daily at 9:15 PM AEST (`15 21 * * *`)
**Script:** `~/.hermes/scripts/amlhive_daily_report.py`
**Job ID:** `3ebed4e59ee3`
**Delivery:** Professional HTML email to `shoaib@amlhive.com.au`, `tech@amlhive.com.au` from `operator@harishabib.au`

## Architecture

Uses the same SSM tunnel pattern as Tapease but with AMLHive infra:

```
WSL (psql) -> localhost:5435 -> SSM -> Backend EC2 (i-02276d...) -> RDS:5432
```

**Credentials:** `AWS_ACCESS_KEY_ID_AMLHIVE` / `AWS_SECRET_ACCESS_KEY_AMLHIVE` from Windows `.env` — loaded via `amlhive_prod_monitor.load_aws_creds()`
**RDS Secret:** `amlhive/prod/rds` in AWS Secrets Manager
**RDS Endpoint:** `amlhive-prod.ch4ykiy82n3q.ap-southeast-2.rds.amazonaws.com`
**DB:** `amlhive`, user `amlhive`, password from secret

## SSM Tunnel Setup

```bash
#!/bin/bash
export PATH="/tmp/ssm-extract/usr/local/sessionmanagerplugin/bin:$PATH"
export AWS_ACCESS_KEY_ID=<AMLHIVE access key>
export AWS_SECRET_ACCESS_KEY=<AMLHIVE secret key>
aws ssm start-session \
    --region ap-southeast-2 \
    --target i-02276d537152046d9 \
    --document-name AWS-StartPortForwardingSessionToRemoteHost \
    --parameters '{"host":["amlhive-prod.ch4ykiy82n3q.ap-southeast-2.rds.amazonaws.com"],"portNumber":["5432"],"localPortNumber":["5435"]}'
```

## Performance: Single-Query Pattern

The AMLHive monitor runs 10+ sub-queries. To avoid SSM latency, **bundle all queries into one SQL file** using a single SSM call:

1. Base64-encode the complete SQL script
2. `echo '<base64>' | base64 -d > /tmp/amh_all.sql` on remote
3. Run `psql -f /tmp/amh_all.sql` once
4. Parse labeled results with `###` delimiters

Each SELECT outputs: `###LABEL|val1|val2|val3...` — parse by splitting on `|`.

## Query Window

9AM → 9PM AEST (business day). Uses `AT TIME ZONE 'Australia/Sydney'` consistently.

```python
AEST = timezone(timedelta(hours=10))
NOW = datetime.now(AEST)
TODAY = NOW.strftime("%Y-%m-%d")
LOWER = f"{TODAY} 09:00:00"
UPPER = f"{TODAY} 21:00:00"
```

## Metrics Queried

### Agencies (`agencies`)
| Metric | Query | Column |
|--------|-------|--------|
| Created today | COUNT WHERE created_at IN window | `created_at` (timestamptz) |
| Total | COUNT(*) | — |
| Active | is_active=true AND lifecycle_status='active' | `is_active` (bool), `lifecycle_status` |
| Trial | lifecycle_status='trial' | — |
| Onboarding | lifecycle_status='onboarding' | — |
| Cancelled | lifecycle_status='cancelled' | — |

### Users (`users`)
- Created today (created_at), total (COUNT), active (is_active=true)

### Platform Users (`platform_users`)
- Total, logins today (last_login IN window)

### Screenings (`screening_results`)
- Total today (performed_at), CLEAN count, HIT count, employee screenings

### KYC (`kyc_identities`)
- Created today (created_at), VERIFIED, PENDING, EXPIRED/FAILED/REJECTED

### Clients (`clients`) & Matters (`matters`)
- Clients: created today, total
- Matters: created today, OPEN, ACTIVE

### CDD (`cdd_checklists`)
- Created today, SIGNED_OFF count

### Onboarding (`onboarding_progress`)
- Completed today

### Audit (`audit_entries`)
- Total entries today

### Issues
- KYC failures: verification_status IN ('FAILED','EXPIRED','REJECTED')
- KYB failures: status NOT IN ('COMPLETED','VERIFIED')

## Single-Query Template (abbreviated)

```sql
SELECT '###AGENCIES' as lbl,
  (SELECT COUNT(*) FROM agencies WHERE created_at>=('{LOWER}' AT TIME ZONE 'Australia/Sydney') AND created_at<('{UPPER}' AT TIME ZONE 'Australia/Sydney')),
  (SELECT COUNT(*) FROM agencies),
  ...;

SELECT '###USERS' as lbl,
  (SELECT COUNT(*) FROM users WHERE created_at>=('{LOWER}' AT TIME ZONE 'Australia/Sydney') ...),
  ...;
```

## Professional HTML Email Format

- **Color scheme:** Navy (#1a237e) + Teal (#26a69a) — distinct from Tapease (#00bcd4)
- **Logo:** Same Pluto SVG, different accent color
- **Sections:** Agencies → Users → Screenings → KYC → Clients & Matters → CDD → Audit → Issues
- **No CSV attachment** — this is a summary report, not a data export
- **Success/failure color-coded** throughout

## Tables Reference

| Table | Key Timestamp | Key Status Column |
|-------|---------------|-------------------|
| `agencies` | `created_at` | `is_active`, `lifecycle_status` |
| `users` | `created_at` | `is_active` |
| `platform_users` | `last_login`, `created_at` | — |
| `screening_results` | `performed_at` | `outcome` (CLEAN/HIT) |
| `employee_screening_records` | `performed_at` | `outcome` |
| `kyc_identities` | `created_at` | `verification_status` |
| `kyb_records` | `created_at` | `status` |
| `clients` | `created_at` | — |
| `matters` | `created_at` | `status` (OPEN/ACTIVE) |
| `cdd_checklists` | `created_at` | `status` |
| `onboarding_progress` | `completed_at` | — |
| `audit_entries` | `performed_at` | `action_type` |
