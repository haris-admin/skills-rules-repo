---
name: pluto-monthly-strategy-review
description: "Use when running the first-Monday monthly strategy review cron. Assembles evidence against baseline and recommends ≤3 priorities; distinct from the pluto-monthly-strategy handoff."
version: 1.1.0
tags: [pluto, amlhive, monthly, seo, geo, strategy-review]
---

# Pluto Monthly Strategy Review (operating contract)

Recurring first-Monday cron (`0 11 * * 1`, job id `50eea054f911`; in-job gate
keeps day ≤ 7 — OR-semantics fix applied 01 Sep 2026, see Pitfalls) under the
pluto-amlhive-operating-contract. **Distinct from the `pluto-monthly-strategy` handoff skill**
(Honcho/Mempalace → local executor with ad-spend context) — see Pitfalls.

**Sibling chain (31 Aug 2026):** the Month-End Review (`09d6d950544f`, 1st 00:01) →
Start-of-Month Rule Refresh (`2f4e89762abb`, completion-gated, consumes the month-end
output to refresh rules) forms the monthly bookend; the first-Monday strategy review sits
in the middle of the month. The month-end review's "RULES TO REFRESH" section and this
review's priorities should cross-pollinate — Start-of-Month applies rule/skill/doc refreshes
from month-end evidence; this review supplies strategy priorities. See
`date-gated-crons` skill for the completion-gate mechanism.

## Trigger / window check (do this FIRST)

1. `date +%u` (weekday, Monday=1) and `date +%d` (day of month).
2. Full review only when weekday=1 AND day ∈ 1..7. Otherwise: append a SKIPPED record to
   `~/.hermes/research_outputs/monthly-strategy-review-runlog.md` (date, trigger, why skipped,
   next expected window, escalation note if 2+ consecutive off-window firings) and STOP — no
   evidence gathering, no priorities.
3. Read the runlog first — it carries the prior month's decisions, escalations, and recheck dates.
4. Append a FULL REVIEW record when a full review is delivered.

## Assemble evidence (in order of usefulness)

1. **Weekly Evidence Summary** (Friday job `f7e6cb145925`) — richest single source: GSC numbers,
   blog delivery, version state, AI-answer status, social, approval gates, recheck dates.
2. Weekly Search & Content Review (Tue `291c2320c81b`), AI-Answer Review (Wed `f1b73c7cd48d`,
   fortnightly full), Metadata/Blog/Social Audit (Thu `7059cc6796d6`), Daily Discovery Health
   (weekdays `756e4e66c320`), fleet monitors, daily probe summary — see
   references/evidence-map.md for job IDs, output paths, and spot-check recipes.
3. Baseline docs: `docs/seo_geo_keyword_baseline_2026-07-15.md` (GSC seed queries + Day-0 status),
   `seo_geo_live_baseline_2026-07-10.md`, `seo_geo_ai_crawler_baseline_2026-07-11.md`.
4. Live spot checks (allowed: browse/analyse public sources): homepage, `/austrac-compliance`,
   `llms.txt`, `llms-full.txt`, blog index, and any blog URLs flagged stale. Grep controlled
   facts + stale-deadline strings; compare `<title>` vs `og:title` vs `twitter:title`.
5. Version + attribution probe histories (`research_outputs/.version_check/history.jsonl`,
   `.attribution_probe/probe_history.jsonl`).

## Identify gaps vs baseline

Compare: index coverage (GSC URLs ever seen), query visibility (brand vs non-brand), AI accuracy
(found/conflated/facts_correct — record "unmeasurable" if no API keys), content freshness
(post-regulator-change stale copy), metadata defects. Use measured numbers only; never convert
"not observed" into a ranking claim.

## Recommend ≤3 priorities

Ordering: **current regulator change > stale content > missing intent coverage > technical repair**.

**Escalation override (added 1 Oct 2026):** an unresolved CMS-publish blocker that survives **three consecutive weekly evidence records** jumps to the **top** of the next monthly review regardless of the ordering above — it is a live public defect, not a stale-content item. The record must name the proven one-write fix path (`backend/scripts/migrate_blog_posts.py --mode update`, which patches page + blog index + sitemap lastmod + both llms files in one PATCH — proven 29 Sep 2026) and state exactly what is blocked on whose approval. Worked example: the 29-July-deadline / prohibited "2-week" / expired-offer cluster was live for 6 weeks with correction copy ready 42 days as at 1 Oct 2026.
Each priority must carry: evidence gap (measured), recommended action, expected measurable signal
(bounded — no rank/click promises), recheck date. No ranking shortcuts; no content-for-show.

Format:

```
## Pluto Monthly Strategy — [Month Year]

Priority 1: [Title]
- Evidence gap:
- Recommended action:
- Expected measurable signal:
- Recheck date:

Priority 2: ...
Priority 3: ...
```

Also list: evidence gaps carried forward (measurement blockers, not priorities) and what went
right this month (measured wins). Deliver the review as the final response — the cron delivers it.

## Pitfalls

- **Do NOT confuse with `pluto-monthly-strategy`**: that skill is the Honcho/Mempalace
  intelligence handoff to a local executor job (job token, stdin JSON, SMTP email). This review
  needs none of that — no token, no executor, no email.
- `raw.githubusercontent.com/amlhive-tech/amlhive1/dev/.version` returns 404 (private repo) —
  trust the hourly version check (api.amlhive.com.au/version vs repo), which reports MATCH.
- GSC click spikes can be single-date events (e.g. 6 Jul 2026 = 45% of clicks, rolls off ~3 Aug);
  judge Day-7/28 on **non-brand impressions/position**, not total clicks.
- Copy releases (e.g. C350 v0.5.68) fix static surfaces but do NOT fix metadata tags or CMS blog
  articles — verify those separately (metadata audit items; CMS packets are approval-gated).
- AI-answer direct engine probes are unmeasurable without API keys; record that as a measurement
  gap, never fabricate found/conflated/facts_correct cells.
- Controlled facts to grep live: "Your Virtual Compliance Officer", "14-day free trial",
  "Reports are never auto-submitted" — never "two-week"/"30-day".
- The two 29-July blog articles are the classic stale-deadline trap: check meta descriptions too
  ("must apply to enrol by 29 July 2026"), not just body copy.
- **Cron fires ~8×/month despite `0 11 1-7 * 1`:** Hermes' cron parser uses POSIX **OR semantics**
  between day-of-month and day-of-week — when both are restricted the job fires when EITHER matches,
  i.e. every day 1–7 PLUS every Monday (verified 08-2026: runs 07-20, 07-27, 08-01…08-06). The
  in-job first-Monday gate (weekday=1 AND day ∈ 1..7) already handles this, so off-window runs just
  record SKIPPED — but they waste API calls and risk timeouts. FIX APPLIED 01 Sep 2026 (Start-of-Month rule refresh): schedule.expr is now `0 11 * * 1`
  (Mondays only; gate filters day ≤ 7). Off-window firings eliminated — job now fires ~4-5×/month
  with silent skips. Keep the in-job gate (weekday=1 AND day ∈ 1..7). Verify next_run_at lands on
  the first Monday (2026-09-07) and no longer advances daily.
- **Month-end output location (learned 01 Sep 2026, refined 01 Sep 00:15):** the Month-End job
  (09d6d950544f) writes BOTH the cron output file `cron/output/09d6d950544f/<ts>.md` AND (since the
  00:05 AEST generation) `~/.hermes/research_outputs/month-end-YYYY-MM.md` with an explicit
  `## RULES TO REFRESH` section. CHECK `research_outputs/month-end-YYYY-MM.md` FIRST and verify its
  generation timestamp + RULES TO REFRESH; if absent (monitor race / early partial output), read the
  latest cron output file's `## Response` section instead of deferring blindly.
  **Watch for double-firing:** the completion monitor can trigger Start-of-Month on a NON-canonical
  early month-end run (00:02 firing consumed a 31 Aug 14:35 partial; the canonical 00:05 review
  triggered a second firing at 00:15). If the injected review lacks a RULES TO REFRESH section,
  re-check for a newer month-end output before concluding.
- **Expect a SPURIOUS pre-completion fire every 1st of month at ~00:00 (verified 01 Oct 2026).**
  `month_end_complete_check.py` prints `MONTH_END_COMPLETE <ym>` only once the file exists; on the
  next 1st its output necessarily flips to `NOT_COMPLETE` because the new month's file cannot exist
  before the 00:01 month-end job finishes (~11 min runtime). The monitor fires on ANY output change,
  so Start-of-Month fires ~00:00 — **before the Month-End Review has even been dispatched**
  (01 Oct 2026: this job dispatched 00:00:45, month-end dispatched 00:01:40, `next_run_at` already
  advanced to 01 Nov). The `context_from` injection then carries the PREVIOUS month's review, which
  was already applied last month — the same trap as the 01 Sep double-fire.
  **Rule:** on a 1st-of-month fire before ~00:15, check `ls ~/.hermes/research_outputs/month-end-<prev-month>.md`
  (fall back to the newest `cron/output/09d6d950544f/*.md` `## Response`). If it is absent, append a
  DEFERRED record to the runlog and STOP — never derive refreshes from the stale injected review.
  The gate re-evaluates every 15 min (00:00–03:45) and fires legitimately once the file lands; if no
  such firing happens, the month-end review itself failed and needs escalation.
  **Archive caveat:** the cleanup cron moves month-end files out of `research_outputs` (Aug 2026's is
  now at `~/.hermes/archive/research/2026/09/month-end-2026-08.md`) — absence there is expected for
  older months, so never treat a missing older file as a defect in its own right.
- **Watch for timeouts:** the 08-05 off-window run hit `TimeoutError: idle for 603s (limit 600s)`
  waiting for a non-streaming API response and recorded nothing. A timeout on the real first-Monday
  run would silently lose the monthly review — check last_status/executions.db if a month is missing.

See references/evidence-map.md for the full job-ID → output mapping and spot-check recipes.
