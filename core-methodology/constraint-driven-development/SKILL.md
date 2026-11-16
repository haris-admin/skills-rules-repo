---
name: constraint-driven-development
description: >-
  Writes a project's quality bar down as a checkable contract (CONSTRAINTS.md) and catches agents quietly lowering it. Use when no quality bar is written down, when asked to set up constraints, quality gates or standards, when coverage, performance or accessibility numbers are argued per pull request, when an agent keeps silencing checks, skipping tests or editing thresholds to get to green, or before running an unattended agent loop whose only guard is a test suite the agent also wrote.
---

# Constraint-Driven Development

Source: adapted from `addyosmani/agent-skills` (MIT, (c) 2025 Addy Osmani), rewritten for this repo's rules.

Spec says what to build. Tests prove it works. **Constraints say what "good enough to ship" means**, decided once, with numbers and a command that produces the verdict, so nobody argues it in a pull request and no agent can quietly relax it.

This sits under the global chain (Requirement, Test, Implementation). A constraint is a standing requirement, and a failing check means the code is wrong, not the check.

## When to use

- A project or feature starts and no quality bar is written down.
- Checks exist in CI but nobody can say which ones block a merge.
- An agent produces more code than anyone reads line by line.
- An agent proposes relaxing a threshold, adding a suppression or skipping a test instead of fixing the code.

Skip for throwaway spikes. If `CONSTRAINTS.md` already exists, read it and follow it; do not rewrite it.

Needs a live human for the interview. In a scheduled or autonomous run, apply the floor below, say so, and flag the rest for a person.

## Process

### 1. Detect before asking
Read the stack, test runner, linters, current coverage, CI files and agent harness files. Report what you found in two lines and ask only what is left.

### 2. At most four questions, each with a recommendation and a default
Ask one at a time (use AskUserQuestion). "I don't know" must still produce a working config.
1. Which dimensions beyond the floor: coverage on new code, security scanning, performance budgets, accessibility, architecture boundaries. State what each costs (performance and accessibility need a running URL).
2. On a failing check mid-task: block or warn. Default: block on the floor, warn on the rest for two weeks.
3. Target numbers, or measure today and hold that line. Default: measure and hold (a ratchet).
4. Slowest acceptable check at task end. Default: 90 seconds, unlimited in CI.

### 3. Write CONSTRAINTS.md at the repo root
Sections: **Floor**, **Enforced with numbers**, **Measured, not yet enforced**, **Exceptions**.

Floor (always on, no tooling needed):
- No new suppression comments (`@ts-ignore`, `eslint-disable`, `# noqa`, `# type: ignore`).
- No unimplemented stubs, no empty `catch`/`except: pass`.
- No skipped or deleted tests without a reason in the commit message.
- No secrets in source.
- The file itself is never weakened to make a change pass.

Every enforced row names **the command that produces the verdict** and **where it runs** (every edit, task end, CI, preview). A number with no command is an aspiration, not a constraint. Every number states its reason, or the next person deletes it.

Exceptions need an ID, the rule, the path, the reason, an owner and an expiry (default 90 days, never over a year).

Add one line to `AGENTS.md`: `Read CONSTRAINTS.md before writing code. Do not weaken it to make a change pass.`

### 4. Install a mechanism per dimension
Use the de facto tool, not a hand-rolled checker. Typical picks: `tsc`/`mypy`, the project's own linter, `pytest-cov`/`vitest --coverage` on **changed lines**, `gitleaks` with `--redact`, `osv-scanner`, Semgrep or Bandit, Lighthouse, axe-core, `size-limit`, `dependency-cruiser`, Stryker or mutmut on changed files.

Traps:
- Run gitleaks with `--redact`. Without it the secret lands in the transcript (see `rules/no-secret-fragments-in-tool-output.md`).
- Some scanners exit 0 on findings. Prove each gate by running it on a known violation (must fail), a clean control (must pass), a broken scanner (must fail), and a below-threshold finding (must pass).
- Scope slow checks to the diff. A check that stalls the agent gets switched off.
- Reuse the coverage report the suite already writes; do not run the suite twice.

### 5. Place each check by cost
Edit loop (seconds): types, lint, secrets, floor. Task end (under 90 s): related tests, changed-line coverage. Review and CI (minutes): everything, mutation, dependency audit. Preview deploy: Lighthouse, axe.

### 6. Guard the bar itself
At review time, diff against the branch point and look for the five cheapest roads to green:
1. **Threshold moved.** Budget lowered, severity dropped, a check removed from a faster stage.
2. **Test made easier.** `.skip`, deleted file, assertions removed from a surviving test.
3. **Checker silenced.** New suppression, `istanbul ignore`, `Stryker disable`.
4. **Work unfinished.** Throwing stub, swallowing `catch`, a TODO where code belongs.
5. **Exception appeared.** A new Exceptions row nobody discussed.

Tightening the bar is silent. Loosening it is loud, and per the global rule a changed requirement needs Haris's confirmation before the test or threshold changes.

Rank checks by circularity: **external** (axe, a vulnerability database, a real browser), **project** (lint rules a human owns), **suite** (your own tests, the only circular one). Require at least one external constraint.

### 7. Ratchets when there is no number
Record today's value and a direction ("must not fall"). Compare against the recorded value, never an aspiration. When a number improves, move the record up. Tolerance default 0.5%.

## Sane defaults (use only when the owner has no number)

| Constraint | Default | Reason |
|---|---|---|
| Changed-line coverage | 80% or more | forces a test, allows a config line |
| Project coverage | today's value, must not fall | no argument needed |
| Mutation score | 60% to start | typical for a suite never mutated |
| Dependency vulnerabilities | none high or above | below that is mostly noise |
| LCP / CLS | 2500 ms / 0.1 | Core Web Vitals "good" |
| Accessibility | zero critical or serious | moderate is debatable |

Defaults live in `CONSTRAINTS.md` with their reason, so they are configuration, not hardcoding (see `rules/no-hardcoding-configurable-or-admin-managed.md`).

## Common rationalizations

| Excuse | Reality |
|---|---|
| "We will add constraints once the code settles" | Code settles around whatever was allowed while it moved. |
| "The tests are the constraints" | Tests you wrote prove you agree with yourself. |
| "We cannot hit 80%" | Then set today's number and hold it. |
| "This will slow the agent" | Only if slow checks are in the edit loop. That is a placement error. |
| "Constraints will block shipping" | An exception with an owner and a date unblocks you. Deleting the rule unblocks everyone forever. |

## Red flags

- Interview ran past four questions.
- A budget the codebase already fails, with no plan.
- A number with no command behind it.
- Every constraint is judged by the project's own tests.
- `CONSTRAINTS.md` changed in the same commit as the feature that was failing.
- An exception with no owner or a far-off expiry.
- The agent proposes lowering a threshold instead of fixing the code.
- Someone starts using `--no-verify`.

## Verification

- [ ] `CONSTRAINTS.md` exists and every number has a stated reason.
- [ ] The floor passes on the current codebase.
- [ ] Each chosen dimension has a command that runs today and a stated place in the loop.
- [ ] Each enforced command was shown to fail on a violation and pass on a clean control.
- [ ] At least one constraint is external.
- [ ] Measured-only metrics record today's value and a direction.
- [ ] Exceptions have an owner and an expiry.
- [ ] `AGENTS.md` points at the file.

## See also

`rules/evidence-based-scoring-no-target-fitting.md`, `rules/prove-new-security-tests-bite-with-mutations.md`, `rules/ci-gate-commands-run-locally-before-push.md`, `rules/openspec-tdd-mandate.md`.
