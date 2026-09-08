---
name: amlhive-content-drafting
description: Use when drafting AMLHive blog posts or compliance guides.
---

# AMLHive Content Drafting

## Trigger
Use when asked to write, draft, refresh, or review AMLHive (amlhive.com.au) blog posts, compliance guides, marketing copy, or content drafts (e.g. tasks named `TASK-0xx-…` landing in `docs/content-drafts/`). Also load when a task mentions Tranche 2, AUSTRAC CDD, eKYC, or any AMLHive public-facing claim.

## Canonical sources — read BEFORE drafting
AMLHive content governance lives in the repo, not the Hermes skill library. Read in order:
1. `AGENTS.md` → section **"Public Marketing And Implementation-Service Guardrails"** — the 14-day trial rule, tagline boundaries, and C146 services rules.
2. `docs/outreach/brand_voice.md` — locked taglines, messaging pillars, words use/avoid, AUSTRAC-accuracy rules (wins on drift).
3. `.agents/skills/amlhive-blogpost/SKILL.md` — the full blog workflow (topic → claim register → bundle → validation → CMS handoff).
4. `.agents/skills/amlhive-content-research/SKILL.md` + `references/validation-gates.md` + `references/amlhive-voice.md`.
5. `pluto-content-firewall` skill — applies to Haris's PERSONAL channels only. AMLHive copy is Stream 2: AMLHive itself may be named freely, but never reference Haris personally and never mention his other ventures inside AMLHive copy.

## Mandatory public-copy guardrails (non-negotiable)
- Trial offer: **"14-day free trial"** ONLY. Never "two-week", "30-day", or any variant.
- Tagline **"Your Virtual Compliance Officer"** may be used verbatim. Never imply AMLHive is a statutory officer, legal adviser, compliance certifier, or outsourced managed-compliance provider. State that the customer retains AML/CTF decisions and legal responsibility.
- C146 implementation services (Go-Live & Adoption, Secure Data Migration & Configuration, Integration Discovery and Delivery, Enterprise Rollout): **"Contact for pricing"**, remote delivery OK where suitable, NO delivery dates / SLAs / open-ended commitments.
- **One CTA max** + a general-information (not legal advice) disclaimer at the end.
- No AUSTRAC-approval claims; no automatic report-lodgement claims (SMRs/TTRs are lodged by the reporting entity via AUSTRAC Online).
- Language: Australian spelling; **SMR** not SAR, **TTR** not CTR; "Tranche 2" not "the changes"; business-day deadlines need the state-public-holiday caveat.
- Regulatory precision (full table + fetch playbook: `../../growth/amlhive-content-writing/references/austrac-source-verification.md`): **foreign** PEP = enhanced CDD **mandatory**, **domestic / international-organisation** PEP = **risk-based**, never an automatic block; sanctions match = prohibition + freeze + report to the Australian Sanctions Office and AFP; tipping-off (**s.123**, reformed offence in force **31 March 2025**) = disclosure that "would or could reasonably be expected to prejudice an investigation"; SMR obligation (**s.41**) needs a designated-service-to-a-customer nexus, so fraud on the agency's own office funds is not an SMR; source of funds ≠ source of wealth.
- Banned words: seamless, robust, leverage, synergies, AI-powered, enterprise-grade (SMB context).

## Medium-confidence intel convention
Claims from secondary/market reporting (market size, provider user counts, accreditation numbers) get an inline `//VERIFY: source (date) — what to confirm before publish` marker on the same line, PLUS a consolidated list in an HTML comment (`<!-- … -->`) at the bottom. Never invent facts beyond what the task provides; flag rather than fabricate.

## Length and word-count method
- Blog drafts target **1100–1400 words**. Count the visible body (everything before the first `<!--`), stripping markdown symbols. Inline `//VERIFY:` annotations count toward the total — so land around ~1300 to leave headroom (publishable prose without markers comes out shorter).
- If over target, trim in this order: short-answer intro → numbered CDD/checklist items → landscape bullets → CTA paragraph. Re-run the verifier after each batch.

## Verification — run before declaring done
Run `scripts/verify_amlhive_draft.py <path>` (asserts word count + all guardrails; exit 0/1). Do NOT trust a bare boolean: regexes span sentences — a multi-line `file.*SMR.*for you` pattern once flagged the compliant sentence "eKYC does not file reports for you" as a violation. Read any FAIL against the actual sentence before acting.

## Pitfalls
- The patch tool's fuzzy matching can merge two lines when you delete a blank line (saw "suggests:1." instead of "suggests:\n\n1."). Re-read the diff after trims.
- Sweep AMLHive drafts for Haris's other venture names (finai, paylicence, exitlens, tokenpilot, cloudproof, tapease, agentgate, cloudwise, verifylink) and "haris" — they must not appear; the reverse firewall holds even though AMLHive itself is the promoted brand.
- The full repo blog workflow wants OpenSpec plan gates + claim registers for CMS-ready bundles. A plain draft in `docs/content-drafts/` is a lower bar — match the task scope, don't invent a human decision, and never claim publication/deployment.

## Support files
- `scripts/verify_amlhive_draft.py` — word-count + full guardrail compliance checker.
