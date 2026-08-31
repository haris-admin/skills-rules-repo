# YouTube Cookies Export — WSL Workaround

## The Problem
As of June 2026, YouTube persistently blocks transcript requests from the WSL IP (429 on all methods). Browser cookies from a logged-in YouTube session bypass this block.

## Export Method: Chrome Extension

1. Install **"Get cookies.txt LOCALLY"** from Chrome Web Store
2. Go to https://www.youtube.com — make sure you're logged in
3. Click the extension icon → **Export** 
4. Save as `youtube_cookies.txt`
5. Move to a WSL-accessible path:
   ```
   C:\Users\habib\Downloads\youtube_cookies.txt  →  /mnt/c/Users/habib/Downloads/youtube_cookies.txt
   ```
6. Copy to Hermes dir (avoids cross-mount I/O slowness):
   ```bash
   cp /mnt/c/Users/habib/Downloads/youtube_cookies.txt /home/habib/.hermes/youtube_cookies.txt
   ```

## Usage

### yt-dlp
```bash
/tmp/podcast_venv/bin/yt-dlp --cookies /home/habib/.hermes/youtube_cookies.txt \
  --write-auto-subs --sub-format srt --skip-download \
  'https://www.youtube.com/watch?v=VIDEO_ID'
```

### youtube-transcript-api (requires cookie string, not file)
The `fetch_transcript.py` script at `skills/media/youtube-content/scripts/fetch_transcript.py` doesn't support cookies directly. Use yt-dlp for transcript extraction instead, or modify the script to accept a cookie file parameter.

## Cookie Expiry
YouTube cookies expire after ~30 days or on password change. Re-export when the 429 errors return.

## Why Not WSL Direct Cookie Access
- Chrome cookies at: `C:\Users\habib\AppData\Local\Google\Chrome\User Data\Default\Network\Cookies` (note `Network/` subdirectory)
- WSL can't read across the mount boundary: "Permission denied"
- Chrome locks the SQLite database while running
- The extension approach is the only reliable method
