---
name: pluto-voice-overview
description: Pluto's voice overview pipeline — converts daily research JSON outputs to spoken MP3 briefings via OpenAI TTS (Nova voice) and delivers them on Telegram as audio messages. Use when managing, debugging, or extending the voice pipeline.
allowed-tools: [terminal, file, cronjob, text_to_speech]
---

# Pluto Voice Overview Pipeline

## When to Use
- Managing the daily voice briefing pipeline
- Debugging audio generation issues
- Adding voice output to new research workflows
- Testing or manually triggering a voice overview

## Architecture

```
Daily Research Cron (b0de180cec84)
  └─ 5:05 AM AEST daily ─ generates research_*.json
       │
       ▼ (Synth + Action Bridge run at 5:10-5:15, Briefing Improver at 5:20)
Voice Overview Cron (c527fed4a1da)
  └─ 10:15 PM AEST daily ─ reads JSONs → TTS → MP3
       │
       ├─ Primary: OpenAI TTS (Nova voice, gpt-4o-mini-tts)
       │    └─ Provider set via Hermes config (tts.provider: openai)
       ├─ Fallback: gTTS (free, Google TTS API)
       └─ Fail: script exits code 1 ("No research found")
       │
       ▼
  Telegram audio delivery (MEDIA: mp3) + text summary
```

### TTS Provider Chain
1. **OpenAI TTS** — `gpt-4o-mini-tts` model, voice `nova` (warm, natural female). Chosen June 9 after A/B testing nova/fable/shimmer with technical content. Costs ~$0.015 per 1,000 characters.
   - Provider configured in `~/.hermes/config.yaml`: `tts.provider: openai`, `tts.openai.voice: nova`
   - Key must be in `OPENAI_API_KEY` in `~/.hermes/.env` or `/mnt/c/Users/habib/.hermes/.env`
   - If API call fails OR key missing: falls through to gTTS
2. **gTTS** — Free Google TTS engine (fallback only). Always works with internet. Lower quality — no voice selection.
3. **OpenRouter limitation:** OpenRouter does NOT proxy OpenAI TTS endpoints — only multimodal audio input models (`openai/gpt-audio-mini`). For TTS output, you need a direct OpenAI API key. The config calls OpenAI's TTS endpoint directly, not via OpenRouter.

## Script: voice_overview.py

Location: `~/.hermes/scripts/voice_overview.py`
Output: `~/.hermes/voice_outputs/pluto_briefing_YYYY-MM-DD.mp3`

### Usage
```bash
# Today's research
python3 ~/.hermes/scripts/voice_overview.py

# Specific date
python3 ~/.hermes/scripts/voice_overview.py 2026-05-22

# Text preview only (no audio generation)
python3 ~/.hermes/scripts/voice_overview.py --preview

# Full text, skip audio
python3 ~/.hermes/scripts/voice_overview.py --text-only
```

### What It Does
1. Loads all `research_*.json` files from `~/.hermes/research_outputs/` and filters by date substring
2. Matches **both** filename conventions: `research_DATE.json` (new format) and `research_TOPIC_DATE.json` (old format)
3. Formats a natural spoken briefing (intro → topics → findings with type labels → outro)
4. Condenses each finding to first 2 sentences (max ~280 chars) for listenability
5. Generates MP3 via OpenAI TTS (if key available) or gTTS fallback
6. Saves to `~/.hermes/voice_outputs/`

### Voice Message Transcription (related capability)
For transcribing user voice messages when no STT provider is configured, see `pluto-autonomous-research` skill → `references/voice-transcription-pipeline.md`. Uses OpenRouter's `openai/gpt-audio-mini` ($0.60/$2.40 per 1M tokens) with ogg→mp3 conversion via ffmpeg. Cost: ~$0.0003 per message.

### Finding Type Labels
- threat → "Threat alert"
- regulatory → "Regulatory update"  
- opportunity → "Opportunity"
- trend → "Trend"
- technical → "Technical insight"
- market → "Market update"

## Cron Job

| Field | Value |
|---|---|
| Job ID | `c527fed4a1da` |
| Schedule | `15 22 * * *` (10:15 PM AEST daily) |
| Chained from | Research cron `b0de180cec84` (5:05 AM, generates research JSONs) |
| Gap | ~17 hours between research and voice generation — intentional buffer |
| Delivery | Origin (Telegram DM to Haris) |
| Toolsets | terminal, file |

## Pitfalls
- gTTS downgrades `click` to 8.1.8 (typer needs 8.2.1+). Non-blocking — gTTS works fine despite the pip warning. If typer breaks, reinstall click 8.4.0.
- gTTS requires internet (calls Google TTS API). No offline fallback.
- If no research JSONs exist for the date, script exits with code 1 and message "No research found"
- Audio files accumulate in `voice_outputs/` — consider periodic cleanup
- The script condenses findings to 2 sentences max. For full-content audio, modify `format_briefing()` to include all sentences.
- **Dual filename convention:** Research outputs use two naming patterns: `research_DATE.json` (new, e.g. `research_2026-05-31.json`) and `research_TOPIC_DATE.json` (old, e.g. `research_cloud_fintech_2026-05-22.json`). The glob pattern `research_*_{date}.json` only matches the OLD format — the underscore before the date breaks matching for new-format files. As of May 31, 2026, the script uses `glob("research_*.json")` + date-substring filtering to match both conventions.
