# Australian business registers for list enrichment

What each public register actually exposes, and how to classify the resulting businesses by size. The
recurring question is "can I get phone and email from the register?" — for most Australian occupational
registers the answer is no, by design, and the contact data has to be scraped from the business's own site.

## Register matrix (verified by probe)

| State | Access | What the register publishes | Contact data |
|---|---|---|---|
| NSW | Undocumented JSON API behind the SPA, unauthenticated | name, licence no, type, status, suburb, postcode, **ABN, ACN** | **None** — no phone/email at any depth (search, detail, or Excel export). Statutory. |
| WA | JSON dump | name, trading names, **full street address**, postcode, entity type | Schema has `businessPhone`/`mobilePhone`/`emailAddress`/`website` — **all 0% filled**. |
| SA | CSV export | name, street address, postcode | None; check the dataset's vintage before use — a stale dump yields dead businesses. |
| TAS | **PDF only**, republished periodically | name, business name, place of business, managing agent, directors, expiry | None; licence number also absent. |
| VIC | CSV export | name, ABN, ACN, street address, web address, phone (partial) | Some phone/website. |
| QLD | Export exists but is largely **individual licensees with no address** | — | Unusable for business-level enrichment. |

Design the pipeline on the assumption that **location + name are the only universal fields**. Identifiers
(ABN/ACN) are patchy: one register carries ACN on every row and ABN on 39%, others carry neither, and
several publish nothing at all. Never build a join that requires an identifier to exist.

**Count businesses, not licensees.** Registers mix licensed *people* into the same stream as licensed
*businesses*, and the individuals are usually the majority — one state's 4,450-row dump held 2,823
individuals against 1,627 bodies corporate and partnerships. Filter on entity type before quoting any
total, or the agency universe is inflated by roughly 60% and every coverage rate downstream is computed
against the wrong denominator.

## ABR Lookup API — the ownership and identity source

The registers tell you who holds a licence; the Australian Business Register tells you **which legal entity
stands behind it**, which is the field owners actually ask for ("doesn't say who owns the business"). It is
free and needs only a GUID from abr.business.gov.au, stored as `ABN_LOOKUP_GUID`:

```
GET https://abr.business.gov.au/abrxmlsearch/AbrXmlSearch.asmx/SearchByABNv202001
    ?searchString=<11-digit ABN>&includeHistoricalDetails=N&authenticationGuid=<GUID>
```

Returns XML carrying `organisationName` (or `mainName` for an individual), `entityType`, and
`businessName` entries — enough to resolve a trading name to its legal entity, and to confirm a website's
ABN against the register. Two limits worth setting expectations on: it identifies the *entity*, not a
named contact person, and a wrong or missing GUID returns an error payload with HTTP 200, so parse for the
exception element rather than trusting the status code. A Cloud `GOOGLE_API_KEY` is not a substitute here,
and the AI Studio keys cannot reach the Maps/Places side at all.

Pace at one request per second and cache one XML file per ABN — about 1,260 lookups finish in roughly 20
minutes and every re-run costs nothing. Redact the GUID before writing a response to cache: the payload
echoes it back in `<authenticationGUID>` (see the credential-scrubbing rule in SKILL.md).

Parsing details that decide coverage and honesty:

- **Trading names live in three elements** — `mainTradingName`, `otherTradingName` and `businessName`.
  Collect all three or the output under-reports the names the business actually trades under.
- **GST is cancelled, not absent, when `goodsAndServicesTax` carries an `effectiveTo` date.** Treat a
  present `effectiveTo` as `N`; only a live registration has no end date. Reading mere element presence as
  "registered" overstates GST coverage.
- **Sole traders resolve to the natural person** — no `organisationName`, the person in `mainName`, and the
  business sitting in the trading names. Surface that as the owner; it is not a missing entity.
- **Expect a small share of source rows to carry an ABN that fails the checksum** (about 2 in 1,260 seen).
  The API answers `Search text is not a valid ABN or ACN`. Leave those blank and report them: a bad ABN in
  the input list is a finding about the source, not something to repair or substitute.
- **Take state and postcode from the ABR address, not the input file.** The register's own address is the
  authoritative one, and a disagreement between the two is worth surfacing rather than silently resolving.

## NSW API shape (the undocumented public one)

Base `https://verify.licence.nsw.gov.au/publicregisterapi/api/v1`, no auth, no cookie:

- `POST /licence/search/advQuery` — body `{licenceGroup, autoComplete:false, pageNumber, pageSize,
  licenceTypes[], status:["Current"], location:["<locationId>"], search, address, wildCardAddressSearch}`.
  **`pageSize` is hard-capped at 200**; larger values return HTTP 400, and a truncated result set fails
  silently unless you check the paging info. Segment by postcode, then by suburb for dense postcodes.
- `POST /licence/search/areasNoCount` — `{licenceGroup, suburbLGAText:"<2+ chars>", autoComplete:true}`;
  returns the postcode's `locationId` plus each suburb's, which is how you subdivide a postcode.
- `GET /licence/search/details/{licenceType}/{licenceId}` — URL-encode the type
  (`Property%20-%20Corporation/8846502`). Returns the deep record incl. associated roles.
- `POST /licence/search/advQuery/export?format=excel` — same 200-row cap, and no contact columns.

Edge behaviour: send a real browser User-Agent (a default `urllib` UA is refused), set `Origin`/`Referer`
to the SPA host, and pace at ~1 request/second. Sustained fast calls trigger a temporary IP block; cache
every response to disk so a block costs nothing and the harvest resumes. Rebuild the output from the cached
responses rather than from whichever process wrote the CSV last.

## Boutique vs enterprise classification

Enterprise means "present in more than 3 suburbs/branches". Three signals, cheapest first — each record
carries the evidence string that produced its bucket, so any row can be audited:

1. **Known network list** — name matching a franchise/property group is enterprise with no lookup. Match
   on the **squashed** name as well as the literal (`L J Hooker` → `ljhooker`), or spaced spellings slip
   through into the boutique bucket.
2. **Domain collision** — the same website appearing on several licence records in different suburbs is a
   multi-office group. Free, computed from data already held, and the most trustworthy signal: it caught
   groups the network list missed, and it is the only one that comes from evidence rather than a guess.
3. **Brand-word cluster** — leading non-generic words recurring across 5+ suburbs.
4. **Shared contact** — a phone or email appearing on 3+ licence records is one operator holding several
   licensed entities, not several boutiques. Only computable after contact extraction, so apply it as a
   demotion pass at the end rather than during classification.

```
enterprise  : known network | site spans >=4 suburbs (>=5 = certain) | brand cluster >=5 suburbs
boutique    : site found and spans <=3 suburbs      -> confirmed, ready to enrich
boutique?   : no site yet, cluster <=3 suburbs      -> needs discovery
unverified  : neither
```

**Two traps in the cluster signal.** A key that appears inside its own suburbs is a **place name**, not a
brand — "Central Coast" and "Perth" otherwise collapse dozens of unrelated agencies into one fake group;
test `key in suburb` and drop the key. And generic industry adjectives (choice, prime, premier, central,
first, prestige, elite, national, commercial, strata, property, realty, group) must be excluded before
taking leading words, or every second agency clusters together.

Keep `boutique_confirmed` and `boutique_likely` as separate buckets. Only the first has a verified site;
the second is a priority ordering, not a finding, and should not be reported as contactable.

## Website discovery by search: the aggregator trap

Once a record has no guessable domain, discovery moves to a search provider. The failure mode changes
shape here, because the register name is often a legal entity that no directory lists and no domain
matches, while the suburb is present on dozens of irrelevant pages.

A first batch returned a 100% hit rate and was almost entirely wrong: `homeone.com.au`, `farmbuy.com`,
`auctionsplus.com.au`, `mapquest.com`, and the search provider's own `exa.ai/library/place/…` pages. Every
one named the suburb. Filter in three layers, cheapest first:

1. **Host blocklist** — agents' portals, real-estate aggregators, review sites, credit/data brokers and
   map/location directories. Keep it in one constant so a new leak is a one-line fix.
2. **Directory-shaped paths** — `/agencies/`, `/agentlistings/`, `/library/place/`, `/directory/`,
   `/company/`, `/profile/`, and editorial paths `/news/`, `/blog/`, `/article`, `/press/`. Franchise
   networks run news sections that mention member agencies by name; those are articles, not offices.
3. **Identity score** — a distinctive business-name token (longer than 3 chars, not an industry word) in
   the domain, or at least two such tokens in the body. This is what finally separates "the page mentions
   Rice Livestock" from "this is Rice Livestock's website".

Expect the strict gates to cut the hit rate to roughly a third on rural and legal-entity names. That is
the correct outcome: those records stay in `boutique_likely` until a better query finds them.

Provider quality for AU local-business discovery, measured on the same queries: **Exa** returned the
agency's own site as the top hit most consistently; **Serper** with `gl=au` returned the agency plus a
franchise office page and is the best fallback; **Tavily** returned data brokers and LinkedIn instead of
the business and is the weakest of the three for this job. **Firecrawl** search is usable and costs a credit
per query, but it ranks `realestate.com.au` and `domain.com.au` above the agency's own site — the host
blocklist is what recovers a usable candidate, so it discovers fine and filters badly on its own. Brave
sits between. Order the waterfall by cost anyway — the gates reject the bad answers — but reach for Exa
first when quality matters.

## Audit an enriched list before delivering it

Two checks over the finished file catch most of what the per-record gates let through, and both are cheap:

- **Contact reuse.** Count every phone/mobile/email value across the whole file. A value on 3+ records is
  either one operator with several licensed entities (demote to group) or a shared template/widget number
  (drop the contact). Reporting either as independent boutique contacts inflates the list with duplicates
  the owner will discover on first call.
- **Area code vs state.** Normalise the number and compare its prefix to the record's state (`02` NSW/ACT,
  `03` VIC/TAS, `07` QLD, `08` SA/WA/NT). Flag mismatches in a notes column rather than deleting them: a
  flagged number the owner can check beats a silently missing one.

Report the surviving count as the deliverable and quote the flagged/rejected counts beside it, so the
headline number is auditable instead of a bare total.

## Working implementation

Live scripts in `/home/habib/data/au-re-agencies/probe/`: `au_gate.py` (country + ABN checksum + locality
gates), `domain_guess_fast.py` (DNS-precheck, threaded, free website discovery), `classify_boutique.py`
(buckets with evidence), `enrich_free.py` (urllib contact extraction, email-domain match, resumable
per-record cache), `build_master.py` (multi-state normalisation into one schema), `search_router.py`
(cost-ordered multi-provider waterfall with on-disk quota state and query cache), `site_finder.py`
(search-driven discovery with the aggregator/identity gates above), `build_sheet_export.py` (merges every
source into one sheet-ready file with website precedence search > guess > register), and `sheets_push.py`
(service-account writer: grid expansion, clear, RAW values, header format; see
`google-sheets-delivery.md`).
