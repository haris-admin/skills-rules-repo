---
name: au-sovereignty-alignment-audit
description: >-
  Recurring audit that AMLHive's (and the wider portfolio's) SHIPPED solutions stay aligned with
  current and incoming Australian data-sovereignty, privacy, and AI obligations — as opposed to
  screening a new idea (data-sovereignty-market-screen) or tracking regulatory dates
  (caduceus-compliance-watch). Walks the live system: data flows, external providers, AI/model
  routes, regions, retention, consent surfaces, and automated-decision points; checks each against
  the AU incoming-regulation register in references/; and produces a dated drift report with each
  gap logged as a prod issue, technical-debt entry, or OpenSpec change. Use monthly, before a
  funding/partner/regulator conversation, when an item in the incoming-regulation register reaches
  ~90 days from commencement, or when the user asks "are our solutions still compliant / aligned"
  or "check our sovereignty posture".
version: 1.0.0
license: MIT
metadata:
  tags: [compliance, audit, data-sovereignty, privacy, ai-regulation, australia, drift, recurring]
  related_skills: [data-sovereignty-market-screen, caduceus-compliance-watch, ai-governance-framework, amlhive-prod-monitor, prod-issue-management, verify-external-agent-reports, llm-provider-evaluation]
---

# AU Sovereignty & Regulatory Alignment Audit

Point-in-time check that what is **actually running in production** still satisfies current and
soon-to-commence Australian obligations. Screening ideas is a different skill; this one assumes the
thing is already built and asks "has it drifted, and has the law moved under it".

## When to use

- **Monthly** (bundle with the `ai-governance-framework` monthly AI review).
- An entry in `references/au-incoming-regulation-register.md` is within ~90 days of commencement.
- Before an EOI, accelerator session, investor DD, partner security review, or any regulator-facing
  conversation.
- A new external provider / model / region / data category went live since the last audit.
- The user asks whether solutions are "still compliant", "aligned", or to "check our sovereignty
  posture".

## Method

### 1. Build the current-state inventory (evidence, not memory)
Per `verify-external-agent-reports` — read the live config, don't recall it.

- **Data flows:** every place personal / sensitive / compliance data enters, moves, or leaves.
  Source: OpenSpec specs, `docs/context.md`, route handlers, worker code, webhook receivers.
- **External providers & sub-processors:** every third-party API and the model/region behind it.
  Cross-check against `docs/agent_rules/new-vendor-and-model-data-sovereignty-check.md`'s tracked
  cases and any `context7_*` integration docs.
- **AI / model routes:** each `*_MODEL` env var and its resolved region (e.g.
  `resolve_bedrock_region()`), each prompt version, each place a model output feeds a
  user-visible or record-changing path.
- **Regions:** every AWS region in Terraform / deployed infra; every non-`ap-southeast-2`
  reference.
- **Retention:** what is kept, for how long, soft vs hard delete, and whether any credential/secret
  is being retained as if it were a record.
- **Consent & disclosure surfaces:** where users are told about recording, AI use, automated
  decisions, cross-border disclosure.
- **Automated-decision points:** anywhere a model or rule produces a consequential outcome without
  a human in front of it.

### 2. Check each against the register
For every row in `references/au-incoming-regulation-register.md`:

| Question | Evidence |
|---|---|
| Does this obligation apply to us? | why / why not, in one line |
| If it applies — are we aligned today? | 🟢 aligned / 🟠 partial / 🔴 gap / ⚪ not yet in force but design needed |
| What is the gap, concretely? | file / flow / provider, not "our privacy policy" |
| Commencement date & runway | from the register, confirmed against `caduceus-compliance-watch` |
| Where does the fix go? | prod issue / `technical_debt.md` / OpenSpec change / "no action" |

### 3. Hard-gate re-check (these should never regress)
- All real-data processing/storage in `ap-southeast-2`. Any drift = 🔴, immediate.
- No new non-AU or unconfirmed provider route carrying real data without a dated decision on file.
- No AI output auto-deciding a regulated matter.
- Sensitive data (voice/biometric/health/children) has consent + minimised retention.
- 7-year retention obligations intact; no secret being retained as a record.

### 4. Produce the drift report
Append a dated entry to the portfolio's alignment log (AMLHive:
`docs/compliance/au-alignment-audit-log.md` — create if absent, append-only, never edit past
entries; same convention as `docs/10_star_pathway.md`).

```
## <YYYY-MM-DD> — AU sovereignty & regulatory alignment audit (<model>)

Inventory reviewed: <data flows N · providers N · model routes N · regions N>, as of <commit>.

| Obligation | Applies | Status | Gap | Runway | Fix location |
|---|---|---|---|---|---|
| ap-southeast-2 residency | yes | 🟢 | — | — | — |
| APP 1.7/1.8 ADM transparency | yes | 🟠 | <where> | <date> | OpenSpec Cxxx |
| High-risk AI guardrails / AS 42001 | yes | 🟠 | ... | ... | ... |
| ... | | | | | |

**New 🔴 this cycle:** <list or "none">
**Closed since last cycle:** <list>
**Human decisions needed:** <named or "none">
```

### 5. Log the gaps
- 🔴 (hard gate regressed): open a prod issue now via `prod-issue-management`, disable the offending
  path if it is a live residency/decision breach (`ai-governance-framework` "immediate disable"
  trigger).
- 🟠 needing a design decision: `technical_debt.md` entry or an OpenSpec change proposal.
- ⚪ not yet in force: a dated note + a diary item for the next audit; only build now if runway is
  short or the change is cheap.

## Best practices

- **Evidence over memory.** A status string in a doc is not proof — re-derive from live config
  (`verify-external-agent-reports`, `prod-issue-verify` posture).
- **Keep the three skills distinct:** this audits shipped solutions;
  `data-sovereignty-market-screen` gates new ideas; `caduceus-compliance-watch` tracks the
  regulatory calendar and feeds this skill's register.
- **Update the register in the same pass.** If `caduceus-compliance-watch` or a news item surfaced
  a new obligation, add it to `references/au-incoming-regulation-register.md` before running the
  check against it.
- Not legal advice — this audit tells you where you need a lawyer or an accountable-exec decision,
  and by when.
