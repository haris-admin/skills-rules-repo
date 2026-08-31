# YouTube Cookie + SAPISIDHASH Auth for Transcripts

**Discovered:** June 8, 2026
**Status:** INNERTUBE works, timedtext still IP-rate-limited

## Problem

`youtube-transcript-api` v1.2.4 and yt-dlp get blocked by YouTube's bot detection:
- INNERTUBE API returns `LOGIN_REQUIRED` / `BOT_DETECTED`
- Timedtext API returns `429 Too Many Requests`

Browser cookies (from Chrome "Get cookies.txt LOCALLY" extension) help but aren't sufficient alone.

## Solution: SAPISIDHASH Authorization

YouTube's INNERTUBE API requires a computed Authorization header for authenticated requests:

```python
import hashlib, time

SAPISID = "..."  # from cookies
origin = "https://www.youtube.com"
sapisidhash = hashlib.sha1(f"{SAPISID} {origin}".encode()).hexdigest()
auth_header = f"SAPISIDHASH {int(time.time())}_{sapisidhash}"
```

This header must be sent on INNERTUBE POST requests (`/youtubei/v1/player`).

## What Works

| Endpoint | Without Cookies | With Cookies | With Cookies + SAPISIDHASH |
|----------|----------------|--------------|---------------------------|
| Watch page (`/watch`) | 200 OK | 200 OK | 200 OK |
| INNERTUBE (`/youtubei/v1/player`) ANDROID | LOGIN_REQUIRED/BOT | LOGIN_REQUIRED/BOT | **OK (captions found)** |
| INNERTUBE (`/youtubei/v1/player`) WEB | UNPLAYABLE | UNPLAYABLE | UNPLAYABLE |
| Timedtext (`/api/timedtext`) | 429 | 429 | **429 (still IP-blocked)** |

## Key Finding

The INNERTUBE API and Timedtext API have **separate rate limits**:
- INNERTUBE: Solvable with cookies + SAPISIDHASH (ANDROID client context)
- Timedtext: Pure IP-based rate limiting — cookies don't help

## Scripts

- `/tmp/fetch_transcript_cookies.py` — Cookie+SAPISIDHASH transcript fetcher (monkey-patches youtube-transcript-api)
- `/tmp/aie_cookie_ingest.py` — Batch ingestion with progress tracking
- `/tmp/aie_progress.json` — Progress state (ingested/failed video IDs)
- `/tmp/aie_dates_state.json` — Pre-fetched episode dates (386 episodes)

## Retry Strategy

When timedtext returns 429:
1. Wait for IP cooldown (hours, not minutes — confirmed June 8)
2. Retry with `aie_cookie_ingest.py --limit 3` (small batches)
3. Progress is tracked — already-ingested episodes are skipped
4. Auto-aborts at 5 consecutive 429 failures

## Dependencies

```bash
python3 -m venv /tmp/podcast_venv
/tmp/podcast_venv/bin/pip install requests yt-dlp youtube-transcript-api
```

Cookie file: `~/.hermes/youtube_cookies.txt` (exported from Chrome)
