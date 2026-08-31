# Codex Ideation CONTEXT.md Template

**Proven with:** Codex 5.5 (GPT-5.5), 97K tokens, June 2 2026 — produced 3 net-new ideas scoring 830/795/755.

## Structure

The following sections produced the best Codex output. Keep them all, in this order.

```markdown
# Pluto Research Pipeline — Consolidated Brief for Codex Ideation

**Date:** <TODAY>
**Task:** Review ALL reports and generate 3 net-new startup/project ideas
**Model:** GPT-5.5 (Codex)

## Fleet Status
- <Current cron count, voice status, MemPalace stats>

## COMPLETE Existing Portfolio — DO NOT DUPLICATE

### GitLab Repos (/mnt/c/Code/gitlab/ideas-*)
| Repo | Status | Latest Commit |
|------|--------|---------------|
| **<slug>** | Active | <first line of last commit message> |
...

### Active Production Projects (memory)
- **<Project>** — <one-line description>
...

### Scored Ideas (from previous run — already built/queued)
- <Idea>: <Score>/1000 (<Grade>) — <one-line>
...

## Key Research Signals (<date>)

### Top Findings
1. **<Title>** — <2 sentence summary, include deadline if applicable>
...

### Cross-Domain Signal Patterns (from synthesis)
- `signal`: N× across M domains
...

### Cross-Domain Opportunities (from action items)
- DomainA × DomainB (N shared concepts): concept1, concept2, concept3
...

### Signal Balance
- Pro-regulation: N — Anti-regulation: M (ratio — <trend>)

## Market Timing Windows (CRITICAL)
- **<Event>:** <Date> — <consequence>
...

## Constraints (HARD RULES)
1. **AUD $250 MVP budget** — Phase 1 must be achievable within this
2. **Australian-first** — Local market, local regulations, local buyers. Global = Phase 2.
3. **NO overlap** — Do not duplicate any existing project above
4. **Frontend:** React/Next.js + Tailwind CSS. **NEVER** propose Streamlit.
5. **Backend:** Python/FastAPI
6. **Each idea grounded in ≥1 high-confidence research signal** from reports/
7. **Code location:** `/mnt/c/Code/gitlab/ideas-<slug>/`
8. **No code-only Phase 1 unless essential** — prefer markdown → sheets → static site → React (increasing effort)

## Output Instructions for Codex

1. Read ALL files in `reports/` directory (JSON + MD)
2. Read the Gumby 1000-point assessment framework in `ideas/1000_POINT_ASSESSMENT.md`
3. Review the previous ideation output in `ideas/NEW_IDEAS.md`
4. Generate **3 NET-NEW ideas** (not <list previously-scored ideas>)
5. For each idea produce a **mini-PRD** with: Problem, Solution, Target User, Value Prop, Revenue Model, MVP Scope (AUD $250), Success Criteria
6. Score each idea against the Gumby 1000-point framework
7. Rank them: BUILD ORDER 1, 2, 3 with reasoning
8. Write output to `ideas/NEW_IDEAS_<MONTH>_<DAY>.md`

### Gumby 1000-Point Scoring (for reference)
| Dimension | Points | What it measures |
|-----------|--------|------------------|
| Market Timing | 200 | Is there an active regulatory deadline? |
| TAM | 200 | Addressable market size |
| Moat | 150 | Defensibility |
| Revenue Velocity | 150 | Speed to first dollar |
| Build Feasibility | 100 | Can it be MVP'd for $250? |
| Portfolio Synergy | 100 | Extends existing projects? |
| Regulatory Tailwind | 100 | Regulatory deadline driving demand? |
| **TOTAL** | **1000** | |

Grading: A (800+), A-/B+ (700-799), B (600-699), C/KILLED (<600)

## Critical Pitfalls to Avoid
- Do NOT propose anything that overlaps with <specific exclusions per domain>
- Look for gaps: what regulation is coming that NO existing project addresses?
- <Call out 2-3 under-served whitespace areas as hints>
```

## Key Design Decisions

1. **Portfolio table with commit messages** — Shows Codex exactly what stage each project is in (not just that it exists)
2. **Explicit exclusion list** — Prevents Codex from proposing CGT calculators because "CGT is in the news"
3. **Hard constraints as numbered rules** — Codex respects numbered constraints more than prose
4. **Hints at under-served areas** — Guides Codex toward whitespace without dictating the ideas
5. **Cross-domain signals** — These are the highest-value input; Codex used them to identify FinAI File AU (AI×FinTech) and CloudProof AU (Data Sovereignty signal)
6. **Signal balance metrics** — Quantitative signal data (84× compliance, 33× deadline) gives Codex conviction

## Pitfalls

- Do NOT list every single repo's README content — one-line latest-commit summaries are enough
- Do NOT over-explain existing projects — a table row each is sufficient
- The exclusion list MUST be specific ("Don't propose AUSTRAC T2 compliance tools") not vague ("Don't overlap")
- If the previous run produced ideas that already have repos, list them in "Scored Ideas" as exclusions
