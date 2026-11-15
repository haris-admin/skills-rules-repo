# Alexandria catalogue — provider map, execution shape, quirks

The catalogue is a moving target: **re-enumerate with `scripts/alexandria_discover.py`** rather than
trusting this list. What follows is the shape of it and the traps that cost a call.

## Discovery vs execution (the one thing to get right)

- **Discovery** — `POST /v2/search` body `{"query": "...", "sources": ["alexandria"]}`. Returns
  `data.tools` = **tool contracts** `{provider, capability, description}`, **not** search results, and
  `creditsUsed: 0`. Falling back to a normal search when you meant discovery quietly bills you.
- **Execution** — `POST /v2/scrape` body
  `{"alexandria": {"provider": "<p>", "capability": "<c>", "options": {...}}}`. `alexandria` replaces
  the usual `url` payload (the request schema is `allOf` of url-scrape options plus this alternative).
  `data.alexandria[]` comes back per call with `creditsCost` and either `data` or `error`.
- A `search`-style capability returns **pointers** (`url`, `title`, `snippet`, `updated_at`) — fetch the
  body with a second `/v2/scrape` when you need text.
- **Access gate:** the team's Alexandria access must be enabled, otherwise discovery returns 403.

## Providers observed by vertical

Civil/company registries and filings: `sec-gov` (EDGAR: company, filings, concept, sections, 13F
holdings), `fiscal-ai` (company profile, segments & KPIs, balance sheet as reported), `gleif-org`
(global Legal Entity Identifier — `entities/search`, `entities/entity`), UK
`find-and-update-company-information-service-gov-uk` (search, charges, disqualification, dissolved),
`sos-state-co-us`, `search-sunbiz-org`, `b3-com-br`, `sam-gov`.

Government/statistics: `firecrawl-gov-index.search` (laws, regulations, ordinances), `fda-gov`,
`cftc-gov`, `fiscaldata-treasury-gov`, `data-imf-org`, `data-worldbank-org`.

People: `fullenrich` (work email, personal email, mobile, reverse email, people lookup).

Media/transcripts: `particle` (podcast episodes, feeds, clips, transcripts).

Property: `zillow-com`, `redfin-com`, `craigslist-org`. Marketplaces: `ebay-com`, `etsy-com`.
Reputation/complaints: `bbb-business-profiles-ratings-complaint`, `reclameaqui-com-br`.

**Gap:** no Australian providers. ASIC/ABN lookups, DNCR, AU payments and chargeback data are not in
the catalogue — those stay on our own sources.

## Quirks

- **Option names are per-capability and not guessable.** `gleif-org entities/search` wants `name`, not
  `query`; a wrong key returns `{"error":{"code":"missing_option","message":"... requires name."}}` with
  `creditsCost: 0`. Read the contract description first; a failed option check is free, a wrong scrape
  is not.
- **Every executed call reports its own `creditsCost`** — read it and report the run's total instead of
  estimating from a pricing page.
- **Rate limits are per plan**; a fast multi-query sweep returns 429. Space the calls (~1.5 s) and keep
  batches small.
- **Terms acceptance:** some providers need an organisation admin to accept terms before the tool runs.
- **Indexes are pointers.** The Government/Developer/Research indexes return citations and records
  (URLs, arXiv ids, abstracts, repo paths) that you then fetch or cite — they are not answer engines.
- Research and developer indexes have dedicated endpoints (`GET /v2/search/research/papers`,
  `POST /v2/search/developer`) and do not need the catalogue round-trip.
