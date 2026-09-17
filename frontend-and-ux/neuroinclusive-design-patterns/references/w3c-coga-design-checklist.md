# W3C COGA Cognitive Accessibility Checklist

W3C Cognitive and Learning Disabilities Accessibility Task Force (COGA) and British Dyslexia Association (BDA) standards tailored for digital platforms (e.g. Simplifii-OS).

---

## 1. Cognitive Load & Working Memory

- [ ] **The Rule of 3 to 4 Items**: Primary dashboards and task lists must present no more than 3 to 4 actionable chunks simultaneously.
- [ ] **Persistent Breadcrumbs & Orientation**: Users must always be able to tell *where they are*, *what they just did*, and *how to get back* in 1 click.
- [ ] **Zero Memory Traps**: Never require a user to memorize information from one screen to enter it into another. Auto-fill, persistent side drawers, or side-by-side viewports must preserve context.
- [ ] **Zero Guilt Return**: When a user leaves an uncompleted task or session, never show guilt-inducing prompts ("You have 7 overdue tasks!"). Welcome them back with gentle, low-friction re-entry points ("Pick up where you left off").

---

## 2. Typography & Readability (Dyslexia & ADHD Aligned)

- [ ] **Clean Sans-Serif Font Stack**: Inter, Roboto, Arial, Segoe UI, or OpenDyslexic. Never use decorative or serif fonts with complex letter terminals.
- [ ] **Line Height & Spacing**: Strict **1.5 to 1.6** line height; letter spacing of **0.015em to 0.02em**; word spacing **0.05em**.
- [ ] **Strict Left-Alignment**: Never justify text (justification creates irregular spacing and distracting visual "rivers").
- [ ] **Styling Discipline**:
  - Use **bold** for key concepts to facilitate fast visual scanning.
  - **NEVER use italics** (characters tilt and merge for dyslexic readers).
  - **NEVER use ALL-CAPS** for running copy (destroys the unique silhouette of words).
- [ ] **Bionic Reading & Reading Guides**: Provide an optional reading ruler guide (shaded horizontal bar) and Bionic text highlight toggle.

---

## 3. Sensory Ergonomics & Motion Comfort

- [ ] **Zero Optical Glare**:
  - Avoid stark pure black `#000000` text on pure white `#ffffff`, or pure white text on pitch black.
  - Matte dark canvas base: `#0f1117` with soft elevated cards `#171a23`.
  - Primary text: Soft off-white `#f1f3f9`; secondary text: Warm slate `#a2abbd`.
- [ ] **Motion & Animation Controls**:
  - Respect `prefers-reduced-motion: reduce`.
  - No auto-playing videos, looping GIFs, pulsing banners, or animated carousels.
  - Transitions must be instant or smooth linear fades (<200ms).
- [ ] **Sound Design**:
  - Audio cues must be soft, non-startling chimes; never harsh buzzers or error alarms.
