# Public demo media comes from the current app and is verified in a real browser

Applies to any demo video, screenshot set or walkthrough shown on a public site or shared with investors.

## Why this exists

**2 and 3 Nov 2026, handledispute.** A narrated "how it works" video was first built from September screenshots. Its first frame showed the old brand ("Undispute v0.20.0"), an "API Docs (Port 8008)" link the founder had just asked to remove, and "Resolve card disputes" copy that contradicted the any-payment positioning. The site's "videos" had also never been real: a mock player with a fake progress bar. After shipping, the captions file was served as `application/octet-stream`.

## Core Directives

1. **Capture frames from the current build** with a scripted browser run (a separate Playwright project, not the regression suite), using the same safety guard and seeded demo data. Re-capture whenever branding, links or claims change.
2. **Read every frame before publishing.** Check brand name, version strings, removed links and positioning claims. A stale frame is a defect.
3. **Dual-purpose media never mentions the source document** (an accelerator or funding application). Keep one script for both audiences and test the text for forbidden words.
4. **State only what is built.** If the pitch is broader than the product (for example other payment rails), the narration may state the positioning but the on-screen caption and the docs must say what exists today.
5. **Ship it with a real player:** `<video controls preload="metadata" poster>` with a captions `<track kind="captions" default>`, no autoplay, chapter buttons, a download link fallback.
6. **Serve it correctly:** `.vtt` as `text/vtt` (the nginx alpine mime table lacks it), `video/mp4`, and HTTP 206 on a `Range` request.
7. **Verify on production in real Chrome**, not bundled Chromium, which has no H.264. Check duration, dimensions, no media error, caption cue count, and that a chapter jump plays.
8. **Keep narration cheap and deterministic:** cache each clip, regenerate only changed scenes, enforce a duration cap in the build, and read keys from the secret store (see `one-secrets-store-per-environment`).

## Verification

A browser script against the live URL prints duration, size, `error: null`, cue count and the post-jump time.
