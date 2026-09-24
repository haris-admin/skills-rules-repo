---
name: au-vc-funding-radar
description: "Use when producing the weekly AU/ANZ VC funding radar."
platforms: [linux, macos, windows]
---

# Weekly AU VC funding radar

Produce a 2-minute, Telegram-ready digest of new Australian/ANZ venture rounds, with
regtech / AML / fintech deals flagged. Weekly cadence; the reporting window is the current
AEST week (Sat–Fri), so anchor on the current date rather than on the supplied brief.

## Source ladder (cheapest signal first)

1. **Overnight Success weekly** (`overnightsuccess.vc/p/<N>th-<month>-<year>`) — the single best
   ANZ round-up; usually published Sat, so on a Friday cron the *previous* Saturday's issue is current.
   Its "Startup Retro" section is the deal list; headlines carry policy/fund news.
2. **Startup Daily** funding topic (`startupdaily.net/topic/funding/`) — canonical per-deal articles
   with round size, lead investor and follow-ons. **Fastest dated inventory: the funding-only feed
   `curl -s https://www.startupdaily.net/topic/funding/feed/ | grep -E "<title>|<pubDate>"`** — gives
   title+date for the last ~10 rounds, so you can tell in-window deals from last week's at a glance
   (the HTML page cache can lag a day behind the feed).
3. **SmartCompany** weekly "N ANZ startups that raised $X this week" — aggregates Startup Daily; use
   it to check nothing was missed, and to get NZ deals.
4. **Cut Through Venture** (`cutthrough.com/insights/...`) — quarterly + sector reports (fintech,
   state of funding). **Triple Bubble × Cut Through** publishes the Fintech Funding Report (FY basis).
5. **Tracxn** semi-annual/quarterly report pages for headline totals — but see pitfalls.
6. **Capital Brief / AFR / fintechnews.au / Dealroom** — for rounds covered nowhere else and for M&A.

## Pitfalls (learned the hard way)

- **Tracxn's geography pages contradict its own reports.** The Australia geo page has shown both
  "till June 2026: US$1.77B / 82 rounds" and "till August 2026: US$4.57B / 119 rounds" — an impossible
  jump. Never quote a Tracxn YTD figure; quote the dated semi-annual/quarterly report instead.
- **"$5.48B" is calendar 2025, not FY25.** Cut Through/Folklore's State of Australian Startup Funding
  figure (A$5.48B, 390 deals, +31%) covers Jan–Dec 2025. Cut Through's *FY* fintech baseline is
  different (FY25 fintech = A$730M vs FY26 A$1.73B, +137%). Don't mix FY and CY labels.
- **"Zero IPOs" holds only for VC-backed tech.** Tracxn reports zero tech IPOs in H1 2026, while its
  own geography page counts 11 Australian IPOs Jan–Jul 2026 across all sectors (i.e. small-caps listing).
- **Tracxn (US$) and Cut Through (A$) H1 totals disagree** (US$1.9B vs ~A$3.5B) because of methodology
  and franchise-vs-announced-deal scope. State both and label the method; never average them.
- **Aggregators carry stale dates.** Datapile/Dealroom quarterly lists (e.g. "Q3 2026: Pay.com.au $39M
  Series E") include deals that closed a month earlier (Pay.com.au = 25 Aug 2026), and Dealroom
  re-dates items by month only. Always confirm the announcement date in the primary per-deal article
  before calling a round "this week".
- **A quiet week is a real finding.** Micro-rounds (A$0.5–3M) are often the only new deals; say so
  rather than padding with last week's larger raises (label those clearly as prior week).
- **Regtech/AML supply signal ≠ equity round.** Demand is driven by Tranche 2 AML/CTF (live 1 Jul 2026,
  ~100k entities: real estate, legal, accounting, precious metals, gaming) and shows up as vendor
  partnerships, club/enterprise signings, M&A and follow-on seed — not necessarily a fresh round.

## Output shape

- Header line with the week-ending date; then an **input check** block if a brief/digest was supplied
  (verify its numbers before reuse — see `verifying-supplied-briefs`).
- 🚩 flags block first (regtech / AML / fintech, incl. M&A), then new rounds, then benchmarks, then a
  one-line read-through. Keep under ~450 words, no tables, short lines.

## References

- `references/sources-and-benchmarks.md` — live URLs and the verified 2025/FY26 benchmark figures.
