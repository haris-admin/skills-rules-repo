---
name: neurodiverse-visual-specs
description: Author multi-modal, visual-first change companions (interactive HTML dashboards, impact cards, flow diagrams, and step-by-step trackers) for every architectural proposal, OpenSpec change, or technical audit to support neurodivergent team members (ADHD, Autism, visual-spatial thinkers).
---

# Neurodiverse Visual Specs & Change Companions

## Purpose & Philosophy

Traditional software engineering proposals, specifications, and security audits lean heavily on dense walls of markdown text. For neurodivergent engineering and product team members (including ADHD, Autism, dyslexia, and visual-spatial thinkers), dense text introduces high executive cognitive load, working memory fatigue, and difficulty visualizing the full systemic impact of changes.

**Simplifii-OS's core mission is neuroinclusivity.** We apply this exact philosophy internally:
> **The Trimodal Rule**: Every architectural proposal, OpenSpec change, security review, or technical audit MUST be accompanied by a self-contained, interactive HTML Visual Companion that presents information in three switchable modes:
> 1. **Visual / Spatial Mode**: Cards, color-coded status badges, architectural SVG impact maps, and visual contrast indicators.
> 2. **Sequential / Step-by-Step Mode**: Linear progression tracks, progressive disclosure checklists, before-and-after states, and clear action gates.
> 3. **Low-Cognitive-Load Executive Mode**: Plain-English explanations (zero unexplained jargon), maximum 4-5 items per view, and clear "Why This Matters" callouts.

---

## When to Use

Activate this skill whenever:
- Preparing a new OpenSpec change proposal (`openspec/changes/*/`).
- Performing a security audit, CRAP score review, or technical architectural review.
- Communicating system-wide changes, database schema updates, or refactoring plans.
- Presenting progress to a mixed team of neurotypical and neurodivergent collaborators.

---

## The Visual Companion Standard (HTML Architecture)

Every visual companion must be a single, zero-dependency, self-contained HTML file (e.g. `visual-companion.html` or `visual-<topic>.html`).

### 1. Visual Aesthetics & Calm Cognitive Design
- **Color Palette**: Use calm, non-vibrating, dark-mode tones (inspired by Simplifii-OS / Tailwind zinc):
  - Canvas background: `#09090b`
  - Elevated cards: `#161618` with subtle borders `rgba(139, 124, 246, 0.2)`
  - Accent / Primary: `#8b7cf6` (purple) and `#38bdf8` (sky)
  - Success / Pass: `#10b981` (emerald)
  - Warning / In-Progress: `#f59e0b` (amber)
  - Danger / Vulnerability: `#ef4444` (rose)
- **Typography**: System font stack (`-apple-system, BlinkMacSystemFont, 'Segoe UI', Inter, sans-serif`) with high contrast (WCAG AAA compliant: minimum 7:1 for body text).
- **Sensory Friendly**:
  - No auto-playing animations, harsh flashing colors, or layout jumps.
  - Generous spacing (minimum 16px gaps, rounded corners `12px-16px`).
  - Clear icon indicators paired with text labels (never use color alone to convey meaning).

### 2. The Three Required Modes (Interactive Switcher)

The HTML companion MUST include an accessible mode switcher (buttons at the top) allowing the reader to toggle instantly between:

#### Mode A: Visual & Spatial Overview
- **Impact Cards**: Grid of cards summarizing each component, showing:
  - Component name & purpose
  - Severity / Status badge
  - Before state vs After state visual pills
  - Click-to-expand details
- **System Impact Map**: Visual diagram (SVG or styled CSS flex/grid flow) illustrating the relationship between:
  - User Entry Point → Backend Middleware → Database / RLS → External Services.
- **Filter Pills**: Live click filters (e.g. "All", "Critical Only", "Remediated", "In Progress").

#### Mode B: Step-by-Step Sequential Track
- For procedural, step-by-step thinkers:
  - Numbered sequence (1, 2, 3...) showing the exact chronological execution.
  - Visual checklist (`[x]` Done vs `[ ]` Pending) with completion percentage bar.
  - Code diff highlights presented in calm, scannable snippets rather than unified terminal dumps.
  - Explicit "Verification Test" for each step.

#### Mode C: Executive & Plain-English Glossary
- For high-level alignment and low cognitive load:
  - "The 30-Second Summary": 3 bullet points maximum.
  - "Plain English Translation": What does this CVE / flaw actually mean in human terms?
  - "Why It Matters for Students": Direct impact on user safety, privacy, and system reliability.

---

## Step-by-Step Procedure

1. **Extract Key Metrics & Entities**:
   - Parse the proposal/audit markdown.
   - Extract: Goals, components affected, risk scores (Impact × Likelihood), CVEs, before vs after changes.
2. **Build the Visual HTML File**:
   - Write semantic HTML with embedded CSS and minimal vanilla JS for interactive tab switching and filtering.
   - Ensure the file runs directly from a local browser (`file://`) or dev server without external build steps or external CDN locks.
3. **Verify Usability & Cognitive Budget**:
   - Ensure the view contains no more than 4-5 primary visual clusters at a time.
   - Verify keyboard navigability and high contrast.
4. **Link into Markdown Specs**:
   - Add a direct clickable link in the corresponding `proposal.md` or `design.md`:
     `[Interactive Visual Companion](file:///path/to/visual-companion.html)`
5. **Git Checkpoint**:
   - Commit both the markdown spec and the HTML visual companion together.
