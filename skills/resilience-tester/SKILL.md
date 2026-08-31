---
name: resilience-tester
description: Recalculates the Burrito Path when life events interfere with the schedule (illness, burnout, lost time).
---

# Resilience Stress-Tester

The safety net. Real students get sick, get overwhelmed, lose three days. This skill recomputes a survivable path through the remaining work without pretending the lost time didn't happen.

## Steps

1. **The What-If engine.** Simulate a delay (default 48 hours; configurable). Recalculate the deadline path against the canonical reconciled briefs (`SovereignReconciler` output). Surface the new path with explicit deltas: which tasks now compete for the same week, which slipped, which became impossible at the current dial setting.
2. **Emergency Pareto.** When time-to-deadline drops below 1.5x the remaining word target divided by the student's average words-per-hour, trigger Emergency Pareto:
   - Hide the bottom 80% of micro-tasks ranked by Mark Density (use the `burrito-pareto-optimizer` skill's ranking).
   - Surface only the tasks required to clear a passing grade (50% by default; configurable per stream).
   - Mark hidden tasks as "deferred, recoverable" — never delete; the student must be able to re-expand once the crisis passes.
3. **Cognitive pacing.** Watch for frustration signals via `ExecutiveSpine` events:
   - More than three idle nudges in one focus session: drop `scaffoldingLevel` one notch.
   - More than two focus sessions ended early in a row: lower `gritLevel` one notch and surface a short break suggestion.
   - Section health regressing instead of climbing: pause auto-PlayTime grants (the dopamine loop is misfiring; reset before continuing).
4. **Honest reporting.** Never tell the student they're "back on track" when they aren't. The Resilience Report shows the path that exists, not the path the student wished for.
