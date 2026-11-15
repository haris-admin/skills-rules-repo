---
name: web-data-acquisition
description: Use when scraping, extracting or monitoring web data.
---

# Web data acquisition (Firecrawl + the Alexandria provider catalogue)

Getting page content, structured records or change alerts out of the web for research, enrichment or
AI-discoverability. The fleet's engine for this is **Firecrawl v2**, plus its **Alexandria** layer — a
catalogue of official data providers and curated indexes reachable through the same API.

## Auth and hygiene (always on)

- Key lives in **`/mnt/c/Users/habib/.hermes/.env`** as `FIRECRAWL_API_KEY`; a loader must also check
  `~/.hermes/.env`. Read it with `python3 ~/.hermes/scripts/envpeek.py <file> --key-like` — never
  `grep`/`cat`, never print it, never paste it into a command line you then show. See
  `~/.hermes/rules/secret-handling.md`.
- **Check the credit balance before and after any batch**: `GET https://api.firecrawl.dev/v2/team/credit-usage`
  (also `/v2/team/token-usage`). Report a delta, not a guess. Discovery is free; only execution bills.
  The same response carries `planCredits` and `billingPeriodEnd`: remaining credits **lapse at period end**
  and do not roll over, and `remainingCredits` can exceed `planCredits` when a bonus is active — spend the
  surplus before the period closes instead of letting it expire.
- **Confirm which providers are actually keyed before designing a failover chain.** List the key names in
  the env file (names only, never values) and plan the rotation around what is really there; a
  multi-provider waterfall designed from memory rather than from the env silently degrades to one provider.
- **Separate a dead key from an unentitled one.** These look alike and have opposite fixes. A `401 "API keys
  are not supported by this API"` means the credential type is wrong — AI Studio / Gemini keys (~53 chars)
  are rejected outright by Maps and Places endpoints. A `403 ACCESS_DENIED`, or the legacy
  `This API is not activated on your API project`, means the key is fine and the API is simply not enabled
  on the project. Probe an API the key is known to serve (`GET
  https://generativelanguage.googleapis.com/v1beta/models?key=…` for a Cloud key): if that answers 200 while
  the target returns 403, the fix is a console toggle, not a new key. Say which one it is — "Places is
  broken" sends the owner to buy a key they already have.
- **Scrub your own credential out of cached payloads.** Some registry APIs echo the caller's key back inside
  the response body — the ABR Lookup API repeats `authenticationGuid`. So "cache every raw response for
  resumability" silently writes a live secret to disk in plaintext, where any later grep, log dump or
  handed-over cache directory exposes it. Redact the value before persisting, and prove it by grepping the
  cache directory, output files and logs for the credential rather than by intending to. The written check
  is the control; the intent is not.

## Cost model — pick the cheapest path first

1. **Discovery is free.** `POST /v2/search` with `sources: ["alexandria"]` returns **tool contracts** in
   `data.tools` (`{provider, capability, description}`), `creditsUsed: 0`. Requires the team's Alexandria
   access to be enabled (403 otherwise).
2. **Execute a provider tool** with the same scraper you already use:
   `POST /v2/scrape` body `{"alexandria": {"provider": "<p>", "capability": "<c>", "options": {...}}}`.
   The response carries per-call `creditsCost`. The scrape body is `allOf(url) + ScrapeOptions +
   {alexandria}` — `alexandria` is an alternative payload to `url`, not a sibling format.
3. **Web search / scrape** bills normally (a Government-Index search cost 2 credits; a simple scrape ~1).
4. **`POST /v2/agent` defaults to `maxCredits: 2500`** — always set `maxCredits` explicitly for agentic
   extraction, and prefer the smaller model / `effort: low` when the task is simple.
5. **Order a multi-provider search waterfall by cost, not quality.** Because the country and locality gates
   reject bad matches, a weak free provider costs a retry rather than a wrong record — so the free tier can
   safely go first. Sequence: recurring monthly free credit → other recurring free tiers → one-off starter
   credits (these never refill, so reserve them for what the free tiers could not answer) → paid credits;
   hold JS-rendering scrape back for pages plain HTTP cannot read. Keep per-provider `{used, limit, fails}`
   state on disk and cache results by query hash, so a restarted batch never re-spends what the previous
   attempt already bought. Several providers expose no balance endpoint at all — drive quotas from local
   counters, not from the API.

## Procedure

1. **Enumerate before executing.** Run the discovery sweep (`scripts/alexandria_discover.py`) against the
   question in hand and read the returned contracts — each names its provider and capability.
2. **Execute the narrowest capability** that answers the question, then scrape the URLs a result returns
   if you need the body text (index/gov results are *pointers*, not full text).
3. **Read the contract's option names before calling** — an option mismatch returns
   `{error:{code:"missing_option"}, creditsCost: 0}`.
4. **Turn a site into LLM-ready data**: `POST /v2/map` for the URL set → `POST /v2/crawl` (or `/batch/scrape`)
   for markdown/JSON per page → write `llms.txt` (concise map: who we are, the use cases, dated facts,
   link to `llms-full.txt`) plus `llms-full.txt` (full comparison/recommendation context).
5. **Monitor changes** with `POST /v2/monitor` — targets are `scrape` (explicit URLs), `crawl` or
   `search`; `schedule` takes a 5-field cron OR plain text (`daily at 9am`) plus an explicit `timezone`;
   `goal` + `judgeEnabled` make an LLM judge whether a change is *meaningful* (a `search` target requires
   `goal`); delivery is `webhook` and/or email with `includeDiffs`. Point the webhook at the fleet so a
   regulatory or competitor change lands as an event, not a thing someone remembers to check.

## AI-readiness audit of our own sites

Before claiming a site is AI-ready, check all four: `llms.txt`, `llms-full.txt`, `robots.txt`, sitemap.
A 404 on `robots.txt` is the tell that nobody has done this yet — cheap to fix and it is the difference
between an agent reading clean structured content and re-deriving it from HTML. Re-run the check after
the fix rather than assuming.

## Pitfalls

- **No Australian providers in the catalogue.** AU-specific queries (ASIC/ABN, DNCR, payments/chargebacks)
  return **zero tools**. Firecrawl covers the open web, US/UK/BR/global registries and its own indexes —
  it does **not** replace our ASIC/ABN/ACMA sources. Do not design an AU compliance path that assumes it.
- **Indexes are pointers, not answers.** The Government Index (laws/regulations/ordinances), Developer
  Index (docs, READMEs, issues, PRs) and Research Index (paper abstracts) return citations/records that
  you then fetch; budget a second call per result you actually need.
- **`429` is a rate limit, never an exhausted credential — do not let one disable a provider.** Read the
  body before deciding: Firecrawl returns `retry_after_seconds` alongside `Consumed (req/min)` /
  `Remaining (req/min)`, and the free plan allows roughly 10 requests per minute. Wait that interval, retry
  the same provider once, then hand the query to the next one in the chain. The failure to design against is
  a handler that treats every 4xx as fatal and sets `used = limit`: that turns a five-second throttle into a
  provider switched off for the whole batch, and the sweep silently degrades to the next tier with no error.
  Reserve `used = limit` for `401/402/403` only. Pace with a per-minute token bucket that *skips* a provider
  whose window is full and falls through immediately, rather than sleeping — blocking on the slowest provider
  stalls the entire sweep while faster ones sit idle.
- **Discovery-only is the safe default.** Creating monitors, agent runs or provider terms acceptances
  writes to the owner's account and spends credits — propose them and let the owner choose; explore
  read-only, and say how many credits the exploration cost.
- **Some providers require an organisation admin to accept terms** before execution; a contract can be
  discoverable and still not runnable.
- **A login gate is often an artifact of the URL, not of the content.** Before authenticating — or asking the user
  to — follow the redirect chain and read the final page title: a community/portal "room" or workspace URL that
  302s to a single sign-on page usually resolves to one individual event or record, and that record's canonical
  public page (`/events/details/...` and the like) carries the same body with no auth. Search the exact resolved
  title to find it. Escalate to credentials only when no public canonical exists, and never store a third party's
  identity credentials to read one page.
- **Verify "today" against the machine, not the session context.** Before any time-sensitive claim — an event is
  upcoming versus already held, a deadline is close, a reporting window is open — run `date`. The date carried in
  the session context can lag the real clock, and being wrong flips "it's live right now, join" into "it's on next
  week".

## Entity lists: find the website, then trust nothing

When the deliverable is a contactable business list (agencies, merchants, dealers) built out of public
registers, the failure mode is not an empty field — it is a confident wrong one. Order of work:

1. **Start from the register that carries a location.** Business name + suburb + postcode is the only
   search key that disambiguates. A list with names and ABNs but no locality cannot be matched at all:
   name-only search returns a same-named company in another country, and an ABN alone returns registry
   pages. Enrich the located list first, then use registry identifiers to extend it.
2. **ABN is a verification key, not a discovery key.** Businesses rarely print an ABN in crawlable text,
   so searching the number finds registries, not the business. Use it in the other direction: when a
   fetched page shows an ABN, checksum it (subtract 1 from the first digit, weight
   `10,1,3,5,7,9,11,13,15,17,19`, sum mod 89 == 0) and compare to the register — a match is a hard
   identity confirmation.
3. **Gate every match to the country.** A 100% name match on a foreign company is worth nothing. Accept a
   site only if the host is under `.au`, or the page carries a checksum-valid ABN, or it shows a `+61`/`0X`
   number alongside an Australian state name. Reject foreign TLDs outright — even when the page mentions
   the state, since a `.co.uk` describing NSW is still the wrong business.
4. **Guess the domain before paying for search.** Build candidates from the trading name
   (joined / hyphenated / industry-words-stripped, `.com.au` then `.net.au`), resolve DNS first and only
   fetch the hosts that resolve: a dead candidate costs milliseconds instead of an HTTP timeout. With a
   thread pool this finds roughly a quarter of all websites at zero API cost, and front-loads the paid run.
5. **Keep an email only when its domain matches the site host.** Pages embed partners' and template
   vendors' addresses; without this check a confirmed-looking email belongs to a different company
   entirely.
6. **Require the page to name the locality.** Suburb or postcode present, or the match is discarded —
   this is what stops a plausible same-named business being accepted.
7. **Then require the page to be *that business*, not merely *that suburb*.** Directories, aggregators and
   news posts about the business all name the locality, so the locality gate on its own can pass every
   candidate. Reject known aggregator hosts and directory-shaped URL paths (`/agencies/`,
   `/agentlistings/`, `/library/place/`, `/news/`, `/blog/`), then score identity separately: a distinctive
   token from the business name in the domain, or at least two in the page text. A dropped record is
   recoverable; a directory URL delivered as the agency's website is not.

## Pitfalls — entity lists

- **A directory listing is the most common false positive — not the foreign company.** An aggregator page
  names the suburb, sits on a plausible domain and often mentions the business by name, so it clears the
  country, locality and even weak name checks while being worthless as a contact source. Curate both a host
  blocklist and directory-shaped path fragments, and keep identity as its own gate; tightening only the
  locality rule never removes them. Treat a 100% hit rate on a first batch as a bug report, not a result.
- **A franchise domain is the group, not the office.** `belleproperty.com` / `harcourts.net` confirm the
  network but tell you nothing about the branch; resolve to the office page before treating it as that
  agency's site, and never quote a group's head-office phone as a branch contact.
- **Check a register column's fill rate before building on it.** Fields can exist in the schema and be
   uniformly empty in the published data; a column that is present is not a column that is populated.
  Count filled values across the whole dump first, and treat location and name as the reliable backbone.
- **For independent/boutique businesses the free path often beats the paid one.** Small operators publish
  real contact blocks; franchise offices hide behind enquiry forms. Plain HTTP + an HTML parser with the
  gates above covered ~93% of boutique agencies against ~60% for the same list through JS-rendering
  scrape, at zero credits. Try direct fetch first and spend credits on the failures.
- **A standalone script cannot import `hermes_tools`** — that package exists only inside the agent's
  `execute_code` kernel. Fetchers that must run unattended or over more than the tool-call ceiling should
  use `urllib.request` plus `html.parser`, and keep `execute_code` for interactive probing.
- **An API key cannot write to the owner's Google Sheet, and an OAuth *client* file is not a credential.**
  Delivering a finished list into a spreadsheet needs an *authorised user*, not a key. Three paths, cheapest
  to check first: a token already stored by the `gog` CLI, a service-account JSON whose email the sheet
  shares as Editor, or Application Default Credentials from an authenticated `gcloud auth
  application-default login`. Files named `credentials*.json` are usually only `{"installed": {...}}` client
  configs with no refresh token, and a Maps/Gemini API key has no Sheets scope at all.
  Run `gog status` and list `~/.config/gogcli/keyring/token:*` before designing anything: an email there means
  the authorisation already exists and only the keyring is locked. Headless use fails with `no TTY available
  for keyring file backend password prompt`; the fix is `GOG_KEYRING_PASSWORD` present in the env file, added
  by the owner (never ask for the value, never echo it), after which `gog sheets append <id> <range>` works as
  that account. Two things still to confirm before promising the update: the sheet must be shared with *that*
  address rather than one you assume has access, and the Sheets API must be enabled on the OAuth client's own
  project — a disabled Sheets API returns 403 naming a project id that need not be the one in
  `GOOGLE_CLOUD_PROJECT`. Offer paste-in CSV as the zero-setup fallback.
  A service account that mints a token but returns `403 The caller does not have permission` is not
  misconfigured — the file simply is not shared with its `client_email` yet; do not go re-enabling APIs on
  that error. Writing more rows than the tab's default 1,000 also needs the grid expanded first, and the
  result must be confirmed by reading the range back rather than trusting the write response. Recipe:
  `references/google-sheets-delivery.md`.

## Support files

- `scripts/alexandria_discover.py` — free discovery sweep; prints provider/capability contracts for a set
  of queries (or CLI args), saves the aggregate JSON, and reports the credit balance.
- `references/alexandria-catalogue.md` — the observed provider map by vertical, the execution shape, and
  the option-name quirks worth knowing before a first call.
- `references/au-entity-enrichment.md` — state-by-state matrix of Australian licence registers (what each
  publishes, and whether phone/email exist at all), the NSW API shape, the boutique-vs-enterprise
  classifier, the aggregator trap in search-driven discovery, and the pre-delivery audit checks.
- `references/google-sheets-delivery.md` — choosing a Sheets credential that survives a refresh, the
  service-account share step and its misleading 403, and the write order (grid expansion, RAW values,
  `userEnteredFormat` mask) plus read-back verification.

## Related

- `undispute-merchant-enrichment-agent` — the merchant-enrichment worker whose "official merchant web"
  evidence leg is a natural consumer of scrape/crawl + policy-change monitoring.
- `amlhive-ai-authority` — AI discoverability and the content side of `llms.txt`.
- `grounded-citations` / `verifying-supplied-briefs` — cite what you actually fetched, from the official
  domain, with the observation time.
