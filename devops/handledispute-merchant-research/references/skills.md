# Hermes Agent Skills: HandleDispute Merchant Enrichment & Identity Resolution

Version-controlled modular skills library for the HandleDispute Hermes worker.
Pair this file with the canonical worker prompt: [`docs/runbooks/hermes-agent-instructions.md`](hermes-agent-instructions.md).

> **Contract boundary:** Skills marked **Active** map directly to the live `/api/v1/agent/merchant-enrichment/*` contract (`backend/app/api/v1/hermes_enrichment.py`). Skills or fields marked **Planned (`OpenSpec 34d`)** or **Proposed (`OpenSpec 68`)** must not be added to `/complete` payloads until the corresponding backend schema and API changes are deployed.

**Scope and setting:** Use Australian-first research. For the initial stage recommend only a registered Australian business, with
registration checked against ABR or an appropriate Australian register and merchant-specific identity independently corroborated.
An inactive or uncertain registration, unavailable register or multiple plausible matches goes to human review. A similar overseas
business is a possible name collision, not proof of identity or that an Australian ABN does not exist. `.com.au` and `.au` are useful
indicators, and `.com` can also belong to an Australian business; no domain suffix alone proves registration or identity. Respect the
existing API and its permitted job fields; name-only queueing is still planned. `HERMES_ACMA_CHECK_ENABLED` is a Hermes-only boolean,
initially `false`, configured by the owner. Missing or invalid means false. When false, do not call ACMA; send the required fields
`acma_decision: "UNKNOWN"` and `acma_evidence_reference: "not-checked"`. When true, use only a separately approved, configured check;
unavailable or inconclusive checks remain unknown. Never fabricate `ALLOWED`. This flag does not change the backend, where unknown
does not make the merchant action-ready for automated outreach.

---

## Skill Index & Recommended Execution Order

| # | Skill ID | Purpose | Status |
|---|---|---|---|
| 1 | `abr-abn-acn-lookup` | Resolve & verify legal entity, ABN, ACN, and status via ABR (`ABN_LOOKUP_GUID`) | **Active** (ABN-anchored and name-only lookup as a read-only report) / **Planned (`34d`)** (queueing and saving name-only & confidence routing) |
| 2 | `web-domain-discovery` | Find and corroborate the merchant's official HTTPS website (`Exa`, `Tavily`, `Brave`, `Serper`) | **Active** |
| 3 | `website-scrape-policy-extract` | Scrape returns/refunds/complaints/contact pages (`Firecrawl`/HTTP) and extract literally grounded `policy_fields` | **Active** |
| 4 | `tiered-dispute-contact-routing` | Discover best dispute channel in strict tier order (Disputes → Compliance → Support → General) | **Active** |
| 5 | `owner-decision-maker-enrichment` | Research business profile, owners, and sign-up decision makers for human review | **Proposed (`OpenSpec 68`)** |
| 6 | `acma-compliance-and-confidence-gate` | Run fail-closed ACMA DNCR check (`POST /api/v1/check/contact`) and score confidence | **Active** (`acma_decision`) / **Planned (`34d`)** (`identity_confidence` auto-link) |
| 7 | `handledispute-queue-push` | Claim jobs, maintain lease heartbeat, validate JSON, and push `/complete` or `/fail` | **Active** |
| 8 | `identity-research-job` | Claim an identity research job (business name plus unverified customer hints), research it with skill 1 to 3, and push candidates with `identity_confidence` to `/agent/identity-research/{job_id}/complete` or `/fail`. Results are recorded for human review and never link a merchant | **Live since release 0.270.0 (16 Nov 2026)** (live since release 0.270.0, 16 Nov 2026; its lease is 120 minutes by default (setting `IDENTITY_RESEARCH_LEASE_MINUTES`, spec 85 D73; it was 30 until that change reaches production) with no heartbeat route, unlike the 10 minute enrichment lease). Few-shot examples and fixed JSON for every outcome, including a franchise case and a failed ABN check, are in `hermes-agent-instructions.md`, section "Worked examples" |
| 9 | `research-report-submission` | Read the claim whole, validate payload rules, submit the full structured report (`/reports`) before `/complete` or `/fail`, with contacts, franchise entities and every candidate | **Active** (OpenSpec 85, 84c) |
| 10 | `research-completeness-check` | Check every candidate across identity, registration, leadership, dispute contact and sign-up contact before finishing; go back for anything missing | **Active** (OpenSpec 84c) |

---

## Skill 1: `abr-abn-acn-lookup` (ABR, ABN, ACN & Business Identity)

**When to use:** First step on every claimed job before any web search or scraping.

**Inputs:** `merchant_name`, `abn` (optional in `34d`), `acn` (optional), `candidate_business_email`, `candidate_business_phone`.

**Tools / Credentials:**
- `ABN_LOOKUP_GUID` (AWS Secrets Manager `handledispute/secrets/prod`, key `ABN_LOOKUP_GUID`; keep a copy in the worker secret store; the SSM copy was removed on 16 Nov 2026)
- Australian Business Register JSON/SOAP endpoints (`abr.business.gov.au`)

**Procedure:**
1. **If `abn` is present:** Query `AbnDetails.aspx` with `ABN_LOOKUP_GUID`. Confirm 11-digit ATO Mod-89 validity, `Active` status, legal entity name, ACN (if company), state/postcode, and registered business/trading names.
2. **If `acn` is present (and `abn` missing):** Query `AbnByAcn.aspx` → `AbnDetails.aspx` to resolve the 11-digit ABN and entity details.
3. **If only `merchant_name` (or a trading or business name) is present (works today as a read-only lookup; queueing and saving the result need `OpenSpec 34d`):** follow `hermes-agent-instructions.md`, section "Locating an Australian business from its name", exactly. In short:
   - Build the name variants (as submitted, normalised, with and without company suffixes, `&`/`and`, `The`, apostrophes, `T/A` both sides, first two or three words, product or location word removed, joined or spaced forms, domain read as words).
   - Search ABR `MatchingNames` with `ABN_LOOKUP_GUID` (entity, business and trading name types) and the public `abr.business.gov.au` name search for each variant, most specific first; use ASIC registers for a company or business name that points to the same ABN. Keep every Australian entity as a candidate whatever its status (OpenSpec 84a); record the exact status, and record an overseas or unrelated entry as a candidate that is ruled out with its reason.
   - Verify each candidate through `AbnDetails` (and `AbnByAcn` for an ACN): checksum, status, legal name, ACN, state and postcode, every registered business and trading name.
   - Corroborate with at least two independent pieces of evidence (website footer ABN or legal name, Australian address or phone matching ABR, a second source naming the same ABN) via Skills 2 and 3.
   - Score `identity_confidence` with the published points and penalties, then choose the outcome. In an identity research job report one of `MATCHED`, `AMBIGUOUS`, `NOT_FOUND` or `OVERSEAS_ONLY` (a register outage is reported through the fail route, not as an outcome). In a read-only report the owner also sees `AUSTRALIAN_MATCH`, `NO_AUSTRALIAN_MATCH` and `REGISTER_UNAVAILABLE`.
4. **Disambiguation rule:** Distinguish legal entity, trading name, parent company, and brand. Never merge two unrelated businesses sharing a generic word.
5. Corroborate the Australian match with merchant-specific evidence, such as ABR trading name and the business's published website,
   address or contact details. Domain suffix, matching name or ABN checksum alone is insufficient. Retain conflicting evidence and
   stop with identity unresolved if no candidate is adequately supported. Do not substitute a foreign same-name business.
6. Verify supplied ABN or ACN against the business name; when absent, search the name to discover and verify candidate identifiers.
   If both ABN and ACN remain missing, require human review. Not every business has an ACN.
7. Estimate identity confidence independently from policy-field confidence. `identity_confidence < 0.90` goes to human review; 0.90
   or above does not itself establish identity or permit outreach. Conflicts, missing identifiers or insufficient corroboration also
   require review. Send identity confidence and candidate evidence only through the identity research routes (skill 8); the enrichment routes cannot receive them, so never put them in other fields.

**Output when there is no job (case with no merchant row):** send the owner an *identity lookup report* (format in `hermes-agent-instructions.md`, section "Locating an Australian business from its name"): candidates with ABN, ACN, status, evidence for and against, `identity_confidence`, and a recommendation of `AUSTRALIAN_MATCH`, `AMBIGUOUS`, `NO_AUSTRALIAN_MATCH` or `OVERSEAS_ONLY`. Do not write to the API or contact anyone.

**Output (internal working record):** `legal_name`, `trading_names[]`, `abn`, `acn`, `abn_status`, `entity_state`, `identity_confidence` (`0.0–1.0`), `identity_evidence[]`.

---

## Skill 2: `web-domain-discovery` (Internet Website Search)

**When to use:** After Skill 1 anchors the entity, to locate the merchant's own official Australian HTTPS website.

**Inputs:** `merchant_name`, `legal_name`, `abn`, `acn`, `entity_state`.

**Tools / Cascade (run in priority order of configured availability):**
1. **Exa** (`EXA_API_KEY`) — semantic/company search for official corporate domain and Australian storefront.
2. **Tavily** (`TAVILY_API_KEY`) — targeted queries for `"<merchant_name>"`, `"ABN <11-digit>"`, `returns`, `refunds`, `complaints`, `contact us`.
3. **Brave / Serper** (`BRAVE_API_KEY` / `SERPER_API_KEY`) — Google/web SERP verification that the candidate domain is the official trading presence and surfaces footer ABN text.

**Verification & Rejection Rules:**
- `official_domain` must serve **HTTPS** directly on the business's own domain (e.g., `example.com.au`).
- **Reject** social media profiles (Facebook, Instagram, LinkedIn), business directories (Yellow Pages, ABN Lookup pages, Crunchbase), coupon/review aggregators, and URL shorteners.
- If no official HTTPS domain can be verified, stop and fail the job with `error_code=no_website_found` (or `UNVERIFIABLE_MERCHANT_IDENTITY`).

---

## Skill 3: `website-scrape-policy-extract` (Scraping & Grounded Policy Extraction)

**When to use:** Once `official_domain` is verified in Skill 2.

**Tools:** `Firecrawl` (`FIRECRAWL_API_KEY`) or clean public HTTP / headless browser (no login walls, no paywall bypass).

**Target Pages on `official_domain`:**
- Footer & About Us / Legal / Terms & Conditions / Privacy Policy (to corroborate ABN/ACN on-site)
- Returns / Refunds / Shipping & Warranty policy page
- Complaints / Disputes / Chargebacks / Escalations page
- Contact Us / Help Centre

**Procedure & Grounding Rules:**
1. Extract plain text (strip all HTML tags) into `raw_policy_text` (**1 to 10,000 characters**).
2. Record exact `https` URLs on `official_domain` (or a subdomain):
   - `source_url` (exact page read for `raw_policy_text`)
   - `return_policy_url` (`null` if not published)
   - `chargeback_resolution_url` (complaints/disputes/chargebacks page, else `null`)
   - `observed_at` (ISO 8601 UTC timestamp)
3. Populate `policy_fields` **only when literally stated in `raw_policy_text`** (omit key otherwise):
   - `return_window_days`: integer `0..365` **only** if `raw_policy_text` literally contains `<N> day` (e.g., `30 days`).
   - `refund_method`: `original_payment_method`, `store_credit`, or `exchange` **only** if `raw_policy_text` literally contains that phrase with spaces (`original payment method`, `store credit`, or `exchange`).
   - `proof_of_purchase_required`: boolean (`true` **only** if `raw_policy_text` literally contains `proof of purchase`).
4. Send `llm_assessment: {}`, `llm_commentary: {}`, `llm_rule_analysis: {}` (the HandleDispute backend runs its own bounded assessment).

---

## Skill 4: `tiered-dispute-contact-routing` (Tiered Contact Hierarchy)

**When to use:** During Skill 3 page inspection, to select the best published dispute contact channel.

**Strict Priority Hierarchy (search all tiers; pick highest verified tier):**
1. **Tier 1 — Dedicated Dispute / Chargeback Management:**
   - Look for: `disputes@`, `chargebacks@`, `fraud@`, `payments@`, `settlements@`, or a dedicated dispute/chargeback escalation portal.
2. **Tier 2 — Formal Escalation / Compliance / Legal:**
   - If Tier 1 is absent, look for: `complaints@`, `compliance@`, `legal@`, `privacy@`, `escalations@`.
3. **Tier 3 — Customer Support / Returns Desk:**
   - If Tier 1 & 2 are absent, look for: `returns@`, `customercare@`, `support@`, `help@`, `service@`.
4. **Tier 4 — General Published Front Door:**
   - If Tiers 1–3 are absent, use: `contact@`, `hello@`, `info@`, a published contact form URL, or `candidate_business_email` if confirmed on `official_domain`.

**Hygiene & Preservation Rules:**
- Only submit addresses published **verbatim** on `official_domain` (or confirmed `candidate_business_email`). Never guess `disputes@<domain>` if unpublished.
- Reject asset/template/tracker false positives (`*@2x.png`, `sentry.io`, `wixpress.com`, `example.com`).
- Preserve channel type: a web form URL or phone number is not an email address; submit `contact_email: null` if only a form/phone exists.
- Normalize Australian phone numbers into `contact_phone` (`null` if unpublished).
- Retain discovered alternatives and note which tiers were checked vs absent in your internal run summary.
- **Identity research jobs (version 2):** the identity `/complete` body has no contact field, so the dispute contact you find goes into the report (skill 9.5) as a `contacts` entry with purpose `DISPUTE`, the candidate it belongs to, the tier in `limitations`, and the sources. The research is not finished until a dispute contact is recorded or the area is marked `NO_EVIDENCE_FOUND` with the tiers you searched.

---

## Skill 5: `owner-decision-maker-enrichment` (Business Owners & Decision Makers) — *Proposed (`OpenSpec 68`)*

**Status:** **Proposed (`OpenSpec 68` draft)** — Keep **completely separate** from Dispute Contact Routing (Skill 4), and **do not** add these fields to `/complete` until the OpenSpec 68 storage/API contract is deployed.

**Purpose:** Build an evidence-based profile of the business and potential B2B sign-up decision makers for human sales/operations review.

**What to collect (when enabled):**
1. **Business Profile:** Legal name, trading name, confirmed ABN/status, official domain, industry, physical locations/branches, parent/franchise relationship, core products/services.
2. **Decision-Maker Candidates:** Owners, founders, directors, and senior managers in operations, customer service, e-commerce, payments, finance, risk, compliance, or legal:
   - `full_name`, `title`, `organisation`, `relevance_to_signup`, `published_work_contact` (if verbatim published), `source_url`, `observed_at`, `confidence`, `reason`.

**Strict Guardrails:**
- **Never** log in to LinkedIn, scrape LinkedIn profiles, or bypass paywalls/auth. Public search snippets mentioning LinkedIn are unverified leads only and must be corroborated elsewhere.
- Distinguish **verified fact** from **inference** (a founder or ASIC director is not automatically the current operational owner; mark ownership `unknown` when not established).
- Never infer/guess personal or work email patterns; never contact any person. All findings enter as **proposed** for human review.

---

## Skill 6: `acma-compliance-and-confidence-gate` (ACMA DNCR & Confidence Routing)

**When to use:** Before submitting `/complete`.

**ACMA check (conditional):**
- Follow `HERMES_ACMA_CHECK_ENABLED` above. Initially false: skip ACMA and submit `acma_decision: "UNKNOWN"` and
  `acma_evidence_reference: "not-checked"` to satisfy the current API. Do not mark the result allowed or bypass the backend.
- If enabled later, use only the approved, configured check. If it is unavailable or inconclusive, report unknown. Record allowed only
  when supported by an actual permitted check and evidence; this setting is not an authorisation to contact the merchant.

**Confidence Scoring & Routing:**
- Set `field_confidence` (`0.0–1.0`) honestly reflecting match quality across identity, domain, contact, and policy text.
- **Planned (`OpenSpec 34d`):** `identity_confidence < 0.90` and the other identity gaps above require human review. The routing,
  candidate storage and any automatic linking are not built and require an approved design. Do not treat the score as proof.

---

## Skill 7: `handledispute-queue-push` (Claim, Heartbeat & Push Back)

**When to use:** Wraps Skills 1–6 into the HandleDispute worker loop.

1. **Startup check:** Confirm `HANDLEDISPUTE_AGENT_KEY` is set and base URL is `https://api.handledispute.com.au`. Refuse to start otherwise.
2. **Claim:** Every 60s, generate `worker_run_id` (8–64 chars) and `POST /api/v1/agent/merchant-enrichment/claim` with `X-Hermes-Agent-Key`.
   - `204 No Content` → log `Hermes: job queue is empty; sleeping until next poll` and sleep 60s.
   - `401` → stop and alert operator.
3. **Lease management:** Hold one job at a time (10-minute lease). Call `POST /api/v1/agent/merchant-enrichment/{job_id}/heartbeat?lease_token=<token>` before expiry if Skills 1–6 take longer.
4. **Push result back:**
   - **Success:** `POST /api/v1/agent/merchant-enrichment/{job_id}/complete` with validated JSON (`lease_token`, `merchant_name`, `official_domain`, `contact_email`, `contact_phone`, `return_policy_url`, `chargeback_resolution_url`, `source_url`, `observed_at`, `field_confidence`, `raw_policy_text`, `policy_fields`, `llm_assessment: {}`, `llm_commentary: {}`, `llm_rule_analysis: {}`, `acma_decision`, `acma_evidence_reference`).
   - **Failure:** `POST /api/v1/agent/merchant-enrichment/{job_id}/fail?lease_token=<token>&error_code=<short_code>`.

`MERCHANT_EMAIL_REDIRECT_ENABLED` is a HandleDispute backend setting, not a Hermes setting. When enabled, it routes merchant email to
configured `MERCHANT_EMAIL_REDIRECT_TO` recipients. Haris identifies `haris@handledispute.com.au` as the intended test recipient; the
live setting and recipient have not been independently verified. Hermes never sends the email or changes the redirect.

---

## Skill 9: `research-report-submission` (Full report, payload rules, claim handling)

**Status:** Active for the report routes of OpenSpec 85 (`/reports`). Version 2 of the prompt (OpenSpec 84c).

**When to use:** On every identity research job and every enrichment job, after the research and before `/complete` or `/fail`. The `/complete` body is a short summary for the existing flow. **The report is where the full findings go**: every candidate (not only five), every source and search, the dispute and sign-up contacts, the franchise and lookalike entities, the limitations and the whole narrative. Do not squeeze these into the 2000 character `notes`.

### 9.1 Read the claim whole

1. Save the claim response to a file (for example `claim.json`) and read that file by parsing it. Never rely on what the terminal printed: a capture can be cut off, and an earlier run missed `postcode` and `receipt_clues` that way.
2. Check every key of `hints`: `suburb`, `state`, `postcode`, `website`, `phone`, `abn`, `abn_check`, `phone_check`, `receipt_clues`. In `receipt_clues` read `truncated` and `clue_count`. `truncated: true` means the server stopped at its cap of 20 contacts in a group; say so under limitations.
3. Treat every hint as a lead. A `FAILED` check is not evidence for or against a candidate.

### 9.2 Payload rules (check locally, before sending)

The API rejects with `422` a body that breaks any of these. Check all of them before you send, so a rejected call is never how you learn a rule.

| Field | Rule |
|---|---|
| `candidates[].legal_name` | Never null: a string of 1 to 255 characters. If the legal name is unknown, use the registered name you have and say so in the evidence note. |
| `candidates[].abn` | Null or 11 digits that pass the ABN checksum (ATO modulus 89). |
| `candidates[].acn` | Exactly 9 digits, or null. Never an empty string, never spaces or letters. |
| `candidates[].candidate_confidence`, `identity_confidence` | A number from 0 to 1. |
| `candidates` | At most 5 candidates in `/complete` (five candidates). The full list goes in the report. |
| `candidates[].trading_names` | At most 10, each 1 to 255 characters. |
| `candidates[].evidence` | At most 10 items; each `source_url` is `http` or `https`; `observed_at` is a UTC timestamp. |
| `notes` | At most 2000 characters. No secrets, no personal data. |
| `recommended_abn` | Null unless exactly one candidate is clearly best; same checksum rule. |
| `/fail` `error_code` | Lower case letters, digits and underscore, 1 to 64 characters, for example `source_unavailable` or `time_budget`. |

### 9.3 The ABR status trap

`IsCurrent` in an ABR name search describes the name record, not the ABN. A franchise can have many entities with the same trading name and different statuses. Read each ABN's status from `AbnDetails`. Record cancelled, deregistered and expired candidates in the report with the exact status text and keep them as candidates.

### 9.4 Franchise and related entities

When the same trading name is carried by several entities (franchisees, a licensee, a brand owner, a parent), put each one in the report as its own candidate, say which entity most likely ran the transaction and why, and name the others as alternatives. If the receipt ABN or a hint settles it, say that is what settled it. A store-level entity is a real possibility when a receipt ABN could have been misread.

### 9.5 Contacts

For an identity job the `/complete` body has no contact field. Put every dispute contact and sign-up contact you find in the report under `contacts`, with the `candidate_id` it belongs to, `purpose` `DISPUTE` or `SIGNUP`, the `channel` (`EMAIL`, `PHONE`, `WEB_FORM`, `POSTAL` or `OTHER`), the `value` exactly as published, `source_ids`, `observed_at` and `limitations`. Use the tier order of skill 4. Never guess an address that is not published. Contacts are proposed for human review; do not contact anyone.

### 9.6 Submit

1. `POST /api/v1/agent/identity-research/{job_id}/reports` (enrichment: `/api/v1/agent/merchant-enrichment/{job_id}/reports`) with `{"lease_token": "<from claim>", "idempotency_key": "<16 to 128 characters, new for this run, reused only to repeat the same body>", "report": <the report>}` and the `X-Hermes-Agent-Key` header. The report has `schema_version` `"1"` and `research_mode` `"claimed_job"`. `201` or `200` means stored. Read `readiness`: `STORED_AWAITING_ATTACHMENTS` means upload the files you declared first.
2. Upload each declared attachment (multipart, route in the contract), only public pages or documents you fetched, never customer files.
3. Then `/complete` (or `/fail` for a source outage or a lost lease). Order: report, attachments, completion.
4. Errors: `422 REPORT_INVALID` carries `findings` with the rule and field (never your text): fix and resubmit with a new `idempotency_key`. `409 LEASE_INVALID`: stop, do not retry, tell the owner. `503 STORAGE_UNAVAILABLE`: retry up to three times 30 seconds apart and then still call `/complete` before the lease ends so the job is not lost, with `notes` saying "report not stored: storage unavailable". The backend raises a missing-report item for a person. Never claim the report was stored unless you got `201` or `200`.

### 9.7 Worked example (invented business, validated by a test against the backend validator)

```json report
{
  "schema_version": "1",
  "run_id": "run-0001-example",
  "research_mode": "claimed_job",
  "submitted_name": "Sample Footwear",
  "available_clues": ["business name", "receipt ABN hint", "postcode"],
  "missing_clues": ["store address"],
  "started_at": "2026-11-18T01:00:00Z",
  "completed_at": "2026-11-18T01:40:00Z",
  "outcome": "AUSTRALIAN_CANDIDATE",
  "summary": "Sample Footwear Pty Ltd matches the receipt ABN. Franchisee entities share the trading name, so a store-level entity is possible.",
  "recommended_candidate": {"candidate_id": "cand-head", "source_ids": ["src-abr"]},
  "coverage_assessments": [
    {"candidate_id": "cand-head", "area": "identity_and_case_link", "state": "WELL_SUPPORTED", "source_ids": ["src-abr", "src-site"], "missing": []},
    {"candidate_id": "cand-head", "area": "registration", "state": "WELL_SUPPORTED", "source_ids": ["src-abr"], "missing": []},
    {"candidate_id": "cand-head", "area": "leadership", "state": "NOT_CHECKED", "source_ids": [], "missing": ["director source not searched"]},
    {"candidate_id": "cand-head", "area": "dispute_contact", "state": "PARTIAL", "source_ids": ["src-site"], "missing": ["no dedicated disputes address published"]},
    {"candidate_id": "cand-head", "area": "signup_contact", "state": "NO_EVIDENCE_FOUND", "source_ids": ["src-site"], "missing": ["decision maker"]},
    {"candidate_id": "cand-fran", "area": "identity_and_case_link", "state": "PARTIAL", "source_ids": ["src-abr"], "missing": ["store location"]},
    {"candidate_id": "cand-fran", "area": "registration", "state": "WELL_SUPPORTED", "source_ids": ["src-abr"], "missing": []},
    {"candidate_id": "cand-fran", "area": "leadership", "state": "NOT_CHECKED", "source_ids": [], "missing": ["director source not searched"]},
    {"candidate_id": "cand-fran", "area": "dispute_contact", "state": "NOT_CHECKED", "source_ids": [], "missing": ["contact research"]},
    {"candidate_id": "cand-fran", "area": "signup_contact", "state": "NOT_CHECKED", "source_ids": [], "missing": ["contact research"]}
  ],
  "sources": [
    {"source_id": "src-abr", "name": "ABR AbnDetails", "source_type": "registry", "url": "https://abr.business.gov.au/", "observed_at": "2026-11-18T01:10:00Z", "status": "SUCCESS"},
    {"source_id": "src-site", "name": "Business website terms page", "source_type": "website", "url": "https://example.com.au/terms", "observed_at": "2026-11-18T01:20:00Z", "status": "SUCCESS"}
  ],
  "searches": [
    {"search_id": "srch-1", "query": "Sample Footwear", "source_id": "src-abr", "observed_at": "2026-11-18T01:05:00Z", "status": "SUCCESS", "coverage_note": "Name search found the head entity and franchisee entities."}
  ],
  "candidates": [
    {"candidate_id": "cand-head", "legal_name": "Sample Footwear Pty Ltd", "trading_names": ["Sample Footwear"], "identifiers": [{"type": "ABN", "value": "51824753556", "jurisdiction": "AU", "source_id": "src-abr"}], "geography": "AUSTRALIA", "registrations": [{"kind": "ABN", "identifier_value": "51824753556", "status": "ACTIVE", "status_text": "Active per AbnDetails", "source_id": "src-abr"}], "case_identity_assessment": "SUPPORTED", "disposition": "INVESTIGATE", "reasons_for": ["Receipt ABN hint matches this ABN."], "reasons_against": [], "source_ids": ["src-abr", "src-site"]},
    {"candidate_id": "cand-fran", "legal_name": "Franchisee Example Pty Ltd", "trading_names": ["Sample Footwear"], "identifiers": [{"type": "ABN", "value": "53010000350", "jurisdiction": "AU", "source_id": "src-abr"}], "geography": "AUSTRALIA", "registrations": [{"kind": "ABN", "identifier_value": "53010000350", "status": "CANCELLED", "status_text": "Cancelled per AbnDetails", "source_id": "src-abr"}], "case_identity_assessment": "UNDETERMINED", "disposition": "UNRESOLVED", "reasons_for": ["Shares the trading name as a franchisee."], "reasons_against": ["Receipt ABN does not match this ABN."], "source_ids": ["src-abr"]}
  ],
  "leadership": [],
  "contacts": [
    {"contact_id": "con-1", "candidate_id": "cand-head", "purpose": "DISPUTE", "role": "customer support", "channel": "EMAIL", "value": "support@example.com.au", "source_ids": ["src-site"], "observed_at": "2026-11-18T01:20:00Z", "limitations": ["Tier 3 support address. No dedicated disputes address is published."]}
  ],
  "other_findings": [],
  "limitations": ["Directors were not searched in this run.", "The store address was not available."],
  "open_questions": ["Which store issued the receipt?"],
  "recommended_next_actions": ["A person should confirm the receipt ABN against the head entity."],
  "full_narrative": "Searched the ABR name register and AbnDetails for the submitted name. The receipt ABN hint matched the head entity. Franchisee entities share the trading name and one is cancelled; both are kept as candidates. The business website lists a customer support address only.",
  "declared_attachments": []
}
```

---

## Skill 10: `research-completeness-check` (Check everything before you finish)

**When to use:** After the research and before the report is submitted. A run is not finished until this check is done. This skill exists because earlier runs stopped after identity and left leadership, dispute contact and sign-up contact empty without saying so.

**Procedure:**

1. List every candidate you investigated. Keep them all: a cancelled, deregistered, expired, overseas or ruled-out candidate is kept in the list with the exact status and the reason (never dropped for status alone).
2. For each candidate set a state for each of the five areas: identity and case link, registration, leadership, dispute contact, sign-up contact. The states are `WELL_SUPPORTED`, `PARTIAL`, `CONFLICTING`, `NO_EVIDENCE_FOUND` (you searched and found nothing), `NOT_CHECKED` (you did not search) and `SOURCE_UNAVAILABLE` (a source failed). `NOT_CHECKED` and `SOURCE_UNAVAILABLE` are not negative findings.
3. **Missing work rule.** Any area that is empty, or `NOT_CHECKED` without a reason, is work you have not done. Go back and do it now with skills 1 to 6. Only when you cannot (no source, no time, a source down) set the honest state, name what is missing, and put it under limitations and open questions.
4. Check the franchise and related entities: lookalikes, licensees, brand owner, parent. Each is a candidate or a stated alternative.
5. Check the policy pages and the dispute contact in tier order (skill 4): disputes or chargebacks, then complaints or compliance, then support, then the general front door. Record which tiers you checked.
6. Check the claim was read whole (skill 9.1) and that every hint was used or marked unused with a reason.
7. Check the payload rules (skill 9.2) on `/complete` and the report.
8. Check no secret, token or customer data is in any note, query or report.
9. Check the summary does not claim more than the evidence: a strong identity does not verify a contact, and an agent opinion is not a system flag or a human decision.

**Output:** the completed coverage list in the report, with limitations and open questions naming everything not done. If you could not finish a required area and had time left, you were not finished.

---

## Recommendations for Organizing Hermes Skills

1. **Keep these two files as your version-controlled source of truth in Git:**
   - **Prompt:** [`docs/runbooks/hermes-agent-instructions.md`](hermes-agent-instructions.md)
   - **Skills:** [`docs/runbooks/hermes-agent-skills.md`](hermes-agent-skills.md)
2. **Copy both into the Hermes agent's folder** when deploying or updating the worker. Any change goes through a PR/commit in this repo first so you always have an exact audit trail of what Hermes was given.
3. **If your Hermes runtime requires one folder per skill (`<skill-name>/SKILL.md`):** Keep `docs/runbooks/hermes-agent-skills.md` as the master version-controlled spec and split Skills 1–7 into individual `SKILL.md` directories only at export/packaging time (so you don't maintain 7 diverging copies).
4. **OpenSpec status:** `34d` proposes name-only jobs and confidence routing but remains draft. `68` proposes Skill 5 storage for
   business owners and decision makers. Neither is an active contract; do not assume either resolves the correct Oak and Ash identity.
