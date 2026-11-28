# ABR JSON API — name search + entity detail (GUID)

Use when you must go **from a business name to an ABN** (identity resolution), not just validate an
ABN you already hold. The HTML `/ABN/View?abn=` path in SKILL.md step 2 needs no credential and is
still the right choice for a single known ABN; the JSON API is what makes name search possible.

## Endpoints

```
GET https://abr.business.gov.au/json/MatchingNames.aspx?name=<urlencoded>&maxResults=<1-25>&guid=<ABN_LOOKUP_GUID>
GET https://abr.business.gov.au/json/AbnDetails.aspx?abn=<11 digits>&guid=<GUID>
GET https://abr.business.gov.au/json/AbnByAcn.aspx?acn=<9 digits>&guid=<GUID>
```

`ABN_LOOKUP_GUID` is a free per-user GUID from abr.business.gov.au; in this fleet it lives in
`/mnt/c/Users/habib/.hermes/.env` and is read from there — never printed.

## Parsing traps (each one silently corrupts results)

- **Responses are JSONP-wrapped**: `callback({...})`. Strip with
  `re.search(r"\((.*)\)\s*$", raw, re.S)` before `json.loads`; an "invalid JSON" error is almost
  always the wrapper.
- **`BusinessName` is a list on some records and a bare string on others** — normalise
  (`[x] if isinstance(x, str) else x`) before iterating, or the script dies on one record.
- **`MatchingNames` gives `AbnStatus` as a numeric code string** (`0000000001` …), not `Active`/
  `Cancelled`; the readable status comes from `AbnDetails.AbnStatus`. Never classify liveness from
the search response.
- **`Score` is search relevance 0–100, not confidence** in identity. Do not feed it into any
  scoring rubric.
- **`IsCurrent` describes the name record, not the entity** — a current name can belong to a
  cancelled ABN.
- One ABN appears under several names (entity, business, trading). Dedupe on `(abn, name)` and
group by ABN before scoring.

## Efficient sweep order

1. Control query first (`name=Bunnings`) — proves the GUID is accepted. An invalid GUID and a real
   zero-hit return look identical otherwise.
2. `MatchingNames` for every name variant (10 hits each is enough), collect into a dict keyed by
   `(abn, name)`, `time.sleep(0.4)` between calls.
3. `AbnDetails` only for survivors — never for every raw hit.
4. Treat a hit in a **different trade** as a collision, not a candidate (gift hampers, barbershops,
   florists and photography studios dominate name-word searches). Establish the trade from the
   entity's own site before scoring.
5. Keep cancelled/deregistered entities as `excluded` with the reason, not silently dropped — the
   user needs to see the near-misses.

## Jurisdiction

Same rule as the main skill: a foreign same-name business is worthless as a match. Check the
foreign register for the exact legal name (UK: `find-and-update.company-information.service.gov.uk/
company/<number>` — status, incorporation date, registered office, **SIC codes**; 47599 = retail of
furniture/lighting). Site-side corroboration is cheap: currency/region selector, foreign returns
address, EU cooling-off clause. Report the lookup as "no Australian match / overseas only" with the
collisions listed — never submit an overseas entity as an Australian one.
