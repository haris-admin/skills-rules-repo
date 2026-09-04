# AI Governance Framework — Generic Multi-System v1.0

**Owner:** Haris Habib / Accountable Executive  
**Jurisdictional posture:** Australia  
**Applies from:** [approval date]  
**Review cycle:** Monthly, with a weekly-ish agent-fleet review  
**Framework status:** Reusable operating scaffold for a small operator

---
## 1. Purpose

This framework governs how Haris's systems select, build, test, deploy, supervise, and retire artificial-intelligence capabilities. It is deliberately practical.
It is not a claim that AI is risk-free, a substitute for legal advice, or a 40-page corporate policy.
Its purpose is to ensure that AI creates useful assistance while people retain accountability, regulated decisions remain controlled, client data is protected, and internal autonomous agents cannot silently create unacceptable production, security, privacy, financial, or reputational risk.
This framework has two distinct use-case classes:

| Class | Meaning | Primary control objective |
|---|---|---|
| Customer-facing AI | AI that processes, generates, prioritises, translates, extracts, recommends, or otherwise assists in a customer product or customer workflow. | Do not let AI make regulated, legally material, or customer-impacting decisions without required human and deterministic controls. |
| Internal autonomous agents | Internal agents, automations, skills, crons, and memory/knowledge services that research, write, monitor, change systems, or act on behalf of the operator. | Keep agent autonomy bounded, attributable, reviewable, secure, and reversible. |
The two classes overlap where an internal agent helps operate a customer-facing system.
In that case, apply the stronger control from either class.

---
## 2. Scope

This framework covers every current, planned, evaluated, disabled, and retired AI use case in the following systems.

| System or estate | Current context | Framework application |
|---|---|---|
| AMLHive (amlhive.com.au) | Production AML/CTF compliance SaaS. AI assists with document extraction, trust-deed extraction, screening sub-triage, screening translation, and model comparison. The evidence pack is a core product feature; Pro is approximately A$299. | Customer-facing, high-consequence regulated use. |
| Tapease (tapease.com.au) | Merchant-payments platform for drivers using Clover Flex hardware, Fiserv processing, and Oxygen Global prepaid cards. Current AI use is minimal. | Presently low AI activity; future onboarding or risk AI is regulated-payments adjacent. |
| ExitLens AU | Portfolio idea or early product for AI guidance. | Planned or early customer-facing AI. |
| TokenPilot AU | Portfolio idea or early product, regtech-adjacent. | Planned or early customer-facing AI. |
| FinAI File AU | Portfolio idea or early product, regtech-adjacent. | Planned or early customer-facing AI. |
| CloudProof AU | Portfolio idea or early product, regtech-adjacent. | Planned or early customer-facing AI. |
| PayLicence | Portfolio idea or early product, regtech-adjacent. | Planned or early customer-facing AI. |
| Agent fleet and operating estate | Pluto, Mercury, six Mercury sub-agent profiles, OpenClaw agents, Codex CLI, DeepSeek Harness, cron jobs, Mempalace, Honcho, and the skills-rules-repo. | Internal autonomous-agent use. |
The framework applies whether the AI is a hosted large-language model, an embedded model, an API, an agent framework, a deterministic workflow with AI input, a local model, a vendor tool, a skill, a script, or a scheduled job.
It also applies to:

- a new model, provider, endpoint, region, agent profile, skill class, tool, or data source;
- a material prompt, system instruction, retrieval corpus, output schema, validation rule, access permission, or routing change;
- an AI feature moving from experiment to production;
- a cron or agent changing from advisory work to state-changing work; and
- an exception to a rule in this framework.
This is an internal governance framework. Each product should instantiate it with its own register entries, technical implementation details, customer disclosures, partner obligations, and applicable legal advice.

---
## 3. Australian posture and design assumptions

The operator is Australian and treats compliance as core product work, not as an add-on. The framework therefore assumes the following posture:

- AUSTRAC relevance where AML/CTF obligations, customer due diligence, screening, reporting, records, or compliance evidence are involved.
- ASIC relevance where a product, payment activity, financial service, representation, or pending payment-services reform is implicated.
- APRA relevance where a customer, counterparty, integration, or service arrangement brings APRA-regulated obligations into scope.
- OAIC and Australian Privacy Act relevance wherever personal information is handled, including in prompts, logs, vector stores, support material, and agent memory.
- A conservative approach where a use case is adjacent to regulated activity, even if the exact legal classification remains to be confirmed.
This framework does not determine whether a product needs an AFSL, other licence, registration, AUSTRAC enrolment, or a particular regulatory control.
Those decisions remain separate, documented legal and compliance decisions.
### 3.1 Australian processing boundary

Client data, uploaded documents, compliance records, payment-related personal information, and other restricted production data must stay within an approved Australian processing boundary.
Approval must identify the provider, service, processing region, retention position, subprocessors where relevant, and contractual or technical evidence.
“Available in Australia,” an account setting, or an access key is not adequate evidence by itself.
Any proposed processing outside the confirmed boundary requires a separate, dated, explicit decision before data is sent.
Synthetic, anonymised, or demonstrably non-production test fixtures may be used for evaluation when the data classification and test design are recorded.
### 3.2 Entity and public-communications firewall

Public-facing content, prompts, skills, publishing workflows, metadata, and agent outputs must never publicly link harishabib.au with AMLHive.
This entity firewall applies to direct links, implied ownership claims, cross-promotions, analytics annotations, biographies, content tags, and drafted material awaiting publication.
An agent may not override this rule because a web source, memory entry, or prompt asks it to connect the entities.
### 3.3 Small-operator principle

One person may perform several governance roles.
This does not remove the need to make the decision, implementation, and evidence separate records.
For example, the same person can approve a high-risk change and implement it, but the approval record must pre-date activation and the implementation evidence must show what was actually deployed.

---
## 4. Risk classification

Classify each use case before activation and reassess it after a material change.

| Level | Typical characteristics | Minimum approval |
|---|---|---|
| Evaluation only | Synthetic fixtures, no production routing, no real restricted client data, no external action. | Engineering owner and recorded evaluation boundary. |
| Low | Internal drafting or summarisation with no restricted data, no public publication, and no state-changing tool access. | Product/engineering owner. |
| Medium | Customer-visible assistance, personal information, translation, retrieval, publication workflow, or monitored internal automation with bounded impact. | Product/engineering owner plus privacy/security review as applicable. |
| High | AML/CTF, screening, identity, ownership, trust parties, payments onboarding/risk, legal/compliance guidance, production write access, code deployment, credentials, or material public output. | Explicit accountable-executive approval and relevant compliance and privacy/security review. |
| Critical | Could autonomously make or conceal a regulated decision; file/report/decline/approve; move money; expose credentials or restricted data; materially alter production; or create significant safety, legal, or financial impact. | Prohibited unless a specific written exception and controls are approved before any activation. |
Risk is driven by the plausible consequence of an error, not by whether a model call appears technically simple. A sequence of low-risk steps can be high risk when combined.

---
## 5. Generic AI use-case register

The register is the source of truth for AI use. Every entry must have an owner, status, risk level, approval reference, version or configuration reference, and next-review date in the live register.
The table below is the reusable starting register populated with known facts.

| Use case | Class | Status | Data involved | Risk | Required control |
|---|---|---:|---|---|---|
| AMLHive: ownership-document extraction | Customer-facing | Production or production-candidate; verify flag status | Uploaded ownership and trust documents; may include personal and compliance data | High | Stage output only; retain source citations; use deterministic ownership calculations; require human approval before promotion; kill switch and rollback. |
| AMLHive: trust-deed party extraction | Customer-facing | Production or production-candidate; verify flag status | Trust deeds, named-party data, and associated compliance information | High | Explicit consent where required; structured output; spend cap; kill switch; human verification before any record is committed. |
| AMLHive: screening-hit sub-triage | Customer-facing | Production or production-candidate; verify flag status | Client identifiers and sanctions, PEP, criminal-list, or screening-hit context | High | Reading aid only; AI must not remove, downgrade, or decide a hit; failure must show all high-priority hits; compliance/legal prompt review before production enablement. |
| AMLHive: screening translation and transliteration | Customer-facing | Production or production-candidate; verify flag status | Screening-provider hit text that may include personal information | Medium–High | Preserve original text; translation must not block review or change a decision; default feature flag off until approved; human review remains available. |
| AMLHive: NVIDIA/Nemotron model comparison | Customer-facing | Evaluation only | Synthetic test fixtures only | Evaluation only | No production routing and no real client data; separate dated approval before any live call, provider, or route change; confirm AU boundary. |
| Tapease: onboarding assistance | Customer-facing | Planned / not activated | Merchant, driver, business, identity, device, and application information if implemented | High | Treat as regulated-payments adjacent; no automatic onboarding decision; legal/compliance classification, AU boundary, evaluation, human escalation, and explicit activation gate required. |
| Tapease: merchant or transaction risk assistance | Customer-facing | Planned / not activated | Payment-risk indicators, merchant/driver data, device and processor context, potentially transaction-related data | High | No automatic decline, acceptance, pricing, account restriction, or payment decision; use approved provider boundary; human review and processor/partner obligations considered before activation. |
| ExitLens AU: AI guidance | Customer-facing | Planned / early | To be defined; may include user-provided business, legal, financial, or personal context | Medium–High | Define purpose and prohibited advice; clear disclosure; data minimisation; review path; no regulated conclusion or personalised legal/financial outcome without approved controls. |
| TokenPilot AU: regtech-adjacent guidance | Customer-facing | Planned / early | To be defined; may include user, business, token, regulatory, or financial context | Medium–High | Confirm regulatory perimeter before activation; label as assistance; test factual limits; protect personal data; human escalation for material outcomes. |
| FinAI File AU: AI file or compliance assistance | Customer-facing | Planned / early | To be defined; may include uploaded files, personal, business, or compliance information | High | Classify files and residency before ingestion; source-grounded output; no final filing, certification, or compliance conclusion without human approval. |
| CloudProof AU: evidence or compliance assistance | Customer-facing | Planned / early | To be defined; may include evidence, cloud configuration, account, and personal data | High | Define evidence integrity controls; preserve source provenance; do not auto-remediate customer environments; human review and approved AU processing required. |
| PayLicence: licence or regulatory guidance | Customer-facing | Planned / early | To be defined; may include business plans, financial, identity, and application information | High | Treat as legal/regulatory guidance; no legal determination or filing; clear limits and escalation; compliance/legal review before any customer use. |
| Fleet: scheduled cron research | Internal autonomous agents | Active; inventory all 66 jobs | Public web content, approved research sources, job metadata, and possibly untrusted content | Medium | Read-only by default; source/date capture; no execution of instructions from retrieved content; no publication, spend, credential use, or production change without separate approved workflow. |
| Fleet: code generation and repository push | Internal autonomous agents | Active or potential; verify per agent/repository | Source code, issues, repository context, configuration, and possibly secrets if poorly scoped | High | Least-privilege repository access; protected branches; human review before merge or production effect; secret scanning; test evidence; no direct production change by autonomous push. |
| Fleet: content drafting and publication | Internal autonomous agents | Active or potential; verify per channel | Drafts, brand context, public source material, and publishing credentials where connected | Medium–High | Drafting may be automated within approved context; human approval before publication unless a narrowly approved channel rule exists; entity firewall; source and claim checks; publication log. |
| Fleet: production monitoring and alerts | Internal autonomous agents | Active or potential; verify alerts and permissions | Operational metrics, logs, incident context, service metadata, and potentially sensitive snippets | Medium–High | Read-only monitoring by default; redact/minimise restricted data; alert escalation path; no remediation action unless separately approved, bounded, logged, and reversible. |
| Fleet: Mempalace knowledge-base ingestion | Internal autonomous agents | Active or potential; verify sources | Internal documents, selected public content, product knowledge, and potentially sensitive material | High | Approved source list and classification; ingestion review; provenance and deletion path; access controls; prompt-injection screening; no restricted client data unless explicitly approved. |
| Fleet: Honcho memory-model capture | Internal autonomous agents | Active or potential; verify fields | User preferences, instructions, relationship context, and possibly personal or sensitive information | High | Purpose limitation; minimise and classify fields; consent/notice where required; retention and deletion rules; prohibit storage of secrets, credentials, and unneeded restricted data. |
| Fleet: skills-rules-repo skill changes | Internal autonomous agents | Active | Skill definitions, rules, tool permissions, templates, and agent operating instructions | High | Git history, peer or accountable-owner review, version pinning where practical, test run, change approval, and rollback. |
| Fleet: external-model or tool routing | Internal autonomous agents | Active or potential; verify per provider | Prompts, task context, tool inputs, metadata, and potentially restricted data | High | Provider/region approval; data allow-list; AU boundary where client/restricted data is involved; rate and spend controls; credentials scoped per service. |
### 5.1 Register operating notes

The live register should add, at minimum, these fields to each row:

- unique identifier;
- product or fleet lane;
- accountable executive and implementation owner;
- status: proposed, evaluation, approved-not-enabled, active, paused, retired, or rejected;
- data classification and source;
- provider, model ID, model version, endpoint, and processing region;
- prompt, schema, retrieval corpus, skill, and code version references;
- human-review point and prohibited autonomous outcomes;
- feature flag, kill switch, rollback method, and test environment;
- evaluation reference, acceptance criteria, and latest result;
- monitoring metrics and alert owner;
- approval reference, approval date, exception reference if any, and next review date; and
- customer disclosure, consent, contractual, or partner-control requirement.

> **Status convention:** “planned,” “early,” “evaluation only,” and “production-candidate” do not authorise production data use or activation.
>
> Only an approved and explicitly enabled register entry does that.
### 5.2 Distinct treatment of the internal agent fleet

The internal fleet is a use-case class in its own right.
It is not merely developer tooling because it can write code, draft public content, monitor production, run recurring research, use skills, retain knowledge, and touch production repositories and AWS credentials.
The known fleet components include:

| Lane | Known components | Governance focus |
|---|---|---|
| WSL Hermes | Pluto | Task scope, tool permissions, repository and AWS access, activity logs. |
| Windows Hermes | Mercury and six profiles: Sol, Vulcan, Aurora, Lumen, Vigil, and Caduceus | Profile purpose, tool access, role separation, output review, and escalation. |
| OpenClaw | Gumby, Brainy, Jonny-Quest, and Tracker | Task allow-lists, source trust, publishing/action controls, and logs. |
| Coding agents | Codex CLI with GPT-5.6-luna and GPT-5.6-terra; DeepSeek Harness (dsh) | Repository, test, branch, dependency, secret, and deployment controls. |
| Scheduled automation | 66 cron jobs | Job inventory, owner, schedule, inputs, permissions, outputs, failure alert, spend cap, and last-review date. |
| Knowledge and memory | Mempalace knowledge base; Honcho user memory model | Data classification, provenance, retention, retrieval boundary, correction, and deletion. |
| Skills and rules | skills-rules-repo with 279 skills | Provenance, code review, capability classification, version history, and safe rollout. |
No fleet component is exempt because it is internal, familiar, inexpensive, or normally runs unattended.

---
## 6. Non-negotiable rules

These rules apply to all systems unless a stricter product or partner control applies.
### 6.1 Decision and outcome controls

1. **AI proposes; humans and deterministic controls decide.**
   AI may organise, extract, translate, summarise, compare, recommend, draft, or prioritise information within an approved use case.
   Accountability for the outcome remains human.

2. **AI must not autonomously make a regulated, legally material, or final customer decision.**
   Without a specific approved exception, AI must not automatically file, report, approve, decline, onboard, offboard, screen, classify a person as sanctioned, change a risk rating, determine a UBO, create a final compliance conclusion, set a payment outcome, move money, or create a final legal/financial outcome.

3. **High-risk outputs require a visible human-review path.**
   The reviewer must be able to see relevant source material, the AI output, uncertainty or failure state, and the action they are being asked to take.
   The workflow must not hide, silently downgrade, or make inaccessible a risk that the human would otherwise review.

4. **AI failures fail safely.**
   A timeout, malformed response, provider outage, guardrail failure, or validation failure must preserve the prior safe workflow.
   It must not silently create a decision, hide a high-priority screening hit, overwrite a record, or substitute fabricated output for missing evidence.
### 6.2 Data, privacy, and security controls

5. **Use only approved data in approved processing boundaries.**
   Client data, uploaded documents, compliance records, and restricted production data remain in the approved Australian processing boundary.
   Do not send them to an unconfirmed provider, account, endpoint, region, evaluation environment, model, vector store, or agent memory.

6. **Minimise data and prevent sensitive leakage.**
   Send the least data needed for the task.
   Production logs, prompts saved for debugging, metrics, traces, tickets, screenshots, and governance reports must not contain document text, names, dates of birth, addresses, credentials, payment details, tokens, or other unnecessary personal or restricted data.

7. **Credentials are never agent memory or prompt context.**
   Secrets, AWS credentials, API keys, passwords, private keys, session tokens, and customer access tokens must be stored and supplied only through approved secret-management and runtime mechanisms.
   They must not be copied into skills, knowledge bases, Honcho memory, prompts, chat transcripts, test fixtures, issue descriptions, or generated code.

8. **Use least privilege and separate environments.**
   Development, test, staging, and production must have separate credentials, permissions, data sets, and where practical separate accounts or projects.
   An agent's tool access must be limited to the smallest scope, repository, environment, and duration required for its approved lane.
### 6.3 Transparency, change, and control controls

9. **Every production AI workflow has an owner, kill switch, and rollback.**
   The owner must be named in the register.
   Disabling the workflow must be practical under incident conditions, and the documented rollback must restore a known safe state.

10. **Material AI configuration is versioned and reviewable.**
    Version prompts, model IDs, schemas, retrieval settings, validation rules, skills, agent profiles, tool permissions, and important policy instructions.
    A material change is a governed change, not a routine copy edit.

11. **Do not treat access provisioning as approval.**
    An API key, provider account, repository permission, AWS role, or installed skill authorises nothing beyond the approved use-case entry.
    A separate dated approval is required to activate a new provider, region, agent capability, external integration, or production data route.

12. **Customer and public communication must be accurate and bounded.**
    Do not present AI assistance as a substitute for professional judgement, legal advice, a regulated determination, or a guarantee of compliance.
    Apply the entity firewall: never publicly link harishabib.au and AMLHive.
### 6.4 Internal autonomous-agent rules

13. **Human approval comes before production-affecting autonomous action.**
    Agents may inspect, draft, test, and recommend within their approval scope.
    Before an action can affect production, customer data, live configuration, deployment, customer communication, access permissions, billing, or a public claim, a named human must approve it unless a narrow pre-approved action rule explicitly permits that exact action.
    Pre-approval must define scope, conditions, reversibility, monitoring, and an expiry or review date.

14. **No undisclosed autonomous spend.**
    No agent, skill, cron, or external tool may create unapproved spend, subscriptions, paid API usage beyond an approved cap, cloud resources, purchases, credits, transfers, or financial commitments.
    Approved recurring costs require an owner, cap, alert threshold, and a way to stop future expenditure.

15. **Agent work must be sandboxed and attributable.**
    Use isolated workspaces, short-lived credentials where practical, allow-listed tools and destinations, branch protections, and distinct identity or service accounts for material automation.
    Every material action must be traceable to an agent/profile, skill or job, human initiator or owner, timestamp, inputs category, and result.

16. **Skills, prompts, rules, and artifacts need provenance.**
    Treat a skill, imported prompt, retrieval source, workflow template, plugin, model adapter, and generated executable artifact as a supply-chain input.
    Record where it came from, its purpose, version or commit, reviewer, granted capabilities, and known data/tool access.
    Do not enable unreviewed executable or action-capable artifacts in production.

17. **Agents must expect prompt injection and data poisoning.**
    Web pages, emails, documents, repositories, tickets, tool output, retrieved knowledge, and embedded metadata are untrusted instructions unless approved by the governing task and trusted source controls.
    Agents must not follow retrieved instructions to reveal secrets, alter their authority, install software, run commands, exfiltrate data, or bypass review.
    Ingestion workflows must preserve provenance, distinguish source content from system instructions, and allow suspect content to be removed.

18. **Autonomy may not evade review.**
    Splitting a material action across agents, cron jobs, sub-tasks, or low-risk tool calls does not avoid the approval gate.
    The owner assesses the end-to-end outcome and combined permissions.
### 6.5 Prohibited patterns

The following are prohibited unless a written exception is approved before use:

- giving a customer-facing AI feature unrestricted production write authority;
- allowing an agent to merge directly to a protected production branch or deploy to production without the required human approval;
- sending restricted data to an unapproved provider or unconfirmed region;
- using real client data in an evaluation that is approved only for synthetic fixtures;
- storing secrets in Mempalace, Honcho, skills, prompts, source code, logs, or tickets;
- allowing an agent to spend funds, acquire a subscription, provision paid infrastructure, or move funds without explicit approved authority;
- publishing content autonomously when it could create a regulated claim, customer commitment, entity-firewall breach, or material reputational impact;
- creating a final AML/CTF, sanctions, payment-risk, legal, or compliance outcome solely from AI output; and
- disabling logging, approval records, or safety controls to make automation easier.

---
## 7. Roles and accountability

The roles below are functional roles, not necessarily different people. At the current small-team stage, Haris may hold all four.
The live record must still show who acted in each capacity and link the separate decision and implementation evidence.

| Role | Core accountability | Typical current holder | Cannot delegate away |
|---|---|---|---|
| Accountable Executive | Accepts risk; approves high-risk use cases, material changes, vendors, exceptions, and activation. | Haris Habib | Final accountability for scope, risk acceptance, and resource allocation. |
| Product/Engineering Owner | Maintains register, architecture, flags, safeguards, tests, monitoring, rollback, and implementation evidence. | Haris or delegated technical owner | Accurate technical control implementation and current system status. |
| Compliance Reviewer | Reviews compliance framing, prohibited outcomes, human-review design, regulated-domain evaluation, and material incidents. | Haris acting separately or an appropriately qualified reviewer | Whether the workflow remains consistent with the intended compliance posture. |
| Privacy/Security Reviewer | Reviews data classification, AU boundary, provider terms, access, secrets, retention, logging, and incident implications. | Haris acting separately or an appropriately qualified reviewer | Whether the proposed processing and access controls are acceptable. |
### 7.1 Fleet-lane accountability map

Each lane needs a named current owner in the live register.

| Fleet lane | Accountable owner responsibility | Implementation owner responsibility |
|---|---|---|
| Pluto / WSL Hermes | Approves its task classes, repository and AWS scope, and any production-capable tools. | Maintains isolation, configuration, logs, and kill access. |
| Mercury and Sol, Vulcan, Aurora, Lumen, Vigil, Caduceus | Approves each profile's purpose, authority boundary, and escalation route. | Maintains profile prompts, tools, permissions, evaluation, and activity record. |
| OpenClaw: Gumby, Brainy, Jonny-Quest, Tracker | Approves source, publishing, research, and action boundaries per agent. | Maintains jobs, source allow-lists, content review queue, and logs. |
| Codex CLI: GPT-5.6-luna and GPT-5.6-terra | Approves repository classes, review rules, and any connected production access. | Maintains branch controls, test gates, secret scanning, and coding-agent configuration. |
| DeepSeek Harness (dsh) | Approves data boundary and workloads, especially any code or context sent externally. | Maintains provider route, access scope, logging, and evaluation. |
| 66 cron jobs | Approves job purpose, frequency, data source, spend, and action class. | Maintains inventory, failure alert, outputs, credentials, and disable procedure. |
| Mempalace | Approves knowledge categories and access boundary. | Maintains source provenance, ingestion, retention, retrieval controls, and deletion process. |
| Honcho | Approves memory fields, purpose, retention, and correction/deletion approach. | Maintains field allow-list, access controls, export, and deletion process. |
| skills-rules-repo / 279 skills | Approves new high-impact skill classes and exceptions. | Maintains Git history, review records, tests, versioning, and rollback. |
### 7.2 Separation of records when one person holds multiple roles

For a high-risk change, record at least:

1. the accountable decision to proceed, including conditions;
2. compliance and privacy/security review observations or sign-off;
3. the implementation change reference, tests, configuration version, and flag;
4. the activation confirmation; and
5. the first post-activation monitoring review.
An email, issue, pull request, dated decision log, or signed register record can be sufficient if it contains the required evidence and is retained.

---
## 8. Required approval gate

Complete this gate before activating a new AI use case or materially changing an active one. Examples of material changes include a model/provider/region route, a prompt that changes behaviour or data disclosure, a new retrieval corpus, new write access, an output-schema or validator change, a feature flag enablement, or a changed agent permission.
### 8.1 Standard gate record

Record all of the following:

1. **Purpose and boundary** — intended user or operator benefit, intended users, explicit prohibited uses, and decision/action limits.
2. **Register classification** — system, class, status, risk level, owner, and related regulatory or partner context.
3. **Data flow** — data categories, sources, minimisation, retention, logging, retrieval/memory use, and whether any personal, payment, compliance, or restricted data is involved.
4. **Provider and residency** — model/provider, endpoint, processing region, AU-boundary evidence, contract/terms position, subprocessors where relevant, and external data-sharing consequence.
5. **Human and deterministic controls** — who reviews, what evidence they see, how they override, what must never be automated, and safe failure behaviour.
6. **Technical configuration** — prompt/profile/skill, model ID, schema, validation, retrieval sources, tool permissions, feature flag, identity and secret handling, and environment.
7. **Evaluation** — representative permitted test set, safety tests, failure modes, acceptance criteria, results, limitations, and unresolved issues.
8. **Operations** — monitoring, error and spend thresholds, audit log, alert owner, kill switch, rollback method, and customer/support response where relevant.
9. **Communications** — customer disclosure, consent, contract, partner, regulator, or public-claim review needs, including entity-firewall check.
10. **Approvals** — accountable executive, product/engineering owner, compliance reviewer, privacy/security reviewer, date, conditions, and expiry/review date.
High-risk changes require explicit approval before activation.
New vendors or routes outside the confirmed Australian boundary require a separate dated decision.
### 8.2 Internal-agent activation gate

In addition to the standard gate, complete this activation gate before enabling:

- a new agent profile, including Pluto, Mercury profiles, or OpenClaw agents;
- a new skill class or a skill that can execute commands, access a network, retrieve or write data, use credentials, publish, spend, change infrastructure, or change production;
- a new or materially changed cron, especially one that touches production, repositories, AWS, customer data, public channels, or external APIs;
- a new external model provider, agent framework, plugin, vector store, memory service, search/retrieval source, or connected tool; or
- a material expansion of an existing agent's tool, repository, cloud, data, or action authority.
The activation record must state:

| Question | Minimum answer |
|---|---|
| What exact task may it perform? | A concise allow-list, not a general aspiration. |
| What may it read? | Named repositories, data classifications, systems, sources, and environment. |
| What may it write or trigger? | Exact locations/actions; default is none outside a sandbox or review queue. |
| What may it never do? | Production changes, financial actions, secret handling, public publication, data export, or other lane-specific prohibitions. |
| Who approves material output? | Named human role and approval mechanism. |
| What identity/credentials does it use? | Least-privilege service identity, environment, expiry/revocation path, and secret owner. |
| What happens on failure or suspicion? | Stop condition, alert target, log location, disable method, and rollback. |
| How is it tested? | Sandbox/test evidence, adversarial prompt-injection test, and acceptance criteria. |
| What does it cost? | Provider/tool, rate limit, budget or cap, alert threshold, and billing owner. |
| How is it audited? | Activity-log location, job/skill/profile version, retention, and review cadence. |
### 8.3 Approval outcomes

| Outcome | Meaning |
|---|---|
| Approved for evaluation | May use the defined synthetic or otherwise approved test data only; not production activation. |
| Approved, not enabled | Controls are accepted but feature flag or runtime activation has not occurred. |
| Approved and enabled | May operate only within the documented scope, version, data, environment, and expiry/review date. |
| Approved with conditions | May operate only after each condition is evidenced; unresolved conditions block activation. |
| Paused | Must be disabled while the condition is investigated or remediated. |
| Rejected | Must not be activated; retain reason to avoid repeated unsafe proposals. |
### 8.4 Exceptions

Exceptions are rare and time-limited.
They must identify the exact rule, business reason, risk, compensating control, owner, approval date, expiry date, monitoring, and rollback/stop condition.
No exception permits unlawful processing, knowingly unsafe handling of credentials, or silent removal of required human accountability.

---
## 9. Customer-facing AI controls by lifecycle

### 9.1 Design

Define the user problem and why AI is necessary.
Prefer deterministic logic, source-grounded workflows, or human process where they provide a safer and sufficient outcome.
Write prohibited outcomes before building the happy path.
For AMLHive, evidence and source traceability are product requirements, not optional UI improvements.
For Tapease and the portfolio products, assess the regulatory perimeter before the product starts making or appearing to make an onboarding, payment-risk, licensing, or legal conclusion.
### 9.2 Build

Use structured outputs and validation for data extraction and workflow inputs.
Preserve original source text or document references when AI translates, summarises, extracts, or classifies.
Avoid using a model output as the only source of truth for a material record.
Place model calls behind feature flags where practical.
Use bounded retries, output size limits, error handling, rate limits, and spend limits appropriate to the use case.
### 9.3 Evaluate

Use evaluation material that is permitted for the chosen environment.
High-risk evaluations should test accuracy, completeness, source citation, hallucination, refusal/failure behaviour, adversarial inputs, prompt injection, privacy leakage, deterministic validation failures, and reviewer usability.
Define pass/fail acceptance criteria before reading the result.
Record limitations; a model comparison is not an approval to route production data to the model.
### 9.4 Activate

Confirm the approved version is what will run.
Confirm the feature flag, kill switch, rollback, human-review path, alerting, residency evidence, and named owner.
Enable progressively where possible and monitor the first production use.
### 9.5 Operate and retire

Review quality, manual corrections, exceptions, volume, spend, data flow, customer feedback, provider changes, and incidents.
Pause or retire a use case when it no longer meets its acceptance criteria, operates outside approved scope, becomes unnecessary, or cannot be supported safely.
Retirement includes disabling routes, revoking access, applying retention/deletion rules, preserving required evidence, and updating the register.

---
## 10. Internal autonomous-agent controls by lifecycle

### 10.1 Configure

Each agent, profile, cron, skill, and connected tool must have a documented purpose and allowed task class.
Do not use broad instructions such as “manage production,” “handle customer operations,” or “research and act” without a bounded action design.
Assign a stable identifier for the agent/profile and record the model/provider, prompt or instructions version, tool list, repositories, credentials scope, environment, budget, and owner.
### 10.2 Source and retrieval hygiene

Treat all retrieved content as data, not authority.
For external research, retain source URLs or identifiers, retrieval date, and a short assessment where the result informs a material decision or public claim.
For knowledge ingestion, retain document/source provenance, classification, ingestion version, access group, and deletion route.
Do not let source content alter the agent's system instructions or approval boundary.
### 10.3 Code and configuration changes

Coding agents may propose and prepare changes within approved repositories and branches.
Before merge or release, require the normal branch, test, review, and deployment controls for the risk level.
Generated dependencies, scripts, infrastructure definitions, migrations, and workflow files require the same review as human-authored changes.
Run secret scanning and inspect diffs for unintended data paths, permission changes, destructive operations, and supply-chain additions.
### 10.4 Scheduled jobs

Maintain an inventory of all 66 cron jobs.
For each job record the schedule, purpose, owner, invoking identity, input classification, output destination, provider/tool, cost basis, error behaviour, alert target, latest successful run, and disable method.
Review jobs that fail repeatedly, operate without recent business need, use a new provider, increase costs, or have gained access/authority since their last approval.
### 10.5 Public content and communications

Agents can assist drafting only within approved brand and claim boundaries.
Before publication, verify factual claims, regulatory implications, customer commitments, confidential information, intellectual-property risk, and the harishabib.au / AMLHive entity firewall.
Store the approving person, channel, content version, publication time, and any material sources or disclosures.
### 10.6 Monitoring, remediation, and incident response

Monitoring agents should start with read-only access and alerting.
If an automated remediation is proposed, treat it as a separate production action class with bounded conditions, reversibility, a known-safe command or runbook, alerting, and approval.
An agent must stop and alert rather than improvise when the observed state is ambiguous, access is denied, source content is suspicious, or its action would exceed its approval boundary.
### 10.7 Knowledge and memory

Mempalace and Honcho must have purpose-limited fields and retrieval boundaries.
Store only information necessary to provide the approved utility.
Provide a practical correction and deletion route for material inaccurate or unwanted memory, subject to any required legal record retention.
Do not use the knowledge base or memory model as a back door around product data boundaries or access controls.

---
## 11. Operating rhythm

### 11.1 Monthly AI governance review

Hold a concise 30-minute monthly review while the framework is new. Review and record:

- every active, evaluation, paused, and planned customer-facing use case and its feature-flag or activation status;
- new or changed models, prompts, schemas, validators, retrieval sources, providers, regions, skills, profiles, tools, cron jobs, and access grants;
- evaluation outcomes, manual correction rates, validation failures, timeouts, job failures, customer-visible errors, and drift by version;
- AU processing-boundary evidence, data classifications, new data routes, and privacy/security concerns;
- spend, volume, rate-limit events, and unresolved approval conditions;
- public communications or disclosures involving AI, including the entity-firewall check;
- incidents, near misses, exceptions, overdue actions, and register accuracy; and
- whether any workflow has crossed its approved scope or expiry date.
### 11.2 Weekly-ish fleet activity review

At least weekly while the fleet is active, review a short operational snapshot.
This may be a five-to-fifteen minute review, but it must be recorded for material findings.
Review:

- activity from Pluto; Mercury; Sol, Vulcan, Aurora, Lumen, Vigil, and Caduceus; Gumby, Brainy, Jonny-Quest, and Tracker; Codex CLI; and dsh where active;
- new, changed, failed, disabled, or unusually expensive cron jobs among the 66;
- repository changes, pull requests, branch-protection events, deployments, failed tests, secret-scan results, and privilege changes;
- public content drafts or publications awaiting/requiring approval;
- Mempalace ingestion sources, Honcho memory changes, deletions, corrections, access anomalies, and prompt-injection indicators;
- provider use, new external routes, error rates, unexpected tool calls, and spend anomalies; and
- outstanding stop conditions, action items, and whether any agent should be paused until clarified.
### 11.3 Immediate incident triggers

Immediately disable or constrain the relevant feature, agent, tool, skill, cron, provider route, or credential and investigate if any of the following occurs:

- data-residency breach or unapproved external data route;
- unauthorised autonomous regulated, customer, financial, public, or production-affecting action;
- loss of human review in a high-risk workflow;
- exposure, suspected exposure, or improper storage of a credential or restricted personal/client/payment/compliance data;
- critical evaluation failure, systematic unsafe output, or evidence integrity failure;
- prompt injection, poisoned knowledge source, malicious skill/artifact, or suspected agent instruction override;
- unapproved spend, spend cap breach, unexpected cloud resource, or financial action;
- material customer-visible incident, regulatory concern, security event, or entity-firewall breach; or
- an agent acting outside its documented authority or unable to explain its action trail.
The accountable executive determines when and how to re-enable the capability after remediation evidence is reviewed.

---
## 12. Minimum evidence to retain

Retain evidence in a location that is access-controlled, searchable, and linked to the relevant register entry, code change, issue, or decision. Avoid duplicating restricted customer information in governance evidence unless strictly necessary for an investigation.

| Evidence type | Minimum content |
|---|---|
| AI use-case register | Current and historical entry, status, risk, owner, data classification, provider/region, approval, configuration reference, flag, and next review. |
| Approval record | Purpose, boundary, risk, reviewers, conditions, decision date, expiry/review date, and any exception. |
| Evaluation report | Test-data permission/classification, version tested, scenarios, criteria, results, failures, limitations, and decision. |
| Version history | Prompts, model IDs, schemas, validators, retrieval sources, skills, agent profiles, tool permissions, code/configuration, and release references. |
| Implementation and test evidence | Pull request or change record, tests, security/secret checks, feature flag, rollback confirmation, and activation time. |
| Monitoring summary | Quality, error/failure, manual correction, volume, spend, alert, and drift results for the review period. |
| Incident record | Trigger, impact, data/actions affected, containment, root cause, notifications/decisions, remediation, re-enable decision, and follow-up owner. |
| Customer/public communication record | Disclosure/consent where applicable, approved published version, claim/source review, channel, and approver. |
| Agent activity log | Agent/profile or cron ID, task/run, initiating source, tool/action category, environment, result, time, and material approval link. |
| Cron inventory and run history | All 66 job definitions, owners, schedules, inputs/outputs, permissions, cost controls, failures, alerts, last review, and disable path. |
| Knowledge/memory record | Mempalace source provenance, ingestion/classification/access/deletion data; Honcho field purpose, retention, correction, deletion, and access evidence. |
| Skill/artifact provenance | Origin, version/commit, reviewer, capability class, permissions, tests, change approval, and retirement/rollback record. |
| Skills-rules-repo history | Git commit history and review/change evidence for the 279 skills and associated rules. |
### 12.1 Retention approach

Apply the retention period required by applicable law, contract, product record obligation, incident needs, and the approved data-retention schedule.
Where no mandatory period applies, retain governance evidence long enough to demonstrate the approval, operation, monitoring, and retirement of the use case.
Restrict access to the minimum people needed, and ensure deletion of supporting data does not erase evidence that a governance decision occurred.

---
## 13. Operational-readiness checklist

This framework becomes operational for the whole estate when the following are complete.
### 13.1 Foundation

- [ ] This v1.0 framework is approved and has an approval date.
- [ ] The four functional roles are named, including when one person holds more than one role.
- [ ] The register has a live owner, storage location, and monthly review date.
- [ ] The approved Australian processing boundary is documented by provider, service, account/project, endpoint, and evidence reference.
- [ ] The entity-firewall rule is included in public-content and agent instructions.
- [ ] A standard approval-gate template and exception record are available.
### 13.2 Product use cases

- [ ] All five known AMLHive entries are in the live register with current feature-flag and production-status evidence.
- [ ] AMLHive high-risk workflows have source visibility, human-review points, validation, kill switches, rollback, and monitoring confirmed.
- [ ] The NVIDIA/Nemotron comparison is explicitly constrained to synthetic fixtures until separately approved otherwise.
- [ ] Tapease onboarding and risk use cases are recorded as planned and blocked from production activation pending the complete approval gate.
- [ ] ExitLens AU, TokenPilot AU, FinAI File AU, CloudProof AU, and PayLicence each have planned/early register entries before any client-data AI use.
- [ ] Customer disclosure, consent, partner, and legal/compliance reviews are identified for each activated product use case.
### 13.3 Agent-fleet controls

- [ ] Pluto, Mercury, Sol, Vulcan, Aurora, Lumen, Vigil, Caduceus, Gumby, Brainy, Jonny-Quest, Tracker, Codex CLI, and dsh have documented purpose, environment, owner, permissions, and stop/disable route.
- [ ] The 66 cron jobs are inventoried with owner, task, schedule, credentials, data classification, outputs, spend control, alert, and disable method.
- [ ] Production, staging/test, and development credentials/access are separated and least privilege is verified for agent use.
- [ ] Production-affecting actions require a human approval mechanism or a separately documented narrow pre-approved action rule.
- [ ] Public-content publication has a review path and entity-firewall check.
- [ ] Mempalace source/ingestion/access/deletion controls and Honcho memory-purpose/retention/deletion controls are documented.
- [ ] Skills-rules-repo changes are versioned in Git, reviewed proportionately to capability, and can be rolled back; the 279 skills are inventory-managed.
- [ ] New skill, profile, cron, provider, and connected-tool activation uses the internal-agent gate.
- [ ] Agent logs, cost alerts, failed-job alerts, secret scanning, and prompt-injection/data-poisoning safeguards are operating.
### 13.4 Evidence and rhythm

- [ ] Initial approvals, evaluation reports, configuration versions, test evidence, and kill/rollback information are retained for active use cases.
- [ ] The first monthly AI review has been completed and minuted.
- [ ] The weekly-ish fleet activity review is scheduled and its record location is known.
- [ ] Incident triggers, pause authority, credential revocation, and re-enable process have been tested or tabletop-exercised for high-risk lanes.
- [ ] Outstanding risks, exceptions, and planned activations have named owners and due dates.
Until these items are substantially complete, describe the organisation as **developing and implementing** this AI governance framework, rather than as fully operating it.

---
## 14. Reuse instructions

When a new system, product, model, agent, skill, cron, provider, or workflow is introduced:

1. add or update its use-case register entry;
2. choose the two-class and risk classification;
3. complete the required approval gate before activation;
4. implement the required controls and retain evidence;
5. add it to the appropriate monthly and weekly-ish review; and
6. pause, investigate, and remediate if it crosses an incident trigger.
This framework is intentionally vendor-neutral and system-neutral.
Its controls travel with the data, decision consequence, action authority, and agent capability—not with the name of the model or product.
