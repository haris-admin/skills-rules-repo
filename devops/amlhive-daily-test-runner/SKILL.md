---
name: amlhive-daily-test-runner
description: Use when running the AML Hive daily test suite.
---

# AML Hive Daily Test Suite

Cron `044c0bc41e31` (daily **3:40 AM** AEST — the job's own NAME still reads "03:00 AM" and is stale;
the schedule expr is `40 3 * * *`) → `~/.hermes/scripts/amlhive_daily_test_runner.py`.

**Purpose:** Run the full AML Hive test pyramid daily against the native WSL
ext4 repo `~/code/amlhive1` (3–10× faster than the NTFS mirror):
- backend pytest (SQLite)
- frontend Vitest
- Playwright E2E

**Failure diagnosis** is routed to OpenRouter free models for root-cause hints.

**Repo semantics (updated Aug 23):** the runner now does `git fetch` →
`checkout pluto_pr` (or `checkout -B pluto_pr origin/pluto_pr` if missing) →
`reset --hard origin/pluto_pr` → `merge origin/dev --no-edit`, then runs the
suite on the merged tree (user instruction Aug 23: pull ALL code back onto
`pluto_pr` so the branch the main agent reviews has genuinely-green results).
The OLD stash-push-then-pop flow was popping `stash@{0}` (unrelated old WIP)
when nothing was stashed, re-corrupting the index every run — do NOT
reintroduce stash/pop. (Earlier it was `reset --hard origin/dev` directly.)

**01 Sep 2026 (month-end rule):** two additions to the runner —
1. **Pre-merge untracked-file cleanup**: after `reset --hard origin/pluto_pr`
   the runner runs `git clean -fd` (untracked NON-IGNORED files only; gitignored
   .env etc. are safe). Fixes the Aug 31 blocker where a stray untracked
   `frontend/tests/screening-page-resilience.test.ts` made `git merge
   origin/dev` abort with "untracked working tree file would be overwritten".
2. **Known-flake whitelist with 3-run escalation** (`~/.hermes/state/
amlhive_known_flaky.json`): the recurring frontend set (Blob/JSDOM issue-279
   test, reduced-motion E2E, signOut race) drifted 17 days without escalation.
   Runs 1–2 whose failures match `KNOWN_FLAKY_PATTERNS` stay green
   (reported whitelisted); run 3+ escalates to a real failure + Codex route.
   Exit code still reflects real failure state (`sys.exit(1)` on un-whitelisted
   fail/error).

## Pitfalls
- **`npm ci` EUSAGE = the lockfile is out of sync with `package.json`; it is a REPO fault, not a runner fault.** Signature: `npm error code EUSAGE` / ``npm ci` can only install packages when your package.json and package-lock.json are in sync` followed by a long `Missing: <pkg>@<ver> from lock file` list. Seen 2026-10-31: `Missing: webpack@5.112.2 …` (plus the whole `@webassemblyjs/*` tree) after commit `50fb44a55` (zod 3→4.6.7) rewrote `frontend/package-lock.json` deleting 580 lines without a full `npm install` regeneration — `@sentry/bundler-plugins` peer-requires `webpack >=5.0.0`, so the omitted tree surfaces as the missing list. It is deterministic: `npm ci --dry-run` on a CLEAN tree reproduces it, and it landed on `origin/dev`, so every clone and every CI job hits it. Confirm reach from the remote before assigning blame (`git merge-base --is-ancestor <sha> origin/dev`) — a lock drift confined to a lane is a local problem, one on `dev` is fleet-wide. Fix is `npm install` in `frontend/` then commit the regenerated lock; do NOT hand-edit the lock, and do NOT patch the runner to "work around" it.
- **Current baseline (2026-10-31, day 25): `9846 passed / 58 failed / 3 errors`.** Backend `9518 passed / 53 failed` → `⚪ 35/53 are SQLite-vs-PostgreSQL suite gaps (issue-134)` + `🔴 18 genuine`. The previous band (days 20-22) was `9274/51` with `🔴 16`; the 10-31 move is explained by a **202-commit `origin/dev` merge** into `pluto_pr` (+244 collected), NOT a regression — a big merge moves the collected count, the failing count, and the 🔴 count together. Always get the merge size (`git log --oneline <merge>^1..<merge>^2 | wc -l`) before calling a count-trend break.
  **`npm ci` can fail and the frontend leg will STILL report counts — read the install line first.** 2026-10-31 04:44: `❌ Frontend dep install failed: … EUSAGE` (see the lockfiles pitfall below) yet vitest printed `282 passed / 1 failed` against the PRE-EXISTING `node_modules`. Those numbers are not wrong, they are from the WRONG tree — No-Fake-Pass says surface the environment blocker, never present that leg as a pass, and never diagnose its failures as code until the install succeeds.
  The older band (2026-10-20, day 14) is kept for trend only: `8057 passed / 38 failed`, backend `34` split `⚪ 30/34` + `🔴 4`; 1 frontend
  vitest (`Blob` instanceof in jsdom + concurrent-signOut race, now **15 consecutive** runs escalated as
  real); 3 Playwright E2E (**13 consecutive**). The old "11 failing,
  6,320 passed" figure (W32, Aug 16) is SUPERSEDED — do not quote it. The 34-failure backend band has
  been flat since 2026-10-09 (post-`origin/dev`-merge elevation, ~4× the 6-8 pre-merge baseline) and is a
  COUNT-TREND watch, not a per-day incident; escalate only on a trend change or a new component. **Since
  10-19 the actionable backend number is the GENUINE count (4), not 34** — a rising 🔴 count or a
  collapsing ⚪ share is the escalation trigger. The E2E
  leg DOES move: it sat at `48 passed / 2 failed` (whitelisted `reduced-motion`) from 10-13 to 10-17,
  jumped to `46/4` on 10-18 and `47/3` on 10-20 with the diagnosis naming an **NFR load-timing benchmark**
  (and on 10-18 a **forgot-password recovery-copy/CTA** assertion) — read the per-leg diagnosis before
  calling E2E "the usual flake"; it is only back on `48/2` when the composition says so.
  Backend always shows `poetry not found → venv fallback` — that is the PERMANENT path on this host, never
  a fault. Real failures here are REAL regressions, not infra — route to Codex/dev for root-cause (see
  `coding-agent-delegation`).

**From 2026-10-19 the backend leg classifies SQLite-vs-PostgreSQL suite gaps** (`classify_pg_gated()`,
added 2026-10-18 06:03 after the issue-134 investigation). It matches ONLY pytest's `--tb=line` form
(`^/\S+\.py:\d+: ` + one of `requires TEST_DATABASE_URL` / `no such table: pg_roles` / `type 'UUID' is not
supported`), prints `⚪ N/<failed> are SQLite-vs-PostgreSQL suite gaps (issue-134), not product
regressions`, and stops routing to OpenRouter when every failure is PG-gated. **Expect a new ⚪ line and
a SILENT backend diagnosis from the next run — that is not a fix and not a fake pass** (failures are still
counted, exit code still reflects them). If the ⚪ count exceeds the failed count, or a NORMAL
`AssertionError: assert 1 == 2`-shaped failure lands in it, the classifier has over-matched — fix the
regex, do not accept the masking.
- **backend/.venv drifts from pyproject.toml → 54 collection errors (Aug 18).**
  `poetry` is NOT installed on this host, so the runner's "venv fallback"
  (`backend/.venv/bin/pytest`) is the real backend path. When a new dep is added
  to `backend/pyproject.toml` (e.g. `rapidfuzz` for `identity_matching_service`)
  but nobody runs install, the venv goes stale and EVERY test file importing it
  throws `ModuleNotFoundError` at collection → "Interrupted: 54 errors during
  collection" → `0 passed`. Diagnose + fix:
  ```bash
  cd ~/code/amlhive1/backend
  .venv/bin/python -m pytest tests/ --collect-only -q 2>&1 | grep -oE "No module named '[^']+'" | sort -u
  uv pip install --python .venv/bin/python "rapidfuzz>=3.14.5"   # uv @ ~/.local/bin/uv
  ```
  A clean collection (~6000 tests) confirms the fix. Do NOT route
  `ModuleNotFoundError` collection errors to Codex as test *regressions* —
  they're an env-sync gap; `uv pip install` the missing module first.
- A2Square frontend has a SEPARATE weekly runner (`a2square_weekly_test_runner.py`,
  cron `0320d41d6d71`) — don't conflate the two suites.
- E2E takes ~9–15 min; run with timeout 1800s.
