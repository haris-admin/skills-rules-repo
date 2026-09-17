---
name: aarrr-pirate-metrics
description: >-
  Model, audit, and optimize Dave McClure's AARRR Pirate Metrics funnel (Acquisition, Activation, Retention, Revenue, Referral) for startups and SaaS businesses. Use when analyzing product conversion funnels, mapping customer lifecycle drop-offs, establishing activation benchmarks, optimizing product-led growth (PLG), or evaluating stage-by-stage unit throughput.
---

# AARRR Pirate Metrics Funnel Architecture

A structured implementation of Dave McClure's canonical **AARRR Pirate Metrics** framework for startups, SaaS businesses, and digital product teams.

## When to Use

- **Growth Funnel Audits**: When diagnosing conversion leakage between landing page visits, account signups, and paying customers.
- **Onboarding & Activation Optimization**: When designing the first-time user experience to accelerate time-to-value (TTV).
- **Product-Led Growth (PLG) Strategy**: When aligning engineering, marketing, and product telemetry around unified lifecycle stages.
- **SaaS Pipeline Modeling**: When forecasting revenue throughput and viral referral loops for venture-backed and bootstrapped ventures.

---

## The Five Pirate Lifecycle Stages

```
   Stage               Core Question                           Primary Metric
┌─────────────┐
│ ACQUISITION │ ──► How do customers discover you?        ──► Traffic, CTR, CPC, CAC
└──────┬──────┘
       │
┌──────▼──────┐
│ ACTIVATION  │ ──► Do they have a great first experience?──► Signup %, Time to Value (TTV)
└──────┬──────┘
       │
┌──────▼──────┐
│  RETENTION  │ ──► Do they come back repeatedly?         ──► DAU/MAU, Cohort Retention
└──────┬──────┘
       │
┌──────▼──────┐
│   REVENUE   │ ──► How do you monetize their usage?      ──► ARPU, MRR, Paying Conv %
└──────┬──────┘
       │
┌──────▼──────┐
│  REFERRAL   │ ──► Do they tell their peers?             ──► Viral K-Factor, NPS, Invites
└─────────────┘
```

### 1. Acquisition
- Focus on traffic volume, source distribution, and customer acquisition cost across organic, content, search ads, and direct channels.

### 2. Activation
- The critical step where a visitor experiences the core value ("Aha!" moment). Measure percentage of signups who complete their initial setup or first transaction within 24 hours.

### 3. Retention
- The bedrock of sustainable growth. High acquisition with poor retention forms a leaky bucket. Measure Day 1, Day 7, and Day 30 cohort retention curves.

### 4. Revenue
- Monetization efficiency: free-to-paid conversion rate, Average Revenue Per User (ARPU), expansion revenue, and Net Revenue Retention (NRR).

### 5. Referral
- The viral growth loop. Measure the viral coefficient ($K = i \times c$) where $i$ is invites sent per user and $c$ is invite conversion rate.

---

## Funnel Calculator CLI

Use the bundled calculator script to model conversion rates and cumulative throughput:

```bash
# Calculate standard funnel metrics
python3 growth/aarrr-pirate-metrics/scripts/calculate_aarrr_funnel.py \
  --visitors 10000 \
  --signups 600 \
  --activated 420 \
  --retained 250 \
  --paying 100 \
  --referrals 25

# Output JSON for reporting pipelines
python3 growth/aarrr-pirate-metrics/scripts/calculate_aarrr_funnel.py --json
```

---

## References & Playbooks

- [Funnel Stage Breakdown & Benchmarks](./references/funnel-stage-breakdown.md) — Comprehensive metric definitions, formulas, and tactical optimization levers for each stage.
- [B2B SaaS Pirate Metrics Case Study](./references/b2b-saas-case-study.md) — Applied case study for compliance SaaS (AMLHive) and workflow systems (Simplifii-OS).
