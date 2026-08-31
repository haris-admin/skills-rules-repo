# Pluto Cron Job Registry — AMLHive Operations

All times in AEST (Australia/Sydney). All cron jobs created/updated July 2026.

## Daily (Every Day)

| Time | Job ID | Name | Type | Script |
|------|--------|------|------|--------|
| `30 2 * * *` (02:30) | `0dbba3db3116` | ★ Daily Repo Sync — Pull Latest Dev Branch | no_agent | `daily_repo_sync.py` |
| `0 3 * * *` (03:00) | `044c0bc41e31` | ★ AMLHive Daily Test Suite | no_agent | `amlhive_daily_test_runner.py` |

**Repo Sync Purpose:** Pulls the latest `.version` from the `Dev` branch of `amlhive-tech/amlhive1` into the local repo at `/mnt/c/Code/github/almhive-tech/amlhive1`. Feeds the hourly version check with up-to-date comparison data.

**Repo Sync Pattern:** `git fetch origin && git reset --hard origin/dev` on the local Windows repo clone.

**Test Suite Purpose:** Runs the full AMLHive test stack — backend `pytest`, frontend `jest`, frontend `playwright test`. Reports results summary. Exit code 0 = all pass, 1 = any failures.

## Hourly (Every Day)

| Time | Job ID | Name | Type | Script |
|------|--------|------|------|--------|
| `0 * * * *` (:00) | `4689311b6ad0` | ★ Hourly Production Version Check | no_agent | `hourly_version_check.py` |
| `30 * * * *` (:30) | `b705c3ee3882` | ★ Hourly Marketing-Attribution Probe | no_agent | `hourly_attribution_probe.py` |

### Version Check Pattern
- Fetches `https://api.amlhive.com.au/version`
- Compares to local `.version` file (reads GitHub PAT from Windows `.env`, falls back to local repo)
- **Exits FAIL + sends 🚨 URGENT email** on: API behind repo (stale build)
- **No alert** on: API ahead of repo (repo `.version` is lagging — no stale-build risk)
- **Tolerance:** mismatch within ~10 min of known deploy is timing false-positive

### Attribution Probe Pattern
- Tests 3 endpoints: homepage (+10KB cookie), /signup, /api/health
- State tracked in `.attribution_probe/probe_state.json`
- **Exits FAIL + sends 🚨 URGENT email** when: 3+ failures in 15min OR 100% failure in 24h

## Weekdays

| Time | Job ID | Name | Type | 
|------|--------|------|------|
| `0 9 * * 1-5` | `756e4e66c320` | ★ Pluto Daily Discovery Health | LLM agent + skill |

## Weekly

| Day | Time | Job ID | Name |
|-----|------|--------|------|
| Tue | `30 10 * * 2` | `291c2320c81b` | ★ Weekly Search & Content Review |
| Wed | `30 10 * * 3` | `f1b73c7cd48d` | ★ Weekly AI-Answer Review *(fortnightly full)* |
| Thu | `0 11 * * 4` | `7059cc6796d6` | ★ Weekly Metadata/Blog/Social Audit |
| Fri | `0 15 * * 5` | `f7e6cb145925` | ★ Weekly Evidence Summary |
| Mon | `30 2 * * 1` (02:30) | `0320d41d6d71` | ★ A2Square Weekly Test Suite — `a2square_weekly_test_runner.py` |

**A2Square Weekly Test Suite:** Runs pytest on `portal_backend_lambda_eventbridge` and `tapease_portal_fastapi_a2square`, plus Playwright e2e on `tapease_frontend_nextjs_prod`. Auto-pulls latest code. Uses `GITHUB_PAT_CLASSIC_A2SQUARE_AGENT` from `.env`.

## Monthly

| Time | Job ID | Name |
|------|--------|------|
| `0 11 1-7 * 1` (1st Mon) | `50eea054f911` | ★ Monthly Strategy Review |

## Existing Supporting Pipeline (pre-July 2026)

| Time | Name | Script |
|------|------|--------|
| 4:55 AM | Gmail Briefing Ingestor | `gmail_ingestor_imaplib.py` |
| 5:00 AM | AmLHive AWS Fleet Monitor | `amlhive_prod_monitor.py` |
| 5:05 AM | Pluto Morning Research | LLM agent |
| 5:07 AM | Pluto Competitor Intel | `competitor_intel.py` |
| 6:00 AM | Pluto Morning Briefing (Mon-Fri) | LLM agent |
| Every 5m | Mempalace Watcher | `mempalace_watcher.py` |
| 9:15 PM | AML Hive Daily Business Report | `amlhive_daily_report.py` |
| 9:30 PM | Tapease Daily Transactions | `tapease_daily_transactions.py` |
| 11:00 AM/5:00 PM | TapEase Fleet Monitor | `tapease_prod_monitor.py` |
| 5:00 AM/11 AM/5 PM/11 PM | AmLHive Fleet Monitor | `amlhive_prod_monitor.py` |

## Credential Loading Pattern (All Scripts)

All no_agent scripts follow this pattern to load credentials:

```python
# Read from .env instead of hardcoding
pw = ""
for p in ["/mnt/c/Users/habib/.hermes/.env", str(Path.home() / ".hermes" / ".env")]:
    try:
        with open(p) as f:
            for line in f:
                if "SECRET_NAME" in line and "=" in line and not line.startswith("#"):
                    pw = line.split("=", 1)[1].strip()
                    break
    except: pass
```

**Why:** Hardcoded passwords expire/rotate. Reading from `.env` dynamically avoids the 13-day outage pattern seen with the Gmail ingestor.

**Paths checked (in order):**
1. `/mnt/c/Users/habib/.hermes/.env` (Windows .hermes)
2. `~/.hermes/.env` (WSL .hermes)
3. `~/.openclaw/.env` (WSL OpenClaw)

**Key credential names:**
- `AWS_ACCESS_KEY_ID_AMLHIVE` / `AWS_SECRET_ACCESS_KEY_AMLHIVE` — AMLHive AWS account
- `GITHUB_PAT_CLASSIC_AMLHIVE_AGENT` — GitHub PAT for `amlhive-tech/*` raw content fetches
- `SMTP_PASSWORD` — Purelymail SMTP for email delivery
- `GOOGLE_GMAIL_APP_PASSWORD_MACARTHUR` — Gmail ingestor app password

**Alert email shared module:** When a script needs to escalate, import `alert_email.send_alert()`:
```python
from alert_email import send_alert
send_alert(
    "URGENT — Alert Subject",
    "Plain text description",
    "<p><b>HTML detail</b> with formatting</p>"
)
```
This sends a dark-themed 🚨 URGENT RED HTML email to hhsiddiqui@gmail.com + shoaib@amlhive.com.au + tech@amlhive.com.au via Purelymail SMTP.

## Delivery Targets
- `origin` = deliver back to the conversation where the job was created
- `local` = save only, no delivery
- All ★-prefixed jobs deliver to origin so Haris sees the output
