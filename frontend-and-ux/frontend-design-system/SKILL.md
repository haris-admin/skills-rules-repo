---
name: frontend-design-system
description: Enforce design token consistency, component reuse, and strict WCAG 4.5:1 (text) and 3:1 (non-text) contrast compliance.
---

# Frontend Design System

## Design Tokens
- Never write hardcoded color hex codes or inline styles. Use CSS custom properties (`var(--c-*)`).
- Standardize spacing (`--sp-*`), font sizes (`--fs-*`), and border radii (`--r-*`).

## Contrast Rules
- Normal Text: Minimum 4.5:1 contrast against background.
- Large Text / Headings: Minimum 3:1 contrast.
- UI Components / Interactive Borders: Minimum 3:1 contrast.

