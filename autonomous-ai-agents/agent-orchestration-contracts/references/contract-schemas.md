# Contract Schemas

Copy a template into `.agents/contracts/<pipeline>.yaml`, replace every
placeholder, and keep the comments while it is being reviewed. These are
operational schemas: consumers should reject a missing required value rather
than infer it from a prompt or a deployment setting.

## Goal Contract — rung 4, the Manager

```yaml
# Owns a bounded business outcome rather than a prescribed sequence of steps.
contract_type: goal # Identifies this document as a Goal Contract.
contract_id: <domain>-<outcome>-v1 # Gives this versioned contract a stable identifier.
schema_version: 1 # Identifies the schema revision used to interpret this file.
pipeline: <pipeline-name> # Names the project pipeline governed by this contract.
rung: 4 # Declares the autonomy rung this contract enables.
owner: # Names the accountable business owner for the outcome.
  role: <accountable-role> # States the role that accepts risk and review responsibility.
  contact: <escalation-target> # Gives the route used for owner escalation.
objective: # Defines the result the agent is accountable for producing.
  statement: <measurable-business-outcome> # States the outcome without prescribing implementation steps.
  scope: <included-work-and-population> # Limits which work items and entities are in scope.
success_criteria: # Lists measurable conditions that define successful operation.
  - id: <criterion-id> # Gives the criterion a stable evidence and review label.
    measure: <metric-or-assertion> # Defines exactly what is measured or checked.
    target: <threshold-or-required-state> # States the pass threshold or required result.
    measurement_source: <system-or-query> # Names the authoritative source used to measure it.
    evaluation_window: <period-or-event> # States when the measure is evaluated.
constraints: # Lists non-negotiable safety, policy, and operating guardrails.
  guardrails: # States domain rules that must never be violated.
    - <guardrail> # Defines one mandatory rule or policy boundary.
  data: # Bounds what data may be read, written, retained, or shared.
    classification: <allowed-data-classes> # Limits the sensitivity classes the agent may process.
    allowed_sources: # Lists approved data sources the agent may read.
      - <approved-source> # Names one approved source.
    retention: <retention-period-and-location> # States where and how long decision data may persist.
    prohibited_uses: # Lists disallowed data handling or inference uses.
      - <prohibited-use> # Defines one prohibited use.
authority: # Makes the agent's permitted and forbidden actions testable.
  allowed_actions: # Lists actions the agent may take without per-item approval.
    - <allowed-action> # Defines one autonomous action.
  prohibited_actions: # Lists actions that always require a human or another authority.
    - <prohibited-action> # Defines one forbidden autonomous action.
  spend: # Bounds monetary commitments made by the agent.
    currency: <ISO-4217-code> # States the currency for spend limits.
    per_action_limit: <amount> # Caps a single autonomous commitment.
    period_limit: <amount-and-period> # Caps aggregate autonomous commitments.
  external_communications: # Bounds messages sent outside the organisation.
    permitted: <true-or-false> # States whether external communication is allowed.
    allowed_recipients: <recipient-classes-or-none> # Limits who may receive an allowed message.
    approved_templates: <template-ids-or-none> # Limits content to reviewed templates when applicable.
  data_actions: # Bounds data mutations and transfers.
    permitted_writes: <write-scope-or-none> # Limits records or fields the agent may change.
    permitted_exports: <export-scope-or-none> # Limits data that may leave the approved boundary.
    prohibited_mutations: # Lists writes that the agent must never make.
      - <prohibited-mutation> # Defines one prohibited mutation.
stop_conditions: # Lists conditions that immediately halt autonomous progress.
  - condition: <unsafe-uncertain-or-conflicting-state> # Defines the condition that stops work.
    immediate_action: <halt-quarantine-or-preserve> # States the safe action taken on detection.
    escalation_target: <role-or-queue> # Names who receives the stopped item.
evidence_required: # Defines the auditable proof emitted for each decision.
  record_location: <immutable-or-tamper-evident-store> # States where the evidence record is written.
  required_fields: # Lists fields that every evidence record must contain.
    - contract_id_version_hash # Records exactly which contract governed the decision.
    - input_references_and_hashes # Records reproducible input identities and integrity values.
    - decision_rationale_and_confidence # Records the decision and its basis or uncertainty.
    - authority_and_guardrail_checks # Records which boundaries were evaluated.
    - actor_and_timestamps # Records the agent identity and timing.
  retention: <retention-period> # States how long decision evidence is retained.
escalation_triggers: # Lists conditions that require a human or designated queue.
  - trigger: <condition> # Defines the condition that causes escalation.
    route: <role-or-queue> # Names the recipient responsible for the escalation.
    required_context: <evidence-fields-or-artefact> # States what must accompany the escalation.
    response_sla: <duration> # States the required response time.
review_cadence: # Defines ongoing human accountability for the autonomous outcome.
  frequency: <daily-weekly-monthly-or-event> # States how often operation is reviewed.
  reviewer_role: <role> # Names the role that performs the review.
  sample_or_metric: <sample-plan-or-dashboard> # States what evidence the reviewer examines.
  change_authority: <role-or-change-process> # States who may alter this contract.
```

| Property | Type | Required | Constraint |
| --- | --- | --- | --- |
| `contract_type`, `contract_id`, `schema_version`, `pipeline`, `rung` | string, string, integer, string, integer | Yes | `contract_type = goal`; `rung = 4`; ID is stable and versioned. |
| `owner` | object `{role, contact}` | Yes | A business role, not merely an agent name, is accountable. |
| `objective` | object `{statement, scope}` | Yes | Statement is outcome-focused and scope is finite. |
| `success_criteria[]` | array of `{id, measure, target, measurement_source, evaluation_window}` | Yes, non-empty | Every target has an authoritative measure and window. |
| `constraints` | object `{guardrails[], data}` | Yes | Data rules name allowed sources, retention, and prohibited uses. |
| `authority` | object | Yes | Includes allowed/prohibited actions and explicit spend, communications, and data limits. |
| `stop_conditions[]` | array of `{condition, immediate_action, escalation_target}` | Yes, non-empty | Stop is safe and routes the work item. |
| `evidence_required` | object `{record_location, required_fields[], retention}` | Yes | Evidence is retained in an auditable store. |
| `escalation_triggers[]` | array of `{trigger, route, required_context, response_sla}` | Yes, non-empty | Each trigger supplies sufficient context and a response expectation. |
| `review_cadence` | object `{frequency, reviewer_role, sample_or_metric, change_authority}` | Yes | Review and contract-change accountability are named. |

## Handoff Contract — rung 5, the Conductor

```yaml
# Transfers a verifiable artefact from one agent to another without human relay.
contract_type: handoff # Identifies this document as a Handoff Contract.
contract_id: <pipeline>-<producer>-to-<consumer>-v1 # Gives this versioned handoff a stable identifier.
schema_version: 1 # Identifies the schema revision used to interpret this file.
pipeline: <pipeline-name> # Names the pipeline containing this handoff.
rung: 5 # Declares the autonomy rung this contract enables.
producer: # Identifies the agent responsible for producing the artefact.
  agent_id: <producer-agent-id> # Gives the producing agent a stable runtime identity.
  responsibility: <what-the-producer-delivers> # States the producer's bounded responsibility.
consumer: # Identifies the agent responsible for accepting and acting on the artefact.
  agent_id: <consumer-agent-id> # Gives the consuming agent a stable runtime identity.
  responsibility: <what-the-consumer-does-after-acceptance> # States the consumer's bounded responsibility.
artefact: # Specifies the exact deliverable that crosses the handoff boundary.
  path: <exact-project-or-object-store-path> # Gives the exact immutable or versioned artefact location.
  format: <media-type-or-file-format> # States the serialisation format the consumer must parse.
  schema_ref: <schema-id-or-repository-path> # Names the schema and version used to validate the artefact.
  checksum: <algorithm-and-value-or-field-reference> # Supplies an integrity value the consumer verifies.
acceptance_criteria: # Lists checks the consumer can perform without asking a person.
  - id: <criterion-id> # Gives the acceptance check a stable label.
    assertion: <required-property> # States the property that must be true.
    verification: <deterministic-check> # States how the consumer verifies the assertion.
    on_failure: <reject-quarantine-or-escalate> # States the consumer action if the check fails.
provenance: # Requires the lineage needed to reproduce and audit the artefact.
  correlation_id: <shared-work-item-or-decision-id> # Links the handoff to its end-to-end work item.
  goal_contract_ref: <contract-id-and-version> # Links to the governing Goal Contract when one exists.
  input_references: # Lists immutable input locations or identities.
    - <input-uri-or-id> # Identifies one producer input.
  input_hashes: # Lists integrity values for the producer inputs.
    - <algorithm:value> # Provides one input integrity value.
  producer_run_id: <run-id> # Identifies the producer execution that made the artefact.
  transformations: # Lists material transformations applied by the producer.
    - <transformation-and-version> # Records one transformation and version.
  produced_at: <RFC-3339-timestamp> # Records when the artefact was created.
idempotency: # Defines how producer and consumer prevent double action on retries.
  key: <stable-business-event-contract-consumer-key> # Supplies the stable key shared across redeliveries.
  scope: <consumer-action-scope> # States which consumer action the key de-duplicates.
  duplicate_action: <return-prior-result-or-no-op> # States the required behavior for an already accepted key.
deadline_sla: # States when delivery and acceptance must happen.
  artefact_available_by: <RFC-3339-timestamp-or-duration> # Sets the producer delivery deadline.
  consumer_ack_by: <RFC-3339-timestamp-or-duration> # Sets the consumer acceptance deadline.
  completion_by: <RFC-3339-timestamp-or-duration> # Sets the deadline for the consumer's bounded action.
failure_mode: # Defines deterministic recovery rather than a human relay.
  retry: # States how transient failure is retried.
    max_attempts: <positive-integer> # Caps automated retry attempts.
    backoff: <strategy-and-duration> # States the delay strategy between retries.
    retryable_errors: # Lists errors eligible for automated retry.
      - <error-class> # Defines one retryable error class.
  escalation: # States how terminal failure is handled.
    trigger: <exhausted-retries-or-nonretryable-error> # Defines when escalation occurs.
    route: <role-or-queue> # Names the responsible escalation recipient.
    preserve: <artefact-and-evidence-location> # States evidence that must remain available.
notification: # Defines who is informed of material handoff state changes.
  target: <system-topic-or-queue> # Names the machine or human notification target.
  events: # Lists handoff events that require notification.
    - accepted # Notifies when the consumer accepts the artefact.
    - failed # Notifies when delivery or acceptance fails terminally.
  payload_ref: <notification-schema-or-artefact-path> # Names the notification payload contract.
completion_record: # Defines the receipt that closes the handoff.
  path: <exact-receipt-path> # Gives the exact location of the consumer receipt.
  required_fields: # Lists fields the consumer must write to the receipt.
    - idempotency_key # Links the receipt to the duplicate-prevention key.
    - acceptance_status # Records accepted, rejected, or escalated state.
    - consumer_run_id # Identifies the accepting consumer execution.
    - completed_at # Records when the acceptance or failure completed.
```

| Property | Type | Required | Constraint |
| --- | --- | --- | --- |
| `contract_type`, `contract_id`, `schema_version`, `pipeline`, `rung` | scalar fields | Yes | `contract_type = handoff`; `rung = 5`. |
| `producer`, `consumer` | objects `{agent_id, responsibility}` | Yes | Both runtime identity and bounded responsibility are explicit. |
| `artefact` | object `{path, format, schema_ref, checksum}` | Yes | Path is exact; schema and checksum are independently verifiable. |
| `acceptance_criteria[]` | array `{id, assertion, verification, on_failure}` | Yes, non-empty | Verifications are deterministic and consumer-owned. |
| `provenance` | object | Yes | Includes correlation, inputs/hashes, producer run, transformations, and time. |
| `idempotency` | object `{key, scope, duplicate_action}` | Yes | Key is stable across retries and de-duplicates a named action. |
| `deadline_sla` | object `{artefact_available_by, consumer_ack_by, completion_by}` | Yes | All three timing expectations are declared. |
| `failure_mode` | object `{retry, escalation}` | Yes | Retry is bounded; terminal failure preserves evidence and routes ownership. |
| `notification` | object `{target, events[], payload_ref}` | Yes | State changes have a specified recipient and payload. |
| `completion_record` | object `{path, required_fields[]}` | Yes | Receipt proves consumer acceptance, rejection, or escalation. |

## Correlation Rule — rung 6, the Ringmaster

```yaml
# Converts related cross-system signals into one owned, deduplicated decision.
contract_type: correlation_rule # Identifies this document as a Correlation Rule.
contract_id: <pipeline>-<decision>-v1 # Gives this versioned rule a stable identifier.
schema_version: 1 # Identifies the schema revision used to interpret this file.
pipeline: <pipeline-name> # Names the pipeline governed by this rule.
rung: 6 # Declares the autonomy rung this rule enables.
signal_sources: # Lists every system signal used to reach the combined decision.
  - source_id: <source-id> # Gives this source a stable rule-local identifier.
    system: <system-name> # Names the system that is authoritative for the signal.
    event_or_metric: <event-type-or-metric> # States the exact event stream or metric used.
    query_or_filter: <versioned-query-or-filter> # Defines how this signal population is selected.
    freshness_sla: <duration> # States how stale a source may be before the rule stops or degrades.
correlation: # Defines how source signals are joined into one candidate decision.
  key: <shared-entity-or-segment-key> # States the common join key available in every source.
  join_window: <duration> # Limits how far apart source observations may occur.
  minimum_sources: <positive-integer> # Requires this many distinct source IDs before deciding.
severity_mapping: # Maps joined signal strength to a declared severity.
  - when: <deterministic-threshold-expression> # Defines the condition for this severity row.
    severity: <low-medium-high-critical> # States the severity assigned when the condition matches.
    rationale: <why-this-level-matters> # Explains the operational significance of the mapping.
dedupe: # Prevents repeated output for the same operational situation.
  key: <correlation-key-decision-version> # States the stable identity used to collapse duplicates.
  window: <duration> # States how long a prior decision suppresses or updates a duplicate.
  duplicate_action: <update-existing-or-suppress> # States what happens when the key repeats.
decision_output: # Defines the single action emitted for a matched correlation.
  decision_type: <one-decision-name> # Names the one decision, not a list of independent alerts.
  destination: <case-queue-or-state-store> # Names where that decision is recorded or enacted.
  required_payload: # Lists fields attached to the single decision.
    - correlation_key # Identifies the joined entity or segment.
    - severity # Records the mapped severity.
    - source_evidence_refs # Links all source evidence to the decision.
    - contract_id_version_hash # Records the rule that governed the decision.
accountable_owner: # Names the person or role accountable for the output.
  role: <business-role> # States the role that owns the operational response.
  contact: <queue-or-escalation-target> # Gives the route to reach that owner.
evidence_trail: # Defines the auditable record that accompanies every decision.
  record_location: <immutable-or-tamper-evident-store> # States where combined evidence is written.
  required_fields: # Lists the proof required for every emitted decision.
    - source_event_ids_and_hashes # Records the exact joined observations and integrity values.
    - evaluated_thresholds_and_severity # Records calculations and their mapped result.
    - correlation_and_dedupe_keys # Records join and duplicate-prevention identities.
    - decision_output_and_owner # Records the one decision and accountable role.
    - evaluator_run_id_and_timestamp # Records the rule execution that emitted it.
stop_conditions: # Lists states where correlation must not produce an autonomous decision.
  - condition: <missing-stale-or-incompatible-source> # Defines the state that invalidates safe correlation.
    action: <halt-and-escalate-or-degrade> # States the safe response to that state.
    route: <role-or-queue> # Names who receives the stopped evaluation.
```

| Property | Type | Required | Constraint |
| --- | --- | --- | --- |
| `contract_type`, `contract_id`, `schema_version`, `pipeline`, `rung` | scalar fields | Yes | `contract_type = correlation_rule`; `rung = 6`. |
| `signal_sources[]` | array `{source_id, system, event_or_metric, query_or_filter, freshness_sla}` | Yes, at least 2 | Every source is identifiable, reproducible, and fresh enough. |
| `correlation` | object `{key, join_window, minimum_sources}` | Yes | Key exists across sources; window and source count are finite. |
| `severity_mapping[]` | array `{when, severity, rationale}` | Yes, non-empty | Conditions are deterministic and mutually reviewed for precedence. |
| `dedupe` | object `{key, window, duplicate_action}` | Yes | Repeated observations update or suppress a named decision. |
| `decision_output` | object `{decision_type, destination, required_payload[]}` | Yes | Exactly one decision type is emitted per correlation match. |
| `accountable_owner` | object `{role, contact}` | Yes | One business role owns the response. |
| `evidence_trail` | object `{record_location, required_fields[]}` | Yes | Evidence links all sources to calculation, output, and owner. |
| `stop_conditions[]` | array `{condition, action, route}` | Yes, non-empty | Bad or stale source state cannot silently yield a decision. |
