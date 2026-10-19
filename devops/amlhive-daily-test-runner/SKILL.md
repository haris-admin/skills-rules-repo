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
- **Current baseline (2026-10-19, day 13): `8056 passed / 39 failed`, but the backend number is now SPLIT — read the split, not the total.** 34 backend pytest → `⚪ 30/34 are SQLite-vs-PostgreSQL suite gaps (issue-134)` + `🔴 4 genuine assertion failures`; 1 frontend
  vitest (`Blob` instanceof in jsdom + concurrent-signOut race); 4 Playwright E2E. The old "11 failing,
  6,320 passed" figure (W32, Aug 16) is SUPERSEDED — do not quote it. The 34-failure backend band has
  been flat since 2026-10-09 (post-`origin/dev`-merge elevation, ~4× the 6-8 pre-merge baseline) and is a
  COUNT-TREND watch, not a per-day incident; escalate only on a trend change or a new component. **Since
  10-19 the actionable backend number is the GENUINE count (4), not 34** — a rising 🔴 count or a
  collapsing ⚪ share is the escalation trigger. The E2E
  leg DOES move: it sat at `48 passed / 2 failed` (whitelisted `reduced-motion`) from 10-13 to 10-17 and
  jumped to `46/4` on 10-18 with the diagnosis naming a **forgot-password recovery-copy/CTA** assertion and
  an **NFR load-timing benchmark** — read the per-leg diagnosis before calling E2E "the usual flake".
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
