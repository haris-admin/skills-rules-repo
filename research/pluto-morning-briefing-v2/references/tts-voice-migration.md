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

## User Preference (June 9)

"Voice is our major medium. We have lots of technical terms so voice only doesn't work that well."

→ Deliver voice + text **together**. Both formats, simultaneously. Not voice-first. Not text-only.
