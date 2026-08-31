---
name: pluto-content-firewall
description: Content firewall rules for all agents working on Haris Habib's blog content. Defines what can and cannot be mentioned in harishabib.au blog posts, LinkedIn content, and all Haris Habib personal brand materials.
allowed-tools: []
---

# Content Firewall — All Agents MUST Follow

## Core Rule & Reason

Haris Habib works at **Data Mesh Group**, which has a strict employment policy: no personal startup products or venture ideas may be mentioned or promoted on Haris Habib's personal channels. This is not a preference — it is an employment requirement.

## ❌ NEVER MENTION (Hard Firewall)

These are Haris's own startup products/ventures. They must NEVER appear in:
- harishabib.au blog posts, website, or any hosted content
- Haris Habib's LinkedIn profile, posts, or comments
- Any content associated with Haris Habib as a personal brand

**Complete firewalled list** (case-insensitive):

| Product/Brand | Aliases | Notes |
|---|---|---|
| AML Hive | amlhive, AML Hive | Separate entity at amlhive.com.au |
| FinAI File | FinAI, fin AI file | AI governance product |
| PayLicence | Pay Licence, paylicence | PSP licensing |
| ExitLens | exitlens, Exit Lens | ESOP/CGT — free tool gray zone (ask) |
| TokenPilot | tokenpilot, Token Pilot | Digital assets |
| CloudProof | cloudproof, Cloud Proof | Cloud compliance |
| Tapease | tapease, Tap Ease | Market infrastructure |
| AgentGate | agentgate, Agent Gate | Agent gateway |
| CloudWise | cloudwise, Cloud Wise | Cloud operations |
| VerifyLink | verifylink, Verify Link | Verification |
| NDIS BillBot | ndis bot | NDIS automation |
| RegStack | regstack | Regulatory stack |
| ExtRisk | extrisk | Risk assessment |

## ✅ ALLOWED TO MENTION

- **Third-party commercial products** — Snyk, Sysdig, Microsoft, AWS, Docker, GitHub, Netlify, etc. — these are fully allowed
- **Third-party open-source tools** — Trivy, Kubernetes, Astro, Next.js, etc.
- **Free utility tools** hosted on harishabib.au (calculators, worksheets, interactive components) — may appear on the site itself, but blog posts should not promote the branded product behind them
- **Regulatory frameworks and bodies** — AUSTRAC, ASIC, APRA, AFSL, Privacy Act, CPS 230
- **Industry events, publications, and companies** — any third-party entity is fine

## Gray Zone: Free Tools With Product Branding

Example: ExitLens has a free CGT calculator hosted at esop.harishabib.au. The calculator itself is a free utility tool (which is allowed on the site). But mentioning "ExitLens" by name in a blog post is promoting the product brand. **When in doubt, strip the brand name and describe the tool generically, or ask Haris.**

## Content Stream Separation

- **Stream 1 (Haris Habib):** harishabib.au + LinkedIn — pure opinion, no personal product mentions
- **Stream 2 (AML Hive):** amlhive.com.au — standalone, no cross-linking to Haris Habib

These two streams must never cross or reference each other. They are separate identities.

## Compliance Sweep Procedure

When new blog posts are added (by Haris or other agents), run a full sweep:

```bash
# From the harishabib_au_code repo root:
grep -rni "aml hive\|finai\|paylicence\|exitlens\|tokenpilot\|cloudproof\|tapease\|agentgate\|cloudwise\|verifylink" src/content/blog/ linkedin/ src/content/internal/ --include="*.md"
```

## Review Checklist (Before Every Publish)

1. Grep for all firewalled terms (use sweep procedure above)
2. Check all internal links — do they cross to firewalled products?
3. Check LinkedIn companion sections in blog posts
4. Third-party commercial mentions are OK — do NOT strip them
5. When in doubt, remove and replace with generic description

## Interactive Worksheet Removal (June 9, 2026)

The `BlogTool.astro` component rendered an "Interactive worksheet / Article Readiness Check" widget at the bottom of blog posts that had a tool mapped in `blogTools.ts`. This was removed for ALL blog posts by commenting out the render line in `src/pages/blog/[...slug].astro`:

```astro
<!-- BlogTool removed per firewall: no interactive worksheets on blog posts -->
```

14 blog posts had mapped tools (Docker Moment, Human-AI Partnership, Resilience Engineering, etc.). The removal is blanket — no blog post receives a tool widget anymore. The ESOP calculator at esop.harishabib.au is a separate page, unaffected.

LinkedIn companion posts go as **separate files** in the `linkedin/` directory, NOT embedded in blog post content. Format:

```
linkedin/linkedin-post-YYYY-MM-DD-slug.md
```

When Haris asks for a LinkedIn post to pair with a blog post, write it as a standalone file — never embed it under a "## LinkedIn Companion Post" section inside the blog markdown. Blog posts are blog posts. LinkedIn posts are separate artifacts.

- **The rule is not "no commercial products"** — it's "no HARIS'S products." Third-party commercial products are completely fine.
- **Existing posts may contain old violations** — run compliance sweeps periodically, not just on new posts.
- **Internal posts (src/content/internal/) still count** — they're redirected to /restricted but should be clean too.
- **LinkedIn companion sections in blog posts are part of the blog** — they inherit the same firewall rules.
- **The BrandCopy component on AML Hive is for AML Hive alone** — never reference it from harishabib.au content.
