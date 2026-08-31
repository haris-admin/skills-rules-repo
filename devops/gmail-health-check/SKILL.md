---
name: gmail-health-check
description: Use when diagnosing Gmail IMAP/credential failures.
---

# Gmail Health Check

Cron `4161036f7818` (daily 4:50 AM AEST, no_agent) → `~/.hermes/scripts/gmail_health_check.py`.

**Purpose:** Pre-flight IMAP login test that runs 5 min BEFORE the Gmail
Briefing Ingestor (`e5675447ed37`, 4:55 AM). Catches credential expiry within
24 hours instead of leaving the ingestor dark for 7 days.

**Exit codes:**
- `0` — IMAP login succeeded
- `1` — IMAP login failed → writes a P0 alert to `mempalace-inputs/gmail-health-alert-*.md`
- `2` — config missing (`GMAIL_USER` / `GMAIL_APP_PASSWORD` not set)

**Credentials** load from WSL `~/.hermes/.env` OR Windows
`/mnt/c/Users/habib/.hermes/.env` (check both).

**State:** `~/.hermes/research_outputs/.gmail_health_state.json`.

## Pitfalls
- W31 (Aug 1–7) this was CRITICAL for 7+ days: `GMAIL_USER/GMAIL_APP_PASSWORD
  not set`. Root cause was the .env key missing entirely, not a bad password —
  check for the keys' existence first, not just the IMAP error.
- Resolved as of W32 — if it regresses to exit 2, check which .env the keys
  are missing from (WSL vs Windows), not the password.
