# Lighthouse performance gate (all agents) — blocking, not guidance

Human decision, 7 Aug 2026, prompted by `frontend/prod_issues/issue-246-turnstile-csp-block-and-lighthouse-perf-regression.md`:
two live Lighthouse reports (mobile + desktop) showed `yourapp.com.au` regressing from
Performance 92 (OpenSpec `310-homepage-performance-optimization`, implemented) to **70 mobile**,
with a CSP misconfiguration silently disabling the site's own anti-spam control on top of it —
and no gate existed that would have caught either before it reached production.

## The rule

**A change that touches a public-facing route (anything under `frontend/app/` served outside
`/dashboard/**` and `/admin/**`, including shared layout, global CSS, third-party script loaders,
or the CSP builder) is not ready to mark `Fixed`/`status: implemented`/merge to `dev` unless a
Lighthouse run — mobile **and** desktop — is cited as evidence and clears the bar below.** This is
the same evidentiary standard the repo already applies elsewhere (`status: implemented` requires a
commit; the core audit-trail mandate requires a durable row) — a Lighthouse score claim without a
cited run is not evidence, same as an audit-trail claim without a row.

| Category | Hard floor (block below this) | Target |
|---|---|---|
| Performance — mobile | **93** | 100 |
| Performance — desktop | **93** | 100 |
| Accessibility | 100 | 100 |
| Best Practices | 100 | 100 (a CSP console error, like issue-246's, is an automatic fail here) |
| SEO | 100 | 100 |

Core Web Vitals floors (both form factors unless noted):

- **LCP** ≤ 2.5 s mobile / ≤ 1.0 s desktop
- **FCP** ≤ 1.8 s mobile / ≤ 0.8 s desktop
- **TBT** ≤ 200 ms
- **CLS** ≤ 0.00 (zero — no non-composited animation on an above-the-fold element; see 310's
  `shimmerText` fix for the pattern of what *not* to do)

**Ambiguity resolves to blocking.** If you cannot produce a same-session Lighthouse run for a
change that touches a public route, the change is not done — surface that gap and ask, the same
posture the retention mandate takes ("in case of any ambiguity … we can't take a risk").

## How to run it (three tiers, pick the first that's available)

1. **CI (authoritative):** `.github/workflows/lighthouse-ci.yml` runs `treosh/lighthouse-ci-action`
   against a production build served on `localhost`, both `mobile` and `desktop` LHCI presets, and
   fails the job if performance drops below 93 on either. Like this repo's other test workflows
   (`frontend-tests.yml`), it is `workflow_dispatch`-triggered, not a GitHub branch-protection
   required check — running it before merging a public-route change is a discipline this doc
   mandates, not something GitHub enforces automatically. Run it deliberately; a green run is the
   evidence a completion log or prod-issue fix cites.
2. **Local, Chrome/Chromium present:** `cd frontend && npm run audit:lighthouse:local -- --url=http://localhost:3000` —
   wraps the `lighthouse` CLI for both presets against a locally built+served app. Use this when
   iterating on a fix before pushing.
3. **No local Chrome (e.g. this repo's Claude Code sandbox has none installed):**
   `cd frontend && npm run audit:lighthouse -- --url=<deployed-or-preview-url>` — calls the public
   Google PageSpeed Insights API (no Chrome binary needed, works anywhere with outbound HTTPS) for
   both `strategy=mobile` and `strategy=desktop` against an already-reachable URL. This cannot check
   pre-deploy local changes (PSI fetches a live URL) — use it against a preview/staging deploy, or
   post-deploy as the live confirmation step a prod-issue fix needs anyway (same posture as
   issue-167's "verify live, not just locally").

None of these three requires the data to leave `ap-southeast-2` in a sovereignty-relevant sense —
they're checking an already-public marketing page's load performance, not processing customer or
compliance data; the pricing/data-sovereignty rule elsewhere in `CLAUDE.md`/`AGENTS.md` doesn't
apply here.

## What this does not gate

- `/dashboard/**` and `/admin/**` authenticated app routes — no Lighthouse SEO/marketing-page
  concerns apply there; use normal perf profiling (React DevTools Profiler) and
  **`/prod-db-perf-audit`**, whose Step 5b now covers the *frontend* request-per-item scan for
  these routes as well as the backend query audit.

  **This delegation had a hole until 12 Aug 2026, and something real fell through it.** The gate
  excluded authenticated routes and pointed at `/prod-db-perf-audit`, but that skill only read
  backend code — so no check owned frontend data-fetching on `/dashboard/**`. C405 found
  `clients/page.tsx` issuing one `GET /matters/{id}` **per matter** on every page load, against a
  table that was sequentially scanning. Step 5b was added to close it. If you exclude a route
  class from a gate by delegating it, confirm the thing you delegated to actually covers it.
- A change that doesn't touch any public route or its shared chunks (layout, `globals.css`,
  `lib/csp.ts`, `next.config.ts`, third-party script components) is unaffected by this gate.

## Recurring root causes to check first (from issue-246 and OpenSpec 310/396)

- **CSP drift:** every new 3rd-party script (Turnstile, a new pixel, a new tag manager) needs its
  origin added to `frontend/lib/csp.ts`'s `script-src`/`connect-src`/`frame-src`/`img-src` as
  appropriate, with a test in `tests/unit/lib/csp.test.ts` — see issue-033, issue-167, issue-246 for
  the exact same bug shipping three times.
- **Legacy JS / polyfills — usually a false positive, not fixable at the app level:** a `core-js`
  polyfill showing up in the Lighthouse "Legacy JavaScript" audit for a Baseline-since-2020+ feature
  (`Array.prototype.at`/`flat`/`flatMap`, `Object.fromEntries`/`hasOwn`,
  `String.prototype.trimStart`/`trimEnd`) is very likely **Next.js's own internal polyfill module**,
  not a real `core-js`/`core-js-pure` dependency — confirmed 7 Aug 2026 by fetching the live chunk
  and reading the flagged bytes (`find node_modules -iname "core-js*"` came back empty). It's a
  Lighthouse library-detector false positive on Next's feature-detection idiom, ships unconditionally
  in every Next.js production build, and is not fixable at the application level as of Next.js
  16.2.7. **`tsconfig.json`'s `target` does not affect this either way** — this project builds with
  **Turbopack** (`next build` defaults to it as of Next 16), under which `tsconfig.json`'s `target`
  is inert for the shipped bundle (Next/SWC's real transpilation target comes from `browserslist` in
  `package.json`). Don't re-chase this finding — see
  `openspec/changes/396-homepage-performance-regression-round-2/tasks.md` T396.01.
- **CDN/edge bot-detection or security scripts:** before assuming a large unexplained main-thread
  task is app code, check which origin it's actually on — a task under `/cdn-cgi/` (Cloudflare) or
  similar is proxy/edge infrastructure, and can dwarf every other cost found. Confirmed 8 Aug 2026:
  Cloudflare's `enable_js` Bot Management "JS Detection" script cost 1.1–1.2s of TBT on
  `yourapp.com.au`, more than every other 3rd-party script combined, with **no downstream
  consumer** (Bot Fight Mode was off, no WAF rule referenced the bot score). Diagnose read-only via
  the Cloudflare API before touching anything: zone ID via `GET /zones?name=yourapp.com.au`, then
  `GET /zones/{id}/settings/security_level`, `GET /zones/{id}/bot_management`, and
  `GET /zones/{id}/rulesets/{custom_firewall_ruleset_id}` to confirm no rule's `expression`
  references the bot score before recommending `enable_js: false`. Credentials from AWS Secrets
  Manager (`CLOUDFLARE_ACCOUNT_TOKEN`/`CLOUDFLARE_ACCOUNT_ID` in `yourapp/prod/backend`) per
  `docs/agent_rules/aws-profile-and-secret-recovery.md` — never `wrangler login`. This is a
  security-adjacent zone setting: get explicit human sign-off before changing it, same as any other
  production security control.
- **Build-tool config mismatches (Turbopack vs webpack):** this project's `next build` defaults to
  **Turbopack** — any performance fix or diagnostic tool scoped to webpack (a webpack
  `resolve`/`treeshake` option inside `withSentryConfig`, `@next/bundle-analyzer`, a `next.config.ts`
  `webpack()` callback) may silently not apply, giving false confidence a fix landed. Confirmed twice
  in one session (8 Aug 2026): `tsconfig.json`'s `target` (above) and a
  `withSentryConfig({ webpack: { treeshake: {...} } })` option were both no-ops for the real bundle.
  Before trusting a webpack-oriented fix, check `npx next build --help` for the Turbopack-native
  equivalent — e.g. `next build --experimental-analyze` (writes
  `.next/diagnostics/route-bundle-stats.json`, per-route First Load JS + chunk byte sizes) instead of
  installing `@next/bundle-analyzer`.
- **3rd-party main-thread cost:** confirm `ClarityScript`/`MetaPixel`/`GoogleAdsTag` are still using
  `strategy="lazyOnload"` + `requestIdleCallback` deferral (the existing pattern) before adding any
  new tracking script — never load a 3rd-party tag synchronously in `<head>` or with `next/script`'s
  `beforeInteractive`/`afterInteractive` strategies on a public route.
- **Missing preconnect:** every 3rd-party origin the page actually calls in its critical path
  (analytics, error reporting like Sentry ingest) should have a matching
  `<link rel="preconnect">`/`dns-prefetch` in `app/layout.tsx` — Lighthouse's "Preconnect candidates"
  insight lists exactly what's missing.
- **`npm run audit:lighthouse:local`'s default `simulate` throttling can hide a real finding
  entirely, not just misreport a noisy metric.** Confirmed 21 Aug 2026 (issue-271): a
  `third-party-cookies`/`inspector-issues` Best Practices failure (Clarity/Bing tracking cookies)
  scored a clean 100 under `simulate` but 73–77 under `--throttling-method=devtools` — the exact
  method the real CI config (`.github/lighthouse/lighthouserc.*.json`) uses. Cross-check with
  `--throttling-method=devtools` before trusting a clean local score on Accessibility/Best
  Practices/SEO, the same way trap #8 in `.claude/skills/lighthouse-performance-gate/SKILL.md`
  already requires for a failing Performance/LCP number.

## Root-causing a specific finding (LCP delay, a long task) — not just checking the score

The three tiers above return a score; to attribute *why*, retain the full JSON instead of letting
the wrapper scripts discard it:

```bash
npx lighthouse <url> --output=json --output-path=<scratchpad>/trace.json \
  --chrome-flags="--headless --no-sandbox" --only-categories=performance --quiet
```

Then inspect `audits['lcp-breakdown-insight']`, `audits['long-tasks']`, and
`audits['network-requests']` in the JSON for phase/task/request-level attribution — the score-only
wrapper scripts (`audit:lighthouse:local`, `audit:lighthouse`) discard this detail.

**Trace the live URL, not a local `next start` build, when root-causing LCP or long tasks
specifically.** Confirmed 8 Aug 2026: a local trace produced internally inconsistent numbers (91ms
element render delay against a 4.3s total simulated LCP) and swung 76→86 Performance run-to-run —
localhost lacks the compression/CDN characteristics Lighthouse's simulated-throttling model assumes.
Local traces are still fine for catching gross app-level regressions and iterating before a deploy;
they're not reliable for pinning an exact millisecond-level cause.

**When reporting a finding, cite Lighthouse's own estimated savings for it** (e.g. "Est savings of
150 ms" for render-blocking requests, "Est savings of 26 KiB" for legacy JS, "Est savings of 259 KiB"
for unused JS) — pulled from the pasted report's Insights section or the JSON's `numericValue`/
`displayValue` fields, not just named as a root cause with no size attached. This states the fix's
expected impact up front and lets a human weigh several findings against each other before picking
which to act on first.

## Reference

Founding incident: `frontend/prod_issues/issue-246-turnstile-csp-block-and-lighthouse-perf-regression.md`.
Prior remediation this gate builds on: `openspec/changes/310-homepage-performance-optimization/`
(implemented) and `openspec/changes/396-homepage-performance-regression-round-2/` (the round that
prompted this gate). Claude: `yourapp-jeff-dean-performance-audit` skill (latency-ratio framing) and
the `lighthouse-performance-gate` skill (this gate's runnable checklist). Cursor:
`.cursor/rules/frontend-lighthouse-performance-gate.mdc`. Antigravity:
`.agents/rules/frontend-lighthouse-performance-gate.md`.
