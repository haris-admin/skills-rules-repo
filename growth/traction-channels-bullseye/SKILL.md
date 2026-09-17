---
name: traction-channels-bullseye
description: >-
  Prioritize customer acquisition channels using Gabriel Weinberg's 19 Traction Channels and 3-ring Bullseye Framework. Use when designing go-to-market (GTM) strategies, overcoming channel bias, scoring acquisition experiments with ICE (Impact, Confidence, Ease), or systematically testing channels to identify the single primary growth engine.
---

# 19 Traction Channels & The Bullseye Framework

A systematic growth methodology based on Gabriel Weinberg and Justin Mares' *Traction* to eliminate founder channel bias and identify the single most effective customer acquisition channel for a startup.

## When to Use

- **Go-To-Market (GTM) Planning**: When launching a new product or venture and deciding where to allocate initial marketing budget and effort.
- **Breaking Growth Plateaus**: When an existing acquisition channel saturates and the business needs a disciplined process to discover its next growth driver.
- **Experiment Prioritization**: When evaluating dozens of competing marketing ideas and needing an objective framework (ICE) to pick the top 3–5 candidate channels.
- **Product-Market Fit to Scale**: When transitioning from manual founder-led sales to scalable, repeatable channel distribution.

---

## The 3-Ring Bullseye Architecture

```
  ┌────────────────────────────────────────────────────────┐
  │              1. OUTER RING: WHAT'S POSSIBLE            │
  │          Brainstorm tests for all 19 channels          │
  │    ┌────────────────────────────────────────────┐      │
  │    │        2. MIDDLE RING: WHAT'S PROBABLE     │      │
  │    │      Run cheap, fast tests on 3-5 channels │      │
  │    │     ┌────────────────────────────────┐     │      │
  │    │     │   3. INNER RING: WHAT'S WORKING│     │      │
  │    │     │       Focus 80%+ on 1 channel  │     │      │
  │    │     └────────────────────────────────┘     │      │
  │    └────────────────────────────────────────────┘      │
  └────────────────────────────────────────────────────────┘
```

### 1. Outer Ring (What's Possible)
- Review all 19 channels systematically.
- Formulate at least one concrete test idea for every channel with zero preconceptions.

### 2. Middle Ring (What's Probable)
- Rank ideas using the **ICE framework**: $\text{ICE} = \frac{\text{Impact} + \text{Confidence} + \text{Ease}}{3}$.
- Select the top 3–5 channels and run low-cost validation experiments ($\le \$500–\$1,000$ or 2 weeks per test).
- The goal is **not** to scale the channel, but to answer: *Does this channel show promising unit economics?*

### 3. Inner Ring (What's Working)
- Focus 80%+ of marketing effort and capital on the single winning channel from the middle ring.
- Optimize and exploit that channel until diminishing returns (channel saturation) set in, at which point restart the Bullseye loop.

---

## Interactive Channel Scorer CLI

Score candidate traction channels and select your Middle Ring experiments:

```bash
# Run the default B2B SaaS channel ranker
python3 growth/traction-channels-bullseye/scripts/score_traction_channels.py

# Output JSON for automated reporting
python3 growth/traction-channels-bullseye/scripts/score_traction_channels.py --json
```

---

## References & Matrices

- [The 19 Traction Channels Matrix](./references/nineteen-channels-matrix.md) — Comprehensive breakdown of all 19 channels with startup costs, velocity, and B2B SaaS playbooks.
- [Bullseye Experiment Runbook](./references/bullseye-experiment-runbook.md) — Detailed instructions for running Outer Ring brainstorms, Middle Ring micro-experiments, and Inner Ring scaling.
