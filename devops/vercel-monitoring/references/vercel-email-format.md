# Vercel Monitor Email Format (Updated June 6, 2026)

## Subject Line
```
[AML Hive] Vercel Monitor — {Weekday} {DD} {Mon} {AM|PM} Session — {STATUS}
```
Where STATUS is `✅ HEALTHY` (no alerts) or `⚠️ ACTION REQUIRED` (1+ alerts).

## Body Template

```
AML Hive — Vercel Deployment Monitor
{Weekday}, {DD} {Month} {YYYY} | {AM/PM} Session
═══════════════════════════════════════════════════════

PROJECT
  Name:       {project_name}
  Framework:  {framework}
  Team:       {team_slug}
  Dashboard:  https://vercel.com/{team_slug}

RECENT DEPLOYMENTS
  [{uid}] {icon} {state} — {timestamp}
  [{uid}] {icon} {state} — {timestamp}
  ...up to 10 entries

ALERTS ({count})
  • {alert_message}
  ...or "✅ No issues detected — all deployments healthy"

QUICK STATS
  Deployments shown:     {count}
  In last 12 hours:      {count}
  Alerts generated:      {count}

  Full Vercel logs → {logs_url}

═══════════════════════════════════════════════════════
AML Hive Monitoring — Pluto 🌑
Haris Habib's Automation Platform
Runs twice daily (5:05 AM/PM AEST)
```

## Design Decisions

- **Plain text, not HTML.** Plain text ensures deliverability and readability across all email clients (Outlook, Gmail, mobile). No dark theme, no CSS — just clean structure.
- **Emoji icons for scanability.** Each deployment state has an icon (✅ READY, 🔴 ERROR, 🚫 BLOCKED, etc.). Each alert gets a bullet.
- **Always sends, even when healthy.** Silence is ambiguity. Both healthy and alert-state emails go out so recipients know monitoring is active.
- **Both recipients in separate To fields.** `hhsiddiqui@gmail.com` and `shoaib@amlhive.com.au` each get separate emails (not CC). Gmail SMTP with separate `send_message()` calls per recipient.

## SMTP Configuration

```python
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

EMAIL_SENDER = 'macarthurgarments@gmail.com'
EMAIL_RECIPIENTS = ['hhsiddiqui@gmail.com', 'shoaib@amlhive.com.au']

# Password from himalaya config, NOT .env
# Extract: re.search(r'auth\.cmd\s*=\s*"echo\s+(\S+)"', config)

msg = MIMEMultipart()
msg['From'] = EMAIL_SENDER
msg['To'] = recipient
msg['Subject'] = subject
msg.attach(MIMEText(body, 'plain'))

with smtplib.SMTP('smtp.gmail.com', 587, timeout=15) as server:
    server.starttls()
    server.login(EMAIL_SENDER, password)
    server.send_message(msg)
```

## Verification

Test with: `python3 -u /home/habib/.hermes/scripts/vercel_monitor.py 2>&1`
Check stderr for `📧 Email sent → ...` lines.
