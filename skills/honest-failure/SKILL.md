---
name: honest-failure
description: "Detect and block any code path that converts broken, missing, or truncated data into a rendered success state. ALWAYS load when reviewing CC-T diffs that add fallbacks, defaults, repair logic, empty catch blocks, merged pools, or best-effort rendering, and when scoping any fix for a trust-critical bug. Also load when Aaron asks is this safe to ship, review this diff, or a fix involves the words fallback, repair, default, merge, or sanitise. The one-sentence test question is whether the change converts a failure into silent success."
---

# Honest Failure

The single highest-damage bug class in Simplifii-OS is not crashes. It is success states built on broken data. Every major trust incident traces to it:

- **B-012:** rubric extraction failed silently, canvas FELL BACK to a merged course-level pool, student saw the WRONG rubric rendered confidently.
- **Notes-save:** localStorage write failed inside an empty catch, UI said saved, work was gone on refresh.
- **JSON repair layer (blocked 11 Jun):** bracket-closing truncated scaffolds would have rendered plans with amputated weeks and no error.
- **Guided plan fixture:** screen rendered fixture data ("due 2025-10-17") as if it were the student's real assessment.

For a neurodivergent student who has been burnt by systems before, one confidently-wrong screen ends the relationship with the product. An honest "this didn't work, try again" preserves it.

## The one-question test

For every diff, fallback, default, or catch block, ask:

**"If the data this renders is broken, missing, or partial, does the user see a failure state or a success state?"**

If the answer is success state, the change is blocked regardless of how helpful the fallback seems.

## What honest failure looks like

A blocked path must have ALL of:
1. A visible failure state in the UI (message + retry affordance, 44px target).
2. A log line naming the endpoint/component and the cause class (TRUNCATED, PARSE FAILURE, MISSING PREREQUISITE), with sizes/counts, never secrets.
3. No partial render. Either the full verified data renders or the failure state does. No "render what we got".

## Specifically banned patterns

- Empty or comment-only `catch` blocks on persistence or fetch paths.
- Falling back to a BROADER data pool when the specific one fails (course-level pool when assessment-level extraction fails = B-012).
- Repairing malformed structured data into parseable form (quote/bracket closing, trailing-comma stripping as a rescue path).
- Rendering fixture/sample data on any production path. Fixture in prod path = P0, always.
- Defaulting a missing value to a plausible one (4 weeks, today's date, first item in list) where the user will treat it as their real data.
- UI copy claiming an action succeeded before the artifact exists (saying "Saved" before the write confirms).

## Acceptable defaults (the boundary)

Defaults are fine when the user can SEE they are defaults and correct them: a pre-selected dropdown, a placeholder labelled as suggestion, an "estimated" badge. The line: a default presented as the user's own data is dishonest; a default presented as a suggestion is scaffolding.

## When CC-T proposes a rescue path

Standard reply shape: "That converts failure into silent success: [name the broken data it would render]. Replace with the honest failure state and log line. If the underlying failure rate is the real problem, fix the failure rate, not the visibility."
