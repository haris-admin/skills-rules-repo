# Evidence map — AMLHive monthly strategy review (verified Aug 2026)

## Cron job registry & outputs

- Job registry: `/home/habib/.hermes/cron/jobs.json` (id → name → schedule). Parse with python3 json.
- Outputs: `/home/habib/.hermes/cron/output/<jobid>_<YYYYMMDD>_<HHMMSS>.txt`
  (latest per job: `ls -t <jobid>_*.txt | head -1`).

| Job id | Name | Schedule | Use for |
|--------|------|----------|---------|
| `f7e6cb145925` | Pluto Weekly Evidence Summary | Fri 15:00 | **RIChest single source** — GSC numbers, blog delivery, version state, AI status, approval gates, recheck dates |
| `756e4e66c320` | Pluto Daily Discovery Health | weekdays 09:00 | homepage/robots/sitemap/llms checks, controlled facts, regulatory calendar |
| `291c2320c81b` | Weekly Search & Content Review | Tue 10:30 | content opportunities, claim registers, social drafts |
| `f1b73c7cd48d` | Weekly AI-Answer Review | Wed 10:30 | AI-answer spot checks (fortnightly full), escalation conditions |
| `7059cc6796d6` | Weekly Metadata/Blog/Social Audit | Thu 11:00 | per-page metadata table, blog freshness inventory, controlled-facts verification |
| `50eea054f911` | Monthly Strategy Review | first Mon 11:00 | this job |
| `4689311b6ad0` | Hourly Production Version Check | hourly | `research_outputs/.version_check/history.jsonl` |
| `b705c3ee3882` | Hourly Marketing-Attribution Probe | :30 hourly | `research_outputs/.attribution_probe/probe_history.jsonl` + `probe_state.json` (total_probes, signups) |
| `4f4dc2487b98` / `6728be78d1bf` / `d52fa74ab6c1` / `be5061d19a5a` | AmLHive AWS Fleet Monitor | 5/11/17/23 | prod health (docker, CW alarms, Sentry) — context only, not discovery |
| `eca044f22146` | AMLHive Daily Probe Summary | 21:45 | probe summary markdown |

## Research outputs layout

`/home/habib/.hermes/research_outputs/`:
- `weekly-reports/weekly-report-*.md` — git-sync reports (NOT SEO evidence; low value)
- `monthly-strategy-review-runlog.md` — SKIPPED/FULL run records (read first, append after)
- `.version_check/history.jsonl`, `.attribution_probe/probe_history.jsonl` + `probe_state.json`
- `synthesis_YYYY-MM-DD.md`, `research_YYYY-MM-DD.json`, `competitor_intel_*.json`,
  `morning-briefing-*.md`, `.performance_tracker/2026-WNN.json`

## Baseline & OpenSpec docs

- `/home/habib/code/amlhive1/docs/seo_geo_keyword_baseline_2026-07-15.md` — GSC seed query table,
  Day-0 spot-check status, priority actions, measurement cadence (Day 7/28/monthly)
- `docs/seo_geo_live_baseline_2026-07-10.md`, `docs/seo_geo_ai_crawler_baseline_2026-07-11.md`
- `openspec/changes/350-post-deadline-discovery-refresh/` — `CLAIM_REGISTER_*.md`,
  `AUDIT_*.md` (severity-tagged stale-copy inventory), design/tasks
- `docs/current_progress.md` — release log (which version shipped what, e.g. C350 in v0.5.68)

## Live spot-check recipes (public checks only — no auth, no login walls)

```bash
curl -s -L --max-time 30 https://amlhive.com.au/ -o /tmp/home.html -w "HTTP %{http_code}\n"
curl -s -L --max-time 30 https://amlhive.com.au/austrac-compliance -o /tmp/ac.html
curl -s -L --max-time 30 https://amlhive.com.au/llms.txt -o /tmp/llms.txt
curl -s -L --max-time 30 https://amlhive.com.au/llms-full.txt -o /tmp/llmsfull.txt
curl -s -L --max-time 30 https://amlhive.com.au/Compliance/compliance-blog -o /tmp/blog.html
```

Greps that catch the classic defects:
- Stale deadline (post 29 Jul 2026): `grep -o -i ".\{60\}29 July.\{60\}" file` — check meta
  descriptions too, not just body ("must apply to enrol by 29 July 2026", "enrol by 29 July")
- Metadata consistency on `/austrac-compliance`: compare `<title>` vs `property="og:title"`
  vs `name="twitter:title"` — all three must match; twitter:title sometimes still carries the
  homepage title (known MEDIUM defect pattern)
- Controlled facts: "Your Virtual Compliance Officer", "14-day free trial", "Reports are never
  auto-submitted"; never "two-week"/"30-day"
- Version: `curl -s https://api.amlhive.com.au/version` → e.g. `{"version":"0.5.74"}`.
  NOTE: `raw.githubusercontent.com/amlhive-tech/amlhive1/dev/.version` returns 404 (private
  repo) — do not treat as an alert; hourly version check reports MATCH via API comparison.

## GSC context (Day-0 baseline, AU filter, 29–30 Jul 2026)

- 33 clicks (all AU), 104 AU impressions, CTR 31.7%, avg position 19.3
- Only brand query `amlhive` converts (pos 1.0, 18 clicks); all 20 non-brand queries zero
  clicks at positions 20–96 (`austrac compliance software` at 96)
- Only 6 URLs ever appeared in AU results over 3 months — none a blog post
- 6 Jul spike = 45% of clicks, rolls off ~3 Aug; Day 7 (~6 Aug) judged on non-brand
  impressions/position, NOT total clicks
