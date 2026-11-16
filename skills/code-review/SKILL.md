---
name: code-review
description: >-
  Conducts a structured multi-axis code review of a diff or pull request, whether written by you, another agent or a human. Use when asked for a code review, PR audit, pull request feedback or code quality inspection, before merging any change, when reviewing agent-written code, or when asked to review a diff even if it is pasted inline and looks quick to read.
---

# Code Review

Source: five-axis structure and change-sizing guidance adapted from `addyosmani/agent-skills` `code-review-and-quality` (MIT, (c) 2025 Addy Osmani), merged with this repo's earlier checklist.

Approve a change when it clearly improves overall code health, even if it is not how you would have written it. Do not wait for perfect. Do not rubber-stamp.

## Process

1. **Understand the context.** Read the spec, ticket or commit message first. What is this meant to do? Run `git diff` and `git status`; read the surrounding code, not just the hunks.
2. **Review the tests first.** Do they encode the requirement, cover edge and error paths, and fail without the change? A test that cannot fail proves nothing (`rules/a-ui-test-that-cannot-fail-proves-nothing.md`). Tests must trace to a requirement, and a test edited in the same change as the code it checks needs the requirement change to justify it.
3. **Review the implementation on five axes**, below.
4. **Verify the verification.** What did the author run? Did the build pass? Is there runtime evidence (output, screenshots, before and after)? "Tests pass" is a claim until you see the run.
5. **Label and order findings**, then give a verdict.

## The five axes

| Axis | Ask |
|---|---|
| **Correctness** | Matches the spec? Null, empty and boundary cases? Error paths, not only the happy path? Races or state drift? |
| **Readability and simplicity** | Could a new engineer follow it unaided? Could it be fewer lines? Do abstractions earn their cost (not before the third use)? Is a new conditional bolted onto an unrelated flow, or repeated on the same shape (a missing model)? |
| **Architecture** | Follows existing patterns, or justifies a new one? Dependencies flow one way? Is feature logic leaking into a shared module? Does a refactor reduce concepts or just move them? Are type boundaries explicit (no gratuitous `any`, casts, silent fallbacks)? |
| **Security** | Input validated at the boundary, secrets out of code and logs, authorization on every protected route, queries parameterized, external data treated as untrusted. Use `security-audit` for depth, and [the checklist](./references/checklist.md). |
| **Performance** | N+1 queries, unbounded loops or fetches, missing pagination, sync work that should be async, hot-path allocations. |

When you flag a structural problem, **propose the move**: replace a conditional chain with a typed model, collapse duplicate branches, separate orchestration from business logic, reuse the canonical helper, delete a pass-through wrapper, split a large file. Prefer the remedy that removes moving parts over one that relocates them.

## Change size

About 100 changed lines is good, 300 is acceptable for one logical change, 1000 is too large: ask for a split (stack, by file group, horizontal then vertical). Refactoring and feature work are separate changes. Large deletions and mechanical refactors are the exception. A small diff can still push a file past a healthy size (around 1000 lines total).

## Labelling findings

| Prefix | Meaning | Author action |
|---|---|---|
| **Critical:** | Blocks merge: security hole, data loss, broken behaviour, breaking change without migration | Must fix |
| *(none)* | Required change | Must fix before merge |
| **Optional:** or **Consider:** | Worth considering | Author decides |
| **Nit:** | Style or minor naming | May ignore |
| **FYI** | Context only | No action |

Lead with leverage: correctness and security, then structure, then nits. Do not bury a real issue under cosmetic ones. Before reporting, check each finding against callers, guards and tests that reach the code, and drop it if they rule it out. Mark defects that already existed in the base separately from regressions this change introduces.

## Honesty in review

- No "LGTM" without evidence you reviewed.
- Do not soften a real bug into "minor concern". Quantify: "this N+1 adds about 50 ms per row" beats "could be slow".
- Push back on clear problems and propose an alternative. Accept an override when the author has full context. Comment on the code, not the person.
- Facts and data beat opinion; the style guide beats taste; consistency is fine if it does not degrade health.
- Do not accept "I will clean it up later". Require it now, or a filed ticket with a reason.

## Dead code and dependencies

After a refactor, list newly unreachable code and **ask before deleting**. For a new dependency, check: is it needed, maintained, licensed compatibly, free of known advisories, and small enough to justify its weight. A dependency major upgrade ships alone (`rules/dependency-major-upgrades-ship-alone.md`).

## Output template

```
## Review: <change title>
Context: <what it does, spec or ticket>
Correctness / Readability / Architecture / Security / Performance: <findings, labelled>
Verification: <what was run, what is missing>
Verdict: APPROVE | REQUEST CHANGES, with the blocking items listed
```

## Review speed

Respond within one business day at most; quick individual replies beat a slow final approval. Ask for a split rather than reviewing one huge change.

## Common rationalizations

| Excuse | Reality |
|---|---|
| "The author is senior, it is fine" | Review the change, not the person. |
| "The tests pass" | Passing tests that cannot fail prove nothing. Read them. |
| "It is too big to review properly" | Then ask for a split. Do not approve unread code. |
| "I will mention it next time" | Deferred cleanup rarely happens. |

## Red flags

- Approval with no comment on tests or verification.
- A review that only says "this is complex" with no proposed move.
- Everything labelled required, so the author cannot tell what matters.
- Acceptance of a threshold, test or checker being weakened in the same diff (see `constraint-driven-development`).
- Agent-written code merged on the agent's own report (`rules/verify-external-agent-reports.md`).

## Verification

- [ ] Tests were reviewed before the implementation.
- [ ] All five axes were considered, with findings labelled by severity.
- [ ] The author's verification was checked, not assumed.
- [ ] Every Critical finding names the fix.
- [ ] Dead code was listed and not silently deleted.

## Reference

- [Comprehensive Code Review Checklist](./references/checklist.md)
- Related: `core-methodology/adversarial-reviewer`, `core-methodology/doubt-driven-development`, `software-development/requesting-code-review`, `compound-engineering/ce-code-review`
