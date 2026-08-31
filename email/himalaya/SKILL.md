---
name: himalaya
description: "Himalaya CLI: IMAP/SMTP email from terminal."
version: 1.1.0
author: community
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [Email, IMAP, SMTP, CLI, Communication]
    homepage: https://github.com/pimalaya/himalaya
prerequisites:
  commands: [himalaya]
---

# Himalaya Email CLI

Himalaya is a CLI email client that lets you manage emails from the terminal using IMAP, SMTP, Notmuch, or Sendmail backends.

## References

- `references/configuration.md` (config file setup + IMAP/SMTP authentication)
- `references/message-composition.md` (MML syntax for composing emails)

## Prerequisites

1. Himalaya CLI installed (`himalaya --version` to verify)
2. A configuration file at `~/.config/himalaya/config.toml`
3. IMAP/SMTP credentials configured (password stored securely)

### Installation

```bash
# Pre-built binary (Linux/macOS — recommended)
curl -sSL https://raw.githubusercontent.com/pimalaya/himalaya/master/install.sh | PREFIX=~/.local sh

# macOS via Homebrew
brew install himalaya

# Or via cargo (any platform with Rust)
cargo install himalaya --locked
```

## Configuration Setup

Run the interactive wizard to set up an account:

```bash
himalaya account configure
```

Or create `~/.config/himalaya/config.toml` manually:

```toml
[accounts.personal]
email = "you@example.com"
display-name = "Your Name"
default = true

backend.type = "imap"
backend.host = "imap.example.com"
backend.port = 993
backend.encryption.type = "tls"
backend.login = "you@example.com"
backend.auth.type = "password"
backend.auth.cmd = "pass show email/imap"  # or use keyring

message.send.backend.type = "smtp"
message.send.backend.host = "smtp.example.com"
message.send.backend.port = 587
message.send.backend.encryption.type = "start-tls"
message.send.backend.login = "you@example.com"
message.send.backend.auth.type = "password"
message.send.backend.auth.cmd = "pass show email/smtp"

# Folder aliases (himalaya v1.2.0+ syntax). Required whenever the
# server's folder names don't match himalaya's canonical names
# (inbox/sent/drafts/trash). Gmail is the common case — see
# `references/configuration.md` for the `[Gmail]/Sent Mail` mapping.
folder.aliases.inbox = "INBOX"
folder.aliases.sent = "Sent"
folder.aliases.drafts = "Drafts"
folder.aliases.trash = "Trash"
```

> **Heads up on the alias syntax.** Pre-v1.2.0 docs used a
> `[accounts.NAME.folder.alias]` sub-section (singular `alias`).
> v1.2.0 silently ignores that form — TOML parses fine, but the
> alias resolver never reads it, so every lookup falls through to
> the canonical name. On Gmail this means save-to-Sent fails *after*
> SMTP delivery succeeds, and `himalaya message send` exits non-zero.
> Any caller (agent, script, user) that retries on that exit code
> will re-run the entire send — including SMTP — producing duplicate
> emails to recipients. Always use `folder.aliases.X` (plural, dotted
> keys, directly under `[accounts.NAME]`).

## Hermes Integration Notes

- **Reading, listing, searching, moving, deleting** all work directly through the terminal tool
- **Composing/replying/forwarding** — piped input (`cat << EOF | himalaya template send`) is recommended for reliability. Interactive `$EDITOR` mode works with `pty=true` + background + process tool, but requires knowing the editor and its commands
- Use `--output json` for structured output that's easier to parse programmatically
- The `himalaya account configure` wizard requires interactive input — use PTY mode: `terminal(command="himalaya account configure", pty=true)`

## Common Operations

### List Folders

```bash
himalaya folder list
```

### List Emails

List emails in INBOX (default):

```bash
himalaya envelope list
```

List emails in a specific folder:

```bash
himalaya envelope list --folder "Sent"
```

List with pagination:

```bash
himalaya envelope list --page 1 --page-size 20
```

### Search Emails

```bash
himalaya envelope list from john@example.com subject meeting
```

### Read an Email

Read email by ID (shows plain text):

```bash
himalaya message read 42
```

Export raw MIME:

```bash
himalaya message export 42 --full
```

### Reply to an Email

To reply non-interactively from Hermes, read the original message, compose a reply, and pipe it:

```bash
# Get the reply template, edit it, and send
himalaya template reply 42 | sed 's/^$/\nYour reply text here\n/' | himalaya template send
```

Or build the reply manually:

```bash
cat << 'EOF' | himalaya template send
From: you@example.com
To: sender@example.com
Subject: Re: Original Subject
In-Reply-To: <original-message-id>

Your reply here.
EOF
```

Reply-all (interactive — needs $EDITOR, use template approach above instead):

```bash
himalaya message reply 42 --all
```

### Forward an Email

```bash
# Get forward template and pipe with modifications
himalaya template forward 42 | sed 's/^To:.*/To: newrecipient@example.com/' | himalaya template send
```

### Write a New Email

**Non-interactive (use this from Hermes)** — pipe the message via stdin:

```bash
cat << 'EOF' | himalaya template send
From: you@example.com
To: recipient@example.com
Subject: Test Message

Hello from Himalaya!
EOF
```

Or with headers flag:

```bash
himalaya message write -H "To:recipient@example.com" -H "Subject:Test" "Message body here"
```

Note: `himalaya message write` without piped input opens `$EDITOR`. This works with `pty=true` + background mode, but piping is simpler and more reliable.

### Move/Copy Emails

Move to folder:

```bash
himalaya message move 42 "Archive"
```

Copy to folder:

```bash
himalaya message copy 42 "Important"
```

### Delete an Email

```bash
himalaya message delete 42
```

### Manage Flags

Add flag:

```bash
himalaya flag add 42 --flag seen
```

Remove flag:

```bash
himalaya flag remove 42 --flag seen
```

## Multiple Accounts

List accounts:

```bash
himalaya account list
```

Use a specific account:

```bash
himalaya --account work envelope list
```

## Attachments

Save attachments from a message:

```bash
himalaya attachment download 42
```

Save to specific directory:

```bash
himalaya attachment download 42 --dir ~/Downloads
```

## Output Formats

Most commands support `--output` for structured output:

```bash
himalaya envelope list --output json
himalaya envelope list --output plain
```

## Debugging

Enable debug logging:

```bash
RUST_LOG=debug himalaya envelope list
```

Full trace with backtrace:

```bash
RUST_LOG=trace RUST_BACKTRACE=1 himalaya envelope list
```

## Tips

- Use `himalaya --help` or `himalaya <command> --help` for detailed usage.
- Message IDs are relative to the current folder; re-list after folder changes.
- For composing rich emails with attachments, use MML syntax (see `references/message-composition.md`).
- Store passwords securely using `pass`, system keyring, or a command that outputs the password.
- **Heredoc pipes time out in terminal(); use file-based pipes instead.** `cat << 'EOF' | himalaya template send` inside `terminal()` may time out with BLOCKED status (June 4, 2026). The reliable pattern: (1) `write_file` the email body to a temp file, (2) `terminal("cat /tmp/email-body.txt | himalaya template send")`. This works because the file read completes instantly, unlike heredocs which can hang waiting for stdin EOF in the terminal sandbox.
- **Never use `execute_code` to modify email files for re-sending.** `read_file` from `hermes_tools` prepends line numbers (`1|From:...`) into the content. If this corrupted content is written back to a file and piped to himalaya, it returns "cannot parse MML message: empty body." Always use the native `write_file` tool directly to create email bodies — never `execute_code` with string replacement on existing email files (June 4, 2026).

## Auth Command Failure & SMTP Fallback (CRITICAL — Updated June 2026)

**Problem:** `auth.cmd = "echo <password>"` in `~/.config/himalaya/config.toml` fails in the Hermes terminal sandbox with:

```
Error: cannot build IMAP client
  → cannot get imap password from global keyring
  → cannot get secret from command
  → No child process (os error 10)
```

The Hermes terminal sandbox prevents child process spawning for auth commands. The `echo` command works in a real shell but the sandbox blocks it. This breaks ALL himalaya commands (send, list, read) because even SMTP-only operations try to build an IMAP client first (to save to Sent folder).

**Production SMTP: Purelymail (June 2026)**
All outgoing email now uses Purelymail SMTP via `operator@harishabib.au`. Credentials are in `/mnt/c/Users/habib/.hermes/.env`:
```
EMAIL_FROM=operator@harishabib.au
SMTP_SERVER=smtp.purelymail.com
SMTP_PORT=587
SMTP_USERNAME=operator@harishabib.au
SMTP_PASSWORD=...
```

**Fallback: Python smtplib via execute_code** (works for any SMTP provider)

```python
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_email(env, to_addrs, subject, body):
    """Send via Purelymail (or any SMTP). env = dict with SMTP_* keys."""
    msg = MIMEMultipart()
    msg['From'] = env.get('EMAIL_FROM', 'operator@harishabib.au')
    msg['To'] = ', '.join(to_addrs) if isinstance(to_addrs, list) else to_addrs
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))
    
    with smtplib.SMTP(env['SMTP_SERVER'], int(env.get('SMTP_PORT', '587')), timeout=15) as server:
        server.starttls()
        server.login(env['SMTP_USERNAME'], env['SMTP_PASSWORD'])
        server.send_message(msg)

# Load env from .env file
def load_env(path='/mnt/c/Users/habib/.hermes/.env'):
    tokens = {}
    with open(path) as f:
        for line in f:
            line = line.strip()
            if '=' in line and not line.startswith('#'):
                k, v = line.split('=', 1)
                tokens[k.strip()] = v.strip().strip('"').strip("'")
    return tokens

env = load_env()
send_email(env, ['hhsiddiqui@gmail.com'], 'Subject Here', body)
```

This uses Python's stdlib `smtplib` — no dependencies, not rate-limited. Works with Purelymail, Gmail, or any SMTP provider. Use when himalaya is blocked for sending.

**Recipient env vars in .env:**
- `EMAIL_TO_DEFAULT` = `admin@harishabib.au,hhsiddiqui@gmail.com,habibshoaib841@gmail.com`
- `EMAIL_TO_TAPEASE` = `shoaib.habib@a2square.com.au`
- `EMAIL_TO_PRIMARY` = `admin@harishabib.au`

**Himalaya remains useful for IMAP reads** (listing/searching Gmail). The auth.cmd failure is sandbox-specific and may work in different execution contexts. Use himalaya for reading, Python smtplib + Purelymail for sending.

**Professional HTML emails:** Use the shared `purelymail_sender.py` module (`~/.hermes/scripts/purelymail_sender.py`) instead of raw smtplib. It provides Gumby's battle-tested professional HTML template (ported from `professional_email_unified.ps1`): agent branding, pandoc markdown→HTML with regex fallback, table-based Outlook layout, MSO conditionals, plain-text alternative, and emoji-safe color labels. Import `send_professional_email()` and call with subject, body_markdown, recipients, report_type, time_of_day, job_id, and agent profile.
