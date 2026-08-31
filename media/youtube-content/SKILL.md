---
name: youtube-content
description: "YouTube transcripts to summaries, threads, blogs."
platforms: [linux, macos, windows]
---

# YouTube Content Tool

## When to use

Use when the user shares a YouTube URL or video link, asks to summarize a video, requests a transcript, or wants to extract and reformat content from any YouTube video. Transforms transcripts into structured content (chapters, summaries, threads, blog posts).

Extract transcripts from YouTube videos and convert them into useful formats.

## Setup

```bash
pip install youtube-transcript-api
```

## Helper Script

`SKILL_DIR` is the directory containing this SKILL.md file. The script accepts any standard YouTube URL format, short links (youtu.be), shorts, embeds, live links, or a raw 11-character video ID.

```bash
# JSON output with metadata
python3 SKILL_DIR/scripts/fetch_transcript.py "https://youtube.com/watch?v=VIDEO_ID"

# Plain text (good for piping into further processing)
python3 SKILL_DIR/scripts/fetch_transcript.py "URL" --text-only

# With timestamps
python3 SKILL_DIR/scripts/fetch_transcript.py "URL" --timestamps

# Specific language with fallback chain
python3 SKILL_DIR/scripts/fetch_transcript.py "URL" --language tr,en
```

## Output Formats

After fetching the transcript, format it based on what the user asks for:

- **Chapters**: Group by topic shifts, output timestamped chapter list
- **Summary**: Concise 5-10 sentence overview of the entire video
- **Chapter summaries**: Chapters with a short paragraph summary for each
- **Thread**: Twitter/X thread format — numbered posts, each under 280 chars
- **Blog post**: Full article with title, sections, and key takeaways
- **Quotes**: Notable quotes with timestamps

### Example — Chapters Output

```
00:00 Introduction — host opens with the problem statement
03:45 Background — prior work and why existing solutions fall short
12:20 Core method — walkthrough of the proposed approach
24:10 Results — benchmark comparisons and key takeaways
31:55 Q&A — audience questions on scalability and next steps
```

## Workflow

1. **Fetch** the transcript using the helper script with `--text-only --timestamps`.
2. **Validate**: confirm the output is non-empty and in the expected language. If empty, retry without `--language` to get any available transcript. If still empty, tell the user the video likely has transcripts disabled.
3. **Chunk if needed**: if the transcript exceeds ~50K characters, split into overlapping chunks (~40K with 2K overlap) and summarize each chunk before merging.
4. **Transform** into the requested output format. If the user did not specify a format, default to a summary.
5. **Verify**: re-read the transformed output to check for coherence, correct timestamps, and completeness before presenting.

## Error Handling
## Pitfalls
- **YouTube RSS feeds are rate-limited.** After 3-5 RSS feed fetches in a session, YouTube starts returning 404 for ALL channels — even ones that previously returned valid XML. This is not per-channel blocking; it's session-level rate limiting. **Always prefer yt-dlp for channel discovery** in batch workflows. RSS is suitable for a single one-off channel lookup but not for multi-channel ingestion pipelines (June 2026).
- **RSS feeds may return IPv6-only DNS for some channels**, making them unreachable from WSL. yt-dlp handles DNS resolution better and works reliably from WSL.
- **System Python is externally managed on modern Ubuntu.** Always create a temp venv for dependencies: `python3 -m venv /tmp/yt_venv && /tmp/yt_venv/bin/pip install yt-dlp youtube-transcript-api`.
- **yt-dlp --flat-playlist does not include upload dates.** Use without `--flat-playlist` for date filtering, at the cost of slower listing. For channels with 100+ videos, limit with `--playlist-end N`.

## Error Handling
- **Transcript disabled**: tell the user; suggest they check if subtitles are available on the video page.
- **Private/unavailable video**: relay the error and ask the user to verify the URL.
- **No matching language**: retry without `--language` to fetch any available transcript, then note the actual language to the user.
- **Dependency missing**: run `pip install youtube-transcript-api` and retry. If system Python is externally managed, create a temp venv: `python3 -m venv /tmp/yt_venv && /tmp/yt_venv/bin/pip install youtube-transcript-api`.

## Channel-Level Knowledge Extraction (NEW — June 2026)

When the user shares a channel URL (`youtube.com/@handle`) and wants a knowledge base from all episodes, use this pipeline. Proven on @moonshotsclips (15 episodes, 110KB transcripts → knowledge base with frameworks + quiz questions).

### Step 1: Discover videos via channel RSS (yt-dlp preferred)

**Method A: yt-dlp (recommended — reliable, includes dates)**
```bash
# Install both tools in a venv
python3 -m venv /tmp/yt_venv && /tmp/yt_venv/bin/pip install yt-dlp youtube-transcript-api

# List videos with titles, IDs, and upload dates
/tmp/yt_venv/bin/yt-dlp --playlist-end 20 --print "%(title)s||%(id)s||%(upload_date)s" \
  --no-warnings "https://www.youtube.com/@HANDLE"
```
Output format: `Title||videoID||YYYYMMDD` — one per line. Parse by splitting on `||`. Filter by date to get the desired range (e.g., `20260101`+ for 2026).

**Method B: YouTube RSS (fallback — rate-limited)**

Extract the channel ID from the page, then fetch the RSS feed:
```bash
# Get channel ID
curl -sL -A "Mozilla/5.0" "https://www.youtube.com/@HANDLE" | grep -oP 'channel_id=([a-zA-Z0-9_-]+)' | head -1

# Fetch RSS (returns last 15 videos)
curl -sL -A "Mozilla/5.0" -o /tmp/channel_rss.xml \
  "https://www.youtube.com/feeds/videos.xml?channel_id=CHANNEL_ID"
```

Parse with Python: `re.findall(r'<entry>(.*?)</entry>', data, re.DOTALL)` to extract `<title>`, `<link>` (for video ID via `v=VIDEOID`), and `<published>`.

### Step 2: Batch download all transcripts

Use the helper script from a venv with `youtube-transcript-api` installed:
```bash
mkdir -p /tmp/channel_transcripts
for vid in VIDEO_ID1 VIDEO_ID2 ...; do
  /tmp/yt_venv/bin/python3 SKILL_DIR/scripts/fetch_transcript.py "$vid" --text-only \
    > "/tmp/channel_transcripts/${vid}.txt"
done
```

**Venv setup** (if youtube-transcript-api not in system Python):
```bash
python3 -m venv /tmp/yt_venv && /tmp/yt_venv/bin/pip install youtube-transcript-api
```

### Step 3: Extract knowledge base

Read each transcript and extract:
- **Core idea** — the central argument or theme (1 paragraph)
- **Key framework** — any named model, matrix, or mental model discussed
- **One quiz question + answer** — thought-provoking, not trivia (e.g., "Why is X broken in the age of AI?" not "What are the six dimensions?")
- **Episode metadata** — date, title, type (trend/threat/opportunity/market)

### Step 4: Structure as knowledge base JSON

Output to `~/.hermes/research_outputs/[channel]-knowledge-base.json`:
```json
{
  "topic": "Channel Name — Knowledge Base",
  "tags": ["relevant", "tags"],
  "meta": { "source": "channel URL", "total_episodes": N },
  "findings": [
    {
      "title": "Episode title",
      "content": "Synthesized core idea...",
      "confidence": "high",
      "url": "https://youtube.com/watch?v=VIDEO_ID",
      "type": "trend|threat|market|opportunity",
      "episode_date": "YYYY-MM-DD",
      "key_framework": "Named framework from episode",
      "quiz_question": "Thought-provoking question?",
      "quiz_answer": "Concise answer with context"
    }
  ]
}
```

**Quiz question quality:** Questions should test understanding, not recall. Ask about implications, paradoxes, or counterarguments — not lists of dimensions. Good: "Why is GDP fundamentally broken in the age of AI?" Bad: "What are the six dimensions of personhood?"

### Step 5: Feed to MemPalace

```bash
python3 ~/.hermes/scripts/pluto_mempalace_feeder.py \
  --input [channel]-knowledge-base.json \
  --topic "Channel Name Knowledge Base" \
  --tags "comma,separated,tags" \
  --source "channel_name_transcripts"
```

The feeder auto-routes to the best-fit chamber. Check with `--status` to confirm.

### Step 6: Set up daily learning (optional)

If the user wants a daily learning session from the knowledge base, create a cron job:
```
Name: [Channel] Daily Learning
Schedule: user's preferred time (e.g., 6:15 AM AEST = 15 20 * * *)
Toolsets: terminal, file, skills
Skills: pluto-mempalace-bridge, pluto-morning-briefing
Prompt: "Pick a random topic from the [chamber] MemPalace chamber. Teach the concept in 300-400 words, connect to Haris's portfolio, and ask one quiz question."
```

See `pluto-morning-briefing-v2` skill → `references/daily-learning-format.md` for the proven delivery format.
