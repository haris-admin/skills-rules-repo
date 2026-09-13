# Phase 7: Weekly Digest — Full Workflow

Full detail behind the Phase 7 weekly digest summary in `SKILL.md`
(weekend cross-topic synthesis run).

~~Run once per week via cron `3cde85223e18` (Sunday 23:00 AEST).~~ **PRUNED June 13, 2026** — superseded by the Saturday Weekly Review (`7d24b37a03f2`, Sat 6AM) which covers cross-topic synthesis with performance data. Uses DeepSeek v4 Pro for reliability.

## Workflow

1. **Query the mempalace** for recent topics and status:
   ```bash
   /home/habib/.hermes/venv/bin/python3 ~/.hermes/scripts/gumby_mempalace_query.py --status
   ```
2. **Load all research JSONs** from the past 7 days via `search_files(target='files', pattern='research_*.json', path='/home/habib/.hermes/research_outputs/')`, then filter by date.
3. **Cross-day deduplication (CRITICAL — new step):** Before synthesizing, scan all loaded JSONs for duplicate topics across days. A topic like CGT may appear on 5 separate days (as happened June 1–7, 2026). When the same topic repeats:
   - **Deduplicate findings:** If a finding's title or topic is substantively the same across days, consolidate into a single weekly insight with the strongest available confidence across all days.
   - **Signal balance aggregation:** Do NOT use a single day's `meta.signal_balance` as the week's verdict. Aggregate counts across all days for that topic. If `signal_balance` is structured per-dimension (e.g., `pro_compliance: 6, burden_concern: 2`), sum the counts. Re-check the 5:1 threshold against the aggregate, not any single day's snapshot.
   - **Cross-day weight normalization:** A finding that appeared in 5 daily JSONs is not 5× more important than one that appeared once — it may just mean the topic has sustained media coverage. Weight by novelty and portfolio impact, not frequency alone.
   - **Mempalace topic vs file-level topic mismatch:** The `recent_topics` from `gumby_mempalace_query.py --status` may use different labels than the actual `topic` field in the daily JSONs (verified June 7, 2026: mempalace returned "EU AI Act 2026" but no daily JSON had that exact topic). Always read the actual file content — do not rely solely on the mempalace topic list for coverage completeness.
4. **Synthesize across topics** — produce:
   - **Top 5 insights** across all research (1-2 sentences each with "Why it matters to Haris" — map to a portfolio project)
   - **Emerging trends** table (trend, momentum: accelerating/building, horizon: 0-3/3-6/6-12 months, portfolio impact)
   - **Regulatory watch** table (deadline, event, jurisdiction, urgency: critical/high/monitor)
   - **Recommended focus areas** for the coming week (area, rationale, priority: immediate/high/medium, project)
5. **Feed back to mempalace** — wrap all synthesized items as `findings` in the JSON:
   ```bash
   /home/habib/.hermes/venv/bin/python3 /home/habib/.hermes/scripts/pluto_mempalace_feeder.py \
     --input /path/to/weekly_digest_YYYY-MM-DD.json \
     --topic "Weekly Research Digest — Week of ..." \
     --tags "weekly,digest,..." \
     --source "pluto_weekly"
   ```
6. **Gumby handoff (SKIP for weekly digest):** The `gumby-brief-input.md` is for daily briefings only. For the weekly digest, do NOT write a Gumby handoff — the weekly digest JSON + mempalace feed are the authoritative outputs. Phase 5's Gumby handoff is already marked optional for daily briefings; it is even less relevant on a weekend run with no subsequent daily pipeline.

## Digest JSON format

The feeder script requires a `findings` array at the top level. Each finding follows the standard schema (`title`, `content`, `confidence`, `type`). Synthesized items like top insights, emerging trends, regulatory watch items, and focus areas all become `findings` entries — do NOT use keys like `top_insights`, `trends`, or `regulatory_watch` at the top level. See Pitfalls (`references/pitfalls-and-incident-log.md`). Use `type: "opportunity"` for recommended focus areas to distinguish them from regulatory findings.

**Output file:** `~/.hermes/research_outputs/weekly_digest_YYYY-MM-DD.json`

**Key difference from daily research:** The weekly digest re-synthesizes already-stored findings into cross-topic intelligence. It does not perform new web research — it produces meta-analysis. Every finding in the digest is a synthesis of multiple daily findings, so `confidence` should reflect the weight of corroborating sources (typically `high` when backed by 2+ daily findings from different sources).
