# Investigate every error immediately — including pre-existing/old ones (all agents)

Human decision, 7 Aug 2026, from this session's `npx tsc --noEmit` run: a real type error in
`frontend/lib/auditTrailDisplay.ts:272` (`ActorClassifiable` missing `user_name`, even though the
function already read `e.user_name`) had been sitting in the tree, surfaced once already
(`frontend/prod_issues/issue-246-turnstile-csp-block-and-lighthouse-perf-regression.md`'s
verification section), and was initially written off there as "pre-existing, unrelated, not my
concern" instead of being investigated. It turned out to be a one-line, safe, correct fix
(`user_name?: string | null` added to the interface, matching the pattern already used for
`user_id`/`notes`) that had been silently failing `npm run build`'s type-check step the whole time.

## The rule

**When you encounter an error — a failing test, a `tsc`/build error, a console error, a lint
violation, a runtime exception, a CI failure — investigate it immediately, in the same session, to
at least a root-cause conclusion. This applies even when:**

- The error is on a file you didn't touch and isn't related to your assigned task.
- The error already existed before your session started.
- Another agent's or the human's in-progress, uncommitted work introduced it (this is a shared
  worktree — see `docs/agent_rules/git-commit-hygiene-shared-worktree.md` — pre-existing does not
  mean someone else is already handling it).
- Fixing it feels like scope creep against `docs/agent_rules/openspec-tdd-mandate.md`'s "work only
  the assigned task" discipline.

**"Investigate" is not optional busywork — it means read the error, find the actual root cause, and
reach one of these three outcomes, stated explicitly rather than silently skipped:**

1. **Fix it now**, if the fix is small, safe, and doesn't require a design decision (this session's
   `auditTrailDisplay.ts` fix: one added interface field, no behavior change, existing tests still
   pass, `tsc --noEmit` and `npm run build` go green). Record what you found and fixed.
2. **Log it** (a `prod_issues/` doc if it's a live production defect, or a `docs/technical_debt.md`
   entry if it's a code-quality gap that isn't safe to fix inline) when the fix needs a design
   decision, touches code outside your task's scope in a way `openspec-tdd-mandate.md` would flag,
   or is too large to fix opportunistically. **Logging is not a substitute for investigating** — you
   still need to have found the actual root cause, not just noted the symptom.
3. **Ask the human**, one decision at a time, if you genuinely cannot tell whether outcome 1 or 2
   applies (ambiguous root cause, or a fix that could ripple into other in-progress work in a shared
   worktree).

**What this rule forbids:** writing "pre-existing, unrelated to this change" (or equivalent) as a
reason to move on without having actually looked at the error. That phrase describes a fact about
timing, not a conclusion about root cause — this session's tsc error was pre-existing *and* a
one-line fix, and the two facts have nothing to do with each other. Only write "pre-existing" after
you've done outcome 1, 2, or 3 above, not instead of doing one of them.

## Relationship to other rules

- This is about **your own workflow discipline** when you personally observe an error signal
  (build/test/lint/console/CI output) — distinct from
  `docs/agent_rules/observability-and-error-management.md`, which is about the *application's own*
  runtime error handling (exceptions never swallowed, Sentry capture, etc.). Both apply; this one is
  narrower and about what you do the moment you see red output, regardless of whose code caused it.
- Does not override `docs/agent_rules/openspec-tdd-mandate.md`'s scope discipline — investigating is
  mandatory, but *fixing* something clearly out-of-scope for your assigned task still routes through
  outcome 2 (log) or 3 (ask) rather than an unbounded silent expansion of the diff. The line: a fix
  under ~a handful of lines with no design decision and no behavior change is safe to just do
  (outcome 1); anything bigger is outcome 2/3.
- Does not override `docs/agent_rules/git-commit-hygiene-shared-worktree.md` — investigating another
  session's in-progress error is fine; committing over their uncommitted work without checking is
  not (verify current state, e.g. `git status`/`git log -- <path>`, before assuming what you're
  looking at is still there to fix).

## Reference

Founding incident: `frontend/prod_issues/issue-246-turnstile-csp-block-and-lighthouse-perf-regression.md`
verification section (where the error was first spotted and deferred) →
`openspec/changes/396-homepage-performance-regression-round-2/tasks.md` (where it was actually
investigated and fixed, same session, after this rule was created). Claude: this doc + `CLAUDE.md`.
Cursor: `.cursor/rules/immediate-error-investigation.mdc`. Antigravity:
`.agents/rules/immediate-error-investigation.md`. Codex: `AGENTS.md`.
