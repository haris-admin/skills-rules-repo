---
name: harishabib-blog-hero-images
description: "Use when making a harishabib.au blog hero image."
platforms: [linux, macos, windows]
---

# harishabib.au blog hero images

Every post in `harishabib_au_code` carries a `heroImage`: a hand-authored **whiteboard SVG** in a
fixed house style. **There is no generator** — you copy the house template, fill it, and then
**rasterise and look at it** before calling it done.

## Repo, branch, and where the asset goes

- LIVE repo: `/mnt/c/Code/gitlab/harishabib_au_code` (GitLab `hhsiddiqui/harishabib_au_code`).
- **`main` is PRODUCTION.** Netlify builds `main`, so pushing there publishes in ~2 min.
- Do the work on the **working branch** (`pluto_br`) and push that — checking in is not publishing.
  Confirm the split before committing: `origin/HEAD -> main` on one side, and a branch carrying
  pending content commits on the other. Never assume "commit to main" is the safe move.
- Asset: `public/images/whiteboard-<slug>.svg`. Wire it in the post frontmatter as
  `heroImage: "/images/whiteboard-<slug>.svg"` (optional per the schema; universal by convention).

## House style — copy the template

`templates/whiteboard-hero-1600x1120.svg` is the skeleton; replace its content, keep its geometry.
A live reference is `public/images/whiteboard-cloud-first-policy.svg`.

- **1600×1120** `viewBox`, with `width`/`height` set.
- Outer `#f6f2e8`; inner card `#fbfaf7` with `stroke="#d7d2c7"` and an `feDropShadow` filter.
- Corner brackets, `stroke="#2d2d2d" stroke-width="6"`.
- Centred 54px/800 title, blue rule `#1d4ed8`, two-line subtitle.
- 2×2 numbered cards (blue `#1d4ed8` → green `#047857`) plus an amber `#b45309` wide footer card.
- Bullets are 12×12 squares, `fill="rgba(4,120,87,0.08)" stroke="#047857"`.
- Close with a tag line, a `#d7d2c7` divider, footnotes, and bottom-right `harishabib.au · <section>`.

## Procedure

1. Copy the template to `public/images/whiteboard-<slug>.svg`.
2. Fill it with the post's **thesis and its numbers** — the figures that carry the argument, not prose.
3. **Render it and LOOK at it** (below). This step is mandatory.
4. Fix whatever the render exposes; re-render until clean.
5. Add `heroImage` to the post frontmatter.
6. `npm run build` — must pass (it validates the frontmatter and renders the post).
7. Commit the SVG **and** the frontmatter change together; push the working branch.

## Render-and-inspect loop (mandatory)

Text overflow and clipping are **invisible in the SVG source** — a line that runs past its card looks
perfectly fine in markup and is cut off in the render. Always rasterise and view it.

No system converter is installed; **use the repo's own `sharp`**, which Astro already depends on:

```js
// render_hero.cjs — the .cjs extension is required (see pitfalls)
const sharp = require('sharp');
const fs = require('fs');
sharp(fs.readFileSync('public/images/whiteboard-<slug>.svg'), { density: 144 })
  .resize(1400).png().toFile('/tmp/hero-check.png')
  .then(i => console.log('ok', i))
  .catch(e => { console.error('FAILED', e.message); process.exit(1); });
```

```bash
node render_hero.cjs        # writes /tmp/hero-check.png
```

Then **view the PNG with your own vision** and check specifically:

- Does any line run past its card's right edge, or get clipped mid-word?
- Do any text elements overlap each other?
- Does each card's content actually sit inside its `rect`? (Bullets level with the bottom edge clip.)

Keep the render helper in `/tmp/`, never in the repo, so it cannot land in a commit.

## Pitfalls

- **One line of body text over ~130 characters will overflow a full-width card at 21px.** Split it
  into two `<tspan>` lines inside a single `<text>` and give the card the height for both — an
  unbroken one-liner is silently clipped at the right edge.
- **Name any render helper `.cjs`, not `.js`.** The repo sets `"type": "module"`, so `require()` in a
  `.js` file throws `ReferenceError: require is not defined in ES module scope`.
- **Line endings differ across the existing SVGs** (a mix of CRLF and LF). Match the template file you
  copied rather than converting the whole family.
- Keep the SVG's `<title>`/`<desc>` accurate — they are the accessible description of the figure.
- **Do NOT trust your render's font metrics when the SVG names a Windows-only font.** Some hero SVGs
  specify `'Segoe Print'` / `'Segoe UI'` / `'Comic Sans MS'`. None of those exist on this host, so the
  renderer substitutes a face ~10-15% wider — which **invents overflow and clipping that does not
  exist in a browser**. Before you believe a render, check the font stack: if the text is in a
  substituted font, compute the geometry instead (`x` + font-size × char count vs the card's right
  edge). SVGs that specify generic `sans-serif` render consistently everywhere and are the safer
  choice for anything that must not shift.
- **Never replace a LIVE hero on the strength of a substituted-font render.** Confirm what is actually
  serving before you touch it (`curl -s -o /dev/null -w '%{http_code}' <site>/images/<name>.svg`, and
  check which `heroImage` the published post references). Two agents authored competing heroes for the
  same post once; the render of the live one "looked broken" purely because of font substitution, and
  acting on it would have overwritten a working asset. If a live asset and yours both exist, surface
  the choice to Haris — do not silently pick.
- **Adding a hero to an already-published post is a publish action.** It ships on merge to `main`, so
  it needs the same explicit GO as new content.

## Verify before commit

```bash
cd /mnt/c/Code/gitlab/harishabib_au_code
python3 -c "import xml.dom.minidom as m; m.parse('public/images/whiteboard-<slug>.svg'); print('valid XML')"
npm run build
# confirm the hero is actually wired into the built page:
grep -o 'whiteboard-<slug>[^\"]*' dist/blog/<slug>/index.html | head -1
```

The firewall applies to the image text too — it is published content. See `pluto-content-firewall`.
