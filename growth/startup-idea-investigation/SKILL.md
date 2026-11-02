---
name: startup-idea-investigation
description: >-
  Investigate a startup idea or venture folder end to end: ingest every document, build a claims register, independently re-verify every figure as if prior verification were wrong, tag each as VERIFIED, PARTLY VERIFIED, CONTRADICTED, UNVERIFIED or UNMAPPABLE, then hand off to pre-mortem and blind VC review, and initialise AGENTS.md and context.md for shared agent state. Use when starting work on an unfamiliar idea, when asked to "validate the numbers", "second check the figures", "investigate this startup", or before any pitch, application or funding submission.
---

# Startup Idea Investigation

Turns a folder of strategy documents into an audited evidence base and a shared operating context. It is the front door for [startup-premortem](../startup-premortem/SKILL.md) and [startup-vc-skeptic](../startup-vc-skeptic/SKILL.md).

## When to Use

- New or inherited idea folder; the claims have not been independently checked.
- The user says earlier verification cannot be trusted and wants a second pass.
- Before an application, pitch, or grant that quotes figures from the documents.
- Do NOT use for live customer interviews (see [startup-idea-validation](../startup-idea-validation/SKILL.md)).

## Procedure

1. **Ingest.** Read AGENTS.md, README, `docs/`, specs, application answers, and code. List the ventures the documents describe; flag if there is more than one (thesis drift).
2. **Evidence inventory.** Count interview logs, LOIs, replies, live integrations, revenue versus desk-research documents.
3. **Claims register.** Extract every number and factual claim into a table: ID, claim, file, type (market size, competitor, customer, policy, funding, arithmetic, person/title). Follow [figure-verification-protocol.md](./references/figure-verification-protocol.md).
4. **Verify independently.** Assume each claim is wrong. Split by domain and run research in parallel (read-only research agents, each with a denial-of-authority clause). Do your own arithmetic on the plan's inputs in a script, not in your head.
5. **Tag every claim**: VERIFIED (primary source, dated), PARTLY VERIFIED (explain), CONTRADICTED (give the right figure), UNVERIFIED (plausible, not checked), UNMAPPABLE (no source can exist or be found, such as invented job titles or internal projections). Keep UNMAPPABLE as its own list.
6. **Run the next lenses.** Pre-mortem for failure modes; blind VC review for a hostile external view. The reviewers must be blind to each other.
7. **Initialise shared context** if missing: update AGENTS.md (current venture, phase gate, handoff routine, authorization boundary for subagents) and create `context.md` using [context-md-template.md](./references/context-md-template.md).
8. **Report.** Save the register and findings in the idea's own folder. Surface the open decisions as structured questions for the founder.

## Guardrails

- Subagent dispatch: every brief carries an explicit denial of push, deploy, send, delete, and file-writing authority unless the task needs it; after dispatch, check `git status` and `git log origin/<branch>..HEAD`.
- Do not stretch a weak source into VERIFIED. One secondary source is PARTLY VERIFIED at best.
- Never alter the founder's documents silently. Propose corrections; record contradicted figures in the register.
- Never hardcode or print secrets or tokens found in a repo.
- Check domain, trademark, and entity claims with a live lookup (whois, dig, registry), and date the result.
