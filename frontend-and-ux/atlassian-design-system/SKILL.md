---
name: atlassian-design-system
description: Use when applying the Atlassian Design System (ADS) to a UI. Tokens-first styling, @atlaskit components, WCAG accessibility, and Atlassian content/voice rules.
---

# Atlassian Design System (ADS)

Source of truth: <https://atlassian.design/>. Atlassian's own design system — the language behind Jira,
Confluence, and Rovo. Use it two ways: (a) as a **reference implementation** of a mature enterprise
design system whose decisions we borrow, and (b) as a **component stack** when we build Atlassian-
adjacent UI (Forge apps, Marketplace, internal tooling).

This skill is the *Atlassian* system. For our own generic token/contrast rules see
`frontend-and-ux/frontend-design-system`; for cognitive-accessibility specifics see
`frontend-and-ux/neuroinclusive-design-patterns`; for casing/microcopy see `frontend-and-ux/ui-casing-microcopy`.

## The system in three parts

| Part | What it is |
|---|---|
| **Foundations** | Design tokens + guidelines (accessibility, content) + styles (spacing, grid, color, typography, iconography, illustrations, logos, elevation, border, radius) |
| **Components** | Reusable building blocks that meet specific interaction needs |
| **Content** | Clear, concise, conversational language for UI |

## Non-negotiables — these catch the majority of reviews

1. **Tokens, never raw values.** If a value is hardcoded, it is a bug: use the token layer
   (`color.text.accent.red`, `elevation.surface.hovered`, `color.border.brand`). Tokens are the
   *single source of truth* for naming and storing UI decisions — colour, spacing, radius, elevation.
   In code this means tokens-first CSS (XCSS is Atlassian's safer, tokens-first CSS-in-JS).
2. **Contrast: 4.5:1 for regular text, 3:1 for large text and graphics.** Never rely on colour alone
   to convey meaning.
3. **Design-system components first.** ADS components ship built-in keyboard support and sensible ARIA.
   Building a bespoke control throws that away and fragments consistency.
4. **Semantic HTML.** `header`, `nav`, `footer`, `main` — not `div`/`span` soup. It is how assistive
   technology navigates.
5. **Content at a reading level of ages 12–14.** Plain, concise language. No jargon, no metaphors or
   idioms (they do not survive translation and exclude readers).
6. **Give people control.** Support reflow at all sizes, honour reduced-motion settings, allow scale
   and contrast adjustment, and warn *before* high-impact changes.

## Values and principles — how ADS resolves design arguments

**Values:** *Foundational* (solve common problems, no consistency for its own sake, reject infinite
flexibility) · *Harmonious* (building blocks feel like one family) · *Empowering, for everyone* (works
regardless of role, experience, or skill; self-service by default).

**Principles:**
1. **Trusted fundamentals before comprehensive patterns** — solve the common foundational problem
   first; ship opinionated building blocks, not a blank canvas.
2. **Meet system needs before delivering individual features** — documentation, support, tooling and
   maintenance are part of the product; finish what you start.
3. **Bring people on the journey before helping for the moment** — co-create, optimise for
   self-service, aim to make every consumer a champion of the system.

## Component status is part of the contract

ADS marks components **Beta**, **Early access**, **Caution**, and **Deprecated**. Check status before
adopting. Deprecated ones must not be used for new work (as of this review: `atlassian-navigation`,
`layout-grid`, `onboarding`, `page-layout`, `side-navigation`). `Caution` on `Page`, `Table`, and
`Inline dialog` means prefer the recommended alternative.

## Our stack (React / Next.js + TypeScript)

- Install `@atlaskit/*` components; wrap the app in the **App provider** at the root.
- Enforce with the **ESLint plugin for the design system**, the **UI Styling Standard** ESLint plugin,
  and the **Stylelint plugin** — these are what make "tokens, not raw values" mechanical rather than
  a review opinion.
- `@atlaskit/css` + Compiled CSS-in-JS gives style components backed by tokens; `css-reset` is the base
  stylesheet.

## Designing for AI

ADS has a first-class **AI patterns** area (Rovo UI). If we build agentic UI, that is the closest
published, accessibility-tested precedent for how an enterprise design system presents AI surfaces —
prefer it over inventing our own agent affordances.

## References

- `references/foundations-and-tokens.md` — token architecture, naming, and every foundation.
- `references/components-catalog.md` — the full component inventory by category, with statuses.
- `references/accessibility-and-content.md` — the 8 accessibility principles, disability classes, and
  the content guidelines (inclusive language, voice and tone, dates, messages).
- `references/adoption-plan.md` — **our development plan** for adopting ADS across the fleet.

## Pitfalls

- **Do not fork ADS components to make one visual tweak.** Compose with primitives (`Box`, `Inline`,
  `Stack`, `Flex`, `Grid`, `Bleed`, `Text`) and tokens instead; a fork silently loses a11y behaviour.
- **Do not read the token list as a palette.** Tokens are *semantic* (`color.text.warning`) — choose the
  token that means the thing, not the one that looks right today; that is what makes theming work.
- **Do not copy ADS component names into our own system and then diverge.** The value of matching
  names (Lozenge, Banner, Section message, Empty state, Flag, Inline message) is that every agent and
  engineer already knows which is which — divergence destroys that.
- **"No Protection"-style confusion does not apply here** — but status does: a `Beta` component is a
  stated risk, not an oversight.
