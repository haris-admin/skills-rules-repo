# AML Hive Content Workflow

> **Purpose:** Guide for creating content bundles (blog + LinkedIn + Facebook) for amlhive.com.au and AML Hive social channels. This is the SECOND content stream — completely separate from harishabib.au / Haris Habib personal brand.

## When to Use

- Haris asks for blog posts, LinkedIn posts, or social media content about AML compliance
- Content needs to be published on amlhive.com.au
- Alvina needs LinkedIn or Facebook content about AML/CTF, AUSTRAC, Tranche 2
- Stats or survey data about AML compliance need to be turned into content

## Content Stream Separation (CRITICAL)

| Stream | Channels | Author | Products Allowed | Products Forbidden |
|--------|----------|--------|------------------|-------------------|
| **Haris Habib** | harishabib.au, @harishabib LinkedIn | Haris Habib | None (pure thought leadership) | ALL personal products |
| **AML Hive** | amlhive.com.au, Alvina's LinkedIn/Facebook | Alvina / AML Hive | AML Hive | Only AML Hive is relevant |

**These streams NEVER cross:**
- No AML Hive content on harishabib.au
- No Haris Habib personal brand on amlhive.com.au
- No cross-linking between the two domains
- Alvina posts about AML Hive solutions; Haris posts about AI governance opinions

## Content Bundle Pattern

When a signal or stat warrants a content push, produce **three pieces** targeting different platforms:

### 1. Blog Post (amlhive.com.au) — Long Form

**Format:** Educational article, 800–1500 words

**Structure:**
- **Headline:** Problem-first with specific stat ("AUSTRAC Penalties Reach $X Per Breach — Is Your Firm Ready?")
- **Problem setup:** The penalty/regulatory reality (with verified stats)
- **Evidence:** Case examples, survey data, regulatory timelines
- **Toolkit/Checklist:** Actionable steps the reader can take
- **AML Hive solution:** How AML Hive addresses the problem (product features mapped to each pain point)
- **Cost comparison:** Table showing cost of non-compliance vs cost of solution
- **CTA:** Get started / Book a demo / Free consultation

**Tone:** Authoritative, educational, urgent but not alarmist (treats audience as professionals who need to act)

**File format:** Markdown with YAML frontmatter (if for website CMS) or standalone markdown

### 2. LinkedIn Post (Alvina) — Medium Form

**Format:** Professional thought leadership, ~1000–1200 characters

**Structure:**
- **Hook:** 1-2 sentence grabber with the specific data point
- **Angle:** 2-3 sentences connecting to the audience's experience/pain point
- **Quick list/insight:** 3-5 bullet points of key takeaways
- **Solution reference:** Gentle mention of AML Hive as an example of how to solve this
- **CTA:** Engagement question ("Is your firm ready?") or offer ("DM me for a compliance checklist")

**Tone:** Professional, knowledgeable insider — Alvina positions herself as someone who understands the regulatory landscape and can help

**No generic hashtag stuffing.** Use 5-8 targeted hashtags relevant to the specific topic.

**Post to:** Alvina's LinkedIn (not Haris's). If Haris is posting, use the harishabib.au firewall rules instead.

### 3. Facebook Post (Alvina) — Short Form

**Format:** Conversational alert, ~600–900 characters

**Structure:**
- **Opener:** Emoji + warning/call to attention
- **The stat/problem:** 1-2 sentences with the key number
- **What changed:** Quick explainer
- **The solution:** 1-2 sentences about how AML Hive helps
- **Engagement bait:** Comment prompt or reaction request

**Tone:** More conversational and urgent than LinkedIn. Speaks to small business owners and practitioners directly. Uses emojis strategically.

**Post to:** Alvina's Facebook (not Haris's).

## Claim Verification Pipeline (Run Before Writing Anything)

Every stat used in content must be verified — the AML/CTF space has rapidly changing numbers and dates.

### Step 1: Identify the claim
What exact numbers/dates need verification?
- Penalty amounts: Who sets them? What statute? What date?
- Survey data: Who ran it? When? What sample size?
- Regulatory deadlines: What regulation? What section? What timeline?

### Step 2: Cross-reference
Use multiple independent sources:

| Source Type | Examples | Trust Level |
|-------------|----------|-------------|
| Legal databases | ICLG, Austlii, government websites | ✅ Highest |
| Official regulators | AUSTRAC, ASIC, APRA, Treasury | ✅ Highest |
| Major news | AFR, ABC, SMH, The Australian | 🟡 Medium-High |
| Industry publications | PEXA Exchange, FinTech Global, LSJ | 🟡 Medium |
| Secondary reports | Blog posts, LinkedIn, Twitter | ❌ Low |

**Minimum verification:** 2 independent sources for any stat used in content.

### Step 3: Check for recency
- AML/CTF penalty units change annually (indexed to CPI)
- Survey dates: PEXA conducted surveys in June-August 2025, not 2026
- Regulatory deadlines shift: always check current legislation date

### Step 4: Flag caveats to the client
Before publishing, tell Haris:
- Where the number came from
- Any discrepancy found (e.g., "The PEXA survey was 2025, not 2026")
- Any alternative figure (e.g., "Statutory max is $33M, your figure says $22.2M")
- Let him decide on the final wording

### Step 5: Document your sources
Include a sources section in the blog post or keep a working doc for reference.

### ⚠️ Pipeline-Sourced Claims — Special Handling

Some claims come from Pluto's internal research pipeline rather than external articles:

- **Signal frequency counts** (e.g., "deadline appeared 44 times today") are aggregate keyword frequencies across the full document corpus — not 44 individual articles. There is NO single link to cite.
- **Cross-chamber signal counts** (e.g., "AUSTRAC mentioned 79 times") reflect market conversation volume, not article-level sources.

When Haris asks for links to these, say so directly — they're pipeline metrics, not article links. Offer the research JSON findings instead (~6 per cycle, each with named outlets).

### 🔴 Stale Data Rule — User Preference

Haris will scrap content rather than publish stale data. Directional correctness is NOT enough. If a survey is from 2025 and he expected 2026, the entire content bundle is shelved — no fudging dates.

**Checklist before writing:**
- Are the dates current (within 3 months)?
- If older: does the stat still hold true with new data?
- If uncertain: flag to Haris FIRST before writing anything
- Never write a full post around a stat you can't verify as current

## Real Example (June 11, 2026)

**Signal:** "Penalties reach AUD $22.2M per breach. 77% of agents say they are concerned or unprepared (PEXA survey, 2026)."

**Verification findings:**

| Claim | Found | Verdict |
|-------|-------|---------|
| $22.2M per breach | Actual max is $33M (100,000 penalty units × $330) | Close but understated — used both figures |
| 77% unprepared | 75% from realestatebusiness.com.au, June 2025 | Directionally correct, date was 2025 not 2026 |
| PEXA survey 2026 | Articles were June-August 2025 | Wrong year — flagged to Haris |

**Content produced:**
1. Blog: "AUSTRAC Penalties Reach $22.2M Per Breach — Is Your Firm Prepared?" (~4900 chars, educational)
2. LinkedIn: Professional post for Alvina (~1100 chars, thought-leadership style)
3. Facebook: Short conversational post (~900 chars, urgent tone with emojis)

## Quality Gates (MANDATORY)

- [ ] All stats verified against 2+ independent sources
- [ ] Penalty figures cite the correct statute (AML/CTF Act, not Criminal Code)
- [ ] Survey dates are accurate (not assumed from vague referencing)
- [ ] Blog post's solution section is helpful, not pushy
- [ ] LinkedIn post has NO direct sales language ("buy", "purchase", "get started")
- [ ] Facebook post is conversational but accurate
- [ ] Caveats flagged to Haris before publishing
- [ ] Two streams respected: no AML Hive on harishabib.au / no personal products on amlhive.com.au

## Platforms and Delivery

- **Blog:** amlhive.com.au CMS (check with Haris — may be direct CMS or markdown-based)
- **LinkedIn:** Alvina's personal LinkedIn profile
- **Facebook:** Alvina's personal or business Facebook page
- **Delivery format:** Save to `~/.hermes/research_outputs/` as `.md` files, then inform Haris. He can forward to Alvina or post directly.
