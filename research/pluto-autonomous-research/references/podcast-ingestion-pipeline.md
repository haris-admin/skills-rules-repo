# Podcast Transcript Ingestion Pipeline

## Architecture: Supabase + DB-Driven Ingestor

The pipeline stores podcasts, episodes, and transcripts in Supabase (`podcast_kb` schema, `vyqagemgwxfscppkfswq`, ap-southeast-2). The Python ingestor at `~/.hermes/scripts/podcast_ingestor.py` is **fully DB-driven** — it queries `podcast_kb.podcasts` for all entries with a `youtube_handle` or `channel_id`, discovers videos via yt-dlp, downloads transcripts, and stores them.

**To add new channels:** update the `youtube_handle` and `channel_id` columns in `podcast_kb.podcasts`. No ingestor code changes needed. The next run picks them up automatically.

Venv: `/tmp/podcast_venv/` (has yt-dlp, psycopg2-binary, youtube-transcript-api)

> ⚠️ **June 25, 2026:** `/tmp/podcast_venv/` was cleared (tmpfs cleanup). The venv MUST be rebuilt before podcast_ingestor.py can run. See rebuild instructions below. If `podcast_ingestor.py` fails with `No such file or directory: '/tmp/podcast_venv/bin/yt-dlp'`, rebuild the venv first.

## Content Acquisition (priority order)

1. **YouTube descriptions** (`yt-dlp --print "%(description)s"`) — NOT rate-limited, contains timestamps and topics. Primary source.
2. **Full transcripts** (`youtube-transcript-api`) — rich but IP-blocked under load. Use 90s delays overnight.
3. **Website scraping** — NOT viable for major podcast sites (JS-rendered). Skip this.

## Step 1: YouTube Handle → Channel ID Discovery

**Method A: Channel page HTML (reliable, not rate-limited):**
```bash
html=$(curl -sL --max-time 10 -A "Mozilla/5.0" "https://www.youtube.com/@HANDLE")
cid=$(echo "$html" | grep -oP '"channelId"\s*:\s*"[^"]+"' | head -1 | grep -oP ':"\K[^"]+')
# Fallback regex for some channel page formats:
# cid=$(echo "$html" | grep -oP '"externalId":"[^"]+"' | head -1 | grep -oP ':"\K[^"]+')
```

**Method B: YouTube search page (when handle is unknown):**
```bash
curl -sL --max-time 10 -A "Mozilla/5.0" \
  "https://www.youtube.com/results?search_query=Podcast+Name" | \
  grep -oP '/@[a-zA-Z0-9_-]+' | sort | uniq -c | sort -rn | head -5
```

**Method C: yt-dlp (may be rate-limited after transcript downloads):**
```bash
yt-dlp --flat-playlist --print "%(channel_id)s" "https://www.youtube.com/@HANDLE"
```

## Step 2: Run the Ingestor

```bash
/tmp/podcast_venv/bin/python3 ~/.hermes/scripts/podcast_ingestor.py
```

The ingestor: (1) queries Supabase for podcasts with handles, (2) lists up to 50 videos per channel via yt-dlp flat-playlist, (3) downloads transcripts for new videos, (4) inserts into `podcast_kb.episodes`.

## Step 3: Repair Missing Transcripts

**Description repair (instant, no rate limit):**
```bash
/tmp/podcast_venv/bin/python3 ~/.hermes/scripts/podcast_repair_descriptions.py
```

**Transcript repair (overnight, 90s delays):**
```bash
/tmp/podcast_venv/bin/python3 ~/.hermes/scripts/podcast_repair_transcripts.py
```

On June 4-5, 2026, the 90s-delay overnight repair cleared YouTube's IP block, upgrading 48 episodes from description-only to full transcripts (7→55 rich episodes).

## Confirmed Podcast Handles & Channel IDs (June 2026)

### Tier 1 (6 podcasts, fully ingested)
| Podcast | Handle | Channel ID |
|---------|--------|-------------|
| All-In Podcast | @allin | (in DB) |
| a16z Podcast | @a16z | (in DB) |
| My First Million | @MyFirstMillionPod | (in DB) |
| Acquired | @AcquiredFM | (in DB) |
| Moonshots Podcast | @Moonshots | UCCpNQKYvrnWQNjZprabMJlw |
| Lenny's Podcast | @lennyspodcast | (in DB) |
| Silicon Valley Girl | @siliconvalleygirl | (in DB — 0 episodes, needs first run) |

### Tier 2 (8 podcasts, handles confirmed June 5)
| Podcast | Handle | Channel ID |
|---------|--------|-------------|
| a16z Crypto | @a16zcrypto | UCTHq3W46BiAYjKUYZq2qm-Q |
| HBR IdeaCast | @HarvardBusinessReview | UCjwwTPtfMOXZu0QdN01y9rg |
| How I Built This | @HowIBuiltThis | UCn-hX1cX2CrQdyDh-qik1ZA |
| Masters of Scale | @mastersofscale | UCQDXdr8B2Ou72uNZynnAt3A |
| The Knowledge Project | @tkppodcast | UCLtTf_uKt0Itd0NG7txrwXA |
| The Logan Bartlett Show | @TheLoganBartlettShow | UCsa9FJqjpUmMF5TZjOX2K2g |
| The Prof G Pod | @TheProfGPod | UCp4CBeq4nzeg9smAvdjPrig |
| We Study Billionaires | @TheInvestorsPodcastShow | UCPbMnGLeHscshhD7PAEnvbw |

## Supabase Connection (from WSL)

Connection string in `/mnt/c/Users/habib/.hermes/.env` as `SUPABASE_OPERATOR_SPOOLER_DATABASE_URL`. **Parsing pitfalls:**

- **Double `=` in env value:** The line is `KEY==postgresql://...` — regex must use `=+` not `=`
- **`pgbouncer=true` breaks psycopg2:** Supabase pooler URLs include `?pgbouncer=true` which psycopg2 rejects as "invalid URI query parameter." Strip it before connecting: `url = re.sub(r'[?&]pgbouncer=true', '', url)`
- Use `re.match(r'SUPABASE_OPERATOR_SPOOLER_DATABASE_URL=+["\x27]?(.*?)["\x27]?\s*$', line.strip())` for robust parsing

## Pitfalls

- **System Python is externally managed** — always install packages in `/tmp/podcast_venv/`
- **YouTube transcript API rate-limiting (CRITICAL):** Both `youtube-transcript-api` and `yt-dlp --write-auto-subs` return HTTP 429 when called rapidly. Use 90s delays overnight. Short backoffs worsen the block. Descriptions via `yt-dlp --print "%(description)s"` are NOT rate-limited.
- **Podcast websites are JS-rendered:** All major sites (allinpodcast.co, a16z.com, acquired.fm, lennysnewsletter.com) return empty pages via curl. Skip website scraping.
- **yt-dlp flat-playlist returns no channel ID:** Some handles work for channel page HTML but not for yt-dlp. Use Method A (channel page HTML) as primary discovery, yt-dlp as fallback.
- **YouTube RSS channel ID 404:** Some channel IDs return 404 from RSS endpoint even when channels exist. Known for All-In, a16z, MFM, Acquired. Use yt-dlp flat-playlist instead of RSS for video listing.
- **The ingestor is DB-driven:** Adding new channels = UPDATE podcast_kb.podcasts SET youtube_handle, channel_id. No script changes needed.
