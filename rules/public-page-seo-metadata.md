# Public page SEO metadata (all agents)

Applies when adding or editing public/marketing routes in `frontend/app/` that appear in `sitemapRoutes`.

For a **brand-new** public route, this doc covers only the title/description/canonical piece —
see [new-public-page-registration-checklist.md](new-public-page-registration-checklist.md) for the
full registration list (`PUBLIC_PATHS`, `ai-discovery.ts`, content-guard, footer, etc.).
Admin routes (`frontend/app/admin/**`) are not SEO surfaces — register them in
`PRIVATE_ADMIN_ROUTE_TEMPLATES` per that checklist's Private admin pages section.

Regressions: `frontend/prod_issues/issue-088`, `issue-089`.

## Canonical (hard requirement — blocks Bing indexing)

- Every sitemap HTML route needs `layout.tsx` metadata or server `page.tsx` `export const metadata`.
- `alternates.canonical` must be the **page’s own URL** — never inherit root `app/layout.tsx` (`canonical: "/"`) on child routes.
- `'use client'` pages **still require** a parent `layout.tsx` for metadata.

## Title and meta description (hard limits)

Enforced in `frontend/lib/seo-metadata.ts` and `npm run audit:seo-metadata`:

| Field | Hard min | Hard max | Notes |
|-------|----------|----------|--------|
| `<title>` | — | **60** chars | Bing “title too long” above this |
| `<meta name="description">` | **120** chars | **160** chars | **Not 180** — Bing flagged 212; Google truncates SERP snippets near 155–160 |

Trim SERP `title` / `description` only; keep full headline in on-page H1 and JSON-LD `headline`.

## Registry and tests

1. Register the route in `frontend/lib/public-seo-metadata-registry.ts`.
2. Run `cd frontend && npm run audit:seo-metadata`.
3. CI **fails** on wrong canonical; title/description gaps are **reported** for periodic cleanup.

## Periodic audit

```bash
cd frontend && npm run audit:seo-metadata
cd frontend && npm run audit:seo-metadata -- --live --base-url=https://yourapp.com.au --blog-api-url=https://api.yourapp.com.au
```

Claude: `/seo-metadata-audit` skill. Cursor: `.cursor/rules/public-page-seo-metadata.mdc`.

## New prod issues

Use the next global ID per [prod-issue-numbering.md](prod-issue-numbering.md) (frontend-only unless backend is involved).
