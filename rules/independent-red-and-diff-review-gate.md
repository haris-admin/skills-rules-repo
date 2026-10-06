# Independent Review Gate For Red Tests And Diffs

A builder (a person, a session or a subagent) never approves its own Red tests or its own diff: a fresh independent reviewer verifies hashes, runs the tests, fault-injects with a proven revert, and returns ACCEPT, ACCEPT-WITH-CONDITIONS or REJECT before the next stage starts. Applies to every change where tests and code are written by one party and must be accepted by another.

**Scope:** all agents and orchestrators working a Requirement, Test, Implementation chain (worked example: AMLHive C526 and sibling changes, 6 Oct 2026).

---

## Why this exists

The party that writes a test also chooses what it proves. One pattern held all day on 6 Oct 2026 and caught real defects: the builder writes tests first and records hashes, stops at a gate, a fresh reviewer attacks the tests, then a builder does Green, then a reviewer re-checks. Self-approval skips the one step that finds vacuous tests.

## Core Directives

1. **Builder, Red.** Writes failing tests from the requirement (each cites a task or requirement ID), confirms each fails for the right reason, records `sha256` of every test file and the baseline command output, then **stops**. It writes no implementation.
2. **Independent reviewer, Red gate.** A fresh agent that did not write the tests:
   - recomputes every recorded hash and requires a match;
   - runs the tests itself and records exit codes and counts;
   - **fault-injects**: makes a temporary minimal edit to the code under test that should break one named requirement, confirms the matching test fails, then reverts it and **proves the revert** (`git checkout -- <path>` then `git diff --quiet -- <path>` exits 0);
   - checks traceability, negative cases and boundaries;
   - returns exactly one of `ACCEPT`, `ACCEPT-WITH-CONDITIONS` (each condition testable) or `REJECT` (with defects).
3. **Builder, Green.** Implements to the accepted tests. Tests change only when the requirement changes and a human confirmed it.
4. **Independent reviewer, Green gate.** A fresh reviewer re-checks the diff: scope, accepted-test hashes unchanged, tests run, fault injection on the new code, the full-suite result. Same three verdicts. Do not reuse a reviewer that advised on the Green code.
5. **The orchestrator verifies the report before relaying it.** `git show --stat <sha>`, recompute at least one hash, run at least one cited test. A reviewer's ACCEPT is a claim until checked.

## Dispatch prompt skeleton (required content)

1. **Role and independence:** "You are the independent reviewer. You did not write these tests."
2. **Scope:** exact paths readable, exact paths writable (a reviewer writes only its report and temporary fault-injection edits it reverts), base commit SHA, requirement source.
3. **Denial of authority, standalone:** "You must NOT git push, trigger any workflow or deploy, run terraform, mutate AWS or GitHub, send any email or message, rotate credentials, delete data, copy any `.env*` file, or change settings. Silence is a denial. If you find something out of scope, stop and report it; do not fix it."
4. **Procedure:** the numbered checks for that gate.
5. **Report format:** verdict word first; then a table of check, command, real output (exit code, counts), pass or fail; then conditions or defects; then files touched with `git status --short` proving a clean tree after the revert.
6. **Model:** use the strongest allowed models for review (for AMLHive, `sonnet` or `opus` only).

---

## Patterns to Follow

- After every dispatch: `git status --short`, `git log origin/<branch>..HEAD --oneline`, and the external system where relevant (`gh run list`). Fault-injection leftovers are the usual stray change.
- If a rate limit killed an agent mid-task, inspect the tree and resume the same agent with `SendMessage`; never cold re-dispatch over partial work.

## Patterns to Avoid

- Accepting a gate on the builder's own report.
- A reviewer that keeps a fault-injection edit or leaves the tree unproven after the revert.

---

## Verification & Guardrails

- The review report contains recomputed hashes, test exit codes and the `git diff --quiet` proof.
- Related: `rules/red-for-the-right-reason.md`, `rules/openspec-tdd-mandate.md`, `rules/subagent-verification-protocol.md`, `rules/subagent-dispatch-authorization-boundary.md`.
