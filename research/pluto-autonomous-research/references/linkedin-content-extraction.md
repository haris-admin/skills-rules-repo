# LinkedIn & Blog Content Extraction from Research Outputs

**Last updated:** June 3, 2026 — automated pipeline added

## When to Use
After daily research fires, convert research findings into social-ready content. Now automated via `linkedin_ideas_generator.py` cron at 6:45 AM AEST.

## Automated Pipeline (NEW June 3, 2026)

### Script
`/home/habib/.hermes/scripts/linkedin_ideas_generator.py`

### Cron
- **Job ID:** `ee4e48300826`
- **Schedule:** `45 6 * * *` (6:45 AM AEST — after all research stages)

### Input Sources
1. **Gmail briefings** — Perplexity Tasks signals via himalaya (see `references/gmail-briefing-integration.md`)
2. **Today's research JSON** — `~/.hermes/research_outputs/research_YYYY-MM-DD.json`
3. **Today's actions JSON** — `~/.hermes/research_outputs/actions_YYYY-MM-DD.json`
4. **Existing blog posts** — Scraped from harishabib.au:
   - `/blog/the-docker-moment-for-ai-agents`
   - `/blog/human-ai-partnership`
   - `/blog/resilience-engineering-cloud`
   - `/blog/esop-cgt-2026-budget-implications`

### Content Pillars
| Pillar | Existing Blogs | Portfolio Link |
|--------|---------------|----------------|
| AI Agents & Governance | Docker Moment, Human-AI Partnership | FinAI File AU, AgentGate |
| Australian Fintech Regulation | ESOP CGT 2026 | AML Hive, PayLicence AU |
| Cloud & Resilience Engineering | Resilience Engineering | CloudProof AU |
| Startup & ESOP | ESOP CGT 2026 | ExitLens AU |

### Output
`~/.hermes/research_outputs/linkedin-ideas_YYYY-MM-DD.md` — Markdown with LinkedIn post ideas (hook + angle + CTA) and blog post ideas (pillar match + gap analysis).

## Manual Pipeline (pre-June 2026)

### 1. Load Today's Research
```python
from hermes_tools import read_file
import json

# Find today's research
result = terminal("ls -lt ~/.hermes/research_outputs/research_$(date +%Y-%m-%d)*.json")
files = [line.split()[-1] for line in result['output'].split('\n') if line.strip()]

for f in files:
    data = json.loads(read_file(f)['content'])
    for finding in data.get('findings', []):
        # Extract post-worthy findings
```

### 2. Post-Worthiness Criteria
A finding is LinkedIn-post-worthy if it has:
- **Timeliness:** A deadline, legislative event, or regulatory change within 4 weeks
- **Stake:** Direct impact on Haris's audience (founders, fintech, compliance, accountants)
- **Hook:** A counter-intuitive angle, a number, or a "most people don't know yet" insight

### 3. Post Structure (Deepak Singh Pattern)
Don't lead with "founders lose money." Lead with the stakeholder most people care about.

| Domain | Wrong Hook | Right Hook |
|--------|-----------|------------|
| CGT reform | "Founders lose $366K on exit" | "Your employees' ESOP just lost 27% of its value" |
| AML compliance | "Firms face new regulatory burden" | "AUSTRAC just handed lawyers a compliance deadline — most don't know yet" |
| Digital assets | "New crypto regulation is here" | "Every crypto startup now needs a regulated pilot plan" |

### 4. Output Format
Each post should include:
- **Hook line** (1 sentence)
- **The Signal** (1 paragraph — what changed, from which source)
- **Your Angle** (1 paragraph — how it connects to Haris's products/position)
- **Source attribution** (where the signal came from)

### 5. Which Product Does This Support?
Map each finding to the portfolio:

| Finding Type | Product to Mention |
|-------------|-------------------|
| CGT, tax reform, startup exits | ExitLens AU (esop.harishabib.au) |
| AUSTRAC, AML, Tranche 2, compliance | AML Hive (amlhive.com.au) |
| Tokenised settlement, stablecoin, DLT | TokenPilot AU |
| AI regulation, agent security | AgentGate / AgentSRE |
| Cloud repatriation, sovereign infrastructure | SovereignBridge |

## Proven Posts (May-June 2026)

### Post 1: CGT Senate Inquiry + ESOP Framing
- Hook: "The CGT changes are NOT final. The carveout for startups is being negotiated RIGHT NOW."
- Product: ExitLens AU
- Result: Posted, engagement data pending

### Post 2: AUSTRAC Tranche 2 — Sector Expansion
- Hook: "AUSTRAC just handed lawyers, accountants, and real estate agents a compliance deadline. Most don't know it yet."
- Product: AML Hive
- Source: AUSTRAC Program Starter Kits + SMSF Association

### Post 3: Digital Assets Legislation + TokenPilot
- Hook: "Australia just enacted its first digital assets legislation. Every crypto and stablecoin startup now needs a regulated pilot plan."
- Product: TokenPilot AU
- Source: ASIC roadmap
