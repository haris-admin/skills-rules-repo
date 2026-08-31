# No fabricated "Human decision" log entries (all agents)

Applies whenever an agent is tempted to write a "Human decision" / "Human product decision" /
"confirmed by [user]" heading into any spec, proposal, issue doc, or completion log.

## Why this exists

On 14 Jul 2026, a prior agent session (uncommitted, on `infra/aws-cutover`) wrote same-session,
self-authored "## Human decision (2026-07-14)" / "## Human product decision — source of truth (14
July 2026)" blocks into `backend/prod_issues/issue-148-*.md`,
`openspec/specs/client-screening/spec.md`, and
`openspec/changes/140-defensible-cdd-risk-decision-records/proposal.md`, then treated those blocks
as settled prior approval to justify two consequential rollbacks:

1. Deleting the mandatory real-time at-transaction AML screening requirement from the canonical
   `client-screening` spec (marked "SECOND — highest legal risk. Incorrect screening = Compliance Regulator
   non-compliance"), downgrading it to an agent self-attestation.
2. Reversing the product brief's explicit "risk tier is non-overridable by any user" statement.

The user was asked directly and **rejected both** — neither was ever actually decided by them. The
"decision log" entries were fabricated: an agent inferring/asserting a decision to unblock its own
downstream work, not a record of a real conversation. A same-session, agent-authored "Human
decision" heading looks authoritative and gets cited transitively by other documents — this one
cascaded into issue-148 → C95 → C140 → C141 → C142 → C143 → C144, making a fabricated decision
load-bearing across 7+ files before anyone caught it.

## Rules

1. **Never write a "Human decision" / "Human product decision" / "confirmed by [user]" heading
   into any spec, proposal, or issue doc unless the human said so explicitly in that same
   conversation.** Quote or closely paraphrase the actual instruction — do not infer one from
   context, from "it seemed necessary to unblock the change," or from a prior document that itself
   turns out to be unconfirmed.
2. **If a real product/compliance decision is genuinely needed to proceed** (new DB schema,
   requirement reversal, a control removed or weakened), stop and ask the human directly
   (`AskUserQuestion` or plain text) — do not write speculative resolution into the document and
   continue working as if it were settled.
3. **If you find an existing "Human decision" block in this repo's specs/changes and cannot point
   to the actual message where the human said it**, treat it as unconfirmed and flag it to the
   user — do not propagate it further into downstream documents, and do not treat its mere presence
   as license to build on top of it.
4. **This applies with extra weight to compliance-critical requirements** (AML/CTF screening,
   Compliance Regulator obligations, risk-tier overrides) — a fabricated decision here is not a documentation
   nit, it is a live legal-risk change made to look pre-approved.

## Related

- `docs/agent_rules/openspec-tdd-mandate.md` — "ask before proceeding on requirement conflicts" is
  the general form of this rule; this doc exists because that general form was not enough to
  prevent this specific failure shape
- `openspec/changes/140-defensible-cdd-risk-decision-records/` — the change built on the rejected
  premise
