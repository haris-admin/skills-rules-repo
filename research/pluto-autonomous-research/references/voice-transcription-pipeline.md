# Voice Message Transcription Pipeline

When a user sends a voice message and no STT provider (Whisper) is configured, use this pipeline to transcribe via OpenRouter's GPT Audio Mini model.

## Why This Exists

OpenRouter does NOT proxy OpenAI Whisper (`/v1/audio/transcriptions`). But it DOES proxy `openai/gpt-audio-mini` — a multimodal LLM that can process audio INPUT and produce text. This pipeline converts the voice message and sends it to GPT Audio Mini for transcription.

## Pipeline Steps

### 1. Find the audio file
Voice messages from Telegram arrive as `.ogg` files in `~/.hermes/audio_cache/`:
```bash
find /home/habib/.hermes/audio_cache -name "*.ogg" -newer /tmp/marker 2>/dev/null | head -5
```

### 2. Convert ogg → mp3
GPT Audio Mini only accepts `wav` and `mp3` formats. Convert using ffmpeg:
```bash
ffmpeg -y -i /path/to/audio.ogg -acodec libmp3lame -b:a 64k /tmp/voice_msg.mp3
```

If ffmpeg isn't installed, download a static build (no sudo needed):
```bash
curl -sL "https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz" -o /tmp/ffmpeg.tar.xz
cd /tmp && tar xf ffmpeg.tar.xz
/tmp/ffmpeg-*-amd64-static/ffmpeg -y -i input.ogg -acodec libmp3lame -b:a 64k output.mp3
```

pydub alone won't work — it wraps ffmpeg and needs the binary.

### 3. Encode as base64 and send to GPT Audio Mini
```python
import base64, urllib.request, json

with open('/tmp/voice_msg.mp3', 'rb') as f:
    audio_b64 = base64.b64encode(f.read()).decode()

# Get OpenRouter key from Windows or WSL .env
body = json.dumps({
    "model": "openai/gpt-audio-mini",
    "messages": [{
        "role": "user",
        "content": [
            {"type": "input_audio", "input_audio": {"data": audio_b64, "format": "mp3"}},
            {"type": "text", "text": "Transcribe this voice message to text exactly as spoken. Return ONLY the transcription."}
        ]
    }],
    "max_tokens": 300
}).encode()

req = urllib.request.Request("https://openrouter.ai/api/v1/chat/completions", data=body,
    headers={"Authorization": f"Bearer {or_key}", "Content-Type": "application/json",
             "HTTP-Referer": "https://hermes-agent.local"})

resp = urllib.request.urlopen(req, timeout=30)
data = json.loads(resp.read())
text = data["choices"][0]["message"]["content"]
```

## Cost
- GPT Audio Mini: $0.60/M prompt tokens, $2.40/M completion tokens
- Typical voice message (~30s): ~$0.0003 total
- Longer message (~2 min): ~$0.001

## Limitations
- Only `mp3` and `wav` formats accepted — NOT `ogg`
- Max audio length: ~10 minutes (model context limit)
- Not suitable for batch transcription (use direct Whisper for volume)
- Requires ffmpeg binary (static build works, no sudo needed)
- OpenRouter key must be in `~/.hermes/.env` or `/mnt/c/Users/habib/.hermes/.env`
