---
name: agent-orchestration-contracts
description: >-
  Use when designing or upgrading an AI pipeline from human-coordinated steps to
  autonomous, auditable agent decisions with explicit goal, handoff, and correlation contracts.
---

# Agent Orchestration Contracts

Replace the human-as-message-bus pattern with versioned, machine-readable
contracts. A contract states what an agent may decide, what another agent can
trust, and which combined signals warrant one accountable decision.

## Contract location and lifecycle

Store one version-controlled contract file per pipeline at
`.agents/contracts/<pipeline>.yaml`, beside the pipeline code. Treat changes to
authority, stop conditions, acceptance checks, or correlation logic as a
reviewable product and risk change. Version the contract; retain the version
and content hash in each run's evidence record.

| Rung | Contract | What changes | Required outcome |
| --- | --- | --- | --- |
| 4 — the Manager | Goal Contract | Hand over an outcome, not a procedure | Bounded agent decisions are measured and reviewable. |
| 5 — the Conductor | Handoff Contract | Agents exchange a verifiable baton directly | A consumer accepts an artefact without human relay. |
| 6 — the Ringmaster | Correlation Rule | Related signals become one decision | One owner receives one deduplicated, evidence-backed decision. |

Read [the contract schemas](references/contract-schemas.md) when authoring or
reviewing a contract. Read [the AML worked example](references/worked-example-aml-alert-triage.md)
when applying this to a regulated alert pipeline.

## Authoring procedure

1. Map the current pipeline: decisions, systems, human relays, authority, and
   evidence gaps. Use the assessment below to select only the next rung.
2. Create or revise `.agents/contracts/<pipeline>.yaml`. Declare every
   required field; do not infer authority, acceptance, or escalation from
   prompts or team habits.
3. Exercise the contract with a normal case, a boundary case, a duplicate
   delivery, a partial failure, and an escalation. The consumer must be able
   to verify its inputs without asking a person.
4. Review sampled evidence at the declared cadence. Tighten or expand the
   contract through a versioned change, never through an undocumented prompt
   exception.

## Ladder self-assessment

Place a pipeline at the highest row whose evidence is consistently true, then
build the item in **Next** before claiming the next rung.

| Rung | Observable state | Next |
| --- | --- | --- |
| 2 | An agent assists a person, but the person decides, copies outputs, and starts every next step. | Define a bounded stage input, output, and human approval point. |
| 3 | Agents perform bounded stages, but a person still routes work or translates context between stages. | Identify one recurring outcome and write its Goal Contract. |
| 4 | An agent owns a bounded outcome under measurable success criteria, guardrails, stop conditions, escalation, and review. | Replace one human relay with a Handoff Contract. |
| 5 | Producers deliver versioned artefacts directly to consumers; consumers verify acceptance and handle duplicates/failures. | Identify a multi-system pattern that should result in one decision. |
| 6 | Correlated sources, a join window, dedupe, severity, one decision output, and one accountable owner are operating. | Tune thresholds from evidence and govern contract changes. |

## Operating invariants

### Goal Contracts — rung 4

State the objective and how success is measured, then bound the agent with
constraints, authority limits (including spend, external communication, and
data), stop conditions, evidence requirements, escalation triggers, and a
review cadence. A sequence of instructions is not a goal. If the agent cannot
choose among permissible means while safely pursuing a measurable outcome, it
is still a stage workflow.

### Handoff Contracts — rung 5

Name the producer and consumer. Specify the exact artefact path and
schema/format, consumer-verifiable acceptance criteria, provenance,
idempotency key, deadline/SLA, failure/retry/escalation policy, and notification
target. A handoff is complete only after the consumer has recorded acceptance
or a contract-defined failure.

### Correlation Rules — rung 6

List the signal sources, correlation key, join window, severity mapping,
dedupe rule, one decision output, and accountable owner. Do not surface each
input as its own alert when the operational action should be singular.

### Idempotent and resumable handoffs

Derive a stable idempotency key from the business event, contract version, and
consumer action—not a run timestamp. Persist producer state and consumer
receipts keyed by it. On a retry, return the prior accepted result or resume
only unfinished work; never create a second external action, duplicate case,
or duplicate notification. Record attempt number, state transition, and
recovery decision in the evidence trail.

### Evidence-first design

Every rung-4-or-higher decision emits an auditable record before it is treated
as complete. Include contract ID/version/hash, correlation and idempotency
keys, input references and hashes, rule/model versions, decisions, confidence
or rationale, authority checks, timestamps, actor identity, and resulting
artefact or notification. Evidence must be immutable or tamper-evident and
retrievable by the accountable reviewer.

## Anti-patterns to remove

| Anti-pattern | Contract correction |
| --- | --- |
| Steps dressed up as a goal | Define an outcome, measures, boundaries, and freedom within them. |
| Implicit handoff | Publish the path, schema, acceptance criteria, SLA, and receiver. |
| No provenance | Require input references, hashes, transformations, and contract version. |
| Unbounded authority | Declare allowed and prohibited actions plus spend, comms, and data limits. |
| No stop condition | Make unsafe, uncertain, stale, and policy-conflict conditions explicit. |
| Human as the message bus | Make producer-to-consumer delivery, receipts, and failure handling machine-readable. |
| Correlated signals as separate alerts | Correlate, dedupe, and emit one owned decision with its combined evidence. |

## Completion check

- The contract is in `.agents/contracts/`, version-controlled with the
  pipeline, and references its schema version.
- A reviewer can determine what happened from the evidence record alone.
- A failed or repeated delivery produces no duplicated business action.
- Authority boundaries, stop conditions, acceptance checks, and the decision
  owner are explicit and testable.
