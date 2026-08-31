# Agent rule — YourApp frontend design system

**Status:** Canonical · **Created:** 4 August 2026 (C381) · **Applies to:** every agent surface
**Mirrors:** `.cursor/rules/frontend-design-system.mdc` · `.agents/rules/frontend-design-system.md`
**Enforced by:** `cd frontend && npm run audit:design-tokens` +
`frontend/tests/unit/components/design-tokens-contrast.test.ts`

Companion docs: `docs/branding.md` (identity, logo, voice) · `docs/brand_colours.md` (token tables
and the contrast matrix). **If this file disagrees with `frontend/app/globals.css`, the CSS wins** —
and you update this file in the same change.

---

## Why this rule exists

`globals.css` has defined a full token system since early in the project, and `branding.md §10`
has mandated "change tokens first" for just as long. On 4 Aug 2026 an audit measured what the
application actually did with it:

| Defined | Actually used across 185 `.tsx` files |
|---|---|
| 30 colour tokens | **0** `var(--c-*)` references |
| 9-step type scale | 25 distinct font sizes |
| 5-step radius scale | 18 distinct radii |
| one primary button | 4 radii × 5 font sizes × 2 weights × ~10 paddings, across 455 hand-styled `<button>`s |

The rule was inert because **nothing consumed it**. A brand change meant a ~3,900-site
find-and-replace, and two WCAG AA failures sat in the palette undetected — including the primary
CTA — while `brand_colours.md` documented them as passing.

The lesson encoded here: **a design system is not a document, it is a component plus a detector.**

---

## The four rules

### 1. Never write a raw colour

No hex, `rgb()`, or named colour in `.tsx` under `frontend/app` or `frontend/components`. Use
`var(--c-*)`. If no token fits the role, that is a signal to **add a token** — in `globals.css`
and `docs/brand_colours.md` in the same change, with its computed contrast — not to inline a
literal "just this once".

```tsx
// NO
<div style={{ color: '#6B7280', background: '#F9FAFB' }} />
// YES
<div style={{ color: 'var(--c-text-muted)', background: 'var(--c-surface-subtle)' }} />
```

### 2. Never hand-style a button

Import the primitive. There is exactly one button in this app:

```tsx
import { Button } from '@/components/ui/Button'

<Button>Verify client</Button>                          // primary, md
<Button variant="secondary" size="sm">Cancel</Button>
<Button variant="danger" loading={saving}>Delete</Button>
<Button variant="ghost" fullWidth>Skip</Button>
```

`variant`: `primary` | `secondary` | `danger` | `ghost` · `size`: `sm` | `md` | `lg` (default `md`)
· plus `loading`, `fullWidth`, and every native `<button>` attribute.

`style` passthrough is for **layout only** (`margin`, `flex`, `alignSelf`). Setting `background`,
`color`, `fontSize`, `borderRadius` or `padding` through it defeats the primitive and is flagged
by the audit.

**A new variant is a design decision, not an implementation detail.** If a control genuinely does
not map onto the four variants, style it locally with tokens and a comment saying why — see the
warning-mode buttons in `components/ui/ConfirmDialog.tsx` for the worked example. Do not add a
fifth variant to serve one dialog; that is how a primitive decays back into a grab-bag.

### 3. Size and radius come from the scales

| Scale | Steps |
|---|---|
| Font | `--fs-2xs` 10.5 · `--fs-xs` 11.5 · `--fs-sm` 12.5 · `--fs-base` 13.5 · `--fs-md` 14.5 · `--fs-lg` 16 · `--fs-xl` 18 · `--fs-2xl` 22 · `--fs-3xl` 28 |
| Radius | `--r-sm` 6 · `--r-md` 8 · `--r-lg` 12 · `--r-xl` 16 · `--r-pill` 9999 |
| Spacing | `--sp-1` 4 … `--sp-8` 32 (4-point grid) |
| Line height | `--lh-tight` 1.3 · `--lh-base` 1.5 · `--lh-loose` 1.7 |

Nothing between the steps. If the design needs 15px, it needs `--fs-md` or `--fs-lg`, not a new
number. Do not mix units: this codebase sizes in px via tokens — `rem` strings (`'0.85rem'`) are
drift, not a second valid system.

### 4. Contrast is a requirement, not a review note

Two bars, and **confusing them is how the CTA shipped broken**:

| Bar | Applies to | Minimum |
|---|---|---|
| WCAG 1.4.3 | Text — including **every button label in this app** | **4.5:1** |
| WCAG 1.4.11 | Non-text UI: borders, icons, focus rings, graphical objects | **3:1** |

"Large text" (3:1) means ≥24px, or ≥18.66px bold. App labels at 12–14px are **normal text**. There
is no button in YourApp that qualifies as large text.

Before using any colour pair not already in `docs/brand_colours.md`, compute it:

```bash
python3 openspec/changes/381-frontend-design-system-alignment/contrast.py
```

Never copy a ratio from a document — the previous `brand_colours.md` table was wrong in three
verdicts and six figures, which is precisely how `--c-success` sat at 3.77:1 while documented as
4.55:1 ✅ AA.

---

## Token quick reference

Full tables with contrast: `docs/brand_colours.md`. The ones agents get wrong:

| Use | Token | Note |
|---|---|---|
| Primary button fill | `--c-btn-primary-bg` `#B45309` | **not** `--c-amber` |
| Brand accent | `--c-amber` `#D97706` | 3.19:1 — borders/icons/badges only, **never behind a label** |
| Success (text-safe) | `--c-success` `#047857` | changed from `#059669` in C381 |
| Body text, lightest AA-safe | `--c-text-muted` `#6B7280` | 4.83:1 |
| Disabled/decorative | `--c-text-faint` `#9CA3AF` | 2.54:1 — **never body copy** |
| Stronger border | `--c-border-strong` `#D1D5DB` | inputs, table rules |
| Inset/zebra surface | `--c-surface-subtle` `#F9FAFB` | |
| Text on a status tint | `--c-{success,error,warning,info}-text` | deeper step for the tinted background |

### Snap these on sight

| Literal | Use instead |
|---|---|
| `#F59E0B` | `--c-amber` |
| `#EF4444` | `--c-error` |
| `#16A34A`, `#059669` | `--c-success` |
| `#64748B` | `--c-text-muted` |
| `#F8FAFC`, `#FAFAFA` | `--c-surface-subtle` |

---

## Scope, honestly stated

C381 migrated the token layer, the `Button` primitive, and `frontend/components/ui/`. It did
**not** migrate everything, and this rule does not pretend otherwise. **The remainder is tracked
in C382** (`openspec/changes/382-frontend-token-migration-and-reusable-button-css/`):

- **Button migration is done** (`T381.05`, completed 5 Aug 2026, committed to `dev` — 434 buttons
  across 66 files; the "446 across 74 files" figure below and in C382's proposal both predate
  that and were left uncorrected until 11 Aug 2026). Only 1 raw `<button>` with an inline hex
  background remains app-wide, and it's `T381.05`'s own documented, deliberate exception
  (`app/admin/agencies/[id]/page.tsx` — no exact token match for a purple/indigo accent).
- **React colour-literal migration is complete** (C382 T382.10b/T382.11, 11 Aug 2026): a standing
  repo-wide gate at `frontend/tests/unit/lib/design-token-literal-gate.test.ts` covers every React
  file under `frontend/app` and `frontend/components`, derives the dark-theme boundary from
  `landing.css` / `AuthShell` imports plus `app/components/*`, verifies each theme separately, and
  permits only the self-contained root-error exemption below. Light surfaces use `--c-*`; dark
  surfaces use `landing.css` / `auth.css` tokens. The only regex-visible `#xxx` strings left in
  React are `/product#cdd` URL fragments, which the gate identifies as links rather than colours.
- **The spec is currently only consumable from React.** Anything that is not a React `<button>` —
  `ExperienceState`'s link-as-button, `global-error.tsx`, the email CTA, `landing.css` — hand-copies
  it. C382 turns the variants into CSS classes so any surface that can set a `class` gets the
  identical spec. Until then, if you must copy it, copy it *with a comment naming what it mirrors*.
- **`audit-design-tokens.mjs` currently re-hardcodes the token table it guards** (`TOKEN_FOR`),
  so a token added to `globals.css` is invisible to it. Known defect, C382 T382.05. If you add a
  token, add it to that map too until the manifest lands.
- **⚠ `--c-*` tokens are LIGHT-SURFACE ONLY. Never apply them to a dark-theme file.** Every
  `--c-*` value and every contrast figure in `docs/brand_colours.md` assumes a white/light
  background — they describe the authenticated app. The public marketing site is a **separate dark
  theme** in `landing.css` (`--bg-deep` `#0F1B27`, `--bg-card` `#1E3347`, `--amber` `#FBBF24`).
  Replacing a hex with "the nearest `--c-*` token" inside a `.landing-root` file **breaks contrast
  that was deliberately tuned for a dark background**.

  Dark-theme surfaces: `app/page.tsx`, `app/components/*`, `contact`, `security`, `about`,
  `product`, `signup`, `Compliance/*`, `cookie-policy`, `privacy-policy`, `terms-of-service`,
  `coming_soon`, `maintenance`, `auth/_components/AuthShell.tsx`.

  **Reference table for this surface**: `docs/brand_colours.md`'s "Landing/marketing (dark theme)"
  section (T382/T384.07, added 11 Aug 2026) — every `landing.css` colour token with computed
  contrast against all three dark backgrounds (`--bg-deep`/`--bg-primary`/`--bg-card`). Its absence
  is arguably why both C380 and C381 independently reasoned about dark-theme colours without one
  and landed on the same class of bug (`docs/technical_debt.md` §5.5's C384 entry).

  Worked example: `PricingSection.tsx` carries `#4ADE80` (5.9:1 on `#374151`) and `#15803D`
  (5.0:1 on white) for the *same* badge, because its background flips between the two and no
  single colour clears 4.5:1 on both. No `--c-*` token can express that. Its destination is
  `landing.css` tokens — C382 T382.10b.
- **Known accepted exception:** `#D97706` on navy `#1E3A5F` measures **3.61:1**, below AA for
  text. It affects the email header badge in `backend/app/templates/_brand.css`, not the frontend.
  Documented, not fixed — changing it needs deliverability re-testing. Use `#FBBF24` on navy
  (6.89:1) for any new amber-on-navy **text**.

---

## The enforcement loop

```bash
cd frontend
npm run audit:design-tokens                      # token/button/scale violations in migrated files
npx vitest run tests/unit/components/            # Button behaviour + contrast assertions
./node_modules/.bin/tsc --noEmit
```

`scripts/audit-design-tokens.mjs` checks only files on its CLEAN list. That list is **shrink-only**:

- Migrated a file? **Add it** — that is how progress is banked.
- A listed file fails? **Fix the file.** Removing the entry to go green is the single edit that
  defeats the mechanism, and it is how `branding.md §10` became inert in the first place.

## Change control

1. Change the token in `frontend/app/globals.css`.
2. Recompute contrast with `contrast.py`; update `docs/brand_colours.md` **and** `docs/branding.md`
   in the same change.
3. Run the enforcement loop above.
4. Token values and Button variants are **product decisions** — a human approves them via the
   OpenSpec plan gate (`docs/agent_rules/openspec-tdd-mandate.md`). Do not repaint the product
   because a colour looks off to you.
