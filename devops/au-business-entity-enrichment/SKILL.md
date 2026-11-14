---
name: au-business-entity-enrichment
description: Use when building an enriched AU business list.
version: 1.0.0
author: mercury
license: MIT
metadata:
  hermes:
    tags:
      - data-acquisition
      - enrichment
      - abr
      - asic
      - lead-generation
    related_skills:
      - undispute-merchant-enrichment-agent
      - web-data-acquisition
---

# AU business entity enrichment (identity → validity → contacts → size → group)

## When to Use

- The user asks for a list of Australian businesses or agencies with contact details (phone, mobile, email).
- You are about to scrape a business directory, portal or search engine for AU business contacts.
- You need to confirm an ASIC/ABN entity is still active before using it for outreach.
- You are sizing Australian businesses or resolving franchise/group affiliation.

Building a callable B2B list of Australian businesses (real-estate agencies, merchants, any licensed
vertical) from public sources, with a provenance column for every field.

## Source hierarchy — establish this before promising a deliverable

1. **There is no national business register for licensed trades.** Licensing is **state-based**; each
   state exposes a different-shaped register. Say so up front rather than implying a single download.
2. **AUSTRAC publishes COUNTS, not lists.** No public enrolled-entity list for Tranche 2 real estate.
3. **Our own asset first: the ASIC reference dump.** `/home/habib/data/asic_sync/asic_companies.csv`
   (company name, ACN, type, status, state, ABN) and `asic_business_names.csv` (name, status, state,
   ABN). Filter registered + name-pattern to build the universe for free — a real-estate name filter
   (`REAL ESTATE|REALTY|ESTATE AGENT|LAND AGENT|PROPERTY MANAGEMENT|PROPERTY GROUP|REALTOR`) yields
   ~26k unique ABNs. **Do this before spending anything on discovery or scraping.**
   Project work dir for agency lists: `/home/habib/data/au-re-agencies`.
4. **ABR is the validity oracle and needs no credential** — see below. It is also the best source of
   state/postcode ("main business location"), which ASIC lacks for business names.
5. **Contact details exist only on the business's own website.** No register in Australia publishes
   phone, mobile or email for these entities — verify before telling anyone otherwise.

## Step 1 — identity universe

Parse the ASIC files as **tab-delimited**: they are single-column CSVs whose one quoted field contains
`\t`-separated values (this is the trap — a naive `csv.DictReader` gives one giant column). Dedupe on
**ABN**, which is the join key everywhere. Carry `entity_type` (company / business_name / both) because
business names are the trading name the customer sees and companies are the legal entity.

## Step 2 — validity (this is the step people skip and regret)

`GET https://abr.business.gov.au/ABN/View?abn=<11 digits>` — plain HTML, **no API key, no GUID**.
Parse: `ABN status` (+ `from <date>` when cancelled), `Entity type`, GST registration,
`Main business location: <STATE> <POSTCODE>`, `Entity name`.

- Rate-limit to **~1 request/second**.
- **Expect a large cancelled share.** In the first real sample an ABN from the ASIC extract marked
  "Registered" came back **Cancelled since 2022**. Never treat an ASIC status as proof of life.
- Add live checks: website HTTP status, and licence currency from the state register where obtainable.

Required output columns: `abn_status`, `abn_status_from`, `website_http`, `validated` (YES/NO),
`validation_checks` (human-readable reason string), `checked_at`. A row is only `YES` when the ABN is
Active **and** the website resolves; say which check failed otherwise.

## Step 3 — contacts from the entity's own site

1. Discover the domain by search on the trading name, then **prefer the host that contains a name token**.
2. **Exclude aggregators explicitly** — see Pitfalls; they are what you get if you do not.
3. Fetch the homepage, then the `contact`/`about`/`team` links. Extract `mailto:` emails, `tel:` links
   and AU patterns (`0[2378] xxxx xxxx`, `04xx xxx xxx`, `13/1300/1800 xxx xxx`).
4. Normalise `+61`/`0061` → leading `0` **before** classifying; otherwise every mobile is misread as
   `other`. Classify landline / mobile / service; put the mobile in its own column.
5. Mobiles are the scarcest field — they live on individual agent profile pages, not the contact page.
   Crawl profile pages when mobiles matter; do not report 04xx coverage from a homepage-only pass.

## Step 4 — size (use lawful proxies only)

There is no public field for headcount or revenue. Proxies that work: ABR **entity type** (individual/
sole trader = micro; company/trust/partnership = SME), **GST registration**, agent count from the
business's own `/team` page, and office count from its own site. State clearly that these are bands,
not revenue.

## Step 5 — group affiliation

Match the trading name against a brand registry (Ray White, LJ Hooker, McGrath, Belle Property, PRD,
First National, Barry Plant, Harcourts, Elders, Raine & Horne, Century 21, RE/MAX, Coronis,
Professionals, Richardson & Wrench, Stockdale & Leggo, Nelson Alexander, Jellis Craig, Marshall White,
Kay & Burton, Biggin & Scott, Woodards, Fletchers, Starr Partners, The Agency, Colliers, JLL, CBRE,
Knight Frank, Savills, Cushman & Wakefield).

- **Name match = high precision.** Use it as the primary signal (`group_evidence=name`).
- **Body-text mention = false positives.** A whole-page scan matched an independent agency to CBRE
  because a listing mentioned them. Restrict the second signal to the footer/copyright block
  ("part of", "member of", franchise disclaimers) and record `group_evidence`.

## State registers (starting points, verify each before use)

- **ACT** — full bulk: `https://www.data.act.gov.au/resource/rggi-3jr9.json?$limit=50000` (Socrata,
  ~1,755 licence rows). Columns include `email` and address fields that are **empty for every row**;
  names + licence numbers only.
- **NSW** — `verify.licence.nsw.gov.au` (search-oriented; postcode-range harvests work).
- **VIC** — `registers.consumer.vic.gov.au/EAsearch`. Data.Vic's CAV datasets are **aggregate counts**,
  not licence records.
- **QLD** — Office of Fair Trading; `data.qld.gov.au` carries no agent register (only cadastral/pool safety).
- **WA** — `consumerprotection.wa.gov.au` licence search (`data.wa.gov.au` CKAN returns 500).
- **SA** — `cbs.sa.gov.au/find-a-licence-holder`.
- **TAS** — Property Agents Board register. **NT** — `licensingnt.nt.gov.au/PublicRegister/`.

## Pitfalls

- **Portals are closed and must stay closed:** `realestate.com.au` returns **429**, `ratemyagent`
  returns **403**, `allhomes`/`wheree` are aggregators. Never design a path that depends on them; the
  entity's own site is both lawful and more accurate.
- **Aggregator bleed in domain discovery** — exclude `realestate.com.au, domain.com.au, ratemyagent,
  allhomes, wheree, homely, onthehouse, propertyvalue, abr.business.gov.au, facebook, linkedin,
  instagram, yellowpages, truelocal` before accepting a "website". Otherwise the "agency website" is a
  listing page and every contact field comes back empty.
- **A cancelled ABN can still sit in an ASIC extract marked Registered** — always re-validate.
- **OpenStreetMap `office=estate_agent`** is a useful free contact source (~2.7k AU, ~590 with phone,
  ~110 with email, ~660 with website) but carries `addr:state` on almost no rows — derive state from
  postcode ranges or leave it blank rather than guessing.
- **Scale honestly:** ~26k entities × (1 ABR + 1 search + 2–3 fetches) at 1 req/s ≈ 20–25h
  single-threaded, ~3–4h with 8 workers respecting per-host limits. Offer validation-only first as the
  cheap milestone.

## Downstream

Once contacts exist, outreach gating reuses `undispute-merchant-enrichment-agent` (ACMA/DNCR check
before any contact) — do not build a second outreach path.
