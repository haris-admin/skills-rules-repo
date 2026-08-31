# Silent Ingestion-Parser Failure — Claude Daily Research (Aug 2026)

## Symptom

The Gmail Briefing Ingestor cron (`e5675447ed37`, daily 4:55 AM AEST) reported
`0 new emails processed` every single day for weeks — with NO error. Meanwhile
Claude Daily Research emails WERE arriving (forwarded from Haris to
macarthurgarments@gmail.com), confirmed by direct IMAP search: 6 emails in the
last 14 days, subject "Claude Daily Research".

Zero `claude-research-*.md` files were ever written. The parser was silently
eating the feed.

## Root cause — format drift

The email format changed (mid-June 2026) and `extract_claude_signals()` in
`gmail_ingestor_imaplib.py` matched nothing.

**Old format (worked):**
```
*1. Ramp Raises $750M Series F* — *FinTech Global, 5 Jun 2026*
```
`CLAUDE_FINDING_PATTERN` expected `\*(\d+)\.\s+(.+?)\*\s*—\s*\*(.+?)\*`.

**New format (Aug 2026):**
```
💳 Global Fintech News                        <- section header (emoji-prefixed)
SEC Proposes "Regulation Crypto Assets"       <- plain title line, NO asterisks
<https://www.google.com/url?q=...>            <- URL on its own line
                                               <- blank
The SEC unveiled a proposed rule...           <- description paragraph(s)
```

## The silent-failure mechanism

1. `extract_claude_signals()` returns `[]` for the new format
2. `if signals:` → False → file never written
3. Email msg_id appended to `processed_ids` state anyway
4. Cron reports "0 new emails processed" — looks like an empty inbox, not a bug

## Detection rule

If a feed cron reports `0 new items` for 2+ consecutive runs while the source
is confirmed still producing content (verify with a direct IMAP/API search),
**test the parser against a live item directly** — do not just re-run the cron.

```python
# fetch the latest Claude DR email, run gi.extract_claude_signals(body)
# — if 0 signals, the format changed AGAIN
```

## Fix (applied 20 Aug 2026)

1. `SECTION_PATTERN` emoji set broadened — added 💳🦞📬🛡️⚡🏦🏢📱💻🧠📰🗞️✅❌🎯🧭🌏♻️🔎🧩💼🏛️📉📌
   (was missing 💳 = "Global Fintech News", so section detection died too).
2. New patterns:
   - `CLAUDE_TITLE_PATTERN = re.compile(r'^[^*\s<].{8,160}$')`
   - `CLAUDE_URL_PATTERN = re.compile(r'^<https?://.+>$')`
3. `extract_claude_signals()` rewritten: **a finding title is a plain line
   whose next non-empty line is a `<url>`**. This kills header noise and
   description-splitting. Descriptions append after the URL until the next
   title/section.

## Verification

- 6 real emails → 142 signals extracted (was 0)
- 8 `claude-research-*.md` files written, all fed to chambers by the watcher
- 230 claude-tagged docs in ChromaDB (162 in regulatory-ai, 9 in fintech-aml)

## Backfill — the 2-day window trap

PASS 2 searches `SINCE <2 days ago>`. Older emails sitting in the inbox are
skipped forever once the window passes. After fixing the parser, run a one-off
backfill pass over ALL history (no SINCE clause) to write + feed missed files.
Verified: 9/9 emails recovered (3 June old-format + 6 Aug), 191 findings total.

**IMPORTANT:** state vs file check. An email can be in `processed_ids` with NO
file (the old broken parser marked it processed before the fix). Always check
for actual `claude-research-{id}-*.md` files, not just state membership.

## The lesson generalizes

Any parser that silently returns empty on format drift is a permanent data
loss bug. The cheap guard: a monitor that flags "N consecutive zero-extraction
runs while source has items". The skill-level rule: never trust cron
`last_status: ok` or "0 new items" as proof the pipeline is healthy — verify
one extraction end-to-end.
