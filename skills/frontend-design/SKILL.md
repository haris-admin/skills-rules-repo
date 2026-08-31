---
name: frontend-design
description: Design and implement React UI components with Tailwind CSS, following the Sovereign OS design system and ADHD-friendly principles.
---

# Frontend Design Skill

## When to use
Invoke when the user asks to design, build, or refine a UI component, page layout, or visual element in the Sovereign OS React frontend.

## Design Principles

1. **ADHD-friendly.** Reduce visual noise. One clear action per view. Use whitespace generously. Avoid walls of text — use progressive disclosure.
2. **LOD-aware.** Components must respect the current Level of Detail setting (Compass / Sprint / Map). Compass shows only the immediate task. Sprint shows the current block. Map shows the full picture.
3. **Steerable.** All AI-generated UI must be controllable via the Steering Drawer dials (Persona, Scaffolding, Grit, LOD). Read from `localStorage` before rendering.
4. **Calm signals.** Use Section Health dots, Shadow State pills, and Authenticity Pulse — not raw scores or loading spinners with percentages.

## Tech Constraints

- React 18 + Create React App (no TypeScript).
- Tailwind CSS + custom CSS where Tailwind falls short.
- Australian English in all user-facing text.
- Zero em-dashes — the style checker will block them.
- Components go in `src/components/`. Pages go in `src/pages/`.

## Workflow

1. **Understand the need.** Clarify what the component does, where it lives, and who interacts with it.
2. **Check existing components.** Search `src/components/` for similar patterns before creating new ones. Reuse and extend.
3. **Sketch the structure.** Describe the component tree and props before writing code.
4. **Implement.** Write the component with Tailwind classes. Keep files under 500 lines. Use functional components with hooks.
5. **Wire up.** Connect to EventBus if the component emits spine events. Connect to localStorage for steering state.
6. **Verify.** Run the build. Check for style violations with `node scripts/check-style.js`.

## Colour and Typography
- Defer to existing Tailwind config and CSS variables in the project.
- Use `text-sm` / `text-base` for body, `text-lg` / `text-xl` for headings.
- High contrast for readability. Dark mode support if the project uses it.
