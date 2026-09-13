# Phase 10: Podcast Knowledge Ingestion — Full Detail

Full detail behind the Phase 10 podcast ingestion summary in `SKILL.md`.
For the transcript/RSS pipeline mechanics themselves see
`references/podcast-ingestion-pipeline.md`; for the Supabase schema see
`references/supabase-podcast-architecture.md`; for handle discovery see
`references/youtube-handle-discovery.md`.

For building knowledge bases from podcast transcripts. **Backend: Supabase + pgvector (LIVE).** 143 episodes across 15 podcasts as of June 5, 2026.

## Contents

- [Scripts](#scripts)
- [Content acquisition (priority order)](#content-acquisition-priority-order)
- [Adding a new tier (step-by-step)](#adding-a-new-tier-step-by-step)
- [YouTube channel types and their quirks](#youtube-channel-types-and-their-quirks)

## Scripts

(all in `~/.hermes/scripts/`):
- `podcast_ingestor.py` — Full pipeline: DB-driven, queries `podcast_kb.podcasts` for all channels with handles. Uses yt-dlp listing → transcript download → Supabase storage. Wed+Sun 6AM cron.
- `podcast_ingest_tier2.py` — Description-based ingestion (no transcript API). For new tiers where transcripts are blocked.
- `podcast_fix_tier2_failed.py` — Targeted fix for channels that returned 0 from main ingest. Handles topic channels, extended date ranges.
- `podcast_repair_transcripts.py` — Repair missing transcripts with 90s delays overnight. VALIDATED June 5: 7→55 transcripts.
- `podcast_repair_descriptions.py` — Fill content from YouTube descriptions (NOT rate-limited, use first).

## Content acquisition (priority order)

1. **YouTube descriptions** (`yt-dlp --print "%(description)s"`) — NOT rate-limited. Contains timestamped topics, guest names, links. ~2K chars average. PRIMARY source. Use first.
2. **Full transcripts** (`youtube-transcript-api`) — rich but IP-blocked. Use 90s delays overnight ONLY. Run `podcast_repair_transcripts.py` as a background process.
3. **Website scraping** — NOT viable (JS-rendered). Skip.

## Adding a new tier (step-by-step)

1. **Discover YouTube handles:** Three methods in priority order:
   - **(A) Curl channel page + grep** — `curl -sL "https://www.youtube.com/@HANDLE" | grep -oP '"channelId":"[^"]+"' ` — most reliable, not rate-limited
   - **(B) YouTube search page** — `curl -sL "https://www.youtube.com/results?search_query=NAME" | grep -oP '/@[a-zA-Z0-9_-]+' | sort | uniq -c | sort -rn` — when exact handle is unknown
   - **(C) yt-dlp flat-playlist** — may be rate-limited after transcript downloads. Use as last resort.
2. **Verify:** Curl the handle URL, extract `<title>` and `channelId`/`externalId` from JSON.
3. **Update DB:** `UPDATE podcast_kb.podcasts SET youtube_handle = '@handle', channel_id = 'UC...' WHERE name = 'Podcast Name'`
4. **Run ingestion:** Use description-based script first (fast, no rate limits). Follow with transcript repair overnight.
5. **The ingestor is DB-driven** — no script changes needed. Cron auto-discovers new channels next run.

## YouTube channel types and their quirks

- **Standard user channels:** `flat-playlist` works. `@handle` URL works. Example: All-In, a16z, Lenny's, Logan Bartlett.
- **Topic channels (auto-generated):** `flat-playlist` returns nothing. `@handle` URL gives "does not have a videos tab". Use channel ID URL: `https://www.youtube.com/channel/UC...`. Example: Masters of Scale, How I Built This.
- **flat-playlist date issue:** `--flat-playlist` returns `NA` for `upload_date` on some channels (Logan Bartlett). Individual date fetches work: `yt-dlp --print '%(upload_date)s' VIDEO_ID`. Non-flat playlist (`--playlist-end N` without `--flat-playlist`) returns dates but is slower.
- **SINCE_DATE filtering:** The ingestor filters videos by `SINCE_DATE` (default 2025-12-01). Some channels (Logan Bartlett) had newest videos from Sep 2025 — ALL got filtered. When debugging empty results, check: (1) flat-playlist returned videos? (2) dates are not NA? (3) dates pass SINCE_DATE? Extend to 2024-06-01 for broad discovery.
