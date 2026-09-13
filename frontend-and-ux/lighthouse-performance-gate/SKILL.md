---
name: lighthouse-performance-gate
description: Enforce strict performance, accessibility, best practices, and SEO benchmarks on frontend builds. Use when reviewing a frontend build or PR for Lighthouse scores, checking LCP/CLS/INP against targets, or gating a release on performance/accessibility/SEO thresholds.
---

# Lighthouse Performance Gate

## Standards
- **Performance**: Minimum score 93+ (Target 100).
- **Largest Contentful Paint (LCP)**: < 2.5s.
- **Cumulative Layout Shift (CLS)**: < 0.1.
- **First Input Delay / INP**: < 200ms.
- **Accessibility & SEO**: Strict 100.

