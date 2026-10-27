---
name: idealab-daily-assessment
description: Use when running the daily IdeaLab idea assessment.
version: 1.0.0
author: Pluto
license: MIT
allowed-tools: [read_file, write_file, patch, terminal, execute_code, skill_manage]
metadata:
  hermes:
    tags: [idealab, research, briefing, amlhive]
    related_skills: [pluto-morning-briefing, pluto-amlhive-operating-contract]
---

# IdeaLab daily assessment

## When to Use

- The daily `IdeaLab daily assessment` cron runs (05:30 Australia/Sydney) and must feed the 06:00 briefing.
- Any manual refresh of `idealab-assessment-*.md` / `idealab-brief-*.md` or the `<!-- IDEALAB_START -->` block.

Produces the `### 💡 IdeaLab Assessment — YYYY-MM-DD` block that sits inside Pluto's 06:00 Australia/Sydney briefing. Research only: no outreach, spend, publishing or product changes.

## 1. Collect (bounded, never evade limits)

```bash
~/.hermes/venv/bin/python ~/.hermes/scripts/idealab_collect_ideas.py \
  --output-dir ~/.hermes/research_outputs/idealab \
  --data-dir ~/.hermes/data/idealab --lens all
```

- `--details ID1,ID2,...` fetches up to **10** full briefs (numeric IDs only); `--pages {1,2}`.
- The response carries `allowance`: briefs 10/day, searches 50/day, `resetsAt` ≈ 22:17 Sydney. Read it before fetching briefs.
- **The brief cap is per visitor session, not per day.** `allowance.briefs.used` equals the cumulative `opened-briefs` calls in `data/idealab/idealab-requests.jsonl`, and it does **not** reset when `resetsAt` rolls the search window over (verified 25 Oct: counter stayed 10/10 at 05:31 with searches back at 1/50). Once 10 unique briefs are open, **no new brief is obtainable in that session** — report the cap and escalate the access decision to Haris (accept summary-only / named account / retire the brief stage). Do not reset cookies or change identity to regain it.
- To read the allowance without writing files, import the module in a scratch script and make one `limit:5` `/api/idea-search` call through `Client`, then print `client.allowance`. There is no `--allowance` flag.
- HTTP 401/403/429 is **terminal for the run** — report the exact refusal and coverage. Never reset cookies, rotate identity, or retry around a quota.
- The site is an undocumented visitor interface: fail visibly, never reconstruct data from previews or general news as if it were the search result.

## 2. Coverage is a sample — the register is the truth

- **Identical queries return different rows between passes.** One page per lens gives ~100 rows and is *not* stable; use `--pages 2` when you need stable daily coverage.
- A record absent from a later result set is a **ranking artefact, not a withdrawal**. `idea-register.json` (all IDs ever seen, with `content_hash`, `first_seen`, `last_surfaced_*`) is the source of truth; `candidates-YYYY-MM-DD.json` is only this pass's sample.
- Full briefs expose `record.createdAt` / `updatedAt` and `idea.updatedAt`. **Keep the field meaning**: say "record created 9 September", never "updated" when the value is `createdAt`.
- `details-YYYY-MM-DD.json` caches briefs per day; reuse them at their original `checked_at` rather than re-fetching.
- First seen ≠ newly published. The collector has no publication date; say "first seen today" and never imply a publication date.

## 3. Assess

Priority order: Buy Australian AI → AMLHive → pre-dispute → TAPEase/POS. Read titles *and* thesis from every lens, group near-duplicates, then check the shortlist (`data/idealab/shortlist.json`, max 10, `history[]` holds rejects) and `last_surfaced_hash` before re-surfacing anything.

Weights: product/customer fit 25, AU demand evidence 20, pilot in 2–4 weeks 20, revenue/distribution 15, differentiation 10, delivery/regulatory feasibility 10. Report **demand confidence separately**; never derive it from keyword counts, and never present IdeaLab market sizes, capital needs or timing as validated Australian demand.

Known overlaps to reject as "new": #1654719 (AMLHive core), #1035601 (ownership engine/C425), #979788 (C523), #813498 (C496 HiveCoach). Check `openspec/changes/` for real status (`partial`/`proposal`/`implemented`) and treat docs as planned/local evidence, not live production.

## 3a. Measure the lens geography every run

Compute, over the union of all `candidates-*.json` files (dedupe by ID, keep lens tags), how many records in each lens mention Australia in title+thesis. Report the rate per lens in the assessment. Rationale: the priority lens can be **structurally mislabelled**. On 27 Oct the `buy_au_ai` lens was **0/81 unique records over six days** while `amlhive` was 4/65 and the rest ~1.5–2%. That is a query-weighting artefact, not an empty corpus.

- Test it with **1–2 probe searches** (searches are cheap, briefs are not): import the module, `Client(Path(data_dir))`, call `/api/idea-search` with an obligation-first query (`"AUSTRAC AML/CTF compliance software for Australian real estate agencies, CDD and SMR"`, `"Australian small business invoicing and payments, GST BAS reconciliation"`) and count AU mentions. Same corpus returns AU rows immediately (3–5 of 20).
- Diagnosis to report: a query built from *"Australian" + assurance-evidence/supplier-verification/procurement* tokens is drowned by the global AI-assurance cluster; the single geography token loses to four domain tokens.
- **Quantified on 28 Oct (reuse these as the baseline):** shipped `buy_au_ai` query 0/25 AU (0/81 seven-day union); the same assurance vocabulary with the word "Australian" stated **twice** still 0/10 AU; obligation-first AU tax/trust wording **21/25 (84%)**. Conclusion to state: the *domain vocabulary* controls the result, adding geography words does nothing — the fix is deletion, not emphasis.
- **Cross-tab geography × domain, not just geography.** A lens can be "AU-rich" and still useless if its domain never overlaps ours. On 28 Oct a real-estate-anchored AML/CTF probe returned 9 AU rows and 4 AML rows and **0 that were both** (AU rows were tax/trust; AML rows were South Africa, Indonesia, US life insurers, CFTC, RERA) — while `amlhive`'s seven-day union was 4/65 (6.2%) AU. If AU∩domain ≈ 0, say the lens is a **competitor/pattern feed, not demand evidence**, and do not rewrite a second standing lens on one 25-row probe; measure two more runs first.
- **The corpus's only AU-dense seam is AU tax/trust/property-reform** (ATO pre-filing, trust distribution control rooms, indexed gains, bucket companies, rental reform). High AU rate, but outside all four lanes with no customer base — record it as a *query-design* insight, never as a product recommendation.
- Escape hatch for the row worth keeping: a probe-revealed AU row can be carried forward, but label its provenance (`source_note: diagnostic probe, not a lens query`) in both the assessment and `idea-register.json`.

## 4. Verify Australian claims at source

- Buy Australian AI dates live at `https://www.ai.gov.au/buy-australian-ai-partnership-program` and the Stone & Chalk page `https://www.stoneandchalk.com.au/buy-australian-ai`. Re-check every run — do not hardcode cohort dates. (Oct 2026 state: EOI closed 24 Sep, cohort 5 Oct–27 Nov, so no application action; programme is banking/insurance/super, so AMLHive fit is partial.) Selection ≠ contract, procurement approval or funding.
- AUSTRAC guidance URLs: confirm HTTP 200 with curl and cite them for the *problem*, not for willingness to pay.

## 5. Output contract

- `idealab-assessment-YYYY-MM-DD.md` — exact titles/IDs/links, original idea vs adaptation, current product/backlog overlap, AU evidence, effort/dependencies, revenue path, risks, confidence, seven-day cheap validation.
- `idealab-brief-YYYY-MM-DD.md` — at most three candidates in priority order, each with link, proposed use, why now/fit, confidence, next cheap action, plus a coverage line. If nothing qualifies: "No strong new IdeaLab matches today."
- `idealab-brief-*.md` holds the block **without** the marker lines (markers are added at insertion). Insert between `<!-- IDEALAB_START -->` / `<!-- IDEALAB_END -->` in `morning-briefing-YYYY-MM-DD.md`, **replacing** the existing block (assert each marker occurs once). Anchor for a first insert: `\n---\n📎 *Full report:` — the block goes just above the footer, leaving all `## ` sections untouched (assert the section count is unchanged afterwards). A preview copy written by integration tests holds the same block — refresh it too or it ships stale coverage.
- Update `shortlist.json` (≤10 entries, `history[]`, review_history) and set `last_surfaced_at`/`last_surfaced_hash` in the register for surfaced IDs only.

## 6. Verify before finishing

Nonempty; today's Sydney date; markers exactly once; every surfaced ID resolves (`curl -o /dev/null -w %{http_code}` on `https://idealab.ai/idea-details/<id>` → 200); each recommendation has evidence **or an explicit evidence gap** plus a next action; no other briefing section rewritten.

## Pitfalls

- **Probe mechanics (cost 3 wasted calls on 28 Oct):** import the collector module, `Client(data_dir)`, then **`c.initialise()` before any call**. `call()` rejects any path not starting with `/api/` (`ValueError: Invalid IdeaLab API path`), so pass `/api/idea-search`, not `idea-search`. The body is the full search request — `{"query": q, "sectors": [], "capital": [], "limit": N, "sort": "match", "includeTotal": True}` — a bare `{"query","limit"}` is not what the site expects. `client.allowance` is `None` until the first call returns.

- **With zero briefs but first-seen rows, disposition EVERY first-seen row** (fold / reject-with-reason / improve-existing), not just the interesting ones. That is the whole decision output of the run: it retires rows from future candidate lists. A reject is legitimate when the thesis's own first two sentences name a jurisdiction or buyer that is not ours.
- **Screen jurisdiction and ICP before anything else on the AMLHive lens.** New rows are overwhelmingly US-specific (senior care, Medicaid, state-vendor privacy, notaries, M&A law firms, condo/HOA); one read of the thesis is enough to reject, and no score should be issued. Two structural tells: (a) it sells *to suppliers/vendors of* the regulated entity — the ICP is inverted; (b) it sells confidentiality/privacy controls, not an AML/CTF obligation.
- **Read the `vehicleLabel` as a delivery-model tell.** `Founder Need`, membership, collective, cooperative, group insurance or "specialist human review" means managed service — conflicts with the SaaS-first model and can be rejected without a brief. Likewise pooled benefits distribution.
- **Report per-lens rotation, not just first-seen counts**: comparing this pass's ID sets with the previous day's file (typical: 15–22 of 25 repeat per lens) separates "register stable, sample noisy" from real change in one line. A shortlist row can fall out of the sample entirely (#1345801 did) — check its register hash before writing anything about absence.
- **Verified Australian sources for taxi/workforce rows:** `safeworkaustralia.gov.au/.../psychosocial-hazards` (HTTP 200) supports the generic PCBU psychosocial duty; there is **no** taxi-specific fatigue page — `pointtopoint.nsw.gov.au/safety/driver-fatigue` and the NSW point-to-point "driving a taxi or hire car" page both return 404. Say "evidence gap" rather than implying either way.
- **An all-repeat pass (0 first-seen, 0 changed) is a real result, not a failed run** — say so plainly and do not surface a carried row to look busy. When briefs are unavailable the highest-value work on such a sample is a **thesis-level duplicate/fold screen** against the open shortlist: title+thesis only, labelled as such in `idea-register.json` (`assessment_depth: thesis_level_no_brief`), so the row stops re-appearing as a candidate. Folds should say *which* dimension they add (segment, managed-vs-SaaS, payments) rather than just "duplicate".

- **Identical queries minutes apart return different row sets, different `total`, and different AU-mention counts** (217 vs 326; 3 vs 5 of 20; 6 vs 2 of 20 on 27 Oct). Never quote `total` as corpus or market size; quote a probe result as *direction*, and keep the per-lens six-day union figure as the stable measure.
- **Verified AU trigger for payments-reconciliation ideas** (use for #814027 and merchant fee rows; `rba.gov.au/.../2026-03/conclusions-paper/faqs/` is curl-able 200): 1 Oct 2026 surcharge ban **and** lower domestic interchange caps; **30 Oct 2026** networks and large acquirers must publish card-fee data; **30 Jan 2027** acquirers must publish interchange pass-through; **1 Apr 2027** all acquirers must give merchants detailed statements. Taxi surcharging stays with state/territory regulators — never attribute the ban to taxi fares.
- **AI-incentive ideas have no AU cash analogue:** `business.gov.au/expertise-and-advice/ai-adopt-centres` (200) shows AI Adopt Centres give **free** services (training, consults, roadmaps) to SMEs in NRF priority sectors — no application-evidence incentive to sell against. `business.gov.au/grants-and-programs/ai-adopt-program` and `industry.gov.au/funding-and-incentives/ai-adopt-program` are both **404**.
- `accc.gov.au` card-surcharge pages return **403 to curl**; read them via the search index and corroborate with the RBA FAQ + AusPayNet release rather than citing a failed fetch.
- The **Buy AU AI lens is dominated by one AI-assurance / "AI passport" / procurement-evidence cluster** (often ~35 of 44 rows, many near-duplicates). Treat it as a cluster, not a shortlist: those businesses need auditor independence and a buyer Haris does not have. Borrow the artefact (a machine-readable evidence pack for enterprise procurement), not the business.
- Priority-lens ordering can legitimately invert: when the top three lenses yield only clusters or consumer-side ideas, surface the tapease/POS candidates and **say explicitly that the priority lenses produced nothing** — do not pad with a weak higher-priority row.
- PCI SSC's PDF hosts (`docs-prv.pcisecuritystandards.org`, `/documents/*.pdf`) return **403/404**; do not cite PCI DSS requirement text (e.g. 9.5.1 POI inventory) as verified unless fetched. PCI SSC FAQ pages (`/faqs/1301/`) do resolve.
- `service.nsw.gov.au` pages are curl-able primary evidence for taxi obligations (annual safety inspection regardless of vehicle age, CTP, 6-month inspection validity). `web_extract` may time out on them — curl and grep the HTML.
- `--details` writes a JSON **list** and does not echo the allowance; count brief opens yourself against the 10/day cap.
- **The day's brief allowance can arrive nearly spent** (e.g. 9/10 used by the previous run, resets ≈05:30 Sydney). Before choosing what to open, read `allowance.briefs.remaining`: with one open left, spend it on the single most *distinct* row and leave cluster variants and folds summary-only. Say explicitly which candidates are summary-only and lower their confidence. With **zero** left, open nothing and state the cap.
- A single `--lens all` pass at `--pages 1` returns only ~25 rows per lens. Records surfaced the day before can then vanish from the sample (#814027 did on 24 Oct) — check `last_seen`/`content_hash` in the register before implying anything was withdrawn.
- **The Buy AU AI lens can be 100% one cluster** (25/25 assurance/"AI passport" rows on 24 Oct). Two rejection reasons repeat and should be named fast: a *managed service* conflicts with the SaaS-first model, and anything selling procurement readiness **to AI suppliers** sells to Haris rather than to his customers.
- Fresh rows can be disguised duplicates: #886514 (driver licensing/inspection concierge) is the same deadline+document+escalation pattern as #1345801 (fleet inspection desk) — fold it as a *scope note* (which credential sits on the deadline) instead of a second build.
- For lead-gen/adtech rows, **[OAIC APP 7](https://www.oaic.gov.au/privacy/australian-privacy-principles/australian-privacy-principles-guidelines/chapter-7-app-7-direct-marketing)** is curl-able (HTTP 200) and states an organisation must not use or disclose personal information for direct marketing unless an exception applies, with consent/notification/opt-out duties. Cite it as the constraint on any idea that monetises customer PII by routing offers to third parties.
- Check the source jurisdiction before assessing fit: #1027708's only publisher was `larepublica.pe` (Peru) with all five competitors in New York. IdeaLab market figures derived as "N providers × $X/year spend" are assumptions, not observed spend.
- `service.nsw.gov.au/transaction/apply-for-a-taxi-driver-authority` returns **404** and `pointtopoint.nsw.gov.au` returns **403**; only the renew-a-taxi-registration page has been curl-verified for taxi obligations.

- `--lens all` rewrites the candidate file from the *existing* file plus this pass's rows; a concurrent or earlier narrower run can leave the file smaller than the register. Compare counts, don't assume continuity.
- Detail fetches count against the brief allowance; check `allowance.briefs.remaining` first.
- **`idea-register.json` tolerates a `_meta` key** for findings that belong to no single idea (e.g. query-probe results). The collector only does keyed `.get(idea_id)` lookups and rewrites the dict wholesale, so `_meta` survives; keep idea IDs as bare numeric strings so nothing collides. Verify after writing that the idea-ID count is unchanged.
- **Thin days are for measurement, not for manufacturing a candidate.** With 2 first-seen rows and 0 briefs, the run's deliverable was a measured replacement query (0% → 84% AU) plus two clean rejects — that is a successful run. Do not pad the brief with a weak higher-priority row, and do not re-surface an unchanged shortlist row just to have a "candidate"; a hold with a calendar trigger (e.g. #814027's 30 Oct date, 2 days out) is a status line, not a re-surface.
- **Zero briefs for five days means every judgement is `search_summary`.** Say so at the top of the report and cap confidence explicitly; do not let a summary-only rejection read like a researched one.
- Weekend delivery prompts must include the same block inside their existing response.
