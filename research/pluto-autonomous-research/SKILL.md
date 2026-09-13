---
name: pluto-autonomous-research
description: Pluto's autonomous deep research pipeline — web search, synthesize, structure, and feed into ChromaDB mempalace. Use when doing self-directed research, running scheduled research cron jobs, or investigating any topic that should be persisted to the mempalace.
allowed-tools: [delegate_task, execute_code, terminal, read_file, write_file, skill_manage, memory, web_search, web_extract]
---

# Pluto Autonomous Research Pipeline

## When to Use
- Any self-directed or cron-triggered research task
- When findings should be persisted to the ChromaDB mempalace
- For daily/weekly intelligence gathering on tracked topics
- When building the Pluto knowledge graph

## Pipeline Steps

### Phase 0: Check Staging Inbox (before research)
1. **Watcher health check (FIRST):** Count *actually-pending* files — those WITHOUT a `.done` marker in `.processed/` — NOT total files in the directory. `ls mempalace-inputs/*.md | wc -l` counts already-processed files too and is MISLEADING (verified Aug 16, 2026: 45 .md files present but 0 actually pending, 161 .done markers). Processed markers live in the hidden `.processed/` dir, not `processed/`.
   ```bash
   pending=0
   for f in ~/.hermes/mempalace-inputs/*.md; do
     stem="${f##*/}"; stem="${stem%.md}"
     [ -f ~/.hermes/mempalace-inputs/.processed/"${stem}".done ] || pending=$((pending+1))
   done
   echo "Actually pending .md: $pending"
   echo "Processed markers: $(ls ~/.hermes/mempalace-inputs/.processed/*.done 2>/dev/null | wc -l)"
   ```
   **⚠️ Only if actually-pending >20 AND the oldest pending file is >1 day old is the watcher DOWN.** The watcher's parser was also updated (line ~49 uses `glob("*")` not `glob("*.md")`) and DOES parse gmail-briefing files (verified Aug 16, 2026 — 3 findings per file). See Pitfalls #1 below.
2. The watcher cron (`5678a363ce3b`, every 5 min) should auto-process `.md` files — check `processed/` to see what was handled. An empty `processed/` directory with many pending inputs = watcher not functioning.
3. For urgent requests, run manually: `python3 ~/.hermes/scripts/mempalace_watcher.py`
4. See `pluto-mempalace-bridge` skill → `references/mempalace-inputs.md` for the complete operational workflow

**⚠️ Known gap:** The watcher only globs `*.md` files (line 49 of `mempalace_watcher.py`). JSON files like `pluto-msg-*.json` placed in the inputs directory are invisible to the watcher and accumulate unprocessed. As of June 27, 2026, 17 pluto-msg JSON files (June 2–14) remain unprocessed. See Pitfalls section below.

### Phase 0b: Gmail Briefing Ingestion (before research — NEW June 3, 2026)

Pull Perplexity Tasks and other automated briefings from `macarthurgarments@gmail.com` into the mempalace pipeline. This runs via cron `e5675447ed37` at 4:55 AM AEST — 10 minutes before the research pipeline.

**Access:** Himalaya CLI configured with Gmail app password (`GOOGLE_GMAIL_APP_PASSWORD_MACARTHUR` from Windows `.env`). Config at `~/.config/himalaya/config.toml` with Gmail-specific folder aliases (`[Gmail]/Sent Mail`, etc.).

**Manual run (imaplib — no himalaya dependency):**
```bash
python3 -u /home/habib/.hermes/scripts/gmail_ingestor_imaplib.py
```

**Manual run (deprecated himalaya — broken in sandbox, DO NOT USE):**
```bash
# himalaya auth.cmd fails with "No child process (os error 10)" in Hermes sandbox
/home/habib/.hermes/venv/bin/python3 /home/habib/.hermes/scripts/gmail_briefing_ingestor.py
```

**What it does:**
1. Lists recent emails via himalaya (`--output json` returns a JSON array)
2. Filters for Perplexity Tasks, Genspark, or subjects containing "briefing"/"intel"/"digest"
3. Extracts bullet-point signals from each briefing email
4. Writes structured `.md` files to `~/.hermes/mempalace-inputs/gmail-briefing-{msg_id}-{timestamp}.md`
5. Tracks processed IDs in `~/.hermes/research_outputs/.gmail_ingestor_state.json`
6. The mempalace watcher cron (every 5 min) auto-feeds these to ChromaDB

**Briefing sources detected so far:**
- Perplexity Tasks (`team@mail.perplexity.ai`) — daily AU fintech/AML/AI briefings
- Genspark (`macarthurgarments@genspark.email`) — weekly intel digests (seen in mempalace history)

**himalaya JSON parsing note (DEPRECATED as of June 7, 2026):** `--output json` returns a valid JSON array, NOT JSON lines. Parse with `json.loads()`, not line-by-line. The `from` field is a dict: `{"name": "Perplexity Tasks", "addr": "team@mail.perplexity.ai"}`. Message IDs are strings that need `int()` conversion.

**⚠️ Himalaya is deprecated for email reading.** `auth.cmd = "echo <password>"` fails in the Hermes sandbox with `No child process (os error 10)`. Use the imaplib-based `gmail_ingestor_imaplib.py` script instead. See `pluto-gmail-signal-ingestion` skill.

**Credentials location:** `GOOGLE_GMAIL_APP_PASSWORD_MACARTHUR` in `/mnt/c/Users/habib/.hermes/.env` (Windows side). The himalaya config uses `auth.cmd = "echo <password>"` — not ideal for production but functional for WSL.

See `references/gmail-briefing-integration.md` for full config, quirks, and troubleshooting.

### Phase 0d: Manual Intel Feeding — Conversation-Sourced Reports (NEW July 3, 2026)

When Haris shares a structured intel report **in the conversation itself** (e.g. Genspark Claw startup intel, a competitor analysis from another agent, a research briefing pasted into chat), the report needs manual feeding to the mempalace — it won't arrive via the Gmail pipeline.

**Trigger:** Haris pastes or forwards a structured report (numbered opportunities, findings, financial data, tagged sections).

**Steps:**
1. **Save to mempalace-inputs** — Write a `.md` file to `~/.hermes/mempalace-inputs/` with:
   - `genspark-intel-claw-{YYYYMMDD}.md` for Claw reports
   - `competitor-intel-{topic}-{YYYYMMDD}.md` for competitor analysis
   - Use `## Finding` headers per section (watcher-compatible)
   - Include `Source:`, `Tags:`, `Type:`, `Confidence:` fields per finding
2. **Run the mempalace watcher:** `python3 ~/.hermes/scripts/mempalace_watcher.py`
3. **Verify** — Check output shows `"status": "processed"` with correct finding count
4. **Verify chamber** — `python3 ~/.hermes/scripts/pluto_mempalace_feeder.py --status | grep -A5 <chamber>`

**Why this matters:** Reports shared in conversation bypass the Gmail ingestor. If not manually fed, they never reach ChromaDB. Verified July 3, 2026: Genspark Claw report with 6 findings successfully fed.

**Pitfall:** Watcher requires `Source:`, `Type:`, `Confidence:` fields after each `## Finding`. Plain entries without these get `"status": "skipped"`. Always add these three fields.

### Phase 0e: Audit Before Recommending (tool/service evaluation protocol)

**Trigger:** User asks "what should I use?" or "is X any good?" or "what's the best Y?" — any request where you're about to recommend a new tool, service, or subscription.

**MANDATORY checklist — run ALL four steps before making any recommendation:**

1. **Audit existing subscriptions first.**
   Ask or check memory for what the user already pays for. Common subscriptions this user holds: Gemini Advanced ($20/mo), ChatGPT Plus ($20/mo ≈ $35 AUD), ChatGPT Team (~$130 AUD, 2 seats), Codex plan, ElevenLabs credits. Check Honcho memory for up-to-date subscription inventory. Do NOT recommend a new tool until you've confirmed the user doesn't already have equivalent capability through an existing subscription.

2. **Audit existing infrastructure.**
   Check what infrastructure the user already runs: Vercel deployments, AWS resources (EC2, SES, S3, CloudWatch), Cloudflare (DNS, R2, Workers), Fly.io. A tool that runs on their existing infra is better than one that needs new accounts, new billing, and new vendor management. **Cloudflare Workers + R2 in particular** — the user already has Cloudflare DNS and R2 buckets provisioned. Worker-based solutions (click trackers, redirectors, API gateways) cost $0 to start on the existing plan.

3. **Check current-date capabilities, not last-known.**
   The user explicitly flags stale data ("we have GPT-5.5 now, not GPT-4"). Before comparing tools, LOOK UP their current feature sets from their official sites — do not rely on cached knowledge more than 30 days old. For AI models: check what's included in the user's existing subscription tier, not just the headline model name. Many models (Veo 3.1, Sora, Imagen 3) may be bundled into subscriptions the user already has.

4. **Count total cost correctly.**
   When presenting options, show the TOTAL new cost — not just the price of the new tool. Frame as: "You already have X (paid), Y (paid), and Z (credits). The only gap is [specific gap]. Here's the minimum spend to fill it." Prefer a stacked recommendation (use what you have + one affordable add-on) over a suite of new tools.

Two verified incidents of skipping this checklist (recommending BytePlus while the user already had Veo 3.1 via Gemini Advanced; forgetting already-provisioned Cloudflare/AWS/Vercel infra) are logged in [Audit Before Recommending](references/audit-before-recommending.md).

**Reference:** `references/cloudflare-click-tracker-pattern.md` documents the implementation that resulted from this audit-first protocol — a Cloudflare Worker click tracker with KV logging, UTM enrichment, rate limiting, and a frontend tracking component.

**Reference:** `references/crm-integration-pattern.md` documents the AU real estate CRM research for AML Hive API integration opportunities — top 10 CRMs, competitive threats (Reapit AML/CTF built-in), and integration priority scoring.

### Phase 1: Research

**Preferred approach: Google News RSS Direct Pipeline** (proven June 2, 2026 — 60 headlines, 5 topics, 2 minutes). This is the most reliable pattern — it avoids all subagent delegation, execute_code subprocess, and cron invocation issues:

1. **Fire 5 Google News RSS queries sequentially** (the `&` backgrounding operator in `terminal()` is actively BLOCKED by the Hermes security scanner — sequential completes all 5 in ~75-90s):
   ```bash
   cd /tmp && for q in "AUSTRAC+AML+Tranche+2+compliance+Australia+2026" "Australia+digital+assets+cryptocurrency+ASIC+2026" "ASIC+AI+financial+services+regulation+Australia+2026" "Australia+PSP+payment+provider+licensing+reform" "Australia+CGT+startup+Senate+inquiry+2026"; do
     name=$(echo $q | md5sum | head -c 8)
     curl -sL --max-time 15 -A "Mozilla/5.0" -o "/tmp/gn_${name}.xml" "https://news.google.com/rss/search?q=${q}&hl=en-AU&gl=AU&ceid=AU:en"
   done
   ```
   **Always use `hl=en-AU&gl=AU&ceid=AU:en`** for Australian news — surfaces local regulatory coverage (SMSF Adviser, Law Society Journal, SmartCompany, ABC, AFR) that US locale queries miss. Shell `md5sum` and Python `hashlib.md5()` hash differently and `/tmp/gn_*.xml` accumulates across sessions — pick *this* run's files via `sorted(glob.glob('/tmp/gn_*.xml'), key=os.path.getmtime, reverse=True)[:5]`, not by recomputing the hash.

2. **Extract headlines with grep** (handles minified XML):
   ```bash
   for f in /tmp/gn_*.xml; do
     grep -oP '<title>(?!.*Google News)(.*?)</title>' "$f" | head -12 | sed 's/<title>//;s/<\/title>//'
   done
   ```

3. **Synthesize into structured JSON** — write to `~/.hermes/research_outputs/research_YYYY-MM-DD.json` with the standard schema (topic, tags, meta.signal_balance, findings array)

4. **(Optional) Write gumby-brief-input.md** — a secondary cross-reference file for fleet coordination (Gumby, Jonny-Quest). NOT the primary delivery (see Phase 5); skip if time-constrained.

5. **Skip delegate_task entirely** unless additional depth on a specific finding is needed. RSS headline synthesis alone provides enough signal for medium-to-high confidence findings when cross-referenced across 5+ sources.

**Confidence-tiering for RSS-only findings:** high = 3+ distinct credible publications covering the same event; medium = single credible publication, no cross-reference; low = speculation/second-hand.

**Enrichment: `web_search → web_extract` depth-adding pattern.** Google News RSS article links cannot be curled (HTTP 400), but `web_search` can discover the same article on the publisher's own site, then `web_extract` pulls full content for `high`-confidence findings. Pick 2-4 top-signal headlines after RSS extraction, `web_search(query="<headline> <publisher>", limit=3)`, then `web_extract(urls=[...])` (up to 5 per call). Validated June 17, 2026 (4/4 success). Not needed for every finding — only when a headline deserves verified `high`-confidence content. `web_search` results carry an `untrusted_tool_result` wrapper; the content inside is still real, don't dismiss it. Full pattern with evidence: `references/search-extract-enrichment.md`.

Legacy per-feed discovery (direct publisher RSS), broad Google News RSS discovery, the minified-XML extraction options (grep vs. Python title+source parsing), the multi-angle parallel-fetch pattern, the `subprocess.run` pitfall inside `execute_code`, the recommended `execute_code` curl-to-file pattern, source-depth confidence tiering, and the `delegate_task` fallback (with its known empty-`tool_trace` failure mode): see [RSS Research Extraction Patterns](references/rss-research-extraction-patterns.md).

### Phase 2: Synthesize

#### Step 1: Signal Balance Check (MANDATORY — do not skip)
After collecting findings, run a signal polarity audit. **Adapt the polarity dimensions to the topic:**
- For regulation topics (AI, fintech): count pro-regulation vs anti-regulation, pro-intervention vs market-freedom
- For cloud/infrastructure: count pro-growth/hyperscaler vs caution/repatriation/cost-concern
- For startup/VC: count bullish/funding vs bearish/correction signals
- For security: count threat-escalation vs defense-innovation narratives
1. Count both sides across all findings using the topic-appropriate dimensions
2. **If any ratio exceeds 5:1, run a targeted counter-signal sweep before proceeding.** Re-run Phase 1 with explicitly opposite-angle queries (see `references/anti-regulation-signal-sources.md` for proven query patterns).
3. Document the dimensions used and before/after ratio in the research output's `meta.signal_balance` field.
4. See `references/signal-balance-adaptation.md` for topic-specific polarity frameworks.

**Why:** On May 30, 2026, Haris flagged a 35:3 pro-to-anti-regulation blind spot. Research defaults toward amplifying the dominant narrative (more coverage = more signals found). Active counter-balancing is required to produce credible intelligence. On May 31, 2026 (Cloud topic), adapting dimensions to "pro-growth vs caution" yielded a 0.67:1 balance — proving the adaptation pattern works.

**The sweep is NOT optional when imbalance > 5:1.** Run it, document the counter-signals found, and record the post-sweep ratio.

**⚠️ Post-sweep ratio still above 5:1 — when to stop vs loop:** Some topics are inherently skewed. "AI Regulation & Compliance" research will always surface more pro-regulation coverage because that IS the global trajectory (EU, Australia, UK, Canada all legislating). A counter-sweep surfaces the minority view (US deregulation, compliance burden concerns) but won't flip the ratio. **After one counter-sweep, check the `signal_balance.note` field:** if you can credibly explain why the imbalance persists (topic skew vs blind spot), proceed. Do NOT run multiple counter-sweeps trying to hit an arbitrary numeric threshold — one well-documented sweep is sufficient. Verified July 4, 2026: AI Regulation topic had 133:19 (7:1) post-sweep — the US deregulation counter-narrative was found and documented, but global regulatory trajectory means pro-regulation coverage genuinely dominates. The note field explained this, and the pipeline proceeded with credible findings.

#### Step 2: Structure Findings
1. Structure each finding as: {title, content, confidence, url, type, portfolio_hit, impact, sources}
2. Types: regulatory, technical, market, opportunity, threat, trend
3. Confidence levels: high (official source), medium (credible analysis), low (speculation)
4. **portfolio_hit (recommended):** Map to Haris's portfolio: FinAI File AU, AML Hive, PayLicence AU, TokenPilot AU, ExitLens AU, CloudProof AU, Tapease
5. **impact (recommended):** critical (immediate deadline), severe (significant), medium (monitor)
6. **sources (recommended):** Array of 3+ publication names for cross-referencing and briefing-engine provenance
7. Add `meta.signal_balance` to output JSON with polarity counts, dimension labels, ratio, and threshold flag

### Phase 3: Feed to Mempalace
Run the feeder script AFTER Phase 2 (Cross-Chamber Synthesis) is complete — the JSON must include the enriched `meta.signal_balance` field for the ChromaDB record to be complete.
```bash
/home/habib/.hermes/venv/bin/python3 /home/habib/.hermes/scripts/pluto_mempalace_feeder.py \
  --input /path/to/research_output.json \
  --topic "Topic Name" \
  --tags "tag1,tag2,tag3" \
  --source "pluto_autonomous"
```
**Pitfall:** The feeder is NOT automatically invoked by the cron research pipeline (verified June 5, 2026 — research JSON and full briefing were generated but mempalace was not fed). It must be called explicitly as an inline step at ~5:12 AM AEST, right after Cross-Chamber Synthesis completes.

### Phase 4: Daily Summary (end of day)
If this is the last research run of the day, also create a daily summary:
```bash
/home/habib/.hermes/venv/bin/python3 /home/habib/.hermes/scripts/pluto_mempalace_feeder.py \
  --status
```

### Phase 5: Full Morning Briefing (Pluto Direct — No Gumby Forwarding)

**As of June 4, 2026, Pluto delivers the full morning briefing directly.** No Gumby forwarding — the primary delivery is the morning briefing MD + dual-email + voice overview + Telegram. The `gumby-brief-input.md` file is **optional** and written only as a lightweight fleet-reference cross-check for other agents (Gumby, Jonny-Quest). It is NOT the primary handoff.

**Briefing report format:** Write to `~/.hermes/research_outputs/morning-briefing-YYYY-MM-DD.md` with these sections:
1. **Header:** Date, topics, signal balance summary
2. **🚨 TOP SIGNALS:** Each finding as a standalone section with:
   - 🟢/🟡/🔴 severity marker + 📜/🔒/📈/💰 type emoji
   - Title, content, sources, confidence, type
   - **> For Haris:** actionable insight with specific portfolio project + action
3. **📊 SIGNAL BALANCE AUDIT:** Table showing pro/con counts per topic with 5:1 threshold flag
4. **🔗 PORTFOLIO IMPACT MAP:** Cross-reference table mapping each signal to portfolio projects
5. **✍️ LINKEDIN POST IDEAS:** 3-4 post drafts with hook/angle/CTA + content pillar
6. **📝 BLOG POST IDEAS:** 2-3 blog ideas with pillar, gap filled, companion post
7. **⏱️ TIMELINE & ACTIONS:** Priority table with deadlines

**Email delivery (see Phase 9) uses himalaya with file-based piping:**
```bash
cat /tmp/email-body.txt | himalaya template send
```
Send to BOTH `hhsiddiqui@gmail.com` AND `admin@harishabib.au`. See `himalaya` skill for the file-based pipe pattern (heredocs time out in terminal).

**Honcho push (complementary):** The `pluto_honcho_bridge.py` cron still pushes structured `[pluto]` signal cards to Honcho at 5:30 AM AEST for the Honcho memory layer. See `fleet-intelligence` skill → `references/honcho-signal-bridge.md`.

### Phase 6: Voice Overview (automated)
The Morning Briefing cron (`c527fed4a1da`, 6:00 AM Mon-Fri) delivers the briefing with TTS (voice overview) via the `pluto-voice-overview` skill pipeline. If voice delivery fails, the text briefing still goes out via the morning briefing's normal delivery.

### Phase 7: Weekly Digest (weekend run — cross-topic synthesis)

**PRUNED June 13, 2026** — superseded by the Saturday Weekly Review (`7d24b37a03f2`, Sat 6AM), which covers cross-topic synthesis with performance data. Where still run: query the mempalace for recent topics, load the past 7 days of `research_*.json`, deduplicate/aggregate findings that repeat across days (do NOT treat a single day's `signal_balance` as the week's verdict), synthesize top insights/emerging trends/regulatory watch/focus areas as `findings` entries, and feed the result back to the mempalace with `--source "pluto_weekly"`. Skip the Gumby handoff entirely for weekly runs.

Full cross-day deduplication algorithm, the digest JSON format (`findings` array requirement — do NOT use top-level keys like `top_insights`), and how this differs from daily research: see [Weekly Digest Workflow](references/weekly-digest-workflow.md).

### Phase 8: LinkedIn & Blog Content Ideation (NEW June 3, 2026)

Runs via cron `ee4e48300826` at 6:45 AM AEST — after all research stages complete. Generates LinkedIn post drafts and blog post ideas for harishabib.au.

**Manual run:**
```bash
/home/habib/.hermes/venv/bin/python3 /home/habib/.hermes/scripts/linkedin_ideas_generator.py
```

**What it does:**
1. Pulls latest Perplexity signals from Gmail via himalaya
2. Reads today's research JSON and actions JSON
3. Cross-references Haris's 4 existing blog posts on harishabib.au:
   - The Docker Moment for AI Agents
   - The Human-AI Partnership: A Framework for Safe Adoption
   - Resilience Engineering in the Cloud
   - The 2026 Budget Changed the ESOP Question
4. Maps to Haris's content pillars: AI Agents & Governance, Australian Fintech Regulation, Cloud & Resilience, Startup & ESOP
5. Generates 3-5 LinkedIn post ideas (hook + angle + CTA) and 2-3 blog ideas (filling content gaps)
6. Outputs to `~/.hermes/research_outputs/linkedin-ideas_YYYY-MM-DD.md`

**Haris's portfolio projects (for cross-referencing):** ExitLens AU (ESOP/CGT), PayLicence AU (PSP licensing), TokenPilot AU (DLT/AFSL), FinAI File AU (AI governance), CloudProof AU (cloud compliance), AML Hive (AML/CTF), Tapease.

**LinkedIn post structure:** Hook (1-2 sentence grabber with specific data), Angle (2-3 sentences connecting to Haris's expertise), CTA (1 sentence engagement prompt referencing specific portfolio offering).

**Blog post structure:** Fill gaps in existing content. Each idea notes pillar, gap filled, and companion-post recommendation.

**Output file:** `~/.hermes/research_outputs/linkedin-ideas_YYYY-MM-DD.md`

See `references/linkedin-content-extraction.md` for content pillar details and `references/gmail-briefing-integration.md` for Gmail signal sourcing.

### Phase 9: Email Delivery (NEW June 4, 2026 — Updated June 5, 2026)

After the briefing report is written, send it to Haris's email addresses. This replaces the old Gumby handoff — Pluto delivers directly.

**Recipients (both required):**
- `hhsiddiqui@gmail.com`
- `admin@harishabib.au`

**Primary method: Python smtplib (RELIABLE — June 5, 2026)**

Himalaya `auth.cmd` fails in the Hermes terminal sandbox with "No child process (os error 10)" — the sandbox cannot spawn child processes for auth commands. This breaks ALL himalaya commands. Use Python's stdlib `smtplib` instead:

```python
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_email(to_addr, subject, body, password):
    msg = MIMEMultipart()
    msg['From'] = 'macarthurgarments@gmail.com'
    msg['To'] = to_addr
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))
    
    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        server.login('macarthurgarments@gmail.com', password)
        server.send_message(msg)

# Gmail app password from himalaya config
password = 'mlcbaeezdhquyewk'
for to in ['hhsiddiqui@gmail.com', 'admin@harishabib.au']:
    send_email(to, subject, body, password)
```

**Gmail app password:** Hardcoded in `~/.config/himalaya/config.toml` as `auth.cmd = "echo mlcbaeezdhquyewk"`. Extract from there or use `GOOGLE_GMAIL_APP_PASSWORD_MACARTHUR` from Windows `.env`.

**Email format: Unified Briefing style (NEW June 5, 2026).** Haris prefers the clean, sectioned Gumby-style format. Use emoji markers (🔴🟡🟢) NOT text markers ([RED]/[YELLOW]/[GREEN]). Required sections in order:

1. `Unified Morning Briefing` header + date line + agent attribution
2. `TOP 3 (cross-area)` — three most impactful signals, each: emoji + title + 2-line summary + `>> Project: Action. Deadline.`
3. `BY AREA` — 10-12 categories on one line each with status: `🔴 ACTIVE`, `🟡 ACTIVE`, `🟢 WARM`, or `quiet`
4. `LINKEDIN POSTS READY` — numbered list with project attribution
5. `BLOG IDEAS` — numbered list with deadlines in parentheses
6. `SOURCES USED` — checkmark-tracked source inventory: `[✓]` or `[ ]`
7. `ONE ACTION FOR TODAY` — 3-5 sentences on the single most impactful thing to do
8. `PRIORITY QUEUE` — P0/P1/P2 with project + deadline
9. `ATTACHMENTS` — file paths to full report, research JSON, voice MP3
10. Footer: `Pluto 🌑 | Autonomous Research Agent` + `Hermes Executive Reporting System`

**Template:** `~/.hermes/templates/email-briefing-template.txt` — copy and fill in `{date_long}`, `{datetime}`, `{top_3_signals}`, `{area_status}`, etc.

**Sender:** `Pluto Research <macarthurgarments@gmail.com>`

**Fallback: himalaya file-based pipe (⚠️ BROKEN in sandbox — DO NOT USE as of June 2026):**
```bash
# 1. Write email body to temp file first
write_file("/tmp/email-body.txt", email_content)
# 2. Pipe file to himalaya
terminal("cat /tmp/email-body.txt | himalaya template send")
```

See `himalaya` skill → `references/smtplib-fallback.md` for the full smtplib pattern and when to use which method.

### Phase 10: Podcast Knowledge Ingestion (June 2026 — Updated June 5, 2026)

For building knowledge bases from podcast transcripts. **Backend: Supabase + pgvector (LIVE).** 143 episodes across 15 podcasts as of June 5, 2026. DB-driven pipeline (`podcast_ingestor.py`, Wed+Sun 6AM cron) with description-first content acquisition (YouTube descriptions are not rate-limited; full transcripts are, so those need 90s-delay overnight repair).

Full script inventory, the content-acquisition priority order, the step-by-step process for onboarding a new podcast tier, and YouTube channel-type quirks (topic channels, flat-playlist date bugs, SINCE_DATE filtering): see [Podcast Knowledge Ingestion](references/podcast-knowledge-ingestion.md), `references/podcast-ingestion-pipeline.md` for full patterns, `references/supabase-podcast-architecture.md` for schema, and `references/youtube-handle-discovery.md` for Tier 2 confirmed handles.

### Phase 11: Daily Learning Sessions

Cron `0fb6bf47f704` delivers a daily learning session at 6:15 AM AEST. It picks one topic from MemPalace chambers (odd days: `critical-infra`, even days: `startup-vc`), explains the concept in 300-400 words, connects to Haris's portfolio, and asks a thought-provoking question.

See `pluto-morning-briefing-v2` skill → `references/daily-learning-format.md` for the full session format.

## Morning Cron Pipeline (Complete — June 4, 2026)

All times AEST (Sydney). Server is UTC — cron uses AEST timezone. **Pluto now delivers the full morning briefing directly — no Gumby intermediary.**

| Time | Job ID | Name | Phase |
|------|--------|------|-------|
| 4:55 AM | e5675447ed37 | Gmail Briefing Ingestor | 0b |
| 5:05 AM | b0de180cec84 | Pluto Morning Research | 1 |
| 5:10 AM | ddceef1f9e5b | Cross-Chamber Synthesis | 2 |
| 5:12 AM | (inline) | Mempalace Feed | 3 |
| 5:15 AM | 38c1aa80a5b8 | Action Bridge | 3 |
| ~5:10 AM | (inline) | Full Briefing + Email Delivery | 5, 9, 10 |
| ~5:25 AM | (inline) | Pipeline Verification | — |
| 5:30 AM | pluto_honcho_bridge_daily | Honcho Signal Bridge | Honcho push |
| 6:10 AM | 59f18c4d557c | Feedback Loop | — |
| 6:45 AM | ee4e48300826 | LinkedIn Ideas Generator | 8 |
| 6:00 AM | c527fed4a1da | Morning Briefing + TTS | 6 |
| Sun 9:00 AM | PRUNED (was 3cde85223e18) | Weekly Digest — superseded by Saturday Weekly Review | — |
| Fri 11:05 PM | cc5ca5690d05 | Weekly Self-Review | — |
| Sat 12:00 AM | 159702fe072c | Weekly Auto-Improvements | — |

**Weekly Review + Improvement Cycle:** The Friday 11:05 PM `pluto-weekly-review` cron audits all pipelines, crons, research quality, and skill debt — producing an honest report to `~/.hermes/reviews/weekly/`. The Saturday 12:00 AM auto-improvement cron reads that report and implements the action items (skill creation, config fixes, cron repairs). This is the fleet's self-healing loop. See `pluto-weekly-review` skill for the full pipeline.

## Tracked Topics (Priority Order)
1. **AI Regulation & Compliance** — EU AI Act, Australian AI guardrails, global AI governance
2. **Cloud & Infrastructure** — Cloud repatriation trends, AWS/Azure/GCP shifts, cost optimization
3. **FinTech Regulation** — AUSTRAC, AML/KYC, Australian regulatory changes
4. **Agentic AI & Security** — Multi-agent systems, AI security landscape, red-teaming
5. **Startup & VC Trends** — Australian startup ecosystem, fintech funding, moonshot opportunities

## Output Format
Research outputs must be valid JSON:
```json
{
  "topic": "Research Topic",
  "research_date": "YYYY-MM-DD",
  "tags": ["tag1", "tag2"],
  "meta": {
    "signal_balance": {
      "dimensions_used": ["dimension_a", "dimension_b"],
      "dimension_a": <count>,
      "dimension_b": <count>,
      "ratio": "X:Y",
      "below_5_1_threshold": true|false,
      "note": "context on counting methodology (e.g. deadline delays counted as moderation)"
    }
  },
  "findings": [
    {
      "title": "Finding title",
      "content": "Detailed content...",
      "confidence": "high|medium|low",
      "url": "https://source.url",
      "type": "regulatory|technical|market|opportunity|threat|trend",
      "portfolio_hit": "FinAI File AU",
      "impact": "critical|severe|medium",
      "sources": ["Source A", "Source B", "Source C"]
    }
  ]
}
```
**`portfolio_hit` and `impact` are optional but RECOMMENDED** — the v2 briefing improver (`briefing_improver.py`) depends on them for portfolio heatmaps and action checklists. Include both whenever findings map to Haris's portfolio projects (FinAI File AU, AML Hive, PayLicence AU, TokenPilot AU, ExitLens AU, CloudProof AU, Tapease). `impact` values: `critical` (immediate deadline/obligation), `severe` (significant but not imminent), `medium` (trend to monitor). The `sources` array is also recommended — it provides the briefing engine with provenance for confidence-tiering without needing to re-parse the full content field.

## Phase Verification (Post-Run Guardrail)

After the inline pipeline completes (~5:25 AM AEST), verify all phases actually produced output. **Do not trust `last_status: ok` alone** — phases can silently produce zero output while reporting success (research JSON with 0 findings, stale briefing, mempalace feeder skipped, voice MP3 not generated). If 2+ phases are missing simultaneously, regenerate from Phase 1.

**Pluto is the sole operator of the full morning briefing pipeline as of June 4, 2026** — research, synthesis, LinkedIn/blog ideation, voice overview, email delivery (hhsiddiqui@gmail.com + admin@harishabib.au), and Telegram delivery, with no Gumby forwarding.

The full verification one-liner, per-phase remediation steps, and the separate mempalace-feeder verification check: see [Post-Run Phase Verification](references/post-run-phase-verification.md).

## Pitfalls

Quick rules that apply on every run:
- Do NOT generate fake URLs — if no URL, leave empty string
- Do NOT exceed 10 findings per topic — quality over quantity
- Always validate JSON before feeding; the feeder needs its ChromaDB ONNX model downloaded (first run is slow)
- Research outputs go to `/home/habib/.hermes/research_outputs/`
- When running as a cron job, check which topics were already covered today before picking a new one
- Staging inbox watcher (`5678a363ce3b`) auto-processes `mempalace-inputs/` every 5 min — no manual steps needed unless urgent
- Check `/mnt/c/Users/habib/.hermes/.env` for Windows-side credentials if a key is missing
- Hermes cron uses LOCAL time (AEST), not UTC — always check `next_run_at`'s timezone suffix
- Time-aware communication: server is UTC, Haris is Sydney AEST — never use time-based greetings without checking current Sydney time first

The full dated incident log — watcher format-mismatch vs. down, research JSON topic collisions, the mempalace feeder being silently skipped, the feeder's topic auto-routing bug, both himalaya email failure modes, cron silently producing zero output, subagent/web-tool failure modes, the three inline-Python/curl-pipe failure modes, JSON/`read_file()` parsing gotchas, the publisher curl reliability lists (which sites work vs. are JS-walled), signal polarity bias, cron scheduling gotchas, model pricing, and podcast/YouTube rate-limiting incidents — is preserved in full at [Pitfalls & Incident Log](references/pitfalls-and-incident-log.md).

## Reference Files
- `references/rss-research-extraction-patterns.md` — Legacy/broad RSS discovery, minified-XML extraction options, multi-angle parallel pattern, subprocess/execute_code pitfalls, delegate_task fallback
- `references/audit-before-recommending.md` — Case studies behind the Phase 0e tool/subscription/infra audit checklist
- `references/weekly-digest-workflow.md` — Full Phase 7 cross-day dedup, aggregation, and digest JSON format
- `references/podcast-knowledge-ingestion.md` — Full Phase 10 script inventory, tier onboarding steps, YouTube channel-type quirks
- `references/post-run-phase-verification.md` — Full post-run verification one-liner, remediation steps, mempalace feeder check
- `references/pitfalls-and-incident-log.md` — Full dated incident log (watcher issues, feeder bugs, email failure modes, JSON/parsing gotchas, publisher curl reliability, etc.)
- `references/delegation-pattern.md` — Proven subagent prompt templates
- `references/australian-news-feeds.md` — RSS feed catalog
- `references/google-news-rss-patterns.md` — Google News RSS search queries per topic
- `references/anti-regulation-signal-sources.md` — Counter-signal sweep query catalog
- `references/signal-balance-adaptation.md` — Per-topic polarity frameworks
- `references/voice-transcription-pipeline.md` — ogg→mp3→GPT Audio Mini workflow
- `references/model-pricing.md` — OpenRouter LLM cost comparison
- `references/email-smtp-fallback.md` — Python smtplib fallback when himalaya auth.cmd fails (see `himalaya` skill → `references/smtplib-fallback.md`)
- `references/gmail-briefing-integration.md` — Gmail→MemPalace ingestion pipeline (June 2026)
- `references/linkedin-content-extraction.md` — LinkedIn/Blog content ideation pipeline (June 2026)
- `references/podcast-ingestion-pipeline.md` — YouTube RSS→transcript→framework extraction for podcast knowledge bases (June 2026)
- `references/supabase-podcast-architecture.md` — Supabase+pgvector schema, podcast tiers, AU relevance scoring, hybrid search (June 2026)
- `references/educational-content-sourcing.md` — Agentic AI educational content sourcing: proven query catalog, creator discovery, MemPalace feed (June 2026)
- `references/youtube-handle-discovery.md` — YouTube channel handle/ID discovery: curl+regex, search page, yt-dlp methods; confirmed Tier 2 handles (June 2026)
- `references/antigravity-investigation.md` — Emerging tech intelligence gathering case study: Google Antigravity 2.0 investigated via Google News RSS, npm ecosystem analysis, and installation testing (June 2026). Pattern: RSS discovery → registry search → landing page probe → local verification → synthesize from headlines.
- `references/js-bundle-pricing-extraction.md` — Extract full pricing from SPA JS bundles when landing pages only show deposits. Technique: curl bundle → grep for `Af=` pricing config → extract `full` vs `reservation` amounts. Verified June 12, 2026 on Monako.ai ($399 full, $19 deposit).
- `references/cgt-reform-knowledge-bank.md` — Condensed CGT reform knowledge bank: Senate hearing timeline, 9 recommendations from Startup Daily submission, key structural data points (2/3 foreign capital, <0.5% super to VC, Canva CR 2025/34 tax trap), angel investing indexation model analysis. Compiled June 14, 2026.
- `references/search-extract-enrichment.md` — web_search → web_extract depth-adding pattern: bypass Google News RSS link restrictions by discovering articles on publisher domains, then extracting full content. Validated June 17, 2026 (4/4 success rate).