---
name: amlhive-content-writing
description: "Write AMLHive public copy within brand and CTA guardrails."
---

# AMLHive Content Writing

## When to use
Any task producing or reviewing public AMLHive copy: blog articles, compliance guides, landing pages, newsletter, or social drafts for amlhive.com.au. Deliberately separate from `pluto-content-firewall`, which governs Haris Habib's personal brand (harishabih.au / LinkedIn). The two streams must never cross or reference each other.

## Non-negotiable guardrails (AGENTS.md + C146 + brand voice)
1. **Offer:** the permanent eligible-account offer is a **14-day free trial**. Never "two-week", "30-day", or any other duration.
2. **Tagline:** "Your Virtual Compliance Officer" — verbatim and capitalised when used. It never implies AMLHive is a statutory officer, legal adviser, compliance certifier, or outsourced managed-compliance provider. Always keep the responsibility boundary: the reporting entity retains its AML/CTF decisions, risk judgement, legal responsibility and AUSTRAC lodgements. Reports are never auto-submitted.
3. **Implementation services:** only the four C146 services — Go-Live & Adoption, Secure Data Migration & Configuration, Integration Discovery and Delivery, Enterprise Rollout. Use "Contact for pricing"; remote delivery "where suitable". Never promise a delivery date, SLA, compliance outcome, or legal advice.
4. **Structure:** exactly one CTA per piece (normally the 14-day free trial), plus a closing disclaimer: general information only, not legal advice; check AUSTRAC's current guidance and consult a professional adviser.
5. **Facts:** never claim AUSTRAC approval, guaranteed compliance, automatic lodgement, or unavailable features. No invented dates, stats, or regulatory detail — use only task-given facts, repo-sourced facts (live `content.ts` files), or primary sources. Re-verify regulatory facts before publication; they go stale.

## Source of truth — read before writing
Repo map and exact paths: `references/amlhive-content-guardrails.md`. Key files: `AGENTS.md` guardrails section, `docs/branding.md`, `docs/outreach/brand_voice.md`, `docs/pluto_agent_instructions.md` (controlled facts), and `frontend/app/Compliance/*/content.ts` (live published facts safe to reuse, e.g. `austrac-tranche-2-guide/content.ts`).

## Voice
Direct, practical, urgent-but-calm, credible — a knowledgeable no-nonsense compliance expert, not a regulator or lawyer. Australian English (organise, enrolment, lodgement, program). Spell out first use: Customer Due Diligence (CDD), Suspicious Matter Report (SMR — never "SAR"), Threshold Transaction Report (TTR — never "CTR"), and define "designated service" (AUSTRAC's term) the first time.

## AUSTRAC accuracy rules (non-negotiable)
- SMR timing: within 24 hours of a terrorism-financing suspicion; within 3 business days for other suspicions. Business-day counts vary with state public holidays — say so.
- CDD records generally kept 7 years from the end of the business relationship or completion of an occasional transaction.
- Tipping off (section 123 of the Act) is a criminal offence — treat seriously, never casually.
- Sanctions match = legal obligation to refuse/report. PEP match = enhanced due diligence, NOT automatic refusal. Never conflate.
- Do NOT reference "Part A / Part B" of AML/CTF programs — that structure was abolished (repo issue-023).
- Enrolment: general rule within 28 days of starting a designated service; AUSTRAC's transition enrolment date was 29 July 2026. Check current AUSTRAC guidance for the reader's circumstances.

## Structure (answer-first)
H1 + first-paragraph direct answer ("Yes, it applies to you if..."). Question-phrased H2s. Obligations as numbered lists. Practical steps. Consequences of non-compliance. One CTA + disclaimer. Articles typically 1200–1500 words.

## After writing — verify
Run the sweep commands in `references/amlhive-content-guardrails.md`: grep banned trial durations and banned words (expect nothing), em-dash count = 0, body word count via awk excluding YAML frontmatter. Apply a `humanizer` pass: no em dashes, no AI-isms (seamless/robust/end-to-end/leverage/AI-powered), varied sentence rhythm, minimal bold.

## Delegated drafts (subagents) — always re-sweep yourself
When content is drafted by delegated subagents (parallel `delegate_task`), the
subagent's "all compliance checks pass" self-report is NOT trustworthy — the
2026-08-08 batch (3 AMLHive drafts) came back with 63 em-dashes across two
files despite each subagent claiming a clean pass. After delegation lands:
1. Re-run the full sweep yourself (em-dashes, banned words, trial durations)
   over the actual files — do not trust the summary.
2. Fix mechanically (`text.replace("\u2014", ",")`) rather than re-delegating.
3. Verify word counts against the spec; subagents trim/expand to fit but check.
4. If you asked for `//VERIFY:` markers on medium-confidence intel, grep for
   them and resolve each before publication — they are the paper trail for the
   claims Pluto must check against primary sources.
To get markers reliably, put the exact marker text in the delegation goal
(e.g. 'mark any claim from medium-confidence intel with a //VERIFY: comment').

## Publication flow — IndexNow ping
After a post is published, ping IndexNow (`https://api.indexnow.org/indexnow?url=<page>&key=<KEY>`).
Key handling and the IndexNow-vs-Bing-Webmaster-API distinction are in
`references/bing-indexnow-verification.md` (both `.env` keys are IndexNow keys;
the Webmaster API rejects them).
