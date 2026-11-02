---
name: startup-premortem
description: >-
  Run an objective startup pre-mortem: assume the venture failed and shut down 6 months from now, then work backward to every specific reason it died, grounded in the actual plan documents. Produces a Failure Story, Hidden Fatal Assumptions, and Month 1 to 2 Early Warning Signals with thresholds. Use when asked to "pre-mortem", "post-mortem an idea", "assume it failed", "why will this die", or before a funding application, stage gate, or build decision.
---

# Startup Pre-Mortem

An evidence-grounded failure analysis. Not a forecast, a stress test: it names which assumptions, if wrong, kill the venture and what you would see first.

## When to Use

- A founder has a plan, pitch, or docs folder and wants the failure modes before committing money or build time.
- Before a stage gate (see [startup-idea-validation](../startup-idea-validation/SKILL.md)), an accelerator or grant submission, or starting a build.
- Do NOT use as a substitute for customer interviews. It finds what to test; it does not test it.
- For a hostile investor view use [startup-vc-skeptic](../startup-vc-skeptic/SKILL.md). For repo ingestion and figure checking first use [startup-idea-investigation](../startup-idea-investigation/SKILL.md).

## Procedure

1. **Read everything first.** Every file in the plan folder (docs, specs, code, application answers). Do not start from the founder's summary.
2. **Inventory evidence.** Count primary-evidence artefacts (interview logs, LOIs, replies, live integrations, revenue) versus desk-research documents. Record the ratio; it is usually the headline finding.
3. **Verify load-bearing facts externally** (policy dates, market counts, competitor status) with dated sources. Mark anything unchecked as UNVERIFIED. See [figure verification protocol](../startup-idea-investigation/references/figure-verification-protocol.md).
4. **Do the arithmetic yourself.** Recompute price versus customer spend, TAM/SAM/SOM, GTV to revenue, float, margins, payback. Use only the plan's own inputs first; contradictions in the plan's own numbers are the strongest findings.
5. **Walk the lenses** in [failure-mode-lenses.md](./references/failure-mode-lenses.md). For each, ask what in THIS plan fails, not what fails in startups generally.
6. **Write the three outputs** using [assessment-template.md](./references/assessment-template.md):
   1. **Failure Story**: month-by-month operational collapse, plus a ranked cause table and the branch if the main funding bet succeeds.
   2. **Hidden Assumptions**: table of ID, assumption, source in the plan, why fatal if false.
   3. **Early Warning Signals**: observable Month 1 to 2 metrics, how to measure, alarm thresholds, linked failure mode, and proposed kill or pivot criteria.
7. **Add "what would change my mind"** and a **limits** section (what the analyst could not see).

## Guardrails

- Ground every failure in a quoted detail of the plan. Reject generic tropes ("ran out of cash", "poor marketing") unless tied to a specific number or document.
- Never present a derived or unchecked figure as fact. Tag: VERIFIED, PARTLY VERIFIED, CONTRADICTED, UNVERIFIED, UNMAPPABLE.
- Thresholds are proposals; the founder sets final numbers. Record them as such.
- Save as a file in the plan's own folder (for example `docs/validation/`), labelled as an assessment, not a requirement.
- Do not use em dashes in prose written for Haris (global writing rule).
