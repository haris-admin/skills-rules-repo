# Next.js Data Cache: A Takedown Must Expire Immediately

The Next.js data cache never stores a 404, so after a revalidation or TTL a stale cached 200 for an unpublished item keeps being served; a takedown must expire the tag immediately with `revalidateTag(tag, { expire: 0 })`. Applies to any route that reads a CMS or backend item through a cached `fetch` and must stop serving it once unpublished, archived or deleted.

**Scope:** Next.js 16.x App Router sites with tagged or timed cached reads (worked example: AMLHive markdown twin of a blog post, 6 Oct 2026, T519.17).

---

## Why this exists

The markdown twin of a blog post kept serving after the post was unpublished. After revalidate or TTL, the only cache entry for that item was the stale 200, and the refresh that would have produced a 404 stored nothing, so the stale 200 was served again for ever while the backend already returned 404. Stale-while-revalidate makes it worse: the stale value is returned first.

## Core Directives

1. **A takedown uses immediate expiry:** `revalidateTag(tag, { expire: 0 })`. Never stale-while-revalidate or a time-based `revalidate` for a takedown. A publish or edit may use the softer form.
2. **Do not rely on the cache to learn "not found".** A non-OK backend answer for a single item returns the 404 or 410 response and never falls back to a cached value for that item.
3. **Tag every cached read** with an item tag (`blog:<slug>`) and a list tag so a takedown expires both.
4. **Prove it on a real production build.** `next build` and `next start` against a stub backend: publish, fetch (200), unpublish, call the revalidate hook, fetch again and require 404 on every representation (HTML, markdown twin, feed, sitemap). A unit test that imports the handler cannot show cache behaviour.
5. **Do the proof in a scratch copy** that follows `rules/scratch-app-copies-never-include-env-files.md`; the revalidate hook can call real third parties when real keys are present.
6. **A stale local `node_modules` can fake a build failure** (`Cannot find module @vercel/turbopack/postcss`); install fresh in the scratch copy before blaming the code.

---

## Patterns to Follow

```ts
import { revalidateTag } from 'next/cache';
revalidateTag(`blog:${slug}`, { expire: 0 });   // takedown: immediate expiry
revalidateTag('blog:list', { expire: 0 });
```

## Patterns to Avoid

```ts
revalidateTag(`blog:${slug}`, 'max');            // stale-while-revalidate: the stale 200 is served again
fetch(url, { next: { revalidate: 300 } });       // TTL only: no takedown path at all
```

---

## Verification & Guardrails

- A real-server proof script asserts 404 on every representation immediately after takedown, with no TTL wait.
- Related: `rules/agent-legible-website.md`, `rules/public-discoverability-crawler-access.md`.
