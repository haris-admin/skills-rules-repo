# ADS Foundations and Tokens

Reference for `atlassian-design-system`. Source: <https://atlassian.design/foundations>.

## Design tokens

> "Design tokens are the single source of truth to name and store design decisions."

They exist so a decision is made **once** and consumed everywhere — design tooling and code read the
same name. Anything hardcoded in a component is a decision that now has to be found and changed
everywhere it was copied.

### Naming is semantic, not visual

Tokens encode **intent**. The same token resolves to different raw values per theme (light/dark) and
per brand, which is exactly why you never reference the raw value.

Representative names observed in the token picker:

```
color.text.accent.red          color.text.warning        color.text.success
color.text.accent.blue         color.text.danger         color.link
color.text.accent.purple       color.icon.disabled       color.icon.accent.teal
color.icon.accent.orange       color.border.brand        color.border.success
color.border.warning            color.border.accent.magenta
color.background.accent.lime.bold
elevation.surface.hovered       elevation.surface.overlay
```

Read the shape: `<property>.<role>.<emphasis>` —
- `color.text.*` = foreground text colour (vs `color.icon.*`, `color.border.*`, `color.background.*`)
- `.danger` / `.warning` / `.success` / `.link` = **meaning**
- `.accent.*` = decorative brand hues (not semantics)
- `.bold` / `.subtle` = **emphasis level**
- `elevation.surface.*` = layered-surface treatment (`hovered`, `overlay`) — elevation is a token
  concern, not a box-shadow value typed by hand.

**Practical rule:** pick the token whose *name describes the intent*. If you find yourself choosing
"the blue that looks right", you want `color.text.accent.blue`; if you are showing an error, you want
`color.text.danger` even if it is red today.

### Token surfaces
- **Library / picker:** `https://atlassian.design/components/tokens/all-tokens` — search, filter, pick.
- **Design tokens explained:** `/tokens/design-tokens`
- **Use in code:** `/tokens/use-tokens-in-code`
- **Use in design (Figma, preview):** `/tokens/use-tokens-in-design`
- **Migrate to tokens:** `/tokens/migrate-to-tokens` — how apps move off legacy style values. Useful as
  a *migration playbook* if we ever retrofit our own system.

## Foundations: guidelines

### Accessibility
Accessible design lets people of all abilities interact with, understand, and navigate our apps. ADS
components ship keyboard support and ARIA, but **you must still review patterns, content and
interactions** — components alone do not make an app accessible. Full detail in
`accessibility-and-content.md`.

### Content
Clear, concise, conversational language. Covers **inclusive language**, **style/grammar/punctuation**,
**voice and tone**, **date and time**, and **designing messages**. Full detail in
`accessibility-and-content.md`.

## Foundations: styles

| Foundation | What it governs |
|---|---|
| **Spacing** | A spacing system that simplifies page layout and UI construction |
| **Grid** | Positioning content and creating consistent page layouts |
| **Color** | Brand distinction and reinforcing experience across apps (via tokens) |
| **Typography** | The system of fonts and text styles |
| **Iconography** | Visual representation of commands and common actions |
| **Illustrations** | Conveying complex ideas simply |
| **Logos** | Visual representation of a brand or app |
| **Elevation** | Layered surfaces that form the foundation of UI |
| **Border** | Defining boundaries, separating components, adding emphasis |
| **Radius** | Standardised corner roundness |

**Why this list matters more than it looks:** it is a complete, sane *taxonomy* for a design system.
If we define our own token set, these ten categories are the checklist for what needs coverage —
omitting elevation/border/radius is the classic gap that forces one-off hardcoded values later.

## Key pages
- Overview: <https://atlassian.design/foundations>
- Tokens: <https://atlassian.design/foundations/tokens>
- Accessibility: <https://atlassian.design/foundations/accessibility>
- Content: <https://atlassian.design/foundations/content>
- Typography: <https://atlassian.design/foundations/typography>
- Color: <https://atlassian.design/foundations/color-new>
