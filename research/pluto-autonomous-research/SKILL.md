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

**⚠️ Known gap:** JSON files (`pluto-msg-*.json`) in the inputs directory are invisible to the watcher and accumulate. See Pitfalls below.

### Phase 0b: Gmail Briefing Ingestion (before research — NEW June 3, 2026)

Pull Perplexity Tasks and other automated briefings from `macarthurgarments@gmail.com` into the mempalace pipeline. This runs via cron `e5675447ed37` at 4:55 AM AEST — 10 minutes before the research pipeline.

**Access:** Himalaya CLI configured with Gmail app password (`GOOGLE_GMAIL_APP_PASSWORD_MACARTHUR` from Windows `.env`). Config at `~/.config/himalaya/config.toml` with Gmail-specific folder aliases (`[Gmail]/Sent Mail`, etc.).

**Manual run (imaplib — no himalaya dependency):**
```bash
python3 -u /home/habib/.hermes/scripts/gmail_ingestor_imaplib.py
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

**⚠️ Himalaya is deprecated for email reading.** `auth.cmd = "echo <REDACTED-SUPABASE-CREDENTIAL-ROTATE-ME>"` fails in the Hermes sandbox with `No child process (os error 10)`. Use the imaplib-based `gmail_ingestor_imaplib.py` script instead. See `pluto-gmail-signal-ingestion` skill.

**Credentials location:** `GOOGLE_GMAIL_APP_PASSWORD_MACARTHUR` in `/mnt/c/Users/habib/.hermes/.env` (Windows side). The himalaya config uses `auth.cmd = "echo <REDACTED-SUPABASE-CREDENTIAL-ROTATE-ME>"` — not ideal for production but functional for WSL.

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
   Check what infrastructure the user already runs: AWS resources (EC2, SES, S3, CloudWatch, RDS), Cloudflare (DNS, R2, Workers). Note: Vercel and Fly.io were retired Aug 2026 — the fleet moved to AWS. A tool that runs on their existing infra is better than one that needs new accounts, new billing, and new vendor management. **Cloudflare Workers + R2 in particular** — the user already has Cloudflare DNS and R2 buckets provisioned. Worker-based solutions (click trackers, redirectors, API gateways) cost $0 to start on the existing plan.

3. **Check current-date capabilities, not last-known.**
   The user explicitly flags stale data ("we have GPT-5.5 now, not GPT-4"). Before comparing tools, LOOK UP their current feature sets from their official sites — do not rely on cached knowledge more than 30 days old. For AI models: check what's included in the user's existing subscription tier, not just the headline model name. Many models (Veo 3.1, Sora, Imagen 3) may be bundled into subscriptions the user already has.

4. **Count total cost correctly.**
   When presenting options, show the TOTAL new cost — not just the price of the new tool. Frame as: "You already have X (paid), Y (paid), and Z (credits). The only gap is [specific gap]. Here's the minimum spend to fill it." Prefer a stacked recommendation (use what you have + one affordable add-on) over a suite of new tools.

**Pitfall — defaulting to "buy new" when the user already has everything:** In July 2026 this user had Gemini Advanced (Veo 3.1 video gen + Imagen 3 images), ChatGPT Plus (Sora video + GPT-5.5 scripting + TTS), ChatGPT Team (more Sora), and ElevenLabs credits (voice). A first-pass recommendation of BytePlus (which would need a new paid subscription, sales call, and China data compliance review) was wrong — the correct answer was "you already have Veo 3.1 in Gemini Advanced, try that first."

**Pitfall — forgetting existing infrastructure:** After fixing the tool recommendation, the user also had Cloudflare (DNS, R2, Workers) and AWS SES already provisioned. A click tracker that runs on Cloudflare Workers ($0 extra, uses existing infra) is better than any third-party tracking SaaS that needs a new account and billing arrangement.

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

**Generator hardening — consolidated rules 1–30** (full defect log, per-item fix detail and
assertions: `references/linkedin-generator-defects.md`). Read that reference before changing
`linkedin_ideas_generator.py`: it holds the `KNOWN_BLOGS` gap-check/rotation rules, the
`BLOG_CANDIDATES` coverage requirement, the pillar-resolution order, the hook/angle boundary
and hook-stat gates, the grounding gates, and the CTA-dedupe rules. The list was condensed
here to keep SKILL.md under the 100K limit.

**Review before delivering:** the engine's angle/CTA are still mechanical — read the output, rewrite the hooks in Haris's voice, and append a `# ✅ Curated by Pluto` section to the day's file. Deliver the curated set.

**Rules 24–46 (Sep 22 – Oct 11 2026) — condensed; full defect log + regression harnesses in `references/linkedin-generator-defects.md`:** blog picks need ONE FRESH GROUNDED candidate per slot — count the pool the matcher USES (`_fresh()` also excludes every `KNOWN_BLOGS` key, so each published post permanently removes a candidate from its pillar); a repeat loses to a fresh candidate (10-day `_repeat`) and must not take a leftover slot while ≥2 fresh exist; candidates must be SUBJECT-bound with countable title claims; hook gates (`_DANGLE_VERBS`, no bare quantity after a scaffolding pop, no split proper noun or bare initialism); CTAs dedupe via a day-level `seen` (fingerprint ≥0.4); punctuation-stripping helpers need `_ensure_terminal()`; an external command must degrade, not kill the run. Verify hook changes with the before/after harness (0 regressions) plus a blog-candidate replay.

**Rule 44 (Oct 8 2026) — detail in `references/linkedin-generator-defects.md`:** the subordinate-tail cut in `_short_title` runs BEFORE the scaffolding pops, so a trailing weak token hides the tail from the bounded `{1,3}` regex and the hook ships mid-clause — re-apply it after the pops, widened to 6 tokens, gated on the tail carrying NO finite verb. General rule: a rule that runs before another that MODIFIES the string must be re-evaluated after it. An idea can also fire on a publication NAME in a finding's content — print the exact keyword that fired and read its context.

**Rule 46 (Oct 11 2026) — detail in `references/linkedin-generator-defects.md`:** a stat clause that is itself a full sentence makes the `stat: title` join restate one fact twice — the overlap ratio is diluted by stat length and Rule 34's de-parenthesised numeric check misses the title's own figure sitting inside the stat's parenthetical (AirTrunk shipped a 141-char doubled hook). Reject the stat when the JOIN length exceeds 130 chars; title-only is always a complete claim. Gate on the artefact the reader sees, not on a proxy that degrades as the stat grows.

**Rule 45 (Oct 9 2026) — detail in `references/linkedin-generator-defects.md`:** a returning 5-day-cycle topic whose LIVE pool is short pads the slate with verbatim repeats. On Startup & VC (same `date%5` slot as 4 Oct) the Startup & ESOP pool had only two live entries, both shipped five days earlier, so two of three ideas repeated while the day's biggest new signals (Diraq/DARPA, Breaker/Rheinmetall, Metal's stablecoin seed) had no candidate. Count the pool the matcher USES (`day_pillars` ∩ `_fresh`) when a topic returns and the slate looks familiar; add fresh subject-bound candidates, never loosen the gate. Keep every 5-day-cycle topic at ≥1 fresh grounded candidate per slot.

See `references/linkedin-content-extraction.md` for content pillar details and `references/gmail-briefing-integration.md` for Gmail signal sourcing.

### Phase 8b: AMLHive Content-Ideas Cron — dedupe and re-feed rules (Sep 14, 2026)

The 5:45 AM AMLHive content-ideas cron writes three files: `research_outputs/content-ideas-YYYY-MM-DD.md`, an appended section in `research_outputs/morning-briefing-YYYY-MM-DD.md`, and `mempalace-inputs/content-ideas-YYYY-MM-DD.md` (watcher feeds it to the `fintech-aml` chamber).

- **Identify each `inbox_*.json` by its own `topic` field — do NOT assume `inbox_*.json` means Perplexity (Sep 21 2026).** The 05:00 inbox dumps are one file PER CHANNEL: on Sep 21 the two files were `topic: "Genspark Briefing: …"` and `topic: "Claude Daily Research: …"`, with no Perplexity-topic file at all. Read every `inbox_<date>*.json` (not just `ls -t | head -1`) and report the source inventory from those `topic` strings; declaring a source "present" from the filename alone misreports provenance to Haris.
- **Check the last 7 days of ideas before shortlisting — two sources, not one.** The `content-ideas-*.md` files use inconsistent heading formats across days (some `### 1. Title`, older `# 1. Title` under a "Full idea list" heading), so a single heading regex misses titles. Also query the chamber itself: the watcher-fed docs in `fintech-aml` (metadata `topic: AMLHive Content Ideas — <date>`) are the authoritative record of what was already proposed. Reusing an angle from 3 days earlier is the most common failure of this cron.
- **Keep the mempalace input file to idea headings only — a trailing `## Section` is parsed as a finding (Sep 26 2026).** The watcher accepts any `##` block as a finding, so a metadata section such as `## Shortlist (top 3 delivered to the briefing)` or a dedupe note gets stored too and the chamber count comes back one higher than the idea count (observed: 6 ideas → 7 docs, ids `pluto_<YYYYMMDD>_<HHMMSS>_6`). Put slate metadata in the `research_outputs/content-ideas-<date>.md` file only, then after feeding assert the per-topic doc count and unique-text count both equal the number of ideas and `col.delete(ids=[...])` any extra id.
- **Re-feeding a corrected file requires deleting the previous docs.** The watcher's `.processed/<stem>.done` marker stops reprocessing, and removing only the marker re-feeds the file — but the FIRST feed's docs stay in the chamber, leaving duplicates. After rewriting an input file that was already fed: (1) `col.delete(ids=...)` the stale docs, (2) remove the `.done` marker, (3) re-run `mempalace_watcher.py --file <path>`, (4) dedupe the chamber by exact document text under that day's `topic` and assert the count equals the number of findings.
- **`where_document={"$contains": ...}` searches document text, not metadata** — filtering on a `Source:`/`url` substring silently returns 0. Filter by metadata (`where={"topic": ...}`) instead. **And `$contains` on a metadata FIELD is also unsupported/returns 0** (verified 2026-10-04 on chromadb 1.x: `col.get(where={"topic": {"$contains": "AMLHive Content Ideas"}})` returned 0 docs against a 314-doc `fintech-aml` collection holding 6 matching docs) — an unfiltered `col.get(include=["documents","metadatas"])` plus a Python substring scan over the metadatas is the reliable dedupe read, and a bare `0` from a `$contains` metadata filter is a failed check to re-run, never a real "nothing stored".
- **The content-ideas input file's `tags:` line decides its chamber — keep AMLHive vocabulary there, not the day's research topic (Sep 18 2026).** Tagging the input file with the day's research tags (`agentic-ai`, `agent-security`, `red-teaming`) makes `route_to_chamber()` send the whole idea set to `agentic-security`, so the ideas disappear from `fintech-aml` and the next day's dedupe query (which greps `fintech-aml` for `topic: AMLHive Content Ideas — <date>`) sees nothing. **Sep 30 2026:** file-level tags come from the LAST `Tags:` line only, so put AMLHive vocabulary on EVERY finding and read back `fintech-aml` by topic to confirm routing. Scope tags to `amlhive, content-ideas, real-estate, tranche-2, fintech, compliance` regardless of the research topic. To correct a mis-routed day: `col.delete(ids=...)` the wrong-chamber docs, fix the tags line, remove `.processed/<stem>.done`, re-run `mempalace_watcher.py --file <path>`, then assert the docs exist in `fintech-aml` and NOT in the research chamber (the watcher has no `--chamber` flag — routing is purely tag-driven).
- **`mempalace_watcher.py --file` resolves RELATIVE TO `mempalace-inputs/` — pass the bare filename (Oct 9 2026).** `--file mempalace-inputs/content-ideas-<date>.md` (run from `~/.hermes`) prints `❌ File not found: /home/habib/.hermes/mempalace-inputs/mempalace-inputs/...` and feeds nothing, while the read-back check (which correctly reports 0 docs) makes it look like a routing/sidecar failure rather than a path bug. Correct form: `scripts/mempalace_watcher.py --file content-ideas-<date>.md`. Always confirm `"status": "processed"` with `fed` == finding count before believing the ideas landed.
- **Mirror the previous day's input-file HEADING CONVENTION, not just its tags.** Use `## [AMLHive Content Idea] <title>` (one `##` per idea) — matching the prior file makes the chamber dedupe-by-title query (previous bullet) reliable across days, and the watcher's plain `## Finding` fallback drops the convention prefix otherwise. Confirm the file parsed by running `mempalace_watcher.py --file <path>` before finishing; expect `"fed": N, "status": "processed"`.
- **`Source:` lines become the ChromaDB `url` field.** For ideas with no verifiable external article, use `Source: internal://pluto/content-ideas/<date> (provenance)` rather than a descriptive sentence or a guessed URL — never invent a publisher URL.
- **When the day's signals carry NO direct AML/AUSTRAC item, derive ideas from the three adjacent signal classes instead of reaching for the same regulator story (Sep 24 2026).** That day's Genspark brief had zero AUSTRAC/Tranche-2/enforcement lines and the day's research topic was Startup & VC, yet three non-repeating ideas still came out of: (a) a **sector breach that exposes the exact documents collected at CDD** (Quest Apartment Hotels: 1,991,613 customers told to reissue passports and replace licences) → verifying an identity, not a document; (b) a **policy thread that will cite that breach** (Privacy Act reform / Digital Duty of Care) → the 7-year retention vs data-minimisation question; (c) a **macro/credit shift that changes how funds arrive** (RBA 29 Sep hike ~86-91% priced) → deposit bonds and guarantees are not cash, so what evidences source of funds. Each still maps to a real estate principal's search intent, so the idea set stays AMLHive-native without inventing a regulator development. Check the last 7 days of `content-ideas-*.md` first — the adjacent-class framing is what keeps a signal-poor day from recycling an angle already used.

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
password = os.environ["GOOGLE_GMAIL_APP_PASSWORD_MACARTHUR"]
for to in ['hhsiddiqui@gmail.com', 'admin@harishabib.au']:
    send_email(to, subject, body, password)
```

**Gmail app password:** read from `GOOGLE_GMAIL_APP_PASSWORD_MACARTHUR` (env store: `/mnt/c/Users/habib/.hermes/.env` on Windows). The local himalaya config holds a copy as `auth.cmd = "echo $$GOOGLE_GMAIL_APP_PASSWORD_MACARTHUR"`; update BOTH when rotating. Never print the value.

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
**⚠️ `portfolio_hit` shape is consumed by two different normalizers:** the research JSON schema below emits `portfolio_hit` as a **STRING** (`"portfolio_hit": "FinAI File AU"`), but `briefing_improver.py`'s podcast path emits a **LIST** of dicts/strings. Any consumer must handle BOTH shapes — `score_project_heat()` did not (list-only) and silently dropped all research findings from the Portfolio Pulse heatmap until 2026-09-13. Prefer emitting the string form that the schema specifies and let consumers normalize; do NOT switch to a list here without checking every consumer.

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

Moved to `references/pitfalls-full.md` (2026-10-11) to keep this file under the 100,000-char ceiling.
Full catalogue: watcher/feeder format + dedup defects, Supabase URL parsing (`==`, `pgbouncer=true`),
YouTube transcript/handle discovery, competitor-intel false positives, and the daily-run failure modes.
Load it before debugging the morning pipeline or the mempalace sync path.

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
- `references/daily-run-pitfalls.md` — Operational daily-run pitfalls: the day-of-month % 5 topic rule, the unsatisfiable `write_file` stale guard on long-line files, chamber read-back verification, producer-side `.findings.json` contract failures.
- `references/pitfalls-full.md` — The full pitfalls catalogue extracted from SKILL.md 2026-10-11 (watcher/feeder format + dedup defects, Supabase URL parsing, YouTube transcript/handle discovery, competitor-intel false positives). Read this one for history; `daily-run-pitfalls.md` holds the current run-time rules.
- `references/linkedin-generator-defects.md` — Full defect log for `linkedin_ideas_generator.py` (rules 1–23): blog gap-check/rotation, pillar resolution, hook/angle boundary rules, stat-clause gates, quote balancing, the pillar gate on matched blog candidates, and the file-level verification recipes. Load before modifying the generator; SKILL.md holds the condensed rules.