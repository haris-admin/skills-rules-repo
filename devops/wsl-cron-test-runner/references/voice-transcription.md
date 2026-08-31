# Voice Message Transcription (WSL) — Local Whisper + Windows ffmpeg

Verified Aug 2026. Two paths: **local Whisper (free, preferred)** and **OpenRouter GPT Audio Mini (fallback)**.

## When to use
- User sends a Telegram voice message (`audio_<hash>.ogg` in `~/.hermes/cache/audio/`)
- Auto-transcription failed / no STT provider is wired to the gateway
- Need the exact spoken text (transcription), not a summary

## Path 1: Local Whisper (free — preferred)

Whisper IS installed on WSL at `~/.local/bin/whisper`. It shells out to the exact binary name `ffmpeg`, which WSL lacks. Windows has a full ffmpeg 8.1 build via WinGet.

### The ffmpeg shim trick (no sudo)

Playwright's bundled `ffmpeg-linux` (`~/.cache/ms-playwright/ffmpeg-1011/ffmpeg-linux`) is a **stripped build without Opus/Ogg demuxing** — it fails with `Invalid data found when processing input` on Telegram `.ogg` files. The Windows WinGet ffmpeg is a full build that handles Opus fine:

```bash
# 1) Convert ogg → wav 16kHz mono with the WINDOWS ffmpeg:
WINFF="/mnt/c/Users/habib/AppData/Local/Microsoft/WinGet/Packages/Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe/ffmpeg-8.1-full_build/bin/ffmpeg.exe"
"$WINFF" -y -i input.ogg -ar 16000 -ac 1 /tmp/voice_msg.wav

# 2) Create a PATH shim so whisper finds `ffmpeg` (whisper calls the exact name):
mkdir -p /tmp/ffshim
ln -sf "$WINFF" /tmp/ffshim/ffmpeg
chmod +x /tmp/ffshim/ffmpeg

# 3) Transcribe:
PATH="/tmp/ffshim:$PATH" whisper /tmp/voice_msg.wav --model base --language English \
  --output_format txt --output_dir /tmp/whisper_out
cat /tmp/whisper_out/*.txt
```

Whisper notes:
- CPU-only prints `FP16 is not supported on CPU; using FP32 instead` — harmless warning.
- `base` model is accurate enough for short voice notes; `small`/`medium` for noisy audio.
- Verify container with `file` first (should say `Ogg data, Opus audio`); if not ogg, inspect the actual container before converting.
- Telegram voice messages land in `~/.hermes/cache/audio/` (e.g. `audio_<hash>.ogg`). Find recent ones with `find ~/.hermes/cache/audio -name "*.ogg" -newer /tmp/marker 2>/dev/null | head -5`.

## Path 2: OpenRouter GPT Audio Mini (fallback)

OpenRouter does NOT proxy OpenAI Whisper (`/v1/audio/transcriptions`). It DOES proxy `openai/gpt-audio-mini` — a multimodal LLM that accepts audio INPUT.

1. Convert ogg → mp3 (any full ffmpeg; static build from johnvansickle.com works, no sudo).
2. base64-encode, POST to `https://openrouter.ai/api/v1/chat/completions` with model `openai/gpt-audio-mini`, content `[{"type":"input_audio","input_audio":{"data":b64,"format":"mp3"}},{"type":"text","text":"Transcribe this voice message exactly as spoken. Return ONLY the transcription."}]`.
3. Cost: ~$0.0003 per 30s message. Limits: mp3/wav only (not ogg), ~10 min max audio.

(Full fallback code sample lives in the user-owned `pluto-autonomous-research` skill → `references/voice-transcription-pipeline.md`; the local-whisper path above supersedes its ffmpeg section.)
