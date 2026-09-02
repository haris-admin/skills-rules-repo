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

