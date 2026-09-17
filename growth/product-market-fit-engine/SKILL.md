---
name: product-market-fit-engine
description: >-
  Measure, track, and optimize Product-Market Fit (PMF) using the Sean Ellis 40% rule, Rahul Vohra's Superhuman PMF engine, and cohort retention curve flattening. Use when surveying active users, diagnosing retention drop-offs, prioritizing product roadmaps, or deciding whether a startup is ready to scale marketing and sales.
---

# Product-Market Fit (PMF) Engine Architecture

A systematic, quantitative engine for measuring customer satisfaction, isolating High-Expectation Customers (HXC), and driving iterative product sprints until reaching the **Sean Ellis 40% PMF threshold**.

## When to Use

- **Early Traction Diagnostics**: When evaluating whether an MVP has true pull from the market or is leaking users.
- **Roadmap Prioritization**: When deciding which features to build next based on customer feedback segmentation.
- **Scale Readiness Gate**: Before ramping paid marketing, sales hiring, or growth expenditure (premature scaling kills startups that lack PMF).
- **Investor Milestone Verification**: When demonstrating quantifiable PMF to seed or Series A investors.

---

## The PMF Engine Workflow

```
┌─────────────────────────────────────────────────────────────┐
│ 1. SURVEY ACTIVE USERS (Ellis 40% "Disappointment" Test)   │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ 2. CALCULATE PMF SCORE (% who would be "Very Disappointed") │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ 3. SEGMENT HIGH-EXPECTATION CUSTOMERS (HXC Lovers vs Fence) │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ 4. 50/50 ROADMAP SPRINT: Double down on loves / Fix blockers│
└─────────────────────────────────────────────────────────────┘
```

---

## PMF Score Calculator CLI

Run the bundled calculator to process survey results:

```bash
# Run demonstration PMF survey evaluation
python3 growth/product-market-fit-engine/scripts/calculate_pmf_score.py --demo

# Calculate custom survey responses
python3 growth/product-market-fit-engine/scripts/calculate_pmf_score.py \
  --very 52 \
  --somewhat 34 \
  --not-disappointed 14

# Output machine-readable JSON for dashboards
python3 growth/product-market-fit-engine/scripts/calculate_pmf_score.py --demo --json
```

See [calculate_pmf_score.py](./scripts/calculate_pmf_score.py) for the scoring algorithm.

---

## The Superhuman 50/50 Rule

When allocating engineering and design resources:
1. **50% of Sprint Capacity**: Deepen what the "Very Disappointed" users cherish. Protect your core differentiator.
2. **50% of Sprint Capacity**: Address what prevents the "Somewhat Disappointed" users from falling in love, specifically targeting those who value the same core benefit as your lovers.
3. **0% of Sprint Capacity**: Completely ignore users who said "Not Disappointed". Trying to please everyone dilutes the product and destroys PMF.

Refer to the complete [Superhuman PMF Methodology Guide](./references/superhuman-pmf-methodology.md) for the 4-question survey design and cohort retention benchmarks.
