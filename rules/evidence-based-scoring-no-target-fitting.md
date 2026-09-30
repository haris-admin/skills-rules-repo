# Evidence-based scoring: never fit a score to a requested target (all agents)

Applies whenever an agent scores, grades or sizes an idea, venture or plan (Gumby 1000-point, TAM/SAM/SOM, unit economics) and a human or document states a desired score, grade or size.

**Scope:** venture-scorer runs, portfolio scorecards, market-sizing work, pitch and partner packs.

---

## Why this exists

**30 Sep 2026, Undispute Pre-Dispute (Change 50 and the omnichannel radar):** the requester asked for the idea to "score at least 80% for each scale", then relaxed it to "two of them 70+ and overall 75+", then asked for a path "even if we need to reduce the scope" or "add more features". Two independent scorer runs reached the same result from opposite directions: the ceiling was about 755 at best, mostly from external gates no feature builds, and the requested shape was under 5% reachable. Answering "yes, here is 80%" would have produced a number that failed the first partner conversation. Separately, the requester then said the pilot merchant would not be paying, which invalidated a revenue assumption that both scorers had made.

## Core Directives

1. **Treat a target as a gap analysis, not a result.** State the current score, the target, the per-dimension gap, and the specific evidence that would earn each point. Do not write the target as the score.
2. **Never inflate to fit.** If the target is unreachable, say so plainly with the binding dimensions and a realistic range. Do not bank evidence that does not exist yet.
3. **Separate what scope or features can move from what only external gates can move.** Report both, with the share of the gap each explains. Here about 133 of 162 points came from external gates (acquirer answer, legal opinion, paying merchants, issuer acceptance).
4. **Score from an independent run.** The agent that builds the plan does not score it. Re-score after new evidence, not in advance of it.
5. **Record scoring assumptions and re-flag them when a constraint changes.** When the human states a fact that breaks an assumption (unpaid pilot, no budget, a licence blocker), mark every dependent score as unevidenced in the document and say it has not been re-scored.
6. **Label every input.** Tag figures as sourced, derived, assumption or knowledge-only. A search snippet, a 403 first-party page or the agent's own memory is not a primary source. Re-verify before any investor or bank use.
7. **State the grade table used.** Quote the framework's own bands (for example B is 600 to 699 and A-/B+ is 700 to 799) so a paraphrased "B, 700+" cannot slip through.
8. **Show the margin.** Scores carry about plus or minus 20. Do not report a 5-point change as a lift.

## Patterns to Follow

```text
Target 750. Now 593. Gap 157.
Evidence-driven dimensions: Build +25, Portfolio +12 (about 29 points net).
Gate-driven dimensions: Regulatory, Moat, Revenue, Timing (about 133 points).
Realistic: 684 (mid 2027, range 637 to 755). Requested shape: under 5%.
```

## Patterns to Avoid

```text
"Scores updated: every dimension now at 80%."   (target written as result)
Re-scoring the same document after the requester objects, without new evidence.
Averaging two scorers' figures to hide a disagreement; show both and why they differ.
```

## Verification & Guardrails

- Before publishing a score, confirm each dimension cites the evidence that would exist for it, and that no sentence presents a target as achieved.
- Grep the document for the words "reached", "achieved" and "now scores" and check each against evidence.
- If paired with a Cursor rule, update `cursor-rules/evidence-based-scoring-no-target-fitting.mdc` to match.
