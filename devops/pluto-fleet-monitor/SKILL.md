---
name: pluto-fleet-monitor
description: "★ Pluto Fleet Monitor — AMLHive AWS Production. EC2, Docker, RDS, CloudWatch, Sentry, public endpoints. Fly.io + Vercel RETIRED Aug 2026 — checks removed (Supabase Auth remains in design). Runs 4x daily (5/11/17/23 AEST). Emails to EMAIL_TO_AMLHIVE from .env."
version: 3.5.0
author: Pluto
license: MIT
---

# ★ Pluto Fleet Monitor — AMLHive AWS Production

## When to Use

- **Primary use:** Monitoring AMLHive production on AWS — EC2, Docker, RDS, CloudWatch alarms and logs, Sentry, public API/frontend health
- Debugging the fleet monitor cron jobs
- Investigating stale CloudWatch alarms or observability drift
- Checking container restart patterns across cron cycles
- Verifying AWS account identity before trusting monitor output
- Fallback: quick health check of Fly.io / Vercel rollback surfaces
- **Diagnosing delivery discrepancies:** when Telegram shows different data than email

## Architecture — AWS First

| | |
|-----|------|
| Pre Jul 14 2026 | Instances: i-02276d (backend), i-0cf88f (frontend). Old instances terminated. |
| Jul 16 2026 | Instances replaced: i-0bda9f (backend), i-0cb6f5 (frontend). Old RDS endpoint c9aso80ocbn0 replaced with ch4ykiy82n3q. New RDS has new schema (tables renamed, status values UPPERCASE). |

**⚠️ Instance ID drift — SOLVED with auto-discovery (July 2026).** Previously, when an EC2 instance was replaced, its ID changed and both monitor scripts needed manual patching. Now `amlhive_prod_monitor.py` and `amlhive_daily_report.py` use `get_instance_id()` which auto-discovers instances by Name tag. No manual intervention needed on recycle. See `amlhive-prod-monitor` skill's `references/ec2-auto-discovery.md` for the full reusable function.

| Layer | Status | Details |
|-------|--------|---------|
| ☁️ AWS | **Primary** | Account 560205084533, ap-southeast-2 |
| 🖥️ EC2 | Running | Backend: amlhive-prod (t3.medium, auto-discovered by tag) Frontend: amlhive-frontend (t3.small, auto-discovered by tag) |
| 🐳 Docker | Running | Backend `amlhive-app-1`, Frontend `amlhive-frontend` |
| 🗄️ RDS | Available | amlhive-prod, postgres 17.x, db.t4g.small, 100GB. Endpoint: amlhive-prod.ch4ykiy82n3q.ap-southeast-2.rds.amazonaws.com (replaced Jul 2026 — was c9aso80ocbn0) |
| ✈️ Fly.io | **RETIRED Aug 2026** | No longer checked — removed from monitor. amlhive-api was rollback surface only. |
| ▲ Vercel | **RETIRED Aug 2026** | No longer checked — vercel_monitor.py archived, cron `745ec76c6bf9` removed. |
| 🔐 Supabase Auth | **Still in design** | The only non-AWS component retained — auth remains on Supabase. |

**⚡ 2026-08-08 update:** All Fly.io and Vercel monitoring removed per Haris — `check_legacy_fly()` and `check_legacy_vercel()` deleted from `amlhive_prod_monitor.py`, section 9 (LEGACY) removed from the report, standalone `vercel_monitor.py` cron removed and script archived to `~/.hermes/scripts/retired/`. Supabase Auth remains in the design.

## Script Architecture — Two Monitors, One Fleet

**There are TWO scripts that run the same schedule (5/11/17/23 AEST):**

### Primary (source of truth): `amlhive_prod_monitor.py`

- AWS-first: EC2, Docker, RDS, CloudWatch alarms + logs, Sentry, public endpoints
- **No Fly.io/Vercel checks (removed Aug 2026)** — sections 1-8 only
- Uses Sentry `/events/` with `statsPeriod=10h` — accurate time-windowed data
- Emails via raw smtplib using `EMAIL_TO_AMLHIVE` recipients
- Cron jobs: `4f4dc2487b98` (5AM), `6728be78d1bf` (11AM), `d52fa74ab6c1` (5PM), `be5061d19a5a` (11PM)
- Deliver: **origin** (Telegram) + email
- **Cloudflare / Nginx monitoring (Section 7, added Jul 2026):** Detects proxy-layer failures that bypass the app entirely (oversized cookies, malformed headers, upstream failures). Uses SSM tail of nginx access log + CloudWatch filter on `/amlhive/frontend-system` for HTTP 400/502/503/504 patterns. Alerts when >10 400s or >3 5xxs in 6h window.

### Retired (Aug 2026): `pluto_fleet_monitor.py` + `vercel_monitor.py`

- **`pluto_fleet_monitor.py`** — old unified Fly.io + Vercel + Sentry monitor, cron `a0b1f0f642af` paused 10 Jul 2026, script archived to `~/.hermes/scripts/retired/` 08 Aug 2026
- **`vercel_monitor.py`** — dedicated Vercel watchdog, cron `745ec76c6bf9` (5:05 AM/PM) **removed 08 Aug 2026**, script archived to `~/.hermes/scripts/retired/`
- Neither is scheduled; do not re-enable without explicit instruction

## Diagnosis: Telegram Shows Different Data Than Email

**Symptoms:** Email report shows accurate, clean data (0 errors, all green) while Telegram shows the same format but with stale Sentry errors (old ProgrammingError, PII, Brevo issues from days ago).

**Root cause:** Two cron jobs running the same schedule with swapped delivery targets:

| Cron Job | Script | deliver: | Data source | Accurate? |
|----------|--------|----------|-------------|-----------|
| `a0b1f0f642af` (legacy) | `pluto_fleet_monitor.py` | origin → **Telegram** | Sentry `/issues/` → 403 → lifetime counts | ❌ Stale |
| `4f4dc..` (new, 4 slots) | `amlhive_prod_monitor.py` | local → **file only** | Sentry `/events/` + 10h window | ✅ Accurate |

**Fix:**
1. Check which cron jobs run the same schedule via `cronjob list`
2. Identify which scripts are the "source of truth" vs "legacy"
3. For `no_agent: true` scripts: stdout IS the message — `deliver` field controls where it goes
4. Legacy scripts that also hardcode `send_professional_email()` inside their code will continue emailing even after cron deliver is changed to `local` — these must be **paused** not just redirected
5. Update the accurate script's delivery to `origin`, pause the legacy job

**Prevention:** Any new monitor script should:
- Be the ONLY script covering its schedule
- Have clear `deliver` targeting (origin for Telegram, local for archival-only)
- Not duplicate email sends that overlap with another script

## Hourly Probe Companion Jobs

Two no_agent scripts run on the hour as companions to the 4x daily fleet monitor — both escalate via `alert_email.py` (URGENT RED HTML email):

| Job | Schedule | Script | Alert Condition |
|-----|----------|--------|-----------------|
| Version Check | :00 | `hourly_version_check.py` | API unreachable or version mismatch (stale build) |
| Attribution Probe | :30 | `hourly_attribution_probe.py` | 3+ failures in 15 min or 100% failure in 24h |

See `amlhive-prod-monitor` → `references/alert-email-module.md` for escalation details.

## AML Hive Daily Business Report

A companion cron to the 4x daily fleet monitor — runs once per day at **9:15 PM AEST** covering the **9AM→9PM** business day window.

**Script:** `~/.hermes/scripts/amlhive_daily_report.py`
**Job ID:** `3ebed4e59ee3`
**Delivery:** Professional HTML email to `shoaib@amlhive.com.au`, `tech@amlhive.com.au` from `operator@harishabib.au` via Purelymail SMTP

### What It Reports

| Section | Metrics |
|---------|---------|
| 🏢 Agencies | New today, total, active, onboarding, trial, cancelled |
| 👥 Users | New today, total, active |
| 🔍 Screenings | Total, CLEAN, HIT, employee screenings |
| 🪪 KYC | Created, verified, pending, expired/failed |
| 📁 Clients & Matters | New clients, total clients, new matters, open, active |
| ✅ CDD & Onboarding | Created, signed off, completed |
| 📋 Audit | Entry count today |
| ⚠️ Issues | KYC failures, KYB unverified |

### Architecture

Uses **SSM send-command** (not tunnel) — psql is installed on the backend EC2 and the RDS is in the same VPC. All queries are batched into ONE SQL file via base64 encoding to minimize SSM round-trips. See `references/amlhive-daily-report-patterns.md` for full query templates and parsing code.

**⚠️ Timezone fix (July 2026):** The `AT TIME ZONE` PostgreSQL operator works BACKWARDS on string literals — it casts the string to timestamptz (session TZ) then converts TO the named zone. For a UTC session, `'09:00:00' AT TIME ZONE 'Sydney'` gives 19:00 (7PM), not the UTC equivalent of 9AM Sydney. All daily reports now pre-compute UTC timestamps in Python using `datetime.astimezone(utc)` and inject them as `WHERE col>='YYYY-MM-DD HH:MM:SS UTC'` directly in SQL.

### Key Differences from Tapease Daily Report

| Aspect | AML Hive | Tapease |
|--------|----------|---------|
| Window | 9AM→9PM (12h) | 9PM→9PM (24h) |
| Approach | SSM send-command | SSM tunnel + local psql |
| CSV attachment | No (stats fit in email body) | Yes (90+ raw transaction rows) |
| Recipients | shoaib@amlhive.com.au, tech@amlhive.com.au | hhsiddiqui@gmail.com |
| `last_login` tracking | NULL — NOT usable | Not applicable |

## ⚠️ Known Bugs & Fixes

### Literal `\n` in Reports (Jul 2026)
**Root cause:** `build_report()` at line 1839 used `"\\n".join(lines)` — the double backslash produces literal `\n` characters instead of real newlines.

**Fix:** Changed to `"\n".join(lines)` — single backslash produces real newline characters.

**Symptoms:** Fleet monitor output showed `\n` as visible text in both cron messages and emails. Output was a single unreadable line.

**Lesson:** Always use `"\n".join(lines)` for multi-line report assembly. Single backslash = real newline. Double backslash = literal `\n`.
