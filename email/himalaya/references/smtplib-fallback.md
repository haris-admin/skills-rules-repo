# Python smtplib Fallback — When Himalaya Auth Fails

## Why

Himalaya's `auth.cmd = "echo <password>"` fails in the Hermes terminal sandbox with:
```
Error: cannot build IMAP client → cannot get secret from command → No child process (os error 10)
```

The sandbox prevents child process spawning for auth commands. This breaks ALL himalaya commands.

## Fix: Python stdlib smtplib

```python
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_email(to_addr, subject, body):
    msg = MIMEMultipart()
    msg['From'] = 'macarthurgarments@gmail.com'
    msg['To'] = to_addr
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))
    
    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        server.login('macarthurgarments@gmail.com', 'mlcbaeezdhquyewk')
        server.send_message(msg)

# Send to both recipients
for to in ['hhsiddiqui@gmail.com', 'admin@harishabib.au']:
    send_email(to, 'Morning Briefing - 2026-06-05', body)
```

## Email format: Unified Briefing style

Haris prefers Gumby's clean, sectioned format. See `~/.hermes/templates/email-briefing-template.txt`.

Template variables: `{date_long}`, `{weekday}`, `{datetime}`, `{source_file}`, `{top_3_signals}`, `{area_status}`, `{gn_au_status}`, `{gmail_status}`, `{podcast_status}`, `{web_status}`, `{linkedin_posts}`, `{blog_ideas}`, `{one_action}`, `{priority_queue}`

## Credential Location

- Gmail app password: In `~/.config/himalaya/config.toml` as `auth.cmd = "echo mlcbaeezdhquyewk"`
- Also in Windows `.env` as `GOOGLE_GMAIL_APP_PASSWORD_MACARTHUR`
- SMTP: `smtp.gmail.com:587` with STARTTLS

## Proven Success

- June 4, 2026: 2/2 emails sent (hhsiddiqui + admin)
- June 5, 2026: 4/4 emails sent (2 original + 2 reformatted)
