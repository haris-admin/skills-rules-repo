# Worked Example: AML Alert Triage

This example is for a RegTech founder operating a transaction-monitoring
service. The daily queue contains alerts from customer activity. The desired
outcome is to tag each alert, draft a disposition, and refer the uncertain or
high-risk cases to Enhanced Due Diligence (EDD) without allowing the agent to
file a suspicious activity report, freeze an account, or communicate with a
customer.

The examples use generic internal paths and roles deliberately: adapt them to
your controlled environment and approved retention policy.

## Before: a Stages 1–3 workflow

At this point the system has useful agents, but people still translate context
and push work between them. It is an efficient workflow, not autonomous
orchestration.

| Stage | Actor and activity | Output | Human-as-message-bus dependency |
| --- | --- | --- | --- |
| 1 — assist | An analyst asks `alert-tagging-agent` to tag a downloaded queue using `cash-structuring`, `high-velocity`, `sanctions-adverse-media`, or `data-quality`. | A spreadsheet with tags and a confidence score. | The analyst decides which queue extract to send and copies results into the case tool. |
| 2 — bounded task | The agent drafts `close-no-concern`, `monitor`, or `refer-edd` text for alerts selected by the analyst. | Draft dispositions in a chat response. | The analyst chooses the confidence cut-off, edits drafts, and manually creates EDD cases. |
| 3 — bounded batch | The agent processes the morning batch and places uncertain rows in a `needs-review` tab. | A batch summary and a tab of uncertain alerts. | An operations lead forwards rows to EDD, messages the queue owner about failures, and separately forwards alert-volume and complaint-volume spikes. |

### Why this plateaus at Stage 3

The agent has no declared business outcome, no authorised decision boundary,
no stop condition, and no standard proof of what it considered. EDD receives
a person-curated request rather than an artefact it can verify. A queue spike
and a complaint spike become two alerts to interpret, so no single person owns
the combined decision.

## After, rung 4: Goal Contract for alert triage

The following contract replaces instructions such as “review the queue, apply
these steps, and send me uncertain cases.” It grants a bounded outcome and
explicitly reserves regulated decisions for humans.

```yaml
contract_type: goal
contract_id: aml-alert-triage-daily-v1
schema_version: 1
pipeline: aml-alert-triage
rung: 4
owner:
  role: Financial Crime Operations Manager
  contact: financial-crime-operations/triage-owner
objective:
  statement: >-
    Triage every newly created eligible transaction-monitoring alert by its
    service-level deadline, apply a reason tag, and produce an auditable draft
    disposition or an EDD referral for uncertain or high-risk alerts.
  scope: >-
    Alerts created in the last 24 hours with status `new` for Australian
    retail customers; excludes sanctions-list matches and active investigations.
success_criteria:
  - id: eligible-alert-coverage
    measure: eligible alerts with a completed triage record divided by eligible alerts received
    target: ">= 99.5% by 14:00 Australia/Sydney each business day"
    measurement_source: transaction-monitoring queue and triage evidence ledger
    evaluation_window: each business day
  - id: quality-sample
    measure: QA agreement with tag and disposition on a stratified 5% sample
    target: ">= 95% agreement; zero un-escalated high-risk sample errors"
    measurement_source: weekly independent QA review
    evaluation_window: weekly
  - id: uncertainty-safety
    measure: alerts below confidence threshold that are referred rather than closed or monitored
    target: 100%
    measurement_source: triage evidence ledger
    evaluation_window: each business day
constraints:
  guardrails:
    - Never file a suspicious activity report, freeze or close an account, or alter a transaction-monitoring rule.
    - Never select `close-no-concern` for a sanctions, politically exposed person, adverse-media, or linked-case indicator.
    - Treat missing customer identity, transaction history, or screening data as uncertainty, not as negative evidence.
  data:
    classification: internal-confidential and regulated personal information
    allowed_sources:
      - transaction-monitoring case record
      - approved customer profile and transaction-history views
      - approved screening-result view
    retention: evidence ledger retained for seven years in the controlled compliance archive
    prohibited_uses:
      - Export customer data outside the controlled compliance boundary.
      - Use protected attributes or free-text complaint sentiment as a sole disposition basis.
authority:
  allowed_actions:
    - Apply one or more approved reason tags to an eligible alert.
    - Draft `close-no-concern`, `monitor`, or `refer-edd` disposition text.
    - Create an EDD handoff only when an escalation trigger is met.
  prohibited_actions:
    - Submit regulatory reports or finalise a regulated suspicious-activity disposition.
    - Freeze, close, restrict, or contact a customer.
    - Modify source records, customer risk ratings, or monitoring thresholds.
  spend:
    currency: AUD
    per_action_limit: 0
    period_limit: 0 per day
  external_communications:
    permitted: false
    allowed_recipients: none
    approved_templates: none
  data_actions:
    permitted_writes: reason tags, draft disposition, and evidence fields on the existing alert case
    permitted_exports: none
    prohibited_mutations:
      - Change a final investigator disposition.
      - Change customer profile, risk, or transaction data.
stop_conditions:
  - condition: The alert has an active investigation, a sanctions-list match, or conflicting customer identity data.
    immediate_action: Preserve current evidence and halt triage for that alert.
    escalation_target: financial-crime-operations/high-priority-review
  - condition: The approved screening-result or transaction-history view is unavailable or older than four hours.
    immediate_action: Suspend affected batch items and mark them `data-unavailable`.
    escalation_target: financial-crime-operations/triage-owner
evidence_required:
  record_location: compliance-evidence://aml-alert-triage/<alert-id>/<triage-run-id>.json
  required_fields:
    - contract_id_version_hash
    - alert_id_customer_reference_and_input_snapshot_hashes
    - tags_draft_disposition_confidence_and_rationale
    - authority_guardrail_and_stop-condition_checks
    - model_or_ruleset_version_actor_and_timestamps
    - edd_handoff_reference_when_created
  retention: seven years
escalation_triggers:
  - trigger: Confidence is below 0.80 for any draft disposition.
    route: edd-agent/intake
    required_context: triage evidence record, source case references, and proposed reason tags
    response_sla: acknowledge within 15 minutes
  - trigger: A sanctions, politically exposed person, adverse-media, linked-case, or cash-structuring indicator is present.
    route: edd-agent/intake
    required_context: triage evidence record and indicator references
    response_sla: acknowledge within 15 minutes
  - trigger: A stop condition is met or the eligible-alert coverage target is at risk.
    route: financial-crime-operations/triage-owner
    required_context: affected alert IDs, stop reason, queue count, and evidence references
    response_sla: respond within 30 minutes
review_cadence:
  frequency: daily dashboard review and weekly stratified QA sample
  reviewer_role: Financial Crime Operations Manager
  sample_or_metric: coverage, elapsed time, EDD referral rate, and a 5% stratified QA sample
  change_authority: Financial Crime Operations Manager with Compliance Policy approval
```

### What is now autonomous, and what is not

| Decision | Contract result |
| --- | --- |
| Tag an eligible alert and draft a non-final disposition | Autonomous within the Goal Contract. |
| Refer an uncertain or enumerated high-risk alert to EDD | Autonomous, but only through the Handoff Contract below. |
| File a report, make a final suspicious-activity decision, or change customer access | Explicitly outside agent authority; a human remains accountable. |
| Missing, stale, conflicting, or out-of-scope data | Stop and preserve evidence; do not improvise a disposition. |

Every completed alert now produces a retrievable evidence record. The contract
measures coverage and safety rather than merely checking whether the agent
followed a prompt.

## After, rung 5: triage-to-EDD Handoff Contract

This is the direct baton pass used when the Goal Contract triggers EDD. The
EDD agent can reject malformed or duplicate referrals without an operations
lead translating an email or spreadsheet.

```yaml
contract_type: handoff
contract_id: aml-triage-to-edd-referral-v1
schema_version: 1
pipeline: aml-alert-triage
rung: 5
producer:
  agent_id: aml-alert-triage-agent
  responsibility: Produce one evidence-backed EDD referral for each eligible escalation trigger.
consumer:
  agent_id: aml-edd-intake-agent
  responsibility: Validate the referral, open or resume the EDD case, and record an acceptance receipt.
artefact:
  path: .agents/run-artifacts/aml-alert-triage/2026-09-12/batch-20260912T060000Z/edd-referrals.ndjson
  format: application/x-ndjson
  schema_ref: .agents/contracts/schemas/aml-edd-referral-v1.json
  checksum: sha256:9cfd9d0e97dc1b4d3b23e68f44a6f70b2f2ed2cce6d0df5f1f0c1738a84045f1
acceptance_criteria:
  - id: valid-record-shape
    assertion: Every line validates against aml-edd-referral-v1 and has alert_id, customer_reference, escalation_reason, evidence_ref, and triage_confidence.
    verification: Parse NDJSON, validate each object, and reject the artefact if any line fails.
    on_failure: Quarantine the artefact, write a rejection receipt, and invoke failure_mode.
  - id: evidence-is-retrievable
    assertion: Each evidence_ref resolves to a seven-year triage evidence record whose alert_id matches the referral.
    verification: Resolve each evidence_ref and compare alert_id and recorded contract hash.
    on_failure: Reject only the invalid referrals and escalate their alert IDs.
  - id: referral-is-authorised
    assertion: escalation_reason is a Goal Contract trigger and no final regulated disposition is requested.
    verification: Match the reason to aml-alert-triage-daily-v1 escalation triggers.
    on_failure: Reject the referral and route it to high-priority human review.
provenance:
  correlation_id: aml-alert:ALRT-20260912-004821
  goal_contract_ref: aml-alert-triage-daily-v1@1
  input_references:
    - case://transaction-monitoring/ALRT-20260912-004821
    - compliance-evidence://aml-alert-triage/ALRT-20260912-004821/triage-20260912T061418Z.json
  input_hashes:
    - sha256:42f218277dc9c59d03442ef776b9e5a74a2c5a9c8e8d0fab212c197dd0da5d89
  producer_run_id: triage-20260912T060000Z
  transformations:
    - approved-reason-tagging-ruleset@2026-08-28
    - triage-disposition-model@2026-09-01
  produced_at: 2026-09-12T06:14:18Z
idempotency:
  key: edd-intake:ALRT-20260912-004821:aml-triage-to-edd-referral-v1
  scope: create-or-resume the EDD case for this alert and contract version
  duplicate_action: Return the existing EDD case ID and prior acceptance receipt; do not open a second case or notify again.
deadline_sla:
  artefact_available_by: within 5 minutes of the triage escalation decision
  consumer_ack_by: within 15 minutes of artefact availability
  completion_by: EDD case opened or resumed within 30 minutes of artefact availability
failure_mode:
  retry:
    max_attempts: 3
    backoff: exponential, starting at 60 seconds and capped at 10 minutes
    retryable_errors:
      - transient artefact-store timeout
      - consumer intake service unavailable
  escalation:
    trigger: retries exhausted, checksum mismatch, schema rejection, or evidence reference unavailable
    route: financial-crime-operations/high-priority-review
    preserve: original artefact, checksum, producer evidence, rejection receipt, and all attempt records
notification:
  target: compliance-events/aml-edd-handoffs
  events:
    - accepted
    - failed
  payload_ref: .agents/contracts/schemas/aml-handoff-event-v1.json
completion_record:
  path: .agents/run-artifacts/aml-edd-intake/2026-09-12/receipts/ALRT-20260912-004821.json
  required_fields:
    - idempotency_key
    - acceptance_status
    - consumer_run_id
    - completed_at
    - edd_case_id
```

### Resuming the exact referral

If the triage agent delivers the same artefact again after a timeout, EDD first
looks up `edd-intake:ALRT-20260912-004821:aml-triage-to-edd-referral-v1`.
An existing accepted receipt returns `EDD-2026-0912-1187`; it does not create a
new case, a second notification, or a new regulated decision. If the receipt
shows a partial failure, EDD resumes only the unfinished validation or case
creation step and appends the attempt to the same evidence trail.

## After, rung 6: correlate queue and complaint spikes into one decision

The previous workflow reported “alert queue spike” and “complaint spike” as
separate alerts. The following rule turns the matching pattern into one
quality-incident decision, which has one owner and an attached evidence trail.

```yaml
contract_type: correlation_rule
contract_id: aml-triage-service-quality-incident-v1
schema_version: 1
pipeline: aml-alert-triage
rung: 6
signal_sources:
  - source_id: alert-queue-rate
    system: transaction-monitoring operations metrics
    event_or_metric: new eligible AML alerts per 15-minute interval
    query_or_filter: jurisdiction=AU; customer_segment=retail; status=new; baseline=previous 28 matching weekdays
    freshness_sla: 10 minutes
  - source_id: customer-complaint-rate
    system: customer-complaint case register
    event_or_metric: complaints about delayed review, account access, or unexplained monitoring per 15-minute interval
    query_or_filter: jurisdiction=AU; customer_segment=retail; complaint_status=open; baseline=previous 28 matching weekdays
    freshness_sla: 15 minutes
correlation:
  key: jurisdiction|customer_segment|payment_product
  join_window: 30 minutes
  minimum_sources: 2
severity_mapping:
  - when: alert-queue-rate >= 3.0 standard deviations above baseline AND customer-complaint-rate >= 2.0 standard deviations above baseline
    severity: high
    rationale: Concurrent queue growth and affected-customer complaints indicate a probable triage service degradation.
  - when: alert-queue-rate >= 5.0 standard deviations above baseline AND customer-complaint-rate >= 3.0 standard deviations above baseline
    severity: critical
    rationale: Extreme concurrent growth risks missed review deadlines and requires immediate operational control.
dedupe:
  key: jurisdiction|customer_segment|payment_product|aml-triage-service-quality-incident-v1
  window: 24 hours
  duplicate_action: Update the existing incident evidence and severity; suppress a new decision unless severity increases.
decision_output:
  decision_type: open-or-update-one-aml-triage-service-quality-incident
  destination: financial-crime-operations/service-quality-incidents
  required_payload:
    - correlation_key
    - severity
    - source_evidence_refs
    - contract_id_version_hash
    - recommended_control: pause autonomous close-no-concern drafts for the affected key pending owner review
accountable_owner:
  role: Head of Financial Crime Operations
  contact: financial-crime-operations/service-quality-owner
evidence_trail:
  record_location: compliance-evidence://aml-triage-service-quality/<correlation-key>/<decision-id>.json
  required_fields:
    - source_event_ids_query_versions_baselines_and_hashes
    - fifteen-minute-series_values_and_calculated_standard_deviations
    - correlation_key_join_window_and_dedupe_lookup
    - severity_mapping_row_decision_output_and_accountable_owner
    - evaluator_run_id_contract_hash_and_timestamp
stop_conditions:
  - condition: Either source exceeds its freshness SLA or lacks the correlation key.
    action: Do not emit the quality-incident decision; write an incomplete-correlation evidence record and escalate.
    route: financial-crime-operations/service-quality-owner
```

### One decision, with the joined proof attached

For `AU|retail|card-payments` at `2026-09-12T08:30:00Z`, the rule finds 412
new alerts (5.4 standard deviations above baseline) and 37 matching complaints
(3.2 standard deviations above baseline) inside the 30-minute window. It emits
only this record:

```json
{
  "decision_id": "AMLSQI-20260912-0830-AU-RETAIL-CARD",
  "decision_type": "open-or-update-one-aml-triage-service-quality-incident",
  "correlation_key": "AU|retail|card-payments",
  "severity": "critical",
  "owner": "Head of Financial Crime Operations",
  "evidence_ref": "compliance-evidence://aml-triage-service-quality/AU%7Cretail%7Ccard-payments/AMLSQI-20260912-0830-AU-RETAIL-CARD.json",
  "source_evidence": [
    "metrics://transaction-monitoring/queue-rate/2026-09-12T08:30:00Z#sha256:8d55...",
    "cases://complaints/rate/2026-09-12T08:30:00Z#sha256:3a81..."
  ],
  "dedupe_key": "AU|retail|card-payments|aml-triage-service-quality-incident-v1"
}
```

The attached evidence record carries the raw source IDs and hashes, query and
baseline versions, time series, standard-deviation calculations, matched
severity row, contract hash, evaluator run ID, dedupe lookup, and owner route.
It lets the accountable owner audit one decision without reconstructing two
unrelated alerts or relying on a person’s message history.
