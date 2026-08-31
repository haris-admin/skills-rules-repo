---
name: podcast-knowledge-base
description: Podcast transcript ingestion pipeline — YouTube channels → Supabase pgvector knowledge base with AU relevance scoring. Use when building, querying, or maintaining the podcast knowledge base, setting up new podcast sources, or debugging the yt-dlp ingestion pipeline.
allowed-tools: [terminal, file, read_file, write_file, execute_code, memory]
---

# Podcast Knowledge Base — Supabase + pgvector

## When to Use
- Ingesting new podcast episodes into the knowledge base
- Adding a new podcast source
- Debugging the yt-dlp + transcript pipeline
- Querying the knowledge base for Australian-relevant podcast insights
- Setting up monitoring crons for podcast ingestion

## Architecture

```
┌──────────────────────────────────────┐
│  Podcast Sources (YouTube channels)   │
│  All-In, a16z, MFM, Acquired,         │
│  Lenny, Moonshots + 14 more           │
└──────────────┬───────────────────────┘
               │ yt-dlp + transcript-api
               ▼
┌──────────────────────────────────────┐
│  Supabase (vyqagemgwxfscppkfswq)     │
│  ap-southeast-2 (Sydney)             │
│                                      │
│  podcast_kb schema:                  │
│  ├── podcasts (20 shows)             │
│  ├── episodes (title, transcript,    │
│  │   au_relevance_score, frameworks) │
│  ├── chunks (vector embeddings, FTS) │
│  ├── cross_references                │
│  ├── au_keywords (30 keywords)       │
│  ├── ingest_log                      │
│  └── hybrid_search() function        │
└──────────────────────────────────────┘
               │
               ▼
┌──────────────────────────────────────┐
│  Daily Learning Cron (0fb6bf47f704)  │
│  6:15 AM AEST — random episode →     │
│  teach concept + quiz Haris          │
│  ⚠️ Depends on frameworks[] — only   │
│  Moonshots populated. See Pitfalls.  │
│                                      │
│  ⚠️ Ingestion: FIXED Jun 13. YouTube API v3 live.       │\n│  Was fabab82f804a (now removed).     │\n│  REASON: YouTube IP-blocked both     │\n│  yt-dlp and transcript-api.          │\n│  FIX: YouTube Data API v3 wrapper    │\n│  ready (see youtube_api_wrapper.py). │\n│  Add YOUTUBE_DATA_API_KEY to .env    │\n│  to restore ingestion.               │\n└──────────────────────────────────────┘
```

## Supabase Connection

**Project:** `vyqagemgwxfscppkfswq` (ap-southeast-2)
**Connection:** Use the session pooler at port 6543 for write operations

```python
host = 'aws-1-ap-southeast-2.pooler.supabase.com'
port = '6543'
user = 'postgres.vyqagemgwxfscppkfswq'
dbname = 'postgres'
# Password is embedded in SUPABASE_OPERATOR_SPOOLER_DATABASE_URL (NOT a separate env var).
# Extract it from /mnt/c/Users/habib/.hermes/.env:
#   import re
#   match = re.search(r'postgres\.vyqagemgwxfscppkfswq:([^@]+)@', line)
#   password = match.group(1)  # contains '!' — always use Python subprocess, never bash
# Connection string for psql:
#   postgresql://postgres.vyqagemgwxfscppkfswq@aws-1-ap-southeast-2.pooler.supabase.com:6543/postgres
#   (set PGPASSWORD env var for the password — avoids '!' issues in connection strings)
```

**Critical: IPv6 from WSL.** The `db.vyqagemgwxfscppkfswq.supabase.co` hostname resolves to IPv6 only. WSL cannot route IPv6. Always use the pooler endpoint `aws-1-ap-southeast-2.pooler.supabase.com` which has IPv4.

**pgvector version:** 0.8.0 (IVFFlat + HNSW access methods)

## Schema

### Tables
- `podcast_kb.podcasts` — registered shows (name, channel_id, youtube_handle, tier, relevance_au)
- `podcast_kb.episodes` — individual episodes (title, published_date, youtube_id, transcript_text, au_relevance_score, tags[], frameworks[], key_quotes[])
- `podcast_kb.chunks` — transcript chunks with vector embeddings (1536-dim) and tsvector FTS
- `podcast_kb.cross_references` — links between related chunks across episodes
- `podcast_kb.au_keywords` — 30 Australian-specific keywords with weights for relevance scoring
- `podcast_kb.ingest_log` — audit trail of ingestion runs

### Key Indexes
- `idx_episodes_published_date` — date-based queries
- `idx_chunks_embedding` — IVFFlat cosine vector index (lists=100)
- `idx_chunks_fts` — GIN full-text search index

### Hybrid Search Function
```sql
podcast_kb.hybrid_search(
    query_text TEXT,
    query_embedding VECTOR(1536),
    match_threshold NUMERIC DEFAULT 0.5,
    match_count INT DEFAULT 10,
    au_filter BOOLEAN DEFAULT FALSE
)
```
Combines vector similarity + full-text search + optional AU relevance filter.

## Ingestion Pipeline

**Script:** `~/.hermes/scripts/podcast_ingestor.py`
**Python venv:** `/tmp/podcast_venv/` (yt-dlp, youtube-transcript-api, psycopg2-binary)
  - Rebuild if missing: `python3 -m venv /tmp/podcast_venv && /tmp/podcast_venv/bin/pip install yt-dlp youtube-transcript-api psycopg2-binary`
  - Note: `/tmp` is cleared on reboot — the venv will need rebuilding after restarts

### Rate-Limiting Strategy (June 2026)

The daily ingestion script at `~/.hermes/scripts/podcast_ingestor.py` is designed to go **little by little** to avoid triggering YouTube's IP blocks:

- **Max 3 new episodes per show per run** (not 10 — too aggressive)
- **5-second delay between transcript downloads** within a show
- **3-second delay between shows** 
- **Auto-abort after 5 consecutive transcript failures** — indicates persistent IP block, stops the run to avoid burning quota
- **Dynamic SINCE_DAYS=7** — only fetches episodes from the last week, computed as `(datetime.now() - timedelta(days=SINCE_DAYS))`
- **15 videos per channel** max discovery (not 50) — keeps yt-dlp date-fetching fast

This allows the 12:35 AM cron to complete within ~90 minutes and still have buffer before the 5:02 AM insight extractor.

### Two-Phase Video Discovery (CRITICAL)
yt-dlp without `--flat-playlist` crawls full metadata per video, timing out at 60s with 0 results. The fix is two-phase:

1. **Phase 1 — Fast listing:** `--flat-playlist --playlist-end 30 --print '%(title)s||%(id)s'` (~3-5s per channel)
2. **Phase 2 — Per-video dates:** `--print '%(upload_date)s' <video_id>` (~2s per video)
3. Filter to Jan 2026+ before downloading transcripts

### Batch Date Fetching for Large Channels (>100 episodes)

For channels with 300+ episodes (e.g., @aiDotEngineer with 386), fetching per-video dates one-at-a-time via `execute_code` hits the 50-tool-call limit before completing. **Use a subprocess-based script run in `terminal(background=true, notify_on_complete=true)` instead.**

The script should:
- Use `subprocess.run()` to call yt-dlp (avoids Hermes tool-call count)
- Save progress to a JSON state file every 25 videos (resume-safe)
- Process newest videos first (playlist order)
- Filter to a date cutoff (e.g., 12-month window)

Template: `scripts/batch_fetch_dates.py` in this skill.
See session June 6, 2026 for the @aiDotEngineer run that fetched 386 dates in ~8 minutes this way.

### YouTube Handle Verification
Channel handles must be verified before ingestion. Wrong handles silently return wrong channels:
- All-In Podcast: `@allin` (NOT `@allinpodcast` — that's a D&D channel)
- a16z: `@a16z`
- My First Million: `@MyFirstMillionPod`
- Acquired: `@AcquiredFM`
- Lenny's Podcast: `@lennyspodcast`
- Moonshots: `@moonshotsclips`
- **Silicon Valley Girl:** `@siliconvalleygirl` (added June 4, 2026)
- **AI Engineer:** `@aiDotEngineer` (added June 6, 2026) — Channel ID `UCLKPca3kwwd-B59HNr-_lvA`. ~1 ep/day, 372 in 12-month window. Covers agents, MCP, LLM ops, evals, coding agents. Tier 1, relevance 0.85. Dedicated MemPalace `aie-podcast` chamber. **Ingestion started June 8: 14/372 captured before IP block.** Resume with yt-dlp android client + cookies.
- **Sabrina Ramonov:** `@sabrina_ramonov` (added Aug 30, 2026) — Channel ID `UCiGWNa6QK6CiKPvv5-YPv8g`. 364K subs, 2.2K videos, daily uploads, top-5% AI-coding educator. Solo founder of Blotato (AI SaaS content repurposing). Traction/distribution playbook: solve own problem → validate via content → film MVP build → launch to audience → watch PostHog → copy proven hooks → one-day content engine. Tier 1, relevance 0.60.
- **Product Faculty:** `@productfaculty` (added Aug 30, 2026) — Channel ID `UCZBH6VRbAUIAV_wvJA7xRMw`. AI/product founder interview series (host of the Sabrina Ramonov Blotato episode). Tier 2, relevance 0.45.
- **Alex Finn:** `@AlexFinnOfficial` (added Aug 30, 2026) — Channel ID `UCfQNB91qRP_5ILeu_S_bSkg`. "#1 vibe coding channel" — Claude Code, Codex, AI agents, creator economy. Tier 1, relevance 0.55.
- **Alex Kantrowitz (Big Technology):** `@Alex.kantrowitz` (added Aug 30, 2026) — Channel ID `UCye1YedIypHffYb8k6Gp9wg`. Big Technology Podcast — tech industry journalism, CEO interviews (Zuckerberg, Altman, Hassabis). Tier 1, relevance 0.45.
- **NetworkChuck:** `@NetworkChuck` (added Aug 30, 2026) — tier 3, category tech/education, relevance 0.30.
- **This Week in Startups:** `@startups` (added Aug 30, 2026) — Channel ID `UCkkhmBWfS7pILYIk0izkc3A`. Jason Calacanis / Alex Finn OpenClaw agent demos live here (E2246 Ultron, E2247 Clawdbot, E2272 3 AI agents). Tier 2, relevance 0.45.
- **Beyond Coding:** `@beyondcoding` (added Aug 30, 2026) — Patrick Akil, 264 episodes, CTO/principal-engineer interviews + AI. Tier 3, category software-engineering/ai, relevance 0.30.

**oEmbed 404 ≠ invalid handle (Aug 2026):** `https://www.youtube.com/oembed?url=https://www.youtube.com/@HANDLE` returns 404 for some VALID handles (`@startups`, `@beyondcoding`) due to handle-redirect quirks. Don't trust oEmbed for verification — confirm via web search / Apple Podcasts / the channel's own site instead. Channel IDs resolve from search results or the skill's `podcast-directory-full.md` reference.

**Double `@` URL bug:** The database stores handles WITH the `@` prefix. If the script also adds `@`, the URL becomes `https://www.youtube.com/@@handle` — which returns 0 results silently. Always `.lstrip('@')` before constructing URLs. This took 3 pipeline runs to diagnose (June 4, 2026).

### yt-dlp Android Client Workaround (UPDATED June 8, 2026)

**The web client requires solving YouTube's "n challenge" (JavaScript bot detection).** Even with `yt-dlp-ejs` installed, the n challenge may still fail in the Hermes sandbox. **The Android client bypasses this entirely:**

```bash
/tmp/podcast_venv/bin/yt-dlp \
  --extractor-args "youtube:player_client=android" \
  --write-auto-subs --sub-lang en --sub-format srt --skip-download \
  -o "/tmp/transcript" "<video_id>"
```

**Dependencies:**
```bash
# yt-dlp + ejs challenge solver (needed for web client, optional with android)
/tmp/podcast_venv/bin/pip install yt-dlp yt-dlp-ejs
```

**Version note:** yt-dlp 2026.03.17 is the latest stable (June 2026). Nightly builds exist up to 2026.6.6.234447.dev0 but require `--pre` flag to install. Stable is sufficient for the android client approach.

**Why android client works:**
- Mobile APIs don't enforce the n challenge that the web client requires
- Subtitles are found reliably (confirmed June 8 with _B4Pv9ttFgY)
- Works WITHOUT cookies for basic operations
- COOKIES NOT SUPPORTED with android client — cookies are web-client-only. Use android client for transcript-only downloads.

**The subtitle endpoint has SEPARATE rate limiting from video download.** You can successfully download video formats but get HTTP 429 on subtitle download. This is a different rate limit than the main IP block. **Workaround:** use longer delays (8-10s between requests) and the android client which hits a different endpoint.

**youtube-transcript-api v1.2.4 note:** The API changed from older versions. Use instance methods:
```python
api = YouTubeTranscriptApi()        # create instance
result = api.fetch(video_id)        # NOT YouTubeTranscriptApi.get_transcript()
segments = [s.text for s in result] # FetchedTranscriptSnippet objects
```
This library does NOT support browser cookies. Use yt-dlp android client for transcript extraction when the IP is blocked.

### AU Relevance Scoring
Auto-scored during ingestion by keyword density matching against 30 Australian-specific terms:
- Regulatory: AUSTRAC, AML, ASIC, APRA, ATO, Treasury, RBA, OAIC, Privacy Act, ASD Essential Eight
- Market: ASX, Australia, Australian, Sydney, Melbourne
- Sector: fintech, regtech, superannuation, NDIS
- Licensing: PSP, payment service, AFSL, Australian financial services licence
- Tax: CGT, capital gains, ESOP, employee share scheme
- Crypto: digital asset, cryptocurrency, DLT

Score = min(1.0, matches × 0.15). Episodes with score > 0.5 are flagged for AU relevance.

### Podcast Tiers
- **Tier 1 (7 shows):** All-In, a16z, My First Million, Acquired, Moonshots, Lenny's Podcast, AI Engineer — AU relevance 0.50-0.85
- **Tier 2 (7 shows):** Masters of Scale, Prof G, Knowledge Project, Logan Bartlett, We Study Billionaires, How I Built This, HBR IdeaCast, a16z Crypto — AU relevance 0.40-0.55
- **Tier 3 (7 shows):** Diary of a CEO, Foundr, The Pitch, Best One Yet, Girls That Invest, Marketing School — AU relevance 0.30-0.50

## Chunking + Embedding Pipeline

The chunking pipeline was built on June 8, 2026 to fix the "0 vector chunks" problem. The ingestion script stores full transcripts but never generated embeddings — meaning `hybrid_search()` could never return results.

**Script:** `~/.hermes/scripts/podcast_chunker.py`
**Cron:** `79c8ad5b9465` — **[PRUNED June 13, 2026]** Chunking pipeline removed. Was Daily 2:00 AM AEST (no_agent script). If chunking is needed again, create a new `no_agent: true` script with 900s+ timeout.
**Embedding model:** `openai/text-embedding-3-small` via OpenRouter (1536-dim, $0.02/1M tokens)
**Chunking:** 2,000 chars per chunk + 200-char overlap, sentence-boundary aware

**Flow:**
1. Find episodes with transcripts but no chunks
2. Split transcripts into overlapping chunks
3. Batch-embed via OpenRouter (100 inputs/batch)
4. Store in `podcast_kb.chunks` with embeddings + AU keywords
5. Log to `podcast_kb.ingest_log`

**Cost:** ~$0.003 for 198 episodes (139K tokens). Ongoing: ~$0.0002/day for new episodes.

For small-scale (<100 docs, single source), ChromaDB via `pluto_mempalace_feeder.py` works for one-off channel knowledge bases (e.g., Moonshots with 15 episodes, aiDotEngineer with 372 episodes). For 500+ episodes across 30+ podcasts, Supabase + pgvector is the right choice: remote access from any system, hybrid search (SQL full-text + vector), cross-podcast JOINs, auto-generated REST API via PostgREST.

### Dedicated Chamber Pattern (for single high-value channels)

When a podcast channel merits its own MemPalace chamber (rather than mixing into domain chambers):
1. Create chamber via feeder: `python3 pluto_mempalace_feeder.py --input seed.json --chamber <name>`
2. Register in Supabase (for tracking, even if transcripts live in ChromaDB)
3. Batch-fetch all upload dates via two-phase yt-dlp (flat-playlist → per-video dates)
4. Filter to 12-month window (or desired range)
5. Ingest newest→oldest with 3s rate limit between episodes
6. Each episode becomes a ChromaDB document with title, transcript (if available), source URL, and published date

Chambers created this way: `aie-podcast` (aiDotEngineer, 372 episodes, June 2026).
Scripts: `/tmp/aie_chamber_ingest.py` (main ingestion, newest-first, `--limit` + `--dry-run` flags) and `/tmp/aie_continue.py` (offset-based resumption, accepts `OFFSET LIMIT` args, skips already-ingested episodes). Both auto-abort at 5 consecutive transcript failures.

## Lenny's Podcast — Credential Integration

Lenny Rachitsky's podcast does deep interviews on product, growth, and AI. Haris has elevated "insider" access (may include private RSS feed, premium content, or early transcript access). Channel discovery is blocked until the credential format is confirmed — flag to Haris to provide the private RSS URL or credential location. Store credential reference at `~/.hermes/research_outputs/.lenny_credentials.md`.

## Portfolio Cross-Reference

When the daily learning cron surfaces a podcast framework, connect it to Haris's portfolio:

| Framework Theme | Portfolio Project |
|----------------|-------------------|
| CGT, taxation, exits | ExitLens AU |
| PSP, payments licensing | PayLicence AU |
| AI governance, agent security | FinAI File AU |
| AML, AUSTRAC, compliance | AML Hive |
| Digital assets, DLT, crypto | TokenPilot AU |
| Cloud infrastructure | CloudProof AU |
| Market operations | Tapease |

### Daily Monitoring Cron

A dedicated cron monitors all tracked podcast YouTube channels for new episodes, downloads transcripts, and stores to Supabase. **Type:** `no_agent: true` script (June 12, 2026 — was LLM-driven, fixed broken pipe by converting to script mode).

**Schedule:** Daily 4:00 AM AEST (`0 4 * * *`) — first job in the chain, 1+ hours before briefing
**Job ID:** `d4d77c41f6c0`
**Type:** `no_agent: true` script — runs as standalone Python, no LLM dependency
**Timeout:** 3600s (set via `cron.script_timeout_seconds` in config.yaml — was 120s, causing 9 days of silent failures)
**Verification:** Jun 14 test: all 16 channels scanned, **12 episodes ingested in 872 seconds, 0 errors**. Worst-case runtime ~15 min, but the script is rate-limited (5s between episodes, 3s between shows) so headroom is adequate.

### Podcast Chunking — [PRUNED June 13, 2026]
**Schedule:** ~~Daily 2:00 AM AEST (`0 2 * * *`)~~ — **REMOVED**
**Job ID:** ~~`79c8ad5b9465`~~ — **PRUNED** (podcast chunking pipeline removed for stability)
**Original purpose:** Ran the chunker to generate embeddings for newly ingested episodes. Chunking was removed in the June 13 prune (trade-off: stability > embeddings). If needed again, create a new `no_agent: true` script with 900s+ timeout.

### Podcast Insight Extractor (feeds BOTH synthesis AND morning briefing)
**Schedule:** Daily 5:02 AM AEST (`2 5 * * *`) — after ingestion, before synthesis
**Job ID:** `67319a9b2606`
**Delivery:** `origin` (June 12, 2026) — sent directly to Telegram AND saved to `research_outputs/`

Queries Supabase for episodes from last 3 days, extracts key themes/frameworks/quotes, writes to `~/.hermes/research_outputs/podcast_insights.json`. **Two consumers pick up this file:**
1. **Cross-Chamber Synthesis (5:10 AM)** — uses themes for cross-domain pattern detection
2. **Briefing Improver (5:20 AM)** — reads directly, adds dedicated 🎧 Podcast Insights section to morning briefing with portfolio mapping via `_map_podcast_connections()` in `briefing_improver.py`

**Portfolio mapping for the briefing:** Connection strings like `"FinAI/AI-gov - description"` are parsed and mapped to portfolio projects via keyword matching (FinAI→FinAI File AU, ExitLens→ExitLens AU, etc.). If you change the connection string format, update both the extractor AND `_map_podcast_connections()` in `briefing_improver.py`.

**Full workflow documented at:** `references/insight-extractor-workflow.md` — includes extraction steps, portfolio-connection mapping table (7 projects), trend extraction methodology (8 macro trends), dual-consumer pattern (research + LinkedIn), and production track record.

**State tracking:** Store last run date in `~/.hermes/research_outputs/.podcast_monitor_state.json`:
```json
{"last_run": "2026-06-04T20:30:00+10:00", "episodes_processed": 146}
```

## YouTube Data API v3 — Live (June 14, 2026)

The YouTube Data API v3 wrapper (`scripts/youtube_api_wrapper.py`) is **live with an API key.** Key added to WSL `~/.hermes/.env` on June 14.

**Ingestion cron restored:** `d4d77c41f6c0` at 4:00 AM AEST daily (`no_agent`, script: `podcast_ingestor.py`)

**What changed:**
1. `list_channel_videos()` — now tries YouTube API first (search_channel → playlistItems.list), falls back to yt-dlp
2. `download_transcript()` — updated to use `YouTubeTranscriptApi()` instance + `.fetch()` (new v2 API, works, not IP-blocked)
3. The ingestor auto-detects `YOUTUBE_DATA_API_KEY` in the environment — no code changes needed when key is present

**Cron jobs (current):**
| Job ID | Name | Schedule | Purpose |
|--------|------|----------|---------|
| `d4d77c41f6c0` | Podcast KB Ingestion | 4:00 AM AEST daily | YouTube API + transcript download |
| `67319a9b2606` | Podcast Insight Extractor | 5:02 AM AEST daily | Extract insights for briefing |
| `0fb6bf47f704` | Daily Learning | 6:15 AM AEST | Random episode → teach + quiz |

**Testing:** Verified June 14 — @aiDotEngineer channel search OK, video listing OK, transcript download OK (599 entries, 20K chars). First run ingested Acquired SpaceX episode.

- **Python buffers stdout — background processes go silent.** Running `python3 scripts/podcast_ingestor.py` in background mode produces ZERO output (even after 4+ minutes with psql and yt-dlp working fine). Even `-u` (unbuffered) doesn't fix it — the Hermes process manager captures background stdout differently. **The workaround: run in foreground with a generous timeout, using smaller chunks (e.g. `--limit 40`) to stay under the 600s foreground cap.** Each episode takes ~8-12s, so `--limit 40` = ~5-7 minutes. Chain multiple foreground runs to process a large backlog.

- **`youtube-transcript-api` may be MISSING even when the venv exists.** The rebuild command `pip install yt-dlp youtube-transcript-api psycopg2-binary` should install all three, but the venv may have been created before `youtube-transcript-api` was added to the requirements. **ALWAYS verify:** run `/tmp/podcast_venv/bin/python3 -c "import youtube_transcript_api; print('OK')"`. If it fails, reinstall. This was the root cause of silent transcript failures from June 7–12, 2026 — the script was running, listing channels, but returning None for every transcript download because the library was absent.

- **`/tmp/podcast_venv` evaporates — NOT just on reboot.** `/tmp` is cleared on system restart AND can be cleaned by systemd-tmpfiles or other mechanisms on long-running systems (confirmed: venv disappeared after 10-day uptime, June 15, 2026). When the venv is missing, rebuild it:
  ```bash
  python3 -m venv /tmp/podcast_venv && /tmp/podcast_venv/bin/pip install yt-dlp youtube-transcript-api psycopg2-binary
  ```
  **Verify:** `/tmp/podcast_venv/bin/yt-dlp --version` and `/tmp/podcast_venv/bin/python3 -c "import youtube_transcript_api; print('OK')"`.
  The script hardcodes `/tmp/podcast_venv/bin/yt-dlp` and `/tmp/podcast_venv/bin/python3` — if the venv is gone, the script fails with "No such file or directory."
  **Daily maintenance should check this.** Include in the daily maintenance health check: `ls /tmp/podcast_venv/bin/yt-dlp || rebuild`. Moving to a persistent location (`~/.hermes/venvs/podcast/`) would eliminate this recurring failure mode.

- **yt-dlp without --flat-playlist times out.** Must use two-phase approach. The `--playlist-end N` flag forces full metadata crawl which hits 60s timeout → 0 results.

- **Double `@` in YouTube URLs returns 0 results silently.** DB stores handles with `@` prefix (`@allin`). If URL construction adds another `@`, you get `https://www.youtube.com/@@allin` — yt-dlp returns empty output with zero errors. Always `.lstrip('@')` before constructing channel URLs. This took 3 pipeline runs to diagnose (June 4, 2026).

- **ON CONFLICT target must match the unique constraint.** The `podcasts` table has a unique constraint on `name`, NOT on `youtube_handle`. Using `ON CONFLICT (youtube_handle)` fails with "there is no unique or exclusion constraint matching the ON CONFLICT specification." Use `ON CONFLICT (name)` for upserts, or check for existence with a SELECT first (June 6, 2026).

- **YouTube channel handles can be wrong.** `@allinpodcast` is a D&D channel, `@allin` is the All-In Podcast with Chamath/Sacks/Calacanis/Friedberg. Always verify with yt-dlp test fetch before registering.

### YouTube transcript blocking — WORKAROUND FOUND (June 9, 2026)

- **The timedtext API is PERSISTENTLY blocked.** All methods return 429 regardless of cookies, auth headers, or TLS fingerprinting. The block has been active since at least June 8, 2026.

- **WORKAROUND: Audio download + local whisper transcription.** YouTube's video/audio CDN is on a DIFFERENT rate limit from the timedtext API. Audio downloads work reliably even when transcripts are blocked.

- **Production pipeline:** `/tmp/aie_whisper_ingest.py` — full automated pipeline:
  1. yt-dlp (web client) downloads format 140 (m4a audio) — only endpoint that works
  2. ffmpeg (Windows binary) converts to 16kHz mono WAV
  3. faster-whisper tiny model transcribes at 35-52x realtime
  4. Feeds to MemPalace chamber via `/home/habib/.hermes/venv/bin/python3`
  
- **Usage:** `python3 /tmp/aie_whisper_ingest.py [OFFSET] [LIMIT]` (LIMIT=0 for all remaining)
- **Dependencies:** faster-whisper in `/tmp/podcast_venv/`, chromadb in `/home/habib/.hermes/venv/`, ffmpeg at Windows path
- **Speed:** ~35-40s per 20-minute episode. 372 episodes = ~4 hours.
- **Results (June 9, 2026):** 339/372 AI Engineer episodes ingested. 33 failed (download timeouts on very long episodes >2 hours).
- **Progress tracking:** `/tmp/aie_progress.json` — resume-safe, saves after each episode.

- **Blocked methods (don't waste time retrying these):**
  - `youtube-transcript-api`: returns "YouTube is blocking requests from your IP"
  - `yt-dlp --write-auto-subs`: HTTP Error 429: Too Many Requests  
  - `yt-dlp` with `--extractor-args "youtube:player_client=android"`: HTTP Error 429
  - INNERTUBE `get_transcript`: "Precondition check failed"
  - Timedtext API with SAPISIDHASH auth: still 429

- **SAPISIDHASH Cookie Auth:** Still works for INNERTUBE player API (metadata) but timedtext is separately rate-limited. Useful for getting video titles/metadata, not transcripts.

- **Repair script:** `~/.hermes/scripts/podcast_repair_transcripts.py` — re-downloads transcripts for episodes where `transcript_text LIKE '%YouTube is blocking%'`. Run manually after cookies are available.

### Database / connection pitfalls

- **Supabase ap-southeast-2 is IPv6-only for direct connections.** Always use the pooler endpoint. The DIRECT_URL may not resolve from WSL — use `aws-1-ap-southeast-2.pooler.supabase.com` explicitly.

- **pgvector IVFFlat needs data.** The index was created with `lists=100` but warns on empty tables. It auto-optimizes as data grows.

- **Password with `!` breaks bash.** The Supabase password contains `!` (bash history expansion). Always use Python's subprocess or single-quote the password.

- **HEREDOCs time out in terminal().** For any pipeline that pipes to himalaya or other CLI tools, use the file-based pipe pattern: write to temp file → `cat file | command`.

### Other

- **`youtube_api_wrapper.py` knows about the API key from env** — when `YOUTUBE_DATA_API_KEY` is set in the environment, it auto-switches to API mode. No code changes needed. Add the key to `.env` and the next script run uses API calls.
- **YouTube Data API v3 quota is 10,000 units/day free.** Our pipeline needs ~3,915. The `YouTubeAPI.get_quota_estimate(num_videos)` method helps stay under budget. Monitor usage in Google Cloud Console.
- **YouTube handles with `@` prefix** — The DB stores handles WITH the `@`. The `YouTubeAPI.search_channel()` does `.lstrip('@')` internally. No double-`@` bug, unlike the yt-dlp approach.

- **Quiz question quality matters.** Questions must test understanding, not recall. Good: "Why is GDP fundamentally broken in the age of AI?" Bad: "What are the six dimensions of personhood?"

- **Only Moonshots has frameworks — daily learning query always returns Moonshots.** As of July 2026, the `frameworks[]` column is populated for 15/20 Moonshots episodes but **0 episodes across all 14 other podcasts** (Lenny's, AI Engineer, Acquired, My First Million, a16z, All-In, Prof G, Knowledge Project, HBR IdeaCast, Logan Bartlett, We Study Billionaires, a16z Crypto, Masters of Scale, Silicon Valley Girl). — daily learning query always returns Moonshots.** As of July 2026, the `frameworks[]` column is populated for 15/20 Moonshots episodes but **0 episodes across all 14 other podcasts** (Lenny's, AI Engineer, Acquired, My First Million, a16z, All-In, Prof G, Knowledge Project, HBR IdeaCast, Logan Bartlett, We Study Billionaires, a16z Crypto, Masters of Scale, Silicon Valley Girl). The daily learning cron query filters on `frameworks IS NOT NULL AND array_length(frameworks, 1) > 0`, so `ORDER BY RANDOM()` will ALWAYS return Moonshots. This breaks the "alternate podcasts — don't repeat the same show two days in a row" rule.
  **Workaround:** Query non-Moonshots episodes by transcript availability instead, then manually extract the concept from the transcript text:
  ```sql
  SELECT p.name, e.title, e.published_date, LEFT(e.transcript_text, 6000) as preview, e.key_quotes
  FROM podcast_kb.episodes e JOIN podcast_kb.podcasts p ON e.podcast_id = p.id
  WHERE e.transcript_text IS NOT NULL AND p.name != 'Moonshots Podcast'
  ORDER BY RANDOM() LIMIT 1;
  ```
  Read the transcript preview, identify the core framework/idea, and compose the daily learning from scratch. This uses more agent tokens but produces diverse, cross-podcast learning sessions. The long-term fix is to populate `frameworks[]` for all podcasts — either via the insight extractor cron (`67319a9b2606`) or a dedicated backfill script.

- **youtube-transcript-api v1.2.4 API changed from older versions.** Don't use `YouTubeTranscriptApi.get_transcript()` (doesn't exist). Use: `api = YouTubeTranscriptApi(); result = api.fetch(video_id)`. The `fetch()` method returns `FetchedTranscriptSnippet` objects with `.text`, `.start`, `.duration`. See `fetch_transcript.py` for canonical usage.

## Adding a New Podcast

1. Find the YouTube channel handle and ID:
```bash
curl -sL -A "Mozilla/5.0" "https://www.youtube.com/@HANDLE" | grep -oP 'channel_id=([a-zA-Z0-9_-]+)' | head -1
```

2. Register in Supabase (unique constraint is on `name`, not `youtube_handle`):
```sql
INSERT INTO podcast_kb.podcasts (name, channel_id, youtube_handle, tier, category, relevance_au)
VALUES ('Podcast Name', 'UC...', '@handle', 2, 'Category', 0.50)
ON CONFLICT (name) DO UPDATE SET channel_id = EXCLUDED.channel_id, youtube_handle = EXCLUDED.youtube_handle;
```

3. Run ingestion:
```bash
/tmp/podcast_venv/bin/python3 /home/habib/.hermes/scripts/podcast_ingestor.py
```

## Reference Files
- `references/supabase-schema.md` — Complete DDL for the podcast_kb schema (all 6 tables, indexes, hybrid_search function)
- `references/podcast-directory-full.md` — All 31 tracked podcasts with YouTube handles, channel IDs, tiers, and RSS feed status
- `references/youtube-cookies-export.md` — How to export YouTube cookies from Chrome (June 2026)
- `references/yt-dlp-android-transcript.md` — Android client workaround for n challenge bypass (June 8, 2026)
- `references/aie-ingestion-log.md` — AI Engineer ingestion session log (June 8, 2026)
- `references/insight-extractor-workflow.md` — Full podcast insight extractor workflow: extraction steps, 7-project portfolio mapping, 8-trend methodology, dual-consumer pattern, production track record
