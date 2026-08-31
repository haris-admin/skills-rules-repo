---
name: amlhive-daily-business-report
description: "AML Hive Daily System Report — 9AM→9PM AEST window tracking agencies, users, screenings, KYC/KYB, matters, clients, CDD, audit, user activity with hourly trend chart and auto-generated system health assessment"
trigger: "Daily cron at 9:15 PM AEST via no_agent script"
version: 2.0.0
---

# AML Hive Daily System Report

## What it does
Generates a daily **system behavior report** for AML Hive covering the **9AM→9PM AEST** window. Shows how the system is performing — agency growth, user activity, screening throughput, KYC completion rates, matter pipeline, hourly activity trends, and auto-generated health assessment. Emails HTML report to `hhsiddiqui@gmail.com` (To) with BCC to `shoaib@amlhive.com.au` and `tech@amlhive.com.au`.

**This is NOT an infrastructure monitoring report.** Infrastructure checks (EC2, Docker, CloudWatch, nginx, Cloudflare) belong in the fleet monitor (5/11/17/23). The 9:15 PM report focuses exclusively on RDS business data and system behavior — explaining how the system is working and behaving, not whether the servers are up.

## Script: `~/.hermes/scripts/amlhive_daily_report.py`

## Key approach
1. **SSM send-command** — Runs psql directly on backend EC2 `i-0b111b75d3c70fcb7` (auto-discovered by Name tag `amlhive-prod-backend`). No local tunnel needed. Same credential approach as the fleet monitor (`load_aws_creds()` from `amlhive_prod_monitor`).
2. **All DB params from Secrets Manager** — `fetch_creds()` pulls username, password, host, port, dbname from `amlhive/prod/rds-admin` on every run. **Nothing hardcoded** — no literal host, no `-U amlhive`, no PGPASSWORD literal.
3. **rds-admin FIRST (RLS bypass)** — The app user (`amlhive/prod/rds`, RLS-scoped) returns ZEROS on cross-agency aggregates because RLS restricts each role to one agency. The daily business report needs cross-agency totals, so it must connect as `rds-admin`. Secret order: `amlhive/prod/rds-admin` → `amlhive/prod/rds` → `tapease/rds/credentials-production` (last one is stale, may not exist in this account).
4. **Username comes from the secret** — the rds-admin username is NOT `amlhive` (16-char name). Hardcoding `-U amlhive` produces `password authentication failed for user "amlhive"` even with the correct password.
5. **Requires SSL** — Must prefix commands with `PGSSLMODE=require PGPASSWORD=...`.
6. **Single batched query** — All metrics in one SQL string with `###LABEL` prefixes. Split on `###` and parse pipe-separated values.
7. **Flatten SQL** — Multi-line SQL f-strings are flattened with `sql.replace(chr(10), " ")` and `re.sub(r'\s+', ' ', flat)` before being passed to psql via shell command.
8. **Dynamic UTC window** — Pre-computed from AEST window via `datetime.strptime().replace(tzinfo=AEST).astimezone(timezone.utc)`. No hardcoded dates.
9. **Hourly activity chart** — Separate query to `platform_audit_log` table, extracts `hour from performed_at`, builds text-based bar chart.
10. **Auto-generated health assessment** — Rule-based heuristic: KYC pending → issue, screening failures → issue, no activity → issue, new agencies → positive insight.

## Report Format — 8 Sections

| Section | Data | What it tells you |
|---------|------|-------------------|
| 🚀 Growth Today | Agencies created/total/active/onboarding/trial | Business growth velocity |
| 👥 Users & Activity | New/total/active users, platform users, audit events, active users | User adoption and daily engagement |
| 🔍 Screening Pipeline | New/completed/in-progress/failed + completion rate | Workflow throughput health |
| 🆔 KYC / KYB Status | Today totals, verified/pending, verification rates | Compliance pipeline health |
| 📁 Matters & Clients | Pipeline: new/open/active/closed matters + clients + CDD | Case pipeline and client base |
| ⏰ Activity Trend | Hourly bar chart of platform audit log events (█ characters) | Peak usage times, dead hours |
| 📋 Audit Trail | Total audit events recorded today | Compliance logging activity |
| 💡 Assessment | Auto-generated issues + insights | Quick health verdict |

## SQL Tables (Current Schema — Updated July 2026)

| Old Name | New Name | Notes |
|----------|----------|-------|
| `screenings` | `employee_screening_records` | Uses `performed_at` (not `created_at`). `outcome` values: `CLEAN`, `HIT` (not `completed`/`in_progress`/`failed`). `decision` values: `FALSE_POSITIVE` or NULL |
| `kyc` | `kyc_identities` | Values UPPERCASE: `VERIFIED`, `PENDING`, `EXPIRED`, `FAILED`, `REFER` |
| `kyb` | `kyb_records` | Uses `status` (not `verification_status`). Values: `Active` |
| `cdd` | `cdd_checklists` | Uses `status` (UPPERCASE: `IN_PROGRESS`, `SIGNED_OFF`) |
| `user_sessions` | `platform_audit_log` | Uses `performed_at` (not `created_at`), `platform_user_id` (not `user_id`) |
| `audit_entries` | `audit_entries` (unchanged) | Now uses `performed_at` instead of `created_at` |
| `agencies` | `agencies` (unchanged) | Uses `created_at` |
| `users` | `users` (unchanged) | Uses `created_at` |
| `matters` | `matters` (unchanged) | Uses `created_at` |
| `clients` | `clients` (unchanged) | Uses `created_at` |

## Timestamp Columns Per Table

| Table | Timestamp column | Type |
|-------|-----------------|------|
| `agencies` | `created_at` | timestamptz |
| `users` | `created_at` | timestamptz |
| `employee_screening_records` | `performed_at` | timestamptz |
| `kyc_identities` | `created_at` | timestamptz |
| `kyb_records` | `created_at` | timestamptz |
| `matters` | `created_at` | timestamptz |
| `clients` | `created_at` | timestamptz |
| `cdd_checklists` | `created_at` | timestamptz |
| `audit_entries` | `performed_at` | timestamptz |
| `platform_audit_log` | `performed_at` | timestamptz |

## Activity Chart Rendering
```python
peak = max(hourly.values()) if hourly else 1
bar = "█" * max(1, int(c / max(peak, 1) * 20))
# Renders as:   09:00 ██████████████ 15
```

## SSM send-command pattern
- **Backend EC2**: Auto-discovered by Name tag (`amlhive-prod`) via `get_instance_id()` — no hardcoded IDs. Falls back to `i-05e1c3d33cacb4015` if EC2 unreachable (this is the SSM-registered instance; a previous refresh had no SSM agent).
- **psql**: Already installed on backend (`sudo yum install -y postgresql15` done Jul 19). Requires reinstall if instance replaced.
- **Full schema reference**: `skill_view(name='amlhive-daily-business-report', file_path='references/amlhive-prod-rds-schema.md')`
- **Credentials**: `load_aws_creds()` from `amlhive_prod_monitor` (returns env dict with `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_DEFAULT_REGION`)
- **RDS creds**: `fetch_creds()` → `aws secretsmanager get-secret-value --secret-id amlhive/prod/rds-admin` — returns username/password/host/port/dbname dict, all consumed at runtime
- **RLS caveat**: NEVER use the app secret (`amlhive/prod/rds`) for cross-agency aggregates — RLS scopes it to one agency and returns zeros. The report MUST use `rds-admin`.
- **Command**: `aws ssm send-command --instance-ids <EC2> --document-name AWS-RunShellScript --parameters commands=...`
- **Poll**: `get-command-invocation` every 2s up to 90s (45 iterations)
- **SQL flattening**: Required before wrapping in shell command
- **SSL**: `PGSSLMODE=require` required

## Email
- From: `operator@harishabib.au`
- To: `hhsiddiqui@gmail.com` (visible To)
- Bcc: `shoaib@amlhive.com.au`, `tech@amlhive.com.au`
- SMTP: `smtp.purelymail.com:587` STARTTLS
- Subject: `📊 AML Hive Daily System Report — YYYY-MM-DD`
- HTML + plain text MIMEMultipart

## Database
- **Host**: From Secrets Manager `amlhive/prod/rds-admin` `host` field (NOT hardcoded — was `amlhive-prod.ch4ykiy82n3q.ap-southeast-2.rds.amazonaws.com` as of Aug 2026)
- **User**: From secret `username` field — rds-admin user is a 16-char name (NOT `amlhive`; hardcoding `-U amlhive` = auth failure)
- **DB**: From secret `dbname` field (default `amlhive`, NOT `amlhive_prod` — that db doesn't exist)
- **Password**: From Secrets Manager `amlhive/prod/rds-admin` — NOT hardcoded
- **Port**: From secret `port` field (default 5432)
- **SSL**: Required (`PGSSLMODE=require`)
- AWS creds from `.hermes/.env`: `AWS_ACCESS_KEY_ID_AMLHIVE` / `AWS_SECRET_ACCESS_KEY_AMLHIVE`

## Pitfalls
- **RLS makes app-user queries return ZEROS (Aug 2026)** — the app DB role (`amlhive/*` from `amlhive/prod/rds`) is RLS-scoped to a single agency, so cross-agency aggregates (total agencies/users/matters) return 0. The daily report MUST connect as `amlhive/prod/rds-admin` (RLS bypass). Symptom: report "works" (email sends) but shows 0s everywhere — that's RLS, not a quiet day.
- **Hardcoded `-U amlhive` = auth failure even with correct password (Aug 2026)** — the rds-admin username in the secret is a 16-char name containing "amlhive" (e.g. `amlhive_<suffix>`), NOT `amlhive`. Use the secret's `username` field. Symptom: `FATAL: password authentication failed for user "amlhive"` while the actual password is correct.
- **psql -At output is pipe-separated on ONE line, not one value per line.** When running multi-column SELECT with `psql -At`, the output is `###SUMMARY|14|28` — all values on ONE line. The parser MUST split the first line by `|` and take values from `parts[1:]`, NOT look at `lines[1:]`. This was the root cause of the all-zero report bug on July 16 2026 — the parser was reading `lines[1:]` which was always empty when all values fit on the first line.
  ```python
  # CORRECT parsing for psql -At multi-column output:
  line = lines[0].strip()
  parts = line.split("|")
  label = parts[0]  # e.g. "###SUMMARY"
  vals = [int(p.strip()) for p in parts[1:]]  # e.g. [14, 28, ...]
  ```
  The v() helper function in the script handles this with x.split("|") but was bypassed because the previous parser used lines[1:] which was always empty. Current SSM-registered backend is i-05e1c3d33cacb4015.
- **psql installation (Amazon Linux 2023):** `sudo yum install -y postgresql15` — NOT apt-get. Already installed on current backend (Jul 19). Must reinstall if instance is replaced.
- **RDS was also replaced** — new endpoint, new database, new password, new schema.
- **Schema was updated** — table names changed. See the table mapping above.
- **`clients.is_active` doesn't exist** — use `WHERE (is_archived=false OR is_archived IS NULL)` for active clients. The column is `is_archived`, not `is_active`.\n- **All status values are UPPERCASE** — `kyc_identities.verification_status` uses `VERIFIED`, `PENDING`, `EXPIRED`, `FAILED`, `REFER`. `employee_screening_records.outcome` uses `CLEAN`, `HIT`. `cdd_checklists.status` uses `IN_PROGRESS`, `SIGNED_OFF`. `kyb_records.status` uses `Active` (mixed case). Do NOT use lowercase values in WHERE clauses.\n- **`screenings` table doesn't exist** — use `employee_screening_records` with `outcome`/`decision` columns.
- **`user_sessions` table doesn't exist** — use `platform_audit_log` with `performed_at`/`platform_user_id`.
- **SSM send-command** uses `AWS-RunShellScript`, NOT `AWS-StartPortForwardingSessionToRemoteHost` (that needs `session-manager-plugin` which isn't installed on WSL).
- **Multi-line f-strings break SSM shell commands** — always flatten SQL with `chr(10).replace()` and `re.sub(r'\\s+', ' ')`.
- **This report is NOT for infrastructure monitoring** — Cloudflare/nginx/EC2/Docker checks belong in the fleet monitor. Adding them here dilutes the report's purpose.
- **`AT TIME ZONE` string-literal pitfall** — `'09:00:00' AT TIME ZONE 'Sydney'` works BACKWARDS. Never use in SQL.
- **AML Hive vs Tapease timezone are opposite**:
  - AML Hive: `timestamptz` → use UTC strings
  - Tapease: `timestamp without tz` (AEST) → use raw AEST strings
