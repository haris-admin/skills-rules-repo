---
name: video-voiceover-pipeline
description: Build a narrated product walkthrough video with ElevenLabs voiceover, frames captured from the live app, WebVTT captions, a poster and a duration cap, then put it on a site with a real accessible player. Use when a task asks for a demo or "how it works" video, a voiceover, captions, or fixing site videos that do not play. Covers keys from the secret store, cached narration, ffmpeg without text filters, loudness and duration gates, and verifying playback in real Chrome.
---

# Video and Voiceover Pipeline (ElevenLabs, frames from the live app)

Origin: HandleDispute "How it works" video, 2 to 3 Nov 2026 (OpenSpec 56, 2:54, one calm Australian voice, two linked parts).

## Order of work
1. **Script as data.** One `script.json`: `max_seconds`, voice env-var name, and scenes `{part, image, caption, text}`. About 150 words per minute; budget under the cap with headroom (a 180 s cap needs a script that lands near 170 s). No em dashes in narration or captions. Dual-purpose media never mentions the source application.
2. **Keys from the secret store.** `ELEVENLABS_API_KEY` and voice ids come from env vars, then Secrets Manager `<product>/<env>/secrets`, then a git-ignored `.env` (rule `one-secrets-store-per-environment`). Never print them. One voice for the whole piece unless the founder picks two.
3. **Narration per scene, cached.** `POST https://api.elevenlabs.io/v1/text-to-speech/{voice_id}?output_format=mp3_44100_128` with header `xi-api-key`, JSON `{text, model_id: "eleven_multilingual_v2", voice_settings}`. Save `sNN.mp3`; skip a scene whose clip exists, delete a clip to regenerate only that scene. On error report the HTTP status only.
4. **Frames from the current app.** A separate Playwright project captures 1920x1080 PNGs with the safety guard and seeded data (rule `e2e-real-backend-harness-real-otp-pinned-local-target`). Read every frame for old branding, removed links and claims (rule `public-demo-media-from-current-app-verified-in-real-browser`).
5. **Compose without text filters.** Many Homebrew ffmpeg builds lack `drawtext` and `subtitles`. Draw captions into the frame with PIL, then `ffmpeg -loop 1 -i frame.png -i clip.mp3 -af apad=pad_dur=0.4 -c:v libx264 -tune stillimage -pix_fmt yuv420p -r 25 -c:a aac -shortest`. Concatenate scene clips with the concat demuxer and apply `loudnorm=I=-14:TP=-1.5:LRA=11`.
6. **Gates in the build, not by eye.** Fail when total duration exceeds `max_seconds`; check size with `ffprobe`; build part files and the combined file; write a chapters JSON (start second of each part).
7. **Captions and poster.** Split each scene's text into sentences and spread cue times by character count into a `.vtt`; write a 1280x720 JPEG poster from frame 1.
8. **Player.** `<video controls preload="metadata" poster playsInline>` with `<source type="video/mp4">`, `<track kind="captions" srcLang="en" default>`, chapter buttons that set `currentTime` and call `play()`, and a download fallback link. No autoplay. Test first (Vitest): controls, poster, no autoplay, track attributes, chapter seek, forbidden words absent.
9. **Serve and verify.** `.vtt` must be `text/vtt` (nginx alpine mime table lacks it; add a location with `default_type text/vtt`). Check HTTP 206 on a `Range` request. Then verify on production in real Chrome (Playwright `channel: "chrome"`; bundled Chromium has no H.264): duration, 1920x1080, `error` null, cue count after setting the track to `showing`, chapter jump plays.

## Pitfalls
- A build script that ends with a bare `main()` runs on import and hangs tests (rule `scripts-tests-import-must-not-run-side-effects`).
- Reusing an image tag makes a deploy that compares tags skip the recreate; ship a new release id when only config changed.
- A mock player (thumbnail, fake progress bar) looks like a video and is not. Search for it when users report "videos don't work".
- Budget credits: regenerate only changed scenes; each narration pass costs money.
