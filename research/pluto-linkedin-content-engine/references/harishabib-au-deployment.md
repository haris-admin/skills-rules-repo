# harishabib.au Blog Post Deployment Workflow

## Repo
- **URL:** `gitlab.com/hhsiddiqui/harishabib_au_code`
- **Local path:** `/mnt/c/Code/gitlab/harishabib_au_code`
- **Deploy:** GitLab main branch → Netlify auto-deploy (~2min after push)
- **Framework:** Astro 5.x with content collections

## Blog Post Location
```
src/content/blog/<slug>.md
```

## Frontmatter Schema (Astro Content Collection)
```yaml
---
title: "string (required)"
description: "string (required)"
pubDate: YYYY-MM-DD (required)
updatedDate: YYYY-MM-DD (optional)
reviewedDate: YYYY-MM-DD (optional)
heroImage: "/images/whiteboard-<name>.svg" (optional)
draft: true|false (optional)
pillar: ai-adoption | system-design | tech-leadership (required)
audience: ["string"] (optional)
topics: ["string"] (optional)
industries: ["string"] (optional)
region: ["string"] (optional)
keywords: ["string"] (optional)
summary: "string" (optional)
keyTakeaways: ["string"] (optional)
sources: (optional)
  - title: "string"
    url: "https://..."
ctaPage: "string" (optional)
evergreen: true|false (optional)
---
```

## Content Rules (MANDATORY — Updated June 9, 2026)
1. **NO Haris's own startup products** — AML Hive, FinAI File, PayLicence, ExitLens, TokenPilot, CloudProof, Tapease, AgentGate, CloudWise, VerifyLink, and any other personal venture. Reason: Data Mesh Group employment policy.
2. **Third-party commercial products are FINE** — Snyk, Sysdig, Microsoft, AWS, Docker, GitHub, Netlify, etc. are fully allowed.
3. **Pure opinion/thought leadership** — no lead generation, no "our solution" references, no product landing pages.
4. **Exception:** Free utility tools (worksheets, calculators, OS components) hosted on harishabib.au are OK.
5. **AML Hive** is a completely separate entity — never referenced, never cross-linked.
6. **LinkedIn companion section** at bottom of each post is optional — include when it adds value, remove when redundant.
7. **See `pluto-content-firewall` skill** for the full firewalled terms list and compliance sweep procedure.

## Commit and Deploy
```bash
cd /mnt/c/Code/gitlab/harishabib_au_code
git add src/content/blog/<slug>.md
git commit -m "blog: <title>"
git pull --rebase origin main  # main may have new commits
git push origin main
```

## Merge Conflict Resolution
The repo frequently has merge conflicts because changes are pushed from multiple sources:
1. `git status --short | grep "^UU"` — list conflicted files
2. `git checkout --theirs <file>` — accept remote/main version for each conflicted file
3. `git add <file>` — mark resolved
4. `git commit` or `GIT_EDITOR=true git rebase --continue`

## Compliance Sweep (Run Before Every Publish)
```bash
cd /mnt/c/Code/gitlab/harishabib_au_code
grep -rni "aml hive\|finai\|paylicence\|exitlens\|tokenpilot\|cloudproof\|tapease\|agentgate\|cloudwise\|verifylink" src/content/blog/ linkedin/ --include="*.md"
```
Zero results = clean. See `pluto-content-firewall` for full procedure including internal posts.

## Existing Posts (28 live as of June 9, 2026)
Key posts for internal linking:
- The Docker Moment for AI Agents (2026-03-31)
- Your AI Agent Needs a Soul File (2026-05-01)
- One Model Is the Wrong Default (2026-05-05)
- MCP Supply Chain Crisis (2026-05-28)
- What ASIC's AI Risk Radar Means for Your Startup (2026-06-08)
- Agent Security Supply Chain — Sysdig (2026-06-09)

## Pillars
| Pillar | Description |
|--------|-------------|
| `ai-adoption` | AI governance, agent security, adoption frameworks |
| `system-design` | Architecture, cloud, resilience, compliance-by-design |
| `tech-leadership` | Industry analysis, regulatory landscape, strategy |
