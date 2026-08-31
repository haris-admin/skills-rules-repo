---
name: professional-html-email-pipeline
description: Purelymail HTML report email, rendering + SMTP pitfalls.
---

# Professional HTML Email Pipeline (Purelymail)

## When to Use

- Sending any professional HTML report email via Purelymail SMTP (fleet monitor, website monitor, Vercel monitor, daily business reports, monthly strategy review)
- Debugging emails where **Day headers / nested bullets render flat**, bold text shows as literal `**text**`, or the email body is one unreadable wall
- Debugging SMTP 535 "Authentication Failed" where the .env password looks correct
- Adding a PDF/CSV attachment to a professional HTML email

## Canonical Sender

`~/.hermes/scripts/purelymail_sender.py` — shared by all monitors.

```python
from purelymail_sender import send_professional_email
send_professional_email(
    subject="AMLHive Monthly Strategy Review — 2026-07 (PDF attached)",
    body_markdown=md,
    recipients=["hhsiddiqui@gmail.com", "shoaib@amlhive.com.au"],
    report_type="Monthly Strategy Review",
    time_of_day="2026-07",
    job_id="monthly-strategy",
    agent="pluto",
    body_file_name="pluto_monthly_strategy_job.py",
)
```

- Reads SMTP config from the Windows `.env` at `/mnt/c/Users/habib/.hermes/.env` (`SMTP_SERVER`, `SMTP_PORT`, `SMTP_USERNAME`, `SMTP_PASSWORD`, `EMAIL_FROM`) — works from WSL python too since the path is absolute.
- Builds both HTML and plain-text versions (plain first = client fallback).
- Uses pandoc for markdown→HTML when installed; **regex fallback otherwise** (see rendering fix below).

## ⚠️ markdown→HTML list rendering (Aug 2026 fix)

The regex fallback in `_markdown_to_html()` historically had three defects that made nested sections (After-Action "Day 1:" + indented actions, opportunity portfolio) render flat:

1. `t = line.strip()` stripped leading whitespace → nested bullets flattened to one level
2. `<li>` items were emitted bare, never wrapped in `<ul>` → rendered as flat paragraphs
3. Inline formatting (`**bold**` → `<b>`) ran AFTER list handling → `**Day 1:**` stayed literal

**Fixed with:** `list_stack` / `list_depths` depth tracking (indented bullets → proper nested `<ul>`), inline formatting applied inside the list branch, and open lists closed on headings / blank lines / end-of-body.

**Verify after any renderer change:**
```python
from purelymail_sender import _markdown_to_html
html = _markdown_to_html(md)
import re
assert len(re.findall(r"<ul", html)) == len(re.findall(r"</ul>", html))
assert len(re.findall(r"<li", html)) == len(re.findall(r"</li>", html))
assert len(re.findall(r"<b>", html)) == len(re.findall(r"</b>", html))
```
Balanced tag counts + plain-text version keeping indentation = correct render.

## ⚠️ SMTP env-var shadowing (root cause of "provider authentication error" / 535)

A **stale Windows user env var** (`HKCU\Environment`, e.g. `SMTP_PASSWORD`) shadows the .env value for ANY script run under Windows `py.exe` — the process inherits the registry var and it overrides the correct .env value.

- **Symptom:** `smtplib.SMTPAuthenticationError: (535, b'Authentication Failed')` while the .env password is correct. Direct login test with the .env value succeeds; the job fails.
- **Diagnose:** `cmd.exe /c "reg query HKCU\Environment /v SMTP_PASSWORD"` → shows a stale value. Compare `config.get('SMTP_PASSWORD')[-4:]` vs the .env value.
- **Fix (two layers):**
  1. Delete the registry key: `cmd.exe /c "reg delete HKCU\Environment /v SMTP_PASSWORD /f"` (note: the value persists in already-running process trees — relaunch via `powershell.exe -NoProfile -Command "Remove-Item Env:\SMTP_PASSWORD"` or a fresh shell)
  2. **Make the script treat .env as authoritative** — `executor_config()` / `_load_env()` must NOT let `os.environ` override the .env value for SMTP keys:
     ```python
     # GOOD: .env wins
     config = load_dotenv(Path.home() / ".hermes" / ".env")
     # do NOT: config.update({k: v for k, v in os.environ.items() if v})
     ```
- **Check other scripts:** this same stale var broke the 9:15 PM business report and the monthly strategy job email — audit any script that reads SMTP creds under Windows Python.

## Attachments (PDF / CSV)

`send_professional_email` does NOT attach files. For an email with an attachment, build the MIME yourself using the same `.env` creds and the same HTML/plain builders:

```python
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from purelymail_sender import _load_env, _build_html_email, _build_plain_text

html = _build_html_email(subject, body_md, "pluto", "Monthly Strategy Review", period, "monthly-strategy", "pluto_monthly_strategy_job.py")
plain = _build_plain_text(subject, body_md, "Monthly Strategy Review", period, "monthly-strategy")

for recipient in recipients:
    msg = MIMEMultipart("alternative")
    msg["From"], msg["To"], msg["Subject"] = email_from, recipient, subject
    msg.attach(MIMEText(plain, "plain", "utf-8"))
    msg.attach(MIMEText(html, "html", "utf-8"))
    pdf = MIMEApplication(PDF_PATH.read_bytes(), _subtype="pdf")
    pdf.add_header("Content-Disposition", "attachment", filename=PDF_PATH.name)
    msg.attach(pdf)
    with smtplib.SMTP(server, port, timeout=30) as s:
        s.starttls(); s.login(user, pw); s.send_message(msg)
```

Script example: `~/.hermes/scripts/send_strategy_professional_email.py` (monthly strategy report + PDF).

## Windows Python pitfalls

- `subprocess.run(["codex", ...])` fails with `WinError 2` for `.CMD` shims — resolve with `shutil.which("codex")` and invoke the full path (see `pluto-monthly-strategy` skill for the Codex+Luna routing).
- `strftime('%-d')` is Linux-only — Windows Python raises `ValueError: Invalid format string`. Use `strftime('%d').lstrip('0')` for cross-platform day-of-month.
- When re-rendering an existing result JSON (no re-model call), import the job module and call `markdown_report(result)` / `write_outputs` directly — do not re-run the whole job; and use `/mnt/c/...` paths from WSL python, `C:\...` only under Windows `py.exe`.

## Related

- `pluto-communication-protocol` (Telegram message format — NOT for email)
- `pluto-monthly-strategy` → `references/source-collection.md` (executor + Codex/Luna model routing)
- `references/reportlab-pdf-export.md` — professional PDF export from result JSON (reportlab)
- `references/monthly-strategy-after-action-format.md` — After-Action heading format for the report's "Next 7 days" block + markdown_report renderer pitfalls (append-vs-extend, measurement/growth dict rendering)
