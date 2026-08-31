# TTS Voice Migration — June 9, 2026

## Migration: Edge → OpenAI Nova

- **Before:** Microsoft Edge TTS (`en-US-AriaNeural`) — functional but robotic
- **After:** OpenAI TTS (`gpt-4o-mini-tts`), voice `nova` — warm, natural female

## Config

```yaml
tts:
  provider: openai
  openai:
    model: gpt-4o-mini-tts
    voice: nova
```

## Voice Selection (tested June 9)

Haris tested 3 voices with technical fintech/regulatory content (AUSTRAC, AML, AI Regulation terms):

| Voice | Character | Result |
|-------|-----------|--------|
| **nova** ✅ | Warm, natural female | Selected — handles technical terms smoothly |
| fable | British, expressive female | Tested — too distinctive for daily briefings |
| shimmer | Clear, crisp female | Tested — good precision but less warmth |

## Cost

OpenAI TTS: ~$0.015 per 1,000 characters (gpt-4o-mini-tts). A typical 500-word briefing ≈ $0.03-0.05.

## Fallback

gTTS (free Google TTS) remains as fallback if OpenAI key is unavailable.

## User Preference

"Voice is our major medium. We have lots of technical terms so voice only doesn't work that well." — Haris, June 9

→ Deliver voice + text simultaneously. Not voice-first, not text-only. Both together.
