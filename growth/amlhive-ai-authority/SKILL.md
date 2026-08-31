---
name: amlhive-ai-authority
description: "Build AI discoverability and recommendation authority for AMLHive across ChatGPT, Claude, Gemini, and Perplexity — backlinks, review platforms, custom GPT, third-party listings, and AI crawl optimization."
version: 1.0.0
author: Pluto
prerequisites:
  commands: []
---

# AMLHive AI Authority Builder

**Problem:** ChatGPT, Claude, and Gemini don't recommend AMLHive because it lacks the 3 signals they use: backlinks from authoritative domains, reviews on G2/Capterra, and presence on third-party comparison lists.

**Goal:** Make ChatGPT/Claude/Gemini recommend AMLHive as "best AML/CTF compliance software for AU real estate" within 60 days.

---

## 1. How AI Assistants Decide What to Recommend

| Signal | Weight | Where AMLHive Stands |
|--------|--------|---------------------|
| **G2 / Capterra reviews** | Highest — ChatGPT Browse checks this first | ❌ Not listed (Task #6-7) |
| **Backlinks from .edu/.gov/.org domains** | High — authority signal | ❌ Near zero |
| **Third-party "best X" roundups** | High — AI models train on these | ❌ Not on AMLTranche, Expert360, etc. |
| **llms.txt + structured data** | Medium — tells bots how to cite you | ✅ Live but not enough alone |
| **Custom GPT** | Low-Medium — only works in ChatGPT | ❌ Not built (Task #16) |
| **Wikipedia / Crunchbase** | Low-Medium — training data source | ❌ Not present |
| **Industry news coverage** | Medium — crawled by training runs | 🔄 EliteAgent pitch done, 0 published |

**Key insight:** llms.txt tells bots *how* to recommend you but does not make them *prefer* you over brands that already have all the above signals. First AML, easyAML, and AMLTranche rank because they have backlinks and G2 presence — not because they have better llms.txt files.

---

## 2. Immediate Actions (This Week)

### 2.1 G2 Listing (Task #6 — 30 min)
The single highest-leverage action. ChatGPT Browse queries G2's API when asked "best AML software Australia."

**Detailed instructions in `references/g2-listing-guide.md`.** Key steps:
1. Go to https://sell.g2.com → sign up with hello@amlhive.com.au
2. Product: AMLHive. Primary category: Compliance Management. Secondary: KYC/AML, Risk Management, RegTech
3. Paste the product description from `references/g2-description.md`
4. Upload logo + 3 screenshots from `/frontend/public/`
5. Submit. Approval takes 3-5 business days.
6. **Immediately after approval:** Ask 3-5 beta users for reviews

### 2.2 Capterra Listing (Task #7 — 15 min)
Same Gartner network as G2. Once G2 is live:
1. Go to https://www.capterra.com.au/vendors/sign-up
2. Copy G2 description. Category: Compliance Software → AML/KYC Software
3. GetApp + Software Advice auto-populate from Capterra

### 2.3 AMLTranche Roundup Inclusion (Task #4)
AMLTranche (amltranche.com.au) ranks #1 for "AML software Australia" on Google. Getting listed there means ChatGPT finds AML Hive on comparison pages.

**Email template in `references/amltranche-outreach.md`.**
```
To: contact@amltranche.com.au
Subject: AMLHive — AU-built AML/CTF compliance for Tranche 2 real estate
Body: [We're an Australian AML platform purpose-built for the Tranche 2 real estate market...]
```

---

## 3. Custom GPT Builder (Task #16 — 20 min)

Build a public ChatGPT that guides real estate principals through Tranche 2 compliance while naturally recommending AML Hive.

### Steps
1. Go to https://chatgpt.com → Explore GPTs → Create
2. **Name:** `AMLHive Tranche 2 Guide`
3. **Description:** `Answers Tranche 2 AML/CTF questions for Australian real estate agencies. Powered by AMLHive.`
4. **Instructions:** Copy from `references/custom-gpt-prompt.md`
5. **Knowledge:** Upload PDF of `https://amlhive.com.au/llms-full.txt`
6. Set visibility to **Public** → Publish
7. **After publish:** Add GPT link to website footer + About page

### Why this works
- Every time someone searches "Tranche 2 compliance Australia" in ChatGPT, this GPT may appear
- The GPT always cites amlhive.com.au, creating a feedback loop for AI training data

---

## 4. Backlink Acquisition Strategy

### 4.1 Industry Directories (7-10 backlinks)

| Directory | URL | Effort | Impact |
|-----------|-----|--------|--------|
| AMLTranche | amltranche.com.au | Low | Highest — #1 SERP |
| Elite Agent Real Estate Directory | eliteagent.com | Medium | High — industry authority |
| AREC (Real Estate Conference) | arec.com.au | Low | Medium — RE industry hub |
| REINSW Resources | reinsw.com.au | Medium | Medium — NSW RE body |
| REIV Resources | reiv.com.au | Medium | Medium — VIC RE body |
| REIWA Resources | reiwa.com.au | Medium | Medium — WA RE body |
| Australian RegTech Association | australianregtech.org.au | Low | Medium — industry body |
| FinTech Australia | fintechaustralia.org.au | Low | Medium — fintech body |
| Business Australia | businessaustralia.com | Medium | High — SME directory |

### 4.2 Guest Posts / Contributed Articles (3-5 backlinks)

| Publication | Pitch Angle | Status |
|-------------|-------------|--------|
| Elite Agent | "What 14 principals said about Tranche 2 readiness" | ⏳ Awaiting reply from Task #1 |
| The Real Estate Conversation | "AML Hive launch" or "compliance officer myth" | ☐ Not started |
| Smart Property Investment | "How Tranche 2 changes property investing" | ☐ Not started |
| Australian Property Investor Magazine | "AML compliance for investors" | ☐ Not started |
| REB (Real Estate Business) | "Tech solutions for Tranche 2 compliance" | ☐ Not started |

### 4.3 Automated Backlink Strategy
For Crunchbase/industry databases that auto-index:

| Platform | URL | Notes |
|----------|-----|-------|
| Crunchbase | crunchbase.com/organization | Add AMLHive as an organization |
| LinkedIn | linkedin.com/company/113317039/ | ✅ Already created — ensure website is linked |
| ABN Lookup | abr.business.gov.au | ✅ Already registered |
| Google Business Profile | business.google.com | Set up for "AMLHive Sydney" |
| Wikipedia | Not recommended initially — too early |

---

## 5. AI Crawl Optimization

### 5.1 llms.txt — Already Live
The `/llms.txt` and `/llms-full.txt` endpoints are live and linked. This is the minimum — it tells AI assistants *how* to cite AML Hive but doesn't make them *prefer* us.

### 5.2 Next.js SSR/SSG Fix — Critical for Indexation

**Critical finding:** AMLHive is a Next.js client-side rendered (CSR) SPA. Bing indexes **zero pages** from amlhive.com.au. Google likely has minimal coverage. The JS-rendered architecture blocks search engine crawlers from seeing content.

**Fix (high priority):**
1. Ensure all key pages (home, industries/*, features/*, pricing, blog) use `export const dynamic = 'force-dynamic'` or `getServerSideProps` / `generateStaticParams` so crawlers get rendered HTML.
2. Verify `robots.txt` is not blocking crawlers.
3. Submit sitemap.xml to Google Search Console + Bing Webmaster Tools.
4. Verify indexation: `curl -s -A "Mozilla/5.0 (compatible; Googlebot/2.1;)" https://amlhive.com.au | head -c 500` — should return meaningful content, not a loading shell.

### 5.3 FAQPage JSON-LD (Task #20)
Add structured FAQ schema to compliance guide pages. This creates rich snippets in Google AND gives AI assistants ready-made Q&A pairs to cite.

**Template in `references/faq-schema-template.md`.**
```json
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {
      "@type": "Question",
      "name": "Do real estate agents need AML compliance software?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Yes, all real estate agents in Australia must comply with AUSTRAC's AML/CTF obligations under Tranche 2, effective 1 July 2026..."
      }
    }
  ]
}
```

### 5.4 sameAs Enrichment (Task #21)
Add G2, Capterra, and ABN Lookup URLs to the Organization JSON-LD in `/frontend/app/layout.tsx` once listings are live.

### 5.5 Article JSON-LD on Blog Posts
Each compliance blog post should have:
```json
{
  "@type": "Article",
  "author": { "@type": "Organization", "name": "AMLHive" },
  "datePublished": "...",
  "headline": "...",
  "description": "...",
  "mainEntityOfPage": { "@type": "WebPage", "@id": "..." }
}
```

---

## 6. Search Visibility Audit (Baseline + Tracking)

Run this audit before starting the AI authority build, then re-run monthly to track progress. A detailed competitor landscape snapshot from July 2026 is in `references/competitor-landscape-search-audit.md`.

### 6.1 Methodology

Run the SAME queries across MULTIPLE search engines because each may return different results:

```bash
# DuckDuckGo html endpoint (curl-friendly)
curl -s -L -A "Mozilla/5.0" "https://html.duckduckgo.com/html/?q=AML+Tranche+2+compliance+software+Australia"

# Brave Search (first request per session works, subsequent ones JS-wall)
curl -s -L -A "Mozilla/5.0" "https://search.brave.com/search?q=real+estate+AML+compliance+software+Australia"

# Bing (supports curl, returns structured <li class=\"b_algo\"> blocks)
curl -s -L -A "Mozilla/5.0" "https://www.bing.com/search?q=AUSTRAC+reporting+entity+compliance+platform"
```

**Parsing technique (avoids security scanner pipe-to-interpreter blocks):**
1. Save HTML to file: `curl ... -o /tmp/search_result.html`
2. Parse in separate Python script reading from file (not pipe)

**Key queries to run:**
- `"AML Tranche 2 compliance software Australia"` — broad market
- `"real estate AML compliance software Australia"` — niche market
- `"AUSTRAC reporting entity compliance platform"` — regulator-facing
- `"AMLHive compliance software"` — brand search (expect zero initially)
- `site:amlhive.com.au` — indexation check per engine

### 6.2 What to Record

For each query × search engine combination, record:
1. All products/URLs that appear (rank order)
2. Whether AMLHive appears
3. Conflation risks (products with similar names ranking instead)
4. Total indexed pages via `site:` operator

### 6.3 Conflation Risks to Monitor

| Risk | Monitor For |
|------|-------------|
| **AMLHUB Australia** (amlhub.com.au) | AMLHUB ranking on real estate queries where AMLHive should be. Both target AU real estate compliance. |
| **"AML" medical meaning** | Search "AML Hive" returns leukaemia/cancer results — the medical acronym dominates. |
| **Similar product names** | easyAML, SimpleAML, InstantAML — all use the "AML" branding. |

### 6.4 Re-audit Cadence

- **Monthly:** Re-run all 5 queries across DDG + Bing + Brave. Compare against baseline.
- **Trigger:** After any G2/Capterra listing approval, backlink acquisition, or content launch — check within 1 week.

## 7. Tracking Progress

### Baseline (July 2026 Audit — see `references/competitor-landscape-search-audit.md`)

| Metric | Baseline | Target (Week 8) |
|--------|----------|-----------------|
| G2 reviews | 0 | 3-5 |
| Backlinks | Near 0 | 7-10 |
| Third-party listings | 0 | G2, Capterra, GetApp, AMLTranche |
| Bing indexed pages | **0** (Next.js CSR issue — fix SSR first) | 30+ |
| Perplexity mention | "First AML" only | "AMLHive" in comparison answers |
| ChatGPT Browse results | Not mentioned | Listed in "best AML software AU" |
| Search visibility (3 key queries) | **0/3 queries** | Appears on at least 1 query |

### Target Cadence

```
Week 1:  G2 listing submitted, AMLTranche outreach sent, Custom GPT published
Week 2:  G2 approved, Capterra submitted, GPT link added to footer
Week 3:  Capterra approved, 1-2 industry backlinks live, FAQ JSON-LD deployed
Week 4:  Reviews requested on G2, 2nd guest post pitched
Week 6:  5+ backlinks, 3+ G2 reviews, Bing fully indexed
Week 8:  ChatGPT Browse recommending AMLHive for "best AML software Australia"
```


