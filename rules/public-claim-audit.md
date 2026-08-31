# Public claim audit (all agents)

Applies when adding, editing, or reviewing any public-facing copy (homepage, landing pages,
`frontend/lib/ai-discovery.ts` / `/llms.txt` / `/llms-full.txt`, blog/guide content) or any
internal agent-guardrail doc that carries a customer-facing claim (`AGENTS.md`,
`.agents/skills/*/SKILL.md`, `docs/marketing_profiles.md`, `docs/context.md`,
`docs/product-brief.md`, `docs/outreach/brand_voice.md`) — and periodically as a standing health
check, since this repo has independently reinvented the same "grep public copy for forbidden
claims" guard test at least six times (C89, C97, C105, C112, C122, C146) without ever running them
as one family.

**This is advisory, not a gate.** A finding means "review this," not "stop implementation." Do
not block a commit, PR, or task on it — surface findings and let the project lead decide, the same way the
SEO-metadata rule treats title/description length as advisory while canonical mismatches are the
only hard blocker.

Full procedure (Claude Code): `.claude/skills/public-claim-audit/SKILL.md`.

## What it checks

- **Required boundary language:** the permanent 14-day free trial (never "two-week"/"30-day"),
  `Contact for pricing` for C146 implementation services, and the customer-retains-AML/CTF-
  responsibility sentence.
- **Forbidden claim patterns:** legal advice, Compliance Regulator approval, compliance certification, report
  lodgement, outsourced compliance-officer work, independent evaluation of YourApp's own work,
  "we make you/your agency compliant," "AI-powered compliance officer," a fixed delivery date or
  SLA, scarcity/urgency claims, and named infrastructure vendors in public copy.

## Existing guard-test family (run together, not just the one you touched)

`frontend/tests/unit/{public-copy-truth,public-trust-copy,public-trial-offer-truth,
public-homepage-copy,public-post-july-copy,c146-guardrails,compliance-officer-blog-freshness,
kyb-cdd-blog-truthfulness,aml-ctf-act-overview-freshness,dfat-sanctions-blog-freshness,
enrolment-deadline-blog-freshness,pep-sanctions-guide-freshness,
real-estate-obligations-freshness,smr-guide-freshness,tranche2-compass-blog-freshness,
tranche2-guide-freshness,tranche2-market-blog-freshness}.test.ts`

## When adding a new claim surface

Extend an existing test file for the same file/topic rather than creating a new one. Use
negative-lookbehind regex for forbidden patterns (see `c146-guardrails.test.ts`) so the assertion
does not false-positive on a sentence that correctly says "does not claim X" — a naive substring
match breaks the boundary sentences it's meant to protect.

## Comparison pages naming a competitor (added from C406, 13 Aug 2026)

A page that names a specific competitor (`docs/growth_visibility_plan.md` §4's Tier 1–3
comparison-content workstream — 12 pages committed across the 8-week plan) carries risk this
rule's existing checks don't cover: every other item above is about YourApp's own claims, but a
comparison page also makes claims **about the competitor**, which is Australian Consumer Law
comparative-advertising territory, not just marketing-copy hygiene.

- **Verify every competitor claim against the competitor's own current public site before
  publishing — never trust secondary competitive research alone.** C406 found this the hard way:
  `docs/growth_visibility_plan.md` §2's research assumed First AML had no audit trail; a live
  check of `firstaml.com` found they explicitly claim one. Publishing the unverified claim would
  have put a false statement about a named competitor on a public YourApp page. Record the source
  URL(s) and verification date in the change's completion log — see C406's tasks.md for the
  pattern.
- **Every negative claim about a competitor needs a source; an unverifiable one becomes an
  YourApp-only affirmative claim instead** (state what YourApp has, don't assert the competitor
  lacks it) rather than a flat, unsourced "X doesn't offer this."
- **Shoaib/legal sign-off is required before production release**, same posture as C333's SMR
  template-wording gate — mark it `GATED` in the change's `proposal.md` frontmatter, not just
  noted in prose, so it can't be missed at a glance.
- **Check `lib/ai-discovery.ts` against the C90 identity-disambiguation guard before naming a
  competitor there.** `openspec/changes/90-ai-entity-disambiguation/design.md` Decision D6: a
  competitor name may appear in `llms.txt`/`llms-full.txt` only inside a line that is itself a
  `/vs/<slug>` citation link — never in the identity-denial statement or scattered elsewhere.
  `tests/unit/lib/ai-discovery.test.ts` T90.03 enforces this structurally, not per-competitor-name
  — a new comparison page doesn't need its own carve-out.
