---
name: startup-runway-and-unit-economics
description: >-
  Model, calculate, and forecast startup unit economics, gross and net cashflow burn rate, cash runway, and Zero Cash Date (ZCD) across portfolio projects (e.g. AMLHive, Tapease, Simplifii-OS). Use when evaluating venture financial health, planning capital allocation, calculating contribution margin and CAC payback, or determining Default Alive versus Default Dead trajectory.
---

# Startup Runway, Cashflow Burn & Unit Economics Architecture

A rigorous quantitative financial framework for modeling **unit economics, cashflow burn rate, runway in months, and Zero Cash Date (ZCD)** across early-stage and growth-stage software ventures.

## When to Use

- **Runway & Cash Planning**: When determining how many months of operating capital remain before reaching the Zero Cash Date.
- **Unit Economic Audits**: When measuring contribution margins after variable infrastructure, API query fees, and payment gateway costs.
- **Default Alive vs Default Dead Modeling**: When assessing whether organic monthly revenue growth will outpace burn before cash reserves deplete.
- **Board & Executive Financial Reviews**: When preparing cashflow runway projections, break-even milestones, and hiring budget ceilings.

---

## Core Financial Framework

```
                          ┌────────────────────────────────┐
                          │     AVAILABLE CASH BALANCE     │
                          └───────────────┬────────────────┘
                                          │
                  ┌───────────────────────┴───────────────────────┐
                  ▼                                               ▼
     ┌─────────────────────────┐                     ┌─────────────────────────┐
     │    GROSS MONTHLY BURN   │                     │    MONTHLY CASH INFLOW  │
     │ Salaries · Cloud · SaaS │                     │ Recurring Subscriptions │
     └────────────┬────────────┘                     └────────────┬────────────┘
                  │                                               │
                  └───────────────────────┬───────────────────────┘
                                          ▼
                             ┌─────────────────────────┐
                             │     NET MONTHLY BURN    │
                             │  Gross Burn - Inflow    │
                             └────────────┬────────────┘
                                          ▼
                        ┌───────────────────────────────────┐
                        │      RUNWAY & ZERO CASH DATE      │
                        │ Cash / Net Burn  ·  Default Alive │
                        └───────────────────────────────────┘
```

---

## The Four Key Financial Pillars

### 1. Unit Economics & Contribution Margin
- **Contribution Margin**: $\text{Revenue per Unit} - \text{Direct Variable Costs (COGS)}$.
- **Direct Variable COGS**: Only costs incurred directly in delivering that specific unit (e.g. ASIC registry query APIs, LLM inference tokens, Stripe transaction fees). Excludes fixed engineering salaries.
- **LTV / CAC**: Target $\ge 3.0\times$ with a CAC payback period under 12 months (under 6 months for SMBs).

### 2. Burn Rate & Cashflow Velocity
- **Gross Burn**: Total monthly operational outflows (payroll, infrastructure, contractor fees, office, SaaS).
- **Net Burn**: Cash depleted per month after netting out cash received from customer payments.

### 3. Runway & Zero Cash Date (ZCD)
- **Static Runway**: $\frac{\text{Cash Balance}}{\text{Net Monthly Burn}}$.
- **Health Tiers**:
  - $> 18$ months: Comfortable Growth
  - $12 – 18$ months: Normal Operating Zone
  - $6 – 12$ months: Capital Action Window (fundraising or expense reduction)
  - $< 6$ months: Red Alert Zone (immediate burn compression)

### 4. Paul Graham's Default Alive Test
- Simulates month-by-month compound revenue growth against projected expenses. If current growth carries the company to break-even before cash depletes, the company is **Default Alive**.

---

## Portfolio Calculator CLI

Run the bundled calculator to forecast runway and unit economics for any portfolio project:

```bash
# Model AML Hive B2B compliance SaaS
python3 growth/startup-runway-and-unit-economics/scripts/calculate_runway_and_burn.py --preset amlhive

# Model Tapease merchant payments POS
python3 growth/startup-runway-and-unit-economics/scripts/calculate_runway_and_burn.py --preset tapease

# Model Simplifii-OS AI agent platform
python3 growth/startup-runway-and-unit-economics/scripts/calculate_runway_and_burn.py --preset simplifii

# Custom parameters with JSON output
python3 growth/startup-runway-and-unit-economics/scripts/calculate_runway_and_burn.py \
  --cash 150000 --gross-burn 20000 --revenue 8000 --growth 0.10 --json
```

---

## References & Models

- [Unit Economics Formulae & Direct COGS](./references/unit-economics-formulae.md) — Comprehensive reference for contribution margins, CAC payback, and LTV.
- [Runway & Burn Rate Model](./references/runway-and-burn-model.md) — Mathematical formulations for Zero Cash Date, Default Alive algorithms, and cash conversion cycles.
- [Project Portfolio Economic Profiles](./references/project-portfolio-profiles.md) — Detailed economic profiles and cost structures for AMLHive, Tapease, and Simplifii-OS.
