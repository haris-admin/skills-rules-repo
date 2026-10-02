# Atlassian Design System Standards (all agents)

**Status:** Canonical · **Created:** 2 October 2026 · **Applies to:** every agent building or reviewing UI
**Source standard:** Atlassian Design System — <https://atlassian.design/>
**Skill:** `frontend-and-ux/atlassian-design-system` · **Mirrors:** `.agents/rules/atlassian-design-system-standards.md` · `.cursor/rules/atlassian-design-system-standards.mdc`

Applies whenever you **write or review frontend UI** — components, styles, copy, or accessibility — in
any of our products (AMLHive, TapEase, A2Square, Simplifii, harishabib.au). The design system is not
optional advice; it is the standard these artefacts are judged against.

---

## 1. Tokens, never raw values

- **Never hardcode** a colour, spacing, radius, border or elevation value in a component. Every such
  value is a defect that will have to be found and changed everywhere it was copied.
- Use the **token layer**. Names are **semantic, not visual**: `color.text.danger`, `color.icon.disabled`,
  `color.border.brand`, `elevation.surface.hovered` — never `--red-500`.
- **Pick the token whose name states the intent.** If you are choosing "the blue that looks right", use
  an accent token. If you are showing an error, use the danger token even if it is red today.
- Cover **all ten foundation categories** when defining tokens, explicitly including **elevation,
  border and radius** — the three we habitually omit and later hardcode around.
- Enforcement must be mechanical: wire the design-system ESLint + Stylelint plugins into CI. An
  unenforced standard is documentation, not a standard.

## 2. Components: use the system, respect the vocabulary

- **Prefer a design-system component over a bespoke control.** Components ship keyboard support and
  ARIA; re-implementing one silently discards both.
- Compose with primitives rather than forking a component to make one visual tweak — a fork loses
  accessibility behaviour.
- Use the **industry-standard names**, and their distinctions:
  - **Lozenge** = status pill · **Badge** = numeric tally (never interchangeable)
  - **Banner** (page-level) · **Section message** (alerts a section) · **Inline message** (action
    required) · **Flag** (confirmation) · **Empty state** (no data — say what to do next) ·
    **Spotlight** (educate) · **Modal dialog** (requires interaction)
- Check **component status** before adopting: never start new work on a `Deprecated` component, and
  treat `Beta`/`Caution` as a stated risk to be decided, not an oversight.

## 3. Accessibility floor (non-negotiable)

- **Contrast:** 4.5:1 for regular text, 3:1 for large text and graphics.
- **Never convey meaning by colour alone** — pair colour with text, icon or shape.
- **Semantic HTML**: `header`, `nav`, `footer`, `main` — not `div`/`span` soup.
- **Keyboard operable**, visible focus, correct labels. Every interactive element.
- **Give people control**: reflow at all sizes, honour `prefers-reduced-motion`, allow scale and
  contrast adjustment, warn before high-impact changes.
- **Using the component library does not make the app accessible.** Components provide primitives;
  patterns, content and interactions must still be reviewed and tested (with tooling *and with people
  with disabilities*).

## 4. Content and copy

- Write to a **reading level of ages 12–14**. Plain, concise, conversational.
- **No jargon, metaphors or idioms** — they do not survive translation and exclude readers.
- **Sentence case** for UI text (see `ui-casing-and-microcopy-standards`).
- **Dates must never assume locale or timezone.** We run across AEST and UTC — always make the date and
  the zone explicit. A bare `02/10/2026` is wrong for anyone outside AU.
- **Messages are designed, not typed on the way out.** An error must state what happened and what to do
  next.

## 5. Review checklist (run on every UI change)

- [ ] No hardcoded colour/spacing/radius/elevation — all through tokens
- [ ] Contrast meets 4.5:1 (text) / 3:1 (large text, graphics)
- [ ] No meaning conveyed by colour alone
- [ ] Design-system components used where one exists; correct messaging component chosen
- [ ] Semantic HTML; keyboard-operable; visible focus; labels present
- [ ] Reduced-motion and reflow honoured
- [ ] Copy at ages 12–14; sentence case; no idioms
- [ ] Dates/times carry an explicit zone; error messages are actionable
- [ ] No `Deprecated` component in new work

## 6. Scope and exceptions

- This rule governs **our** products; it does not mean adopting Atlassian's visual brand. Adopt the
  *system* (tokens, rules, vocabulary, accessibility floor); adopt `@atlaskit` components only for
  Atlassian-adjacent work (Forge, Marketplace, Jira/Confluence integration).
- Where a product has a documented, deliberate divergence, record it in that product's design doc —
  never diverge silently by degrees.

## Related

- `rules/frontend-design-system.md` — our own token and contrast rule (this rule sets the standard; that
  one covers local token mechanics)
- `rules/frontend-lighthouse-performance-gate.md` — where the automated UI checks run
- `rules/ui-casing-and-microcopy-standards.md` — casing and microcopy detail
- `rules/neurodiverse-visual-first.md` — cognitive-accessibility presentation
- Skill `frontend-and-ux/atlassian-design-system` — full foundations, component catalog, accessibility
  and content reference, plus the fleet adoption plan
- Alexandria: `vault/canonical/reference/atlassian-design-system-standards.md`
