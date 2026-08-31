# gstack — AI Product Development Workflow (Garry Tan)

> Reviewed May 27, 2026 — 103K GitHub stars. Source: `garrytan/gstack`

## What It Is

gstack is a 23+ skill AI agent operating system that turns a single AI into a full product development team. Each skill is a specialist role: CEO reviewer, Eng Manager, Designer, QA Lead, Release Engineer, Debugger, and more.

## Four-Layer Architecture

```
PLAN ──────────▶ BUILD ──────────▶ SHIP ──────────▶ SECURE
/office-hours     /review           /ship            /cso
/plan-ceo-review  /investigate      /land-and-deploy /health
/plan-eng-review  /qa               /canary          /learn
/plan-design-     /design-review    /document-       /retro
review                              release
/plan-devex-                        /document-
review                              generate
/autoplan
```

## Key Patterns Worth Adopting

### 1. Premise Challenge Before Building
Every plan review starts with: "Is this the right problem? Could a different framing yield a dramatically simpler solution?" The `/office-hours` skill asks 6 forcing questions before any solution is proposed. This is the anti-feature-factory pattern.

### 2. Multi-Mode Review Posture
CEO review has 4 modes that commit once selected:
- **SCOPE EXPANSION** — dream big, propose the 10x version
- **SELECTIVE EXPANSION** — hold baseline + cherry-pick expansions
- **HOLD SCOPE** — maximum rigor, make it bulletproof
- **SCOPE REDUCTION** — ruthless cut to minimum viable

### 3. "Completeness Is Cheap" Principle
AI coding compresses implementation time 10-100x. Always prefer approach A (full, ~150 LOC) over approach B (90%, ~80 LOC). "Ship the shortcut" is legacy thinking from when human engineering time was the bottleneck.

### 4. Error & Rescue Map (Section 2 of CEO Review)
Every codepath gets a table: METHOD → WHAT CAN GO WRONG → EXCEPTION CLASS → RESCUED? → RESCUE ACTION → USER SEES. Catch-all error handling is always a code smell. This is the highest-signal section for catching production failures before they happen.

### 5. Data Flow Shadow Paths
Every data flow has 4 paths: happy, nil input, empty/zero-length input, upstream error. All four get ASCII-diagrammed.

### 6. Search Before Building
Three-layer synthesis: (1) What does everyone already know? (2) What are search results saying? (3) First-principles — where might conventional wisdom be wrong? Eureka moments get logged.

### 7. DIET (Duplication Is Evil Trick)
AI coding's rate limiting is context, not typing speed. Five rules: don't recursively repeat, don't copy whole call sites for small diffs, don't deep-research again mid-build, don't reproduce whole prior output for a prefix change, don't pick a smaller diff when the full one is better and costs the same tokens.

## OpenClaw Integration (4 Skills)

gstack ships 4 OpenClaw-native skills in `/openclaw/skills/` — already formatted for Gumby:

| Skill | Function |
|-------|----------|
| `gstack-openclaw-ceo-review` | 11-section CEO review, 18 cognitive patterns, 4 modes |
| `gstack-openclaw-office-hours` | YC Office Hours — 6 forcing questions, startup + builder modes |
| `gstack-openclaw-investigate` | Systematic root-cause debugging |
| `gstack-openclaw-retro` | Weekly retro with streak tracking, team breakdown, Telegram-formatted |

Gumby can install these directly into `%USERPROFILE%\.openclaw\workspace-wsl\skills\`.

## Fleet Project Mapping

### RegStack (Compliance Platform)
- `/office-hours` — validate the desperate compliance officer persona
- `/plan-ceo-review` (EXPANSION) — dream the 10-star compliance automation
- `/cso` — security audit for compliance data handling
- `/document-generate` — auto-generate Diataxis docs for compliance officers

### AgentSRE (Agent Monitoring)
- `/plan-eng-review` — architecture for multi-agent observability
- `/cso --scope auth` — agent-to-agent authentication
- Google SRE principle #15 (error budgets over uptime targets) is built into eng review's cognitive patterns

### LocalStack (Local Dev Environment)
- `/plan-devex-review` — time-to-first-working-build audit
- `/plan-eng-review` — distribution architecture (how devs install it)

## Differences From Our Current Setup

| Area | Our Current | gstack Approach |
|------|------------|-----------------|
| Plan review | Individual skills (plan, spike) | Structured 4-mode pipeline with forced alternatives |
| Office hours | Not formalized | 6 forcing questions, demand vs interest distinction |
| Code review | `/requesting-code-review` | Interactive one-issue-at-a-time with opinionated recommendations |
| Security | OWASP via standard tools | 14-phase CSO audit with daily/comprehensive modes |
| Retro | Gumby's existing retro | Streak tracking, team breakdown, Telegram-native formatting |
| Learning | Pluto's skill extraction loop | `/learn` skill + gbrain for cross-session memory |
