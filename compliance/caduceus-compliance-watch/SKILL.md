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
- Tranche 2 in force: 1 Jul 2026 (general commencement 31 Mar 2026); Tranche 2 enrolment deadline (transitional) 29 Jul 2026; compliance-officer notification 30 May 2026 (existing REs) / 29 Jul 2026 (T2 + newly regulated VASPs)
- Tranche 2 first Annual Compliance Report: reporting period moves to financial years — first period 1 Jul 2026 – 30 Jun 2027, submission window 1 Jul – 30 Sep → **due by 30 Sep 2027** (verified at source on AUSTRAC annual-compliance-reports page)
- Card surcharge ban: 1 Oct 2026 — **taxi fares: the federal carve-out is GONE but surcharging has not been banned for taxis.** Precisely: RBA Standard No. 3 of 2016's **taxi-fare exclusion was removed**, so the networks' no-surcharge rules now reach taxi fares at rule level; **but** RBA FAQ still says *"surcharging in the taxi industry remains the responsibility of state and territory regulators"*, and states keep their own caps (SA DIT confirmed from 1 Oct 2026 the max **non-cash taxi surcharge stays 5%** and the RBA reforms "do not change South Australia's current rules"). So: no federal ban on taxi surcharges, no federal permission either — it is a **state/territory question** now. **Do not attribute this ban to TapEase** (taxi sector — owner correction 22 Sep 2026). Its reform clocks are CPS 230 + the acquiring migration. The companion **interchange-cap** reduction is separate and sector-agnostic.
- Buy Australian AI Partnership (Stone & Chalk + NAIC): EOI closed 24 Sep 2026 (applicants notified 28 Sep); **National digital track 12 Oct – 4 Dec 2026**; **Intensive accelerator track (10 companies) 1 Feb – 25 Mar 2027** (re-verified at source 12 Oct 2026 — the earlier "Accelerator Oct–Dec 2026" was wrong; the Oct–Dec window is the *digital track*, not the cohort) — see `buy-australian-ai-partnership-watch`
- **RBA card-fee transparency (all in force; merchant statements may comply with old OR new rules 1 Oct 2026 – 31 Mar 2027):** **30 Oct 2026 — LANDED.** First-ever public acquirer price tables published (Table 21, quarter 1 Jul – 30 Sep 2026, i.e. a **pre-interchange-cut baseline**). Verified first-release averages (% of card transaction value, **all direct / small ≤$1m / medium $1–10m**): **Westpac 0.55 / 0.79 / 0.65** · **ANZ Worldline 0.55 / 0.97 / 0.82** · **NAB 0.58 / 0.87 / 0.66** · **CBA 0.55 / 0.86 / 0.70** · **Tyro 0.94 / 1.08 / 1.02** · **Square 1.34 / 1.47 / 1.17**. Small-merchant in-store debit spans **Westpac 0.60% → Square 1.42%**; foreign-issued cards dearest (~2.0–2.15% small merchants). AP+ reported **895.7M domestic eftpos transactions / $48.9bn** in the quarter at **2.8c average eftpos interchange**. Acquirers must keep the data up until **30 Sep 2028**; RBA to republish. **30 Jan 2027** — large acquirers publish interchange pass-through for the Oct–Dec 2026 quarter, then 30 Apr / 30 Jul / 30 Oct 2027. Re-check any copy quoting merchant rates — the post-cut comparison only exists from the 30 Jan 2027 release. (rba.gov.au conclusions-paper appendices C/D + FAQs; CBA average-merchant-service-fee page; Tyro MSF transparency PDF)
- ATO credit-card acceptance: original stop **30 Nov 2026**, **delayed to end of FY → 30 Jun 2027** by Chalmers/Aly/Mulino joint statement 9 Oct 2026 with transitional funding (cost finalised in Dec 2026 MYEFO); from 1 Jul 2027 credit cards still accepted **via third parties** plus debit card and bank transfer. Post-surcharge-ban who-pays flashpoint — cite carefully, it moves.
- **PEXA / IPART ELNO service-fee review — Final Report to the Minister due 30 Oct 2026** (revised from the earlier "September" / 30-Sep expectation; re-verified at source 1 Oct 2026 from PEXA's ASX announcement + IPART's own timetable page). The draft report found PEXA ~99% market share and little competitive constraint from Sympli; it modelled a **-33% to -36% cut to transfer fees** (single title $146 → $93), ~-20% revenue impact on PEXA's Australian Exchange division from FY28, with changes to run four years from 1 Jul. Watch: it resets PEXA Clear's pricing/packaging incentive, so any AMLHive copy referencing PEXA Clear pricing must be re-checked after 30 Oct 2026 and never published with a stale date.
- **Reapit (standing watch):** productising **AML/CTF as a CRM comparison axis** ("Built-in AML & ID Verification", ✓ Reapit / ✗ alternatives) **and** publishing AI-crawler-discoverability content ("Can AI find your agency?") — direct overlap with AMLHive's buyer set and its AI-authority lane. Evidence for private research/decision records only; never named in public AMLHive independence/denial copy (see the operating contract's Ethical Search And Reputation Rules).
- Suncorp Bank merchant acquiring hard stop: 10 Dec 2026 22:00 AEST (facilities close 11 Dec); merchants forced to ANZ Worldline or churn. Suncorp→ANZ full platform migration by Jun 2027.
- AGDIS private sector: 30 Nov 2026
- **RITS tokenised-settlement consultation: closes 30 Oct 2026** (RBA, mr-26-24; same release confirmed **no public-interest case for a retail CBDC** — that question is settled). The live track is wholesale tokenisation settlement.
- **RBA Review of Payments System Regulation** (separate from Treasury's PSP licensing): Issues Paper 25 Jun 2026; **Summary of Submissions published Oct 2026 — 75 submissions**; **PSB met 19 Nov 2026 (MR 2026-32)** — took stock of submissions (mobile wallets, three-party/Amex, A2A, agentic commerce), gave guidance on priorities, **no new rule**, **priorities to be published by end-2026**, then further consultation **from mid-2027**; PSB reiterated dual-network debit must be available in *all* form factors including those used in agentic commerce, and reported high 2025/26 card-rule compliance with merchants **broadly having stopped surcharging** on designated networks post-1 Oct. Submissions pressed debit-network provisioning in wallets/online (tokenisation gave the international networks first-mover advantage and eftpos was absent from routing even where LCR was enabled), Apple Pay NFC access + fee transparency, Amex/three-party parity, BNPL no-surcharge review, token portability, A2A access/sponsorship, and **AI agents in e-commerce** (weight favoured monitoring + industry standards on authority/liability). This is the sharpest "common access" evidence base for PayLicence — RBA lane, not Treasury.
- **ACCC authorisation for the AusPayNet/AP+ A2A Payments Roundtable:** original AA1000690 ran to **31 Jan 2027**; on **28 Oct 2026** the ACCC issued a draft determination proposing revocation + substitution of **AA1000739** extending the collaboration a further 6 months to **31 July 2027** (submissions close **16 Nov 2026**; final determination expected **Dec 2026**). A2A roadmap directional view due **Dec 2026**, public consultation **before end Q1 2027**, next Roundtable **27 Nov 2026**. (Do not quote 31 Jan 2027 as the end date any more — cite it as "extended, proposed to 31 Jul 2027".)
- **DECA "Regulating Agentic Commerce" roundtable — Proactive Policy Forum, Canberra, 15 Mar 2027** (DECA Oct 2026 agentic-commerce brief; industry consultation runs to it; evidence gap named = "records needed to establish responsibility and recourse").
- **ANZ Rewards points caps from 28 Oct 2026** ($25k Platinum / $50k Black eligible spend per statement period) — rewards repricing continues past ban day.
- EU AI Act Art 50 transparency: live 2 Aug 2026 (extraterritorial; high-risk deferred to Dec 2027/Aug 2028)
- ADM transparency obligation (APP 1.7/1.8): 10 Dec 2026
- PSP reform Tranche 1 to Parliament: Q4 2026 (12-18mo transition after Royal Assent)
- **Digital assets / DAF (this digest's own lane — track the countdown here):** INFO 225 class no-action **expired 30 Sep 2026** (last extension 25 Jun; no further extension) → from 1 Oct, un-lodged providers are uncovered, civil + criminal exposure to **10% of annual turnover**. **CP 392** (ASIC 26-245MR, 15 Oct 2026) = DAF implementation standards + draft guidance, **submissions close 5pm AEDT 27 Nov 2026** (fintech@asic.gov.au). DAF Act commences **9 Apr 2027** per ASIC's roadmap + Dentons; the **Act's own commencement table and ASIC's CP 392 media release say 8 Apr 2027** — the Act received Royal Assent 8 Apr 2026 and commences "the day after the end of 12 months beginning on the day of Royal Assent", so **reconcile at source before quoting either date**; full force 9 Oct 2027. Licensing under DAF is *additive* to an AFSL.

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

## AUSTRAC "Enrol with us" page watch (daily cron `ce9caadf1d7b`, 07:15 AEST)

Canonical Tranche 2 enrolment page: **https://www.austrac.gov.au/new-austrac/enrol-us/enrol-us-overview**.
Watch it for in-place edits (no changelog/RSS exists): the 28-day enrolment obligation, the 14-day
detail-update window, who must register vs enrol, removal from the Reporting Entities Roll
(s51G / Rules 3-8), reporting-group enrolment, and the "Enrolment progress by industry" table.

- Monitor-noise note (22 Sep 2026): this cron's `monitor_url` hashes the FULL HTML of the Treasury page, so
  Drupal asset-hash churn (`css_*.css` / `js_*.js` filenames, `gtag.js?<hash>`) fires a false "changed" diff.
  A diff whose only lines are those is NO CHANGE — the real test stays dcterms.date / "Last updated" in the body.
- Detector: `~/.hermes/scripts/austrac_enrol_overview_watch.py` (deterministic: AS_OF, table,
  headings, obligation sentences, content hash — no timestamps, so unchanged ticks stay silent).
  Wired as the cron's `monitor`, so the LLM only runs when the page actually changes.
- **URL note:** `https://www.austrac.gov.au/new-austrac/enrol-or-register/enrol-us` now **301-redirects**
  to the canonical URL above (verified 13 Sep 2026). `austrac_enrolment_gap.py` still points at the
  redirecting path; `curl -L` follows it, so that weekly job still works — but any future reader
  should treat the `/enrol-us/enrol-us-overview` path as canonical.
- Baseline 13 Sep 2026: AS_OF **27 August 2026** — accounting/prof 13,610 · conveyancer 1,590 ·
  jewellers 300 · lawyer 6,500 · real estate 18,070 · **total 40,070**.
- Do not inflate a table refresh into a rule change, or soften an obligation-wording change into
  "a refresh" — say which it is.

## PSP Reform Watch — Tapease (weekly cron, Tue 9AM AEST)

Monitors Treasury's PSP licensing reform and its impact on Tapease's plan: funds flow Tapease→drivers = facilitation risk (s766DC). Fix: acquiring→Fiserv (Clover ISV), driver payouts→Oxygen Global (AFSL 452 187 prepaid Visa) so no funds sit in Tapease-controlled accounts → no new AFSL needed. NOTE: "PSP Tranche 2" (common access, standard-setting body, ePayments Code) ≠ AML/CTF Tranche 2 — don't conflate.

## Sources (check every run)
1. Treasury page: https://treasury.gov.au/policy-topics/banking-and-finance/payments-licensing-reforms (check dcterms.date / "Last updated")
   **Monitor-noise (7th incident, 24 Nov 2026):** besides css/js hash churn, Treasury has run a site-wide Drupal **antibot** deployment — an injected `<noscript><style>form.antibot…</style></noscript>` ahead of the description meta and canonical/identifier switching **https→http**. All of that is infra churn: page `last-modified` moving while `dcterms.date` stays 12/03/2026. The only real test remains `dcterms.date` + the body's "Last updated" line.
2. Consultation hub — beta server-rendered mirror (consult.treasury.gov.au is JS-only, returns "Loading"):
   - https://beta.treasury.gov.au/key-activities/consultations/c2026-746108 (Tranche 1 full package)
   - https://beta.treasury.gov.au/key-activities/consultations/c2025-700532 (Tranche 1a)
   - https://beta.treasury.gov.au/key-activities/consultations (listing — scan for NEW PSP/ePayments consultations)
   **The mirror is STALE (verified 22 Sep 2026):** its listing's newest consultation is 26 May 2026, while the
   live hub carries open items closing 18 Oct 2026; its c2025-700532 dates (9 Oct–22 Nov 2025) also disagree with
   the live page (9 Oct–6 Nov 2025). Use the beta mirror only for individual consultation pages (those match).
   For NEW-consultation detection use the LIVE hub `https://consult.treasury.gov.au/` — a Converlens SPA that
   now loads in the browser; `js("document.body.innerText")` returns the list (sorted by close date desc, so
   page 1 holds every item closing latest). URL params `?search=`/`?page=`/`?q=` do NOT filter or paginate and
   synthetic clicks on the interest/status checkboxes do nothing — scan page 1 instead. Canonical per-consultation
   URLs are `https://consult.treasury.gov.au/c<ID>` (c2026-746108 live = Closed 12 Mar–9 Apr 2026, survey closed,
   no consultation-outcomes section yet). `site:consult.treasury.gov.au <term>` via web_search is the cheap finder.
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

## Daily-digest source URLs (verified 14 Sep 2026 — fetch these, don't guess)
AUSTRAC (all plain-HTML, curl-able; each page carries a "Last updated:" line — compare it first):
- News hub: https://www.austrac.gov.au/news-and-media — but the complete dated list is
  https://www.austrac.gov.au/news-and-media/news-and-media-releases?combine=&field_industry_target_id=All&year=All
  (the hub itself renders the list out of order; the listing is authoritative)
- Enforcement actions: https://www.austrac.gov.au/about-us/record-our-actions/enforcement-actions-taken
- VASP registration actions: .../record-our-actions/virtual-asset-registration-actions
- Remittance registration actions: .../record-our-actions/remittance-registration-actions
- s162 external-auditor notices: .../record-our-actions/written-notices-appoint-external-auditor
  **Announcement→register lag (verified 18 Sep 2026):** the remittance/VASP registration-actions pages can
  publish entity-level entries **1–2 weeks after** the aggregate news announcement (10 Sep "45 registrations
  removed" → names appeared in the 17 Sep page update). So: check the page's own *Last updated* line every run,
  and when it moves with no post-dated decision, call it a **disclosure/register change**, not a new enforcement
  action — state which. The newest *decision date* on the page is the real "is this new?" test.
- Latest guidance updates: https://www.austrac.gov.au/industry-and-business/obligations-and-guidance/latest-guidance-updates
- Consultations (open/closed + deadlines): https://www.austrac.gov.au/industry-and-business/consultations
- Enrolment table: https://www.austrac.gov.au/new-austrac/enrol-us/enrol-us-overview
- Sitemap for URL discovery: https://www.austrac.gov.au/sitemap.xml (its <lastmod> values are bulk-touched, NOT publish dates — do not date anything from them)

ASIC: news/search pages are JS-rendered and there is **no RSS feed** (all /rss* paths 404).
Use the sitemap instead: `curl https://www.asic.gov.au/sitemap.xml` (regenerated daily ~05:00 AEST —
check its HTTP `last-modified` to confirm freshness), collect every `<loc>` under `/about-asic/news-centre/`
with its `<lastmod>`, sort descending. Max lastmod = newest publication, so "nothing since <date>" is
directly provable. Caveat: an old release page can be re-touched (lastmod ≠ publish date for low-numbered
MRs), so read the page's own "Published" line before calling something new.
Digital-asset licensing: https://www.asic.gov.au/regulatory-resources/digital-transformation/digital-assets-financial-products-and-services (INFO 225).
**Newest-MR probe (verified 16 Sep 2026):** the sitemap is regenerated ~05:00 AEST, so anything published
later that day is ABSENT from it. Fastest new-release detector: take the highest `26-NNNmr` in the sitemap,
then GET `.../2026-releases/26-(NNN+1)mr-...` — a 404 is not usable (the slug is required), so instead
web_search `"26-<NNN+1>MR"` (the ASIC page title carries the number) or read /newsroom featured items.
Absence in the 05:00 sitemap + presence live = published today. Discovered via 26-218MR (15 Sep).

**Cross-run catch-up (verified 20 Sep 2026):** the sitemap only shows what existed at its ~05:00 AEST regeneration, so a release published Fri afternoon is invisible to that morning's run and appears in the **next** day's sitemap. Compare the max `26-NNNmr` number across runs — a jump of >1 means an item was missed, and it must be reported (dated to its real publish day), not silently skipped.

**Sitemap generation clock (verified 2 Oct 2026):** the generation timestamp in `Last-Modified` is NOT fixed —
observed 19:00Z (=05:00 AEST next day), 23:05Z, and **08:05Z (=18:05 AEST the same day)**. The latest observed
pattern (08:05Z) means the 08:00 AEST run is served the *previous* day's complete set, so a 1 Oct item IS
visible to the 2 Oct run — never assume "published yesterday afternoon = invisible". Always read `Last-Modified`
and test whether it covers the last completed business day; same-day releases (~09:00 AEST) stay out of reach.
**Sitemap freshness caveat (verified 15 Sep 2026):** the sitemap is served from CloudFront and can be a
day+ stale (response `Age` ~10h, `Last-Modified` one business-day behind). Query strings do NOT bust it.
Before calling "nothing since <date>", confirm the sitemap's max news `<lastmod>` covers the last completed
business day; if not, cross-check the live newsroom page (`https://asic.gov.au/newsroom` is server-rendered
and lists featured items with dates) and third-party coverage. There is no JSON:API (`/jsonapi*` → 404) and
the 2026-releases listing is JS-only, so the sitemap + newsroom pair is the practical toolkit.

FATF pages are Cloudflare-gated against curl — use `web_extract` or the browser, not the shell.

## History

Recent entries inline (newest first). Entries dated **2026-10-31 and earlier** are archived in `references/digest-history-2026-10.md`; **2026-09-30 and earlier** in `references/digest-history-2026-09-and-earlier.md`. Full run outputs also live in `~/.hermes/cron/output/<job>/`. Keep new entries to **≤6 lines**.

- 2026-11-24 (Tue 09:00 AEDT, PSP weekly — cron 40362e331727): **No PSP licensing change; monitor trigger = site-wide Drupal antibot deployment (7th false positive, new variant).** Treasury body identical — `dcterms.date` **Thu 12/03/2026**, "Last updated 12 March 2026", T1/T2 wording unchanged; the diff is the injected `<noscript>form.antibot` style block, canonical/identifier flipping **https→http**, new css_00xu…/css_HUx9… hashes and `gtag.js?tosjnl` (page `last-modified` 20 Nov 2026, HTTP 200 for curl — not a bot block). **Live hub page 1: still NO PSP/ePayments/standard-setting-body consultation**; c2026-746108 re-verified in-browser = **Closed 12 Mar–9 Apr, no outcomes section**; two open items new since 17 Nov but off-lane (CDR Data Standards implementation-effort survey, closes 15 Feb 2027; innovative income streams, 14 Jan 2027); CDR NPP service-values alignment open to 16 Dec. **Tranche 1 licensing Bill still NOT introduced — APH 131 bills before Parliament (was 127), `payment`/`modernisation` title searches = only Hume's private Senator's Taxation Administration Amendment (Reinstating Credit Card Payments) Bill 2026 (16 Nov, before Senate).** 🟢 **PSB met 19 Nov (RBA MR 2026-32):** took stock of the Review submissions (mobile wallets, three-party schemes, A2A, agentic commerce), **priorities published by end-2026**, reiterated dual-network debit in *all* form factors incl. agentic-commerce; 2025/26 card-scheme compliance high and **merchants have broadly stopped surcharging** on designated networks; no new rule. Tapease lens unchanged: Fiserv acquirer + Oxygen issuer keeps funds out of Tapease accounts → no s766DC facilitation; s766DD tech-enablement + mandatory ePayments Code remain rule-making powers only until Bill text is tabled. Next check: Tue 1 Dec 09:00 AEDT.

- 2026-11-17 (Tue 09:00 AEDT, PSP weekly — cron 40362e331727): **No PSP licensing change; monitor trigger = Drupal asset-hash churn (false positive, 6th time).** Treasury body byte-identical — `dcterms.date` **Thu 12/03/2026**, "Last updated 12 March 2026", T1/T2 wording unchanged; diff only `css_11SYnO…`/`css_WQ9Pwl…`/`js_XMBAlj…`/`gtag.js?tokmhl` + permissionsHash. **Live hub page 1: still NO PSP/ePayments/standard-setting-body consultation**; c2026-746108 re-verified in-browser = Closed 12 Mar–9 Apr, no outcomes section. **New since 10 Nov:** `Consumer Data Right NPP service values alignment – draft standards` (Open, closes **16 Dec 2026**) — A2A/NPP-adjacent, not licensing. **APH back online** (was down 10 Nov): **127 bills**, zero payments-licensing bills — the only payments-titled bill is **Taxation Administration Amendment (Reinstating Credit Card Payments) Bill 2026** = **private Senator's bill (Hume), introduced 16 Nov 2026, before Senate**, aimed at the ATO credit-card stop (30 Jun 2027) — a marker on the who-pays flashpoint, not the licensing Bill. **ACCC AA1000739 A2A submissions closed 16 Nov** (final determination expected Dec 2026). Tapease lens unchanged: Fiserv acquirer + Oxygen issuer → no s766DC facilitation; s766DD tech-enablement + mandatory ePayments Code remain powers only until Bill text is tabled. Next check: Tue 24 Nov 09:00 AEDT; watch **PSB 19 Nov**.
- 2026-11-10 (Tue 09:00 AEDT, PSP weekly — cron 40362e331727): **No material PSP change; monitor trigger was Drupal asset-hash churn (false positive, 5th time).** Treasury page body byte-identical — `dcterms.date` **Thu 12/03/2026**, "Last updated 12 March 2026", T1/T2 wording unchanged; diff touched only `gtag.js?tnhxdl→tnwrg4` plus the theme js cache params. **Live hub `consult.treasury.gov.au` page 1: no PSP/ePayments/standard-setting-body consultation** (open = fraud & financial abuse + Financial Innovation Committee, both 27 Nov; CDR min-baseline auth + FAPI 2.0, 26 Nov; better regulation, 20 Nov); c2026-746108 re-verified in-browser = **Closed 12 Mar–9 Apr 2026, still no consultation-outcomes section**. **Tranche 1 licensing Bill still NOT introduced** (exact-title search nil); ⚠️ **APH was down this run ("website system maintenance")** so the bills-before-Parliament count could not be re-verified (last good 3 Nov: 127 bills, zero payments-titled). Tapease lens unchanged: Fiserv acquirer + Oxygen issuer keeps funds out of Tapease accounts → no s766DC facilitation; s766DD tech-enablement + mandatory ePayments Code remain rule-making powers only until Bill text is tabled. Next check: Tue 17 Nov 09:00 AEDT.

- 2026-11-09 (Mon 09:00 AEDT, **Bank & Payments Weekly** — companion job): 🔴 **rate hike + ANZ FY26 + the pass-through scorecard.** **RBA +25bp to 4.85%** on 3 Nov (effective 4 Nov, fifth 2026 hike, ~18-yr high; next MPB 8–9 Dec). **ANZ FY26 (9 Nov):** cash profit **$7,591m** (+10% ex-significant items), **CET1 11.99% (−4bp) absorbing ANZ Worldline**, final div 83c — merchant consolidation now has a hard edge: **Suncorp merchant facilities close 10:00pm AEST 10 Dec**, new applications only via ANZ Worldline, ~1.2m Suncorp customers move by mid-2027, Suncorp brand retires. 🟡 **RBA designated Prosegur Australia (6 Nov, MR 2026-31)** under the **Cash Distribution Framework Act 2026** — Armaguard subsidiary joins Armaguard (designated 3 Sep); both cash-in-transit operators now regulated. 🟡 **Compayr pass-through scoreboard (19 Oct):** only **7 of 20** tracked card plans cut rates post-1 Oct; **only CBA's interchange-plus plans passed the full 0.5%**; cuts range Stripe −0.05% to Zeller −0.20%; adjudication is the **30 Jan 2027** RBA release. 🟢 **PSB meets 19 Nov** (priorities list due end-2026) — first likely venue for routing/Amex/A2A/agentic direction. **PSP Tranche 1 Bill still unintroduced** (Treasury `dcterms.date` 12 Mar 2026, re-verified today; the APH "Payments System Modernisation Bill **2025**" Bills Digest is the PSRA-amendment Act, not the licensing Bill). **CBA gateway estate mid-migration** — CommWeb/BPOINT/PowerBoard closed to new customers while IPSI is integrated. **Calendar:** ACCC A2A comments **16 Nov** (AA1000739, to 31 Jul 2027; final Dec) · PSB **19 Nov** · AGDIS private-sector entry **30 Nov/1 Dec** · Privacy ADM **10 Dec** · A2A Roundtable **27 Nov** · digital-track end **4 Dec**. **Implication:** no Bill means common access is set in the ACCC/RBA lane through 2027, and the Suncorp→ANZ Worldline migration is a dated merchant re-onboarding cohort (CDD/UBO evidence) inside 30 days. Saved: `~/.hermes/research_outputs/bank-payments-weekly-20261109.md`. Next check: Mon 16 Nov.
- 2026-11-03 (Tue 09:00 AEDT, PSP weekly — cron 40362e331727): **No material PSP change; monitor trigger was Drupal asset-hash churn (false positive, 4th time).** Treasury page body byte-identical — `dcterms.date` **Thu 12/03/2026**, "Last updated **12 March 2026**", T1/T2 wording unchanged; diff touched only `css_4foh9…`/`css_g5s0…`/`js_C8Mhy…` filenames. **Live hub `consult.treasury.gov.au` page 1: no PSP/ePayments/standard-setting-body consultation.** New since the 27 Oct scan: **two CDR draft-standards consultations** (minimum baseline authentication; FAPI 2.0 alignment) closing **26 Nov** — adjacent (A2A/open-banking), not PSP licensing; open items otherwise fraud/financial abuse + Financial Innovation Committee (both 27 Nov), better regulation (20 Nov), bankruptcy (**closes today 3 Nov**); c2026-746108 (Closed 12 Mar–9 Apr) + c2025-700532 (Closed 6 Nov 2025) unchanged. **Tranche 1 licensing Bill still NOT introduced: APH Bills before Parliament = 127 (was 124 on 27 Oct), ZERO payments-titled bills** (full alphabetical sweep, both pages; the only "Payments System Modernisation" Bill on APH is the **2025** PSRA-amendment Act, Royal Assent 19 Sep 2025 — do not read it as the licensing Bill). **beta.treasury.gov.au mirror now returns "Site under maintenance"** — use the live hub + treasury.gov.au body instead. Tapease lens unchanged: Fiserv acquirer + Oxygen issuer keeps funds out of Tapease accounts → no s766DC facilitation; s766DD tech-enablement + mandatory ePayments Code remain rule-making powers only until Bill text is tabled. Next check: Tue 10 Nov 09:00 AEDT.
- 2026-11-03 (Tue 08:00 AEDT, Tranche 2 digest): **No alert-level change — 2 new ASIC MRs (Mon 2 Nov, none AML/T2) + a decision-free remittance page touch.** **AUSTRAC:** enforcement page still "Last updated 30 Oct 2026", *Infringement notices* 2026 still **four** (LSM & Co · Kimberley Jane Black · Watches of Switzerland · Belside) — **no fifth**; Star's $260m still under *Current Court Proceedings*; **remittance page touched to 2 Nov** but newest decision still cancel **20 Jul** / suspend **12 Aug** / refuse-renew **4 May** = page touch, not an action; VASP + s162 19 Oct · guidance 14 Oct · **0 open consultations** · enrol 21 Oct, **62,710 @ 20 Oct** (monthly, next ~20 Nov) · news newest **28 Oct**. **ASIC:** sitemap gen **Mon 2 Nov 02:05Z**, max MR **263→266** — 26-264MR = the **renumbered** Fri-30-Oct Youpla/First Guardian release (the 263 duplicate slug is fixed, not new), **26-265MR 2 Nov REP 844** (super trustees' use of complaints: ~¼ not analysing complaints data regularly, 24/45 found <5 systemic issues, 14 none — IDR, **not AML**), **26-266MR 2 Nov** CDPP discontinued the aiding/abetting charge v Clive Palmer (PLC itself convicted 27 Oct, $10k). **Digital asset:** INFO 225 unchanged (`dcterms.date.modified` 2026-10-26, displayDate 25 Oct) → **no extension, day 34** post-cliff; **CP 392 closes 27 Nov (T-24)**; DAF **9 Apr 2027 (T-157)**, full force 9 Oct 2027. **FATF:** no change since the 30 Oct Plenary; Australia's joint FATF/APG **onsite window is "Nov 2026" — now the current month** (watch, but no date published). Next check: Wed 4 Nov 08:00 AEDT.
- 2026-11-02 (Mon 08:00 AEDT, Tranche 2 digest): **Nothing new → [SILENT].** Monday pre-publish; every source byte-checked. **AUSTRAC:** enforcement page still "Last updated 30 Oct 2026", *Infringement notices* 2026 still **four** (LSM & Co · Kimberley Jane Black t/as Infoproperties · Watches of Switzerland · Belside) — **no fifth name**; Star's $260m penalty still not on the register (still under current proceedings); VASP + s162 19 Oct · remittance 21 Oct · guidance 14 Oct · **0 open consultations** · enrol page 21 Oct, **62,710 @ 20 Oct** (monthly cadence, next refresh ~20 Nov); news listing newest **28 Oct**. **ASIC:** sitemap `Last-Modified Fri 30 Oct 23:05Z` (Sat regen, **no Monday regen**), **max MR still 263** (the duplicate-slug Falcon/Youpla pair), probe 26-264MR = nil → nothing published since 30 Oct; today's releases land ~09:00, after this run. **Digital asset:** INFO 225 unchanged (`dcterms.modified` 2026-10-26, displayDate 25 Oct, body identical) → **no extension, day 33** post-cliff; **CP 392 closes 27 Nov (T-25)**; DAF **9 Apr 2027 (T-158)**, full force 9 Oct 2027. **FATF:** the 30 Oct Plenary outcomes remain the latest at source (VA targeted review due Jun + Oct 2027; grey list 22→18; Mexico/US MERs publish Dec 2026; Australia joint FATF/APG, onsite Nov–Dec 2026, Plenary ~Jun 2027) — no change. Next check: Tue 3 Nov 08:00 AEDT.
- 2026-11-01 (Sun 08:00 AEDT, Tranche 2 digest): **Nothing new → [SILENT].** Weekend; every source byte-identical to the 31 Oct run. **AUSTRAC:** enforcement page still "Last updated 30 Oct 2026" and *Infringement notices* 2026 still the same **four** (LSM & Co · Kimberley Jane Black · Watches of Switzerland · Belside) — **no fifth name**; Star still listed under *Current Court Proceedings* (not moved to concluded); VASP + s162 19 Oct · remittance 21 Oct · guidance 14 Oct · **0 open consultations** · enrol page 21 Oct, **62,710 @ 20 Oct**; news listing newest **28 Oct**. **ASIC:** sitemap generation Fri 30 Oct 23:05Z (no Sat/Sun regen), **max MR still 263** (the duplicate-slug Falcon/Youpla pair) → no cross-run gap; no weekend publishing. **Digital asset:** INFO 225 unchanged (`dcterms.date.modified` 2026-10-26, displayDate 25 Oct) → **no extension, day 32** post-cliff; **CP 392 closes 27 Nov (T-26)**; DAF 9 Apr 2027, full force 9 Oct 2027. **FATF:** post-plenary read confirms the VA targeted review reports **due Jun and Oct 2027** (first fixed milestone dates), grey list **22→18** (four removals, no additions), Vietnam flagged for next steps at Feb 2027; Australia unchanged — joint FATF/APG, onsite possible **Nov–Dec 2026**, Plenary ~**Jun 2027**. **Implication for us:** nothing to action; the next real signal is a fifth named notice or a weekday ASIC release. Next check: Mon 2 Nov 08:00 AEDT.
