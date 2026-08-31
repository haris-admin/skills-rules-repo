# YouTube Data API v3 — Credential Setup & Integration

## Setup (5 min)

1. Go to https://console.cloud.google.com/ → Create project or select existing
2. **APIs & Services → Library** → Enable "YouTube Data API v3"
3. **APIs & Services → Credentials** → Create Credentials → API Key
4. **Restrict key:** Under "API restrictions", select "YouTube Data API v3" only. Under "Application restrictions", use "IP addresses" (static IP) or "None" (dynamic IP).
5. Copy the key (starts with `AIzaSy...`)

## Env File Placement

**Must be in both locations:**
- `/mnt/c/Users/habib/.hermes/.env` (Windows) — for manual terminal sessions
- `~/.hermes/.env` (WSL) — for cron `no_agent` scripts

Add to `.env`:
```
YOUTUBE_DATA_API_KEY=AIzaSy...
```

## Quota

Free tier: **10,000 units/day**

| Operation | Cost | Daily Usage (15 podcasts × 5 videos) |
|-----------|------|--------------------------------------|
| `search.list` (find channel) | 100 | 15 × 100 = 1,500 |
| `playlistItems.list` (list videos) | 1/video | 75 × 1 = 75 |
| `captions.list` (list captions) | 1/video | 75 × 1 = 75 |
| `captions.download` (get text) | 50/video | 75 × 50 = 3,750 |
| **Total** | | **~5,400 units/day (54%)** |

## Script

**`~/.hermes/scripts/youtube_api_wrapper.py`** provides:
- `search_channel(handle)` → channel_id
- `list_channel_videos(channel_id, max_videos, since_date)` → [{title, youtube_id, published_date}]
- `get_transcript(video_id)` → text (uses youtube-transcript-api v2, not API download)

**Note on captions.download:** Requires OAuth 2.0, not just API key. The wrapper uses `youtube-transcript-api` (`YouTubeTranscriptApi().fetch(video_id)`) for transcripts instead. This works without OAuth and is not IP-blocked when called at low volume (~5 calls/day).

## Fallback Behavior

The podcast ingestor auto-detects the key:
- **Key present** → uses YouTube API for channel/video discovery (reliable, fast)
- **Key absent** → falls back to yt-dlp (IP-blocked for most channels)

Test with:
```bash
export YOUTUBE_DATA_API_KEY=AIzaSy...
python3 /home/habib/.hermes/scripts/youtube_api_wrapper.py "$YOUTUBE_DATA_API_KEY" "@channel_handle"
```
