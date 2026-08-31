---
name: grill-me
description: This skill should be used when the user runs "/grill-me", asks to "grill me", "quiz me", "test my knowledge", "prep me for the investor/AUSTRAC/customer call", or "ask me hard questions about the product". Runs an adaptive, one-question-at-a-time oral exam grounded in docs/context.md and docs/product-brief.md (with docs/current_progress.md for live status), grades each answer against the source, cites where the answer lives, and ends with a scorecard of weak areas.
---

# Grill Me — Product Knowledge Drill

A spaced, adaptive oral exam that pressure-tests how well the user knows AMLHive. Use it to prep
for investor due diligence, an AUSTRAC/compliance conversation, a customer objection, or an
engineering handoff. Every question and every "model answer" must be grounded in the source
documents below — never invent facts. When the docs are silent or ambiguous, say so rather than
guessing.

## Source of truth (read these first, in this order)

1. `docs/product-brief.md` — MVP scope (in/out), 8 features, pricing/tiers, lifecycle, risk
   register (M/R/T/O/L/F), assumptions, competitors, roadmap phases, Definition of Done.
2. `docs/context.md` — mandate, architecture, tech stack, integrations, env, OpenSpec+TDD rules,
   data-residency callouts, security/PII rules.
3. `docs/current_progress.md` — live build status, change list, migration head, deploy backlog
   (use for "what's shipped / what's next" questions only).

Read the relevant document(s) **before** asking questions in a topic, and re-open them to grade.
Cite the section heading (and line area if useful) when you reveal the model answer.

## Topics

Let the user pick, or default to a mixed set. Cover these areas:

| Topic | Drawn from | Example angles |
|-------|-----------|----------------|
| **Scope** | brief §2 | What's in/out of MVP; the 8 features; why X is "Never Build"; tiers per feature |
| **Compliance / AUSTRAC** | brief §3, §5, risk reg | Tranche 2 obligations; CDD risk-tier engine; SMR/TTR/CBM deadlines; tipping-off; 7-yr retention; the closed G1–G10 gaps |
| **Pricing & business** | brief §1 | Tiers & prices, trial model (14-day floored at 1 Jul 2026, C54), kill signals, TAM/SAM, revenue scenarios |
| **Competitive** | brief §1, risk M-series | PEXA Clear, First AML, AML Hub, the AUSTRAC free starter kit; how AMLHive differentiates |
| **Architecture** | context.md | Stack (FastAPI/Next/Supabase/Fly), RLS multi-tenancy, data residency (`ap-southeast-2`, AU-only Bedrock), provider abstractions |
| **Risk register** | brief §4 | Given a risk, name probability/impact/response/residual; given a kill signal, state the trigger |
| **Process** | context.md | OpenSpec+TDD mandate; "spec wins"; status vocabulary; session start order |

## Run loop

1. **Set up.** Ask the user: which topic(s), how many questions (default 8), and difficulty
   (warm-up / interview / brutal). Confirm, then read the source doc(s) for the chosen topic(s).
2. **Ask ONE question at a time.** Number it (e.g. `Q3/8`), tag it with the topic and difficulty,
   and then **stop and wait** for the user's answer. Never ask the next question, and never reveal
   the answer, in the same turn as the question. Do not answer your own questions.
3. **Grade the answer** against the doc:
   - Verdict: ✅ Correct · 🟡 Partial · ❌ Off / missed.
   - **Model answer**, grounded in and quoting the doc, with the citation
     (`docs/product-brief.md § <section>`).
   - One sentence on what was missing or imprecise (for 🟡/❌).
   - If the user disputes the grade, re-check the doc and correct yourself if they're right —
     the doc is the arbiter, not your first take.
4. **Adapt.** Escalate difficulty after a ✅; drill a follow-up on the same area after 🟡/❌. Don't
   repeat a question already asked.
5. **Track** a running tally (correct / partial / missed) by topic.

## Scorecard (end of session)

Finish with:
- Score: `N correct, M partial, K missed` out of total.
- **Weak areas** — topics with the most 🟡/❌, each pointing at the exact doc section to review.
- **Two or three crisp "if they ask X, say Y" lines** for the weakest spots (interview-ready).
- Offer a focused re-drill on the weak areas only.

## Rules

- **Grounded only.** Every question and model answer must trace to the source docs. If you can't
  find it, don't ask it. If the docs conflict, surface the conflict (it may be drift worth fixing).
- **One question per turn**, then wait — this is an exam, not a lecture.
- **Be a tough but fair examiner.** "Brutal" mode asks the follow-up the investor/regulator would:
  edge cases, exact numbers, "why not the alternative".
- Keep the user honest on **exact figures** (prices, deadlines, thresholds, retention years) —
  these are where compliance and sales answers actually get judged.
