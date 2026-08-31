# yt-dlp Android Client Transcript Approach (June 8, 2026)

## The Problem

YouTube's web client requires solving a JavaScript "n challenge" (bot detection). Even with `yt-dlp-ejs` installed, the n challenge often fails in the Hermes sandbox. Additionally, the subtitle download endpoint (`/api/timedtext`) has SEPARATE rate limiting from video download — you can download video formats but get HTTP 429 on subtitles.

## The Solution: Android Client

The Android client bypasses the n challenge entirely:

```bash
/tmp/podcast_venv/bin/yt-dlp \
  --extractor-args "youtube:player_client=android" \
  --write-auto-subs --sub-lang en --sub-format srt --skip-download \
  --sleep-requests 2 --sleep-interval 2 \
  -o "/tmp/subtitle" "<video_id>"
```

### Why It Works
- Mobile APIs don't enforce the web client's n challenge
- Subtitles are found reliably (confirmed with _B4Pv9ttFgY, pmoDeA3RBZY, etc.)
- Works WITHOUT cookies for transcript-only operations

### Limitations
- Cookies NOT supported with android client (web-only)
- Still subject to IP rate limiting (HTTP 429 after ~14-18 requests)
- Rate limit is per-session, not per-day — clears after cooldown period

## Extracting Text from SRT

```python
import os

sub_file = '/tmp/aie_sub_VIDEO_ID.en.srt'
if os.path.exists(sub_file):
    with open(sub_file, 'r', encoding='utf-8') as f:
        raw = f.read()
    lines = []
    for line in raw.split('\n'):
        line = line.strip()
        if line and not line.isdigit() and '-->' not in line:
            lines.append(line)
    transcript = ' '.join(lines)
    os.remove(sub_file)
```

## Rate Limiting Strategy

- 14-18 successful downloads per IP session
- Auto-abort at 5 consecutive failures
- 2-3 second delays between requests
- The daily cron design (12:35 AM, few episodes per show) aligns with this

## Dependencies

```bash
/tmp/podcast_venv/bin/pip install yt-dlp  # v2026.03.17+
```

## Integration in aie_chamber_ingest.py

The script at `/tmp/aie_chamber_ingest.py` was updated June 8 to use this approach:
- Replaces `youtube-transcript-api` with yt-dlp android client
- Detects 429 rate limits and auto-aborts
- Strips SRT formatting for clean text
- Supports `--limit` and `--dry-run` flags
