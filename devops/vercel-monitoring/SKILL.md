---
name: vercel-monitoring
description: "⚠️ RETIRED Aug 2026 — Vercel no longer used; cron removed, script archived. Historical reference for the watchdog pattern (script-as-cron, stdout=delivery) and purelymail_sender.py email module. Do not debug/re-enable without user direction."
---

# Vercel Deployment Monitoring

## ⚠️ RETIRED 2026-08-08 — Do not debug or re-enable without explicit user direction

**Vercel is no longer used.** The user moved away from Vercel (and Fly.io);
"stop checking for the versal and stop checking for the fly.io — most of the
functionality is now sitting in AWS (Supabase Auth remains in design)."

- Cron job `745ec76c6bf9` (5:05 AM/PM) was **removed** 2026-08-08.
- `~/.hermes/scripts/vercel_monitor.py` was **archived** to
  `~/.hermes/scripts/retired/vercel_monitor.py`.
- `amlhive_prod_monitor.py` (the 4x-daily AWS monitor) has **no Vercel or
  Fly.io sections** — the legacy check functions and "9. LEGACY" report
  section were deleted. The old `pluto_fleet_monitor.py` was also archived to
  `retired/`.
- The content below is kept as **historical reference only** (the watchdog
  pattern it documents is still the pattern for script-as-cron jobs, and
  `purelymail_sender.py` is still the shared email module).

## When to Use (historical — only if Vercel is ever re-adopted)
- Setting up automated deployment health checks for Vercel projects
- Debugging deployment BLOCKED/ERROR states
- Generating deployment health reports for email delivery
- Adding a new Vercel project to monitor

## Architecture

```
┌─────────────────────────────────┐
│  Vercel REST API                │
│  api.vercel.com                 │
│  Auth: Bearer <token>           │
│  Team: ?teamId=<team_id>        │
└──────────┬──────────────────────┘
           │
           ▼
┌─────────────────────────────────┐
│  vercel_monitor.py              │
│  ~/.hermes/scripts/             │
│                                 │
│  1. GET /v9/projects/{id}       │ → Project health
│  2. GET /v6/deployments         │ → Recent deployments
│  3. GET /v2/deployments/{id}/   │ → Error events\n│     events                      │\n│  4. Generate report + save JSON │\n│  5. WATCHDOG CHECK:             │\n│     - No alerts → exit 0,       │\n│       empty stdout (SILENT)     │\n│     - Alerts → exit 0,          │\n│       print incident report     │\n│       + send email alert        │
│  6. Always save JSON report     │ → ~/.hermes/reviews/vercel/
└──────────┬──────────────────────┘
           │
           ▼
┌─────────────────────────────────┐
│  Twice-daily delivery via cron: │
│  5:05 AM + 5:05 PM AEST         │
│  Job ID: 745ec76c6bf9           │
│  no_agent: true (watchdog)      │
│  deliver: local                 │
│  — stdout = delivery payload    │
│    (incidents → non-empty       │
│     stdout → delivered; healthy  │
│     → empty stdout → silent)    │
│  + native SMTP on incidents     │
└─────────────────────────────────┘
```

**Key design decision (June 8, 2026):** Converted to **watchdog pattern** — silent when healthy, alerts only on incidents. The script exits 0 with empty stdout when no alerts are found (cron stays silent). Only prints to stdout + sends email when BLOCKED/ERROR deployments or idle conditions are detected. JSON reports are always saved to disk for historical records regardless of alert state.

**Previous design (June 6, 2026 — superseded):** ~~The script sent emails on EVERY run via `send_professional_email()`. Both recipients received a branded HTML report for every check — healthy or not.~~ This was noisy and has been replaced with incident-only alerting.

## Required Environment Variables

All stored in `/mnt/c/Users/habib/.hermes/.env`:

| Variable | Description |
|----------|-------------|
| `VERCEL_TOKEN_ID` | Vercel API token (Bearer auth) |
| `VERCEL_TEAM_URL` | Team slug (e.g., `amlhive`) |
| `VERCEL_TEAM_ID` | Team ID (e.g., `team_zHk...`) |
| `VERCEL_PROJECT_ID` | Project ID (e.g., `prj_8rY...`) |
| `VERCEL_LOGS_IN_BROSWER` | URL to Vercel logs dashboard |

**Email credentials** (Purelymail SMTP, also in `.env`):

| Variable | Description |
|----------|-------------|
| `EMAIL_FROM` | `operator@harishabib.au` |
| `SMTP_SERVER` | `smtp.purelymail.com` |
| `SMTP_PORT` | `587` |
| `SMTP_USERNAME` | `operator@harishabib.au` |
| `SMTP_PASSWORD` | Purelymail SMTP password |
| `EMAIL_TO_DEFAULT` | Default recipients (comma-separated) |
| `EMAIL_TO_TAPEASE` | Tapease recipient |
| `EMAIL_TO_PRIMARY` | Primary admin recipient |

The script's `load_env()` reads all variables from `.env` — no hardcoded credentials. Purelymail replaced Gmail SMTP on June 6, 2026.

## Vercel API Endpoints

### Project Health
```
GET https://api.vercel.com/v9/projects/{projectId}?teamId={teamId}
```
Returns: `{name, framework, updatedAt, ...}`

### Deployments List
```
GET https://api.vercel.com/v6/deployments?projectId={projectId}&teamId={teamId}&limit=10
```
Returns: `{deployments: [{uid, state, readyState, created, ...}]}`

Deployment states:
- `READY` — healthy, live
- `ERROR` — failed deployment
- `BLOCKED` — blocked (often transient, check events for cause)
- `BUILDING` — in progress
- `QUEUED` — waiting
- `CANCELED` — cancelled
- `INITIALIZING` — starting up

### Deployment Events
```
GET https://api.vercel.com/v2/deployments/{deploymentId}/events?teamId={teamId}&limit=20
```
Returns: Either `[{type, text, ...}]` (list) or `{events: [...]}` (dict). **The API response format changed — handle both list and dict.**

## Alert Rules

The monitor generates alerts for:
- **BLOCKED deployments** — flagged for attention, needs investigation
- **ERROR deployments** — critical, deployment failed

**Stable live apps do NOT trigger idle alerts.** The monitor previously flagged "No deployments in 12 hours" as an alert, but this produced false positives for stable apps like AML Hive (10/10 deployments READY, 0 errors, all healthy). As of June 13, 2026, idle checks are informational-only and do not generate alerts or email notifications. Real health = deployment state only.

### AML Hive Health Status (as of June 13, 2026)
```json
{
  "deployments_total": 10,
  "deployments_ready": 10,
  "deployments_error": 0,
  "alerts": [],
  "healthy": true
}
```

## Email Delivery

**Module:** `~/.hermes/scripts/purelymail_sender.py` — shared professional email sender (Python port of Gumby's `professional_email_unified.ps1`).

**Recipients (mandatory):** `hhsiddiqui@gmail.com` AND `shoaib@amlhive.com.au` — both receive incident alerts (emails only sent when alerts are detected).

**Format:** Professional HTML email with:
- Pluto agent branding (dark purple gradient header, "Pluto 🌑")
- Markdown → HTML conversion (pandoc with regex fallback)
- Styled tables, headers, blockquotes, code blocks
- Table-based layout for Outlook compatibility
- MSO conditionals for Office 365
- Plain-text alternative view for non-HTML clients
- Emoji → colored text labels for email client safety
- Branded footer: "Pluto Research & Monitoring — Haris Habib's Automation Platform"

**Usage from any script:**
```python
sys.path.insert(0, str(Path(__file__).parent))
from purelymail_sender import send_professional_email

send_professional_email(
    subject="[AML Hive] Vercel Monitor — Sat 06 Jun PM — ✅ HEALTHY",
    body_markdown=markdown_body,
    recipients=["hhsiddiqui@gmail.com", "shoaib@amlhive.com.au"],
    report_type="Vercel Deployment Monitor",
    time_of_day="PM Session",
    job_id="vercel-monitor",
    agent="pluto",
    body_file_name="vercel_monitor.py",
)
```

**Agent branding profiles available:** `pluto` (purple), `habibi` (blue), `brainy` (blue), `gumby` (green), `jonnyq` (amber).

**Credentials:** All from `/mnt/c/Users/habib/.hermes/.env` (EMAIL_FROM, SMTP_SERVER, SMTP_PORT, SMTP_USERNAME, SMTP_PASSWORD). The module's `_load_env()` reads them — no hardcoded credentials.

**Subject line format:** `[AML Hive] Vercel Monitor — {Date} {AM/PM} Session — ⚠️ ACTION REQUIRED`
Only sent on incidents — no healthy-status subject lines.

**Body structure (markdown fed to template — incident emails only):**
1. `## ⚠️ INCIDENT DETECTED` — project name, framework, team, dashboard URL
2. `## Recent Deployments` — markdown table with status icons
3. `## Alerts (N)` — bullet list of detected issues
4. `## Quick Stats` — counts + link to full Vercel logs

Emails are sent ONLY when alerts are detected — no emails on healthy checks (watchdog pattern). JSON reports are always saved to `~/.hermes/reviews/vercel/` for historical records.

## Cron Schedule

```
5 5,17 * * *  → 5:05 AM + 5:05 PM AEST daily
```
Cron ID: `745ec76c6bf9`
Mode: `no_agent: true` (watchdog — script IS the job)
Deliver: `local` (stdout is the delivery payload — empty stdout = silent, non-empty = delivered; exit 0 always — cron shows "ok")

The AM check (5:05 AM) and PM check (5:05 PM) run silently when healthy. Alerts are delivered via stdout + email only when BLOCKED/ERROR deployments or idle conditions are detected.

## Adding a New Project

1. Add Vercel env vars to `.env`:
   ```
   VERCEL_TOKEN_ID=<token>
   VERCEL_TEAM_URL=<team-slug>
   VERCEL_TEAM_ID=<team-id>
   VERCEL_PROJECT_ID=<project-id>
   VERCEL_LOGS_IN_BROSWER=<logs-url>
   ```

2. Create a project-specific monitor script (or extend `vercel_monitor.py`)
3. Add a cron job with appropriate schedule
4. Configure email recipients

## Pitfalls

- **BLOCKED deployments are verified before alerting (June 20, 2026).** Before flagging a BLOCKED deployment as real, the monitor now pings `GET /v1/deployments/{uid}?teamId={teamId}` to check if the deployment still exists. If the API returns 404 or `not_found`, the deployment is skipped — it's a garbage-collected artifact that the deployment list hasn't cleaned up yet. This eliminates the 4 stale BLOCKED deployments (dpl_7rXe, dpl_7kaK, dpl_GLpe, dpl_DSrt) that triggered false alerts every run for weeks.

- **Watchdog pattern: stdout = delivery; exit code is irrelevant.** The cron runs in `no_agent: true` mode — the script IS the job and its **stdout** is the delivery payload. The script always exits 0 (even on alerts) because non-zero exit codes are treated as cron execution errors. Empty stdout → silent cron (no delivery). Non-empty stdout → delivered to the target. Always print incident details before returning 0 — don't add debug prints on healthy runs. This is **NOT** an exit-code-based trigger; it's a stdout-only trigger.

- **Deployment events API returns either list or dict.** The `/v2/deployments/{id}/events` endpoint can return `[{...}]` (list) or `{events: [...]}` (dict) depending on the deployment state. Always check `isinstance(data, list)` before calling `.get('events')`. Bug discovered June 5, 2026 — crashed the first dry run on BLOCKED deployments.

- **Event field names vary.** Events may use `type` or `eventType`, `text` or `message` or `payload`. Use `.get()` with fallbacks: `ev.get('type', ev.get('eventType', '?'))`.

- **Deployment aliases may be empty.** The `alias` field on deployments can be `[]` or missing. Don't rely on it for display — use `uid` instead.

- **Token must have deployment read scope.** If the Vercel token lacks `Deployment - Read` scope, the API will return 401 or empty results.

- **Email credentials in .env, not himalaya config.** Purelymail SMTP uses `SMTP_USERNAME` + `SMTP_PASSWORD` from `/mnt/c/Users/habib/.hermes/.env`. The shared module `purelymail_sender.py` handles all formatting and SMTP. Formerly used Gmail SMTP with password extracted from himalaya config — deprecated June 6, 2026. 

- **Use the shared `purelymail_sender.py` module.** Don't inline email sending in new scripts. Import `send_professional_email()` from `~/.hermes/scripts/purelymail_sender.py`. It provides Gumby's battle-tested professional HTML template (pandoc markdown→HTML, table-based Outlook layout, agent branding, plain-text fallback).

## Reference Files
- `references/purelymail-module.md` — Purelymail professional email module documentation (API, features, migration, consumers)
- `references/vercel-email-format.md` — (Legacy) Plain-text email format — superseded by the HTML format in `purelymail_sender.py`
- `references/vercel-email-template.md` — (Legacy) HTML email template with dark theme — superseded
- `scripts/purelymail_sender.py` — Pointer to shared professional email module at `~/.hermes/scripts/purelymail_sender.py`
