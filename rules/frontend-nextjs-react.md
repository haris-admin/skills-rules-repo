# Frontend Engineering: Next.js & React Guidelines

Guidelines for building fast, accessible, and scalable React and Next.js applications.

## Architecture & Framework Rules

1. **Next.js App Router**:
   - Default to Server Components (`RSC`). Only add `'use client'` when state, effects, or browser APIs are necessary.
   - Keep Client Component boundaries as deep down the component tree as possible.
   - Use Server Actions or Route Handlers for server-side mutations.

2. **TypeScript & Types**:
   - Maintain strict typing: avoid `any` and unvalidated type assertions (`as Type`).
   - Define clear interfaces/types for component props and export shared data contracts.
   - Leverage utility types (`Pick`, `Omit`, `Partial`, `Readonly`) to avoid duplication.

3. **Styling & Design Systems**:
   - Prefer Tailwind CSS utility classes with consistent spacing and typography scales.
   - Use helper utilities like `clsx` and `tailwind-merge` (`cn(...)`) for conditional class merging.
   - Support dark mode natively using Tailwind classes.

4. **Accessibility (a11y)**:
   - Ensure semantic HTML tags (`<header>`, `<nav>`, `<main>`, `<button>`, `<section>`).
   - Provide `alt` text for images and `aria-label` / `aria-labelledby` for icon-only buttons.
   - Maintain keyboard navigability with visible `:focus-visible` outlines.

5. **Performance & Web Vitals**:
   - Optimize images using `next/image` with explicit width/height and responsive sizes.
   - Lazy load heavy client components with `next/dynamic` or React `Suspense`.
