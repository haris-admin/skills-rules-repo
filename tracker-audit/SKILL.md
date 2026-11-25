---
name: tracker-audit
description: Use when auditing a user's tracker, watchlist, or log.
version: 1.0.0
author: mercury
license: MIT
metadata:
  hermes:
    tags: [audit, spreadsheet, watchlist, data-quality, provenance]
    related_skills: [wsl-windows-interop, monitoring-alert-verification, web-data-acquisition]
---

# Auditing a user-maintained tracker

The user asks *"how are we tracking X?"*, *"what did we add recently?"*, *"thought we were doing
weekly updates on these?"* Their tracker — a Google Sheet, a Notion table, a local CSV — is the
claim. Your job is to establish what is real: what is on it, when it was last touched, whether the
numbers reconcile, and whether anything actually maintains it.

## When to Use

- "How are we tracking X?", "what's happening with those ones we added?", "what did we include
  recently?" about a watchlist, price tracker, pipeline log or review log.
- "Thought we were doing weekly/fortnightly updates" — the user believes a cadence exists and it
  visibly stopped.
- The user hands over a Sheet/Doc/Notion URL and expects you to know its contents.
- You just built or inherited a monitoring job for something the user maintains by hand.

## Step 0 — find the artifact before declaring it does not exist

**A private cloud document is invisible to every local search you can run.** Grepping the filesystem,
the cron fleet and the config tree and finding zero references does NOT mean the thing was never
built — it means the artifact lives somewhere you cannot see. Ask for the URL, or check the user's
browser history / Drive, *before* writing a confident "there is no tracker".

Concluding "this was never built" from local evidence alone is the failure this skill exists to
prevent: the fleet held 100+ crons, no script referenced the sheet, and the artefact was still real
and being maintained by the user by hand.

When the user pastes a link, treat that as the source of truth and read it first.

## Step 1 — read it

- Private Google Sheet/Doc with no API credentials: read it through the user's signed-in Chrome.
  Full working recipe (and the dead ends that waste calls) lives in the `wsl-windows-interop` skill as
  `cdp-authenticated-app-read.md`.
- Prefer a **view link** (`anyone with the link can view`) over a browser session for anything that
  must be re-read later: a CDP session expires silently and the next read returns a sign-in page as
  if it were data.
- Capture every tab, not just the first. Trackers routinely keep the watchlist, the criteria and the
  review log in separate tabs, and the review log is where the cadence and the history live.

## Step 2 — verify the date, then date the tracker against it

Anchor today's date to a network `Date` header first; the host clock drifts and every staleness
verdict depends on it. Then compare the tracker's own last entry to that date and say the gap out
loud ("last review 20 Nov, today 25 Nov").

## Step 3 — test the "we're tracking it" claim

Search for the resource ID (sheet ID, doc ID, table name) across `cron/jobs.json`, `scripts/`, and
the config tree. Three outcomes, all reportable:

- **Zero references** — the tracker is maintained by hand. Nothing will ever tell the user it stopped;
  that is why it went quiet. Say this plainly rather than implying a pipeline exists.
- **References but stale output** — a job exists and has been failing or reading an empty source.
- **Live job** — then audit its output, not the tracker.

## Step 4 — reconcile the data against a live source

A tracker that has never disagreed with itself has never been checked. For each row compare the
logged value to a live quote/figure and look at the trailing range:

- **A logged value outside the trailing 3-month range, with no split, is a bad input** — not a gain or
  a loss. Do not compute returns from it, and do not report it as a move.
- **Check for splits before reporting any large percentage move.** An unexplained +100% is a corporate
  action or a stale price far more often than a rally.
- Run `scripts/price_reconcile.py TICKER=LOGGED_PRICE ...` for a fast pass; it fetches the trailing
  range and prints whether each logged price is inside it.
- Prices that do reconcile are worth stating explicitly — it tells the user which rows they can trust.

## Step 5 — look for the rubber stamp

Structural signs that a review log is ceremony rather than review:

- **Every row carries the same verdict** ("Active Accumulate / High Conviction") across every period.
  Nothing is ever downgraded, trimmed or exited.
- **Items missing from the latest period** — the watchlist has N entries, the latest review covers N-3.
- **Duplicated blocks** — the same date appearing twice, usually a copy-paste break.
- **Self-contradicting next-date** — one period's rows pointing at a nearer next-review date than the
  later period's rows, which means the cadence drifted (a tab labelled fortnightly whose entries are
  seven days apart).
- **No provenance column** — no "date added", entry price, conviction or kill trigger, so the user
  cannot answer "what did we add recently" from their own sheet.

Report these as findings with the count ("17 of 17 rows identical", "3 of 8 never reviewed"), not as
vibes.

## Step 6 — report, then offer the engine

Order the reply: what is real (contents, totals, scores) → when it last ran and the gap → what is
broken (bad inputs, missing rows, rubber stamp) → the honest reason it lapsed → the decision needed.

To automate it, the only real question is the **write path**:

1. **View link + local output** — cheapest, robust; reads headless forever, the review lands in the
   chat and a local file for the user to paste.
2. **Apps Script webhook / service account** — real read *and* write into the sheet; one-time setup.
3. **Browser session** — fragile (it expires on a Chrome update), only for interactive one-offs.

Finally, propose the columns the tracker is missing (date added, entry value, kill trigger, last
verified) so the next "what did we add recently" is answerable from the sheet itself.

## Pitfalls

- **Do not conclude a private document does not exist from a 401.** A `401` on the CSV export URL
  proves the sheet is private, nothing more.
- **Do not report a delta you computed against your own fetched baseline when the tracker logs its own
  price.** Compare logged price → live price; a baseline you derived silently differs from the row.
- **Clean up after an export.** Reading via a download leaves numbered duplicates (`data (1).csv` …) in
  the user's Downloads. Dedupe by hash, keep one copy in `~/.hermes/data/<tracker>/`, delete the rest.
- **Snapshot what you read** with its capture time and method, so the next session can diff instead of
  re-deriving.
- **Never quote a tracker's own summary cell as verified** ("avg screening score 8.8/10"). Report it as
  the sheet's claim; recompute only if it is cheap.
