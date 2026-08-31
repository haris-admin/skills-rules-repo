# macarthurgarments@gmail.com — Gmail Access via Himalaya

## Credentials

Located in `/mnt/c/Users/habib/.hermes/.env`:
- `GOOGLE_GMAIL_APP_PASSWORD_MACARTHUR` — Gmail app password for IMAP/SMTP
- `GOOGLE_API_STUDIO_KEY_MACARTHUR` — Google AI Studio API key
- `GOOGLE_API_KEY_2_MACARTHUR` — Duplicate (same value as above)

## Himalaya Configuration

Config at `~/.config/himalaya/config.toml`. Account name: `macarthur`.

```toml
[accounts.macarthur]
email = "macarthurgarments@gmail.com"
display-name = "MacArthur Garments"
default = true

backend.type = "imap"
backend.host = "imap.gmail.com"
backend.port = 993
backend.encryption.type = "tls"
backend.login = "macarthurgarments@gmail.com"
backend.auth.type = "password"
backend.auth.cmd = "echo <app_password>"

message.send.backend.type = "smtp"
message.send.backend.host = "smtp.gmail.com"
message.send.backend.port = 587
message.send.backend.encryption.type = "start-tls"
message.send.backend.login = "macarthurgarments@gmail.com"
message.send.backend.auth.type = "password"
message.send.backend.auth.cmd = "echo <app_password>"

folder.aliases.inbox = "INBOX"
folder.aliases.sent = "[Gmail]/Sent Mail"
folder.aliases.drafts = "[Gmail]/Drafts"
folder.aliases.trash = "[Gmail]/Trash"
```

## Critical: Folder Aliases Syntax (Himalaya v1.2.0)

v1.2.0 changed the alias syntax. The OLD format (`[accounts.NAME.folder.alias]` sub-section, singular `alias`) is silently ignored. Must use `folder.aliases.X` (plural, dotted keys directly under `[accounts.NAME]`). Failure mode: save-to-Sent fails silently after SMTP succeeds, and `himalaya message send` exits non-zero. Retries produce duplicate emails.

## Common Operations

```bash
# List folders
himalaya folder list

# List recent inbox (10 messages)
himalaya envelope list --page-size 10

# Read a message
himalaya message read <id>

# Search
himalaya envelope list from "Perplexity Tasks" subject briefing

# Send (non-interactive — pipe via stdin)
cat << 'EOF' | himalaya template send
From: macarthurgarments@gmail.com
To: recipient@example.com
Subject: Subject line

Body text here.
EOF
```

## Current Inbox Pattern (June 3, 2026)

- Daily Perplexity Tasks briefings arrive: "AU fintech, payments and AML briefing", "AU fintech, AI and regulation briefing"
- Google Payments, Airtable, Amazon Seller Central also present
- Perplexity briefings are the highest-value signal source — ideal for auto-ingest into MemPalace research pipeline
