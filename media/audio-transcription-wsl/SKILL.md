---
name: audio-transcription-wsl
description: Transcribe .ogg notes on WSL via Whisper + Windows ffmpeg.
version: 1.0.0
author: Pluto
license: MIT
---

# Audio Transcription on WSL

Transcribe user voice messages (Telegram `.ogg`/Opus files in `~/.hermes/cache/audio/` or `~/.hermes/audio_cache/`) to text on WSL without sudo.

## When to Use
- Hermes says "voice message could not be transcribed automatically; audio available at <path>.ogg"
- User sends voice notes regularly (Haris communicates via voice notes)
- Any local audio file needs speech-to-text

## Method A — Local Whisper (FREE, verified Aug 2026) — PREFERRED

Whisper is installed at `~/.local/bin/whisper`. The blocker is ffmpeg: **WSL has NO system ffmpeg, and Playwright's bundled `ffmpeg-linux` LACKS opus support** (`Error opening input file ... Invalid data found`). Use the **Windows WinGet ffmpeg 8.1 full build** via a PATH shim.

```bash
# 1. Find the Windows ffmpeg (full build — has opus; Playwright's does not)
WINFF=$(ls /mnt/c/Users/habib/AppData/Local/Microsoft/WinGet/Packages/Gyan.FFmpeg*/ffmpeg-*/bin/ffmpeg.exe 2>/dev/null | head -1)
# (or: where.exe ffmpeg  from cmd.exe)

# 2. Convert ogg → wav (16kHz mono for whisper)
"$WINFF" -y -i /path/to/audio.ogg -ar 16000 -ac 1 /tmp/voice_msg.wav

# 3. Whisper insists on calling 'ffmpeg' by name — create a PATH shim
mkdir -p /tmp/ffshim
ln -sf "$WINFF" /tmp/ffshim/ffmpeg
chmod +x /tmp/ffshim/ffmpeg

# 4. Transcribe (base model is fine for short messages)
cd /tmp && PATH="/tmp/ffshim:$PATH" whisper /tmp/voice_msg.wav \
  --model base --language English --output_format txt --output_dir /tmp/whisper_out
cat /tmp/whisper_out/*.txt
```

Notes:
- `whisper` itself will fail with `FileNotFoundError: [Errno 2] No such file or directory: 'ffmpeg'` if the shim isn't on PATH — the shim step is mandatory.
- "FP16 is not supported on CPU; using FP32 instead" warning is harmless.
- ~10s audio → under 10s transcription on CPU with `base` model.

## Method B — OpenRouter gpt-audio-mini (cost ~$0.0003/msg)

When local whisper is unavailable or audio is long. Full pipeline lives in `pluto-autonomous-research` skill → `references/voice-transcription-pipeline.md` (user-owned): ogg→mp3 via static ffmpeg, base64 encode, POST to `openai/gpt-audio-mini` on OpenRouter. Only accepts mp3/wav — never raw ogg.

## Pitfalls
1. **Playwright's ffmpeg-linux does NOT decode Opus** — always use Windows WinGet ffmpeg or a static build, never `~/.cache/ms-playwright/ffmpeg-*/ffmpeg-linux` for .ogg input.
2. **whisper calls `ffmpeg` by name** — PATH shim required; exporting LD_LIBRARY_PATH or passing an env var for the binary does NOT help.
3. **`file` the input first** if conversion fails — confirm it's actually Ogg/Opus (`Ogg data, Opus audio`) before debugging the converter.
4. The WinGet ffmpeg path embeds a version dir (`ffmpeg-8.1-full_build`) — glob it, don't hardcode.
