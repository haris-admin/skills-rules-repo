---
name: nano-banana-pro
description: Generate or edit images via Gemini's Nano Banana image models (default gemini-3.1-flash-image), including multi-image composition (up to 14 images) and 1K/2K/4K resolutions. Use when asked to generate an image from a prompt, edit an existing image, or combine multiple images into one scene.
homepage: https://ai.google.dev/
metadata:
  {
    "openclaw":
      {
        "emoji": "🍌",
        "requires": { "bins": ["uv"], "env": ["GEMINI_API_KEY"] },
        "primaryEnv": "GEMINI_API_KEY",
        "install":
          [
            {
              "id": "uv-brew",
              "kind": "brew",
              "formula": "uv",
              "bins": ["uv"],
              "label": "Install uv (brew)",
            },
          ],
      },
  }
---

# Nano Banana Pro (Gemini Flash Image)

Use the bundled script to generate or edit images.

Generate

```bash
uv run {baseDir}/scripts/generate_image.py --prompt "your image description" --filename "output.png" --resolution 1K
```

Edit (single image)

```bash
uv run {baseDir}/scripts/generate_image.py --prompt "edit instructions" --filename "output.png" -i "/path/in.png" --resolution 2K
```

Multi-image composition (up to 14 images)

```bash
uv run {baseDir}/scripts/generate_image.py --prompt "combine these into one scene" --filename "output.png" -i img1.png -i img2.png -i img3.png
```

Model selection

- Defaults to `gemini-3.1-flash-image` — the latest Flash-tier model that actually supports image
  output as of 2026-09-17 (verified by listing models against a live key). **`gemini-3.8-flash`
  looks like the newer/"latest" Flash model by version number, but it is text/multimodal-input
  only and silently returns no image data (sometimes a text description, sometimes nothing) if
  you pass it here** — the flash-tier text line and the flash-tier image-generation line advance
  independently, and "3.8" only exists on the text line. If a future session needs to re-check
  what's current, list models and filter for `image` in the name/actions rather than assuming the
  highest version number is image-capable.
- Override with `--model <name>` (e.g. `--model gemini-3-pro-image-preview` for the Pro tier).

API key

- `GEMINI_API_KEY` env var
- Or set `skills."nano-banana-pro".apiKey` / `skills."nano-banana-pro".env.GEMINI_API_KEY` in `~/.openclaw/openclaw.json`

Notes

- Resolutions: `1K` (default), `2K`, `4K`.
- Use timestamps in filenames: `yyyy-mm-dd-hh-mm-ss-name.png`.
- The script prints a `MEDIA:` line for OpenClaw to auto-attach on supported chat providers.
- Do not read the image back; report the saved path only.
