# Alert Email Module (`alert_email.py`)

## Purpose
Sends urgent RED HTML email alerts for fleet monitor hourly probes. Used by:
- `hourly_version_check.py` — stale build / auth failure alerts
- `hourly_attribution_probe.py` — probe failure threshold alerts

## Location
`~/.hermes/scripts/alert_email.py`

## Function
```python
from alert_email import send_alert

send_alert(
    subject="🚨 URGENT — Short Alert Title",  # Email subject line
    summary="One-line summary for cron output",  # Printed to stdout
    html_body="<p>Rich HTML body...</p>"   # Full HTML email body
)
```

## Email Format
- Dark-themed RED HTML template
- `🚨 URGENT — PLUTO ALERT` header (red background, white bold text)
- ⛔ Subject line in red, bold
- Styled table for version/status comparisons
- RED divider line
- Plain text fallback in body

## Recipients
Read from `.env` — `EMAIL_TO_AMLHIVE` variable.
Currently: hhsiddiqui@gmail.com, shoaib@amlhive.com.au, tech@amlhive.com.au

## SMTP
Purelymail via `smtp.purelymail.com:465` (SSL).
Credentials read from `.env` at runtime (never hardcoded).

## When to Use
- Auth failures (expired PAT, bad credentials)
- Stale build detected (API version behind repo version)
- Endpoint unreachable
- Probe threshold breached (3+ failures in 15 min, 100% failure in 24h)
