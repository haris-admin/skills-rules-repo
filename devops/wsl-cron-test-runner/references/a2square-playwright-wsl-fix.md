# A2Square Weekly Suite — WSL Playwright Fix Chain (Aug 2026)

Full debug story behind the `0 passed, 31 failed` Tapease frontend weekly cron
failure and the four-part fix. Companion to the SKILL.md section
"Tapease/A2Square Playwright on WSL".

## Symptom
Cron `0320d41d6d71` (Mon 02:30): `❌ 0 passed, 31 failed across 3 repos`.
The two pytest repos were green (0/0 — no tests collected); all failures were
Playwright on `tapease_frontend_nextjs_prod`.

## Root-cause chain (each confirmed by evidence)

1. **`channel: 'chrome'` fails on WSL.** Repo `playwright.config.js` uses
   `channel: 'chrome'` → Playwright looks for `/opt/google/chrome/chrome`
   which does not exist on WSL. Error: `browserType.launch: Chromium
   distribution 'chrome' is not found at /opt/google/chrome/chrome`.
   **Symptom signature:** ALL failures at 5–13ms execution time = browser
   launch failure, not app logic.

2. **`webServer` block commented out in repo config.** Nothing listened on
   :3005 at 2:30 AM → after fixing the browser, next error was
   `net::ERR_CONNECTION_REFUSED at http://localhost:3005/login`.

3. **Stale node_modules.** `package.json`/`package-lock.json` modified
   Jul 28, `node_modules` from Jul 11 → dev server compiled with
   `Module not found: Can't resolve '@tanstack/react-query'`. `npm ci`
   (713 packages) fixed it. mtime compare lock vs node_modules is the
   dep-sync trigger for the runner.

4. **Auth-guard warmup trap.** Tapease `src/proxy.js` (Next proxy) redirects
   `/member/*` and `/admin/*` to `/login?next=...` when no `access_token`
   cookie is present. A naive warmup fetch of protected routes returns 302 →
   those routes never compile → first real navigation after login
   cold-compiles 10–25s → blows the hardcoded
   `waitForURL(..., {timeout:10000})` in auth.spec.js. Warmup must send the
   mock admin JWT cookie (read live from api-mocks.js — JWTs are redacted in
   tool output) and use `redirect:'manual'` so 200 vs 302 is visible.

5. **Server-side proxy check eats 5s per protected page.** `proxy.js` does
   `fetch(NEXT_PUBLIC_API_URL + '/policies/pending')` with
   `AbortSignal.timeout(5000)` on every protected navigation and **fails
   open**. With the real API unreachable from WSL, each page load carries
   ~5s of hang → `performance.spec.js` DataTable NFR failed
   (`expect(loadTime).toBeLessThan(5000)` got 5686ms). Fix: point
   `NEXT_PUBLIC_API_URL` at the dev server in webServer.env so the check
   404s fast. Measured `proxy.ts: 5.0s` → `281ms`, load 5686ms → 916ms.

## Fixes shipped
- `playwright.wsl.config.js` (untracked, repo root) — imports base config,
  strips `channel`, adds webServer auto-start, adds globalSetup warmup,
  overrides NEXT_PUBLIC_API_URL to `http://localhost:3005`. Untracked on
  purpose so `git pull --ff-only` never conflicts.
- `tests/e2e/helpers/wsl-warmup.global-setup.js` — warms public + protected
  routes with the admin JWT cookie.
- `a2square_weekly_test_runner.py` — points at `playwright.wsl.config.js`,
  adds npm-ci dep-sync (lockfile mtime vs node_modules), uses `--retries=1`.

## Final results
- auth.spec.js: 0 → **6 passed**
- Full suite retries=1: **35 passed / 1 failed / 1 skipped** (perf NFR flake
  only, passes solo in 916ms after the NEXT_PUBLIC_API_URL fix)
- Remaining noise: `user/payouts/search` + 2 admin endpoints log
  "Unmocked endpoint" — harmless (default empty response), matcher list in
  api-mocks.js slightly stale vs dashboard calls.

## Re-diagnosis checklist
When a cron test alert says "script failed" with a Playwright repo:
1. Read `~/.hermes/cron/output/<job_id>/<latest>.md` FIRST (real stdout).
2. Check failure timings: all ≈5ms → browser launch/config problem.
3. Check WebServer log lines for `proxy.ts: 5.0s` → server-side fetch eating
   the timeout (perf NFR failures).
4. Check `warmup ... -> 302` vs `200` for protected routes → auth guard.
5. Check lockfile mtime vs node_modules → stale deps.
