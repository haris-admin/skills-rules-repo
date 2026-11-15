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
| 1 | `abr-abn-acn-lookup` | Resolve & verify legal entity, ABN, ACN, and status via ABR (`ABN_LOOKUP_GUID`) | **Active** (ABN-anchored) / **Planned (`34d`)** (name-only & confidence routing) |
| 2 | `web-domain-discovery` | Find and corroborate the merchant's official HTTPS website (`Exa`, `Tavily`, `Brave`, `Serper`, `Perplexity`) | **Active** |
| 3 | `website-scrape-policy-extract` | Scrape returns/refunds/complaints/contact pages (`Firecrawl`/HTTP) and extract literally grounded `policy_fields` | **Active** |
| 4 | `tiered-dispute-contact-routing` | Discover best dispute channel in strict tier order (Disputes → Compliance → Support → General) | **Active** |
| 5 | `owner-decision-maker-enrichment` | Research business profile, owners, and sign-up decision makers for human review | **Proposed (`OpenSpec 68`)** |
| 6 | `acma-compliance-and-confidence-gate` | Run fail-closed ACMA DNCR check (`POST /api/v1/check/contact`) and score confidence | **Active** (`acma_decision`) / **Planned (`34d`)** (`identity_confidence` auto-link) |
| 7 | `handledispute-queue-push` | Claim jobs, maintain lease heartbeat, validate JSON, and push `/complete` or `/fail` | **Active** |

---

## Skill 1: `abr-abn-acn-lookup` (ABR, ABN, ACN & Business Identity)

**When to use:** First step on every claimed job before any web search or scraping.

**Inputs:** `merchant_name`, `abn` (optional in `34d`), `acn` (optional), `candidate_business_email`, `candidate_business_phone`.

**Tools / Credentials:**
- `ABN_LOOKUP_GUID` (SSM `/handledispute/prod/abn_lookup_guid` or worker secret store)
- Australian Business Register JSON/SOAP endpoints (`abr.business.gov.au`)

**Procedure:**
1. **If `abn` is present:** Query `AbnDetails.aspx` with `ABN_LOOKUP_GUID`. Confirm 11-digit ATO Mod-89 validity, `Active` status, legal entity name, ACN (if company), state/postcode, and registered business/trading names.
2. **If `acn` is present (and `abn` missing):** Query `AbnByAcn.aspx` → `AbnDetails.aspx` to resolve the 11-digit ABN and entity details.
3. **If only `merchant_name` is present (`OpenSpec 34d`):**
   - Query `MatchingNames.aspx` (`ABN_LOOKUP_GUID`) for active Australian entities matching `merchant_name`.
   - Cross-check top candidates via `AbnDetails.aspx` and corroborate against `official_domain` footer/terms/privacy pages (Skill 2 + Skill 3) before assigning identity confidence.
4. **Disambiguation rule:** Distinguish legal entity, trading name, parent company, and brand. Never merge two unrelated businesses sharing a generic word.
5. Corroborate the Australian match with merchant-specific evidence, such as ABR trading name and the business's published website,
   address or contact details. Domain suffix, matching name or ABN checksum alone is insufficient. Retain conflicting evidence and
   stop with identity unresolved if no candidate is adequately supported. Do not substitute a foreign same-name business.
6. Verify supplied ABN or ACN against the business name; when absent, search the name to discover and verify candidate identifiers.
   If both ABN and ACN remain missing, require human review. Not every business has an ACN.
7. Estimate identity confidence independently from policy-field confidence. `identity_confidence < 0.90` goes to human review; 0.90
   or above does not itself establish identity or permit outreach. Conflicts, missing identifiers or insufficient corroboration also
   require review. The current API cannot receive identity confidence or candidate evidence: do not put them in other fields.

**Output (internal working record):** `legal_name`, `trading_names[]`, `abn`, `acn`, `abn_status`, `entity_state`, `identity_confidence` (`0.0–1.0`), `identity_evidence[]`.

---

## Skill 2: `web-domain-discovery` (Internet Website Search)

**When to use:** After Skill 1 anchors the entity, to locate the merchant's own official Australian HTTPS website.

**Inputs:** `merchant_name`, `legal_name`, `abn`, `acn`, `entity_state`.

**Tools / Cascade (run in priority order of configured availability):**
1. **Exa** (`EXA_API_KEY`) — semantic/company search for official corporate domain and Australian storefront.
2. **Tavily** (`TAVILY_API_KEY`) — targeted queries for `"<merchant_name>"`, `"ABN <11-digit>"`, `returns`, `refunds`, `complaints`, `contact us`.
3. **Brave / Serper** (`BRAVE_API_KEY` / `SERPER_API_KEY`) — Google/web SERP verification that the candidate domain is the official trading presence and surfaces footer ABN text.
4. **Perplexity** (`PERPLEXITY_API_KEY`) — citation-only cross-check for holding-company → trading-brand mappings (e.g., trading name to parent ABN). Never treat AI summaries as final proof; always inspect the underlying site.

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

## Recommendations for Organizing Hermes Skills

1. **Keep these two files as your version-controlled source of truth in Git:**
   - **Prompt:** [`docs/runbooks/hermes-agent-instructions.md`](hermes-agent-instructions.md)
   - **Skills:** [`docs/runbooks/hermes-agent-skills.md`](hermes-agent-skills.md)
2. **Copy both into the Hermes agent's folder** when deploying or updating the worker. Any change goes through a PR/commit in this repo first so you always have an exact audit trail of what Hermes was given.
3. **If your Hermes runtime requires one folder per skill (`<skill-name>/SKILL.md`):** Keep `docs/runbooks/hermes-agent-skills.md` as the master version-controlled spec and split Skills 1–7 into individual `SKILL.md` directories only at export/packaging time (so you don't maintain 7 diverging copies).
4. **OpenSpec status:** `34d` proposes name-only jobs and confidence routing but remains draft. `68` proposes Skill 5 storage for
   business owners and decision makers. Neither is an active contract; do not assume either resolves the correct Oak and Ash identity.
