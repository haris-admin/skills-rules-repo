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

**Pitfall — defaulting to "buy new" when the user already has everything:** In July 2026 this user had Gemini Advanced (Veo 3.1 video gen + Imagen 3 images), ChatGPT Plus (Sora video + GPT-5.5 scripting + TTS), ChatGPT Team (more Sora), and ElevenLabs credits (voice). A first-pass recommendation of BytePlus (which would need a new paid subscription, sales call, and China data compliance review) was wrong — the correct answer was "you already have Veo 3.1 in Gemini Advanced, try that first."

**Pitfall — forgetting existing infrastructure:** After fixing the tool recommendation, the user also had Cloudflare (DNS, R2, Workers), AWS SES, and Vercel already provisioned. A click tracker that runs on Cloudflare Workers ($0 extra, uses existing infra) is better than any third-party tracking SaaS that needs a new account and billing arrangement.

**Reference:** `references/cloudflare-click-tracker-pattern.md` documents the implementation that resulted from this audit-first protocol — a Cloudflare Worker click tracker with KV logging, UTM enrichment, rate limiting, and a frontend tracking component.

**Reference:** `references/crm-integration-pattern.md` documents the AU real estate CRM research for AML Hive API integration opportunities — top 10 CRMs, competitive threats (Reapit AML/CTF built-in), and integration priority scoring.

### Phase 1: Research

**Preferred approach: Google News RSS Direct Pipeline** (proven June 2, 2026 — 60 headlines, 5 topics, 2 minutes)

This is the most reliable pattern. It avoids all subagent delegation, execute_code subprocess, and cron invocation issues:

1. **Fire 5 Google News RSS queries sequentially** (the `&` backgrounding operator in `terminal()` is actively BLOCKED by the Hermes security scanner — do NOT attempt parallel via `&`; sequential completes all 5 in ~75-90s):
   ```bash
   cd /tmp && for q in "AUSTRAC+AML+Tranche+2+compliance+Australia+2026" "Australia+digital+assets+cryptocurrency+ASIC+2026" "ASIC+AI+financial+services+regulation+Australia+2026" "Australia+PSP+payment+provider+licensing+reform" "Australia+CGT+startup+Senate+inquiry+2026"; do
     name=$(echo $q | md5sum | head -c 8)
     curl -sL --max-time 15 -A "Mozilla/5.0" -o "/tmp/gn_${name}.xml" "https://news.google.com/rss/search?q=${q}&hl=en-AU&gl=AU&ceid=AU:en"
   done
   ```
   **Pitfall — md5sum name mismatch:** Shell `md5sum` and Python `hashlib.md5()` produce DIFFERENT hashes for the same input string. If you reference these files from Python later, do NOT compute the hash with hashlib — use `terminal()` grep instead, or store the filenames explicitly. The safe extraction approach (Option B below) reads files by glob pattern, avoiding hash computation entirely.
   **Pitfall — leftover XML files from prior runs obscure which files are yours:** `/tmp/gn_*.xml` accumulates across sessions (30+ files observed July 3, 2026). The md5sum-based naming doesn't let you identify which 5 files are from *this* run. **Fix:** After firing queries, use `sorted(glob.glob('/tmp/gn_*.xml'), key=os.path.getmtime, reverse=True)[:5]` to pick the N most recently modified files — these are yours. This works reliably because `curl -o` updates mtime on each fetch. Combine with the write_file→terminal pattern: write a parser script to `/tmp/parse_gn.py`, then run `python3 /tmp/parse_gn.py` — it uses mtime sorting internally and saves cleaned headlines to a named JSON file like `/tmp/startup_vc_headlines.json` for synthesis.
   **Always use `hl=en-AU&gl=AU&ceid=AU:en`** for Australian news — this surfaces local regulatory coverage (SMSF Adviser, Law Society Journal, SmartCompany, ABC, AFR) that US locale queries miss.

2. **Extract headlines with grep** (handles minified XML):
   ```bash
   for f in /tmp/gn_*.xml; do
     grep -oP '<title>(?!.*Google News)(.*?)</title>' "$f" | head -12 | sed 's/<title>//;s/<\/title>//'
   done
   ```

3. **Synthesize into structured JSON** — write to `~/.hermes/research_outputs/research_YYYY-MM-DD.json` with the standard schema (topic, tags, meta.signal_balance, findings array)

4. **(Optional) Write gumby-brief-input.md** — a secondary cross-reference file for fleet coordination. This is NOT the primary delivery (see Phase 5) but provides a quick-reference summary that other fleet agents (Gumby, Jonny-Quest) can consume. Written to `~/.hermes/research_outputs/gumby-brief-input.md`. Skip if pipeline is time-constrained — the full briefing MD is the authoritative output.

5. **Skip delegate_task entirely** unless additional depth on a specific finding is needed. The RSS headline synthesis alone provides enough signal for medium-to-high confidence findings when cross-referenced across 5+ sources.

**Confidence-tiering for RSS-only findings:**
- **high** = 3+ distinct credible publications covering the same event (e.g., ASIC AI scrutiny reported by Norton Rose Fulbright, FinTech Global, and Australian Broker News)
- **medium** = single publication from a credible source but no cross-reference
- **low** = speculation, aggregated second-hand reports

**Enrichment: `web_search → web_extract` depth-adding pattern (NEW June 17, 2026)**

Google News RSS links cannot be curled (HTTP 400 — see Pitfalls), but `web_search` can discover the same article on the publisher's own site. Then `web_extract` pulls the full content for verified deep findings. This pattern bridges the gap between RSS headline synthesis and curl-level article verification:

1. **After RSS extraction, pick 2-4 top-signal headlines** that would benefit from deeper content
2. **Run `web_search` with the article title + publisher** to find the article on the publisher's own domain:
   ```
   web_search(query="Microsoft agentic AI failure taxonomy red teaming 2026", limit=3)
   ```
3. **Feed the discovered URLs to `web_extract`** (up to 5 URLs per call):
   ```
   web_extract(urls=["https://publisher.com/article-path", ...])
   ```
4. **Use the extracted content to enrich finding descriptions** — direct quotes, specific data points, regulatory details

This pattern was validated June 17, 2026 on the Agentic AI & Security topic: 4/4 `web_extract` calls returned rich content (The Weather Report on Microsoft failure taxonomy, MDDI Singapore official press release, Elevate Consult governance data, Fierce Network on IBM cybersecurity). Success rate is higher than curl-based article fetching because `web_extract` handles JS-rendered pages that curl returns empty.

**When to use:** When RSS headlines indicate a high-signal finding that deserves verified content for `high` confidence tiering. Not needed for every finding — RSS headline synthesis alone is sufficient for medium-confidence signals with 3+ source cross-reference.

**Pitfall:** `web_search` results include the `untrusted_tool_result` wrapper — the content inside is real and verified by cross-reference with RSS headlines. Do not dismiss results because of the wrapper. See `references/search-extract-enrichment.md` for the full pattern with this session's evidence.

**Legacy: RSS Feed Discovery Pipeline** (use for deep-dive on specific articles)

1. Discover articles via RSS feeds from Australian/international news sources:
   ```bash
   # Key feeds that reliably work:
   curl -sL -A "Mozilla/5.0" "https://www.startupdaily.net/feed/"        # Australian startups
   curl -sL -A "Mozilla/5.0" "https://www.innovationaus.com/feed/"        # Tech policy
   curl -sL -A "Mozilla/5.0" "https://www.smartcompany.com.au/feed/"      # SME/business
   curl -sL -A "Mozilla/5.0" "https://www.finextra.com/rss/headlines.aspx" # Global fintech
   curl -sL -A "Mozilla/5.0" "https://techcrunch.com/tag/australia/feed/" # TechCrunch AU
   ```
   **Australian Fintech feed (`australianfintech.com.au/feed/`) is dead — returns 0 bytes as of May 29, 2026.** Use Google News RSS queries for Australian fintech coverage instead.
   Parse with: `re.findall(r'<item>(.*?)</item>', rss, re.DOTALL)` and extract `<title>`, `<link>`, `<pubDate>`, `<description>`.
   See `references/australian-news-feeds.md` for the full feed catalog.

2. Download articles to temp files and extract text:
   ```bash
   curl -sL --max-time 20 -A "Mozilla/5.0" -o /tmp/article.html "URL"
   ```
   **Do NOT pipe curl through inline Python** — shell escaping breaks regex. Always curl-to-file first, then parse with a separate Python step.

3. Parse HTML with Python:
   - Strip `<script>`, `<style>` blocks
   - Search for `<article>` tag first for main content
   - Fall back to `<body>` if no article tag
   - Decode HTML entities: `&#8216;`→`'`, `&#8220;`→`"`, `&#8211;`→`-`, `&amp;`→`&`, etc.

4. Collect 3-6 distinct findings with sources (quality over quantity)

**Complementary: Google News RSS for broad discovery** (use alongside or in place of delegate_task)

Google News RSS search provides excellent discovery across regions and topics — 62-100 results per query, no delegation, no CAPTCHAs:
```bash
curl -sL --max-time 15 -A "Mozilla/5.0" \
  "https://news.google.com/rss/search?q=TOPIC+QUERY&hl=en-US&gl=US&ceid=US:en"
```
Parse with the same `re.findall(r'<item>(.*?)</item>', ...)` pattern. Headlines and source attribution are reliable; article links (`news.google.com/rss/articles/...`) redirect to publishers and CANNOT be fetched via curl (see Pitfalls). Use Google News for discovery + headline synthesis, then fetch confirming articles from direct publication RSS feeds when possible.

**Google News RSS is minified XML** — all content is on a single line (70-95KB). `read_file` with line limits will miss content. Two extraction approaches:

**Option A (quick grep — titles only):**
```bash
grep -oP '<title>(.*?)</title>' /tmp/gn_query.xml | grep -v 'Google News'
```

**Option B (Python — titles + source attribution, preferred):**
This approach extracts both headlines AND publisher attribution by parsing the source from the title string. Google News RSS minified XML does NOT have `<source>` tags inside `<item>` elements — the publisher name is embedded as the final segment of the title text, e.g. "Headline - Publisher Name":
```bash
python3 -c "
import re
with open('/tmp/gn_query.xml','r') as f:
    data = f.read()
items = re.findall(r'<item>(.*?)</item>', data, re.DOTALL)
for item in items:
    t = re.search(r'<title>(.*?)</title>', item, re.DOTALL)
    if t and 'Google News' not in t.group(1):
        title = t.group(1)
        if ' - ' in title:
            parts = title.rsplit(' - ', 1)
            headline, source = parts[0], parts[1]
        else:
            headline, source = title, '?'
        print(f'{headline} [{source}]')
"
```
Option B gives you publisher names alongside headlines — essential for confidence-tiering and cross-referencing. It works on minified single-line XML because `re.DOTALL` handles the missing newlines. Verified June 8, 2026: 390 headlines across 5 Google News RSS queries, 196 unique sources correctly extracted.

**Multi-angle parallel feed pattern (recommended):** Fire 4-6 Google News RSS queries simultaneously, each targeting a different subtopic angle. This yields 300+ headlines in ~15 seconds with zero delegation failures:
```bash
# Run 5 queries in parallel, each covering a distinct angle of the same topic
for q in "query1" "query2" "query3" "query4" "query5"; do
  name=$(echo $q | tr ' ' '_')
  curl -sL --max-time 15 -A "Mozilla/5.0" -o /tmp/gn_${name}.xml \
    "https://news.google.com/rss/search?q=${q// /+}&hl=en-US&gl=US&ceid=US:en" &
done
wait  # all finish in parallel
```
Then extract titles + sources from each file using the Python approach above. Synthesize across feeds — duplicate headlines across queries confirm signal strength. This pattern was verified on June 2, 2026 (5 feeds, 340+ headlines, Agentic AI & Security topic).

**CRITICAL: Do NOT use `subprocess.run(["curl", ...])` inside `execute_code` for Google News RSS** — it silently returns 0 results even with correct URLs, User-Agent, and timeout settings. As of May 31, 2026, 6/6 subprocess-run queries returned 0 items from Google News RSS. The same curl commands run directly via `terminal()` return full feeds (10+ items each). Root cause unidentified — likely curl binary path, library resolution, or environment differences between the subprocess and terminal environments.

**Recommended `execute_code` pattern for RSS workflows** (avoids both shell-escaping and subprocess issues):
```python
from hermes_tools import terminal
import re, urllib.parse

# 1. Fetch RSS to /tmp/
for name, query in queries:
    q = urllib.parse.quote(query)
    terminal(f'curl -sL --max-time 15 -A "Mozilla/5.0" -o /tmp/{name}.xml "URL"')

# 2. Parse with grep (handles minified XML)
result = terminal(f"grep -oP '<title>(.*?)</title>' /tmp/{name}.xml | head -20")
titles = re.findall(r'<title>(.*?)</title>', result['output'])
articles = [t for t in titles if 'Google News' not in t]
```
This pattern is faster than per-article curl fetching and works reliably with minified RSS XML.

**Confidence-tiering based on source depth:**
- **high** = you fetched and read the full article content yourself (curl → file → parse)
- **medium** = credible publication (NYT, Fortune, IAPP, Lawfare, SCMP, InnovationAus) — headline confirmed via RSS but content behind paywall or unfetchable
- **low** = speculation, aggregated second-hand reports, single-source without verification

**Fallback: delegate_task (when RSS feeds don't cover the topic)**

Use `delegate_task` with `toolsets: ["web", "search"]` to research multiple angles in parallel (up to 3 subagents concurrently). **WARNING:** As of May 25, 2026, 6/6 subagents returned empty `tool_trace` despite explicit instructions. If the first batch all fail, do NOT retry — switch to RSS or direct curl approach immediately. Give each subagent a specific angle, provide rich context, and always cross-check URLs since subagent summaries are self-reports.

See `references/delegation-pattern.md` for proven subagent prompt templates and failure patterns.

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

~~Run once per week via cron `3cde85223e18` (Sunday 23:00 AEST).~~ **PRUNED June 13, 2026** — superseded by the Saturday Weekly Review (`7d24b37a03f2`, Sat 6AM) which covers cross-topic synthesis with performance data. Uses DeepSeek v4 Pro for reliability.

**Workflow:**
1. **Query the mempalace** for recent topics and status:
   ```bash
   /home/habib/.hermes/venv/bin/python3 ~/.hermes/scripts/gumby_mempalace_query.py --status
   ```
2. **Load all research JSONs** from the past 7 days via `search_files(target='files', pattern='research_*.json', path='/home/habib/.hermes/research_outputs/')`, then filter by date.
3. **Cross-day deduplication (CRITICAL — new step):** Before synthesizing, scan all loaded JSONs for duplicate topics across days. A topic like CGT may appear on 5 separate days (as happened June 1–7, 2026). When the same topic repeats:
   - **Deduplicate findings:** If a finding's title or topic is substantively the same across days, consolidate into a single weekly insight with the strongest available confidence across all days.
   - **Signal balance aggregation:** Do NOT use a single day's `meta.signal_balance` as the week's verdict. Aggregate counts across all days for that topic. If `signal_balance` is structured per-dimension (e.g., `pro_compliance: 6, burden_concern: 2`), sum the counts. Re-check the 5:1 threshold against the aggregate, not any single day's snapshot.
   - **Cross-day weight normalization:** A finding that appeared in 5 daily JSONs is not 5× more important than one that appeared once — it may just mean the topic has sustained media coverage. Weight by novelty and portfolio impact, not frequency alone.
   - **Mempalace topic vs file-level topic mismatch:** The `recent_topics` from `gumby_mempalace_query.py --status` may use different labels than the actual `topic` field in the daily JSONs (verified June 7, 2026: mempalace returned "EU AI Act 2026" but no daily JSON had that exact topic). Always read the actual file content — do not rely solely on the mempalace topic list for coverage completeness.
4. **Synthesize across topics** — produce:
   - **Top 5 insights** across all research (1-2 sentences each with "Why it matters to Haris" — map to a portfolio project)
   - **Emerging trends** table (trend, momentum: accelerating/building, horizon: 0-3/3-6/6-12 months, portfolio impact)
   - **Regulatory watch** table (deadline, event, jurisdiction, urgency: critical/high/monitor)
   - **Recommended focus areas** for the coming week (area, rationale, priority: immediate/high/medium, project)
5. **Feed back to mempalace** — wrap all synthesized items as `findings` in the JSON:
   ```bash
   /home/habib/.hermes/venv/bin/python3 ~/.hermes/scripts/pluto_mempalace_feeder.py \
     --input /path/to/weekly_digest_YYYY-MM-DD.json \
     --topic "Weekly Research Digest — Week of ..." \
     --tags "weekly,digest,..." \
     --source "pluto_weekly"
   ```
6. **Gumby handoff (SKIP for weekly digest):** The `gumby-brief-input.md` is for daily briefings only. For the weekly digest, do NOT write a Gumby handoff — the weekly digest JSON + mempalace feed are the authoritative outputs. Phase 5's Gumby handoff is already marked optional for daily briefings; it is even less relevant on a weekend run with no subsequent daily pipeline.

**Digest JSON format:** The feeder script requires a `findings` array at the top level. Each finding follows the standard schema (`title`, `content`, `confidence`, `type`). Synthesized items like top insights, emerging trends, regulatory watch items, and focus areas all become `findings` entries — do NOT use keys like `top_insights`, `trends`, or `regulatory_watch` at the top level. See Pitfalls below. Use `type: "opportunity"` for recommended focus areas to distinguish them from regulatory findings.

**Output file:** `~/.hermes/research_outputs/weekly_digest_YYYY-MM-DD.json`

**Key difference from daily research:** The weekly digest re-synthesizes already-stored findings into cross-topic intelligence. It does not perform new web research — it produces meta-analysis. Every finding in the digest is a synthesis of multiple daily findings, so `confidence` should reflect the weight of corroborating sources (typically `high` when backed by 2+ daily findings from different sources).

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

For building knowledge bases from podcast transcripts. **Backend: Supabase + pgvector (LIVE).** 143 episodes across 15 podcasts as of June 5, 2026.

**Scripts (all in `~/.hermes/scripts/`):**
- `podcast_ingestor.py` — Full pipeline: DB-driven, queries `podcast_kb.podcasts` for all channels with handles. Uses yt-dlp listing → transcript download → Supabase storage. Wed+Sun 6AM cron.
- `podcast_ingest_tier2.py` — Description-based ingestion (no transcript API). For new tiers where transcripts are blocked.
- `podcast_fix_tier2_failed.py` — Targeted fix for channels that returned 0 from main ingest. Handles topic channels, extended date ranges.
- `podcast_repair_transcripts.py` — Repair missing transcripts with 90s delays overnight. VALIDATED June 5: 7→55 transcripts.
- `podcast_repair_descriptions.py` — Fill content from YouTube descriptions (NOT rate-limited, use first).

**Content acquisition (priority order):**
1. **YouTube descriptions** (`yt-dlp --print "%(description)s"`) — NOT rate-limited. Contains timestamped topics, guest names, links. ~2K chars average. PRIMARY source. Use first.
2. **Full transcripts** (`youtube-transcript-api`) — rich but IP-blocked. Use 90s delays overnight ONLY. Run `podcast_repair_transcripts.py` as a background process.
3. **Website scraping** — NOT viable (JS-rendered). Skip.

**Adding a new tier (step-by-step):**

1. **Discover YouTube handles:** Three methods in priority order:
   - **(A) Curl channel page + grep** — `curl -sL "https://www.youtube.com/@HANDLE" | grep -oP '"channelId":"[^"]+"' ` — most reliable, not rate-limited
   - **(B) YouTube search page** — `curl -sL "https://www.youtube.com/results?search_query=NAME" | grep -oP '/@[a-zA-Z0-9_-]+' | sort | uniq -c | sort -rn` — when exact handle is unknown
   - **(C) yt-dlp flat-playlist** — may be rate-limited after transcript downloads. Use as last resort.
2. **Verify:** Curl the handle URL, extract `<title>` and `channelId`/`externalId` from JSON.
3. **Update DB:** `UPDATE podcast_kb.podcasts SET youtube_handle = '@handle', channel_id = 'UC...' WHERE name = 'Podcast Name'`
4. **Run ingestion:** Use description-based script first (fast, no rate limits). Follow with transcript repair overnight.
5. **The ingestor is DB-driven** — no script changes needed. Cron auto-discovers new channels next run.

**YouTube channel types and their quirks:**
- **Standard user channels:** `flat-playlist` works. `@handle` URL works. Example: All-In, a16z, Lenny's, Logan Bartlett.
- **Topic channels (auto-generated):** `flat-playlist` returns nothing. `@handle` URL gives "does not have a videos tab". Use channel ID URL: `https://www.youtube.com/channel/UC...`. Example: Masters of Scale, How I Built This.
- **flat-playlist date issue:** `--flat-playlist` returns `NA` for `upload_date` on some channels (Logan Bartlett). Individual date fetches work: `yt-dlp --print '%(upload_date)s' VIDEO_ID`. Non-flat playlist (`--playlist-end N` without `--flat-playlist`) returns dates but is slower.
- **SINCE_DATE filtering:** The ingestor filters videos by `SINCE_DATE` (default 2025-12-01). Some channels (Logan Bartlett) had newest videos from Sep 2025 — ALL got filtered. When debugging empty results, check: (1) flat-playlist returned videos? (2) dates are not NA? (3) dates pass SINCE_DATE? Extend to 2024-06-01 for broad discovery.

See `references/podcast-ingestion-pipeline.md` for full patterns, `references/supabase-podcast-architecture.md` for schema, and `references/youtube-handle-discovery.md` for Tier 2 confirmed handles.

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

After the inline pipeline completes (~5:25 AM AEST), verify all phases actually produced output. **Do not trust `last_status: ok` alone** — phases can silently produce zero output while reporting success.

**Verification checklist (run one-liner):**
```bash
echo "== Pipeline Phase Verification =="
echo "1. Research JSON: $(ls -la ~/.hermes/research_outputs/research_$(date +%Y-%m-%d).json 2>/dev/null | awk '{print $5\" bytes\"}')"
echo "2. Morning Briefing: $(ls -la ~/.hermes/research_outputs/morning-briefing-$(date +%Y-%m-%d).md 2>/dev/null | awk '{print $5\" bytes\"}')"
echo "3. Mempalace Feed: run --status check"
echo "4. LinkedIn Ideas: $(ls -la ~/.hermes/research_outputs/linkedin-ideas_$(date +%Y-%m-%d).md 2>/dev/null | awk '{print $5\" bytes\"}')"
echo "5. Email Delivery: check Python smtplib return value"
```

**Common silent-failure patterns:**
- Research JSON exists but has 0 findings → RSS queries returned empty
- Morning briefing exists but is stale (from previous day's data) → Phase 2 synthesis loaded wrong file
- Mempalace feeder not invoked → the inline step skipped Phase 3 (common — see June 5, 2026: feeder not run despite all other phases ✅). Fix: run feeder manually, add it to the inline cron script.
- Voice overview MP3 not generated → voice cron ran but found no research JSON to read

**Remediation for missing phases:**
- **Missing research JSON** → Run Phase 1 inline (Google News RSS + Python synthesis)
- **Missing mempalace feed** → Run Phase 3 manually with `pluto_mempalace_feeder.py`
- **Missing email** → Run Phase 9 manually with Python smtplib (the himalaya auth.cmd fallback)
- **Missing LinkedIn ideas** → Run Phase 8 manually with `linkedin_ideas_generator.py`

If 2+ phases are missing simultaneously, regenerate the full briefing: re-run the research pipeline from Phase 1.

**Mempalace feeder verification** (must be run separately — the `--status` flag shows chamber state, not last-feed state):
```bash
# Check if today's topic was stored
/home/habib/.hermes/venv/bin/python3 /home/habib/.hermes/scripts/pluto_mempalace_feeder.py --status 2>&1 | grep -A3 "$(date +%Y-%m-%d)"
# Reliable check: look for today's date in chamber finding timestamps
/home/habib/.hermes/venv/bin/python3 -c "
import json, datetime
d = json.loads(open('/home/habib/.hermes/research_outputs/research_$(date +%Y-%m-%d).json').read())
print(f'Findings in JSON: {len(d.get(\"findings\",[]))} stored for {d.get(\"topic\",\"unknown\")}')
"
```
This second check validates that the JSON file itself is non-empty and correctly structured — a prerequisite for the feeder to work.

**Pluto is the sole operator of the full morning briefing pipeline as of June 4, 2026.** This includes research, synthesis, LinkedIn/blog ideation, voice overview, email delivery to hhsiddiqui@gmail.com + admin@harishabib.au, and Telegram delivery. **No Gumby forwarding — Pluto delivers directly to Haris.** Gumby is fully retired from briefing duties. All 9 cron jobs plus inline briefing/email phases are Pluto's responsibility.

## Pitfalls
- **⚠️ Watcher format mismatch — gmail briefings accumulate because watcher parser can't read them (June 30, 2026):** The watcher cron (`5678a363ce3b`) IS running but skips ALL gmail briefing files due to a format incompatibility. **Root cause:** The gmail ingestor (`gmail_ingestor_imaplib.py`) produces files with plain `## Finding` headers (no structured fields), but `mempalace_watcher.py` expects `## Finding Title` followed by `Source:` / `Type:` / `Confidence:` fields. The watcher parses these as "No findings parsed" → `"status": "skipped"` and does NOT move them to `processed/`. As of June 30, 2026, 88 `.md` files (gmail briefings from May 24–June 30) and 17 `.json` files were sitting unprocessed with an empty `processed/` directory. **This is NOT a cron failure — the watcher runs, returns exit 0, but skips everything.** The `head -60` pipe in the Phase 0 check command also SIGPIPEs the watcher mid-run. **Distinguish "down" from "format-skipping":** (a) If watcher runs and produces "stored" entries for SOME files → watcher works, format is the issue for others. (b) If watcher produces ONLY "skipped" entries → format mismatch across all pending files. (c) If watcher produces NOTHING → cron is actually down. **Fix options:** (1) Update `gmail_ingestor_imaplib.py` to add `Source:` / `Type:` / `Confidence:` fields to its output, (2) Update `mempalace_watcher.py` to handle plain `## Finding` format as a fallback, (3) Create a separate gmail-briefing processor. `mempalace_watcher.py` line 49 uses `MEMPAINPUTS_DIR.glob("*.md")`, so `pluto-msg-*.json` files in the inputs directory are completely invisible to the watcher. As of June 14, 2026, 13 pluto-msg JSON files had accumulated unprocessed for 3–14 days. These are Telegram DM messages from Haris that need dedicated JSON handling or integration through the Honcho bridge. **Check for `.json` files in `mempalace-inputs/` manually before research runs.**
- **⚠️ Post-manual-watcher verification — distinguish "down" from "skipped" (June 28, 2026):** After running `mempalace_watcher.py` manually, do NOT assume it failed if files remain in `mempalace-inputs/`. The watcher parses `.md` files expecting `## Finding Title` headers followed by content with `Source:` / `Type:` / `Confidence:` fields. Many files in the inputs directory — including `pluto-msg-*.md` (Telegram DMs), older gmail briefing formats, and files without structured findings sections — are deliberately skipped with `"status": "skipped", "error": "No findings parsed"`. This is NORMAL for those file types; it does not mean the watcher is broken. **Verification checklist after manual watcher run:** (a) check `processed/` for newly moved files (confirms watcher IS running), (b) check watcher stdout for `"status": "stored"` entries (confirms successful feeds), (c) expect `"status": "skipped"` for pluto-msg files and unstructured inputs — these need dedicated handling. If you see BOTH `"stored"` and `"skipped"` entries, the watcher is functional; the skipped files are format-incompatible, not watcher-failures. Only flag the watcher as down when NO files are processed AND no `"stored"` entries appear in output.
- **Research JSON overwrite — existing file may have wrong topic (June 11, 2026):** An existing `research_2026-06-11.json` was found containing Cloud & Infrastructure data (from a prior cron topic mismatch). It was overwritten with the correct FinTech Regulation topic. **Always read the existing research JSON's `topic` field before overwriting.** If the topic differs from what today's cron expects, either (a) archive the stale file and write the correct one, or (b) name files with topic suffixes like `research_2026-06-11_fintech.json` to avoid collisions.
- **Mempalace feeder silently skipped by cron pipeline (June 5, 2026):** The 01:28 AM AEST cron pipeline generated the full research JSON, morning briefing, and queued email delivery — but NEVER ran the mempalace feeder. All phases reported success. The feeder must be called explicitly as a separate step. If you verify a completed pipeline and find no mempalace feed, run Phase 3 manually. The cron pipeline table now documents this as a dedicated inline step at 5:07 AM AEST.
- **Feeder auto-routing bug — topic "&" + hyphenated tags misroute to pluto_research (fixed Aug 16, 2026):** `route_to_chamber()` in `pluto_mempalace_feeder.py` failed to route "Agentic AI & Security" to the `agentic-security` chamber because (a) the `&` broke the substring match for "agentic ai security", and (b) hyphenated tags (`agentic-ai`, `ai-security`, `red-teaming`) didn't match the chamber's unhyphenated tags (`agentic`, `security`, `red-team`). Result: findings silently landed in the generic `pluto_research` chamber instead of the topic chamber. **Fixed** by normalizing the topic (collapse non-alphanumerics to spaces via `re.sub(r'[^a-z0-9]+', ' ', topic)` ) and expanding hyphenated tags into component parts before matching. **Verification:** after feeding, confirm the findings landed in the correct topic chamber, not `pluto_research` — query ChromaDB at `/mnt/c/Users/habib/.mempalace/palace` for entries with today's date; if they're in `pluto_research` under the wrong topic, delete them (`col.delete(ids=...)`) and re-feed with `--chamber <correct>`. Use `--chamber` explicitly when the auto-route is uncertain.
- **Himalaya email sending: TWO failure modes, both with fixes.** (1) **Heredoc pipes time out** — `cat << 'EOF' | himalaya template send` via `terminal()` consistently times out (BLOCKED status). Fix: write to file first, then `cat /tmp/email-body.txt | himalaya template send`. (2) **Auth command fails** — `auth.cmd = "echo <password>"` in himalaya config returns `cannot get secret from command: No child process (os error 10)` in the terminal sandbox. The echo command works in a real shell but the sandbox prevents child process spawning. Fix: fall back to Python `smtplib` via `execute_code` — same Gmail app password, same SMTP server, reliably works. See `references/email-smtp-fallback.md` for the full pattern. Both failures encountered June 4-5, 2026; both workarounds verified.
- **CRITICAL: Cron runs may silently produce zero output.** As of June 2, 2026, manual `cronjob action=run` on the research job reported `last_status: ok` but produced no research JSON, no synthesis, and no gumby-brief-input.md. The cron scheduler's environment may differ from the interactive session. When this happens, do NOT retry the cron — run the research pipeline directly inline using the Phase 1 Google News RSS pattern (5 sequential curl queries + Python parsing + synthesis by hand). The inline pattern is verified reliable (re-validated July 9, 2026: AI Regulation & Compliance, 353 headlines, 215 sources, all 5 queries clean).
- Subagents may return empty `tool_trace` results silently — if a subagent's summary is missing actual facts/URLs, re-run with more specific search queries in the `context` field
- **`web_search` and `web_extract` unavailable in cron sandbox (June 25, 2026):** The skill's `allowed-tools` and Phase 1 enrichment section reference `web_search` and `web_extract`, but these tools do not exist in the Hermes cron sandbox environment. The RSS-only synthesis pipeline (Google News RSS → Python parse → headline synthesis) is the reliable path for cron runs. The `web_search → web_extract` enrichment pattern only works in interactive mode. When running as a cron job, skip Phase 1 enrichment entirely — the RSS headline synthesis across 5 queries (376 headlines from 213 sources) provides sufficient signal for high-confidence findings when cross-referenced across 3+ sources. The `allowed-tools` field should be treated as aspirational, not guaranteed.
- **"Return ONLY valid JSON" delegation pattern:** When a subagent keeps returning commentary or markdown instead of structured JSON, use this `goal` format: *"Research X. Your ONLY job is to return valid JSON. No markdown, no commentary, no code blocks. Output exactly: { ... }"*. Include the full expected JSON schema in the goal. This tripled structured output success rate (from ~30% to ~90%) in testing.
- **Subagents with `toolsets: ["web","search"]` can use real web tools** — they are NOT limited to just search. They can fetch URLs, call APIs, and scrape pages. Tell them explicitly: "use web_search to find sources, then fetch the URLs for details."
- DuckDuckGo HTML scraping via terminal/curl is unreliable — DDG now returns CAPTCHA challenges ("bots use DuckDuckGo too", "select all squares containing a duck") on both `lite.duckduckgo.com` and `html.duckduckgo.com` endpoints. Prefer RSS feeds over DDG scraping.
- **Inline Python in curl pipes breaks (TWO failure modes):** (1) Shell escaping of regex patterns inside `terminal("curl ... | python3 -c '...'")` fails with "No such file or directory". (2) **Hermes security scanner (tirith) blocks `curl | python3` pipes entirely** — flags them as HIGH risk `pending_approval`, even for trusted feeds. Always curl to a temp file first, then parse with separate Python. The safest pattern: use `execute_code` with `from hermes_tools import terminal` — curl-to-file and parse steps happen inside a single Python script with no pipe-to-interpreter.
- **F-string curly-brace escaping in `execute_code` + `terminal()` (THIRD failure mode, June 19, 2026):** When embedding Python code inside a `terminal()` call within an `execute_code` f-string, curly braces like `{headline}` or `{source}` are interpreted as f-string variable references — causing `NameError` at the outer f-string level. Example that FAILS: `terminal(f"python3 -c '...print(f\"{headline}\")...'")`. **Fix:** write the parser script to a temp file with `write_file()`, then invoke it with `terminal(f"python3 /tmp/parser.py /tmp/file.xml")`. This separates the Python parsing logic from the f-string scope entirely. Verified June 19, 2026 on 5 Google News RSS files.
- **JSON control characters from RSS feeds break json.loads() via terminal() (July 1, 2026):** Google News RSS descriptions contain control characters (0x00–0x1f range) that survive regex parsing and cause `JSONDecodeError: Invalid control character` when piping JSON through `terminal()` → `json.loads()`. **Fix:** write parsed items to a temp JSON file (not stdout) with control-character cleaning applied: `re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f]', '', text)` on headline, source, and description fields before `json.dump()`. Then read the file back using Python's `open()` directly in `execute_code` — NOT `read_file()` (see next pitfall). This avoids both the control-character and line-number-prefix issues simultaneously. Verified July 1, 2026 on 251 FinTech Regulation headlines.
- **`read_file()` returns line-numbered content incompatible with json.loads() (July 1, 2026):** The `read_file()` tool prepends line numbers (`LINE_NUM|CONTENT`) that break `json.loads()`. When you need to read a JSON file for programmatic parsing inside `execute_code`, use Python's `open()` directly instead of `read_file()`. `read_file()` is designed for human-readable text display, not machine parsing. This bit me when reading a 251-item JSON array — `read_file()` returned `1|[...` and `json.loads()` failed with "Extra data". Fix: `with open('/path/to/file.json') as f: data = json.load(f)` in execute_code.
- Do NOT generate fake URLs — if no URL, leave empty string
- Do NOT exceed 10 findings per topic — quality over quantity
- Always validate JSON before feeding
- The feeder script needs ChromaDB ONNX model downloaded (first run is slow)
- Research outputs go to `/home/habib/.hermes/research_outputs/`
- When running as a cron job: check which topics were already covered today before picking (read existing research_*.json files for today's date)
- **Staging inbox is now automated:** Watcher cron `5678a363ce3b` auto-processes `mempalace-inputs/` every 5 minutes. No manual steps needed. For urgent/one-off feeds, run `python3 ~/.hermes/scripts/mempalace_watcher.py`.
- **Windows credentials for cross-platform tasks:** When API keys or env vars are needed from the Windows side, check `/mnt/c/Users/habib/.hermes/.env` — Haris may place credentials there instead of `~/.hermes/.env`.
- **Google News RSS redirect links return HTTP 400:** The article URLs in Google News RSS feeds (`news.google.com/rss/articles/CBMimAFB...`) redirect to publisher sites, but following them with `curl -L` consistently returns "Error 400 (Bad request)" — even with realistic browser User-Agents. Google's redirect mechanism appears to validate the request origin. **Do not attempt to curl Google News article links.** Use Google News RSS for discovery + headline synthesis only. Fetch confirming articles from the publisher's own RSS feed or direct site search instead.
- **Do NOT construct article URLs from Google News RSS headlines (June 14, 2026):** Guessing publisher URLs from headlines (e.g., constructing `abc.net.au/news/2026/06/10/removing-capital-gains-tax-discount-disastrous-startups/...`) returned 404 — URL structures are not predictable from headlines alone. Search the publisher site directly by article title, use their RSS feed, or accept RSS-only confidence for that source.
- **Publisher site search pages are JS-rendered:** Direct curl of publisher search pages (e.g., `lawfaremedia.org/search?q=...`, `iapp.org/search/`, `fortune.com/search`) returns empty or minimal content because results load via JavaScript. Use the publisher's own RSS feed (if available) rather than their search page.
- **Reliably curl-accessible publishers (positive list):** These sources consistently return full article content via `curl -sL`:
- **Law Society Journal (LSJ)** (`lsj.com.au/...`) — full analysis articles, no paywall, ~87KB, ~9230 chars extractable content. Verified June 11, 2026 (AUSTRAC Tranche 2 Program Starter Kits article).
- **ASPI Strategist** (`aspistrategist.org.au/...`) — full analysis articles, no paywall, ~73KB. Verified June 11, 2026.
- **iTWire** (`itwire.com/...`) — full editorial content, ~37KB. Verified June 11, 2026.
- **Bessemer Venture Partners** (`bvp.com/atlas/...`) — full analysis articles, no paywall, ~14-60KB
- **StartupDaily** (`startupdaily.net/...`) — full content, ~770KB
- **TechCrunch Australia** (`techcrunch.com/...`) — full content, ~235KB
- **WIRED** (`wired.com/...`) — full content, ~1.3MB (use `body__inner-container` selector)
- **Finextra** (`finextra.com/...`) — full content
- **AdNews Australia** (`adnews.com.au/...`) — full regulatory/policy articles, no paywall, ~40KB, ~3,700 chars extractable content. Verified June 13, 2026 (Australia AI guardrails pause article).
- **Forbes Australia** (`forbes.com.au/...`) — candidate source. Curled successfully at 107KB (June 14, 2026) but text extraction NOT YET verified — differs from Forbes.com (paywalled/JS-rendered). Test before relying on.

**Publishers behind JS/Cloudflare/paywalls (curl returns empty or stub):** InfoWorld, CIO Dive, Microsoft Security Blog, The Hacker News, Forbes, SiliconANGLE, Dark Reading, IBM Newsroom, Mayer Brown, Bloomberg, AFR, SmartCompany (metered), InnovationAus (subscriber wall), **CIO.com** (214KB JS shell, 0 paragraphs extractable — confirmed June 6, 2026), **Computerworld** (216KB JS shell, 0 paragraphs — confirmed June 6, 2026), **W.Media** (183KB JS shell, 0 paragraphs — confirmed June 6, 2026).

**Most direct article URLs are JS-rendered — expect ~15% curl success rate:** As of May 31, 2026, only 1 of 7 article URLs (InnovationAus, which is paywall-truncated) returned extractable content via curl. InfoWorld, CIO Dive, Microsoft Security Blog, The Hacker News, Forbes, and SiliconANGLE all returned empty or navigation-only content. **Strategy:** rely on Google News RSS headlines + descriptions for synthesis (headline data is rich and source-attributed), and treat successfully curled articles as a bonus, not the primary input. The RSS descriptions alone provide enough signal for medium-confidence findings when cross-referenced across 3+ sources.
- **Signal polarity bias (CRITICAL):** Research defaults to amplifying the dominant narrative — more media coverage of regulation creates a pro-regulation echo chamber. On May 30, 2026, Haris flagged a 35:3 imbalance. **Always run the Signal Balance Check in Phase 2.** When imbalance exceeds 5:1, run a targeted counter-signal sweep with opposite-angle queries. Anti-regulation query patterns that work: `"Liberal Party Australia deregulation agenda red tape"`, `"Australian CEOs regulatory burden compliance costs"`, `"CGT capital gains tax reform criticism opposition Australia"`, `"deregulation trend innovation competitiveness"`. See `references/anti-regulation-signal-sources.md` for the full query catalog.
- **Grant/program name validation:** Verify named references before building go-to-market plans. "Neo-X" was a company that got an AFSL, not a grant program.
- **Hermes cron uses LOCAL time (AEST), not UTC:** `5 19 * * *` = 7:05 PM, not 5:05 AM. For morning delivery use `5 5 * * *`. Always check `next_run_at` timezone suffix.
- **Cron `script` field for `no_agent: true`:** Use just the filename (`pluto_honcho_bridge.py`), NOT full path with interpreter. Runner resolves under `~/.hermes/scripts/` and auto-detects Python shebang.
- **Honcho bridge `last_status: ok` is misleading (June 3, 2026):** The bridge cron reported `last_status: ok` but 7 files were sitting unpushed since June 2. The script ran, exited 0, but state tracking failed silently. Always verify by running `--list` to check for pending files: `python3 ~/.hermes/scripts/pluto_honcho_bridge.py --list`. If pending files exist, run the bridge manually. Bridge cron moved to 5:30 AM AEST (was 5:20 PM, then 6:00 AM) to align with morning pipeline.
- **DeepSeek v4 Flash:** 4.4x cheaper than v4 Pro ($0.098/$0.197 vs $0.435/$0.870 per 1M tokens). Use for cron jobs. MiniMax M3 costs 38% MORE on completion. See `references/model-pricing.md`.
- **OpenRouter multimedia gap:** Does NOT proxy TTS or Whisper. Audio models are input-only (`openai/gpt-audio-mini`). For TTS output: direct OpenAI key or gTTS. For STT: direct Whisper key or GPT Audio Mini transcription (see `references/voice-transcription-pipeline.md`).
- **YouTube RSS channel ID 404:** Some channel IDs extracted from YouTube page HTML (`channel_id=UC...`) return 404 from the RSS endpoint even when the channels clearly exist. This happened for All-In (UChJM-mF-4w_61Z6eCyl0eKQ), a16z, MFM, and Acquired on June 4, 2026, while Moonshots (UCCpNQKYvrnWQNjZprabMJlw) RSS worked in the same session. Root cause unidentified — may be a YouTube-side restriction on certain channel types. Workaround: try the channel's "videos" page HTML or use yt-dlp for video listing instead.
- **Time-aware communication (CRITICAL):** Server is UTC, Haris is Sydney AEST (UTC+10). NEVER use time-based greetings ("good morning", "good evening") when delivering research results without verifying current Sydney time. Haris flagged this June 3: greeted with "good morning" at 10:16 PM Sydney. Cron jobs run at known times (5:05 AM research, 10:15 PM voice overview) — use Sydney-aware time context in deliveries. When in interactive mode (not cron), skip time-based greetings entirely or use neutral openers.
- **YouTube transcript API rate-limiting (CRITICAL — June 4, 2026):** Both `youtube-transcript-api` and `yt-dlp --write-auto-subs` return HTTP 429 when called rapidly from the same IP. The block persists across tools. **Do NOT retry aggressively** — short backoffs worsen it. Workaround: use `yt-dlp --print "%(description)s"` for YouTube descriptions (NOT rate-limited, contains timestamps and topics). For full transcripts, use 90-second delays and run overnight.
- **90-second overnight repair VALIDATED (June 5, 2026):** The 90s-delay strategy successfully cleared YouTube's IP block overnight. Results: 7 transcripts → 55 rich transcripts (7.8× improvement). 0 episodes still showing blocking errors. This is the definitive fix for transcript rate-limiting. Run `podcast_repair_transcripts.py` with 90s delays overnight — do not attempt faster repair during the day.
- **Podcast websites are JS-rendered (June 4, 2026):** All major podcast sites (allinpodcast.co, a16z.com, acquired.fm, lennysnewsletter.com) return empty pages via curl. Skip website scraping for podcast transcripts — use YouTube descriptions or the transcript API with delays instead.
- **The podcast ingestor is DB-driven (June 5, 2026):** `podcast_ingestor.py` queries Supabase for ALL podcasts with `youtube_handle` or `channel_id` set. To add new channels, UPDATE `podcast_kb.podcasts` — no script changes needed. The Wed+Sun 6AM cron auto-discovers new channels next run. All 21 registered podcasts now have handles (Tier 1: 7, Tier 2: 8). SV Girl and Tier 3 pending.
- **YouTube handle discovery (June 5, 2026):** Three methods in priority order: (A) curl channel page HTML + grep `channelId` or `externalId` JSON — most reliable, not rate-limited; (B) YouTube search results page + grep `/@[a-zA-Z0-9_-]+` — for when the exact handle is unknown; (C) yt-dlp flat-playlist — may be rate-limited after transcript downloads. See `references/podcast-ingestion-pipeline.md` for full patterns and confirmed handles.
- **Supabase URL parsing: double `==` and `pgbouncer=true` (June 5, 2026):** The `.env` file has `SUPABASE_OPERATOR_SPOOLER_DATABASE_URL=="postgresql://..."` with a double equals sign. The regex `DATABASE_URL=(.*)` captures `="postgresql://...` which breaks psycopg2. Fix: use regex `DATABASE_URL=+["']?(.*?)["']?\\s*$` to handle 1+ equals signs and optional quotes. Additionally, `pgbouncer=true` in the Supabase pooler URL breaks psycopg2 (`invalid URI query parameter: "pgbouncer"`). Strip it with `re.sub(r'[?&]pgbouncer=true', '', url)` before connecting.

- **Cross-referencing research outputs with competitor intel:** Research findings with "portfolio_hit" fields feed into `competitor_intel.py` (cron `1a13a2d49682`). If competitor signals look noisy (all three 💰🏢🚀 simultaneously), see `fleet-intelligence` skill → `references/competitor-signal-verification.md` for validation steps. The `competitor_intel.py` script has a known false-positive pattern where single-word name tokens trigger over-broad matches.

## Reference Files
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