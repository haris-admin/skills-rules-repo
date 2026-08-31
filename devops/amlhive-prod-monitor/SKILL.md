---
name: amlhive-prod-monitor
description: AmLHive direct AWS production monitor — 4x daily script that checks EC2, Docker, RDS, CloudWatch, Sentry, and public endpoints. Produces plain-text reports and delivers via email. Companion to pluto-fleet-monitor skill (which covers full architecture, alert patterns, and known issues).
allowed-tools: [terminal, read_file, write_file]
---

# AmLHive Production Monitor

## When to Use
- Setting up or modifying the `amlhive_prod_monitor.py` script
- Debugging AMLHive cron monitor job failures
- Understanding the 4x daily monitor schedule (5/11/17/23 AEST)
- Checking AMLHive AWS production health

## Architecture

**Script:** `~/.hermes/scripts/amlhive_prod_monitor.py` (v0.4.12+)
**Sibling script:** `~/.hermes/scripts/amlhive_daily_report.py`
**AWS Account:** 560205084533, ap-southeast-2
**Instances:** Backend `amlhive-prod` (t3.medium), Frontend `amlhive-frontend` (t3.small). **Auto-discovered by Name tag** via `get_instance_id()` — hardcoded IDs no longer required. Current (Jul 19): backend `i-052ca2acc74707378`, frontend `i-0eb3f1faa213420ce`. Previously: i-0bda9f... + i-0cb6f5... (replaced Jul 18); i-02276d... + i-0cf88f... (replaced Jul 16).
**RDS:** amlhive-prod.ch4ykiy82n3q.ap-southeast-2.rds.amazonaws.com, postgres 17.9, db.t4g.small, 20GB. Replaced June 2026 (was c9aso80ocbn0, postgres 15.x, 100GB).

## Cron Schedule

| Time (AEST) | Job ID | Delivery |
|-------------|--------|----------|
| 5:00 AM | `4f4dc2487b98` | origin (Telegram + email) |
| 11:00 AM | `6728be78d1bf` | origin |
| 5:00 PM | `d52fa74ab6c1` | origin |
| 11:00 PM | `be5061d19a5a` | origin |

All are `no_agent: true` — the script IS the job.

## Exit Code Logic (Lines 1314-1321)

The monitor exits with **code 1 when P0 alerts exist OR >2 P1 alerts exist**. This is BY DESIGN — not a bug:

```python
# Exit: 0 = healthy/no alerts, 1 = issues
p0_count = sum(1 for a in all_alerts if a.get("severity") == P0)
p1_count = sum(1 for a in all_alerts if a.get("severity") == P1)
if p0_count > 0:
    return 1
if p1_count > 2:
    return 1
return 0
```

**The 11PM run showing `last_status: error` with exit code 1 IS EXPECTED when alerts exist.** The email IS the alert mechanism — exit code 1 signals "issues found" to the cron scheduler, not "script crashed." This is the documented design pattern for `no_agent` alert scripts.

## Report Layout — Summary + Detail (user preference, July 2026)

The report uses a **compact summary on top, full verbose dump on bottom** format:

- **Top: Summary sections** — numbered 1-9 with key findings, status emojis, alert counts
- **Bottom: `━━━ 📋 DETAIL ━━━`** — full raw output from every source:
  - ALL CloudWatch alarm names with reasons, InstanceId tags, timestamps
  - ALL CloudWatch log pattern sample messages and per-pattern counts
  - ALL Sentry event IDs and full error messages (capped at 80 lines)
  - ALL nginx access/error log entries from the Cloudflare section
  - ALL EC2/Docker details including SSM status lines

Originally the format was more verbose, then got stripped down (v0.4.12 rewrite), then user requested restoring details with summary+detail split.

1. **Public Health** — `api.amlhive.com.au/health` + `amlhive.com.au`
2. **Docker Health** — Container status, restarts, OOM, memory/disk
3. **CloudWatch Alarms** — All `amlhive-*` alarms, stale detection
4. **CloudWatch Logs** — Pattern scan on all log groups (10h window)
5. **Sentry** — Event counts + issue details (python-fastapi = P0/P1, javascript-nextjs = P2 drift)
6. **RDS** — Status, CPU, connections, storage, postgres log patterns
7. **Cloudflare Origin** — Nginx SSM tail + CloudWatch nginx 4xx/5xx search
8. **Issue Ledger** — Open/drift/noise/resolved/regression
9. **Legacy** — Fly.io + Vercel (historical reference only)

### Cloudflare / Nginx Monitoring (Section 7)

Detects proxy-layer failures that bypass the app entirely (oversized cookies, malformed headers, upstream failures). The app never runs and Sentry sees nothing when these occur.

**Three detection methods:**
1. **Cloudflare Analytics API** — Origin 4xx/5xx rate via GraphQL (requires zone-scoped token; current R2-only token returns 403 — falls back gracefully)
2. **Nginx access log (SSM tail)** — Last 1000 lines on frontend EC2, greps for 4xx/5xx
3. **CloudWatch filter-log-events** — Searches `/amlhive/frontend-system` for `"HTTP/1.1" 400` and 502/503/504 patterns in 6h window

**Alert thresholds:**
| Pattern | Threshold | Severity |
|---------|-----------|----------|
| nginx 400 | >10 in 6h | P1 (live) |
| nginx 400 | >3 in 6h | P2 (drift) |
| nginx 502 | >3 in 6h | P0 (live) |
| nginx 503/504 | >3 in 6h | P1 (live) |

## Alert Severity

| Severity | Criteria | Examples |
|----------|----------|----------|
| P0 | Live outage | Public health fails; 5xx spike; OOMKilled; DB locked; PII errors |
| P1 | Degradation needing attention | Container restarted; Traceback; Brevo blocked; SSM lost; disk >80% |
| P2 | Observability drift | Stale alarms; javascript-nextjs browser errors; log growth anomaly |

## Pitfalls

- **Exit code 1 ≠ script failure.** `last_status: error` on the 11PM run is normal when alerts exist. Check stderr for `✅ Email sent` to confirm the monitor ran successfully.
- **Instance ID drift (SOLVED with auto-discovery):** ~~Hardcoded instance IDs in both...~~ **Fixed July 2026** — `amlhive_prod_monitor.py` and `amlhive_daily_report.py` now use `get_instance_id()` which discovers running instances by their `Name` tag (`amlhive-prod`, `amlhive-frontend`). A fallback hardcoded ID is provided for when EC2 is unreachable. The module-level cache ensures only one API call per script run. The function is importable and reusable — see `references/ec2-auto-discovery.md`.
  
  **No manual recovery needed on recycle.** If instances are recycled, the next cron run auto-discovers the new IDs. The fallback ensures the script still runs during an EC2 outage.
- **psql NOT pre-installed on Amazon Linux 2023.** When the backend instance is recycled, `psql` must be reinstalled. Run via SSM: `sudo yum install -y postgresql15`. This does NOT survive instance replacement (unlike Ubuntu where it's often pre-installed). The daily report and any SSM-based SQL queries will fail with `psql: command not found` after a new instance launch. Check immediately after any known instance replacement.

- **RDS alarm INSUFFICIENT_DATA — wrong DBInstanceIdentifier dimension:** The 3 RDS CloudWatch alarms (`amlhive-rds-high-cpu`, `amlhive-rds-high-connections`, `amlhive-rds-low-free-storage`) may have their `DBInstanceIdentifier` set to an **internal RDS resource ID** (`db-XXXXX...`) instead of the actual DB instance name (`amlhive-prod`). CloudWatch RDS metrics use the **DB instance name** as the dimension — not the resource ID. When the dimension is wrong, CloudWatch cannot match the metric stream to the alarm, producing permanent INSUFFICIENT_DATA. Verify with:
  ```bash
  aws cloudwatch describe-alarms --alarm-names \\
    amlhive-rds-high-cpu amlhive-rds-high-connections amlhive-rds-low-free-storage \\
    --query 'MetricAlarms[].[AlarmName,Dimensions[0].Value,StateValue]'
  ```
  **Fix** — overwrite all 3 alarms with the correct dimension using `put-metric-alarm`. The full commands are in `references/rds-alarm-dimension-fix.md`. Steps:
  1. Confirm RDS metrics DO flow for the correct dimension (`amlhive-prod`) — check with `get-metric-statistics`
  2. Run `put-metric-alarm` with `--dimensions Name=DBInstanceIdentifier,Value=amlhive-prod`
  3. Verify state transitions within ~15 min (3 evaluation periods × 300s)

- **CloudWatch log time window:** Always pass `--start-time`/`--end-time` to `filter-log-events`. Without it, you get events from the BEGINNING of the stream, not the most recent.
- **Sentry token scope:** The token has `project:read` but not `event:read`. Use `/events/` endpoint (not `/issues/`) for actual event details.
- **javascript-nextjs Sentry errors = P2 drift ALWAYS.** Client-side browser errors are not service-impacting. Only `python-fastapi` generates P1/P0 Sentry alerts.
- **Email is the alert mechanism.** The monitor sends email regardless of exit code. Exit code signals health to the cron scheduler only.
- **`load_env()` must scan `.openclaw/.env` too.** The Cloudflare API token lives in `.openclaw/.env` as `CLOUDFLARE_API_TOKEN`. If `load_env()` only checks `.hermes/.env`, the token won't be found and the Cloudflare section will show "not configured". Fixed July 2026 — both env paths are now scanned.

## Related Skills

- **`pluto-fleet-monitor`** — Full architecture, alert patterns, suppression catalog, known issues. PRIMARY reference for AMLHive monitoring.
- **`pluto-pipeline-orchestration`** — Cron pipeline schedule, recovery, pitfall patterns
- **`tapease-fleet-monitor`** — Same pattern for TapEase (account 707843605914)

## Hourly Probe Cron Jobs

Two additional no_agent scripts run every hour as companions to the 4x daily fleet monitor:

### Hourly Version Check (`hourly_version_check.py`)
- **Schedule:** Every hour at :00
- **Job ID:** `4689311b6ad0`
- **Purpose:** Detects silent-stale-build regression (issue-151 class) — compares API version against local `.version` file
- **Alerts via:** `alert_email.py` (URGENT RED HTML email) on mismatch or unreachable endpoint
- **Tolerance:** mismatch within ~10 min of known deploy may be timing false-positive

### Hourly Attribution Probe (`hourly_attribution_probe.py`)
- **Schedule:** Every hour at :30
- **Job ID:** `b705c3ee3882`
- **Purpose:** Synthetic first-party attribution journey (C152 T5.4) — checks browser first-touch capture + backend persistence
- **Alerts via:** `alert_email.py` on 3+ failures in 15 min or 100% failure in 24h
- See `references/alert-email-module.md` for shared escalation email details

## Linked Reference Files

- `references/aws-credential-loading.md` — AWS credential extraction from Windows .env
- `references/rds-alarm-dimension-fix.md` — Fix for INSUFFICIENT_DATA RDS alarms (wrong DBInstanceIdentifier)
- `references/amlhive-daily-report.md` — Daily business operations report (agencies, users, screenings, KYC, clients, matters, CDD, audit). Cron: 9:15 PM AEST. Emails shoaib@amlhive.com.au + tech@amlhive.com.au. Uses SSM tunnel → local psql.
- `references/ec2-auto-discovery.md` — `get_instance_id()` tag-based auto-discovery function (reusable snippet)
- `references/alert-email-module.md` — Shared `alert_email.py` module for URGENT RED HTML escalation emails
