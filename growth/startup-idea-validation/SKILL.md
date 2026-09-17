---
name: startup-idea-validation
description: >-
  Validate new startup ideas, assess problem-solution fit, formulate Riskiest Assumption Tests (RAT), conduct Mom Test customer interviews, or design pretotypes and fake door experiments. Use when evaluating a new business concept, testing customer willingness to pay, ranking venture assumptions, or establishing evidence thresholds before writing production code.
---

# Startup Idea Validation Architecture

A systematic, evidence-driven framework to validate startup concepts, kill non-viable ideas cheaply, and prove customer demand before investing engineering capital.

## When to Use

- **New Venture Ideation**: When evaluating whether an initial business hypothesis has commercial legs.
- **Pre-Build Due Diligence**: Before writing production code or committing engineering resources to a new product.
- **Customer Discovery Calls**: When preparing interview questions to prevent false positive flattery.
- **Assumption Prioritization**: When mapping venture risks across Desirability, Feasibility, Viability, and Distribution.
- **Go/No-Go Decision Gates**: When reviewing pilot data to determine whether to proceed, pivot, or kill an idea.

---

## The 5-Phase Validation Flow

```
┌─────────────────────────────────────────────────────────────┐
│ 1. ASSUMPTION EXTRACTION (Desirability / Viability / Tech)  │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ 2. RAT SCORECARD (Prioritize High Impact + High Uncertainty)│
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ 3. MOM TEST DISCOVERY (Interview Past Behaviors, Not Hopes) │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ 4. PRETOTYPING EXPERIMENTS (Fake Door, Concierge, Deposits) │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ 5. STAGE-GATE DECISION (Kill / Pivot / Proceed to MVP Build)│
└─────────────────────────────────────────────────────────────┘
```

---

## 1. Riskiest Assumption Testing (RAT)

Do not build an MVP to test an idea; build a **Riskiest Assumption Test**. An MVP often requires weeks of engineering; a RAT tests the single assumption that could sink the business in 48 hours.

### Categorization Matrix
- **Desirability**: Does anyone genuinely experience this pain point frequently enough to care?
- **Viability**: Will customers actually pay enough to create positive unit economics?
- **Feasibility**: Can we technically build and maintain the solution reliably?
- **Distribution**: Can we acquire customers affordably through repeatable channels?

Run the bundled scorecard CLI to rank your venture assumptions:

```bash
# Evaluate demo assumptions
python3 growth/startup-idea-validation/scripts/rat_scorecard.py --demo

# Evaluate a custom JSON list of assumptions
python3 growth/startup-idea-validation/scripts/rat_scorecard.py --file assumptions.json --json
```

See [RAT Scorecard Script](./scripts/rat_scorecard.py) for the underlying prioritization math.

---

## 2. The Mom Test Interview Standard

When speaking with prospective users:
1. **Never pitch the idea.** Ask about their day-to-day workflow and existing hacks.
2. **Anchor to the past.** "When did this last happen?" beats "Would you use this?"
3. **Seek skin in the game.** Demand time, introductions, or deposits. Compliments are noise.

Refer to the complete [Mom Test Interview Playbook](./references/mom-test-interview-playbook.md) for battle-tested questions and bad-question translations.

---

## 3. Pretotyping & Demand Signals

Before creating backend logic, test user intent with behavioral pretotypes:
- **Smoke / Fake Door Test**: Measure landing page call-to-action click rates (>8% target).
- **Concierge Test**: Manually perform the service for 5 customers to understand edge cases.
- **Deposit Test**: Collect a refundable $10–$50 deposit to verify economic intent.

Consult the [Pretotyping Experiment Catalog](./references/pretotyping-experiment-catalog.md) for 8 pretotyping archetypes and conversion benchmarks.

---

## 4. Stage-Gate Rubric

| Stage Gate | Required Proof | Action If Failed |
| :--- | :--- | :--- |
| **Problem Urgency** | $\ge 5$ prospects describe existing manual workarounds or budget spent on workarounds. | Kill or pivot to adjacent problem. |
| **Economic Intent** | $\ge 3$ prospective clients commit deposits, signed LOIs, or pilot agreements. | Re-index pricing or target customer segment. |
| **Distribution Feasibility**| Predictable CAC can be estimated from smoke test conversion metrics. | Re-evaluate channel economics. |
