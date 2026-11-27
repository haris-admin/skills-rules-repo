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
   **Access: `curl` gets 403 on the `/p/…` URLs and the `/archive` + `/t/os-weekly` pages expose no post
   links — fetch the issue directly with `web_extract` on `https://overnightsuccess.vc/p/<N>th-<month>-<year>`.**
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
- **Government co-investment is not a VC round.** ARENA (Driving the Nation) and Innovation Victoria
  (University Innovation Platform) cheques arrive as grant/co-investment and land in the funding feed —
  separate "equity VC" from "government" in the digest total rather than counting them as rounds.
  Also expect currency splits on the same deal (MP Space: A$23M = US$16M, so Dealroom/Tech in Asia
  report "$16M" — quote the AUD figure from the primary article).
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
- **Regtech/AML items that "look current" in undated search hits are usually months old.** Personr's
  FundWA follow-on is Oct 2025 and Legora's acquisition of Melbourne regtech Graceview is May 2026 —
  both surface as fresh in aggregator/undated hits. Confirm the primary announcement date before
  flagging, and treat the round-up feeds (Startup Daily RSS) as the in-window test.
- **Regtech capital often arrives as a LISTED raise that never enters VC round-ups.** ASX small-caps
  raise by placement + entitlement offer (e.g. Dataworks Group DWG, A$3.0M placement + 1-for-10
  entitlement, Sep–Oct 2026, for its BetStop/BetGuard government regtech platforms). Check ASX
  announcements for regtech names during the window or the 🚩 block misses the only regtech capital
  event of a quiet week.
- **A quiet week is a real finding.** Micro-rounds (A$0.5–3M) are often the only new deals; say so
  rather than padding with last week's larger raises (label those clearly as prior week).
- **The Startup Daily funding RSS caps at 10 items and lags the homepage by hours.** On a Friday cron it can
  show only one in-window deal; when the feed looks empty, cross-check the site homepage (`/`) and
  `dynamicbusiness.com`/`finsmes` hits, which surface rounds the funding tag has not picked up yet.
- **Non-VC "raises" arrive as launch announcements, not funding stories.** ANFF-C Gate 1 pre-seed awards
  (anff.org.au/news), Innovation Victoria pre-seeds inside university spinout launches (e.g. Microcomb),
  and ARENA grants are dated, in-window and real, but appear only via `web_search` on the topic — they
  never enter the Startup Daily funding feed. Classify them separately from equity VC.
- **Capital Brief and fintechnews.au topic pages can sit a week stale** even when articles exist; their
  listing order is not a reliable in-window test. Date each article from its own byline before citing.
- **Sector aggregators resurface year-old raises with fresh-looking URLs.** Plexus's "$6M raise"
  (legaltech-talk) is May 2025 and reads as current in an undated listing — its own byline is the test.
- **Search hits can be a year stale.** A generic query for an in-window deal can return the *same-named
  round-up from the prior year* as a top hit (e.g. a "Cheque-in … to end October" article dated 31 Oct 2025
  surfacing during an Oct 2026 window, full of 2025 deals). Always read the article's own dateline before
  reusing it — the slug/Google snippet carries no year.
- **Regtech/AML supply signal ≠ equity round.** Demand is driven by Tranche 2 AML/CTF (live 1 Jul 2026,
  ~100k entities: real estate, legal, accounting, precious metals, gaming) and shows up as vendor
  partnerships, club/enterprise signings, M&A and follow-on seed — not necessarily a fresh round.

- **Verified-round trackers beat the feeds for micro-rounds.** `trymatchbox.com/news` lists dated AU rounds with
  investors and `leadprysm.com/news` carries global sub-$5M rounds including AU — between them they surface deals
  Startup Daily never tags (COUNT NZ, Mulga, RespirAq). Both mis-record currency though (Matchbox logged Remedy
  Robotics as "A$62M" when it was US$62M/A$92M), so take the amount from the press release.
- **Publication date ≠ announcement date, by up to five days.** Provectus Algae's extension appeared in SmartCompany's
  13 Nov round-up, QIC released 15 Nov, Business Wire 17 Nov, Startup Daily 15 Nov. For borderline cases use the
  company/QIC/Business Wire release date, not the aggregator's.
- **Same-name companies collide across the border and the ASX.** NZ's COUNT raised a US$6.5M seed (KBF/GD1) the same
  month ASX:CUP Count Limited did a A$25M placement — unrelated firms. Check the entity before merging a hit.
- **Capital Brief drops the currency unit.** "Remedy Robotics raises $62 million" is US$62M; the figure only becomes
  A$92M by reading Startup Daily or the release. Never carry a bare "$" from Capital Brief into an AUD total.
- **Tracxn's report URLs rot and come back.** The H1 2026 semi-annual page 404'd in Nov but resolves again at the
  full slug (`/d/insights/market-reports/australia-tech-semi-annual-funding-report-h1-2026/__MyLDaB…`) — if the short
  URL fails, `web_search "Tracxn Australia tech funding report 2026"` to recover the live slug. Keep the figures in
  `references/` either way.
- **Tracxn cumulative "through <month>" figures are as unstable as its geography page** (e.g. "A$5.58B / 162 rounds
  through October 2026"). Quote only the dated semi-annual/quarterly report, never a rolling YTD.

## Output shape

- Header line with the week-ending date; then an **input check** block if a brief/digest was supplied
  (verify its numbers before reuse — see `verifying-supplied-briefs`).
- 🚩 flags block first (regtech / AML / fintech, incl. M&A), then new rounds, then benchmarks, then a
  one-line read-through. Keep under ~450 words, no tables, short lines.

## References

- `references/sources-and-benchmarks.md` — live URLs and the verified 2025/FY26 benchmark figures.

## Verification status

Last full run: 27 Nov 2026 (Fri cron, window 21–27 Nov). In-window sweep = Startup Daily funding RSS + main RSS
(Overnight Success `/p/<N>th-<month>-<year>`, previous Saturday's issue is current), SmartCompany tag pages,
fintechnews.au funding, trymatchbox.com/news, leadprysm.com/news, Cut Through insights, ASX announcement search for
regtech placements. Notes from this run: SmartCompany's weekly round-up lags — it had not published the current
week's wrap by Fri 08:00, so SD's funding RSS was the sole inventory; the Tracxn H1 report URL resolved again (see
pitfalls); a web_search for AU regtech/AML rounds in-window returns only overseas deals (NABU, Arva AI) — treat
those as out-of-scope and do not pad the 🚩 block with them.
