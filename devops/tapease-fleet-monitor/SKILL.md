---
name: tapease-fleet-monitor
description: "★ TapEase Fleet Monitor — Direct AWS Production. Account 707843605914. EC2, SSM process checks, nginx logs, CloudWatch alarms, Lambda, RDS. Runs 4x daily (5/11/17/23 AEST). Replaces old bridge-based monitor (Jun 26-Jul 8 2026)."
version: 1.0.0
author: Pluto
license: MIT
---

# ★ TapEase Fleet Monitor — Direct AWS Production

## When to Use

- **Primary use:** Monitoring TapEase production on AWS — EC2 instances, running processes (uvicorn/nginx/Next.js), nginx error logs, CloudWatch alarms, Lambda functions (clover-sync, rds-backup, log-forwarder), RDS PostgreSQL
- Debugging the tapease fleet monitor cron jobs
- Investigating the TapEase infrastructure
- Replacing the old bridge-based monitor which returned HTML errors since June 26, 2026

## Architecture

| Layer | Details |
|-------|---------|
| ☁️ AWS Account | **707843605914** — ap-southeast-2 |
| 🖥️ Backend EC2 | `tapease-backend-production` (i-062b8ef5437ea6e2f, t4g.medium, 30GB) |
| 🖥️ Frontend EC2 | `tapease-frontend-production` (i-0aca7e109d0f6e773, t4g.small, 30GB) |
| 🖥️ Bastion EC2 | `tapease-bastion-production` (i-06c24009b7ad32725, t4g.micro) |
| 🖥️ NAT EC2 | `tapease-nat-instance-production` (i-0c9a14c400f1e7cdc, t4g.micro) |
| ⚙️ Backend Stack | **uvicorn** (FastAPI/ASGI, port 8000), **nginx** (port 80), **Redis** (port 6379) |
| ⚙️ Frontend Stack | **Next.js 16.1.6** via PM2 (port 3000), **nginx** (ports 80/443, TLS) |
| 🗄️ RDS | `tapease-postgres-production` (db.t4g.small, postgres 17.9, 20GB) |
| ☁️ Lambda | `tapease-clover-sync-production`, `tapease-rds-backup-production`, `tapease-log-forwarder-production` |
| S3 | `tapease-logs-otel-production`, `tapease-objects`, `tapease-customers-data` |
| 🌐 Public | www.tapease.com.au (HTTP 200), app.tapease.com.au (DNS NXDOMAIN) |

**Key architectural differences from AML Hive:** No Docker — bare-metal EC2 with systemd services + PM2. nginx error logs at `/var/log/nginx/tapease-error.log`. Backend logs via journald (`journalctl -u tapease-backend`). CloudWatch agent on both production instances publishing to `/aws/ec2/backend/tapease-production` and `/aws/ec2/frontend/tapease-production`.

## Linked Reference Files

- `references/rds-deep-dive-methodology.md` — 4-step tracing for RDS error patterns
- `references/tapease-daily-export-patterns.md` — Full query templates, timezone handling, SSM escaping, and professional email template for the daily transaction export

**Primary:** `~/.hermes/scripts/tapease_prod_monitor.py` (created Jul 8, 2026)

775-line standalone production monitor. AWS CLI + SSM (no bridge dependency). Covers 7 report sections in one run. Emails via raw smtplib to `EMAIL_TO_TAPEASE` from Windows `.env`.

**Deprecated (retired Jun 26-Jul 8, 2026):** `~/.hermes/scripts/tapease_monitor_runner.py` — old bridge-based monitor that called `POST /tapease/monitor` on the n8n bridge at port 18796. Returned HTML error pages. Replaced by direct monitor.

## Cron Schedule (4x daily — same slots as AML Hive)

```
0 5  * * * → Job: dbd3cb1b5bd3  | script: tapease_prod_monitor.py
0 11 * * * → Job: 582bd225ddd1  | script: tapease_prod_monitor.py
0 17 * * * → Job: 1086e6405da1  | script: tapease_prod_monitor.py
0 23 * * * → Job: be81c61778a8  | script: tapease_prod_monitor.py
```

All `no_agent: true` (script IS the job). Email is the alert mechanism (exit 0 always — alerts go in email body, not exit code).

## Report Format — 8 Required Sections

1. **📊 Overall Status** — Healthy / Attention / Incident with P0/P1/P2 counts
2. **☁️ AWS Identity** — Account verification against 707843605914
3. **🌐 Public Health** — www.tapease.com.au (HTTP 200), app.tapease.com.au (known NXDOMAIN)
4. **🖥️ EC2 Instances** — State, SSM Online/Offline, uptime, disk %, memory % for all 4 production instances
5. **⚙️ Process Health** — SSM `ps aux` checking: uvicorn, nginx, redis (backend); Next.js, PM2, nginx (frontend)
6. **📝 Nginx Error Logs** — SSM tail of tapease-error.log filtered to **last 10 hours** (date prefix parsing)
7. **🔔 CloudWatch Alarms** — All 22 `tapease-*` alarms. INSUFFICIENT_DATA reported as drift, ALARM reported as P1
8. **☁️ Lambda** — Clover Sync, RDS Backup, Log Forwarder: error log events (last 10h) + CloudWatch metrics (invocations/errors last 1h)
9. **🗄️ RDS** — Instance status, endpoint, storage. Postgres log pattern grouping (duplicate key violations, missing columns, syntax errors)

## Credential Loading

TapEase AWS credentials are in Windows `.env`:
```bash
AWS_ACCESS_KEY_ID_TAPEASE=...   # IAM_GRAFANA user
AWS_SECRET_ACCESS_KEY_TAPEASE=...
EMAIL_TO_TAPEASE=shoaib.habib@a2square.com.au,admin@harishabib.au,hhsiddiqui@gmail.com
```

Loaded via Python `line.split("=", 1)[1].strip()` (never `source` the Windows .env in bash — special characters break shell parsing).

### Email recipient loading mechanism + drift trap (Aug 2026)

`tapease_prod_monitor.py` → `get_email_recipients()` (~line 590) reads ONLY the
Windows `.env` at `/mnt/c/Users/habib/.hermes/.env`, matching
`line.startswith("EMAIL_TO_TAPEASE=")`. **Gotcha:** if the key EXISTS but holds
a wrong value (e.g. drifted to a single non-target address), the script's
fallback — which DOES include `hhsiddiqui@gmail.com` — never fires. A key with
the wrong value behaves like a valid config, so the recipient list is whatever
the key literally says.

**Safe verification pattern (never print raw secret/recipient values):** parse
the env value structurally and print only counts + a boolean:

```python
for line in open('/mnt/c/Users/habib/.hermes/.env'):
    if line.startswith('EMAIL_TO_TAPEASE='):
        v = line.split('=', 1)[1].strip()
        addrs = [a.strip().lower() for a in v.split(',') if a.strip()]
        print(f'{len(addrs)} addr(s) | target hhsiddiqui@gmail.com present: {target.lower() in addrs}')
```

Expected healthy state: 1+ addresses with `hhsiddiqui@gmail.com` present (Tapease
emails go ONLY to hhsiddiqui@gmail.com; never mix AML Hive recipients). Known
drift 2026-08-21→31: value was a single non-target address — CoS escalation
active (relationship file `workspace/relationships/current.md`), re-verified at
each monitor run. Fix is a one-line .env edit + Hermes reload, then re-verify.

## SSM Command Pattern (Critical)

Multi-line SSM commands need proper JSON quoting. Use `json.dumps()` for the command parameter:

```python
def ssm_shell(env, instance_id, command, timeout_sec=20):
    r = subprocess.run(["aws", "ssm", "send-command",
        "--instance-ids", instance_id,
        "--document-name", "AWS-RunShellScript",
        "--parameters", f"commands={json.dumps(command)}",
        "--output", "json"],
        capture_output=True, text=True, timeout=30, env=env)
    # ... wait 7s, then list-command-invocations ...
```

**Without `json.dumps()`**, semicolons, pipes, and single quotes in the command string break the AWS CLI parameter parser with `Error parsing parameter '--parameters'`.

## Nginx Log Time Filtering

The SSM tail returns raw log lines. Filter to last 10 hours in Python by parsing the nginx date prefix:

```python
# nginx format: "YYYY/MM/DD HH:MM:SS [error] ..."
parts = l.split()
if len(parts) >= 2:
    log_dt_str = f"{parts[0]} {parts[1]}"
    cutoff_str = ten_hours_ago.strftime("%Y/%m/%d %H:%M:%S")
    if log_dt_str >= cutoff_str:
        error_lines.append(l)
```

This prevents yesterday's errors from appearing in today's report when the log file is quiet.

## CloudWatch Timestamp Gotcha

CloudWatch `describe-alarms` returns `StateUpdatedTimestamp` as a **float** (epoch milliseconds) in JSON output, not a string. Direct indexing `a[2][:16]` fails with `TypeError: 'float' object is not subscriptable`:

```python
# FIX: Wrap in str()
name, state, ts = a[0], a[1], str(a[2] or "")[:16]
```

## Lambda Filter Pattern Trap

CloudWatch Logs `filter-log-events` with `?FAILED` in the filter pattern matches messages like:
```
Found 2 bronze orders to transform (unprocessed or FAILED)
```
This is an **INFO-level status message**, not an actual error. The Lambda's CloudWatch `Errors` metric shows 0, confirming no real errors.

**Fix:** Use more specific filter patterns and cross-check against the CloudWatch `Errors` metric:
```python
"--filter-pattern", '?ERROR ?Traceback ?Exception ?"process exited" ?"Task timed out" ?errorMessage',
```

**Always validate Lambda error log counts against the `Errors` metric** from `get-metric-statistics` — logs can produce false positives from status messages containing error-like keywords.

## Running SQL on Private RDS via SSM (Two Approaches)

For automations that need to query the Tapease RDS (private subnet), there are two approaches:

### Option A: SSM send-command on backend EC2 (WORKS — no plugin needed)

The **backend EC2** (`i-062b8ef5437ea6e2f`) has psql 15.15 installed. Use `aws ssm send-command` to run psql there directly:

```python
cmd = f'PGPASSWORD="{RDS_PW}" psql -h {RDS_HOST} -U {RDS_USER} -d {RDS_DB} -At -c "{flat_sql}"'
result = _ssm_run([cmd])
```

**Key points:**
- Multi-line SQL must be **flattened** (`sql.replace(chr(10), " ")` + `re.sub(r'\s+', ' ', flat)`) before wrapping in shell command
- The bastion (`i-06c24009b7ad32725`) does NOT have psql installed — use the backend
- Password comes from Secrets Manager `tapease/rds/credentials-production` with fallback to `.openclaw/.env`
- Wait for completion by polling `get-command-invocation` every 2s up to 60s
- `aws ssm send-command` only needs standard AWS CLI — NO `session-manager-plugin` required

**CSV export via SSM:** `\\copy (query) TO '/tmp/export.csv'` on remote → `cat /tmp/export.csv` → local write → `rm -f /tmp/export.csv`

### Option B: SSM Tunnel + Local psql (requires session-manager-plugin)

The bastion EC2 (`i-06c24009b7ad32725`) has SSM access and can reach the RDS. This requires the **session-manager-plugin** which is NOT installed on this WSL. If you install it:

```bash
# Install:
pip install session-manager-plugin  # or apt/brew
# Then:
aws ssm start-session --region ap-southeast-2 --target i-06c24009b7ad32725 \
    --document-name AWS-StartPortForwardingSessionToRemoteHost \
    --parameters '{"host":["tapease-postgres..."],"portNumber":["5432"],"localPortNumber":["5434"]}'
```

**Note:** This WSL instance does NOT have the plugin. Option A is the only working path currently.

### Comparison

| Factor | SSM send-command (Option A) | SSM tunnel (Option B) |
|--------|----------------------|-------------------------------|
| Plugin needed | No (standard awscli) | Yes (session-manager-plugin) |
| SQL newlines | Must flatten before quoting | Any SQL works |
| Output size | Unlimited (read from invocation) | Unlimited (local pipe) |
| CSV export | Remote file → cat → cleanup | Direct `\\copy` to local |
| Credentials | Must set `AWS_DEFAULT_REGION=ap-southeast-2` explicitly | Same requirement |

## Daily Transaction Export Cron

**Purpose:** Export 24 hours of `trans_clover_transaction_payments` + refunds, send professional HTML email with full analysis.

**Schedule:** Daily at 9:30 PM AEST (`30 21 * * *`)
**Script:** `~/.hermes/scripts/tapease_daily_transactions.py`
**Job ID:** `114039a7ff9b`
**Delivery:** Professional HTML email + CSV to `hhsiddiqui@gmail.com` from `operator@harishabib.au` via Purelymail SMTP

### Query Window Logic — CRITICAL TIMEZONE NOTE

9PM previous day → 9PM current day (AEST).

The `trans_clover_transaction_payments.created_time` column stores **AEST timestamps WITHOUT timezone** (`timestamp without time zone`). **Do NOT use `AT TIME ZONE` or any UTC conversion.**

```python
AEST = timezone(timedelta(hours=10))
now = datetime.now(AEST)
lower = f"{(now - timedelta(days=1)).strftime('%Y-%m-%d')} 21:00:00"
upper = f"{now.strftime('%Y-%m-%d')} 21:00:00"
# SQL: WHERE created_time >= '{lower}' AND created_time <= '{upper}'
# NO AT TIME ZONE. NO UTC SUFFIX. The column IS AEST.
```

**Historical bug (Jul 2026):** The script previously used `AT TIME ZONE 'Australia/Sydney'` which works BACKWARDS on string literals, shifting the window by 10 hours and producing ~40% fewer transactions. The fix was to remove all timezone conversion and use raw AEST strings.

### Queries Run

1. **Payment summary** — COUNT, SUM(net,surcharge,tip,cashback), passed/failed counts
2. **Card scheme breakdown** — GROUP BY client_card_type: count, amount, success/fail per scheme (VISA, MC, AMEX, etc.)
3. **Refund summary** — COUNT, SUM(bronze_refund_amount) from `trans_clover_transaction_refunds` (non-voided)
4. **Full `\copy` export** — all payment columns to CSV

### Professional HTML Email Format

- **Header:** Deep navy + teal gradient, inline Pluto SVG logo, date/business window, status indicator
- **Executive Summary:** 5 stat cards (Total, Approved, Failed, Gross, Net Settlement), success rate visual bar
- **Amount Breakdown:** Net, Surcharge, Tips, Cashback, Gross, minus Refunds, Net Settlement
- **Card Scheme Breakdown:** Per-scheme: count, amount, OK/fail, success rate %
- **Raw Transactions:** ALL rows in scrollable HTML table — ID, Time (AEST), Result, Net, Sur, Card, Method, Last4
- **Refunds:** Count + amount
- **Footer:** Pluto branding, generated timestamp, "Confidential" notice
- **CSV always attached** as base64 application/octet-stream

### Key Rules

- ALL raw transaction rows MUST appear in the HTML body — never just "see attached CSV"
- Inline CSS only (email clients strip external stylesheets)
- Pluto SVG logo embedded inline (no external URLs)
- Color: #1a237e (navy) + #00bcd4 (teal) gradient
- Success rate shown as green/red progress bar
- SMTP via Purelymail smtp.purelymail.com:587 STARTTLS

### Reference

See `references/tapease-daily-export-patterns.md` for full templates.

## Daily Payout Sweep (Added July 26, 2026)

**Purpose:** Nightly check for merchants with negative Grand Total (`total_payout_amount < 0` in cents) in `trans_payouts`. Groups by status, sends professional HTML email if any negative balances found.

### Key Facts

- **Negative balance is in `total_payout_amount` (cents), NOT `available_payout`** — the dashboard "Grand Total" column maps to `total_payout_amount / 100`. `available_payout` is a separate calculated field that doesn't always reflect negative net positions.
- **Values are in cents (integer)** — divide by 100 for dollars. `total_payout` = "Amt" column, `total_payout_amount` = "Grand Total" column.
- **Dashboard's "Pay ID" column = `user_id`** in the database (column 2 in the dashboard view).

### Query

```sql
SELECT user_id, total_payout_amount, total_payout, commission, status
FROM trans_payouts
WHERE total_payout_amount < 0
ORDER BY status, total_payout_amount ASC
```

### Status Codes

| Code | Label | Meaning |
|------|-------|---------|
| 0 | Pending (Transaction) | Default — from transaction file |
| 1 | Pending (Requested) | Manual payout request by user |
| 2 | Approved | Payout approved for processing |
| 3 | Rejected | Cancellation/failed payout |

### Scripts

| Script | Purpose | Path |
|--------|---------|------|
| `tapease_payout_sweep.py` | CLI output — run from terminal or cron with `no_agent: true` | `~/.hermes/scripts/tapease_payout_sweep.py` |
| `tapease_payout_email.py` | Professional HTML email version — queries DB, builds HTML email, sends via Purelymail SMTP. Fetches backend + frontend version from EC2 instances. | `~/.hermes/scripts/tapease_payout_email.py` |

**Cron:** Job `77f0402cb1de` — 03:45 AEST daily — `no_agent: true` — script: `tapease_payout_email.py`
**Delivery:** Email to hhsiddiqui@gmail.com (Tapease emails ONLY — never Bcc AML Hive recipients)

### Version Number Display

The daily payout email fetches **live version numbers** from running EC2 instances and displays them in the header, date bar, and footer:

```python
# Backend version — read from config.py on backend EC2
out = ssm_run(env, "grep '^VERSION' /home/ec2-user/app/backend/app/config.py")
# Returns: VERSION = "4.1.38"

# Frontend version — read from package.json on frontend EC2
out = ssm_run(env, "grep '\"version\"' /home/ec2-user/app/package.json",
              instance_id="i-0aca7e109d0f6e773")
# Returns: "version": "0.6.29"
```

**Paths differ between instances:**
- Backend: `/home/ec2-user/app/backend/app/config.py`
- Frontend: `/home/ec2-user/app/package.json` (on `i-0aca7e109d0f6e773`)

The version appears in the email subject line (`🔵 TapEase Payout Sweep — Tuesday 28 July 2026 (v4.1.38)`), the date bar, and the footer. This gives an immediate visual confirmation of what's deployed.

### Negative Balance in DB vs Dashboard

The dashboard "Grand Total" column = `total_payout_amount / 100` (cents). The "Amt" column = `total_payout / 100`. **Always use `total_payout_amount < 0`** for the negative balance query, not `available_payout` (which is a separate calculated field).

### Email Delivery Rule (CRITICAL)

**Tapease emails go ONLY to `hhsiddiqui@gmail.com`.** Do NOT Bcc `shoaib@amlhive.com.au` or `tech@amlhive.com.au` on any Tapease communication. AML Hive emails go to `hhsiddiqui@gmail.com` + Bcc `shoaib@amlhive.com.au, tech@amlhive.com.au`. The two delivery lists are separate and must not be mixed.

### Professional HTML Email Format

The `tapease_payout_email.py` script sends a professional HTML email matching the same style as the 09:30 PM AML Hive Daily Report:

- **Header:** Deep navy gradient (`#1a237e → #283593`), "🔵 TapEase Payout Sweep" title
- **Date bar:** Light indigo background (`#e8eaf6`)
- **Warning banner:** Orange left-border (`#fff3e0` bg, `#ff9800` accent) — shows total negative exposure in red
- **Status sections:** Each status group (Pending/Approved) gets its own table with User ID, Amount, Grand Total columns
- **Footer:** "Automated daily sweep · TapEase Production"
- SMTP via Purelymail `smtp.purelymail.com:587` STARTTLS, From: `operator@harishabib.au`

### DB Connection

Uses SSM send-command on backend (`i-062b8ef5437ea6e2f`) with psql. Password fetched from Secrets Manager `tapease/rds/credentials-production` via `aws secretsmanager get-secret-value`. No tunnel or plugin needed.

### Known Pattern

Negative `total_payout_amount` occurs periodically — merchants can owe money (chargebacks, fee adjustments, commission net-negative payouts). The sweep catches these daily at 03:45 so they don't accumulate unnoticed. Output format (grouped by status):

```
─── Approved (1 rows, $-642.50) ───
   User IDs: 65

─── Pending (Transaction) (3 rows, $-36.19) ───
   User IDs: 96, 103, 1095
```

Both scripts always exit 0 (the data delivery IS the success outcome — negative balances found is not a script error).

## Known Issues

### ✅ RESOLVED: Bridge HTML Error Pages (Jul 8, 2026)
Old `tapease_monitor_runner.py` called `POST /tapease/monitor` on the n8n bridge (Windows, port 18796). Since June 26, the bridge returned HTML error pages instead of JSON → `JSONDecodeError` on every run. **Fix:** Replaced with direct AWS CLI + SSM monitor (`tapease_prod_monitor.py`). No bridge dependency. The bridge at port 18796 is still needed for Gumby GC research dispatch (`POST /research` and `POST /pluto/deliver`) but no longer for monitoring.

### ✅ RESOLVED: Double Email (Jul 8, 2026)
Old bridge-based monitor had two email-sending paths: (1) PowerShell `professional_email_unified.ps1` via the bridge, and (2) Python `send_email()` in `tapease_monitor_runner.py`. The new direct monitor has a single email send at the end — no duplication.

### 🔴 RDS Duplicate Key Violations — Clover Sync Schema Drift
`duplicate key value violates unique constraint "trans_device_users_pkey"` — 25x+ per day from IP 10.0.2.43 (Clover sync worker). Root cause: plain INSERT without `ON CONFLICT` handling. Also: `column tphv.commission does not exist` — caused by view definition drift between migrations. See `references/rds-deep-dive-methodology.md` for the full 4-step tracing methodology (extract → classify by IP → map to code path → trace migration history). These are P1 — may require backend code changes to handle upsert instead of insert.

### 🔴 app.tapease.com.au DNS NXDOMAIN
app.tapease.com.au does not resolve (public website is www.tapease.com.au, which works). Reported as P2 observability drift — not a live incident.

### ⚠️ Python urllib User-Agent — Cloudflare WAF Block (CROSS-REFERENCE)

If public health checks produce false HTTP 403, check whether the script uses bare `urllib.request.Request(url)` without a User-Agent header. Cloudflare WAF blocks `Python-urllib/3.x`. See `pluto-fleet-monitor` skill's "API/Frontend False 403 — Cloudflare WAF Blocks Python-urllib" section for the full fix pattern (browser User-Agent → 200 OK). This applies to any HTTP health check in `tapease_prod_monitor.py` as well.

## Related Skills

- `pluto-fleet-monitor` — AML Hive fleet monitor (same pattern, different infra — Docker-based)
- `pluto-pipeline-orchestration` — Full cron pipeline schedule including TapEase 4x daily slots
- `windows-bridge-management` — Manages the n8n bridge (now only used for Gumby GC research, not TapEase monitoring)
