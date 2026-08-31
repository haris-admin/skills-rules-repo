# Podcast Knowledge Base — Supabase + pgvector Infrastructure

**Provisioned:** June 4, 2026
**Project:** `vyqagemgwxfscppkfswq` (ap-southeast-2, Sydney)
**Connection:** IPv4 pooler at `aws-1-ap-southeast-2.pooler.supabase.co:6543` (PgBouncer mode)

## Schema (`podcast_kb`)

### `podcasts` — 20 registered shows across 3 tiers
| Tier | Shows |
|------|-------|
| 1 | All-In (@allin), a16z (@a16z), My First Million, Acquired, Moonshots, Lenny's Podcast |
| 2 | Masters of Scale, Prof G Pod, Knowledge Project, Logan Bartlett, We Study Billionaires, How I Built This, HBR IdeaCast, a16z Crypto |
| 3 | Diary of a CEO, Foundr, The Pitch, Best One Yet, Girls That Invest, Marketing School |

Each has: `youtube_handle`, `channel_id`, `tier`, `relevance_au` (0.0-1.0).

### `episodes` — 66 ingested as of June 4
- 15 Moonshots (manually extracted, real content)
- 51 from yt-dlp pipeline (All-In, a16z, Acquired, MFM, Lenny's — mostly blocked transcripts)
- Fields: `youtube_id`, `transcript_text`, `frameworks[]`, `key_quotes[]`, `au_relevance_score`

### `chunks` — vector-embedded segments
- `embedding VECTOR(1536)` with IVFFlat index
- `content_tsvector TSVECTOR` for full-text search
- Hybrid search via `podcast_kb.hybrid_search(query_text, query_embedding, match_threshold, au_filter)`

### `au_keywords` — 30 Australian relevance terms
Seeded with: AUSTRAC, AML, CGT, ASIC, APRA, PSP, ESOP, ASX, RBA, ATO, Treasury, NDIS, Privacy Act, etc. Each has a weight (0.25-0.95) for scoring.

### `ingest_log` — pipeline run history

## Ingestion Pipeline

**Script:** `~/.hermes/scripts/podcast_ingestor.py`
**Venv:** `/tmp/podcast_venv` (yt-dlp + youtube-transcript-api)

> ⚠️ **June 25, 2026:** Venv may be cleared by tmpfs. If missing, rebuild: `python3 -m venv /tmp/podcast_venv && /tmp/podcast_venv/bin/pip install yt-dlp psycopg2-binary youtube-transcript-api`.
**Repair script:** `~/.hermes/scripts/podcast_repair_transcripts.py`

### yt-dlp pattern (proven):
```bash
# Phase 1: Fast listing (flat-playlist, no date metadata)
/tmp/podcast_venv/bin/yt-dlp --flat-playlist --playlist-end 30 \
  --print '%(title)s||%(id)s' --no-warnings "https://www.youtube.com/@handle"

# Phase 2: Per-video date fetch
/tmp/podcast_venv/bin/yt-dlp --print '%(upload_date)s' --no-warnings <video_id>
```

### Transcript download:
```bash
/tmp/podcast_venv/bin/python3 ~/.hermes/skills/media/youtube-content/scripts/fetch_transcript.py <youtube_id> --text-only
```

## YouTube Channel Handle Verification

**CRITICAL:** Channel handles were verified on June 4, 2026. The original extraction from YouTube page HTML returned wrong handles for some podcasts:

| Podcast | Wrong Handle | Correct Handle |
|---------|-------------|----------------|
| All-In | `@allinpodcast` (D&D channel) | **`@allin`** |
| Others | Verified correct | — |

Always verify handles with `yt-dlp --flat-playlist --playlist-end 1 --print '%(title)s'` before updating the database.

## Bugs Fixed (Session June 4, 2026)

1. **Double `@` in URL:** DB stores `@allin` → script added another `@` → `https://youtube.com/@@allin`. Fix: `.lstrip('@')`.
2. **Missing `--flat-playlist`:** yt-dlp without it crawls full metadata per video → 60s timeout. Fix: two-phase approach.
3. **Blocked transcripts stored as real content:** ~44 episodes have error text in `transcript_text`. Fix: filter with `WHERE transcript_text NOT LIKE '%YouTube is blocking%' AND transcript_text NOT LIKE '%Could not retrieve%'`.

### Content query (real episodes only):
```sql
SELECT p.name, e.title, e.published_date, e.transcript_text, e.frameworks
FROM podcast_kb.episodes e
JOIN podcast_kb.podcasts p ON e.podcast_id = p.id
WHERE length(e.transcript_text) > 500
  AND e.transcript_text NOT LIKE '%YouTube is blocking%'
  AND e.transcript_text NOT LIKE '%Could not retrieve%'
ORDER BY e.published_date DESC;
```

## Cron Jobs

| ID | Name | Schedule | Purpose |
|-----|------|----------|---------|
| `0fb6bf47f704` | Moonshots Daily Learning | 6:15 AM AEST daily | Random episode → teach + quiz |
| `fabab82f804a` | Podcast KB Ingestion | Wed+Sun 6 AM AEST | Scan 6 channels → new episodes |

## Credentials

Password in spooler URL line of `/mnt/c/Users/habib/.hermes/.env` (line 38 — original, line 35 — updated pooler endpoint). Connection uses PgBouncer mode on port 6543 via `aws-1-ap-southeast-2.pooler.supabase.co`.
