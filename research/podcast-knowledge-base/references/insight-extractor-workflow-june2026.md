# Podcast Insight Extractor — Full Workflow

> **Status: PROVEN** — 2 consecutive production cron runs (Jun 7–8, 2026). Cron ID: `67319a9b2606`, 05:02 AM AEST daily.
> **Skill proposal:** `podcast-insight-extractor` — qualifies for skill creation after 2/2 runs.

## Pipeline Position

```
00:35  🎙️ Podcast Ingestion (fabab82f804a)     → Supabase (new transcripts)
05:02  🧠 Podcast Insight Extractor (67319a9b2606) → podcast_insights.json + .md
05:05  🔬 Morning Research (b0de180cec84)        → reads podcast_insights for enrichment
05:10  🔗 Cross-Chamber Synthesis (ddceef1f9e5b) → picks up podcast_insights.json
06:45  📱 LinkedIn Ideas (ee4e48300826)           → uses podcast frameworks for posts
```

The insight extractor sits between ingestion and synthesis, enriching both research and content pipelines — a **dual-consumer** pattern.

## Execution Steps

### 1. Query Supabase for recent episodes
```sql
SELECT * FROM podcast_kb.episodes 
WHERE ingested_at > NOW() - INTERVAL '3 days'
ORDER BY published_date DESC;
```
Typically returns 15 episodes across 5–7 shows.

### 2. Extract frameworks per episode
For each episode with a transcript, run Claude extraction:
- **Key frameworks** — reusable mental models (e.g., "Discovery Non-Deterministic; Payment Deterministic")
- **Explanation** — 2-3 sentence summary with source attribution
- **Quote of the day** — the most quotable line (4-5 selected per batch)

### 3. Map to Haris's Portfolio (7 projects)
Every episode gets mapped to at least 1 portfolio project:

| Episode Theme | Portfolio Project | Relevance |
|--------------|-------------------|-----------|
| Autonomous agent payments / Stripe | PayLicence / PSP | Direct — payment infrastructure for AI agents |
| Multi-agent architecture / OpenClaw velocity | Internal Ops / Fleet | Validates agent fleet architecture |
| AI budget reckoning / cloud cost | CloudProof | Counter-cyclical — cost governance play |
| AI governance / human-in-the-loop with taste | FinAI / AI-gov | Governance principle for financial AI |
| IPO markets / infra maturation | TokenPilot / DLT | Tokenization rides infra wave |
| Stock picking / market dispersion | Tapease / Market Intel | Intelligence feeds more valuable in dispersion |
| GLP-1 / healthcare transformation | ExitLens / CGT | Valuation models must weight healthcare disruption |
| Aging population / fraud vectors | AML Hive / Compliance | Compliance scales with demographic tailwinds |

### 4. Identify macro trends
Extract 8 trends with structured metadata:
```json
{
  "signal": "AI cost vs. human cost parity debate",
  "strength": "strong",
  "direction": "enterprise pullback brewing",
  "horizon": "3-6 months"
}
```
Trend strength levels: `strong`, `medium`, `weak`. Directions: `accelerating`, `steady`, `enterprise pullback`, `building now`, `active now`, `structural`. Horizons: `now`, `3-6 months`, `6-12 months`, `12-18 months`, `2-5 years`, `3-10 years`, `10+ years`.

### 5. Score AU relevance
Currently fixed at 0.30–0.45 for non-AU podcasts (most content is US-centric). Episodes discussing Australian regulation, markets, or companies score higher.

### 6. Output files
- `~/.hermes/research_outputs/podcast_insights.json` (9.9 KB) — structured data for pipeline consumption
- `~/.hermes/research_outputs/podcast_insights.md` (8.5 KB) — human-readable Markdown report

## Dual-Consumer Pattern

The insight extractor feeds TWO downstream pipelines:

1. **Research enrichment** — Morning Research (05:05) reads `podcast_insights.json` to enrich the day's topic with podcast frameworks
2. **LinkedIn content** — LinkedIn Ideas Generator (06:45) converts frameworks and quotes into social posts

This is the first component in the fleet to demonstrate the dual-consumer architecture — one extraction, two consumers, no duplication of work.

## Production Track Record

| Date | Episodes | Shows | Frameworks | Quotes | Trends | Portfolio Connections |
|------|----------|-------|------------|--------|--------|----------------------|
| Jun 7 | 15 | 6 | 6 | 4 | 8 | 8 |
| Jun 8 | 15 | 6 | 6 | 4 | 8 | 8 |

Both runs produced consistent output structure and volume. The extractor is stable.

## Dependencies
- Supabase `podcast_kb.episodes` table (must have recent transcripts)
- Claude API (for framework extraction — high intelligence needed, not just pattern matching)
- Podcast ingestion cron (`fabab82f804a`) must complete successfully before this runs (00:35 vs 05:02 — 4.5 hour buffer)

## Pitfalls
- **If the ingestion cron produces 0 new episodes**, the insight extractor still runs — it queries the last 3 days so it will re-process existing episodes. This is fine for continuity but means frameworks may repeat day-to-day.
- **Claude output format inconsistency:** Framework names sometimes include colons, sometimes don't. The extractor normalizes on ingest.
- **AU relevance scoring is coarse:** Currently a fixed 0.30–0.45 for non-AU podcasts. A fine-grained scoring model (per-episode AU keyword matching) would improve relevance filtering.
