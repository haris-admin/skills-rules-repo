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
- The user mentions an episode the KB does not have → **run the capture audit first** (`python3 ~/.hermes/scripts/podcast_capture_audit.py` — see "Capture-chain integrity"), then go to the source (`references/transcript-sources-and-fallback.md`). Never answer "the KB has nothing on that" without first reporting whether the episode is missing, un-chunked, or unread.

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

**Reusable helper (added 2026-09-16):** `python3 ~/.hermes/scripts/podcast_kb_query.py <file.sql>` — runs SQL through the pooler with the password derived at runtime from `SUPABASE_OPERATOR_SPOOLER_DATABASE_URL` (never printed, never inlined, no shell pipes). Pass SQL as a file argument: piping into a Python interpreter trips the security scanner (`tirith:pipe_to_interpreter`).

**⚠️ Live breakage (2026-09-16) — read before trusting ingestion freshness.** A 2026-09-15 de-hardcoding pass replaced hardcoded Supabase creds in `podcast_ingestor.py` (14:20) and `pluto_chamber_refresh.py` (15:03) with `_required_env("SUPABASE_HOST"|"SUPABASE_PORT"|"SUPABASE_USER"|"SUPABASE_PASS")`. **Those four keys do not exist in either Hermes `.env`** — only `SUPABASE_OPERATOR_DATABASE_URL` / `SUPABASE_OPERATOR_SPOOLER_DATABASE_URL`, and line 50 of the Windows `.env` is malformed (`SUPABASE_OPERATOR_SPOOLER_DATABASE_URL=="postgresql://…"`, double `=`), so the ingestor's naive `key=value` loader cannot recover them either. Result: the 2026-09-16 04:00 ingestion run (`d4d77c41f6c0`) died at import with `RuntimeError: Missing required environment variable: SUPABASE_HOST` (failure_streak=1) and wrote no `podcast_kb.ingest_log` row; the chamber refresh has the same defect. Remediation is either (a) add the four keys to `/mnt/c/Users/habib/.hermes/.env`, or (b) derive them in code from the pooler URL. Diagnostic tell: `podcast_kb.ingest_log` has no `daily_ingest` row for the day (query `SELECT * FROM podcast_kb.ingest_log ORDER BY id DESC LIMIT 5`), and `episodes.created_at` stops advancing.

**✅ Fixed 2026-09-16 06:05 AEST (option b, code-side).** Both `podcast_ingestor.py` and `pluto_chamber_refresh.py` now resolve creds via a `_supabase_creds()` helper: it uses `SUPABASE_HOST|PORT|USER|PASS` if present, else derives host/port/user/password from `SUPABASE_OPERATOR_SPOOLER_DATABASE_URL` in the Hermes `.env` files (regex over the raw file text, so the double-`=` malformed line 50 no longer matters). Verified: `run_sql("SELECT count(*) FROM podcast_kb.episodes")` returns 1185 through both modules. **Any future de-hardcoding pass must keep a derive-from-DSN fallback** — adding `_required_env("SUPABASE_*")` alone will hard-fail every ingestion run because those four keys are not in either `.env`.

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

**A 0-chars transcript is a BLOCK, never "thin data"** — `download_transcript()` returns an empty string
rather than raising, so an IP block looks exactly like a short clip. Classify it: consecutive empty
fetches (>=3) must be counted as BLOCKED and returned as **exit 3**, so the retry driver keeps cycling
instead of declaring success. Without this, a newly registered channel reports `inserted=0, rc=0` and the
retry stops — the row exists, no episodes ever arrive, and nothing looks wrong.

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
- Moonshots: **`@moonshotsclips` is the CLIPS channel, NOT the show** — pointing the row there silently stopped ingest while the main show kept publishing; see "A podcast row can silently watch the WRONG channel" and re-point it at the main handle before expecting new episodes.
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
**Cron:** `bc60994e5592` — Daily 04:30 AEST, `no_agent`, **fail-closed** (re-created 2026-09-26).
History: `79c8ad5b9465` was PRUNED June 13, 2026 and **nothing downstream was adjusted for it — that is the single biggest capture defect in this pipeline.**

**The 3.5-month outage was a HANG, not a prune (root-caused 2026-09-26).** `chunk_text()` ended with
`start = end - overlap; if start >= len(text): break`. Once the remaining tail was <= the overlap,
`end` pinned at `len(text)` and `start` oscillated at `len(text) - overlap` **forever** — the process
spun, appending 200-char tail chunks, and never finished. Newest chunk ever written: **2026-06-08
13:20 UTC**, matching the script's own mtime (Jun 8 23:23 AEST). So the producer died mid-run that
night; the job was removed five days later for "stability", and the real defect was never seen.
**Fix:** `if end >= len(text): break` before advancing, plus a belt-and-braces
`new_start = max(end - overlap, start + (chunk_size - overlap))` so start can never fail to advance.
Regression test: chunk lengths 100 … 120,000 chars must all terminate (50k → 29 chunks, 120k → 68).

**The prune starved every reader.** The daily-learning cron draws episodes with `>= 8` chunks; with chunking gone, only the June-and-earlier episodes ever qualified, so the corpus that the reader can reach is a rounding error of the corpus that exists (measured: 22 of 1,364 episodes; 194 had any chunks at all; newest chunk written 8 June 2026). Symptoms look like a *content* problem, not a pipeline problem: the digest teaches something stale/off-topic and the user's own episode "is not in the KB".

**Rules that keep this from recurring:**
- Restoring chunking is a **prerequisite** for any other capture work — there is no point improving extraction while the reader cannot select the episode. To re-create the job: `no_agent: true` script running `podcast_chunker.py`, timeout >= 900s.
- **Never prune a producer without checking its consumers.** Before removing any stage, grep what selects on its output (here: the daily-learning query's `>= 8` chunks filter, `hybrid_search()`, the insight extractor) and either re-satisfy them or change them in the same change.
- Verify with the capture audit (`references/capture-chain-audit.md`) rather than assuming the prune was harmless.
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

## Capture-chain integrity — measure each link before theorising

The chain is `episode → transcript → chunks → insights → curated knowledge`. **A break anywhere
produces the same symptom**: the KB "has nothing" on an episode the user heard, and the daily digest
teaches something else. Absence of knowledge is not evidence of a bad summary — a summariser that
never received the episode produces exactly the same result as one that summarised it badly.

**Always run the audit before answering "the KB does not have it":**

```bash
python3 ~/.hermes/scripts/podcast_capture_audit.py                        # totals + capture gaps
python3 ~/.hermes/scripts/podcast_capture_audit.py --by-podcast --ledger   # per show + last 60 days
python3 ~/.hermes/scripts/podcast_capture_audit.py --json                  # machine-readable
```

Read-only, and **exits 1 whenever any episode is unreachable** — so it can be scheduled fail-closed.
It reports, per link: episodes with a transcript, with any chunks, meeting the reader's `>= 8` chunk
threshold, the newest chunk timestamp (proves whether the chunk writer is alive), false-green ingest
runs, and the extractor's own window accounting (`episodes_in_window` vs `episodes_read`).

**Read the newest-chunk timestamp first.** It is the fastest tell that a producer died: a chunk date
months behind `episodes.created_at` means the reader has been blind since that date regardless of how
healthy every cron's `last_status` looks.

**Coverage queries (the audit's core):**

```sql
-- how much of the corpus can the reader actually select?
select count(*) total,
       count(*) filter (where exists (select 1 from podcast_kb.chunks c where c.episode_id=e.id)) chunked,
       count(*) filter (where (select count(*) from podcast_kb.chunks c where c.episode_id=e.id) >= 8) selectable
from podcast_kb.episodes e;

-- did any producer claim success while producing nothing?
select count(*) from podcast_kb.ingest_log where coalesce(chunks_created,0) = 0 and status = 'success';
```

### The gate set a repair must satisfy (implementation status varies — check before claiming done)

| Gate | Must assert | Not yet built as of the last audit |
|---|---|---|
| P0 ingest | episode has a *real* transcript | **built** — `--min-chars 2000`, thin runs logged `skipped_thin` (not skipped silently) |
| P1 raw leg | immutable per-episode capture record | **built** — `alexandria-ops/podcast-capture/<YYYY-MM>/episode-<id>.json` |
| P2 chunks | chunks exist, coverage verified, `ch=0` is never success | **built** — chunker re-scheduled `bc60994e5592`; it re-counts rows in the DB and fails the episode if the write didn't land |
| P3 extract | key points stored **per episode** with verbatim quotes | **built** — `jsonb` per episode in `podcast_kb.capture_ledger.key_points` |
| P4 verify | independent pass re-reads the transcript, lists what the maker MISSED, then locks | **built** — `podcast_capture_verify.py` (job `4ef6e889e8d6`) |
| P5 curate | only `locked` episodes reach the curated layer | **built** — `podcast_curated_export.py` (job `b0826b3b4123`) exports `locked` rows only into `mempalace-inputs` → the vault sync carries them to `alexandria`; everything else is reported as an explicit unverified count |

Watchdog job `cc76c11d35d2` (daily 06:25) runs the capture audit and is **silent when healthy** —
it speaks only when episodes cannot reach the reader, so the next silent outage announces itself.

The maker must never be its own verifier (P4) — a self-check passes by construction. Use a different
model family for the verify pass than for the extract pass, and keep the raw leg (P1) on
`alexandria-ops` with the curated layer on `alexandria` so the two can be compared.

### Pitfalls

- **`status = 'success'` with zero output is a false green.** An ingest run that reports success while
  writing 0 chunks hides a dead producer for months: assert the stage's own output count and fail
  non-zero on zero. Any "N processed" line must carry the count of what it actually created.
- **A rolling-window output is not storage.** A JSON/markdown that keeps only the last N days of
  extracted key points discards everything older on every run. If the user expects to ask about an
  episode weeks later, persist one durable record per episode keyed by episode id.
- **Short "transcripts" are YouTube descriptions, not content.** Entries of ~400-1,700 chars are
  shownotes/Shorts, not talk; they cannot yield chunks or key points. Flag them as `transcript_thin`
  rather than counting them as captured.
- **Never match short acronyms with bare substring `ILIKE`.** `transcript_text ILIKE '%AMA%'` matches
  *Amazon* (and "drama", "Kamath"); an episode search that silently returns unrelated rows reads as
  "no such episode". Anchor with a word-boundary regex (`~* '\mAMA\M'`) or search the title.
- **Aggregate-in-`GROUP BY` fails in psql.** `to_char(created_at,'YYYY-MM') || count(*) ... GROUP BY 1`
  errors with "aggregate functions are not allowed in GROUP BY"; bucket in a subquery and concatenate
  outside it.

### The maker/checker verifier (`podcast_capture_verify.py`)

`python3 ~/.hermes/scripts/podcast_capture_verify.py [--episode-id N | --since DAYS | --limit N]`
(runs daily at 05:35 via `podcast_capture_verify_daily.sh`, job `4ef6e889e8d6`).

| Pass | Model | Job |
|---|---|---|
| MAKER | `deepseek-flash` (DeepSeek direct) | 6-14 key points, each with a **verbatim quote** + context |
| CHECKER | `qwen/qwen3.8-flash` (OpenRouter, fallback `google/gemini-3.8-flash`) | per point: quote verbatim? claim supported? **plus the point of the whole exercise — what is MISSING** |
| MAKER round 2 | `deepseek-flash` | returns **only the missing points** (ask for the merged list and the JSON comes back truncated) |
| verdict | code | `locked` only if every point passes the token-window check AND no material point is missing; otherwise `needs_human` |

Measured 2026-09-26 on a 24.6k-char episode: **$0.005-0.010 per episode**, ~2-4 min. Qwen is
~8x cheaper than Gemini on output ($0.47 vs $3.75 per 1M); Gemini runs as the fallback because Qwen
upstream rate-limits (HTTP 429) intermittently. The model actually used is stored per episode
(`checker_model`), so verification provenance is never ambiguous.

**Why the vendor split matters — with the receipt.** On the first full run the DeepSeek maker produced
14 points; the independent checker accepted all 14 quotes and then listed **3 material points the maker
had missed** (Iger's crisis-leadership posture, autocrat/democrat decision balance, quality-vs-volume).
A self-check would have passed by construction.

**Pitfalls that cost real debugging time:**

- **DeepSeek spends the budget on `reasoning_content` first.** With `max_tokens` too small the call
  returns an **empty `content`** and `finish_reason=length` — which reads as "the model said nothing".
  Allow 3 attempts with 8k → 16k → 32k, and treat empty content as retryable, not as an answer.
- **`str.format()` on a prompt containing JSON braces raises `KeyError: '"points"'`.** Use
  `.replace("{transcript}", ...)` instead of `.format()`.
- **`podcast_kb_query.run_sql()` returns the raw stdout TEXT, not rows.** The splitting version lives in
  `podcast_chunker.py`. Iterating the helper's return value walks the string one CHARACTER at a time and
  silently yields digit-characters as "rows" (it reported *54 episodes* for a single-episode query).
  Wrap it: `[line.split("|||") for line in raw.strip().splitlines()]`.
- **A character-exact verbatim check cries wolf.** Models normalise curly quotes/dashes and YouTube
  captions carry speaker labels mid-quote, so compare **word-token windows** (a contiguous 12-word
  window must appear in the transcript) after folding typography to ASCII. A char comparison rejected 6
  genuinely-verbatim quotes out of 14.
- **`\copy ... from stdin` swallows every SQL statement after it** in the same psql session, and a TEMP
  staging table dies with the session. Stage into a permanent table and `\copy` from a FILE.
- **Transcripts contain newlines** (154 episodes do). A `|`-delimited or line-per-row psql read breaks on
  them: transfer `json_build_object(...)::text` (escapes newlines) and split rows on the separator only.
- **Sub-$0.01 is the right order of magnitude for embeddings too:** `text-embedding-3-small` is $0.02/1M
  tokens; a 50k-char episode was 13,354 tokens ≈ $0.00027. A 1,169-episode backfill is pennies.

### Transcript integrity: a transcript can exist and still be a fragment

`scripts/podcast_transcript_integrity.py` fetches each video's real duration and compares the stored text
against this corpus's own speech rate (**~1,100 chars per minute**; measured 981-1,225 across complete
episodes). Classes: `ok` · `clip` (video < 180s — a short transcript is CORRECT, not a loss) ·
`LOSS` (fragment) · `nodef` (couldn't judge — never counted as OK).

Found on first run: **165 fragments, all in episode ids 1-508** (an older ingest era) — e.g. a 2h48m
episode holding 5,000 chars (2.7%), a 77-minute episode holding 1,784 chars. Damage is confined to the
early ids, so check ids first before assuming the current path is broken.

**Repair (`podcast_transcript_repair.py`, driven by `podcast_repair_retry.sh`):** re-fetch the best
English track (manual before auto-generated), accept ONLY if the new text is >= 1.5x stored and >= 2,000
chars, then **clear that episode's chunks** so the chunker rebuilds them — the chunker selects chunkless
rows only, so stale chunks from the fragment would otherwise survive forever. Never overwrite with a
shorter text: leave it and log it, so the fragment stays visible.

**NEVER parallelise YouTube scraping.** Six concurrent shards earned **HTTP 429** on the watch page and
`IpBlocked` on the transcript endpoint, plus yt-dlp's "Sign in to confirm you're not a bot" — 143 rows
got poisoned as `unrecoverable` before this was caught. Cap concurrency at 1-2, pace with a delay, and
treat `IpBlocked` / 429 / "Sign in" as **retry later** (abort the run after 3 consecutive strikes) —
never as "no transcript available". A blocked IP also breaks the nightly ingest fallback (yt-dlp), so
re-check access before the 4:00 AM job.

### A podcast row can silently watch the WRONG channel

`podcast_kb.podcasts` id=5 was named **"Moonshots Podcast"** while its handle was **`@moonshotsclips`** —
a clips channel (last upload 2026-08-05) rather than the main show, so ingest stopped while the podcast
kept publishing. This is why the AMA material never arrived at all.

**Check when a show goes quiet:** compare the newest episode's **duration** against what that show normally
publishes. 8-15 minute "episodes" from a 60-90 minute show means you are watching its clips channel.
Verify `youtube_handle` identity, not just the display name.

**Resolve handle → channel_id without the watch page** (the watch page is the first thing a rate limit
kills; the listing path keeps working):

```bash
/tmp/podcast_venv/bin/yt-dlp --flat-playlist --playlist-end 1 --no-warnings \
  --print '%(channel_id)s|%(title).60s' "https://www.youtube.com/@HANDLE/videos"
```

`scripts/survey_channels.sh HANDLE...` does this for a list of candidates and prints the newest three
titles per handle — use it before inserting a row, so the handle is confirmed to be the SHOW and not a
clips/archive/namesake channel.

**Repointing vs replacing — a data-integrity decision, not a rename.** When a row turns out to watch a
clips channel, do NOT repoint that row at the main channel: the row already owns episodes that were
*correctly* captured as clips, and repointing retro-labels them as full episodes and breaks the
attribution of anything already verified from them. Instead **rename the row to what it actually is**
(e.g. `Moonshots Clips`) and **INSERT a new row** for the real show. Both stay in the table; the audit's
per-show view then reads honestly. Generalise: a row's `name` is provenance — changing what a row points
at invalidates every episode already attached to it.

### Curation gate: only `locked` reaches Alexandria

`scripts/podcast_curated_export.py` (job `b0826b3b4123`, 06:10) reads `podcast_kb.capture_ledger` and
publishes **only `status='locked'` rows** into `~/.hermes/mempalace-inputs/`, which the 06:15 vault sync
carries into `alexandria/vault/inputs`. It always states the unverified count, so a gap reads as
*unverified: N*, never as "nothing important in that episode". Silent when it curated nothing.

### Verifying the corpus without wasting money

`scripts/podcast_verify_backfill.sh WORKERS LIMIT SINCE_DAYS` runs the maker/checker across many episodes in
parallel; it uses `--list-pending --clean-only`, which **excludes fragments and unjudged rows**, so money is
never spent verifying a transcript that is about to be re-fetched (a fragment would be verified, marked
needs_human, and then invalidated by the repair anyway). Measured: ~$0.005-0.010 and 2-4 min per episode.

### Chamber router — BUILT, measured, and in calibration

`scripts/podcast_three_filters.py` reads each **locked** episode and routes its material into three
chambers, verbatim and attributed; `scripts/podcast_filters_report.py` aggregates the run's JSONL into
one markdown file per lens under `~/.hermes/mempalace-inputs/` for the vault sync to carry to Alexandria.

It routes from the **stored** transcript, so a YouTube block does not block it (only ingest/repair are
blocked) — do not park routing work behind a transcript-access problem. Measured over 41 episodes:
**0 failures, $0.00069 per episode**, ~12 chamber-1 items each, i.e. the entire 1,364-episode corpus
routes for about a dollar. Cost is not a reason to ration routing; **relevance calibration is the real
problem** (see the calibration rules below).

1. **Chamber 1 — noteworthy, verbatim**: frameworks, numbers, predictions, contrarian claims, tactics,
   lessons. The quote is copied exactly and carries a short context label.
2. **Chamber 2 — Australian relevance**: geography, regulation, payments rails/schemes, local industry,
   sovereignty, workforce — each with a short `why_australia` line.
3. **Chamber 3 — project lenses**, one file per lens rather than one mixed bucket (retrieval and dedup
   stay clean):
   - `simplifii` — neurodivergent/accessible learning, EdTech, students, study support
   - `predispute` — pre-chargeback reconciliation and recovery, merchant/customer disputes, chargebacks
   - `tapease` — card-present POS, transport ticketing, taxi, forecourt, in-person payments
   - `amlhive` — AML/CTF compliance, AUSTRAC, RegTech, reporting obligations
   - `haris` — the operator's own public positioning: AI adoption and safe agent rollouts in regulated
     environments, agent architecture and governance, payments architecture, cloud/resilience,
     engineering operating models, regulated delivery (APRA CPS 230, AUSTRAC Tranche 2, Privacy Act,
     Essential Eight). Source of truth for this lens is harishabib.au — re-read it when the lens
     looks stale rather than inventing themes.

**Hard rules — each one earned by a failure earlier in this chain:**

- **Only `locked` episodes feed the router.** The P5 gate is the router's input filter, never its job.
- **Verify quotes in code** with the token-window check and drop (counting) anything that fails. A model
  claiming it quoted verbatim is not evidence; some cheap models paraphrase silently.
- **Provenance per item**: episode id, show, published date, transcript sha, router model, run timestamp.
- **Dedup across episodes** — the same idea from N episodes is one entry citing N sources, not N lines.
- **A lens with nothing says so** ("0 items from N locked episodes"). An empty chamber must never be
  indistinguishable from a chamber nothing was routed into.
- **Idempotent and resumable**, keyed by (episode id, lens, quote hash), so re-runs and corpus backfills
  cannot duplicate entries.
- **Choose the model by measurement, not reputation** — route that decision through `llm-cost-routing`
  ("Value bake-off: reference-scored, and per JOB SHAPE"): benchmark against a named reference on the
  router's OWN output shape (many items with quotes), and project corpus cost from measured tokens.
- **Router ladder as measured (2026-09-27)** — ordered by *completion reliability first*, then value:
  1. `deepseek/deepseek-v4-flash` — completes long structured output, quotes verify, ~$0.0007/episode
  2. `z-ai/glm-5.3-flash` — highest recall (82% vs the Qwen 3.8 reference) and 16/16 verbatim, **but only
     with `reasoning: {enabled: false}`**: left on, it spends the whole output budget on hidden reasoning
     and returns an empty `content` (same trap that killed both Nemotrons and starves DeepSeek at low
     `max_tokens`). Reasoning-heavy models must have reasoning turned OFF for extraction work.
  3. `deepseek/deepseek-v4.1-flash` — fallback, 73% recall
  4. `qwen/qwen3.8-flash` — last resort: proven checker, verbose router (truncated at 7k output tokens)
- **Do not park routing behind transcript access.** The router reads the STORED transcript, so a YouTube
  block stops ingest and repair but not routing — run the filters over what is already captured.

**Calibration — a lens LABEL is not evidence that an item belongs in that lens.** The first real run
produced three failure modes worth guarding against in any filter/router prompt:

- **A free-text relevance field invites post-hoc rationalisation.** Asked *why* an item matters to a
  lens, the model will invent a link: a sports/business episode yielded an item claiming it "touches
  fintech and RegTech". Require an **explicit anchor** — the item must name the regulation, rail,
  jurisdiction or entity it connects to — and drop items that only assert generic relevance. A single
  "relevance" field with no anchor requirement manufactures plausible noise at scale.
- **A broad lens becomes a catch-all.** The self-positioning lens absorbed generic AI-infrastructure
  minutiae while the specific project lenses returned zero — including an episode squarely about
  education scoring zero for the education lens. Define every lens by **explicit triggers** (see the
  trigger table in `references/chamber-router.md`) and **score each item's relevance in code** with a
  threshold, rather than trusting which bucket the model chose.
- **Chamber 1 runs ~12 items per episode**, so 40 episodes produced 500+ items. Dedup by normalised
  quote hash across episodes (the same idea from N episodes is ONE entry citing N sources), and expect
  chamber 1 to need theme-level curation on top of quote-level dedup.

**Run mechanics for any multi-episode model pass:** a tool call cannot hold a run of this length (the
`execute_code` cell caps out around five minutes), so launch it **detached** (`tmux new-session -d`),
shard the episode list across 2-3 workers, and have the script **append each episode's result to a
JSONL the moment it lands** — then poll the log with a bounded loop. Partial evidence must survive an
interrupt, and a run must never hold the only copy of its own results in memory.

Sequencing: repair fragments → re-chunk → verify to `locked` → route. Never route ahead of the gate.

**Scheduled:** `scripts/podcast_three_filters_daily.sh` runs 06:45 daily (cron `a2ff28e23482`, `no_agent`
script, `deliver: local`, failures routed to the origin chat). A **2-day window** catches late-ingested
episodes; the router's quote-hash dedup makes re-runs a no-op. It sits at the end of the chain
(04:00 ingest → 04:30 chunk → 05:35 verify → 06:10 curate → 06:25 watchdog → 06:45 route) so it can only
ever route what is already captured and verified.

Full detail, decisions and the gate rationale: `references/capture-chain-audit.md`.
Router prompt contract, lens trigger table and the calibration fixes: `references/chamber-router.md`.

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

**Runner (current):** `python3 ~/.hermes/scripts/podcast_insights_daily.py` — Supabase window query →
keyword-dense transcript sampling (~30k chars/ep) → parallel DeepSeek Flash extraction → verbatim quote
verification against stored transcripts → md + json. `--publish` re-publishes from `/tmp/podcast_insights_raw.json`
and re-verifies quotes (no LLM calls). Optional curation layer `/tmp/podcast_insights_overrides.json`
(quote selection, project-label normalisation, rationale completion) is auto-applied at publish and archived
per-day so it cannot bleed across runs. The `new_since_last_run` / 🆕 baseline resolves defensively
(a publish timestamp from today is ignored → the raw snapshot's `prev_run_cutoff` on a same-day re-run →
a rolling 24h cutoff), so a hand-edit or a re-run can no longer silently mark everything as "not new" —
see `references/insight-extractor-workflow.md`.

**Portfolio mapping for the briefing:** Connection strings like `"FinAI/AI-gov - description"` are parsed and mapped to portfolio projects via keyword matching (FinAI→FinAI File AU, ExitLens→ExitLens AU, etc.). If you change the connection string format, update both the extractor AND `_map_podcast_connections()` in `briefing_improver.py`.

**Full workflow documented at:** `references/insight-extractor-workflow.md` — rewritten 2026-09-20: pipeline
position with live cron timings, runner/CLI, curation-layer keys and rules, known extractor defects + fixes,
post-run verification checklist, recent run metrics. (The older Claude-era steps in git history are historical.)

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

**Answer requests for "what else covers this?" with VERIFIED candidates, not a list of names.** Survey
them live and report only the handles that answered, each with what it actually publishes:

```bash
bash ~/.hermes/skills/research/podcast-knowledge-base/scripts/survey_channels.sh HANDLE1 HANDLE2 ...
```

Group the findings by which lens they feed (frontier AI / startups-VC / payments-fintech / the
portfolio's own domains), and **state the marginal cost before adding any of them**: each new show is
roughly its upload rate per day, and every episode carries the measured verify+route cost. A fleet of
candidate channels is a recurring-bill decision, so offer a tiered recommendation (a small high-signal
core set vs the high-volume reaction channels) and let the user pick.

**Not every domain has a YouTube presence — check before inventing a row.** Australian regulators
(AUSTRAC, APRA, the RBA) publish on their own websites/PDFs and have no channel to watch. For a lens
whose sources are documents, the answer is the web/regulatory ingestion path, not a podcast row; say so
explicitly rather than adding a row that will never produce an episode.

1. Find the YouTube channel handle and ID:
```bash
curl -sL -A "Mozilla/5.0" "https://www.youtube.com/@HANDLE" | grep -oP 'channel_id=([a-zA-Z0-9_-]+)' | head -1
# preferred — works even while the watch page is rate-limited:
/tmp/podcast_venv/bin/yt-dlp --flat-playlist --playlist-end 1 --no-warnings \
  --print '%(channel_id)s' "https://www.youtube.com/@HANDLE/videos"
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

To backfill just the sources you added, use the targeted per-channel ingest
(`podcast_ingest_channels.py <handle>...`) instead of a full-corpus sweep — it retries until transcripts
unblock. **A newly-added row produces NO episodes until transcripts are reachable**: if `IpBlocked`/429
is active (see "Transcript integrity"), the row is registered and waiting, so say *registered, waiting on
transcript access* rather than reporting the channel as captured; the nightly 04:00 ingest collects it
automatically once access returns.

**Give every ingest/repair CLI an argparse with `--dry-run`.** A script that reads source names as bare
positional args treats an unrecognised flag (`--help`, `--limit`) as a source name and **starts the
work** — you get a live ingest instead of usage text.

## Reference Files
- `scripts/survey_channels.sh` — live vetting of candidate channels before adding a row (prints each handle's channel_id + 3 newest titles, or NOT FOUND)
- `references/supabase-schema.md` — Complete DDL for the podcast_kb schema (all 6 tables, indexes, hybrid_search function)
- `references/podcast-directory-full.md` — All 31 tracked podcasts with YouTube handles, channel IDs, tiers, and RSS feed status
- `references/youtube-cookies-export.md` — How to export YouTube cookies from Chrome (June 2026)
- `references/yt-dlp-android-transcript.md` — Android client workaround for n challenge bypass (June 8, 2026)
- `references/aie-ingestion-log.md` — AI Engineer ingestion session log (June 8, 2026)
- `references/capture-chain-audit.md` — the capture chain (episode → transcript → chunks → insights → curated), the coverage queries, the audit script's output fields, and the gate set a repair must satisfy
- `references/insight-extractor-workflow.md` — Full podcast insight extractor workflow: extraction steps, 7-project portfolio mapping, dual-consumer pattern, production track record. (The June 2026 Claude-era draft — incl. the 8-macro-trend methodology — is archived as `insight-extractor-workflow-june2026.md`.)
- `references/youtube-data-api-setup.md` — YouTube Data API v3 setup and quota reference
- `references/youtube-sapisidhash-auth.md` — YouTube cookie + SAPISIDHASH auth workaround for transcript fetching
- `references/transcript-sources-and-fallback.md` — where to get a transcript or summary when the KB is stale (podscripts.co / finance.biggo.com / Apple-Podbean), the freshness query to run first, and the quote-attribution rules (confirm the speaker; check the on-record wording before repeating a paraphrase)
