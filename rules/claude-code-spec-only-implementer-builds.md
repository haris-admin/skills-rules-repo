# Claude Code specs it, designated implementer builds it (all agents)

**Canonical rule.** Mirrors: `.cursor/rules/claude-code-spec-only-implementer-builds.mdc` (Cursor),
`.agents/rules/claude-code-spec-only-implementer-builds.md` (Antigravity). If mirrors drift, this
file wins.

**Human decision, 22 Aug 2026 (the project lead, in-session via `AskUserQuestion`):** general standing rule,
all OpenSpec-governed changes — not scoped to security/PII-sensitive work only. Surfaced first for
`openspec/changes/426-audit-actor-identity-and-pii-redaction-vault/`, where the human twice told
Claude Code not to touch the code ("You create the spec and let Cursor work on the actual changes,
so don't make the changes yourself"; "make sure that you are creating a task for Cursor to do as an
agent. You don't do the actual changes"). Asked directly whether this was a one-off or a standing
policy, the human chose the general form.

**Human clarification, 27 Aug 2026 (the project lead, in-session via `AskUserQuestion`):** the implementer is
assigned per OpenSpec change and named in that change's `IMPLEMENTATION_BRIEF_<tool>.md`. Currently
**Cursor or Gemini Antigravity** on `yourapp1` — Cursor is **not** retired, and both tools remain
supported implementers. C461 is the first change assigned to Antigravity.

## The rule

For any **OpenSpec-governed change** (a `proposal.md`/`design.md`/`tasks.md` trio under
`openspec/changes/<id>-<slug>/`):

- **Claude Code authors the spec.** Requirement capture, options-based `design.md`, TDD-shaped
  `tasks.md` with task IDs — the full `openspec-tdd-mandate.md` process, run exactly as before,
  including the plan-approval gate (rule 2 of that mandate: 2-3 options, human picks, nothing
  proceeds until approved).
- **Code, config, SQL, migrations, and shell commands that appear in `design.md` or an
  `IMPLEMENTATION_BRIEF_<tool>.md` are the *specification of what the implementer writes* — a spec
  author (Claude Code or one of its subagents) does not apply them to the source tree, run
  `poetry lock`, create the test files, or edit `supervisord.conf` / Terraform / `pyproject.toml`.**
  The spec describes the change; the implementer makes it. See
  `docs/agent_rules/subagent-verification-protocol.md`'s third failure mode for the incident this
  exists to prevent.
- **The designated implementer builds the code** — the actual Red → Green → Refactor work `tasks.md`
  describes: writing code, migrations, running the test suite, **committing locally after each
  Green task** (`incremental-local-commits.md`). The implementer is named in the change's
  `IMPLEMENTATION_BRIEF_<tool>.md` (e.g. `IMPLEMENTATION_BRIEF_cursor.md` or
  `IMPLEMENTATION_BRIEF_antigravity.md`). Claude Code does not write the implementation itself once
  a plan is approved and handed off.
- Mark the assignment explicitly in the change's `proposal.md`/`tasks.md` (a short "Execution
  assignment: <implementer>" note near the top, as `426` and `461` do) so a future reader — human
  or agent — doesn't assume Claude Code already built it just because the spec exists.

## What this does not change

- **The plan-approval gate is unchanged and still Claude Code's job.** Claude Code still runs
  `AskUserQuestion`/structured Q&A for ambiguity, still writes the 2-3-option `design.md`, still
  waits for the human to approve before anything is marked ready for implementation. This rule
  moves *who writes the code*, not *who decides what gets built*.
- **The hotfix carve-out is unaffected.** A live production incident may still be fixed immediately
  by whichever agent is present (including Claude Code) — `openspec-tdd-mandate.md`'s carve-out
  (spec backfilled after) is untouched by this rule.
- **Non-OpenSpec-governed work stays with Claude Code as before** — this rule is scoped to
  `openspec/changes/` implementation specifically. It does not touch: content/marketing skills,
  doc-only edits, prod-issue triage and investigation, deploy skills (`/release-frontend`,
  `/release-backend`), diagnostic/read-only work, or verification/audit skills
  (`openspec-verify`, `code-review`, `prod-issue-verify`, `10-star-pathway`, etc.) — those are not
  "implementing an OpenSpec change," they're operating on work already implemented or auditing it.
  Also: **operational / agent-facing docs** (e.g. the Pluto instruction docs
  `docs/pluto_asic_ref_db_sync_instructions.md` / `docs/pluto_agent_instructions.md`) — when an
  OpenSpec change alters a contract these describe, the doc update is Claude Code's, not the
  implementer's; gate it to apply only after the change deploys.
- **Verification of the implementer's work is still Claude Code's job**, same as it already is for any
  agent's self-report per `docs/agent_rules/subagent-verification-protocol.md`'s "don't trust a
  stalled/self-reported result, verify directly" posture — extended here across agents, not just
  subagents. Before a change the implementer built is marked `status: implemented`, re-run its
  cited tests and check git history yourself (`openspec-verify` skill), exactly as you would for a
  Claude Code subagent's own claim.

## Why

The human's own reasoning in-session: this keeps Claude Code's role centred on requirement capture,
design-option framing, and the human-approval gate — the parts that benefit from Claude Code's
conversational planning loop — while implementation goes through the designated implementer's own
execution/testing environment. Not further elaborated beyond that in-session; if a future session
needs the deeper rationale, ask the human rather than inventing one.

## Related

- `docs/agent_rules/openspec-tdd-mandate.md` — the spec-writing process this rule's "Claude Code
  authors the spec" half still runs, unmodified.
- `docs/agent_rules/subagent-verification-protocol.md` — the verify-don't-trust posture this rule
  extends to cross-agent handoffs.
- `docs/handoff_gemini_antigravity_execution_order.md` — the standing implementer playbook for
  changes assigned to Gemini Antigravity.
- `openspec/changes/426-audit-actor-identity-and-pii-redaction-vault/` — the change that surfaced
  the initial execution-split human decision.
- `openspec/changes/462-execution-split-implementer-neutral/` — the change that clarified the
  per-change implementer assignment model.
