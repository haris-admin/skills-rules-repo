---
name: caduceus-compliance-watch
description: "Use for compliance watch: PSP reform, guardrails, mapping."
---

# Caduceus Compliance Watch

## Trigger
Any compliance task: regulatory intel, Tranche 2 analysis, PSP licensing watch, opportunity mapping, content guardrail check.

## Method

1. **Intel watch** (from Mempalace fintech-aml + regulatory-ai + payments-npp):
   - AUSTRAC: rules, transitional guidance, enforcement, deadlines
   - ASIC/APRA: AI accountability, financial services
   - PSP reform: Payments System Modernisation stages, ~450 providers
2. **Competitor moves**: PEXA Clear, AML Partners, Reapit Verify, GBG, Mitek, First AML, Dow Jones
3. **Translate**: regulation → "what this means for us" → product opportunity or risk
4. **Opportunity register** (from codex_deep_product_analysis.md):
   1. Transaction Evidence Packet (M, now)
   2. UBO Evidence API + review desk (M, the moat)
   3. Tranche 2 Professional Services Pack (M, conveyancers first)
   4. Screening Resolution Workbench (S/M)
   5. Fleet Settlement Console (S/M)
6. **Guardrail checks** for Aurora/Vulcan output:
   - No compliance guarantees · no regulator approval claims
   - No automated compliance decisions (human review = moat)
   - UBO: human-approved output only, never sell customer docs
   - Flag unsafe copy ("Tranche 2 Compliant in 14 Days" pattern)

## Feeds

This skill owns the authoritative regulatory **dates**. Keep two downstream skills in sync with the
"Key dates" block below: `data-sovereignty-market-screen` (per-opportunity go/no-go gate) and
`au-sovereignty-alignment-audit` (recurring check that shipped solutions haven't drifted; its
`references/au-incoming-regulation-register.md` maps each date here to "does it apply / what does
aligned look like"). When a date moves here, update those.

## Key dates (tracked)
- Tranche 2 in force: 1 Jul 2026 (general commencement 31 Mar 2026)
- Card surcharge ban: 1 Oct 2026
- Buy Australian AI Partnership (Stone & Chalk + NAIC): EOI closes 24 Sep 2026 (cohort notified 30 Sep); Accelerator Oct–Dec 2026 (~8 wks, cohort of 10) — see `buy-australian-ai-partnership-watch`
- Suncorp Bank merchant acquiring hard stop: 10 Dec 2026 22:00 AEST (facilities close 11 Dec); merchants forced to ANZ Worldline or churn. Suncorp→ANZ full platform migration by Jun 2027.
- AGDIS private sector: 30 Nov 2026
- EU AI Act Art 50 transparency: live 2 Aug 2026 (extraterritorial; high-risk deferred to Dec 2027/Aug 2028)
- ADM transparency obligation (APP 1.7/1.8): 10 Dec 2026
- PSP reform Tranche 1 to Parliament: Q4 2026 (12-18mo transition after Royal Assent)

## AML/CTF third-party reliance mechanics (reformed Act, in force 1 Jul 2026)
Get this exactly right — a bank's financial-crime counsel checks it in the first meeting.
- **Statutory basis:** Act **s 37A** (standing written CDD arrangement + safe harbour), **s 37B** (regular assessment — at least every 2 years and on significant change; written record within 10 business days), **s 38** (case-by-case, stricter, no safe harbour), **s 37** (agency — a different route). AML/CTF Rules 2025 **ss 6-29 to 6-33** (6-32/6-33 = a property/conveyancing-specific model).
- **Who can be relied on:** only another **reporting entity** (or a foreign entity under FATF-equivalent regulation and supervision). AUSTRAC states verbatim that reliance "doesn't include a KYC or outsourced service provider." **A software/evidence provider cannot be a relied-upon party.**
- **Reliance ≠ outsourcing ≠ agency.** In all three, regulatory responsibility for each entity's own program stays with that entity. The s 37A safe harbour forgives only *isolated* counterparty failures; outsourcing/agency give no safe harbour and the RE stays fully liable.
- **The relying entity** must have reasonable grounds (at entry) to believe the third party's CDD meets the Rules, that reliance suits its ML/TF risk, plus a written arrangement with prescribed content (responsibilities incl. record-keeping; right to obtain KYC info before the service and verification data within ~1 business day).
- **Transition:** pre-1 Jul 2026 reliance agreements are **not grandfathered** — review them.
- **Weak link (needs a lawyer):** the *direction* of reliance. "A big bank relies on a small newly regulated agency" is hard — s 37A puts the reasonable-grounds / appropriateness test on the *relying* entity. Don't assume a bank accepts agency-side CDD in production; the near-term buyer is the Tranche 2 business (and mutual ADIs via Cuscal), not Tier-1 production reliance.
- **AMLHive's place:** evidence pipe + provenance + consent/permission control + audit trail. **Never a party to the reliance. Carries no CDD liability.** "AMLHive transfers evidence, never responsibility."

## AI regulation reality (AU 2026)
- NO standalone AU AI Act — National AI Plan (2 Dec 2025) chose standards-led, sectoral-regulator path; AI Safety Institute is advisory-only ($29.9M, no enforcement).
- Mandatory AI pressure comes from: Privacy Act ADM disclosure (10 Dec 2026), EU Art 50 (live), ISO 42001 procurement expectations, AUSTRAC 2026 NRA (AI risk flagged).
- Data sovereignty: data-centre expectations 23 Mar 2026; GovAI = AU infrastructure only (PSPF/ISM/IRAP for gov-facing).

## Positioning vs PEXA
- AMLHive = "independent agency compliance operating system" (pre/post-settlement continuity)
- Differentiate on: AI triage, UBO evidence, training, program governance, audit
- Never claim settlement intelligence or source-of-funds certainty

## Delivery
- Dated + sourced + "what this means for us" line.
- 🔴ACTION/🟡DECISION/🟢FYI framing.

---

# PSP Reform Watch — Tapease (weekly cron, Tue 9AM AEST)

Monitors Treasury's PSP licensing reform and its impact on Tapease's plan: funds flow Tapease→drivers = facilitation risk (s766DC). Fix: acquiring→Fiserv (Clover ISV), driver payouts→Oxygen Global (AFSL 452 187 prepaid Visa) so no funds sit in Tapease-controlled accounts → no new AFSL needed. NOTE: "PSP Tranche 2" (common access, standard-setting body, ePayments Code) ≠ AML/CTF Tranche 2 — don't conflate.

## Sources (check every run)
1. Treasury page: https://treasury.gov.au/policy-topics/banking-and-finance/payments-licensing-reforms (check dcterms.date / "Last updated")
2. Consultation hub — beta server-rendered mirror (consult.treasury.gov.au is JS-only, returns "Loading"):
   - https://beta.treasury.gov.au/key-activities/consultations/c2026-746108 (Tranche 1 full package)
   - https://beta.treasury.gov.au/key-activities/consultations/c2025-700532 (Tranche 1a)
   - https://beta.treasury.gov.au/key-activities/consultations (listing — scan for NEW PSP/ePayments consultations)
3. web_search: `"payment service provider" reform Australia 2026 Treasury update`, `PSP licensing Tranche 2 ePayments Code`, exact-title search `"Treasury Laws Amendment (Payments System Modernisation) Bill 2026"` to detect Parliament introduction.

## PSP reform verified timeline (Mercury, 1 Sep 2026 — first observation)
- Page last updated **12 Mar 2026** (Tranche 1 full exposure draft release). No change since.
- c2026-746108 (Tranche 1: Treasury Laws Amendment Bill 2026 + Payment Entities (Prudential Regulation) Bill 2026 + draft regs): OPEN 12 Mar → CLOSED 9 Apr 2026 (extensions to 13–14 Apr). Submissions: FinTech Australia, DECA, Law Council, etc.
- c2025-700532 (Tranche 1a): closed 6 Nov 2025 (51 submissions).
- Tranche 1 Bill **NOT yet introduced to Parliament** as of 1 Sep 2026. Govt signalled winter sitting (Jun–Aug 2026); missed → expected Q4 2026. Commencement = 12 months after Royal Assent ≈ mid-late 2027. Transition: 1 month for existing AFSL holders to vary; 6 months for other PSPs to apply.
- PSP Tranche 2 (common access requirements, industry standard-setting body, ePayments Code review/update): NO consultation opened yet ("later in 2026").
- Adjacent: Scams Prevention Framework (SPF) draft codes/rules consultation closed 25 Jun 2026; regulated entities prep by 31 Mar 2027; SPF takes priority over ePayments Code for scams.

## Tapease impact lens (answer these each run)
1. **Payment facilitation services limb** = receiving funds + transferring per instructions (acquiring, remittance, flow-of-funds). Tapease avoids it if Fiserv acquires + Oxygen issues — money never touches Tapease accounts.
2. **Payment technology & enablement services limb** (gateways; transmits info needed to produce transfer instruction, not payer/payee/issuer) is BROAD — "any entity that touches a payment". Main residual exposure: Tapease as tech connector could need own AFSL. DECA submission (9 Apr 2026) asks to exclude non-custodial tech infrastructure — aligned with Tapease; watch final Bill.
3. **Safeguarding** (payment-related money) falls on Fiserv/Oxygen as money holders — structure validated. Keep evidence in contracts: no funds control, not payer/payee/issuer, tech-only role.
4. **Mandatory ePayments Code**: Ministerial rule-making power in Tranche 1; can reach ADIs, licensed PSPs, PSRA-regulated entities and entities *acting on their behalf*. Keep Tapease out of consumer-facing dispute/IDR roles; note intermediary PSP obligations (cooperate with AFCA/IDR).
5. Exemptions to track in final regs: low-value payment services (~$8M/month cap), single-payee exemption, transitional/grandfathering.

## PSP watch output format (Telegram-ready, 2-min digest)
1. WHAT changed (dates/documents/consultation openings-closings)
2. IMPACT on Tapease (Fiserv/Oxygen strategy, facilitation risk, tech-enablement limb, safeguarding, ePayments Code)
3. ACTION needed (new consultation to respond to, timeline shifts, contract items)
4. Next check date. Frame: 🟢 FYI / 🟡 DECISION / 🔴 ACTION. If nothing material: one line + stop (or [SILENT] per cron rules).

## History
- 2026-09-09 (ANZ / Stone & Chalk): **ANZ APRA CEU scope clarified** — the 3 Apr 2025 Court Enforceable Undertaking ($1bn op-risk add-on, Program PACT / RCRP / Promontory) is a **Global Markets trader-conduct / non-financial-risk** action, NOT AML. ANZ has no AUSTRAC enforcement history and no public AML remediation program (unlike CBA/Westpac/NAB). BUT Group Financial Crime governance is named in the Promontory report as a Line 2 function being restructured under PACT, and APRA's thesis is ANZ cannot bolt on discrete point solutions — so an AML/CDD vendor pitch to ANZ is off-message by design; least receptive now–end 2026; never name ANZ in an accelerator-public artefact for AML/CDD/onboarding. **Cuscal Financial Crimes growth corrected: +19% to $9.5M (1H26), ~6% of FY26 NOI** — a "+42%" figure in circulation did not verify. **Suncorp merchant migration** (see Key dates) is a compressed forced merchant re-onboarding wave = the "migration-cohort KYB" use case; pitch to CBA, not ANZ. Full analysis: `alexandria/vault/decisions/anz-worldline-suncorp-merchant-migration-2026-09-09.md`.
- 2026-09-03 (Tranche 2 digest): No new AUSTRAC enforcement/lodgement deadlines (register unchanged: Mounties/Entain/Star current, bet365 EU ongoing, Cryptolink suspended). ASIC final-call MR 2 Sep: >45 digital-asset licence apps (up from ~30 in Jun); INFO 225 no-action ends 30 Sep (27 days from 3 Sep); from 1 Oct unlicensed = breach, fines to 10% turnover. AUSTRAC guidance update 31 Aug: real estate + professional designated services pages — licence-to-occupy/leasehold treatment. FATF 5th-round ME still 2026-27, no on-site date. No AUSTRAC news 29 Aug–3 Sep.
- 2026-09-02 (Tranche 2 digest): s167 notices to non-enrolled businesses (28 Aug — RE/legal/accounting/jewellers). Cryptolink VASP reg suspended 3 months (10 Aug, 96 CATMs offline, $56,340 IN paid). Sportsbet EU finalised. INFO 225 no-action expires 30 Sep 2026 (28 days; ~30 licence apps; AML/CS: notify+pre-meeting by 30 Sep, lodge in 12mo). Digital Asset Framework commences 9 Apr 2027 (DAP/TCP auths). AML/CTF Amendment Bill 2026 still before Reps. FATF 5th-round ME 2026-27, no on-site date published; 4th FUR (Mar 2024): 18C/12LC/6PC/4NC, Rec 15 C→PC.
- 2026-09-01: Baseline. No new change. Bill not introduced; PSP Tranche 2 not open. Strategy validated; watch tech-enablement definition in final Bill + ePayments Code scope.
