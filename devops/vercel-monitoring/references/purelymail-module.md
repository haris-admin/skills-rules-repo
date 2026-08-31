# Purelymail Professional Email Module

**Canonical path:** `~/.hermes/scripts/purelymail_sender.py`
**Source:** Python port of Gumby's `professional_email_unified.ps1`

## Overview

Shared email sending module for all Pluto scripts. Replaces ad-hoc smtplib with Gumby's battle-tested professional HTML template.

## API

```python
from purelymail_sender import send_professional_email

send_professional_email(
    subject="[Project] Report Title — Status",
    body_markdown="## Section\nContent with **markdown**...",
    recipients=["user@example.com", "admin@example.com"],
    report_type="Deployment Monitor",    # Header title
    time_of_day="AM Session",            # Header subtitle
    job_id="vercel-monitor",             # For logging/tracking
    agent="pluto",                       # Branding: pluto, habibi, brainy, gumby, jonnyq
    body_file_name="script_name.py",     # Source file for meta box
)
```

## Features

- **Agent branding** — Colored headers per agent (Pluto: dark purple #1a1a3e)
- **Markdown → HTML** — Pandoc with regex fallback (tables, headers, code blocks, blockquotes)
- **Outlook compatible** — Table-based layout, MSO conditionals
- **Multi-part MIME** — HTML body + plain text alternative
- **Emoji safety** — ✅→OK, ⚠️→WARN, 🔴→!! (Outlook-safe colored labels)
- **Purelymail SMTP** — operator@harishabib.au via STARTTLS port 587

## Credentials

All from `/mnt/c/Users/habib/.hermes/.env`:
- EMAIL_FROM=operator@harishabib.au
- SMTP_SERVER=smtp.purelymail.com
- SMTP_PORT=587
- SMTP_USERNAME=operator@harishabib.au
- SMTP_PASSWORD=...

## Migration (June 6, 2026)

| Before | After |
|--------|-------|
| Gmail SMTP (macarthurgarments@gmail.com) | Purelymail SMTP (operator@harishabib.au) |
| Password from himalaya config | Password from .env |
| Plain text MIMEText per script | Shared HTML module with branding |
| Ad-hoc formatting per script | Consistent Gumby professional template |

## Consumers

- `vercel_monitor.py` — AML Hive deployment health (hhsiddiqui@gmail.com + shoaib@amlhive.com.au)
