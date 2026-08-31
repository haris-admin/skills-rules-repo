# IMAPlib Gmail Extraction Pattern (June 2026)

This is the working pattern for reading Gmail from within the Hermes sandbox. Himalaya's `auth.cmd` approach is broken — use `imaplib` directly.

## Core Pattern

```python
import imaplib
import email
from email.header import decode_header
from datetime import datetime, timedelta

APP_PASSWORD = "mlcbaeezdhquyewk"
USERNAME = "macarthurgarments@gmail.com"

# Connect
mail = imaplib.IMAP4_SSL("imap.gmail.com", 993)
mail.login(USERNAME, APP_PASSWORD)
mail.select("INBOX")

# Search (Gmail IMAP search syntax)
since = (datetime.now() - timedelta(days=2)).strftime("%d-%b-%Y")
status, messages = mail.search(None, f'(FROM "team@mail.perplexity.ai" SINCE {since})')

# Fetch
for msg_id in messages[0].split():
    status, data = mail.fetch(msg_id, "(RFC822)")
    msg = email.message_from_bytes(data[0][1])
    # ... extract body, process ...

mail.logout()
```

## Body Extraction

```python
def extract_body(msg):
    body_text = ""
    if msg.is_multipart():
        for part in msg.walk():
            ct = part.get_content_type()
            if ct == "text/plain":
                payload = part.get_payload(decode=True)
                charset = part.get_content_charset() or "utf-8"
                body_text = payload.decode(charset, errors="replace")
                break
            elif ct == "text/html" and not body_text:
                payload = part.get_payload(decode=True)
                charset = part.get_content_charset() or "utf-8"
                html = payload.decode(charset, errors="replace")
                body_text = re.sub(r'<[^>]+>', ' ', html)
                body_text = re.sub(r'\s+', ' ', body_text).strip()
    else:
        payload = msg.get_payload(decode=True)
        body_text = payload.decode(
            msg.get_content_charset() or "utf-8", errors="replace"
        )
    return body_text
```

## Key Quirks

- **Gmail IMAP `SINCE` format:** `DD-Mon-YYYY` (e.g., `04-Jun-2026`). Month is 3-letter English abbreviation.
- **Message IDs are bytes:** Gmail returns them as `b'1234'`. Decode with `.decode()` before storing in JSON state.
- **Subject headers need decode_header:** They may be encoded MIME words. Use `email.header.decode_header()`.
- **Prefer text/plain over text/html:** Multipart emails often have both. Plain text is easier to parse.
- **App password location:** The Gmail app password is currently `mlcbaeezdhquyewk` for `macarthurgarments@gmail.com`. If regenerated, update the script AND `/mnt/c/Users/habib/.hermes/.env`.
