# Professional HTML Email for Cron Alert Scripts

Reusable pattern for sending structured HTML emails from cron scripts that detect conditions in database queries (negative balances, threshold breaches, anomalies).

Used by: Tapease Payout Sweep (`tapease_payout_email.py`), AML Hive Daily Report (`amlhive_daily_report.py`)

## Architecture

```
Python script (cron job)
  │
  ├── 1. Fetch credentials (AWS Secrets Manager / .env)
  ├── 2. Query database (via SSM send-command → psql on EC2)
  ├── 3. Group/aggregate results
  ├── 4. Build HTML + plain text email
  └── 5. Send via SMTP (Purelymail :587 / STARTTLS)
```

## SMTP Pattern (Purelymail)

```python
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Read password from .env
smtp_pw = ""
for c in ["/mnt/c/Users/habib/.hermes/.env", str(Path.home()/".hermes"/".env")]:
    try:
        with open(c) as f:
            for line in f:
                if "SMTP_PASSWORD" in line and "=" in line and not line.startswith("#"):
                    smtp_pw = line.split("=",1)[1].strip()
                    break
    except: pass

msg = MIMEMultipart("alternative")
msg["Subject"] = f"🔵 Subject Line — {DATE}"
msg["From"] = "operator@harishabib.au"
msg["To"] = "hhsiddiqui@gmail.com"
msg["Bcc"] = "shoaib@amlhive.com.au, tech@amlhive.com.au"
msg.attach(MIMEText(plain_text, "plain"))
msg.attach(MIMEText(html, "html"))

with smtplib.SMTP("smtp.purelymail.com", 587) as s:
    s.starttls()
    s.login("operator@harishabib.au", smtp_pw)
    s.sendmail("operator@harishabib.au",
               ["hhsiddiqui@gmail.com", "shoaib@amlhive.com.au", "tech@amlhive.com.au"],
               msg.as_string())
```

## Reuse the fleet's branded HTML builders (`purelymail_sender.py`)

Instead of hand-rolling HTML, reuse the same builder the 5 PM Vercel Monitor uses
(identical branded header/format across the fleet). It lives at
`~/.hermes/scripts/purelymail_sender.py` (WSL side — importable from WSL
python3, NOT Windows `py.exe`):

```python
import sys
sys.path.insert(0, str(Path.home() / ".hermes" / "scripts"))
from purelymail_sender import _load_env, _build_html_email, _build_plain_text

env = _load_env()   # reads /mnt/c/Users/habib/.hermes/.env (SMTP creds)
html_body  = _build_html_email(subject, body_markdown, "pluto", "Report Title",
                               "2026-07", "job-id", "source_file.py")
plain_body = _build_plain_text(subject, body_markdown, "Report Title", "2026-07", "job-id")
```

`_load_env()` already points at the Windows `.env` (`/mnt/c/Users/habib/.hermes/.env`)
so it works unchanged from WSL.

## PDF attachment on the professional email

User-requested pattern (Aug 2026): same branded HTML body + a PDF attached to the
same MIME message. Use `MIMEMultipart("alternative")` with plain first, HTML
second, then append the PDF part:

```python
from email.mime.application import MIMEApplication

msg = MIMEMultipart("alternative")
msg["From"] = email_from
msg["To"] = recipient
msg["Subject"] = subject
msg.attach(MIMEText(plain_body, "plain", "utf-8"))
msg.attach(MIMEText(html_body, "html", "utf-8"))

pdf = MIMEApplication(PDF_PATH.read_bytes(), _subtype="pdf")
pdf.add_header("Content-Disposition", "attachment",
               filename="AMLHive-Monthly-Strategy-Review-2026-07.pdf")
msg.attach(pdf)

with smtplib.SMTP(smtp_server, smtp_port, timeout=30) as server:
    server.starttls()
    server.login(smtp_user, smtp_pass)
    server.send_message(msg)
```

## Execution-side pitfalls (WSL vs Windows)

1. **Run sender scripts with WSL python3**, not Windows `py.exe` — `purelymail_sender.py`
   and its builders only exist in `~/.hermes/scripts` (WSL). Windows `py.exe` cannot
   import it (`ModuleNotFoundError`).
2. **File paths must be `/mnt/c/...` when reading report outputs from WSL** —
   `C:\Users\...` paths raise `FileNotFoundError` under WSL python3. Keep the
   "canonical" Windows path only in the subject/strings, use `/mnt/c/` for `Path()`.
3. **Do not set `Subject` twice** — `EmailMessage.__setitem__` raises
   `ValueError: There may be at most 1 Subject headers` if you build via the
   executor's `build_email_message()` (which sets Subject) and then set it again.
   Reuse the builder's message and only add attachments, or build a fresh message.

## HTML Template Structure

```html
<!DOCTYPE html>
<html>
<body style="margin:0;padding:0;background:#f4f4f4;font-family:-apple-system,...;">
  <table width="100%"><tr><td style="padding:20px 0;">
    <table width="600" style="margin:0 auto;background:#fff;border-radius:8px;box-shadow:0 1px 3px rgba(0,0,0,0.1);">

      <!-- HEADER: Blue gradient -->
      <tr><td style="padding:24px 30px;background:linear-gradient(135deg,#1a237e,#283593);">
        <h1 style="margin:0;color:#fff;font-size:20px;font-weight:600;">🔵 Title</h1>
        <p style="margin:4px 0 0;color:#9fa8da;font-size:13px;">Subtitle</p>
      </td></tr>

      <!-- DATE BAR: Light blue -->
      <tr><td style="padding:12px 30px;background:#e8eaf6;font-size:13px;color:#283593;">
        📅 {date_string}
      </td></tr>

      <!-- ALERT BANNER: Orange (issues) or Green (all clear) -->
      <tr><td style="padding:20px 30px;">
        <div style="background:#fff3e0;border-left:4px solid #ff9800;padding:12px 16px;border-radius:4px;">
          <strong style="color:#e65100;">⚠️ Warning message</strong>
          <span style="display:block;margin-top:4px;font-size:13px;color:#555;">Details line</span>
        </div>
        <!-- For all-clear: background:#e8f5e9; border-left:4px solid #4caf50; -->

        <!-- DATA SECTIONS -->
        <div style="margin-bottom:24px;">
          <h3 style="color:#1a237e;font-size:15px;">📋 Section Title</h3>
          <table style="width:100%;border-collapse:collapse;font-size:13px;">
            <thead>
              <tr style="background:#f5f5f5;">
                <th style="padding:8px 10px;text-align:left;border-bottom:2px solid #ddd;">Col 1</th>
                <th style="padding:8px 10px;text-align:right;border-bottom:2px solid #ddd;">Col 2</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td style="padding:6px 10px;border-bottom:1px solid #eee;font-family:monospace;">value</td>
                <td style="padding:6px 10px;border-bottom:1px solid #eee;text-align:right;font-family:monospace;color:#d32f2f;font-weight:bold;">-$X.XX</td>
              </tr>
            </tbody>
          </table>
        </div>
      </td></tr>

      <!-- FOOTER -->
      <tr><td style="padding:16px 30px;background:#fafafa;border-top:1px solid #eee;font-size:11px;color:#888;text-align:center;">
        Automated report · {date_string}
      </td></tr>
    </table>
  </td></tr></table>
</body>
</html>
```

## Color Palette

| Element | Color | Usage |
|---------|-------|-------|
| Header gradient | `#1a237e` → `#283593` | Title bar |
| Header subtitle | `#9fa8da` | Muted subtitle |
| Date bar | `#e8eaf6` bg, `#283593` text | Date strip |
| Warning banner | `#fff3e0` bg, `#ff9800` left border, `#e65100` text | Alert on negative/failure |
| Success banner | `#e8f5e9` bg, `#4caf50` left border, `#2e7d32` text | All-clear message |
| Table header | `#f5f5f5` bg, `#ddd` border | Column headers |
| Negative values | `#d32f2f` bold | Negative amounts in red |
| Section title | `#1a237e` | Group headers |
| Footer | `#fafafa` bg, `#888` text | Bottom bar |

## Pitfalls

1. **Exit code 0 always** — When the purpose of the script IS the email delivery, always exit 0 even when data shows issues. Exit code 1 marks the cron as "failed" even though the email was sent successfully.
2. **Plain text fallback** — Always include a `MIMEText(plain, "plain")` part before the HTML part. Some email clients show plain text by default.
3. **Monospace for amounts** — Use `font-family:monospace` on numeric columns to align decimal points.
4. **Cent conversion** — Database stores amounts in cents (integers). Divide by 100 for dollar display. Round to 2 decimal places.
5. **SSM polling** — `send-command` + `get-command-invocation` polling takes 3-8s. Set total script timeout > 30s.
6. **SMTP password** — Read from `SMTP_PASSWORD` in `.env`. The same password works for all `operator@harishabib.au` emails.
7. **`executor_config()` env shadowing** — if a script merges `os.environ` over `.env`, a stale Windows user env var (e.g. `SMTP_PASSWORD` in `HKCU\Environment`) silently overrides the good `.env` value → `535 Authentication Failed`. Treat `.env` as authoritative for credential-shaped keys (`SMTP_PASSWORD, SMTP_USERNAME, SMTP_SERVER, SMTP_PORT, EMAIL_FROM`). See `monthly-strategy-executor-config.md`.
