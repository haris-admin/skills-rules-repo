# Neurodiverse Visual-First Rule (Mandatory Visual Companions & Simple Presentations)

**Authority**: Required for all engineering proposals, OpenSpec change sets, technical debt reviews, and stakeholder presentations.

## Mandate

Every OpenSpec proposal (`openspec/changes/*/`), architectural RFC, security review, or team presentation MUST be accompanied by an interactive **HTML Visual Companion** or **Slide Deck** designed for neurodivergent (ADHD, Autism, Dyslexia) and non-technical team members.

## Core Rules of Neuroinclusive Simplicity

1. **The "One Idea" Rule & Chunking**:
   - Limit cognitive load to 1 primary idea per slide or card.
   - Group information into visual chunks (maximum 3-4 cards per view).
   - Use plain-English human summaries first; explain *why it matters for students and teachers* before mentioning code.

2. **Dyslexia & ADHD Typography (BDA Standards)**:
   - Clean sans-serif fonts (`system-ui`, `-apple-system`, `Inter`, `Arial`).
   - Line height: minimum 1.5 to 1.6; generous word and letter spacing.
   - Strictly left-aligned; NEVER justified text (eliminates whitespace "rivers").
   - Bold for key terms; NEVER italics (prevents letter crowding) and NEVER all-caps sentences.
   - Include an interactive font scaler (`A-` / `A+`) in HTML presentations.

3. **Calm Palette (Zero Ocular Glare)**:
   - Avoid stark black on white or stark white on pitch black.
   - Use soft dark matte surfaces (`#0f1117` base, `#171a23` cards, `#f1f3f9` text).
   - Calming accents: `#9d8efb` (purple), `#38bdf8` (sky), `#34d399` (emerald).
   - Always pair color indicators with recognizable icons (✅, 🛑, 🔍, 🛡️, 📦).

4. **Code on Demand (Progressive Disclosure)**:
   - Do NOT overwhelm presentations with raw code dumps on the main slide.
   - Display a clean summary card with an optional `"🔍 View Code"` drawer/modal for technical drill-down.

5. **Two Canonical Outputs**:
   - **Slide Presentations** (`docs/*_PRESENTATION.html`): High-level, card-driven, keyboard-navigable (`←`, `→`, `Space`, `F`).
   - **Master Baseline Reports** (`docs/*_BASELINE_REPORT.html`): Trimodal switcher (Spatial Visual Map, Sequential Step-by-Step, Plain-English Executive Mode).

6. **Automated Collision & Overflow Gate (MANDATORY)**:
   - Before completing work, agents MUST run automated layout validation:
     `node scripts/verify_presentation_layout.js <file.html>`
   - Asserts zero container overflows (`scrollHeight <= clientHeight + 4`), zero element bounding-box collisions, and word budgets (≤40 words per single card) across both 1.0x and 1.25x font scales.
