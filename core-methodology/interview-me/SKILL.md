---
name: interview-me
description: >-
  Extracts what the owner actually wants, not what they think they should want, with a one-question-at-a-time interview that ends in a confirmed statement of intent. Use when a request is underspecified or conventional ("build me a dashboard", "make it faster") and who, why, success or the binding constraint is missing, when you catch yourself silently filling in requirements, or when asked to interview me, stress-test my thinking or check we are sure before a plan, spec or code exists.
---

# Interview Me

Source: adapted from `addyosmani/agent-skills` (MIT, (c) 2025 Addy Osmani), rewritten for this repo's rules.

People ask for what is conventional ("a dashboard") rather than what solves their problem. The cheapest time to find the gap is before any plan, spec or code. This skill produces one deliverable: a **statement of intent** the owner has explicitly confirmed.

It complements the global "ask, do not assume" rule. `grill-me` is a different tool: an oral exam on an existing product. This one runs before the thing exists.

**Do not use** for unambiguous asks, pure questions, mechanical edits, or when the owner asked for speed. **Needs a live person**: in a scheduled or autonomous run, record the missing intent as a blocker instead.

## Process

### 1. Hypothesis and a confidence number
Write your best one-sentence read and an honest 0 to 100 confidence. Below about 70, add what is missing.
`HYPOTHESIS: you want a way to answer "how are we doing?" in standup. CONFIDENCE: 30%, missing: audience, which metrics, what success looks like.`

### 2. One question at a time, each with a guess
Use AskUserQuestion where the answer is a choice, with your recommendation first. Format: the question, then `GUESS:` with the reasoning behind it. Wait for the reaction before the next question.
- A person reacts faster to a wrong guess than they produce an answer from nothing.
- Never batch. The third question often depends on the first.
- Sometimes guess in a direction you expect pushback on, so politeness does not pass for agreement.

### 3. Listen for "want" versus "should want"
Warning signs: best-practice words with no specifics ("scalable", "clean", "modern"), deference to convention ("the standard approach"), "I should probably". When you hear them ask: *If you did not have to justify this to anyone, what would you actually want?*

### 4. Restate in their words
When confidence is high, write it back in 5 to 8 lines they can confirm line by line: Outcome, User, Why now, Success, Constraint, **Out of scope**. Out of scope is mandatory; half of misalignment is silent disagreement about what is not being built.

Label any words that are your reading of free or voice text as an interpretation.

### 5. Require an explicit yes
These are not a yes: "whatever you think" (they are delegating, so re-ask as two concrete options), "sounds good", "sure, let's go", or silence followed by "okay start". Ask what they would refine. Fold corrections in and restate until you get a yes.

### 6. Stop the turn
On a yes: deliver the confirmed statement, offer the next paths (save to `docs/intent/<topic>.md`, draft an OpenSpec proposal, or add a backlog ticket per `requirements-backlog-first`), and **stop**. Start no downstream work in the same turn.

### The 95 percent test
You are done when you can answer yes to: *can I predict the owner's reaction to the next three questions I would ask?* If you cannot after several rounds, that is information about the ask. Say "I have asked N questions and still cannot predict you; here is what I think is unresolved", rather than grinding on.

## Example

`User: build me a dashboard for our metrics.` Without the interview the agent picks chart libraries. With it, question one (who is asking) reveals it is for the owner alone, question two reveals the real gap is "I have no list of running experiments". The artifact is a list, not a dashboard.

## Common rationalizations

| Excuse | Reality |
|---|---|
| "It is obvious what they want" | Then the three predictions are easy. Test them. |
| "I will ask everything at once to save time" | A batch gets skimmed and locks in the wrong framing. |
| "They said sounds good" | Not a yes. Ask what they would refine. |
| "I will start while they think" | Switching costs are real once building starts. |

## Red flags

- Questions with no guess attached.
- More than one question per turn.
- No "Out of scope" line in the restatement.
- Treating a polite agreement as confirmation.
- Continuing into spec or code in the same turn as the yes.

## Verification

- [ ] A hypothesis and confidence were stated up front.
- [ ] Questions were asked one at a time with guesses.
- [ ] The restatement covers outcome, user, why now, success, constraint and out of scope.
- [ ] The owner gave an explicit yes, recorded verbatim.
- [ ] The turn stopped after delivering the intent.

## See also

`requirements-backlog-first`, `grill-me`, `rules/no-fabricated-human-decisions.md`, `rules/decision-provenance-needs-a-record.md`.
