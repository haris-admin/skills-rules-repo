---
name: wizard-cycle
description: >
  The default build cadence for every Simplifii-OS code change: an 8-phase
  plan, explore, test, implement, verify, document, attack, gate loop that makes
  the builder think before it codes. Load at the start of any build session,
  whenever a CC-T prompt is being written, when Aaron says "what's the cycle",
  "run the wizard", "before it builds", or when scoping any slice. Sits underneath
  build-loop-translator, cct-lookahead, honest-failure and verify-simple as the
  spine they hang on. The reversible-vs-dangerous call SIZES each phase; it never
  skips one.
---

# Wizard cycle: think before it codes

## Why this exists
The builder defaults to junior mode: read ticket, open file, type. Fast to start,
slow to finish, because it goes back and fixes what it broke. The senior move is to
plan, explore, verify assumptions, then type. We already do most of this. Naming the
eight phases stops any one from being skipped under time pressure, which is exactly
when it gets skipped.

This does NOT replace the GOVERNOR footer or the reversible-vs-dangerous routing. It
is the cadence those sit inside. The footer is the printed artifact of phases 1, 4, 5
and 6. The routing decides how heavy each phase runs.

## The 8 phases, and who owns each in the three-agent model

| # | Phase | What happens | Owner |
|---|---|---|---|
| 1 | PLAN | Read CLAUDE.md + the canonical Notion pages, find the slice, write a todo + size the blast radius. Output the plan to markdown (BACKLOG / scratch), never leave it in chat. | CC-T drafts, Chat sizes reversible vs dangerous |
| 2 | EXPLORE | Grep and PROVE every model, method, column and constant exists before referencing it. No hallucinated chains. This is print-state-first generalised to every symbol. | CC-T light on reversible; CC-M deep + file:line on dangerous |
| 3 | TEST FIRST | Write FAILING tests with mutation-resistant assertions, run them red. Pin real fixtures (e.g. the four BABS1202 docs). | CC-T writes; CC-M sets the grading rubric |
| 4 | IMPLEMENT MINIMUM | Smallest change to green. Print rollback SHA. Scope additions go to BACKLOG, not into the diff. | CC-T |
| 5 | VERIFY NO REGRESSION | Run npm run test:smoke (full), zero new failures vs the 45/4 baseline. | CC-T runs; CC-M batch-grades |
| 6 | DOCUMENT | Update SSOT (docs/state, docs/events) + inline notes while context is fresh. | CC-T |
| 7 | ADVERSARIAL REVIEW | Before commit, review as an attacker, not the author. | CC-M deep on dangerous; CC-T self-runs on reversible |
| 8 | QUALITY GATE | Loop: smoke + CC-M findings + (dangerous or user-facing) Aaron eye-verifies on live. Fix, repeat until clean. Push held until Aaron says go. | All four |

## Phase 7 is the one that earns its keep
Four questions before every commit:
- What happens if this runs twice concurrently?
- What if the input is null, empty, or negative?
- What assumption am I making that could be wrong?
- Would this embarrass us if it broke in front of a tester?
Plus the honest-failure test: does this change convert a broken, missing, or truncated
state into a rendered success? If yes, it is the bug, not the fix.

## Three non-negotiables this cadence adds
1. EXPLORE-VERIFY every symbol exists before you reference it (phase 2). Kills the
   hallucinated-method-chain class outright.
2. TEST-FIRST with mutation-resistant assertions (phase 3). Assert the side effect,
   not that it runs. assertEquals('done', x.status), never assert(true). A test suite
   should be a skeptic.
3. EXTERNALISE the plan to markdown (phase 1). Chat is for thinking, files are for
   preserving. If it matters, it lands in a file before the next phase.

## How routing sizes it
- REVERSIBLE slice (display, internal logic, unwired, unit-tested): CC-T runs all 8
  phases lightweight and STRAIGHT THROUGH, smoke each, no gate between. CC-M batch-
  grades once.
- DANGEROUS slice (touches a draft key, persistence, schema, a DB mutation, or a value
  hitting a user's eyes first time): phase 2 and phase 7 become the FULL CC-M pre-flight
  + line-by-line grade. CC-T proves state, smallest change, rollback SHA, GOVERNOR footer,
  then STOPS. The human gate sits at phase 8 (Aaron eye-verifies on live).

## Composition
- build-loop-translator turns this cadence into Aaron's three-line view + the builder's
  full prompt.
- cct-lookahead IS phase 7 run ahead of time (predict the traps before commit).
- honest-failure is the phase 7 success-masking check.
- verify-simple is how phase 8's result gets explained to Aaron in one action.
