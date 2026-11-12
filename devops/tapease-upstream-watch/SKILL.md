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
- **Cron:** `★ TAPEase upstream watch — Clover + Oxygen Global (every 2h → group)`, job `e68234a738eb`,
  `0 */2 * * *`, `no_agent: true`, script `upstream_watch.py`,
  `deliver=telegram:-5552363922` (the TapeEase announcements group; **not** the fleet-monitor group
  `-1003834479227`), `failure_deliver` the same.
- **State:** `~/.hermes/state/upstream-watch-state.json` (baselines, failure streaks, notified flags).
  `UW_STATE=<path>` overrides it for tests; `--dry-run` prints without writing or emailing;
  `--no-email` writes state but suppresses mail; `--test <email>` sends a delivery test.
- **Email:** `help@tapease.com.au`, `shoaib.habib@a2square.com.au`, `hhsiddiqui@gmail.com`
  (only when there is news or a standing problem). The group post is built from the same change list
  with a per-source line cap, so the two views cannot drift.

## Sources

- Clover announcements — `docs.clover.com/dev/docs/release-notes-announcements` (static HTML, hashed)
- Clover Android / Clover Go SDK release notes — `docs.clover.com/dev/docs/androidclover-go-sdk-release-notes`
- Clover status — `status.clover.com/api/v2/summary.json`, fingerprinted on incident/maintenance IDs and
  non-operational components only (the payload carries a changing timestamp)
- Oxygen Global availability — `https://oxygen-global.com/`: HTTP 200 **and** the marker `Oxygen Global`
  in the body (the site is Cloudflare-fronted, so a 200 alone proves only that the edge answered)
- Oxygen Global content — WordPress REST API: `/wp-json/wp/v2/posts` and `/wp-json/wp/v2/pages` with
  `_fields=id,date,modified,link,title(,slug)`; fingerprint over ids + `modified` stamps, so reports name
  the actual post/page that changed

## Adding a source

1. Static HTML → append to `HTML_SOURCES` (key, label, url). Must be server-rendered; prove byte-stability
   by fetching twice and comparing hashes before trusting the hash.
2. JSON/status feed → fingerprint IDs and statuses, never the payload (timestamps make it fire every tick).
3. WordPress/SaaS content → prefer the platform's own REST API over hashing rendered HTML; rendered pages
   are frequently client-side shells that hash to the same constant forever.
4. Availability → add to `AVAILABILITY` with a marker string that cannot appear on a parked or empty page.
5. Then re-run `--dry-run` and confirm the new source shows as **armed** (first run baselines silently).

## Pitfalls

- **`docs.clover.com/changelog` is deliberately excluded.** Its entries are client-rendered — the static
  HTML is ~950 characters of navigation, so no hash over it can ever move when an entry is posted. Use the
  announcements page and the SDK release notes instead.
- **A website change is not automatically an announcement.** The Oxygen posts/pages API reports edits
  (copy, pricing, product pages) as well as news; label the section by what moved and let the reader judge.
- **Alert once, not every tick.** A source fetch failure is silent for the first run and announces only at
  the second consecutive failure (≈4h at a 2h cadence), then stays quiet until it recovers — recovery is
  reported once. Never let a transient Cloudflare blip post to the group.
- **Write the state file on EVERY run, including quiet ones.** The first version returned before writing,
  so failure streaks reset each tick and the threshold was unreachable. A watermark only written when
  something is reported never advances.
- **An unchanged fingerprint across a visible site change means the capture is wrong**, not that the site
  is quiet: the page is client-rendered, JS-gated or blocked. Measure the normalised text length before
  trusting a forever-green hash.
- **Availability transition gating, not per-run alarm.** Oxygen availability alerts on up↔down only, so a
  sustained outage is one message (plus the recovery) rather than a message every two hours.
- **Proof harness before trusting it:** `scripts/test_upstream_watch.sh` (failure → threshold → silence →
  recovery) and `scripts/test_change_paths.sh` (tampered state proves each detector fires and that a
  reported change is consumed exactly once). Both run against a temp `UW_STATE` copy, so they never touch
  the production baseline.
