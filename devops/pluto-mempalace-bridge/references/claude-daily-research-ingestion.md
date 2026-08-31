# Claude Daily Research ingestion

## ⚠️ FORMAT CHANGE FIXED 20 Aug 2026 — parser was silently skipping for weeks

**Symptom:** Gmail Ingestor cron (`e5675447ed37`) reports `0 new emails processed` every day even though Claude Daily Research emails ARE arriving (forwarded from Haris to macarthurgarments@gmail.com). Zero `claude-research-*.md` files ever written. No error — a silent skip.

**Root cause:** The email format changed (mid-June 2026). The parser expected the old format:
`*1. Title* — *Source*` (asterisk-marked findings). The current format is:
```
💳 Global Fintech News                    <- section header (emoji-prefixed)
SEC Proposes "Regulation Crypto Assets"   <- plain title line, NO asterisks
<https://www.google.com/url?q=...>        <- URL on its own line
                                            <- blank
The SEC unveiled a proposed rule...       <- description paragraph(s)
```
`extract_claude_signals()` matched nothing → `if signals:` false → file never written → email marked processed → **permanent silent loss**.

**The fix (applied to `gmail_ingestor_imaplib.py`):**
1. `SECTION_PATTERN` emoji set broadened: added 💳🦞📬🛡️⚡🏦🏢📱💻🧠📰🗞️✅❌🎯🧭🌏♻️🔎🧩💼🏛️📉📌 (was missing 💳 Global Fintech, among others).
2. New patterns added: `CLAUDE_TITLE_PATTERN` (plain title line, 8–160 chars) + `CLAUDE_URL_PATTERN` (`<https?://...>`).
3. `extract_claude_signals()` rewritten: a finding title = plain line whose **next non-empty line is a `<url>`**. This kills header noise and description-splitting. Descriptions append after the URL until the next title/section.

**Verification:** 6 real emails → 142 signals extracted (was 0). 8 `claude-research-*.md` files written, all fed to chambers. Post-feed: 162 claude-tagged docs in `regulatory-ai`, 9 in `fintech-aml`.

**Pitfall — the 2-day window:** PASS 2 searches `SINCE <2 days ago>`. Older emails sitting in the inbox are skipped. If you suspect missed emails, backfill manually (see the backfill snippet in this skill's history) or widen the window.

**Detection rule:** if the cron says `0 new emails processed` for 2+ days straight while Haris confirms he's forwarding Claude Daily Research, run the parser test against a live email:
```python
# fetch latest Claude DR email, run gi.extract_claude_signals(body)
# — if 0 signals, the format changed AGAIN. Do not just re-run the cron.
```


**Source:** `hhsiddiqui@gmail.com` forwards Claude Daily Research to `macarthurgarments@gmail.com`
**Subject pattern:** `Claude Daily Research - DD Mmm YYYY`
**Frequency:** Daily
**First ingested:** June 7, 2026 (msg_id 3535)

## Format

Claude Daily Research is a structured multi-section briefing with these sections:

```
🌍 GLOBAL FINTECH         — *N. Title* — *Source, Date*  format
🇦🇺 AUSTRALIAN FINTECH     — *N. Title* — *Source, Date*  format
🤖 AI & AGENTIC PROGRAMMING — *N. Title* — *Source, Date*  format
🚀 STARTUP NEWS            — *N. Title* — *Source, Date*  format
☁️ CLOUD & MODERN TECHNIQUES — *N. Title* — *Source, Date*  format
📍 SYDNEY EVENTS           — *N. Event Name — Date | Location*  (no source field)
💰 ACCELERATORS            — *N. Program Name — Details*  (no source field)
```

## Parser Requirements

### Line Ending Normalization
The forwarded email uses `\r\n` line endings. Always normalize before parsing:
```python
text = text.replace('\r\n', '\n').replace('\r', '\n')
```

### Main Content Sections (Fintech, AI, Startup, Cloud)
Use regex: `r'^\*(\d+)\.\s+(.+?)\*\s*—\s*\*(.+?)\*$'`
- Group 1: number
- Group 2: title
- Group 3: source attribution

Email wrapping often splits the title-source line. Try joining with next line if regex doesn't match:
```python
if not match and i + 1 < len(lines):
    joined = line + ' ' + lines[i + 1].strip()
    match = FINDING_PATTERN.match(joined)
    if match:
        i += 1  # consume next line
```

### Events/Accelerators Sections
Use simpler regex: `r'^\*(\d+)\.\s+(.+?)\*\s*$'`
These sections have no separate source field — the entire line is the finding.

## Chamber Routing

Route Claude signals to dedicated source-topic chambers, not domain chambers:

| Claude Section | Chamber |
|----------------|---------|
| GLOBAL FINTECH | `fintech-aml` (funding, M&A, revenues) or `startup-funding` (mega-rounds) |
| AUSTRALIAN FINTECH | `fintech-aml` |
| AI & AGENTIC PROGRAMMING | `coding-agents` (Copilot, Claude Code) or `ai-frontier` (Foxconn, Itential) |
| STARTUP NEWS | `startup-vc` (ecosystem) or `startup-funding` (funding rounds) |
| CLOUD & MODERN TECHNIQUES | `cloud-frontier` |
| SYDNEY EVENTS | `events-sydney` |
| ACCELERATORS | `accelerators` |

**Keyword overrides** catch items that belong in a different chamber than their section suggests (e.g., "AWS Trainium" in Startup News → `cloud-frontier`).

## Watcher Format

The mempalace watcher only parses `##` headers. Use this format:
```markdown
# Claude Daily Research: Claude Daily Research - 07 Jun 2026
Source: Haris <hhsiddiqui@gmail.com>
Tags: claude, daily_research

## [GLOBAL FINTECH] Ramp Raises $750M Series F at $44B Valuation
*Source: FinTech Global, 5 Jun 2026*
US financial operations platform Ramp secured...
Type: trend
Confidence: high
```

Do NOT use `## Section Name > ### Finding Title` nesting — the watcher will miss the findings.

## Ingestion Script

`~/.hermes/scripts/gmail_ingestor_imaplib.py` handles Claude Daily Research in **PASS 2** (subject-based search):
```python
status, messages = mail.search(None, f'(SUBJECT "Claude Daily Research" SINCE {since_date})')
```

The script uses `extract_claude_signals()` for parsing and `format_claude_markdown()` for output.

## Sydney Events / Accelerators — User Preference

**Per Haris (June 7, 2026):** Preference for online/free events over in-person daytime sessions. He's busy with day job + building solutions. When presenting events, prioritize:
1. Virtual/remote attendance options
2. Free events
3. Evening/weekend sessions
4. Online AMAs and workshops (e.g., Founder Institute's free online events)

Most Sydney events listed in Claude Daily Research are in-person only. The Founder Institute AMA ("What Makes Investors Say Yes", Sep 2) is the standout online+free option.
