# web_search → web_extract Enrichment Pattern

## Why This Exists

Google News RSS is the primary discovery pipeline but its article links (`news.google.com/rss/articles/...`) return HTTP 400 when curled. The `web_search` tool (once thought unavailable) bridges this gap — it discovers the same articles on publishers' own domains, and `web_extract` pulls full content even from JS-rendered pages that curl returns empty.

## Validated Session: June 17, 2026

**Topic:** Agentic AI & Security  
**RSS discovery:** 330 articles from 170 sources across 5 Google News RSS queries  
**Enrichment pattern applied:** 4 `web_search` calls + 4 `web_extract` calls

### Results (4/4 success)

| Search Query | web_search Hit | web_extract Content | Quality |
|---|---|---|---|
| "Microsoft agentic AI failure modes taxonomy red teaming 2026" | theweatherreport.ai | Full article: 7 new failure modes, 34 total, table with safety/security breakdown, "My take" analysis | ✅ Rich |
| "Singapore Model AI Governance Framework agentic AI 2026" | mddi.gov.sg | Official press release: 4 dimensions, WEF Davos announcement, quotes, links | ✅ Authoritative |
| "IBM cybersecurity agentic attacks enterprise 2026" | fierce-network.com | Full newswire: assessment details, frontier model threats, IBM Consulting offering | ✅ Rich |
| "agentic AI security governance 2026 data risks" | elevateconsult.com | Full report: statistics, attack vectors, regulatory enforcement, platform controls | ✅ Rich |

### Key Insight

Every `web_extract` call succeeded — this is significantly better than the ~15% curl success rate documented in the RSS pipeline pitfalls. `web_extract` handles JS-rendered publishers (theweatherreport.ai, elevateconsult.com) that would return empty via curl.

## Pattern

```
Phase 1a: Google News RSS (5 queries) → 300+ headlines, 150+ sources
Phase 1b: Pick 2-4 top headlines → web_search(article title + publisher)
Phase 1c: web_extract(discovered URLs) → rich verified content
Phase 2: Synthesize with both RSS headlines + extracted content
```

## When to Apply

- **Apply:** When a headline group represents a highly credible signal (3+ publications) and deeper content would elevate it to HIGH confidence
- **Skip:** When RSS headline synthesis alone provides enough signal for medium-confidence tiering
- **Skip:** When the topic is low-priority and 1-2 RSS headlines are sufficient

## Confidence Boost

Findings enriched via this pattern automatically qualify for `high` confidence since you've read the full article content (matching the original confidence-tiering rule: "high = you fetched and read the full article content yourself").
