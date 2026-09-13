# RSS Research Extraction Patterns

Detailed Phase 1 research patterns beyond the preferred Google News RSS
Direct Pipeline documented in `SKILL.md` — legacy feed discovery, broad
discovery via Google News RSS, minified-XML extraction options, the
multi-angle parallel pattern, and the subprocess/execute_code pitfalls
that motivate the preferred pipeline.

## Contents

- [Legacy: RSS Feed Discovery Pipeline](#legacy-rss-feed-discovery-pipeline)
- [Complementary: Google News RSS for broad discovery](#complementary-google-news-rss-for-broad-discovery)
- [Google News RSS minified XML extraction](#google-news-rss-minified-xml-extraction)
- [Multi-angle parallel feed pattern](#multi-angle-parallel-feed-pattern)
- [subprocess.run pitfall in execute_code](#subprocessrun-pitfall-in-execute_code)
- [Recommended execute_code pattern](#recommended-execute_code-pattern)
- [Confidence-tiering based on source depth](#confidence-tiering-based-on-source-depth)
- [Fallback: delegate_task](#fallback-delegate_task)

## Legacy: RSS Feed Discovery Pipeline

(use for deep-dive on specific articles)

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

## Complementary: Google News RSS for broad discovery

(use alongside or in place of delegate_task)

Google News RSS search provides excellent discovery across regions and topics — 62-100 results per query, no delegation, no CAPTCHAs:
```bash
curl -sL --max-time 15 -A "Mozilla/5.0" \
  "https://news.google.com/rss/search?q=TOPIC+QUERY&hl=en-US&gl=US&ceid=US:en"
```
Parse with the same `re.findall(r'<item>(.*?)</item>', ...)` pattern. Headlines and source attribution are reliable; article links (`news.google.com/rss/articles/...`) redirect to publishers and CANNOT be fetched via curl (see Pitfalls). Use Google News for discovery + headline synthesis, then fetch confirming articles from direct publication RSS feeds when possible.

## Google News RSS minified XML extraction

Google News RSS is minified XML — all content is on a single line (70-95KB). `read_file` with line limits will miss content. Two extraction approaches:

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

## Multi-angle parallel feed pattern

(recommended) Fire 4-6 Google News RSS queries simultaneously, each targeting a different subtopic angle. This yields 300+ headlines in ~15 seconds with zero delegation failures:
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

## subprocess.run pitfall in execute_code

**CRITICAL: Do NOT use `subprocess.run(["curl", ...])` inside `execute_code` for Google News RSS** — it silently returns 0 results even with correct URLs, User-Agent, and timeout settings. As of May 31, 2026, 6/6 subprocess-run queries returned 0 items from Google News RSS. The same curl commands run directly via `terminal()` return full feeds (10+ items each). Root cause unidentified — likely curl binary path, library resolution, or environment differences between the subprocess and terminal environments.

## Recommended execute_code pattern

(avoids both shell-escaping and subprocess issues)
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

## Confidence-tiering based on source depth

- **high** = you fetched and read the full article content yourself (curl → file → parse)
- **medium** = credible publication (NYT, Fortune, IAPP, Lawfare, SCMP, InnovationAus) — headline confirmed via RSS but content behind paywall or unfetchable
- **low** = speculation, aggregated second-hand reports, single-source without verification

## Fallback: delegate_task

(when RSS feeds don't cover the topic)

Use `delegate_task` with `toolsets: ["web", "search"]` to research multiple angles in parallel (up to 3 subagents concurrently). **WARNING:** As of May 25, 2026, 6/6 subagents returned empty `tool_trace` despite explicit instructions. If the first batch all fail, do NOT retry — switch to RSS or direct curl approach immediately. Give each subagent a specific angle, provide rich context, and always cross-check URLs since subagent summaries are self-reports.

See `references/delegation-pattern.md` for proven subagent prompt templates and failure patterns.
