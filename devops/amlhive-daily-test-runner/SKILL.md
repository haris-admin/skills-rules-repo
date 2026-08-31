---
name: amlhive-daily-test-runner
description: Use when running the AML Hive daily test suite.
---

# AML Hive Daily Test Suite

Cron `044c0bc41e31` (daily 3:00 AM AEST, no_agent) → `~/.hermes/scripts/amlhive_daily_test_runner.py`.

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

## Pitfalls
- As of W32 (Aug 16): **11 failing tests** (6,320 passed) — 9 backend pytest,
  1 frontend `signOut` double-call race, 1 E2E `a11y-reduced-motion-parity`.
  Backend also shows `poetry not found → venv fallback`. These are REAL
  regressions, not infra — route to Codex/dev for root-cause (see
  `coding-agent-delegation`).
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
