# Shared Alert Email Module — `alert_email.py`

## Location
`~/.hermes/scripts/alert_email.py`

## Purpose
Sends **URGENT RED bold HTML emails** via Purelymail SMTP when cron jobs detect escalation conditions. Used by hourly probes that need to alert immediately rather than wait for the next daily report.

## How to Use

```python
from alert_email import send_alert

send_alert(
    "Production Version Mismatch",           # Subject line (prefixed with 🚨 URGENT —)
    "VERSION_MISMATCH: local=0.5.29 != api=0.5.30",  # Plain text fallback
    "<p><b>ALERT DETAILS HERE</b></p>"        # HTML body (dark theme, red accents)
)
```

## Email Format
- **Theme:** Dark (#1a1a2e background, #2d2d44 card, #dc3545 red accents)
- **Header:** 🚨 URGENT — PLUTO ALERT (white bold, red background)
- **Body:** Red bold subject line, dark card with content
- **Footer:** Red divider, auto-generated timestamp
- **Recipients:** `hhsiddiqui@gmail.com`, `shoaib@amlhive.com.au`, `tech@amlhive.com.au`

## SMTP Config
- **Server:** smtp.purelymail.com:587 (STARTTLS)
- **From:** operator@harishabib.au
- **Password:** Reads `SMTP_PASSWORD` from `.env` (checks WSL + Windows paths)

## When to Use
Use for cron jobs where alert thresholds must trigger an immediate email:
- **Hourly version check** — API unreachable or version mismatch
- **Hourly attribution probe** — 3+ failures in 15 min or 100% failure in 24h
- **Fleet monitor P0 conditions** — if you want escalation outside the regular 4x daily email

Do NOT use for routine reports — those go through the normal email pipeline.
