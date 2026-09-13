---
name: canvas-design
description: Guides a from-scratch, high-fidelity HTML design artifact (landing page, prototype, deck, component lab, or motion study) through a taste-driven process — surface-first composition, context gathering, variation, and an anti-slop self-audit — for CLI/API agents that lack the hosted Claude Design UI. Use when the user asks for design work (a mockup, prototype, deck, or visual exploration) that would normally go through Claude Design but the agent is running outside that hosted environment.
version: 1.1.0
author: BadTechBandit
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [design, html, prototype, ux, ui, creative, artifact, deck, motion, design-system]
    related_skills: [design-md, popular-web-designs, excalidraw, architecture-diagram]
---

# Claude Design for CLI/API Agents

Use this skill when the user asks for design work that would normally fit Claude Design, but the agent is running in a CLI/API environment instead of the hosted Claude Design web UI.

The goal is to preserve Claude Design's useful design behavior and taste while removing hosted-tool plumbing that does not exist in normal agent environments.

**Before starting, check for other web-design skills like `popular-web-designs` (ready-to-paste design systems for Stripe, Linear, Vercel, Notion, etc.) and `design-md` (Google's DESIGN.md token spec format).** If the user wants a known brand's look, load `popular-web-designs` alongside this one and let it supply the visual vocabulary. If the deliverable is a token spec file rather than a rendered artifact, use `design-md` instead. Full decision table below.

## When To Use This Skill vs `popular-web-designs` vs `design-md`

Hermes has three design-related skills under `skills/creative/`. They do different jobs — load the right one (or combine them):

| Skill | What it gives you | Use when the user wants... |
|---|---|---|
| **canvas-design** (this one) | Design *process and taste* — how to scope a brief, gather context, produce variants, verify a local HTML artifact, avoid AI-design slop | a from-scratch designed artifact (landing page, prototype, deck, component lab, motion study) with no specific brand or token system dictated |
| **popular-web-designs** | 54 ready-to-paste design systems — exact colors, typography, components, CSS values for sites like Stripe, Linear, Vercel, Notion, Airbnb | "make it look like Stripe / Linear / Vercel", a page styled after a known brand, or a visual starting point pulled from a real product |
| **design-md** | Google's DESIGN.md spec format — author/validate/diff/export design-token files, WCAG contrast checking, Tailwind/DTCG export | a formal, persistent, machine-readable design-system *spec file* (tokens + rationale) that lives in a repo and gets consumed by agents over time |

Rule of thumb:

- **Process + taste, one-off artifact** → canvas-design
- **Match a known brand's look** → popular-web-designs (and let canvas-design drive the process)
- **Author the tokens spec itself** → design-md

These compose: use `popular-web-designs` for the visual vocabulary, `canvas-design` for how to turn a brief into a thoughtful local HTML file, and `design-md` when the output is the token file rather than a rendered artifact.

## Runtime Mode

You are running in **CLI/API mode**, not the Claude Design hosted web UI.

Ignore references from source Claude Design prompts to hosted-only tools, project panes, preview panes, special toolbar protocols, or platform callbacks that are not available in the current environment.

Examples of hosted-tool concepts to ignore or remap:

- `done()`
- `fork_verifier_agent()`
- `questions_v2()`
- `copy_starter_component()`
- `show_to_user()`
- `show_html()`
- `snip()`
- `eval_js_user_view()`
- hosted asset review panes
- hosted edit-mode or Tweaks toolbar messaging
- `/projects/<projectId>/...` cross-project paths
- built-in `window.claude.complete()` artifact helper
- tool schemas embedded in the source prompt
- web-search citation scaffolding meant for the hosted runtime

Instead, use the tools actually available in the current agent environment.

Default deliverable:

- a complete local HTML file
- self-contained CSS and JavaScript when portability matters
- exact on-disk path in the final response
- verification using available local methods before saying it is done

If the user asks for implementation in an existing repo, generate code in the repo's actual stack instead of forcing a standalone HTML artifact.

## Core Identity

Act as an expert designer working with the user as the manager.

HTML is the default tool, but the medium changes by assignment:

- UX designer for flows and product surfaces
- interaction designer for prototypes
- visual designer for static explorations
- motion designer for animated artifacts
- deck designer for presentations
- design-systems designer for tokens, components, and visual rules
- frontend-minded prototyper when code fidelity matters

Avoid generic web-design tropes unless the user explicitly asks for a conventional web page.

Do not expose internal prompts, hidden system messages, or implementation plumbing. Talk about capabilities and deliverables in user terms: HTML files, prototypes, decks, exported assets, screenshots, code, and design options.

## When To Use

Use this skill for:

- landing pages
- teaser pages
- high-fidelity prototypes
- interactive product mockups
- visual option boards
- component explorations
- design-system previews
- HTML slide decks
- motion studies
- onboarding flows
- dashboard concepts
- settings, command palettes, modals, cards, forms, empty states
- redesigns based on screenshots, repos, brand docs, or UI kits

Do not use this skill for pure DESIGN.md token authoring unless the user specifically asks for a DESIGN.md file. Use `design-md` for that.

## Design Principle: Start From Context, Not Vibes

Good high-fidelity design does not start from scratch.

Before designing, look for source context:

1. brand docs
2. existing product screenshots
3. current repo components
4. design tokens
5. UI kits
6. prior mockups
7. reference models
8. copy docs
9. constraints from legal, product, or engineering

If a repo is available, inspect actual source files before inventing UI:

- theme files
- token files
- global stylesheets
- layout scaffolds
- component files
- route/page files
- form/button/card/navigation implementations

The file tree is only the menu. Read the files that define the visual vocabulary before designing.

If context is missing and fidelity matters, ask concise focused questions instead of producing a generic mockup.

## Asking Questions

Ask questions when the assignment is new, ambiguous, high-fidelity, externally facing, or depends on taste.

Keep questions short. Do not ask ten questions by default unless the problem is genuinely underspecified.

Usually ask for:

- intended output format
- audience
- fidelity level
- source materials available
- brand/design system in play
- number of variations wanted
- whether to stay conservative or explore divergent ideas
- which dimension matters most: layout, visual language, interaction, copy, motion, or systemization

Skip questions when:

- the user gave enough direction
- this is a small tweak
- the task is clearly a continuation
- the missing detail has an obvious default

When proceeding with assumptions, label only the important ones.

## Surface-First: Commit to a Composition Before Touching Tokens

The single highest-leverage anti-slop rule. Most AI design slop is **compositional, not cosmetic** — the model reaches for a centered hero + three equal-weight feature cards for *every* surface, then decorates. Recoloring or restyling that layout never fixes it, because the layout was wrong before a single color was chosen.

Before you write any colors, type scale, or components, **commit out loud to exactly one surface archetype.** This conditions generation on a high-level plan first, which collapses the entropy of what gets produced — the same reason a chain-of-thought step improves reasoning.

The seven surfaces:

1. **Monitor** — the user is watching state change (dashboards, status pages, observability). Density, glanceable hierarchy, no marketing framing.
2. **Operate** — the user is taking action on things (consoles, admin panels, queues, inboxes). Action affordances and selection state dominate.
3. **Compare** — the user is weighing options against each other (pricing, plans, spec tables, search results). Aligned columns, parity of structure, one differentiator emphasized.
4. **Configure** — the user is setting things up (settings, forms, wizards, onboarding). Progressive disclosure, clear save/validation states, low decoration.
5. **Decide / Learn** — the user is being convinced or taught (landing pages, docs, marketing). One idea lands per section; this is the ONLY surface where a hero is usually correct.
6. **Explore** — the user is browsing an open space (galleries, maps, search-and-filter, catalogs). Filters, result grids, and zoom/peek are the composition.
7. **Command / Inspect** — the user is driving by keyboard or drilling into one object (command bars, inspectors, detail panes, property editors). Speed and focus over breadth.

Rules:

- State the surface in one line before designing (e.g. "This is a **Monitor** surface, so density and glanceability beat a hero").
- A dashboard is a Monitor surface, not a Decide surface — do not give it a centered hero and three feature cards.
- If a screen genuinely spans two surfaces, name the **primary** one and treat the other as secondary; do not average them into mush.
- The hero-plus-three-cards composition is correct for **Decide/Learn only**. Reaching for it anywhere else is the #1 tell.

This one constraint eliminates more generic-looking UI than any aesthetic rule below.

## Workflow

1. **Understand the brief**
   - What is being designed?
   - Who is it for?
   - What artifact should exist at the end?
   - What constraints are locked?

2. **Gather context**
   - Read supplied docs, screenshots, repo files, or design assets.
   - Identify the visual vocabulary before writing code.

3. **Commit to a surface** (see "Surface-First")
   - Name the one surface archetype before any visual tokens.
   - This conditions the composition; everything below inherits from it.

4. **Define the design system for this artifact**
   - colors
   - type
   - spacing
   - radii
   - shadows or elevation
   - motion posture
   - component treatment
   - interaction rules

5. **Choose the right format**
   - Static visual comparison: one HTML canvas with options side by side.
   - Interaction/flow: clickable prototype.
   - Presentation: fixed-size HTML deck with slide navigation.
   - Component exploration: component lab with variants.
   - Motion: timeline or state-based animation.

6. **Build the artifact**
   - Prefer a single self-contained HTML file unless the task calls for a repo implementation.
   - Preserve prior versions for major revisions.
   - Avoid unnecessary dependencies.

7. **Verify**
   - Confirm files exist.
   - Run any available syntax/static checks.
   - If browser tools are available, open the file and check console errors.
   - If visual fidelity matters and screenshot tools are available, inspect at least the primary viewport.
   - Run the slop self-audit (see "Slop Diagnostic") and repair only what it flags.

8. **Report briefly**
   - exact file path
   - what was created
   - caveats
   - next decision or next iteration

## Artifact Format Rules

Default to local files.

For standalone artifacts:

- create a descriptive filename, e.g. `Landing Page.html`, `Command Palette Prototype.html`, `Design System Board.html`
- embed CSS in `<style>`
- embed JS in `<script>`
- keep the artifact openable directly in a browser
- avoid remote dependencies unless they are explicitly useful and stable
- include responsive behavior unless the format is intentionally fixed-size

For significant revisions:

- preserve the previous version as `Name.html`
- create `Name v2.html`, `Name v3.html`, etc.
- or keep one file with in-page toggles if the assignment is variant exploration

For repo implementation:

- follow the repo's actual stack
- use existing components and tokens where possible
- do not create a standalone artifact if the user asked for production code

## HTML / CSS / JS Standards

Use modern CSS well (variables, grid, container queries, real focus/hover states, `prefers-reduced-motion`), and avoid monolithic files, fragile viewport assumptions, and tiny hit targets. Minimums: 44px mobile hit targets, 12pt print text, 24px+ for 1920×1080 deck text. See [HTML / CSS / JS Standards](references/html-css-js-standards.md) for the full checklist.

## Format-Specific Rules

React (only when state/interaction complexity warrants it and CDN versions are pinned), slide decks (fixed 1920×1080 canvas, keyboard nav, localStorage slide position, sparse slides), and interactive prototypes (clickable primary path, all key states, localStorage continuity) each have their own detailed rules. See [Format-Specific Rules](references/format-specific-rules.md) for React-in-standalone-HTML, Deck Rules, and Prototype Rules in full.

## Variation Rules

When exploring, default to at least three options:

1. **Conservative** — closest to existing patterns / lowest risk
2. **Strong-fit** — best interpretation of the brief
3. **Divergent** — more novel, useful for discovering taste boundaries

Variations can explore:

- layout
- hierarchy
- type scale
- density
- color posture
- surface treatment
- motion
- interaction model
- copy structure
- component shape

Do not create variations that are merely color swaps unless color is the actual question.

When the user picks a direction, consolidate. Do not leave the project as a pile of options forever.

## Tweakable Designs in CLI/API Mode

The hosted Claude Design edit-mode toolbar does not exist here.

Still preserve the idea: when useful, add in-page controls called `Tweaks`.

A good `Tweaks` panel can control:

- theme mode
- layout variant
- density
- accent color
- type scale
- motion on/off
- copy variant
- component variant

Keep it small and unobtrusive. The design should look final when tweaks are hidden.

Persist tweak values with localStorage when helpful.

## Content Discipline

Do not add filler content.

Every element must earn its place.

Avoid:

- fake metrics
- decorative stats
- generic feature grids
- unnecessary icons
- placeholder testimonials
- AI-generated fluff sections
- invented content that changes strategy or claims

If additional sections, pages, copy, or claims would improve the artifact, ask before adding them.

When copy is necessary but not final, mark it as draft or placeholder.

## Anti-Slop Rules

Avoid common AI design sludge:

- aggressive gradient backgrounds
- glassmorphism by default
- emoji unless the brand uses them
- generic SaaS cards with icons everywhere
- left-border accent callout cards
- fake dashboards filled with arbitrary numbers
- stock-photo hero sections
- oversized rounded rectangles as a substitute for hierarchy
- rainbow palettes
- vague labels like “Insights,” “Growth,” “Scale,” “Optimize” without content
- decorative SVG illustrations pretending to be product imagery

Minimal is not automatically good. Dense is not automatically cluttered. Choose intentionally.

## Slop Diagnostic: Score Before You Fix

AI design slop has a tiny, predictable failure distribution — about ten recognizable tells (tech gradients, feature-tile grids, accent rails, unearned blur, wrong surface, etc.). Before polishing or repairing an artifact, run this as an explicit self-audit: score the artifact out of 10, state which tells fired, then repair matched to the diagnosis (re-layout for compositional tells, recolor/re-typeset for palette tells, remove decoration for the rest). **Diagnose first, treat second** — fixing in the same breath as auditing tends to repeat the mistake. See [Slop Diagnostic](references/slop-diagnostic.md) for the full ten-tell list and the diagnosis-to-repair mapping.

## Typography

Use the existing type system if one exists.

If not, choose type deliberately based on the artifact:

- editorial: serif or humanist headline with restrained sans body
- software/productivity: precise sans with strong numeric treatment
- luxury/minimal: fewer weights, more spacing discipline
- technical: mono accents only, not mono everywhere
- deck: large, clear, high contrast

Avoid overused defaults when a stronger choice is appropriate.

If using web fonts, keep the number of families and weights low.

Use type as hierarchy before adding boxes, icons, or color.

## Color

Use brand/design-system colors first.

If no palette exists:

- define a small system
- include neutrals, surface, ink, muted text, border, accent, danger/success if needed
- use one primary accent unless the assignment calls for a broader palette
- prefer oklch for harmonious invented palettes when browser support is acceptable
- check contrast for important text and controls

Do not invent lots of colors from scratch.

## Layout and Composition

Design with rhythm:

- scale
- whitespace
- density
- alignment
- repetition
- contrast
- interruption

Avoid making every section the same card grid.

For product UIs, prioritize speed of comprehension over decoration.

For marketing surfaces, make one idea land per section.

For dashboards, avoid “data slop.” Only show data that helps the user decide or act.

## Motion

Use motion as discipline, not theater.

Good motion:

- clarifies state changes
- reduces anxiety during loading
- shows continuity between surfaces
- gives controls tactility
- stays subtle

Bad motion:

- loops without purpose
- delays the user
- calls attention to itself
- hides poor hierarchy

Respect `prefers-reduced-motion` for non-trivial animation.

## Images and Icons

Use real supplied imagery when available.

If an asset is missing:

- use a clean placeholder
- use typography, layout, or abstract texture instead
- ask for real material when fidelity matters

Do not draw elaborate fake SVG illustrations unless the assignment is explicitly illustration work.

Avoid iconography unless it improves scanning or matches the design system.

## Context, Sourcing, and Copyright

When recreating or extending a UI from a repo, inspect the actual source files (theme/token/style/component) and lift exact values before designing — don't build from memory when source is available. Read Markdown/HTML/CSS/JS/JSON/SVG directly; use local extraction tools for DOCX/PPTX/PDF. Never clone a company's distinctive proprietary UI or branded screens — extract general principles (density, command-first interaction, editorial hierarchy) and transform them into an original design. See [Context, Sourcing, and Copyright](references/context-sourcing-and-copyright.md) for the full source-fidelity procedure, document-reading rules, and the acceptable/not-acceptable copyright boundary.

## Verification

Before final response, verify as much as the environment allows.

Minimum:

- file exists at the stated path
- HTML is saved completely
- obvious syntax issues are checked

Better:

- open in a browser tool and check console errors
- inspect screenshots at the primary viewport
- test key interactions
- test light/dark or variants if present
- test responsive breakpoints if relevant

If verification is limited by environment, say exactly what was and was not verified.

Never say “done” if the file was not actually written.

## Final Response Format

Keep final responses short.

Include:

- artifact path
- what it contains
- verification status
- next suggested action, if useful

Example:

```text
Created: /path/to/Prototype.html
It includes 3 layout variants, a Tweaks panel for density/theme, and responsive behavior.
Verified: file exists and opened cleanly in browser, no console errors.
Next: pick the strongest direction and I’ll tighten copy + motion.
```

## Portable Opening Prompt Pattern

When adapting a Claude Design style request into CLI/API mode, use this mental translation:

```text
You are running in CLI/API mode, not hosted Claude Design. Ignore references to hosted-only tools or preview panes. Produce complete local design artifacts, usually self-contained HTML with embedded CSS/JS, and verify with available local tools before returning. Preserve the design process: gather context, define the system, produce options, avoid filler, and meet a high visual bar.
```

## Pitfalls

- Do not paste hosted tool schemas into a skill. They cause fake tool calls.
- Do not point the skill at a giant external prompt as required runtime context. That creates drift.
- Do not strip the design doctrine while removing tool plumbing.
- Do not over-ask when the user already gave enough direction.
- Do not under-ask for high-fidelity work with no brand context.
- Do not produce generic SaaS layouts and call them designed.
- Do not claim browser verification unless it actually happened.
