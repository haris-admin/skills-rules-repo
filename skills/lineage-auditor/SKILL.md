---
name: lineage-auditor
description: Trace every value rendered on screen back to its named data source, and flag any two surfaces showing contradictory values for the same fact. ALWAYS load when a screenshot or screen transcript shows a date, count, name, or status that might not match another surface, when AURA or any component states a fact, when auditing a new screen before testers see it, or when Aaron reports "it says X here but Y there". Also load before approving any feature that renders extracted document data. Contradiction between surfaces = two sources of truth = P1 minimum; fixture data on a production path = P0.
---

# Lineage Auditor

Single-source-of-truth disease is Simplifii's recurring root cause. Same fact, different surfaces, different values: the user cannot tell which is real, so they trust neither. Found instances:

- AURA greeting: "due 2025-10-17" (the guided-plan FIXTURE date) while the Plan canvas said "Date not set". One fact, two sources, one of them fixture.
- AURA: "I need your marking guide" while the Docs tab showed three rubrics uploaded (B-007 recurrence). AURA's greeting was hardcoded, not reading upload state.
- Guided planner: 19 rubric criteria (merged pool) while canonical extraction held 10 (B-012 pattern).
- Subjects view: "9039 days late" while the dashboard, wired to DateHelper, showed correct dates. One helper, two consumers, one unwired.

## The audit procedure

For any screen under review:

1. **List every rendered fact**: dates, counts, names, percentages, statuses. Not styling, facts.
2. **For each fact, name the source**: which table/column, which extraction field, which helper, or which hardcoded string. "I'd have to check" is the finding: have CC-T print the read path (file:line to data source).
3. **Cross-surface check**: does any other surface render the same fact? If yes, do they read the SAME source through the SAME helper? Different source or different transform = logged bug, even if values currently agree (they will diverge).
4. **Fixture scan**: grep the read path for fixture/sample/mock/test imports. Any hit on a production path = P0 INTERRUPT, regardless of current sprint.
5. **Staleness check**: is the value read once and cached (greeting composed at mount, never refreshed) while the underlying state can change (uploads arrive)? Hardcoded-at-mount facts about mutable state = B-007 class.

## Severity ladder

- Fixture data rendering in production path: **P0, interrupt current work.**
- Two surfaces, two sources, contradictory values visible to a user: **P1.**
- Two surfaces, two sources, currently agreeing: **P2, bank to BACKLOG.md immediately** (it is a divergence waiting for a deploy).
- One source, one consumer unwired from the shared helper: **P2** (the Subjects/DateHelper shape).

## The fix shape (always the same)

Never fix by editing the wrong value to match. Fix by making both surfaces read ONE canonical source through ONE helper, then delete the second source. If the canonical source is missing the fact (canvas says "Date not set" because extraction dropped it), the fix is upstream in extraction/ATTACH, and the surface shows the honest empty state until it lands: see honest-failure skill.

## CC-T prompt fragment

When commissioning a lineage fix, include: "For every value this screen renders, print value, source (file:line to table/field), and helper used. Any value whose source you cannot print is the bug."
