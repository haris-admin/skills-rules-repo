# AML Hive Daily Business Report Patterns

## Overview

Daily business report for AML Hive production — tracks agency creation, user activity, screenings, KYC, clients, matters, CDD, audit entries, and failures. Runs at **9:15 PM AEST** covering the **9AM→9PM** business day window.

**Script:** `~/.hermes/scripts/amlhive_daily_report.py`
**Cron job ID:** `3ebed4e59ee3`
**Schedule:** `15 21 * * *` (daily 9:15 PM AEST)
**Delivery:** Professional HTML email to `shoaib@amlhive.com.au`, `tech@amlhive.com.au` from `operator@harishabib.au`

## Architecture — SSM send-command (NOT tunnel)

Unlike the Tapease daily report (which uses SSM port forwarding + local psql), the AML Hive report uses **SSM send-command** to the backend EC2 because:
- psql is installed on the backend (`sudo yum install -y postgresql15`)
- The report fits within SSM's output limits (single batched query vs. large CSV export)
- The RDS secret is accessible from the backend IAM role (no need to pass credentials through the tunnel)

## Base64 SQL Batching Pattern

Multiple SSM round-trips are SLOW. Batch ALL queries into a single SQL file on the remote:

```python
import base64

sql = """
SELECT '###AGENCIES' as lbl,
  (SELECT COUNT(*) FROM agencies) as total,
  (SELECT COUNT(*) FROM agencies WHERE is_active=true) as active;
SELECT '###USERS' as lbl,
  (SELECT COUNT(*) FROM users) as total;
"""
encoded = base64.b64encode(sql.encode()).decode()
ssm(f"echo '{encoded}' | base64 -d > /tmp/query.sql", timeout=15)
output = ssm(f"PGPASSWORD='{PWD}' psql -h {RDS} -U {USER} -d {DB} -At -f /tmp/query.sql", timeout=90)
```

### Parsing the output

Label each result with `###LABEL` and parse line by line:

```python
for line in output.strip().split("\n"):
    if not line.startswith("###"): continue
    parts = line[3:].split("|")
    label = parts[0]
    values = parts[1:]  # pipe-separated ints
```

### Key tables and their timestamp columns for the 9AM→9PM window

| Table | Timestamp Column | Description |
|-------|-----------------|-------------|
| `agencies` | `created_at` | Agency accounts |
| `users` | `created_at` | Agency user accounts |
| `platform_users` | `last_login` | Admin logins (⚠️ NULL for all users — UNUSABLE) |
| `screening_results` | `performed_at` | PEP/sanctions screening runs |
| `employee_screening_records` | `performed_at` | Employee background checks |
| `kyc_identities` | `created_at` | Customer KYC identity records |
| `clients` | `created_at` | Client records |
| `matters` | `created_at` | Legal matters |
| `cdd_checklists` | `created_at` | CDD checklists |
| `audit_entries` | `performed_at` | System audit events |
| `onboarding_progress` | `completed_at` | Onboarding completions |
| `kyb_records` | `created_at` | KYB business verification |
| `platform_audit_log` | `performed_at` | Admin audit log (sparse - 29 total entries) |

### Query Window Logic

```python
AEST = timezone(timedelta(hours=10))
NOW = datetime.now(AEST)
TODAY = NOW.strftime("%Y-%m-%d")
LOWER = f"{TODAY} 09:00:00"
UPPER = f"{TODAY} 21:00:00"
TZ = "Australia/Sydney"

# SQL: WHERE created_time >= ('{LOWER}' AT TIME ZONE '{TZ}')
#       AND created_time < ('{UPPER}' AT TIME ZONE '{TZ}')
```

## SQL Batching — Single-query Approach

The entire report runs in **one SSM call** using a single multi-statement SQL file. Each SELECT outputs a pipe-delimited row prefixed with `###LABEL`:

```
###AGENCIES|0|28|10|14|2|2
###USERS|0|43|38
###SCREENINGS|0|0|0|0
###KYC|0|0|0|0
###CLIENTS_MATTERS|0|350|0|12|2
###CDD|0|0|0
###AUDIT|0
###FAILURES|0|0
```

The parsing code strips `###` from the start, splits by `|`, and maps label → value array.

## Professional HTML Email Format

Uses the same template as the Tapease daily report but with **teal accent** (`#26a69a`) instead of Tapease's `#00bcd4`:

- Gradient header: `#1a237e → #26a69a`
- Cards: `#00695c` (dark teal) headings
- Sections: Agencies, Users, Screenings, KYC, Clients & Matters, CDD & Onboarding, Audit, Issues
- No raw data table (unlike Tapease which has all 90+ rows inline)
- No CSV attachment (all stats fit in the email body)
- Status emoji: 🟢 if no failures, 🟡 if any KYC/KYB failures

## RDS Connection Details

- Host: `amlhive-prod.ch4ykiy82n3q.ap-southeast-2.rds.amazonaws.com`
- Port: `5432`
- Database: `amlhive`
- User: `amlhive`
- Password: AWS Secrets Manager `amlhive/prod/rds`
- Secret key: `password` in the JSON `SecretString`
- Backend EC2: `i-02276d537152046d9`
- psql: `sudo yum install -y postgresql15` (Amazon Linux 2023)

## Key Rules

- Window is 9AM→9PM AEST, NOT 9PM→9PM (Tapease uses the latter)
- ALL queries in one SSM call — do NOT make individual calls per metric
- Use `###` label prefix for easy parsing
- `last_login` on `platform_users` is NULL for all records — do NOT use for login tracking
- `platform_audit_log` has only 29 entries — sparse, not useful for daily metrics
- Email to `shoaib@amlhive.com.au` + `tech@amlhive.com.au` only (not `hhsiddiqui@gmail.com`)
