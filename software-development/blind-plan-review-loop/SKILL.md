---
name: blind-plan-review-loop
description: >-
  Run repeated independent blind reviews of a long security or money plan until findings
  fall to named residuals: a fresh reviewer sees the plan and the decisions, not the
  author's claims, writes its own mutations, and the author fixes each finding with a test.
  Use before approving a database schema, sign-in, payments or any plan whose tests are
  embedded with hashes.
---

# Blind plan review loop

1. **Author** writes or revises the plan with embedded tests, files and a mutation suite, builds and runs them on a throwaway container, and recomputes every hash.
2. **Reviewer** (fresh agent, own worktree) checks the hash, reads the decisions and earlier reviews, diffs against the previous revision, runs the suite, writes ~15 mutations of its own, probes races, and reads final privileges from the catalogue. Output: one review file with ranked findings, each with a scenario and the smallest fix, and a plain verdict.
3. **Orchestrator** merges the review, asks the owner every decision the findings raise (one at a time, recommendation first, verbatim record), then briefs the next author with exactly those findings.
4. **Repeat** on the diff only. Stop when a round has no blocker and the rest are named residuals; then bring the final hash to the owner.

See [mutation rule](../../rules/a-plans-own-mutation-score-is-not-proof-the-reviewer-writes-fresh-mutations-and-survivors-are-findings.md) and [approval rule](../../rules/approving-a-plan-hash-decides-every-choice-its-tests-encode-so-list-and-ask-before.md).

Limits for every agent: no push, no production, no secrets, own containers only, edit only the one file.
