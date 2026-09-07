---
name: openspec-workflow
description: Structure complex multi-agent features into structured proposals, design documents, executable tasks, and verification gates.
---

# OpenSpec Workflow

## Standard Lifecycle
1. **`proposal.md`**: Problem statement, scope boundaries, user value, observability requirements, and breaking changes.
2. **`design.md`**: Architectural diagram, data models, API contracts, migration strategy, error handling, and alternative options evaluated.
3. **`tasks.md`**: Atomically sequenced checklist with clear acceptance criteria and verification commands.
4. **Implementation Plan Gate**: For significant changes, author `implementation_plan.md`, present 2-3 evaluated options, and obtain user approval before writing code.
5. **Closeout & Verification**: Verify all task criteria with real command output and evidence before marking a change implemented.

## Verification anti-patterns — a checked box is not evidence (added 7 Sep 2026)

From a batch validation that found six `status: implemented` changes with acceptance criteria demonstrably unmet. When verifying (step 5) or reviewing another agent's build:

- **Reconcile every acceptance criterion to the actual committed diff.** `git show <commit>` for each AC — not the `[x]`. An AC naming an alarm, a migration, a base-image digest pin, a metric filter, or an infra resource is met **only if that artifact is in the diff**. The infra/observability ACs are the ones most often checked off without the artifact.
- **Confirm the cited commit contains the change.** A completion log citing commit X for a task while `git show X` doesn't touch those files is a HIGH finding — work leaks between commits and the earlier one still gets tagged and released.
- **A cited test must exist and assert the substance of the AC.** `grep` the test name (a log naming a non-existent test is a HIGH finding). Then read the body: a test that greps a `.sql`/`.tf` file's text does not satisfy an AC that requires executing it; a `mock.assert_called_with(...)` does not satisfy "writes a row / persists"; an integration test that *skips* under the default DB backend is not proof the policy works.
- **Requirement-change test sweep before commit.** If the change alters a contract (signature, return shape, removed fallback, guard swap), grep the whole suite for tests encoding the old contract and update them in the same change. `git stash && <run full suite> && git stash pop` on a clean checkout must be green before the log may claim "all tests pass".
- **`status: implemented` + a version bump requires every AC met.** Genuinely deferred work → `status: partial` with the remainder enumerated and no release yet.

## What counts as an OpenSpec-governed change — the carve-out is narrow

Content, doc-only edits, issue triage, deploy-runner skills, and read-only diagnostics are outside OpenSpec. That carve-out does **not** cover: a new or amended `openspec/specs/*/spec.md` (a spec is the output of a change, never hand-authored alone); a CI change that alters what the test suite does or gates (test DB version, coverage floor, a new build-failing scan); a new production-deploy behaviour; a new cloud resource / IAM policy / secret / env var. Each needs its own thin proposal/design/tasks.

## Tap-Ease repo layout (`openspec/`)

`openspec/config.yaml` (`schema: spec-driven`), `openspec/specs/<Capability>/`
(living specs — `Audit`, `Authentication`, `Cards`, `Devices`, `Integrations`,
`OCR`, `Payouts`, `System`, `Transactions`), and one dir per change under
`openspec/changes/<kebab-slug>/`:

| File | Required | Content |
|---|---|---|
| `proposal.md` | yes | `# Proposal: <title>`, `## Problem Statement`, `## Objectives`, `## System Impact` (Tables / Models / Routers / Services / Migrations Modified), optional `## Non-goals`. Under ~400 words. |
| `design.md` | yes | Real SQL + code snippets citing actual file paths / function names, a request-response flow, an edge-case table. |
| `tasks.md` | yes | `# Tasks: <title> (v<x.y.zz>)` then a `- [ ]` checklist. Include "Version bump — all 7 files" (see `tapease-backend-deploy`), "Docs update", "OpenSpec <Capability> spec", "Deploy to dev", "E2E on staging". |
| `.openspec.yaml` | yes | `version:`, `name:`, `description:` (one line). |
| `specs/<Capability>/spec.md` | only if an external API / DB contract changed | The delta: changed endpoints, before/after tables, request/response examples, error codes, backward-compat note. Pure internal fixes (logging, deploy tooling) skip this. |

Reference example: `openspec/changes/custom-term-id-and-serial-refund-endpoints/`.

## Retroactive backfill

Releases sometimes ship without a change dir. To backfill:

1. `git log --since=<date> --pretty="%h %ad %s" --date=short --stat` + `ls openspec/changes/` — map each shipped release to an existing dir (by topic, not name) or a gap.
2. For each gap, create the dir as above but mark shipped work `- [x]` in `tasks.md` (leave genuinely-open follow-ups `- [ ]`).
3. Cross-check contract details (e.g. `clover_sync_status`) against `docs/pos-clover-shift-sync.md` and `docs/pos-integration-api-guide.md`.
4. Report which releases you judged already-covered or not-needing a spec, and why.

Fan-out work — hand to a subagent when the user asks for it.

