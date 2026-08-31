#!/usr/bin/env python3
"""
YouTube Data API v3 Wrapper — for podcast ingestion pipeline.

Two modes:
  1. API mode (requires YOUTUBE_DATA_API_KEY in env) — uses proper API calls
  2. Fallback mode — uses yt-dlp (current scrape approach)

See also: ~/.hermes/scripts/youtube_api_wrapper.py (canonical copy)

Usage:
  from youtube_api_wrapper import YouTubeAPI
  
  yt = YouTubeAPI(api_key="YOUR_KEY")  # or None for fallback
  videos = yt.list_channel_videos("@handle", max_videos=15)
  captions = yt.get_captions("video_id")
  transcript = yt.download_transcript("video_id")
"""

import os
import json
import time
import urllib.request
import urllib.parse
import urllib.error
import re

API_BASE = "https://www.googleapis.com/youtube/v3"

class YouTubeAPI:
    """Wrapper for YouTube Data API v3 with fallback to yt-dlp."""
    
    def __init__(self, api_key=None):
        self.api_key = api_key or os.environ.get("YOUTUBE_DATA_API_KEY", "")
        self._use_api = bool(self.api_key)
    
    def _api_get(self, endpoint, params=None):
        if params is None:
            params = {}
        params["key"] = self.api_key
        url = f"{API_BASE}/{endpoint}?{urllib.parse.urlencode(params)}"
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "PlutoPodcast/1.0"})
            with urllib.request.urlopen(req, timeout=15) as resp:
                return json.loads(resp.read().decode())
        except urllib.error.HTTPError as e:
            body = e.read().decode() if e.fp else ""
            print(f"  ⚠️  YouTube API error {e.code}: {body[:200]}")
            return None
        except Exception as e:
            print(f"  ⚠️  YouTube API request failed: {e}")
            return None
    
    def search_channel(self, handle_or_name):
        """Find a channel by handle or name. Returns channel_id or None."""
        clean = handle_or_name.lstrip("@")
        data = self._api_get("search", {"part": "snippet", "q": clean, "type": "channel", "maxResults": 1})
        if data and "items" in data and data["items"]:
            return data["items"][0]["snippet"]["channelId"]
        data = self._api_get("channels", {"part": "id", "forHandle": clean})
        if data and "items" in data and data["items"]:
            return data["items"][0]["id"]
        return None
    
    def list_channel_videos(self, channel_id, max_videos=15, since_date=None):
        """List recent videos from a channel. Returns [{title, youtube_id, published_date}]."""
        uploads_data = self._api_get("channels", {"part": "contentDetails", "id": channel_id})
        if not uploads_data or not uploads_data.get("items"):
            return []
        uploads_id = uploads_data["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]
        
        videos = []
        page_token = ""
        while len(videos) < max_videos:
            params = {"part": "snippet", "playlistId": uploads_id, "maxResults": min(50, max_videos - len(videos))}
            if page_token:
                params["pageToken"] = page_token
            data = self._api_get("playlistItems", params)
            if not data or "items" not in data:
                break
            for item in data["items"]:
                snippet = item.get("snippet", {})
                video_id = snippet.get("resourceId", {}).get("videoId")
                title = snippet.get("title", "")
                published = snippet.get("publishedAt", "")[:10]
                if video_id:
                    if since_date and published < since_date:
                        continue
                    videos.append({"title": title, "youtube_id": video_id, "published_date": published})
            page_token = data.get("nextPageToken", "")
            if not page_token:
                break
            time.sleep(0.1)
        return videos[:max_videos]
    
    def list_captions(self, video_id):
        """List available caption tracks. Returns [{language, id, kind}]."""
        data = self._api_get("captions", {"part": "snippet", "videoId": video_id})
        if data and "items" in data:
            return [{"language": i.get("snippet", {}).get("language","?"), "id": i.get("id",""), "kind": i.get("snippet",{}).get("trackKind","")} for i in data["items"]]
        return []
    
    def download_caption(self, caption_id):
        """Download caption track, strip SRT formatting. Returns text or None."""
        url = f"{API_BASE}/captions/{caption_id}?key={self.api_key}&tfmt=srt"
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "PlutoPodcast/1.0"})
            with urllib.request.urlopen(req, timeout=30) as resp:
                srt_text = resp.read().decode("utf-8", errors="replace")
            lines = [l.strip() for l in srt_text.split("\n") 
                     if l.strip() and not re.match(r'^\d+$', l) and not re.match(r'^\d{2}:\d{2}:\d{2}', l)]
            text = " ".join(lines)
            return text if len(text) > 200 else None
        except Exception as e:
            print(f"  ⚠️  Caption download failed: {e}")
            return None
    
    def get_transcript(self, video_id):
        """Full pipeline: find captions → download best → return text. ~51 units."""
        if not self._use_api:
            return None
        captions = self.list_captions(video_id)
        if not captions:
            return None
        en = [c for c in captions if c.get("language","").startswith("en")]
        target = en[0] if en else captions[0]
        return self.download_caption(target["id"])
    
    @property
    def is_ready(self):
        return self._use_api
