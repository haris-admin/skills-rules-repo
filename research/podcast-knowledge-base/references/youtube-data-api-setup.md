# YouTube Data API v3 — Setup & Quota

## Quick Setup

1. Go to https://console.cloud.google.com/ → create project
2. Enable YouTube Data API v3 (APIs & Services → Library)
3. Generate API key (Credentials → Create Credentials → API Key)
4. Restrict key to YouTube Data API v3 only
5. Add to `.env`: `YOUTUBE_DATA_API_KEY=AIzaSy...`

## Quota

| Operation | Cost (units) |
|-----------|-------------|
| `search.list` | 100 |
| `playlistItems.list` | 1/video |
| `videos.list` | 1/video |
| `captions.list` | 1/video |
| `captions.download` | 50/caption |

**Daily usage estimate (15 podcasts, 5 new videos each):** ~5,400 units/day
**Free tier:** 10,000 units/day
**Headroom:** 46%

## API Wrapper

`scripts/youtube_api_wrapper.py` handles all YouTube API calls. Used by `podcast_ingestor.py` when `YOUTUBE_DATA_API_KEY` is set.

Usage:
```python
from youtube_api_wrapper import YouTubeAPI
yt = YouTubeAPI()  # reads YOUTUBE_DATA_API_KEY from env
channel_id = yt.search_channel("@handle")
videos = yt.list_channel_videos(channel_id, max_videos=5)
transcript = yt.get_transcript(video_id)
```

## Important

- `captions.download` requires OAuth 2.0 for some caption types. The wrapper uses the API key + direct download endpoint which works for `asr` (auto-generated) captions but may return 401 for manual captions. Fallback: use `youtube-transcript-api` `YouTubeTranscriptApi().fetch(video_id)` which is NOT rate-limited when called at low volume (<10/day).
- The wrapper auto-detects the key — when absent, falls back to yt-dlp. No code changes needed to toggle.
- Monitor quota in Google Cloud Console → APIs & Services → Quotas.
