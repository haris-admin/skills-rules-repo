---
name: neurodiverse-visual-specs
description: Author multi-modal, visual-first change companions, simple slide presentations, and executive visual reports for technical proposals, security audits, and progress briefings. Specifically optimized for neurodivergent (ADHD, Autism, Dyslexia) and non-technical stakeholders following BDA and WCAG standards.
---

# Neurodiverse Visual Specs, Presentations & Reporting Standards

## Purpose & Philosophy

Traditional software engineering proposals, specifications, and architecture audits lean heavily on dense walls of technical jargon and monolithic markdown files. For neurodivergent team members (ADHD, Autism, Dyslexia, and visual-spatial thinkers) and non-technical stakeholders (product managers, educators, executives), dense text introduces:
- **Executive cognitive fatigue** and attention loss.
- **Working memory overload** from tracking multi-layered technical abstractions.
- **Visual crowding & glare** from poor typography, pure black-on-white contrast, or tight line spacing.

**Simplifii-OS's core mission is neuroinclusivity.** We embody this exact standard internally:
> **The Radical Simplicity & Trimodal Rule**: Every proposal, presentation deck, or audit report MUST prioritize high-level visual clarity, plain-English value, and progressive disclosure:
> 1. **Visual / Spatial Mode**: Generous whitespace, big stat meters, cards with recognizable icons, and before-and-after comparisons.
> 2. **Sequential Mode**: Chronological, step-by-step tracks with clear checkboxes and zero technical clutter.
> 3. **Code on Demand**: Technical code diffs are tucked into accessible, on-demand drawers/modals, keeping the main canvas calm, focused, and non-intimidating.

---

## Neurodivergent & Non-Technical Design Standards

These standards synthesize guidelines from the **British Dyslexia Association (BDA)**, **W3C WCAG 2.2**, and ADHD cognitive research:

### 1. The "One Core Idea" Cognitive Ceiling
- **Maximum 1 Core Takeaway per slide or major card**: Never stack multiple complex arguments into a single block.
- **Visual Chunking**: Limit groups of information to **3 to 4 items maximum** per view.
- **Plain-English Translations**: Lead with human value. Explain *what broke, what we did, and why it matters to students/teachers*, before showing any technical implementation.

### 2. Typography & Readability (Dyslexia & ADHD Aligned)
- **Font Stack**: Clean, uncrowded sans-serif fonts (`-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Inter, Arial, sans-serif`). NEVER use serif, script, or decorative fonts with distracting letter "feet".
- **Line & Letter Spacing**:
  - Line height: **1.5 to 1.6** (prevents line-tracking loss).
  - Letter spacing: **0.015em to 0.02em**; word spacing: **0.05em**.
- **Text Alignment**: Strictly **left-aligned**. NEVER use justified text (justification creates irregular spacing and distracting "rivers" of white space).
- **Styling Discipline**:
  - Use **bold** for key concepts to facilitate fast scanning.
  - **NEVER use italics** (letters blur and tilt together for dyslexic readers).
  - **NEVER use ALL-CAPS** for sentences (obliterates distinctive letter shapes, slowing down reading).
- **Dynamic Font Scaler**: Every presentation or report should provide an interactive `A-` / `A+` control allowing users to scale text to their comfort level.

### 3. Color, Contrast & Sensory Comfort
- **Zero Ocular Glare**:
  - Avoid stark pure-black text on pure-white background, or pure white on pitch black (creates optical glare and visual blurring).
  - Use calming, matte dark surfaces:
    - Base canvas: `#0f1117`
    - Elevated cards: `#171a23` or `#1c202c`
    - Primary text: `#f1f3f9` (soft off-white)
    - Secondary text: `#a2abbd` (warm slate)
- **Calm Semantic Accents**:
  - Success / Good: `#34d399` (soft emerald)
  - Attention / Pending: `#fbbf24` (warm amber)
  - Critical / Risk: `#f87171` (soft rose)
  - Primary / Branding: `#9d8efb` (calming purple)
- **Shape + Icon Pairing**: Never convey meaning through color alone (essential for color-blindness and cognitive mapping). Always pair a status color with a clear icon (✅, 🛑, 🔍, 🛡️, 📦).

---

## Two Canonical Artifact Types

When communicating engineering work, author one of the following two formats:

### Format A: The Interactive Slide Presentation (`docs/*_PRESENTATION.html`)
Used for all-hands meetings, sprint demos, and executive briefings.

- **Structure**:
  - Top: Subtle gradient progress bar + Title badge + Font Scaler (`A-` / `A+`).
  - Center: Fullscreen slide card (maximum 3 visual cards per slide).
  - Bottom: Previous / Next buttons, interactive slide dots, and `Fullscreen` toggle.
- **Code on Demand**:
  - When narrating code, display high-level summary cards on the slide with an explicit `"🔍 View Code"` button.
  - Clicking opens a clean modal containing the syntax-highlighted diff without overwhelming the main presentation.
- **Keyboard Shortcuts**: Arrow keys (`←`, `→`), `Space`, and `F` for Fullscreen.

### Format B: The Master Baseline Report Pair
Used for formal engineering documentation and audit baselines.

1. **Markdown Document** (`docs/*_BASELINE_REPORT.md`):
   - Executive summary, audit matrix, metric tables, and file inventories.
2. **Interactive HTML Companion** (`docs/*_BASELINE_REPORT.html`):
   - Filter bar: live cluster toggles (e.g. "All", "Security", "Database", "Architecture").
   - Trimodal switcher:
     - **Spatial Overview**: Visual cards with before/after state pills.
     - **Step-by-Step Track**: Linear numbered progression with completion bars.
     - **Executive Mode**: Plain-English glossary and "Why It Matters" cards.

---

## Step-by-Step Authoring Workflow

1. **Extract Core Messages**:
   - Strip away raw implementation minutiae; identify the 3 to 5 key human takeaways.
2. **Translate to Human Terms**:
   - e.g., "SEC-002 Express JSON limit" ➔ "Server Protection: Stopping massive payloads from freezing the app".
3. **Build the Self-Contained HTML**:
   - Zero dependencies (no external CDNs, npm scripts, or build locks).
   - Embedded CSS tokens adhering to the Neurodivergent Color & Typography standards.
   - Minimal vanilla JavaScript for slide navigation, keyboard listeners, and modal popups.
4. **Verify Cognitive Ergonomics**:
   - Can a non-technical stakeholder understand each card in 5 seconds?
   - Does the font size scale properly with `A-` / `A+`?
   - Is text left-aligned and free of italics?
5. **Git Checkpoint**:
   - Check in reports and presentation decks together with the active branch.
