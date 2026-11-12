---
name: tapease-upstream-watch
description: Use when monitoring Clover or Oxygen Global sites.
version: 1.0.0
author: Mercury
license: MIT
category: devops
metadata:
  hermes:
    tags: [monitoring, tapease, clover, oxygen-global, vendor-upstream]
    related_skills: [monitoring-alert-verification, tapease-daily-settlement, competitor-news-monitor]
---

# TAPEase upstream watch (Clover + Oxygen Global)

TAPEase depends on two vendors whose changes arrive as silence: **Clover** (terminals, Android/Clover Go
SDK, status page) and **Oxygen Global** (prepaid/wallet platform, WordPress site). Neither pushes
announcements or outages to us, so a platform deadline or a docs outage surfaces only when a terminal
misbehaves.

One script watches all of it and reports **only when something moved**.

## When to Use

- "Is Clover announcing anything?", "did Clover change their SDK/platform notes?", "is Clover down?"
- "Watch oxygen-global.com for changes / availability"
- Adding, fixing or re-baselining a TAPEase vendor-upstream source, or explaining why the group has
  been quiet (silence = nothing moved, not a dead monitor — verify with `--dry-run`).
- Anything about the group post that starts `🔴 TAPEase upstream watch`.

Not for: TAPEase's own availability (that is `tapease-daily-settlement` / the TapEase fleet monitor) or
competitor news (`competitor-news-monitor`).

## What runs

- **Script:** `~/.hermes/scripts/upstream_watch.py` (the only engine — `clover_updates_watch.py` is
  deprecated; do not add logic to it).
- **Cron:** `★ TAPEase upstream watch — 16:00 Sydney daily (Clover + Oxygen → group)`, job `e68234a738eb`,
  `0 16 * * *`, `no_agent: true`, script `upstream_watch.py`,
  `deliver=telegram:-5552363922` (the TapeEase announcements group; **not** the fleet-monitor group
  `-1003834479227`), `failure_deliver` the same.
- **State:** `~/.hermes/state/upstream-watch-state.json` (baselines, failure streaks, notified flags).
  `UW_STATE=<path>` overrides it for tests; `--dry-run` prints without writing or emailing;
  `--no-email` writes state but suppresses mail; `--test <email>` sends a delivery test.
- **Email:** `help@tapease.com.au`, `shoaib.habib@a2square.com.au`, `hhsiddiqui@gmail.com`
  (only when there is news or a standing problem). The group post is built from the same change list
  with a per-source line cap, so the two views cannot drift.

## Sources

- Clover announcements — `docs.clover.com/dev/docs/release-notes-announcements`.md`, clean and dated
- Clover Android / Clover Go SDK release notes — `…/androidclover-go-sdk-release-notes.md`
- Clover announcement index — the page's nav block between the `RELEASE NOTES` and `RESOURCES`
  markers, captured as a line set (the index body lags the nav, so this is what catches a brand-new
  entry)
- Clover status — `status.clover.com/api/v2/summary.json`, fingerprinted on incident/maintenance IDs and
  non-operational components only (the payload carries a changing timestamp)
- Oxygen Global availability — `https://oxygen-global.com/`: HTTP 200 **and** the marker `Oxygen Global`
  in the body (the site is Cloudflare-fronted, so a 200 alone proves only that the edge answered)
- Oxygen Global content — WordPress REST API: `/wp-json/wp/v2/posts` and `/wp-json/wp/v2/pages` with
  `_fields=id,date,modified,link,title(,slug)`; fingerprint over ids + `modified` stamps, so reports name
  the actual post/page that changed
- TapeEase website + www — `tapease.com.au` / `www.tapease.com.au` (marker `eftpos`)
- TapeEase API — `https://api.tapease.com.au/` is a JSON health route (`status`, `version`, `environment`);
  assert the FIELDS and quote the version, so a stale deploy is visible
- touchSMS website — `https://touchsms.com.au/` → www (marker `touchsms`)
- AWS security bulletins — `aws.amazon.com/security/security-bulletins/rss/feed/`, filtered to
  `\brds\b | \baurora\b | \blambda\b | \bpostgres(ql)?\b`
- AWS What's New — `aws.amazon.com/about-aws/whats-new/recent/feed/`, same filter (upgrades, 🆕)
- AWS service health — `status.aws.amazon.com/rss/rds-ap-southeast-2.rss` and `…/lambda-ap-southeast-2.rss`

## Adding a source

1. Static HTML → append to `HTML_SOURCES` (key, label, url). Must be server-rendered; prove byte-stability
   by fetching twice and comparing hashes before trusting the hash.
2. JSON/status feed → fingerprint IDs and statuses, never the payload (timestamps make it fire every tick).
3. WordPress/SaaS content → prefer the platform's own REST API over hashing rendered HTML; rendered pages
   are frequently client-side shells that hash to the same constant forever.
4. Availability → add to `AVAILABILITY` with a marker string that cannot appear on a parked or empty page.
5. Then re-run `--dry-run` and confirm the new source shows as **armed** (first run baselines silently).

## Pitfalls

- **Clover docs are ReadMe.io — every page has a markdown twin: append `.md` to the URL.** It is
  server-rendered, byte-stable and carries `updatedAt` in its frontmatter, so a diff reads as content
  instead of 20k characters of sidebar navigation. The script asserts a `# ` title in the first 2k chars;
  a non-markdown response is a PROBLEM, never a change. This also fixes the old reason the plain
  `/changelog` HTML was excluded (client-rendered entries) — the `.md` twin has them.
- **The announcements INDEX body lags the sidebar.** Two live entries ("Clover billing system upgrade",
  "Clover Compact … Canada") were linked from the nav while absent from the index page's own list, so an
  index-only capture would have missed them. Watch both: `.md` body for content edits, nav line set for
  new entries.
- **A website change is not automatically an announcement.** The Oxygen posts/pages API reports edits
  (copy, pricing, product pages) as well as news; label the section by what moved and let the reader judge.
- **Alert once, not every tick.** A source fetch failure is silent for the first run and announces only at
  the second consecutive failure (≈2h at an hourly cadence), then stays quiet until it recovers — recovery is
  reported once. Never let a transient Cloudflare blip post to the group.
- **Write the state file on EVERY run, including quiet ones.** The first version returned before writing,
  so failure streaks reset each tick and the threshold was unreachable. A watermark only written when
  something is reported never advances.
- **An unchanged fingerprint across a visible site change means the capture is wrong**, not that the site
  is quiet: the page is client-rendered, JS-gated or blocked. Measure the normalised text length before
  trusting a forever-green hash.
- **Availability transition gating, not per-run alarm.** Oxygen availability alerts on up↔down only, so a
  sustained outage is one message (plus the recovery) rather than a message every hour.
- **AWS status feeds are EMPTY when healthy** — 0 items is the good state, so liveness is asserted on the
  parsed channel title, never on item count. A content feed (bulletins, What's New) returning 0 items IS a
  failure and must raise.
- **Filter feeds on WORD boundaries.** `'rds'` as a substring matches "records", "towards", "standards";
  the filter uses `\brds\b`. Same class of bug as alerting on a generic word inside an identifier.
- **A keyword hit is not applicability.** The bulletins feed matched "Babelfish for Aurora PostgreSQL" on
  `aurora`/`postgres`, but Babelfish is AWS's SQL Server emulation layer — TAPEase runs plain PostgreSQL, so
  that is a keyword match, not an exposure. Report it, label the applicability question, never escalate to
  "you are vulnerable" from the title alone.
- **touchSMS's status page is not monitorable from outside.** `status.touchsms.com.au` is a Pulsetic SPA
  (client-rendered, no public JSON API on the usual paths). Monitor the site itself and record incident
  visibility as a gap rather than hashing the SPA shell and calling it covered.
- **One engine, one job.** Every new target is a new entry in `AVAILABILITY` / `FEEDS` / `MD_SOURCES` — never
  a second cron job on the same cadence, which would double every alert.
- **Proof harness before trusting it:** `scripts/test_upstream_watch.sh` (failure → threshold → silence →
  recovery) and `scripts/test_change_paths.sh` (tampered state proves each detector fires and that a
  reported change is consumed exactly once). Both run against a temp `UW_STATE` copy, so they never touch
  the production baseline.
