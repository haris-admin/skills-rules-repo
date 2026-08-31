# Alert Email Pattern — Shared Utility

## Overview
The `~/.hermes/scripts/alert_email.py` module provides a reusable `send_alert()` function for sending **urgent HTML emails** with a dark-themed RED template to `hhsiddiqui@gmail.com` (To), BCC to `shoaib@amlhive.com.au` and `tech@amlhive.com.au`.

Used by both hourly probes (version check + attribution probe). Any future monitoring script can import and use it.

## Usage

```python
from alert_email import send_alert

success = send_alert(
    subject="Short Alert Title",          # Appears in email subject: 🚨 URGENT — {subject}
    body_text="Plain text fallback",       # Used in multipart/alternative text/plain part
    body_html_extra="<p><b>HTML content</b></p>"  # Optional — inserted into main body of HTML template
)
# Returns True if sent, False if SMTP unavailable
```

## Alert Conditions That Trigger Email

The alert is intended for **threshold breaches** — not every probe failure. Example thresholds:
- 3+ failures in 15 minutes (attribution probe)
- 100% failure across 5+ probes in 24h (attribution peak)
- Version mismatch between local `.version` and production API (stale-build regression)
- API endpoint unreachable

## Email Template

Dark theme (`#1a1a2e` background, `#2d2d44` card), red header banner (`#dc3545`):
```
┌─────────────────────────────────────┐
│  🚨 URGENT — PLUTO ALERT           │  ← Red background, white bold
│  timestamp                          │
├─────────────────────────────────────┤
│  ⛔ Subject line                     │  ← Red (#ff6b6b), bold
│                                     │
│  [body_html_extra content]          │  ← Inserted here
│  ─────────────────────────────────── │
│  plain text fallback                │
├─────────────────────────────────────┤
│  Pluto Automated Alert              │  ← Footer
└─────────────────────────────────────┘
```

## SMTP Configuration

- **Server:** smtp.purelymail.com:587 (STARTTLS)
- **From:** operator@harishabib.au
- **Password:** `SMTP_PASSWORD` from `.hermes/.env` (auto-detected: Windows path first, then WSL paths)
- **Recipients:** hhsiddiqui@gmail.com (To) + BCC to shoaib@amlhive.com.au, tech@amlhive.com.au

## Pitfalls

- Always call `send_alert()` BEFORE `sys.exit(1)` — if exit happens before the send, the alert is lost
- The function returns `False` if SMTP credentials aren't found — don't rely on the alert as sole notification mechanism (cron output also delivers to origin)
- SMTP may be rate-limited for bursts. The function catches and logs send failures silently — don't retry in a tight loop
- The HTML template uses inline styles (no CSS classes) — email clients strip `<style>` blocks
