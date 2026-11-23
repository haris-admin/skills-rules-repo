# Buttons carry no arrow glyphs, except pagination

Owner rule: never add an arrow to a button, link or call to action.

**Scope:** every screen, page and email in the owner's products.

---

## Core Directives

1. **No arrows in buttons**: not a right arrow, not `->`, not a chevron, whether typed, from an entity, or drawn by CSS content on a pseudo-element.
2. **Exception**: pagination and next or previous page controls, and even there an arrow is optional and need not look like `<-` and `->`; words, numbers or other treatments are fine.
3. **Guard it with a test** on the built output (no arrow code points in any stylesheet, no `.btn::after`), written before the fix.

## Why this exists

**23 Nov 2026 (SonoVantage):** the landing page button showed an arrow drawn by `.btn::after { content: '\\2192' }`, not by the button text, which a text search missed. The owner said to remove it and to make it a rule.
