# Fleet Monitoring Tracks — AmLHive AWS & TapEase (Separate Tracks)

Full detail on the two parallel fleet-monitoring pipelines referenced from the main schedule's "FLEET MONITORS (4x daily at 5/11/17/23)" line. Both run independently of the daily briefing chain and use raw SMTP instead of the Telegram delivery path.

## AmLHive AWS Fleet Monitoring

A **parallel pipeline** monitoring AmLHive AWS infrastructure (account `560205084533`) through direct AWS CLI calls + SSM. Runs the same 4-slot schedule as TapEase. Uses raw smtplib email with ━━━ plain-text formatting.

| Time (AEST) | Job ID | What It Does | Delivery |
|---|---|---|---|
| 5:00 AM | `4f4dc2487b98` | Full EC2 + Docker + CloudWatch + RDS health check | local (email from script) |
| 11:00 AM | `6728be78d1bf` | Full EC2 + Docker + CloudWatch + RDS health check | local (email from script) |
| 5:00 PM | `d52fa74ab6c1` | Full EC2 + Docker + CloudWatch + RDS health check | local (email from script) |
| 11:00 PM | `be5061d19a5a` | Full EC2 + Docker + CloudWatch + RDS health check | local (email from script) |

**Primary Runner:** `amlhive_prod_monitor.py` — standalone production monitor covering all 10 report sections (EC2, Docker, CloudWatch alarms+logs, RDS, Sentry, public endpoints). Formats plain-text report, sends via SMTP to `EMAIL_TO_AMLHIVE` recipients from .env. Exit 0 on all-healthy, 1 on incidents (email IS the alert mechanism — exit code 1 on issues is by design, not a bug). **Legacy reference:** `amlhive_aws_runner.py` imports `amlhive_aws_health.py` module (kept for dynamic instance discovery pattern).

**AWS resources monitored:** EC2 instances (amlhive-frontend + amlhive-prod via SSM), Docker containers + compose, CloudWatch alarms + log groups, RDS PostgreSQL.

**Credentials:** `AWS_ACCESS_KEY_ID_AMLHIVE` + `AWS_SECRET_ACCESS_KEY_AMLHIVE` from Windows `.env`. Loaded via Python line-by-line parsing (NOT bash `source` — the .env has special characters).

*Created Jul 6, 2026 — mirrors TapEase monitor runner pattern.*

## TapEase Fleet Monitoring + Daily Transactions

**Replaced bridge-based monitor on Jul 8, 2026.** Old `tapease_monitor_runner.py` (bridge-based, HTML errors since Jun 26) → new `tapease_prod_monitor.py` (direct AWS CLI + SSM). See `tapease-fleet-monitor` skill for full architecture, script docs, pitfalls, and known issues.

| Time (AEST) | Job ID | What It Does | Delivery |
|---|---|---|---|
| 5:00 AM | `dbd3cb1b5bd3` | Full EC2 + SSM process + nginx logs + alarms + Lambda + RDS | local (email from script) |
| 11:00 AM | `582bd225ddd1` | Full EC2 + SSM process + nginx logs + alarms + Lambda + RDS | local (email from script) |
| 5:00 PM | `1086e6405da1` | Full EC2 + SSM process + nginx logs + alarms + Lambda + RDS | local (email from script) |
| 9:30 PM | `114039a7ff9b` | **Daily Transaction Export** — SSM → psql → CSV → email | local (email from script) |
| 11:00 PM | `be81c61778a8` | Full EC2 + SSM process + nginx logs + alarms + Lambda + RDS | local (email from script) |

**Credentials:** `AWS_ACCESS_KEY_ID_TAPEASE` + `AWS_SECRET_ACCESS_KEY_TAPEASE` from Windows `.env`.

**Old bridge issues now resolved by direct monitor:**
- 🔴 TapEase Bridge HTML Error Pages → ✅ Replaced by direct AWS calls
- 🔴 Double Email From Same Cron Job → ✅ Single email send in `tapease_prod_monitor.py`

**Chain of duplication (historical, pre-Jul 8 fix):**
```
tapease_monitor_runner.py (cron)
  ├─ POST /tapease/monitor → bridge → powershell
  │   └─ lambda_monitor_unified.ps1 → unified_delivery.ps1
  │       └─ professional_email_unified.ps1 → 📧 EMAIL 1 (clean, HTML, Habibi logo)
  │          Script path: C:\Users\habib\.openclaw\workspace\scripts\delivery\professional_email_unified.ps1
  │          Agent logo: habibi_logo_email.jpg, branded gradient header, PDF+voice attachments
  │
  └─ send_email(summary) in tapease_monitor_runner.py → 📧 EMAIL 2 (raw, plain text)
     Uses Python smtplib → Purelymail SMTP → plain MIMEText, no HTML, no logo

  stdout → cron deliver: origin → 📱 Telegram delivery (separate, not email)
```

**Symptoms (historical):**
- Email 1: Professional HTML with Habibi's avatar/logo, gradient header, tables, PDF+voice attachments
- Email 2: Plain text, no formatting, no logo — stripped-down duplicate of same content
- Goes to overlapping recipients: `hhsiddiqui@gmail.com`, `habibshoaib841@gmail.com`, `admin@harishabib.au`

**Recommended fix (historical):** Remove the `send_email()` call from `tapease_monitor_runner.py` (line ~137). The PowerShell delivery pipeline (`professional_email_unified.ps1`) already handles email — and does it better (HTML, branded, with attachments). The Python `send_email()` is a redundant plain-text duplicate.

**Files to modify:**
```bash
# Edit tapease_monitor_runner.py (WSL path)
# Comment out or remove: sent = send_email(summary)
patch /home/habib/.hermes/scripts/tapease_monitor_runner.py \
  "sent = send_email(summary)" "# sent = send_email(summary)  # DISABLED: duplicates PowerShell email"
```

**Recipients per sender:**
| Sender | Recipients |
|---|---|
| `professional_email_unified.ps1` | `admin@harishabib.au`, `hhsiddiqui@gmail.com`, `habibshoaib841@gmail.com` |
| `tapease_monitor_runner.py` (Python) | `shoaib.habib@a2square.com.au`, `admin@harishabib.au`, `hhsiddiqui@gmail.com`, `habibshoaib841@gmail.com` |

**Related pipeline scripts:**
```
unified_git_sync.py       — pulls a2square + amlhive + operator repos (Thu+Mon 2AM)
unified_weekly_report.py  — Docker tests + report (Wed 2AM)
briefing_improver.py      — v2 morning briefing engine (5:20 AM, deliver:local)
hermes_update_check.sh    — `hermes update --check` (Mon+Fri 4AM) — git-aware, NOT pip
pluto_feedback_processor.py — Gumby→Pluto feedback loop (6:10 AM, no_agent)
skill_extractor.py        — daily skill proposals (11:00 AM, no_agent)
pluto_chamber_refresh.py  — feeds all sources to ChromaDB (5:25 AM, no_agent)
pluto_performance_tracker.py — daily perf snapshots → feeds Saturday review (11:30 PM, no_agent)
```
