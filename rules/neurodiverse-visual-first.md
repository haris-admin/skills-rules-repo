# Neurodiverse Visual-First Rule (Mandatory Visual Companions)

**Authority**: Required for all engineering proposals, OpenSpec change sets, technical debt reviews, and security/performance audits.

## Mandate

Every OpenSpec proposal (`openspec/changes/*/`), architectural RFC, or security review MUST be accompanied by an interactive **HTML Visual Companion** (`visual-companion.html` or `docs/visual-*.html`).

## Principles

1. **Trimodal Communication**:
   - Every proposal must accommodate both visual/spatial thinkers and sequential/step-by-step thinkers.
   - Provide an interactive switcher between:
     - **Visual Mode**: Color-coded impact cards, visual system maps, and status badges.
     - **Sequential Mode**: Chronological step-by-step tracks, before-and-after state comparisons, and test verification gates.
     - **Plain-English Executive Mode**: Low cognitive load, zero unexplained acronyms, and practical student-impact explanations.

2. **Aesthetic Standard**:
   - Zero-dependency, self-contained HTML (works offline or via local HTTP).
   - Non-vibrating, high-contrast dark theme matching Simplifii-OS design tokens (`#09090b` background, `#161618` cards, `#8b7cf6` accent).
   - Generous whitespace, scannable visual chunks, and no sensory-overloading animations.

3. **Traceability**:
   - The markdown spec must link directly to the local HTML visual companion.
   - The visual companion must accurately reflect the tasks, risk scores, and implementation states in `tasks.md`.
