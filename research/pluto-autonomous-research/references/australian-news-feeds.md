# News Feed Catalog — Australian & Global Sources

Proven RSS/feed URLs that return real content (verified May 25-28, 2026). All respond to simple `curl` with `-A "Mozilla/5.0"` user agent.

## Australian Startup & Tech

| Source | Feed URL | Type | Notes |
|--------|----------|------|-------|
| StartupDaily | `https://www.startupdaily.net/feed/` | Startup funding/ecosystem | Covers ANZ startups, funding rounds, VC deals. Full articles accessible. |
| InnovationAus | `https://www.innovationaus.com/feed/` | Tech policy/industry | Deep coverage of Australian tech policy, defense tech, R&D. Some articles paywalled (InnovationAus subscriber wall). |
| SmartCompany | `https://www.smartcompany.com.au/feed/` | SME/business/tax | Strong coverage of budget policy, SME regulation, CGT reform. **Metered paywall** — articles return excerpt (~1000 chars) server-side; full body only for subscribers. Still useful for headline + excerpt synthesis. Use `entry-content wp-block-post-content` selector. |
| TechCrunch Australia | `https://techcrunch.com/tag/australia/feed/` | Global tech (AU filter) | Slower update cadence for AU-specific content. Good for big stories. |

## Fintech

| Source | Feed URL | Type | Notes |
|--------|----------|------|-------|
| Finextra | `https://www.finextra.com/rss/headlines.aspx` | Global fintech | Daily global fintech headlines. Good for international deals and agentic AI in finance. |

For Australian fintech coverage, use Google News RSS queries (see `references/google-news-rss-patterns.md`) or Finextra filtered for AU stories.

## Global Security & Tech Feeds

These feeds cover international security, AI, and technology stories. Use for topics that span beyond Australian sources.

| Source | Feed URL | Type | Notes |
|--------|----------|------|-------|
| WIRED Security | `https://www.wired.com/feed/category/security/latest/rss` | Cybersecurity, AI security | ~20 articles per fetch. RSS gives exact article URLs (not redirects). Articles are ~1.3MB, full content accessible. Use `body__inner-container` selector for text extraction (see parsing section). |
| Information Age (ACS) | (no RSS — use Google News RSS discovery) | Australian tech/IT | Published by Australian Computer Society. Full articles accessible via curl (~35KB). Covers Australian AI/security incidents. Example: PocketOS AI agent incident. |

## Publisher-Specific Parsing Selectors

When the generic `<article>` tag parser returns empty or minimal content, try these publisher-specific selectors first:

| Publisher | Selector | Fallback |
|-----------|----------|----------|
| WIRED | `<div class="body__inner-container">` | Falls through to body |
| The Register | `&lt;div id="article_body"&gt;` | Try `&lt;div class="article-body"&gt;` |
| SmartCompany | `entry-content wp-block-post-content` div | Metered — excerpt only (~1000 chars) |
| Generic (default) | `&lt;article&gt;` → `&lt;main&gt;` → `&lt;body&gt;` | See parsing code below |

## Dead / Unreliable Feeds

| Source | Feed URL | Reason |
|--------|----------|--------|
| AFR Technology | `https://www.afr.com/rss/technology` | Returns 18 bytes (empty) |
| Australian Fintech | `https://www.australianfintech.com.au/feed/` | Returns 0 bytes (empty, May 29 2026) |
| Capital Brief | `https://www.capitalbrief.com/feed` | Returns 0 bytes |
| Feedburner Fintech | `https://feeds.feedburner.com/fintechnewsau` | Returns 1.6KB (minimal, no content) |

## Parsing Pattern

```python
import re

items = re.findall(r'<item>(.*?)</item>', rss, re.DOTALL)
for item in items:
    title = re.search(r'<title>(?:<!\[CDATA\[)?(.*?)(?:\]\]>)?</title>', item, re.DOTALL)
    link  = re.search(r'<link>(.*?)</link>', item, re.DOTALL)
    date  = re.search(r'<pubDate>(.*?)</pubDate>', item, re.DOTALL)
    desc  = re.search(r'<description>(?:<!\[CDATA\[)?(.*?)(?:\]\]>)?</description>', item, re.DOTALL)
```

## Article Fetching & Text Extraction

```bash
# Download (do NOT pipe through inline python — escaping breaks)
curl -sL --max-time 20 -A "Mozilla/5.0" -o /tmp/article.html "URL"
```

```python
# Parse in Python
import re

with open('/tmp/article.html', 'r', encoding='utf-8', errors='replace') as f:
    html = f.read()

# Strip scripts, styles
html = re.sub(r'<script[^>]*>.*?</script>', ' ', html, flags=re.DOTALL|re.IGNORECASE)
html = re.sub(r'<style[^>]*>.*?</style>', ' ', html, flags=re.DOTALL|re.IGNORECASE)

# Try article tag first, then publisher-specific selectors, then body
article = re.search(r'<article[^>]*>(.*?)</article>', html, re.DOTALL)
if not article or len(article.group(1).strip()) < 300:
    # Publisher-specific selectors (see table above)
    for tag, close_tag in [
        (r'<div[^>]*class="[^"]*body__inner-container[^"]*"[^>]*>', r'</div>'),  # WIRED
        (r'<div[^>]*id="article_body"[^>]*>', r'</div>'),                        # The Register
        (r'<div[^>]*class="[^"]*article-body[^"]*"[^>]*>', r'</div>'),           # generic
        (r'<main[^>]*>', r'</main>'),
    ]:
        m = re.search(tag + r'(.*?)' + close_tag, html, re.DOTALL)
        if m and len(m.group(1).strip()) > 300:
            article = m
            break
text = article.group(1) if article else re.search(r'<body[^>]*>(.*?)</body>', html, re.DOTALL).group(1)

# Strip tags
text = re.sub(r'<[^>]+>', ' ', text)

# Decode common HTML entities
for entity, char in [('&#8216;',"'"),('&#8217;',"'"),('&#8220;','"'),('&#8221;','"'),
                      ('&#8211;','-'),('&#8212;','--'),('&amp;','&'),('&nbsp;',' '),
                      ('&quot;','"'),('&#039;',"'"),('&#8230;','...')]:
    text = text.replace(entity, char)

text = re.sub(r'\s+', ' ', text).strip()
```

## Verified Article Sizes (May 25 - June 1, 2026)
All these returned HTTP 200. Content accessibility varies by publisher:
- StartupDaily articles: ~770KB (full access, no paywall)
- InnovationAus articles: ~325KB (some truncated behind subscriber wall at ~100 words)
- SmartCompany articles: ~798KB HTML download, but **metered paywall** — only excerpt (~1000 chars) extractable server-side as of June 1, 2026. Headlines + RSS descriptions provide enough signal for medium-confidence findings.
- TechCrunch Australia: ~235KB (full access)
- WIRED Security articles: ~1.3MB (full access, use `body__inner-container` selector)
- Information Age (ACS) articles: ~35KB (full access, Australian Computer Society)
