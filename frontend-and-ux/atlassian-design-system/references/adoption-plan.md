# Development Plan — Adopting the Atlassian Design System

**Created:** 2026-09-30 · **Source review:** <https://atlassian.design/> · **Status:** proposed, not yet scheduled

This is the development plan the skill exists to serve. It is deliberately **adoption-first**: ADS is
mature enough that the value to us is in its *decisions* (token architecture, the accessibility bar, the
content rules, component vocabulary) far more than in its React package.

---

## Why adopt at all

1. **We already assert most of these rules without a source.** `frontend-design-system` mandates tokens
   and 4.5:1/3:1 contrast; `ui-casing-microcopy` mandates casing; `neuroinclusive-design-patterns`
   covers cognitive accessibility. ADS is the published, enterprise-grade reference that ties those
   fragments into one coherent, citable standard.
2. **It gives us a token taxonomy we are currently missing.** ADS covers ten foundation styles
   (spacing, grid, color, typography, iconography, illustrations, logos, **elevation, border, radius**).
   Our own token sets typically stop at colour/spacing/type — and the missing three are exactly the ones
   that force one-off hardcoded values later.
3. **It gives our agents a shared UI vocabulary.** "Lozenge", "Banner", "Section message", "Empty
   state", "Dynamic table", "Inline edit" mean one thing industry-wide. When an agent writes UI, naming
   the component correctly removes a whole class of ambiguity.
4. **AI surfaces are the frontier and ADS has already published patterns for them** (Rovo UI). For a
   fleet building agentic products, that is the closest accessible, tested precedent available.

---

## Phase 1 — Standards (do first, zero dependencies)

**Goal:** make the ADS bar our written standard, so review has something to cite.

- [ ] Adopt the **six non-negotiables** from `SKILL.md` as the frontend review checklist: tokens-not-raw,
      4.5:1/3:1 contrast, design-system-components-first, semantic HTML, 12–14 reading age, give people
      control (reflow / reduced motion / scale).
- [ ] Cross-link `frontend-design-system` → this skill so token and contrast rules have one owner each
      (no duplicated, drifting copies of the same rule).
- [ ] Extend the review checklist with the two rules we demonstrably break: **dates/times must never
      assume locale** (we mix AEST and UTC daily) and **no colour-alone meaning** (our status pills).
- **Acceptance:** the checklist exists in this repo and is referenced from the frontend skills.
- **Cost:** documentation only.

## Phase 2 — Token architecture (the highest-value technical work)

**Goal:** give our products a semantic token layer with the same *shape* as ADS, so decisions are made
once.

- [ ] Define a semantic layer mirroring ADS naming: `color.text.*`, `color.icon.*`, `color.border.*`,
      `color.background.*`, plus `elevation.surface.*`, spacing, radius, border.
- [ ] **Name by intent, not appearance** (`color.text.danger`, not `--red-500`). This is the rule that
      makes theming possible later and is the whole reason ADS tokens are not a palette.
- [ ] Cover all ten ADS foundation categories, explicitly including **elevation, border and radius**.
- [ ] Wire the enforcement tooling — ESLint + Stylelint plugins (ADS equivalents or our own rules) —
      into CI. Unenforced standards are documentation, not standards.
- **Acceptance:** a new component can be built to spec with no hardcoded colour/spacing/radius/elevation
  value, and CI fails when one is introduced.
- **Applies to:** TapEase portal, A2Square frontend, AMLHive app.

## Phase 3 — Component vocabulary alignment

**Goal:** our component names mean the same thing as everyone else's.

- [ ] Map our existing components to ADS names and **adopt their distinctions**: Lozenge (status pill)
      vs Badge (numeric tally); Banner vs Section message vs Inline message vs Flag; Empty state;
      Toast/flag grouping.
- [ ] Adopt ADS's messaging decision tree in review — picking the wrong messaging component is the most
      common failure in any design system.
- **Acceptance:** a written name-mapping exists; reviewers can state which messaging component applies
  to a case without debate.
- **Risk:** do **not** rename a component to match ADS and then diverge in behaviour — that destroys the
  vocabulary's value. Either match or document the deliberate difference.

## Phase 4 — Give the agents design-system context (fleet-specific)

**Goal:** stop agents inventing UI values.

Atlassian published exactly this problem and their solution: *"Giving AI agents design system context
from the terminal: what we learned building a CLI"* (atlassian.com/blog/ai-at-work). The lesson: agents
produce on-system UI only when the token list and component inventory are **queryable from the
terminal**, not buried in a design tool.

- [ ] Expose our token set + component inventory to the fleet as a script/CLI any agent can call
      (`scripts/` in this repo), returning tokens and the correct component for a described need.
- [ ] Have frontend skills instruct agents to query it before writing UI.
- **Acceptance:** an agent asked for "a status pill" returns our real token-backed component, not a
      hand-rolled `div` with a hex colour.
- **Why this is the fleet-specific win:** it converts the design system from a document into a tool the
  agents can actually use, which is the mechanism Atlassian found made the difference.

## Phase 5 — Review gates

- [ ] Fold ADS checks into the existing `lighthouse-performance-gate` flow rather than creating a
      parallel gate — one gate, more checks.
- [ ] Automated: contrast, token usage, forbidden deprecated components.
- [ ] Human: messaging-component choice, reading age, colour-alone meaning, locale-safe dates.
- **Acceptance:** a PR with a hardcoded colour or a colour-only status fails the gate.

---

## Explicitly NOT doing

- **Not adopting `@atlaskit` wholesale.** Our products are our own brand; ADS components carry Atlassian
  look and feel. We adopt the *system* (tokens, rules, vocabulary, a11y bar) and, where useful, specific
  accessible components as reference implementations. Building on `@atlaskit` is only indicated for
  Atlassian-adjacent work (Forge apps, Marketplace, Jira/Confluence integration).
- **Not porting the whole foundation doc set.** Point at atlassian.design for anything not summarised
  here; a copy will rot and drift.

## Open questions

1. Does Phase 2 target a shared internal package (one token source across products) or per-product token
   files? A shared package is correct long-term and slower to start.
2. Which product is the pilot for Phases 2–3? TapEase portal and A2Square are the most UI-heavy.
3. Do we want the Phase 4 CLI as a Hermes-local tool or a repo `scripts/` entry deployed by `sync.sh`?
