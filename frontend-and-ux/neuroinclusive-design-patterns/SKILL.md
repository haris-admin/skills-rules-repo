---
name: neuroinclusive-design-patterns
description: >-
  Design and audit user interfaces, component design systems, and frontend layouts following W3C COGA cognitive accessibility standards, British Dyslexia Association guidelines, and ADHD/Autism sensory ergonomics. Use when building or reviewing frontend applications for neurodivergent individuals, reducing cognitive load, eliminating ocular glare, implementing dyslexia-friendly typography, or designing trimodal UI modes for platforms like Simplifii-OS.
---

# Neuroinclusive Design Patterns & Cognitive Accessibility

A comprehensive UI/UX engineering standard for building calming, highly accessible, and visually empowering web applications for neurodivergent users (ADHD, Autism, Dyslexia, and Executive Dysfunction).

## When to Use

- **Simplifii-OS Development**: When creating or refining components, navigation bars, document editors, or timelines.
- **Frontend Cognitive Audits**: When evaluating whether an interface causes cognitive fatigue, visual crowding, or sensory overwhelm.
- **Accessible Design Systems**: When defining Tailwind color tokens, typography scales, contrast ratios, and motion policies for inclusive products.
- **Multi-Modal Feature Design**: When building interfaces that support spatial visual learners, sequential checklist thinkers, and literal language users.

---

## Core Cognitive Pillars

```
┌─────────────────────────────────────────────────────────────┐
│ 1. COGNITIVE LOAD CEILING (Max 3–4 visual chunks per screen)│
├─────────────────────────────────────────────────────────────┤
│ 2. SENSORY ERGONOMICS (Zero glare matte dark, reduced motion)│
├─────────────────────────────────────────────────────────────┤
│ 3. DYSLEXIA-FRIENDLY TYPOGRAPHY (Sans-serif, 1.5-1.6 height)│
├─────────────────────────────────────────────────────────────┤
│ 4. TRIMODAL DISCLOSURE (Spatial visual / Sequential / Plain)│
├─────────────────────────────────────────────────────────────┤
│ 5. FORGIVING INTERACTIONS (Undo over modals, auto-save)     │
└─────────────────────────────────────────────────────────────┘
```

---

## Typography & Readability Rules

1. **Sans-Serif Exclusively**: Inter, Roboto, Arial, System UI, or OpenDyslexic. Never use decorative serifs.
2. **Line Height**: Strict `1.5` to `1.6` (prevents tracking loss across lines).
3. **No Justification**: Left-align all running text. Justification creates irregular white-space "rivers".
4. **No Italics**: Letters tilt and blur for dyslexic readers. Use **bold** for emphasis.
5. **No ALL-CAPS**: Sentences in all-caps strip distinctive word shape silhouettes.

---

## Sensory Ergonomics & Color Tokens

- **Avoid Extreme Contrast**: Never use pure black `#000000` text on pure white `#ffffff` or vice-versa (causes ocular glare and letter vibration).
- **Calm Matte Canvas**:
  - Base canvas: `#0f1117`
  - Elevated cards: `#171a23` / `#1c202c`
  - Primary text: Soft off-white `#f1f3f9`
  - Secondary text: Warm slate `#a2abbd`
  - Primary Accent: Soft lavender/purple `#9d8efb`
  - Success Accent: Soft emerald `#34d399`
  - Attention Accent: Warm amber `#fbbf24`
- **Zero Surprises**: No auto-playing animations, flashing elements, or intrusive popups. Honor `prefers-reduced-motion`.

---

## References & Pattern Guides

- [W3C COGA Design Checklist](./references/w3c-coga-design-checklist.md) — Exhaustive checklist for cognitive load, working memory support, and dyslexia compliance.
- [Neuroinclusive UI Component Patterns](./references/neuroinclusive-ui-component-patterns.md) — Specifications for trimodal canvas modes, forgiving undo toasts, and auto-save indicators.
