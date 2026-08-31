# OpenSpec + TDD Delivery Mandate (all agents)

**Canonical rule.** Mirrors: `.cursor/rules/openspec-tdd-mandate.mdc` (Cursor),
`.agents/rules/openspec-tdd-mandate.md` (Antigravity). Summarised in `AGENTS.md` (Codex),
`CLAUDE.md` (Claude Code), `GEMINI.md` (Gemini). If mirrors drift, this file wins.

**Human decisions recorded 2026-07-16 (the project lead, in-session):** hotfix carve-out is the only
exception to spec-first; the approval gate applies to the plan, not to every step; ambiguity is
resolved by structured one-question-at-a-time Q&A. These were explicit answers, not inferences.

**Human decision recorded 22 Aug 2026 (the project lead, in-session):** who authors this process's three
documents and who executes step 4 (TDD implementation) are now different agents — Claude Code
authors `proposal.md`/`design.md`/`tasks.md` and runs the plan-approval gate; **Cursor** executes
the implementation once a plan is approved. See
`docs/agent_rules/claude-code-spec-only-cursor-implements.md` for the full rule and its carve-outs
(hotfix path unaffected; non-OpenSpec-governed work unaffected). Rule 2's "execute end-to-end
autonomously" below now refers to Cursor's execution, not the spec-authoring agent's.

**Human decision recorded 22 Aug 2026 (the project lead, in-session):** local commits after each Green
task or small chunk, so there is a restore point — do not wait to be asked. Push still needs an
explicit ask. Canonical: `docs/agent_rules/incremental-local-commits.md`.

## 1. OpenSpec first — every change

- Every planned change starts as `openspec/changes/<id>-<slug>/` with `proposal.md`, `design.md`,
  and `tasks.md` **before any implementation**. No spec, no code.
- **Hotfix carve-out (the only exception):** a live production incident may be fixed immediately,
  but (a) the `prod_issues/` document must exist **before** the fix (existing `/prod-issue` rule),
  and (b) the OpenSpec record is backfilled in the same or immediately-following session. The spec
  is still mandatory — only its timing may trail the emergency.
- Chain of authority, one direction only:
  `Requirement (OpenSpec / human instruction) → Test cases → Implementation`.

## 2. Plan with options — the human picks before implementation starts

- Before implementing, write `implementation_plan.md` inside the change folder: 2–3 genuinely
  different implementation options, their trade-offs, and one clear recommendation with reasons.
- Present the options to the human and **wait for their choice. Nothing is implemented until the
  plan is approved.**
- Once the plan is approved, execute it autonomously end-to-end — tests, a **local commit after
  each Green task** (`docs/agent_rules/incremental-local-commits.md`; do not wait to be asked),
  any deploys the human ordered — without re-asking at each step. **Pushing still needs an
  explicit ask.** **A deviation from the approved plan reopens the gate**: stop and bring the
  deviation back to the human before continuing.

## 3. Never assume — clarify with structured Q&A

- An ambiguous requirement, conflicting specs, or any needed assumption means **stop and ask the
  human** — one decision at a time, with concrete options where possible (`AskUserQuestion` in
  Claude Code; plain numbered questions on other surfaces).
- Record each answer as a **dated human decision** in the change's documents. Never write a
  "Human decision" the human did not actually make in-session (standing rule — fabricating one is
  a serious defect).
- Assumptions are made **together with the human**. An unasked assumption baked into code is a
  defect even if the code works.

## 4. TDD — Red → Green → Refactor, aligned to the spec

- Tests come from requirements, never from code. Every test cites its task ID
  (e.g. `# T150.03`) or the explicit human instruction it encodes.
- Confirm **Red for the right reason** before implementing. Then the minimum implementation to go
  Green. Then refactor. The test is **does the failure name the thing you are about to build?** —
  not "is it an `AssertionError`". A missing-migration `FileNotFoundError` or a
  not-yet-created-symbol `ImportError` is a *correct* Red; a test typo, broken fixture or unrelated
  collection error is not. Full rule, worked examples and the guard-test
  "prove it is not vacuous" requirement: **`docs/agent_rules/red-for-the-right-reason.md`**
  (clarified 12 Aug 2026, C405 — this line previously said "not an import error", which is wrong
  when the artifact under test does not exist yet).
- **A failing test that is aligned with OpenSpec or the customer's requirement means the
  implementation is wrong. Fix the implementation. Never modify the test to make it pass.**
  When refactoring or code-splitting a file (e.g., extracting subcomponents from `app/page.tsx`),
  guardrail tests may inspect the entry file directly via `fs.readFileSync`. Agents MUST NOT change
  test file paths to point to extracted subcomponents; instead, ensure the entry file satisfies
  both the refactored architecture and all static-contract test assertions.
- Tests change only when the requirement changes — confirmed with the human first, and the
  requirement document is updated in the same commit as the test.

- **Assertions vs. test doubles — a narrow, easily-abused exception** (added 12 Aug 2026, C405).
  Refactoring the *shape of a call a mock simulates* is not the same act as changing what a test
  asserts; the rule above is about assertions. Permitted only when all four conditions in
  **`docs/agent_rules/test-doubles-vs-assertions.md`** hold — every assertion unchanged, forced by
  an approved decision cited by ID, the double faithfully simulates the new real shape, and it is
  stated in the completion log. Relaxing an assertion, widening a matcher, deleting a case or
  adding a skip is never covered.
- Coverage floors (see `AGENTS.md`) hold. An acceptance criterion is done only when real
  command/test evidence is recorded in the change's `tasks.md` completion log — "the code runs"
  is not evidence.

## 5. A mid-build spec revision does not erase what was already built and tested

C413 (16 Aug 2026): implementation was well underway — a full trigger-point wiring built and
Green — when an interactive design-review walk-through (8 findings) substantially revised the
spec, invalidating most of the already-built confirmation/reuse logic while leaving the
matcher/normalization work intact. This is a distinct situation from rule 4's "requirement
changed, update the test" — an entire in-progress build's wrapping changed, not one test's
assertion.

- **Never delete or silently rewrite prior completion-log entries** when a revision invalidates
  them. Mark them explicitly superseded — name the specific finding/decision that invalidated
  each one — directly above or in a clearly-labeled section before the old entries, so the record
  of what was actually built and when survives. Deleting them destroys the audit trail of a real
  build effort; silently leaving them un-marked lets a later reader (human or agent) trust a PASS
  row that is no longer true.
- **Explicitly state what survives the revision and what doesn't**, task ID by task ID, rather
  than leaving it implicit — C413's revision note said plainly "matcher + DOB tasks can stay;
  confirmation/reuse paths cannot." A reader should never have to infer this from diffing old vs.
  new design docs themselves.
- **Nothing gets to stay marked Green on the strength of pre-revision evidence.** Every task the
  revision touches needs fresh Red→Green evidence citing the revision explicitly, even if the
  underlying code turns out to need only a small change (C413's `kyb_service.py` trigger point
  turned out to need only a contract-signature fix, not a behavioral rework — but that was
  discovered by re-deriving it against the new spec and re-running its tests, not by assuming the
  old evidence still applied).
- **A revision this size is itself a human decision and must be dated and recorded** the same way
  the original plan approval was (rule 2) — not silently absorbed into the ongoing build as if it
  had always been the design.

## 6. A gap found during review never just gets mentioned and left — it gets tracked

**Human decision, 26 Aug 2026, refined same day:** any gap, gotcha, or missed requirement
surfaced while scoping, reviewing, or readiness-checking a change — whether found by a human, by
Claude Code, by a subagent, or by another agent's review — must land in a trackable record before
the session moves on. Never just note it in prose and leave it to be remembered.

**Default, preferred action: open a new OpenSpec change for it.** Not a fallback, not conditional
on size — the human's stated preference is to create a new separate OpenSpec change *whenever an
issue is found*, including small ones (`429a` below is the worked example: a 15-line data-file
backfill still got a full `proposal.md`/`design.md`/`tasks.md`). A placeholder change gets
`proposal.md` at minimum (provenance: what was found, when, by what review), and either
`design.md`/`tasks.md` if the work is already fully specified, or an explicit "not yet designed"
note if it isn't — matching the `430`/`432` precedent.

- **If the gap belongs to an already-existing change**, give the new record that change's number
  with a lowercase letter suffix — `429a-<slug>`, `429b-<slug>` — not a fresh top-level number.
  This repo already has this exact convention (`00a`–`00l`, `05a`–`05u`, `47b`, `58a`/`58b`,
  `66a`, etc.) — the lettered suffix keeps the lineage visible in the folder name itself. A
  genuinely new, unconnected gap gets the next free top-level number instead (check
  `openspec/changes/README.md`'s collision-hygiene rule — every long-lived branch, not just the
  current one).
- **If the gap surfaces from inside a dispatched subagent's own work** (not the orchestrating
  session's), dispatch a **separate** subagent to create the OpenSpec placeholder for that
  finding — don't have the original subagent context-switch mid-task to author it, and don't let
  the finding wait, unwritten, until that subagent's task finishes and reports back. The
  orchestrating session is the one that actually creates it (via a fresh subagent scoped to
  exactly that), not something folded into whatever the first subagent was already doing.
- **Emergency deferral, the only carve-out:** if there is active, urgent work already in progress
  when a gap surfaces (mirroring rule 1's hotfix carve-out), creating the OpenSpec record may wait
  until immediately after that urgent work concludes — not skipped, just sequenced after. This is
  about not interrupting a live emergency, not a license to defer routine findings.

**Fallback, only when a genuine new OpenSpec change truly cannot be created in the moment:** log
it in whichever of `docs/technical_debt.md`, `docs/context.md`, or `docs/current_progress.md`
actually fits the finding — and **explicitly tell the human** that further action is required and
has been placed as a pickup item for the next activity. Silence is never acceptable; if the
OpenSpec path is skipped, the notification is not optional in exchange.

**Why this rule exists:** found the gap this rule itself is meant to close, live, in the same
session — C429's own `AuditActionType` values (fifteen, on the actual recount — not the nine
first estimated) shipped to production without `ACTION_LABELS` entries, sat as a one-line "Next
pickup" note in `docs/technical_debt.md` §18 with no OpenSpec record, and the human had to
explicitly ask for it to be backfilled rather than it already being a trackable, actionable item.
A technical-debt entry that only describes a gap in prose, with no change record to execute
against, is exactly the shape of thing that gets mentioned once and then never picked up.
