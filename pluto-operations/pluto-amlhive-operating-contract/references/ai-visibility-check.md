# AI-Answer Visibility Check Pattern

Use this when the user asks why AMLHive isn't appearing in AI/search results, or wants to compare visibility against competitors.

## Quick Check (5 min)

### 1. Public Search — Who appears for target queries?
Run DuckDuckGo searches for priority queries. Extract competitor URLs from organic results.

Key queries for AMLHive:
- `"AML Tranche 2 compliance software Australia"` — AMLHive's core market
- `"real estate AML compliance Australia"` — key vertical
- `"AUSTRAC reporting entity compliance platform"` — regulatory intent
- `"AML compliance platform Australia"` — broad category

### 2. Check AMLHive sitemap freshness
```bash
curl -s https://amlhive.com.au/sitemap.xml | head -20
```
Confirm HTTP 200, valid XML, current lastModified dates.

### 3. Check for entity conflation
Search `"AMLHive"` + competitor names to see if AI systems merge AMLHive with other companies. Red flags:
- AMLHive described as AUSTRAC-affiliated
- Merged with another company
- Priced like a competitor
- Called a legal adviser or automatic lodgement provider

## Full Audit (Weekly AI-Answer Review — Wed 10:30)

When running the controlled prompt set, record per engine:

| Metric | Values | Meaning |
|--------|--------|---------|
| found | yes/no | The engine found AMLHive or its actual product |
| conflated | no/yes + entity | It merged AMLHive with another organisation |
| facts_correct | yes/no + errors | Controlled product/entity facts were accurate |

Engines to check: ChatGPT, Gemini, Claude, Perplexity, Copilot, Google AI features.

## What to Do When AMLHive Is Not Found

1. **Check delivery** — Is the page HTTP 200? (Daily Discovery Health covers this)
2. **Check index coverage** — Google Search Console / Bing Webmaster Tools when authorised
3. **Check content relevance** — Does the page answer the actual query intent?
4. **Check sitemap** — Is the URL included with correct lastModified?
5. **Check internal links** — Is there a crawlable path from the homepage?
6. **Check competition** — Who IS ranking? What do they do better? (title, meta, content structure, backlinks)

## Escalation

If AI engines fabricate facts about AMLHive (e.g., calling it AUSTRAC-approved, merging with competitor, wrong pricing):
- Record the exact prompt + response + engine + date
- This is an immediate `HUMAN_DECISION_REQUIRED` finding
- Pluto prepares correction evidence
- A human submits provider feedback or profile corrections
