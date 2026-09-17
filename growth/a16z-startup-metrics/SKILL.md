---
name: a16z-startup-metrics
description: >-
  Calculate, track, and benchmark Andreessen Horowitz (a16z) startup metrics (ARR, MRR, Gross Margin, CAC Payback, LTV/CAC, and Net Retention) applied to B2B SaaS and AMLHive compliance operations. Use when evaluating startup growth, calculating unit economics, preparing investor board packs, auditing search engine COGS, or running weekly SaaS health checks.
---

# a16z Startup Metrics Architecture (AML Hive Tracking)

A rigorous implementation of Andreessen Horowitz's canonical **16 Startup Metrics** tailored for high-velocity B2B SaaS and specialized for Australian regulatory compliance tracking at **AML Hive (amlhive.com.au)**.

## When to Use

- **Venture Economics & Investor Reviews**: When compiling metrics dashboards, board packs, or monthly strategy reviews for founders and stakeholders.
- **Unit Economic Health Audits**: When evaluating whether Customer Acquisition Cost (CAC), Gross Margin, or LTV/CAC meet sustainable SaaS benchmarks.
- **AML Hive Operational Tracking**: When monitoring active reporting entity subscriptions, ASIC/PEP search query margins, and regulatory deadline cohort surges.
- **Pricing & Tier Strategy**: When modeling changes to flat subscription pricing versus pay-per-scan credit bundles.

---

## The Core Metric Framework

```
                     ┌────────────────────────────────┐
                     │   TOP-LINE RECURRING SCALE     │
                     │    ARR  ·  MRR  ·  ARPU        │
                     └───────────────┬────────────────┘
                                     │
         ┌───────────────────────────┴───────────────────────────┐
         ▼                                                       ▼
┌─────────────────────────────────┐             ┌─────────────────────────────────┐
│       MARGINS & EFFICIENCY      │             │      RETENTION & UNIT HEALTH    │
│  Gross Margin (Search COGS)     │             │  Logo Churn  ·  Net Retention   │
│  Blended CAC  ·  CAC Payback    │             │  LTV / CAC Ratio (Target ≥ 3x)  │
└─────────────────────────────────┘             └─────────────────────────────────┘
```

### 1. Top-Line Recurring Revenue
- **ARR (Annual Recurring Revenue)**: Excludes one-off setup fees, manual advisory audits, or ad-hoc search credit purchases.
- **MRR (Monthly Recurring Revenue)**: Monthly recurring revenue normalized across active reporting entities.
- **ARPU (Average Revenue Per User)**: $\frac{\text{MRR}}{\text{Active Entities}}$.

### 2. Margins & Search Engine COGS
- **Direct Delivery COGS**: ASIC register search API fees, international PEP/sanctions vendor queries, and identity verification SMS costs.
- **Target Gross Margin**: $\ge 75\%$. If API costs push margins below 70%, search credit pricing must be re-indexed.

### 3. Acquisition & Payback Velocity
- **Blended CAC**: Total marketing and sales expenditure divided by new reporting entities onboarded.
- **CAC Payback Period**: Months to recover acquisition costs from gross profit. Target $< 6$ months for SMB compliance tiers.
- **LTV / CAC Ratio**: Ratio of customer lifetime gross profit to acquisition cost. Target $\ge 3.0\times$.

---

## Rapid Calculator CLI

Use the bundled calculator script to run instant unit economic analyses:

```bash
# Calculate standard AMLHive metrics
python3 growth/a16z-startup-metrics/scripts/compute_amlhive_metrics.py \
  --mrr 15000 \
  --entities 100 \
  --sales-spend 3000 \
  --new-entities 12 \
  --cogs-per-entity 22 \
  --churn-rate 0.015

# Output JSON for agentic pipelines
python3 growth/a16z-startup-metrics/scripts/compute_amlhive_metrics.py --json
```

---

## References & Playbooks

- [a16z 16 Startup Metrics Guide](./references/a16z-16-metrics-guide.md) — Comprehensive breakdown of bookings vs revenue, churn, NRR, and efficiency metrics.
- [AML Hive Metrics Dashboard](./references/amlhive-metrics-dashboard.md) — Exact mapping of a16z metrics to AML Hive's subscription model, search COGS, and AUSTRAC compliance cycle.
