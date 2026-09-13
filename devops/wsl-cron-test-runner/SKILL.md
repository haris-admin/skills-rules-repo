---
name: wsl-cron-test-runner
description: "Sets up and debugs Playwright + pytest + Vitest test suites run from Hermes cron jobs on WSL — git mirror/stash sync, no-sudo browser install, per-repo runner config, dependency-sync and false-green guards, and other WSL-specific constraints (no sudo, slow /mnt/c, VPC-bound RDS). Use when writing or fixing a WSL cron test runner script, diagnosing a cron test suite that reports 0 tests/false-green/collection errors, installing or debugging Playwright browsers on WSL, or resolving a git-sync/PAT/credential failure in a mirrored repo."
version: 1.1.0
author: Pluto
tags: [testing, playwright, pytest, wsl, cron, ci]
---

# WSL Cron Test Runner

## Core Problem
Running automated test suites (pytest, Vitest, Playwright) from Hermes cron jobs on WSL. The WSL environment has different constraints than native Linux CI runners: no sudo in cron, slow mounted Windows filesystem (/mnt/c is NTFS via 9P protocol), VPC-bound databases, and Python version requirements.

## Critical Gotchas (read before touching any runner)

These three failure modes all produce the same shape of bug — a cron job that reports ✅ while having tested nothing real — and have each cost real debugging time:

1. **Dependency sync after mirror reset** — a merged dependency change (`pyproject.toml`/`poetry.lock`, `package.json`/`package-lock.json`) doesn't get reinstalled by a plain `git reset --hard`, so pytest/vitest fail at **collection** (`0 passed`) looking like a test regression when it's really an import failure. Fix: hash the dependency files and reinstall (`pip install -e .` / `npm ci`) whenever the hash changes.
2. **Mirror semantics — fetch + `reset --hard origin/dev`, never stash/pop on a pure mirror** — `git stash push` silently no-ops when there are no tracked changes, but a naive runner still calls `git stash pop` afterward, popping an UNRELATED old stash and corrupting the index on every run.
3. **False-green guard — 0 tests ran must be an ERROR, never a ✅** — `parse_pytest`/`parse_vitest` default to `0 passed` when there's no count line at all (config error, collection failure), which makes a totally broken run look green unless every parsed result carries a `ran` flag that a guard checks.

Full code, the exact failure signatures, and three related incident write-ups (a dep-sync trap that looked like a timeout, why a raw-hash version of the dep-sync fix over-fires, and the general "no fake pass" mandate) are in [references/mirror-sync-and-false-green-guards.md](references/mirror-sync-and-false-green-guards.md).

## Pre-Requisites: Always Pull Latest Code

**Always sync to the latest code before executing any test suite** — stale test results are worse than no results. For a pure test mirror, use fetch + `reset --hard` (gotcha #2 above); for a working copy that may carry real local edits, use the stash-pull-pop pattern in [references/git-sync-and-credentials.md](references/git-sync-and-credentials.md#git-stash--pull-pattern). This is non-negotiable and must run before ANY suite, wrapped in try/except so a sync failure is reported, not silently swallowed.

## Current AMLHive Daily Test Suite Architecture

The cron job (044c0bc41e31 at 03:00 AM) runs three suites in sequence in a single script (`amlhive_daily_test_runner.py`):

```
0. 📡 git pull --ff-only origin dev                ← always first
1. Backend pytest (900s default timeout)
   ├── poetry run pytest tests/ -q --no-header --tb=line
   │   └── Falls back to .venv/bin/pytest if poetry not found
   └── On failure: OpenRouter diagnosis via multiprocessing timeout (120s max)

2. Frontend Vitest (600s timeout)
   └── npm run test:unit  (from frontend/package.json)
   └── On failure: OpenRouter diagnosis via multiprocessing timeout

3. Playwright E2E
   ├── Chromium-deps guard: skip ONLY if ~/.local/chromium-deps missing (no more WSLInterop skip)
   ├── npx playwright install chromium
   ├── npm run test:e2e with LD_LIBRARY_PATH + PLAYWRIGHT_SKIP_VALIDATE_HOST_REQUIREMENTS=1 (full 12-project matrix, timeout 3600s, per-test 120000ms)
   └── On failure: OpenRouter diagnosis via multiprocessing timeout
```

**Timeout bump 2026-08-09 (all in `amlhive_daily_test_runner.py`):** diagnosis 30s→**120s**, E2E per-test 60000→**120000ms**, E2E suite 1800→**3600s**, git pull 30→**90s**. Rationale: the diagnosis timeout was expiring before the OpenRouter fallback could answer → produced the misleading "provider timeout" alert text; and the NFR/accessibility E2E test was near the 60s per-test edge. Backend pytest stays 5400s.

Each suite has its own try/except block so a timeout/failure in one doesn't block the others. Exit code = 0 only if ALL suites pass. The script prefers `poetry run pytest` but falls back cleanly to `.venv/bin/pytest` when poetry isn't installed (e.g. fresh WSL setup with `uv`) — see [references/runner-operations.md](references/runner-operations.md#poetry-vs-venv-fallback) for the fallback code.

## WSL-Specific Constraints

| Constraint | Impact | Mitigation |
|-----------|--------|------------|
| **Python version** | Backend requires Python >=3.13.12; WSL 24.04 ships 3.11 | Use `uv python install 3.13` to install CPython 3.13 alongside system Python. Create venv with `uv venv --python 3.13`. |
| **NTFS filesystem (/mnt/c)** | Tests run 3-4x slower on mounted Windows drive vs native ext4 | **Move repo to `~/code/` (native WSL ext4).** Repo at /mnt/c adds ~35s per pytest collection and 3-4x total test time. Copy: `rsync -a /mnt/c/Code/github/amlhive-tech/amlhive1/ ~/code/amlhive1/` then run tests from `~/code/amlhive1/backend/` |
| RDS VPC-bound | Backend pytest that needs RDS is unreachable from WSL | Check conftest.py — many projects use **in-memory SQLite** (e.g. AMLHive backend conftest.py line 4-5: `each test gets a fresh AsyncSession backed by an in-memory SQLite database`). If SQLite-backed, tests work fine on WSL without RDS. Full pattern: [references/runner-operations.md](references/runner-operations.md#common-pitfalls). |
| Slow /mnt/c filesystem | TypeScript/Jest compilation on mounted Windows FS is ~35s per file | Skip full Jest, prefer Vitest/Playwright E2E. **Moving repo to ext4 fixes this** — ext4 gives macOS-level performance |
| No sudo in cron | `npx playwright install --with-deps` prompts for sudo → hangs | Use `npx playwright install chromium` (no `--with-deps`) |
| Playwright needs browsers | Full browser download on first run takes 2-3 min | Cache persists in `~/.cache/ms-playwright/` |
| **Playwright on WSL** | All three browsers now run without sudo via a local-deps fix (see below) | See [references/playwright-wsl-setup.md](references/playwright-wsl-setup.md) |
| Git merge conflicts | Local changes from previous runs prevent `git pull` | Mirror = fetch+reset; working copy = stash-pull-pop (never a blind stash without restore) — see Critical Gotchas above |
| **OpenRouter API timeout** | `chat_with_fallback()` can hang indefinitely, blocking entire cron. The provider timeout error means the diagnosis API call never returned. | Wrap ALL API diagnosis calls in a hard timeout using `multiprocessing.Process` (**120s since Aug 2026**). If the API doesn't respond in 120s, kill it and log `"[Diagnosis skipped: timed out after 120s]"`. The test results themselves always deliver — only the nice-to-have diagnosis is sacrificed. Full pattern: [references/runner-operations.md](references/runner-operations.md#failure-diagnosis-via-openrouter--120s-hard-timeout). |

## Playwright on WSL

**All three Playwright browsers (Chromium, Firefox, WebKit) run on WSL without sudo**, via user-local `.deb` extraction plus `PLAYWRIGHT_SKIP_VALIDATE_HOST_REQUIREMENTS=1`, and the full 12-project device matrix runs with no `--project` filtering needed. A separate fix (`patchelf` RUNPATH patching) is required for the Hermes browser tool itself (`browser_navigate`), since it launches Chrome through a credential-scrubbed long-lived gateway process that never sees `.bashrc` env changes. Safe cron flags are `--workers=1 --retries=0 --timeout=60000` with no `--with-deps` on install; `webServer` config auto-starts/stops the dev server, but leftover processes from an interrupted manual run can block the next one and must be `pkill`ed first. Tapease/A2Square's frontend additionally needs its `channel: 'chrome'` config overridden (Chrome doesn't exist on WSL) plus an auth-guard warmup that sends a mock admin JWT cookie and an env override so its proxy's policy-check doesn't hang 5s per page.

Full setup recipe, all gotchas, the multi-device config, safe flags, webServer lifecycle, and the Tapease/A2Square fix: [references/playwright-wsl-setup.md](references/playwright-wsl-setup.md). Hermes-browser-tool-specific patchelf recipe: [references/hermes-browser-rpath-fix.md](references/hermes-browser-rpath-fix.md).

## No-Sudo ffmpeg for Audio Tasks

WSL has no system `ffmpeg` and no sudo to install it, and Playwright's bundled `ffmpeg-linux` is a stripped build without Opus/Ogg demuxing (fails on Telegram `.ogg` files). The Windows WinGet ffmpeg full build handles Opus fine and is callable directly from WSL; tools that shell out to the literal name `ffmpeg` (e.g. `whisper`) need a PATH shim pointing at it. Full recipe: [references/voice-transcription.md](references/voice-transcription.md).

## Git Sync and Credential Safety

Two different repo roles need two different sync patterns: a **pure test mirror** uses fetch + `reset --hard` (never stash/pop — see Critical Gotchas above); a **working copy that may carry real local edits** uses stash → pull `--ff-only` → pop, which itself can fail on a pre-existing unmerged (`UU`) file left by an earlier interrupted job, or hit a stale zero-byte `.git/index.lock`. Separately, a "provider timeout" cron alert is very often not a real provider failure — read the actual job output before diagnosing.

For git operations needing a GitHub PAT, **never embed the token via `git remote set-url`** — it stacks into `.git/config` on every re-tokenized pull (one repo was found with the PAT embedded 16 times) and classic GitHub PATs also reject `Authorization: Bearer` header auth, requiring the `x-access-token:<PAT>@` basic-auth form passed as a one-off command argument instead.

Full patterns, failure diagnostics, and remote-sanitization commands: [references/git-sync-and-credentials.md](references/git-sync-and-credentials.md). The related nightly review-branch mirror/merge workflow this all supports is documented in [references/review-branch-mirror-merge-flow.md](references/review-branch-mirror-merge-flow.md).

## Windows-Executor Jobs (driving a Windows-hosted job from WSL)

When a job script lives on the Windows side (`C:\Users\habib\.hermes\scripts\`) and reads its config from the Windows `.env`, run it with the Windows interpreter (`/mnt/c/Windows/py.exe`), copy WSL-side dated files into the Windows `research_outputs/` dir, and install any needed libs (e.g. chromadb) for the Windows Python. Also verify model IDs against the live OpenRouter catalog — docs go stale and free-tier keys 402 on paid models. Full recipe: [references/windows-executor-job-pattern.md](references/windows-executor-job-pattern.md).

## SSM / EC2 Operations

The test runner and related monitoring scripts use AWS SSM send-command to run shell commands on EC2 instances, avoiding the need for a direct (VPC-bound) network path to RDS. This covers the core `ssm_run()` pattern, per-project credential/secret lookups (AMLHive needs `rds-admin` first for cross-agency queries; never hardcode the DB username), instance IDs, and the EC2 version-fetch pattern used in reports. See [references/ssm-and-ec2-ops.md](references/ssm-and-ec2-ops.md). The AMLHive RDS secret name changed once in July 2026 — see [references/rds-secret-migration.md](references/rds-secret-migration.md) for what changed.

## Runner Script, Timeouts, Diagnosis, and Common Pitfalls

The full runner script skeleton (repo-sync → run tests → parse → report → exit code), the default timeout table for every suite, the OpenRouter-based failure-diagnosis wrapper (with its deprecated Codex CLI predecessor), the multi-repo runner architecture, and the full accumulated list of WSL cron-runner pitfalls (SSL-required RDS `/ready` checks, escaped-vs-real newlines in report output, Jest vs Vitest, missing `env=None` kwargs, production guards breaking existing mocks, Docker Desktop not reachable from WSL, and more) live in [references/runner-operations.md](references/runner-operations.md). Two specific pitfalls have their own deeper write-ups: [references/sqlite-inmemory-testing.md](references/sqlite-inmemory-testing.md) (why backend tests usually don't need RDS) and [references/postmark-pydantic-settings-trap.md](references/postmark-pydantic-settings-trap.md) (pydantic-settings guard traps) and [references/frontend-shared-response-race.md](references/frontend-shared-response-race.md) (a mocked-`Response` race in concurrent frontend tests).

## Expected Timings

Backend pytest (~5000 tests) takes ~10-15 minutes on WSL regardless of filesystem (WSL CPU, not disk I/O, is the bottleneck); Playwright E2E (full matrix) takes 3-5 minutes; Jest is 30-60 minutes on WSL and should be avoided in cron in favor of Vitest. Moving the repo from NTFS (`/mnt/c/`) to native ext4 (`~/code/`) gives a 3-4x speedup on I/O-bound steps (e.g. backend health tests: 17s → 5s) but doesn't help CPU-bound full-suite runs. Full measured tables for NTFS vs ext4: [references/expected-timings.md](references/expected-timings.md).

## GitHub Actions Workflow-Run Lookups

When a cron check needs the last successful run of a specific workflow (e.g. `hourly_version_check.py` finding the last "Deploy Backend to EC2 (AWS)" run to read its `backend/pyproject.toml` version), use `gh run list --workflow="<display name>"`. The REST `workflow_id` filter silently returns runs from OTHER workflows → false STALE_BUILD alerts. Full recipe incl. Python subprocess + Contents-API version read: [references/gh-workflow-run-lookup.md](references/gh-workflow-run-lookup.md).

**Transient GitHub API 401 ≠ dead PAT:** a single-run 401 with an unchanged, verified-live PAT is usually a blip, not a rotation trigger — diagnose live before rotating. Full debug story: [references/2026-08-14-false-green-debug.md](references/2026-08-14-false-green-debug.md).

## Reference Files

| File | Covers |
|------|--------|
| [references/mirror-sync-and-false-green-guards.md](references/mirror-sync-and-false-green-guards.md) | Dependency sync after mirror reset, fetch+reset mirror semantics, the 0-tests-ran false-green guard |
| [references/playwright-wsl-setup.md](references/playwright-wsl-setup.md) | No-sudo Chromium/Firefox/WebKit setup, multi-device config, safe cron flags, webServer lifecycle, Tapease/A2Square fix |
| [references/a2square-playwright-wsl-fix.md](references/a2square-playwright-wsl-fix.md) | Full root-cause narrative behind the A2Square "0 passed, 31 failed" incident and its four-part fix |
| [references/hermes-browser-rpath-fix.md](references/hermes-browser-rpath-fix.md) | patchelf RUNPATH fix for the Hermes browser tool's Chrome launch |
| [references/git-sync-and-credentials.md](references/git-sync-and-credentials.md) | Stash-pull-pop pattern, unmerged-file/index.lock failure modes, PAT credential safety |
| [references/review-branch-mirror-merge-flow.md](references/review-branch-mirror-merge-flow.md) | The nightly review-branch mirror + merge workflow (pluto_pr + dev) this sync machinery supports |
| [references/ssm-and-ec2-ops.md](references/ssm-and-ec2-ops.md) | SSM send-command pattern, per-project RDS credentials, instance IDs, EC2 version-fetch |
| [references/rds-secret-migration.md](references/rds-secret-migration.md) | The July 2026 AMLHive RDS secret name migration |
| [references/runner-operations.md](references/runner-operations.md) | Runner script skeleton, default timeouts, OpenRouter/Codex diagnosis wrappers, multi-repo architecture, common pitfalls |
| [references/codex-diagnosis-routing.md](references/codex-diagnosis-routing.md) | The original (July 2026) Codex-CLI-based diagnosis pattern, now superseded by the OpenRouter wrapper |
| [references/sqlite-inmemory-testing.md](references/sqlite-inmemory-testing.md) | Why AMLHive backend tests don't need RDS/Docker (in-memory SQLite in conftest.py) |
| [references/postmark-pydantic-settings-trap.md](references/postmark-pydantic-settings-trap.md) | pydantic-settings guard traps (`monkeypatch.setenv` timing) and stale full-suite results |
| [references/frontend-shared-response-race.md](references/frontend-shared-response-race.md) | A mocked-`Response` async race in concurrent frontend unit tests |
| [references/expected-timings.md](references/expected-timings.md) | Measured suite durations, NTFS vs native ext4 |
| [references/gh-workflow-run-lookup.md](references/gh-workflow-run-lookup.md) | `gh run list --workflow=` vs the REST `workflow_id` filter trap |
| [references/2026-08-14-false-green-debug.md](references/2026-08-14-false-green-debug.md) | Transient GitHub API 401 misdiagnosis debug story |
| [references/voice-transcription.md](references/voice-transcription.md) | No-sudo ffmpeg (Opus/Ogg) via the Windows WinGet build |
| [references/windows-executor-job-pattern.md](references/windows-executor-job-pattern.md) | Driving a Windows-hosted job script from WSL |
| [references/wsl-playwright-skip.md](references/wsl-playwright-skip.md) | (Historical, superseded) the pre-Aug-2026 skip-only pattern — kept as a warning never to blind-skip WSL E2E |
| [references/dep-sync-version-strip-hash.md](references/dep-sync-version-strip-hash.md) | Why the raw-`read_bytes()` dependency hash over-fires and the stripped-hash fix |
| [references/cron-script-timeout-and-dep-sync-trap.md](references/cron-script-timeout-and-dep-sync-trap.md) | A real "script timed out" alert traced back to the dep-sync version-bump trap |
| [references/no-fake-pass-guard.md](references/no-fake-pass-guard.md) | The general "never report PASS when the check didn't happen" mandate for all cron scripts |
