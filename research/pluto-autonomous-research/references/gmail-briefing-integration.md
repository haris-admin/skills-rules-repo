# Gmail Briefing Integration — Pluto Research Pipeline

**Updated:** June 7, 2026
**Account:** macarthurgarments@gmail.com
**Access method:** Python `imaplib` (himalaya deprecated — auth.cmd fails in sandbox)

## Credentials

- **Email:** macarthurgarments@gmail.com
- **App Password:** `mlcbaeezdhquyewk` (hardcoded in ingestor script)
- **Ingestor script:** `~/.hermes/scripts/gmail_ingestor_imaplib.py`

## Briefing Sources

| Sender/Pattern | Type | Frequency | Parser |
|--------|------|-----------|--------|
| team@mail.perplexity.ai | Perplexity Tasks | Daily | `extract_signals()` — bullet points |
| SUBJECT "Claude Daily Research" | Claude Daily Research (forwarded by Haris) | Daily | `extract_claude_signals()` — section-based |
| macarthurgarments@genspark.email | Genspark intel | Weekly | `extract_signals()` — bullet points |

## Ingestion Pipeline

### Script
`~/.hermes/scripts/gmail_ingestor_imaplib.py` — uses Python `imaplib` (NO himalaya dependency)

### Why imaplib, not himalaya
Himalaya's `auth.cmd = "echo password"` fails in Hermes sandbox with "No child process (os error 10)". Python's `imaplib` connects directly — no subprocess, no sandbox issue.

### Cron
- **Job ID:** `e5675447ed37`
- **Schedule:** `55 4 * * *` AEST (4:55 AM)
- **Mode:** `no_agent: true`, `deliver: local`
- **Script:** `gmail_ingestor_imaplib.py`

### Flow
1. Two-pass IMAP search:
   - **PASS 1:** Sender-based — `(FROM "team@mail.perplexity.ai" SINCE ...)`
   - **PASS 2:** Subject-based — `(SUBJECT "Claude Daily Research" SINCE ...)`
2. Extract signals with appropriate parser
3. Write `.md` to `~/.hermes/mempalace-inputs/`
4. Track processed IDs in `.gmail_ingestor_state.json`
5. MemPalace watcher cron (`5678a363ce3b`, every 5 min) auto-feeds to ChromaDB

## Claude Daily Research

See `pluto-mempalace-bridge` → `references/claude-daily-research-ingestion.md` for:
- Section-based parsing format
- Chamber routing table
- Watcher format requirements (`##` headers, not `###`)
- User preferences (online/free events priority)
