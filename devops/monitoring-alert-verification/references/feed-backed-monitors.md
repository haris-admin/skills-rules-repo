# Feed-Backed Monitors — Liveness, Recency, Precision

Applies when a checker's input is a **search/news feed** rather than a store you own: competitor
watches, brand-visibility sweeps, headline scans, listing probes. The store-backed rules in the
parent skill still hold; these are the additions that only bite on feed inputs.

## 1. Push recency into the QUERY, not only the post-filter

A company-name query with no recency operator returns **relevance-ranked evergreen** results. A
monitor that then filters to a 4-day window discards every one of them and reports a clean zero.

- Google News RSS: `https://news.google.com/rss/search?q=<urlencoded>&hl=en-AU&gl=AU&ceid=AU:en`,
  with the window appended inside the query text — `when:7d` (also `when:1d`, `when:30d`).
- Keep the downstream date filter as a **second** gate: it covers a provider that ignores the
  operator, but it is not the mechanism doing the work.
- Quote the name and add one anchor keyword (`"<name>" compliance`) to raise source precision.
- Same principle on any provider: the API's own sort/filter parameter beats client-side trimming,
  because client-side trimming cannot recover results the API never returned.

## 2. Count the INPUT, not just the findings

Persist three counters per source per run — `items_seen`, `items_in_window`, `hits` — and decide
from all three:

| State | Meaning | Correct output |
|---|---|---|
| `items_seen == 0` | fetch failed / empty feed | coverage FAILURE |
| `items_seen > 0`, `items_in_window == 0` | the feed returned nothing fresh (stale query or missing recency operator) | coverage FAILURE — the instrument is dead, not the world quiet |
| `items_in_window > 0`, `hits == 0` | genuinely nothing matched | empty state (may stay silent) |

A zero that never asserted its input was live is the same bug class as a fake PASS: it reads as
evidence of quiet when it is evidence of nothing at all.

## 3. Precision gate on name matching

A quoted brand query **still** returns coincidences. Count a mention only when BOTH hold:

1. the full entity name — or the base before any parenthesis, e.g. `Square` from `Square (Block)` —
   appears as a phrase, and
2. at least one category keyword for that entity's domain appears in the same text.

Bare token matching on a multi-word name matches unrelated businesses (a restaurant that happens
to share a vendor's name; a street-festival story containing two ordinary words from a company's
name). Keep a small per-category keyword map rather than a global stop-word list.

## 4. Rotate a large watchlist

Querying every tracked name in one run makes the run grow without bound. Query a fixed slice per
tick and persist the next index in a small state file, so full coverage happens every
`ceil(N / slice)` runs while each run stays bounded. Report the rotation position in the run's
diagnostics so a name's absence from this run is explicable.

## 5. Re-verify the feed shape periodically

Feeds change markup and operators are silently ignored. Keep one cheap assertion ("did we get
items at all?") and one on-topic check ("is the first returned headline plausibly about the
query?") — a feed that answers 200 with parseable but irrelevant blocks is indistinguishable
from success without that check.
