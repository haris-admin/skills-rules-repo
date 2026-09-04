# AMLHive AI Governance Framework — v0.1 Draft (SEED REFERENCE)

> This is Haris's AMLHive-specific AI governance draft. Your task: read it as a REFERENCE, then produce the GENERIC multi-system framework document described in the prompt below.

## Purpose

AMLHive uses AI to assist people with compliance work. AI may organise, extract, translate or prioritise information, but it must not make an AML/CTF decision, create a final compliance record without review, or replace the customer's legal responsibility.

This framework applies to every production AI feature, material prompt/model change, and proposed new AI vendor.

## Current AI register

| Use case | Data involved | Risk | Required control |
|---|---:|---|
| Ownership-document extraction | Uploaded ownership and trust documents; may contain personal and compliance data | High | AI output is staged; evidence citations, deterministic ownership calculations, and human approval are required before promotion. |
| Trust-deed party extraction | Trust deeds and named-party data | High | Explicit consent, platform kill switch, spend cap, structured output, and human verification before any record is committed. |
| Screening-hit sub-triage | Client identifiers and sanctions/PEP/criminal-list context | High | Reading aid only: no hit may be removed, downgraded, or decided by AI; failure shows all high-priority hits. Production enablement requires compliance/legal prompt review. |
| Screening translation/transliteration | Screening-provider hit text, which may include personal data | Medium–High | Preserve original text; translation cannot block review or alter a decision; feature flag defaults off. |
| NVIDIA/Nemotron comparison | Synthetic test fixtures only | Evaluation only | No production routing and no real client data. Any live call outside the confirmed Australian boundary requires a separate, dated approval. |

## Non-negotiable rules

1. AI proposes; humans and deterministic rules decide.
2. No AI output may automatically file, approve, decline, screen, classify a person as sanctioned, or create a final UBO/compliance conclusion.
3. Client data, uploaded documents and compliance records must remain in an approved Australian processing boundary. They must never be sent to an unconfirmed or non-Australian provider.
4. Every production AI workflow needs a kill switch, a documented rollback path, and a named accountable owner.
5. Prompts, model IDs, output schemas and important validation rules are versioned. A material change is treated as a model change, not a routine copy edit.
6. Production logs and metrics must not contain document text, names, dates of birth, addresses, credentials, or other unnecessary personal data.
7. AI failures must fail safely: preserve the existing human-review path, show the source information, and never silently hide a compliance risk.

## Roles

- Accountable Executive: approves new high-risk AI use cases, vendors, material model changes, and any exception.
- Product/Engineering Owner: maintains the AI register, feature flags, technical controls, monitoring, and rollback.
- Compliance Reviewer: approves the compliance framing of high-risk prompts and reviews material evaluation results or incidents.
- Privacy/Security Reviewer: confirms data classification, residency, vendor terms, access controls, and retention before a new provider or region is used.

For the current stage, one person may hold more than one role, but the approval decision and the technical implementation evidence should be recorded separately.

## Required approval gate

Before a new AI feature—or a material prompt, model, provider, or region change—record:

- intended use and prohibited use;
- data categories sent to the model;
- model/provider, processing region, and residency evidence;
- risk level and human-review design;
- evaluation set, safety tests, and acceptance criteria;
- monitoring measures, kill switch, and rollback method;
- accountable executive, engineering owner, and compliance/privacy approver;
- customer disclosure or consent requirement.

High-risk changes require explicit approval before activation. New vendors or non-Australian routes require a separate dated decision; access provisioning alone is not approval to send data.

## Operating rhythm

Hold a 30-minute monthly AI review while the framework is new.

Review:

- every active AI use case and its feature-flag status;
- model, prompt and schema changes since the prior review;
- validation failures, timeouts, failed jobs, customer-visible incidents, and manual corrections;
- evaluation outcomes and any drift by prompt/model version;
- spend, volume, and unresolved risk decisions;
- whether any workflow has crossed its approved boundaries.

Immediately disable the relevant feature and investigate if there is a data-residency breach, unauthorised autonomous decision, critical evaluation failure, loss of human review, or a material privacy/security incident.

## Minimum evidence to retain

For each AI workflow, retain the approved register entry, change approvals, evaluation report, test evidence, version history, monitoring summary, incident records, and review minutes. Keep customer data out of governance reporting unless it is strictly needed for an investigation.

## When this becomes operational

This framework becomes operational when AMLHive has:

1. approved this charter and named the owners;
2. created and approved the five register entries above;
3. recorded the current feature-flag and production-status evidence;
4. run the first monthly review; and
5. applied this gate to the next material AI change.

Until then, AMLHive should describe itself as developing—not operating—an AI governance framework.
