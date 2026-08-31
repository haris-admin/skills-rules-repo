---
name: pluto-gmail-signal-ingestion
description: Pluto's Gmail signal ingestion pipeline — pulls Perplexity Tasks and other briefing emails via Python imaplib, extracts signals, and feeds to the mempalace staging inbox. Use when setting up, debugging, or manually running the Gmail ingestion pipeline.
allowed-tools: [terminal, read_file, write_file, execute_code]
---

# Pluto Gmail Signal Ingestion

## When to Use
- Running the Gmail ingestor manually
- Debugging why briefings weren't pulled
- Adding a new briefing source (new sender)
- Checking what was ingested from email today

## Authority Framework (Signal Triage Tiers)

Use this framework to classify every email-derived signal before deciding whether
Pluto handles it silently, prepares it for review, or escalates it. It applies to
Perplexity Tasks, Claude Daily Research, Genspark intel, and competitor scans.

### ACT

Handle routine signals silently when the correct treatment is obvious and no
public, financial, legal, or relationship-sensitive action is implied:

- Archive-worthy newsletters.
- Perplexity task confirmations.
- Routine Genspark intel — write it to the mempalace staging inbox for normal
  ingestion.
- Competitor scan matches that are informational only.

### DRAFT-FOR-REVIEW

Prepare the relevant signal or proposed response for owner review, and do not
publish or send anything, when it is tone-sensitive or implies a public action:

- Any signal whose wording, framing, or relationship nuance matters.
- Claude Daily Research that suggests content or a public-facing post.
- Startup intel containing strong claims that may need validation or careful
  positioning.

### ALWAYS-ESCALATE

Never handle these signals alone:

- Financial commitments, pricing, contracts, invoices, refunds, or other spend.
- Legal or compliance matters, including AML/UBO-related signals.
- Messages from VIP contacts: `shoaib@amlhive.com.au`, `tech@amlhive.com.au`, or
  `hhsiddiqui+tech`.
- Anything suggesting a product outage or client impact.

Escalation means sending a RED HTML email via Purelymail to
`hhsiddiqui+shoaib+tech`, per the `pluto-amlhive-operating-contract`. Include the
source signal, relevant evidence, urgency or impact, and the specific decision
needed.

When uncertain, default to draft-for-review.

**Trust is earned, not assumed.** Expand silent handling only as repeated,
correct triage establishes confidence.

## Architecture (June 2026 — imaplib rewrite)

**Cron:** `e5675447ed37`, schedule `55 4 * * *` AEST (4:55 AM), `no_agent: true`, `deliver: local`
**Script:** `~/.hermes/scripts/gmail_ingestor_imaplib.py` (Python `imaplib` — no himalaya dependency)\n**Credentials:** `GOOGLE_GMAIL_APP_PASSWORD_MACARTHUR` in `.hermes/.env` (reads dynamically at runtime — no hardcoded password since Jul 18, 2026 fix)\n**State:** `~/.hermes/research_outputs/.gmail_ingestor_state.json`\n**Account:** `macarthurgarments@gmail.com` (Gmail app password in `.env`)
**Output:** Structured `.md` files → `~/.hermes/mempalace-inputs/gmail-briefing-*.md`

**Why imaplib, not himalaya:** Himalaya's `auth.cmd = "echo password"` pattern fails consistently in the Hermes terminal sandbox with `No child process (os error 10)`. The sandbox cannot spawn child processes for auth commands. Python's stdlib `imaplib` connects directly — no subprocess, no sandbox issue. Verified working June 7, 2026.

## Manual Run
```bash
python3 -u ~/.hermes/scripts/gmail_ingestor_imaplib.py
```

## Briefing Sources
| Sender/Pattern | Type | Frequency | Parser |
|--------|------|-----------|--------|
| `team@mail.perplexity.ai` | Perplexity Tasks | Daily | `extract_signals()` — bullet points |
| SUBJECT "Claude Daily Research" | Claude Daily Research (forwarded by Haris) | Daily | `extract_claude_signals()` — section-based numbered items |
| `macarthurgarments@genspark.email` | Genspark intel, Gumby GC research, **Genspark Claw startup intel** | Weekly / on-demand | `extract_signals()` — bullet points; `format_startup_intel_markdown()` for Claw reports |
| ANY email with competitor keywords | Competitor signal scan | Daily (PASS 3) | `scan_for_competitors()` — name matching against 79-company database |

**Gumby GC (Genspark OpenClaw):** A fleet peer agent (June 2026) that Pluto directs for lightweight research. Gumby GC sends results to `macarthurgarments@gmail.com` from `macarthurgarments@genspark.email`. The ingestor's IMAP search `FROM "genspark"` is a substring match that catches all Genspark-sourced emails. Results land in `mempalace-inputs/` for auto-ingestion to ChromaDB chambers. See `fleet-intelligence` skill for the full Gumby GC mission briefing pattern.

**Genspark Claw startup intel (NEW July 3, 2026):** Genspark Claw delivers startup intelligence reports (3 high-conviction opportunities per week) via email from `macarthurgarments@genspark.email` with subjects matching "Startup Intelligence", "startup-intel", "claw", or containing competitor keywords. These are formatted with `format_startup_intel_markdown()` which preserves numbered opportunity sections, financial figures, and tagged metadata. Each opportunity becomes a `## Finding` entry in the mempalace output. See `fleet-intelligence` skill for the Claw mission pattern.

**Claude Daily Research** is detected by subject pattern, not sender (Haris forwards from `hhsiddiqui@gmail.com`). It uses a dedicated parser (`extract_claude_signals()`) that handles:
- `\r\n` line ending normalization
- Multi-line title-source joining (email wrapping)
- Section-based routing to source-topic chambers (`events-sydney`, `accelerators`, `cloud-frontier`, `startup-funding`, `coding-agents`, `ai-frontier`)
- Two format variants: main content (`*N. Title* — *Source*`) and events/accelerators (`*N. Name — Details*`)

See `pluto-mempalace-bridge` skill → `references/claude-daily-research-ingestion.md` for the full ingestion pattern.

## How It Works (imaplib Pipeline — Enhanced July 3, 2026)

### PASS 1: Sender-based briefings (Perplexity, Genspark)
1. **Connect** — `imaplib.IMAP4_SSL("imap.gmail.com", 993)` with app password
2. **Search** — `mail.search(None, f'(FROM "{sender}" SINCE {since_date})')` for each briefing sender
3. **Deduplicate** — skip msg_ids already in `processed_ids` from state file
4. **Extract body** — walks multipart MIME, prefers `text/plain`, falls back to stripped `text/html`
5. **Extract signals** — bullet points (`*`, `-`, `•`) with >30 char minimum; falls back to paragraphs >50 chars
6. **Write .md** — structured markdown with subject, source, date, tags, and findings
7. **Update state** — track `processed_ids`, `total_processed`, `last_run`

### PASS 1b: Genspark startup intel (genspark.email)
Detects Genspark Claw reports by subject keywords ("startup intelligence", "claw", "🦞", competitor terms). Uses `format_startup_intel_markdown()` to preserve numbered opportunity sections with financial figures, tagged metadata, and CRM integration findings. Falls back to standard `extract_signals()` for non-Claw Genspark emails. Both paths write to `mempalace-inputs/`.

### PASS 2: Subject-based Claude Daily Research
Same as before — detects by subject pattern, uses `extract_claude_signals()` section parser, writes to `mempalace-inputs/claude-research-*.md`.

### PASS 3: Competitor subject scan (NEW July 3, 2026)
Scans ALL inbox emails for subject keywords: "competitor", "market intel", "competitive", "funding", "acquisition", "series a", "aml", "compliance", "kyc", "fintech". For each match, checks body against the 79-company competitor database (loaded from `~/.hermes/data/competitors.json`). Matches write to `mempalace-inputs/competitor-email-*.md` with `Competitors detected: X, Y, Z` metadata.

### PASS 4: Competitor signal feed (NEW July 3, 2026)
Across ALL passes (1, 1b, 2, 3), every email body is scanned for competitor names using `scan_for_competitors()`. Detected competitor mentions are aggregated and written to `~/.hermes/competitor_intel_inputs/email_signals_{YYYYMMDD}.json`. This file is consumed by the `competitor_intel.py` cron (5:07 AM AEST) which cross-references email signals against daily research findings.

**What happens next:** The mempalace watcher cron (`5678a363ce3b`, every 5 min) auto-detects new `.md` files and feeds them to ChromaDB chambers via `mempalace_watcher.py` → `pluto_mempalace_feeder.py`. The competitor signal feed is separate — it goes to the competitor intel pipeline, not mempalace.

## State Tracking

`.gmail_ingestor_state.json`:
```json
{
  "last_run": "2026-06-07T09:23:00+10:00",
  "processed_ids": ["3529", "3531", "3532", ...],
  "total_processed": 24
}
```

Prevents re-processing the same email twice. Msg IDs are stored as strings (Gmail IMAP returns them as bytes, decoded to strings for JSON compatibility).

## Signal Extraction

The script extracts:
- Bullet-point findings from Perplexity Tasks emails (lines starting with `*`, `-`, or `•`)
- Falls back to first 8 substantive paragraphs (>50 chars) if no bullets found
- Key topics and tags from subject line patterns
- Source attribution from email `From` header

Output goes to mempalace staging inbox — the watcher cron auto-feeds to ChromaDB.

## End-to-End Verification

After the cron fires at 4:55 AM, verify with:
```bash
# 1. Check ingestor ran
python3 ~/.hermes/scripts/gmail_ingestor_imaplib.py
# Should print "Gmail Ingestor: N new briefings processed"

# 2. Wait 5 min for watcher, or run manually
python3 ~/.hermes/scripts/mempalace_watcher.py

# 3. Verify chamber counts increased
python3 ~/.hermes/scripts/pluto_mempalace_feeder.py --status | python3 -c \
  "import sys,json; d=json.load(sys.stdin); print(f'Total: {d[\"total_documents\"]}')"
```

## Cron Configuration

```
job_id: e5675447ed37
name: Gmail Briefing Ingestor (4:55 AM AEST)
schedule: 55 4 * * *
no_agent: true
script: gmail_ingestor_imaplib.py
deliver: local
```

**Why `no_agent: true`:** No LLM reasoning needed — it's a deterministic script. Runs faster, cheaper, and avoids sandbox auth issues. Output is silent (`deliver: local`) — files go to filesystem, watcher handles the rest.

## Deprecated: Himalaya Approach

The old `gmail_briefing_ingestor.py` used himalaya CLI (`himalaya envelope list --output json`) to pull emails. This is **broken in the Hermes sandbox** because:
- `auth.cmd = "echo mlcbaeezdhquyewk"` in himalaya config requires spawning a child process
- The sandbox returns `No child process (os error 10)` for all `auth.cmd` invocations
- The cron reported `last_status: ok` but produced ZERO results for weeks (confirmed June 7, 2026)

The old script (`gmail_briefing_ingestor.py`) is retained for reference but should NOT be used. Use `gmail_ingestor_imaplib.py` instead.

**Note:** himalaya v1.2.0 uses `himalaya envelope list` (not `himalaya list`), and `-o json` (not `--output json`). But even with correct commands, `auth.cmd` still fails in the sandbox — the command syntax is irrelevant.

## Known Bug — `mempalace_inputs` Variable Name (Fixed June 16, 2026)

The June 12 patch added filesystem duplicate-check logic (`existing = list(Path(mempalace_inputs).glob(...))`) but the variable `INBOX_DIR` was renamed in the patch but the old name `mempalace_inputs` was never defined. This caused **every email fetch to silently fail** with `Error processing {sender}: name 'mempalace_inputs' is not defined` — the exception was caught, logged to stderr, and the script reported 0 new briefings.

**Impact:** 4 days of missed emails (June 12–16, 2026). 3 Perplexity briefings (June 13–15) sat in the inbox unprocessed.

**Fix:** Changed both occurrences to `INBOX_DIR.glob(...)` (line 192 and 237). Verified: ingestor now processes 4 new briefings correctly (3 real + 1 sign-in email filtered as noise).

**Prevention:** Add a test that runs the ingestor against a known email count after any edit to the dedup logic.

## Pitfalls

- **Himalaya auth.cmd is permanently broken in the Hermes sandbox** — confirmed June 7, 2026. Do NOT attempt to use himalaya for email reading OR sending from within Hermes terminal sessions or cron jobs. Use Python `imaplib` for reading and `smtplib` for sending.
- **Credentials MUST be read from `.env`, not hardcoded (FIXED July 18, 2026).** The script previously had the app password hardcoded at line 25. When Google rotates/expires the password (as happened Jul 12–15, 2026), hardcoding means updating the script itself — fragile and easy to miss. **Fixed:** The script now reads `GOOGLE_GMAIL_APP_PASSWORD_MACARTHUR` from `.env` at runtime (checks Windows WSL path first, then Linux paths). To update the password: (1) Go to https://myaccount.google.com/apppasswords, (2) Generate new password, (3) Update `.hermes/.env` (NOT the script), (4) Test with `python3 gmail_ingestor_imaplib.py`.
- **Duplicate prevention by msg_id** — if the state file is corrupted or lost, all emails from the last 2 days are re-processed. This is harmless (embeddings cluster duplicates) but wastes tokens.
- **Briefing format varies by sender** — Perplexity Tasks uses bullet points. Genspark format differs. New senders may need format-specific parsing added to the script.
- **⚠️ Watcher format incompatibility — gmail briefings never reach ChromaDB (June 30, 2026):** The mempalace watcher (`mempalace_watcher.py`) that is supposed to auto-feed gmail briefings to ChromaDB SKIPS them all. **Root cause:** The ingestor writes files with plain `## Finding` headers, but the watcher parser requires `## Finding Title` headers followed by `Source:` / `Type:` / `Confidence:` structured fields. Every gmail briefing file returns `\"status\": \"skipped\", \"error\": \"No findings parsed\"` from the watcher. As of June 30, 2026, 47 gmail briefing files (May 24–June 30) accumulated unprocessed in `mempalace-inputs/` with 0 files in `processed/`. **The \"How It Works\" section above is INCORRECT for gmail briefings** — the watcher does NOT feed them to ChromaDB. **Fix options:** (1) Update this ingestor to add `Source:` / `Type:` / `Confidence:` fields to each finding in the output `.md` files, (2) Update `mempalace_watcher.py` to accept plain `## Finding` headers as valid findings. Option (1) is preferred because it doesn't require changes to the shared watcher.
- **Perplexity findings are truncated to one line (June 9, 2026).** The ingestor's `extract_signals()` regex captures only the first line of each bullet point. Perplexity emails have multi-line findings (e.g., \\\"Regulation deadlines loom: ASIC's 2026 digital-asset licensing cutoff and AUSTRAC Tranche 2 AML/CTF reforms are turning...\\\") where the critical detail is in the second+ lines. The ingested `.md` files at `mempalace-inputs/gmail-briefing-*.md` contain only the truncated first line. To get full findings, the regex needs to handle continuation lines (non-bullet text after a bullet). Workaround until fixed: read the original email body from the ingestor's raw output, or check `.gmail_ingestor_state.json` for the last processed ID and run a manual fetch with `--verbose` flag.
- **Gmail IMAP `SINCE` uses server time** — emails may appear slightly before/after expected dates.
- **Conversation-sourced intel bypasses this pipeline entirely** — When Haris shares Genspark Claw reports, startup intel, or competitor analysis in a chat conversation (not via email), it won't be caught by any PASS in this ingestor. Feed it manually: save to `mempalace-inputs/` as a `.md` file, then run `python3 ~/.hermes/scripts/mempalace_watcher.py`. See `pluto-autonomous-research` skill → Phase 0d for the full manual feeding pattern.
- **`no_agent: true` crons with `deliver: local` are silent** — verify with the end-to-end check above, not with `last_status: ok`.
- **Cron `last_status: ok` is NOT a guarantee** — the old himalaya-based cron reported `ok` for weeks while producing zero results. Always verify output files, not status flags.
- **🔴 Gmail app password expiration is a recurring silent failure mode (last hit: 2026-07-12→18).** Google app passwords expire periodically without warning — there is no advance notification. When the password expires, the ingestor fails with `imaplib.IMAP4.error: [AUTHENTICATIONFAILED] Invalid credentials (Failure)`. The cron shows `last_status: error` but the rest of the pipeline runs normally with ZERO email signals. **Impact:** Perplexity Tasks, Claude Daily Research, Genspark intel, and competitor email signals are ALL missing. The morning briefing feels thin but no alarm fires — it's a silent degradation. **Detection:** `hermes cron list | grep -A5 e5675447ed37` shows the IMAP error; or run `python3 ~/.hermes/scripts/gmail_ingestor_imaplib.py` directly and check for auth failure. **Recovery:** (1) Go to https://myaccount.google.com/apppasswords, (2) Generate a new app password for \"Hermes Gmail Ingestor\", (3) Update `.hermes/.env` (NOT the script — the script reads from `.env` dynamically), (4) Test: `python3 ~/.hermes/scripts/gmail_ingestor_imaplib.py`. **History:** Jul 12–18, 2026 (6 days down before detection). **Prevention:** The `.env` pattern means the script itself doesn't need changes when credentials rotate — update `.env` only.
