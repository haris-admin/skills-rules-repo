---
name: pluto-linkedin-content-engine
description: Pluto's LinkedIn and blog content ideation engine — generates social media post drafts and blog ideas from research signals, mapped to Haris's content pillars and portfolio projects. Use when generating content ideas, debugging the linkedin_ideas_generator.py script, or setting up new content pillars.
allowed-tools: [terminal, read_file, write_file, execute_code]
---

# Pluto LinkedIn & Blog Content Engine

## When to Use
- Running the LinkedIn content generator manually
- Debugging why content wasn't generated
- Adding a new content pillar or portfolio project
- Checking today's content ideas output

## Architecture

**Cron:** `ee4e48300826`, schedule `45 6 * * *` AEST (6:45 AM)
**Script:** `~/.hermes/scripts/linkedin_ideas_generator.py`
**Venv:** `/home/habib/.hermes/venv/bin/python3`
**Output:** `~/.hermes/research_outputs/linkedin-ideas_YYYY-MM-DD.md`

## Content Pillars

1. **AI Agents & Governance** — AI regulation, agent security, governance frameworks
2. **Australian Fintech Regulation** — AUSTRAC, AML, ASIC, PSP licensing
3. **Cloud & Resilience** — Cloud infrastructure, cost optimization, resilience engineering
4. **Startup & ESOP** — Australian startup ecosystem, ESOP reform, CGT, exits

## Content Firewall — Haris Habib Personal Brand (June 9, 2026)

### 🔴 No Personal Products Rule
harishabib.au is an **opinion blog**. LinkedIn is **thought leadership**. Neither may:
- Mention Haris's own startup products/ideas by name (see `pluto-content-firewall` for full list)
- Reference "our solution" or "our product" in any context
- Serve as a lead-generation channel for paid products
- Link to any product landing page or trial

### 🟢 Allowed Content
- Opinion pieces on AI governance, fintech regulation, cloud resilience, startup/ESOP
- **Third-party commercial products** — fully allowed (Snyk, Sysdig, Microsoft, AWS, etc.)
- Free utility tools (worksheets, calculators, OS components) that stand alone — gray zone, ask
- Industry analysis with no commercial call-to-action
- Thought leadership that establishes expertise without naming personal products

### 🔴 AML Hive Firewall
AML Hive is a COMPLETELY SEPARATE ENTITY from Haris Habib. It has:
- **ZERO association** with harishabib.au blog posts
- **ZERO mentions** in Haris Habib LinkedIn content
- **ZERO cross-references** in any Haris Habib personal brand content

AML Hive content lives independently on amlhive.com.au. When generating content ideas, produce TWO DISTINCT STREAMS:
1. **Haris Habib stream:** harishabib.au blog + LinkedIn — pure thought leadership, no product names
2. **AML Hive stream:** amlhive.com.au — AUSTRAC Tranche 2, AML/CTF, regtech (NEVER crosses into stream 1)

### Portfolio Project Mapping — FOR INTERNAL USE ONLY
Do NOT mention these in blog posts or LinkedIn. This mapping is for Pluto's internal signal-to-content routing only:

| Project | Internal Signal Domain |
|---------|----------------------|
| ExitLens AU | ESOP, CGT, exits, startup equity |
| PayLicence AU | PSP licensing, payments reform |
| TokenPilot AU | Digital assets, DLT, AFSL |
| FinAI File AU | AI compliance, agent governance |
| CloudProof AU | Cloud compliance, resilience |

**Never use these project names in any Haris Habib public content.** Map signals to topics, not products.

## LinkedIn Post Structure

Each post has 3 components:
1. **Hook:** 1-2 sentence grabber with specific data point, news event, or trend stat
2. **Angle:** 2-3 sentences connecting to Haris's expertise and thought leadership area
3. **CTA:** 1 sentence engagement prompt ("What's your experience with...", "DM me if...")

**NO commercial product names in any component.** The angle should reference expertise domains (AI governance, cloud resilience, fintech regulation, startup equity) — never specific products.

## Blog Post Structure

Posts live on harishabib.au as Astro content collection markdown files. 

**Location:** `/mnt/c/Code/gitlab/harishabib_au_code/src/content/blog/<slug>.md`
**Deploy:** Commit to `main` branch → GitLab → Netlify auto-deploy (~2min)
**Repo:** `gitlab.com/hhsiddiqui/harishabib_au_code`

### Required Frontmatter
```yaml
title: "Post Title"
description: "1-2 sentence meta description"
pubDate: YYYY-MM-DD
heroImage: "/images/whiteboard-<diagram>.svg"  # optional but recommended
pillar: ai-adoption | system-design | tech-leadership
audience: ["CTOs", "founders"]  # optional
topics: ["ai-governance"]  # optional
keywords: ["keyword1"]  # optional
sources:  # optional
  - title: "Source Name"
    url: "https://..."
```

### LinkedIn Companion Section
Every blog post should include a LinkedIn companion at the bottom:
- **Hook:** 1-2 sentence attention grabber
- **Angle:** 2-3 sentences connecting to thought leadership
- **CTA:** Engagement question
- **Pillar:** Content pillar
- **NO product names anywhere**

### Content Rules (MANDATORY)
- **Haris's own products:** ZERO mentions (AML Hive, FinAI File, PayLicence, ExitLens, TokenPilot, CloudProof, Tapease, AgentGate, CloudWise, VerifyLink, any other personal venture)
- **Third-party commercial products:** FULLY ALLOWED (Snyk, Sysdig, Microsoft, AWS, Docker, etc.)
- Reason: Data Mesh Group employment policy — no personal startup products on personal channels
- Posts are opinion/thought leadership only
- Exception: free utility tools (worksheets, calculators, OS components) that provide standalone value — gray zone, ask Haris
- AML Hive is NEVER a valid blog topic for harishabib.au

Each blog idea for ideation has:
- **Pillar:** Content pillar
- **Gap filled:** What missing topic does this cover?
- **Companion post:** Which existing post to internally link to
- **Angle:** 1-2 sentence description

### Existing Blog Posts (harishabib.au — 27 live as of June 2026)
Key posts for internal linking (most referenced):
1. The Docker Moment for AI Agents
2. The Human-AI Partnership: A Framework for Safe Adoption
3. Resilience Engineering in the Cloud
4. The 2026 Budget Changed the ESOP Question
5. What ASIC's AI Risk Radar Means for Your Startup
6. MCP Supply Chain Crisis: Why Every CTO Needs a Gateway
7. Your AI Agent Needs a Soul File
8. Agent Identity: Who Signs the Contract?
9. AI Washing Is The New Greenwashing
10. One Model Is the Wrong Default

Full catalog at harishabib.au/blog. Update this list when new posts are published.

## Reference Files
- `references/harishabib-au-deployment.md` — Complete harishabib.au blog post deployment workflow: Astro frontmatter schema, GitLab commit/push, Netlify deploy, merge conflict resolution, content rules, existing post catalog
- `references/amlhive-content-workflow.md` — AML Hive content creation workflow (SECOND stream): claim verification pipeline, content bundle pattern (blog + LinkedIn + Facebook), platform-specific tone adaptation, quality gates. Use when creating content for amlhive.com.au or Alvina's social channels. This is completely separate from Haris Habib personal brand content.

## Manual Run
```bash
/home/habib/.hermes/venv/bin/python3 /home/habib/.hermes/scripts/linkedin_ideas_generator.py
```

## Input Dependencies
The script reads:
- Latest Perplexity signals from Gmail (via himalaya)
- Today's research JSON: `~/.hermes/research_outputs/research_YYYY-MM-DD.json`
- Today's actions JSON: `~/.hermes/research_outputs/actions_YYYY-MM-DD.json`

If any input is missing, the generator skips that source and uses what's available. It should never fail completely if at least one source is present.

## Quality Gates
- Hooks MUST include specific data points (not generic statements)
- LinkedIn angle must reference thought leadership domain — never product names
- Blog ideas MUST identify a gap in existing content
- Blog posts MUST have zero personal product references (third-party commercial products like Snyk, Sysdig are fine)
- Never fabricate statistics — use numbers from research findings
- LinkedIn CTA must be engagement-driving, not sales-driving

## AML Hive Content Bundle Pattern (Alvina's Channels)

When creating content for AML Hive, produce a **three-piece bundle** per signal:

1. **Blog post** (amlhive.com.au) — 800-1500 words, educational, authoritative
2. **LinkedIn post** (Alvina) — ~1000-1200 chars, professional thought leadership  
3. **Facebook post** (Alvina) — ~600-900 chars, conversational alert tone with emojis

**Before writing any piece:** run the full claim verification pipeline (see `references/amlhive-content-workflow.md`). Flag any date or stat discrepancies to Haris BEFORE drafting the bundle. He will scrap content over stale data rather than fudge dates.

**Pipeline signal caveat:** Signal counts (e.g., "deadline appeared 44×") are aggregate keyword frequencies across the document corpus, NOT article-level sources. Don't offer them as linkable claims. Offer research JSON findings instead.

## Content Firewall (MANDATORY — Data Mesh Group Employment Policy)

Haris works at Data Mesh Group, which prohibits personal venture promotion on personal channels:

❌ NEVER: AML Hive, FinAI File, PayLicence, ExitLens, TokenPilot, CloudProof, Tapease, AgentGate, CloudWise, VerifyLink, NDIS BillBot, RegStack, ExtRisk — or any personal startup product
✅ ALLOWED: Third-party commercial products (Snyk, Sysdig, Microsoft, AWS), open-source tools, regulatory bodies, free utility tools
📋 Posts must be pure thought leadership — zero Haris product references

When generating LinkedIn posts or blog ideas, scan for ALL firewalled terms before output. Third-party products (Microsoft, AWS, Docker) are fine to mention. Only Haris's OWN products are firewalled. See `pluto-content-firewall` skill for full list.

## LinkedIn Companion Format

LinkedIn companion posts go as SEPARATE files in `linkedin/` directory, NOT embedded in blog markdown:
```
linkedin/linkedin-post-YYYY-MM-DD-slug.md
```
Never add a "## LinkedIn Companion Post" section inside a blog post. Blog posts are standalone articles.
- **Input dependency chain:** If morning research didn't produce JSON, LinkedIn ideas will be thin. The 45-minute buffer (6:00→6:45) usually suffices but check input files before blaming the generator.
- **Himalaya auth.cmd issues:** If Gmail can't be queried, Perplexity signals are unavailable. Fall back to research JSON alone.
- **Blog gap analysis requires knowing existing posts.** Currently 27 live posts on harishabib.au. Update the list as new posts are published.
- **Content pillar balance:** Monitor whether all 4 pillars get coverage. If one goes silent for 2+ days, the generator may need a topic rebalance.
- **🔴 AML Hive firewall (CRITICAL):** AML Hive and Haris Habib are separate entities. Never include AML Hive in harishabib.au blog ideas or LinkedIn posts. Never use AML Hive as a portfolio tie for Haris Habib content. When in doubt, omit — AML Hive has its own content strategy on amlhive.com.au.
- **🔴 Personal products firewall (CRITICAL):** harishabib.au and Haris Habib LinkedIn must never mention Haris's own startup products (AML Hive, FinAI File, PayLicence, ExitLens, TokenPilot, CloudProof, Tapease, AgentGate, CloudWise, VerifyLink). Third-party commercial products (Snyk, Sysdig, Microsoft, AWS, Docker) are fully allowed. These are opinion/thought-leadership channels only. Exception: free utility tools — gray zone, ask Haris.
- **🔴 Two-stream content separation:** Always present content recommendations as two distinct streams: (1) Haris Habib — harishabib.au + LinkedIn, pure thought leadership, zero product names. (2) AML Hive — amlhive.com.au only, AUSTRAC/AML/CTF focus. These streams never cross.
