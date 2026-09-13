# Runner Script Template, Timeouts, Diagnosis, and Common Pitfalls

The full test-runner script skeleton, the default timeout table, the OpenRouter/Codex failure-diagnosis wrappers, the multi-repo runner architecture, and the accumulated list of WSL cron-runner pitfalls. Load this when writing or debugging the actual runner script (as opposed to the WSL/Playwright/git-sync mechanics covered in the other reference files).

## Contents

- [Multi-Repo Runner Architecture](#multi-repo-runner-architecture)
- [Default Timeouts](#default-timeouts)
- [poetry vs venv Fallback](#poetry-vs-venv-fallback)
- [Failure Diagnosis via OpenRouter — 120s Hard Timeout](#failure-diagnosis-via-openrouter--120s-hard-timeout)
- [Legacy: Codex CLI Diagnosis (Deprecated)](#legacy-codex-cli-diagnosis-deprecated)
- [Proper Exception Handling for Test Runners](#proper-exception-handling-for-test-runners)
- [Runner Script Skeleton](#runner-script-skeleton)
- [Common Pitfalls](#common-pitfalls)

## Multi-Repo Runner Architecture

```python
REPOS = [
    {"name": "repo-a", "type": "pytest",    "path": Path("...")},
    {"name": "repo-b", "type": "playwright", "path": Path("..."),
     "playwright_config": "playwright.config.js"},
]

for repo in REPOS:
    update_repo(repo["path"])
    if repo["type"] == "pytest":
        run_pytest(repo)
    elif repo["type"] == "playwright":
        run_playwright(repo)
```

Remember: every `"type": "playwright"` entry needs its own copy of the Chromium-deps guard and `--project=` filter (see [playwright-wsl-setup.md](playwright-wsl-setup.md#multi-device-config--all-browsers-on-wsl)) — one repo having the guard does not protect the others.

## Default Timeouts

| Section | Timeout | Rationale |
|---------|---------|-----------|
| Backend pytest (full suite) | **5400s** (90 min) | Measured at 831-888s on WSL ext4. Suite grows ~40-50 tests per release. Current: 5,223 tests. macOS is 302s — WSL CPU is the bottleneck, not filesystem. Bump generously and re-evaluate monthly. |
| Backend pytest (individual file) | 30-60s | Individual test files complete fast |
| Frontend Vitest | **600s** | Actually completes in ~11s — generous buffer for npm install |
| Playwright E2E | **3600s** (60 min) since Aug 2026; was 1800s/1200s | Full 12-project matrix measured 9-15 min (1463s on 2026-08-09) but grew; generous headroom so a slow NFR/accessibility test can't kill the suite. Per-test timeout is 120000ms. |
| Diagnosis API call | **120s** (hard kill) | 30s was expiring before the OpenRouter→cheap→DeepSeek fallback answered, generating the misleading "provider timeout" alert. 120s gives the chain room while still preventing an indefinite hang. |
| git fetch/reset (mirror sync) | 120s | NTFS + large repos |
| git pull (stash-pull-pop) | 90s | Bumped from 30s (Aug 2026) for NTFS + large repos |

## poetry vs venv Fallback

The script always prefers `poetry run pytest` but falls back to `.venv/bin/pytest` when poetry isn't installed. This is common on fresh WSL setups using `uv` instead of poetry:

```python
try:
    r = run_test(["poetry", "run", "pytest", "tests/", "-q", "--no-header", "--tb=line"],
                 BACKEND, timeout=900)
except FileNotFoundError:
    # poetry not found — fall back to venv
    pytest_bin = BACKEND / ".venv" / "bin" / "pytest"
    if pytest_bin.exists():
        r = run_test([str(pytest_bin), "tests/", "-q", "--no-header", "--tb=line"],
                     BACKEND, timeout=900)
```

If no `.venv` exists either, check for a system-level pytest as a last fallback: `Path(subprocess.run(["which", "pytest"], capture_output=True, text=True).stdout.strip())`.

## Failure Diagnosis via OpenRouter — 120s Hard Timeout

When tests fail, route the raw output to OpenRouter free models for root-cause diagnosis. **CRITICAL: wrap the API call in a hard timeout (120s since Aug 2026) to prevent the diagnosis from hanging and blocking the entire cron job.** The test results (pass/fail) always deliver — only the diagnosis is sacrificed if the API is slow. The original 30s was too tight: it expired before the fallback chain (OpenRouter free → cheap coding → DeepSeek) answered, which is what generated the "provider timeout. Fallback chain was exhausted" alert on 2026-08-09 even though the real failure was a git conflict (see [git-sync-and-credentials.md](git-sync-and-credentials.md)).

```python
from or_free import chat_with_fallback

def codex_diagnose(label, test_output):
    """Route test failure to OpenRouter with 120s hard timeout."""
    try:
        prompt = (
            f"AMLHive {label} test failure. Analyze this output and identify root cause. "
            f"Reply: 1) root cause  2) fix steps  3) which files\n{test_output[:6000]}"
        )
        # 120-second hard timeout via multiprocessing
        import multiprocessing
        q = multiprocessing.Queue()
        def worker():
            try:
                diagnosis = chat_with_fallback(prompt, max_tokens=1024)
                q.put(diagnosis)
            except Exception as e:
                q.put(f"[Diagnosis error: {e}]")
        p = multiprocessing.Process(target=worker)
        p.start()
        p.join(timeout=120)
        if p.is_alive():
            p.terminate()
            diagnosis = "[Diagnosis skipped: timed out after 120s]"
        else:
            diagnosis = q.get_nowait() if not q.empty() else "[Diagnosis: no result]"

        log_path = Path.home() / ".hermes" / "reviews" / "test_diagnoses.log"
        log_path.parent.mkdir(exist_ok=True)
        with open(log_path, "a") as f:
            f.write(f"\n[{datetime.now()}] {label} FAILURE:\n{diagnosis}\n{'─'*60}\n")
        return diagnosis
    except Exception as e:
        return f"[Diagnosis failed: {e}]"
```

Fallback chain: OpenRouter free models → cheap coding models (qwen3-coder, minimax) → DeepSeek API. See the `codex-script-analysis` skill for the full `or_free.py` module documentation. For GitHub Actions workflow-run lookups (a related diagnosis need — finding the last successful run of a specific workflow), use `gh run list --workflow="<display name>"`, never the REST `workflow_id` filter (it silently returns runs from OTHER workflows) — full recipe: [gh-workflow-run-lookup.md](gh-workflow-run-lookup.md). For a real incident where a transient GitHub API 401 was misdiagnosed as a dead PAT, see [2026-08-14-false-green-debug.md](2026-08-14-false-green-debug.md).

## Legacy: Codex CLI Diagnosis (Deprecated)

Previously used `codex exec` for failure diagnosis. Deprecated because Codex CLI auth expires periodically and can't be refreshed from cron. If absolutely needed:

```python
# Requires Codex CLI installed AND authenticated
CODEX_BIN = "/home/habib/.nvm/versions/node/v24.18.0/bin/codex"
subprocess.run(
    [CODEX_BIN, "exec", "--skip-git-repo-check", prompt],
    capture_output=True, text=True, timeout=120,
    env={**os.environ, "CODEX_HOME": str(Path.home() / ".codex")}
)
```

The original (July 2026) version of this pattern — including a fleet-monitor report-generation variant and the device-auth fix for expired Codex tokens — is preserved in full at [codex-diagnosis-routing.md](codex-diagnosis-routing.md).

## Proper Exception Handling for Test Runners

Always wrap test subprocess calls in try/except to prevent a single test suite failure from crashing the entire runner:

```python
try:
    r = subprocess.run([...], capture_output=True, text=True, timeout=300)
    # Parse results...
except subprocess.TimeoutExpired:
    print("   ⚪ Suite timed out (300s)")
except Exception as e:
    print(f"   ⚪ Error: {e}")
else:
    # Process results only if no exception occurred
    pass
```

This ensures a timeout or error in one test suite doesn't prevent subsequent suites from running.

**Common bug:** hardcoded timeout messages — the exception handler prints `"   ⚪ Timed out (300s)"` regardless of the actual timeout passed. If you change `timeout=600`, the message is still wrong. Fix: use an f-string with the actual timeout variable: `print(f"   ⚪ Timed out ({timeout}s)")`.

## Runner Script Skeleton

```python
#!/usr/bin/env python3
"""Test runner template — adapt for each project."""
import subprocess, sys, re, os, time
from pathlib import Path
from datetime import datetime, timezone, timedelta

AEST = timezone(timedelta(hours=10))
NOW = datetime.now(AEST).strftime("%Y-%m-%d %H:%M:%S AEST")

def run_cmd(cmd, cwd, timeout=300, env=None):
    start = time.time()
    r = subprocess.run(cmd, cwd=str(cwd), capture_output=True, text=True, timeout=timeout, env=env)
    return {"output": r.stdout + r.stderr, "duration": round(time.time() - start, 1)}

def parse_results(out):
    p = re.search(r'([\d]+)\s+passed', out)
    f = re.search(r'([\d]+)\s+failed', out)
    s = re.search(r'([\d]+)\s+skipped', out)
    return {"passed": int(p.group(1)) if p else 0, "failed": int(f.group(1)) if f else 0,
            "skipped": int(s.group(1)) if s else 0}

print(f"★ Test Suite — {NOW}")
overall_fail = 0

for repo in REPOS:
    update_repo(repo["path"])
    # ... run tests based on type ...

sys.exit(0 if overall_fail == 0 else 1)
```

Note `run_cmd`/`run_test` must accept an `env=None` kwarg and forward it to `subprocess.run()` — a common `TypeError: run_test() got an unexpected keyword argument 'env'` bug when someone later adds `env=_e2e_env` at a call site without updating the signature.

## Common Pitfalls

- **`test_ready_returns_200_when_db_and_redis_healthy` fails on WSL (503 SSL)** — This test calls `/ready` endpoint which checks the app's `DATABASE_URL`. On WSL, the `.env` config may point to RDS (requires SSL), causing `ESSLREQUIRED` error. Fix options: (a) override `DATABASE_URL=sqlite+aiosqlite:///:memory:` in test env, (b) install local PostgreSQL on WSL, (c) mock `_check_db_ready()` in the test. On macOS, local PostgreSQL or different `.env` avoids this. **Do not ignore** — fix with option (a) or (b).
- **`"\\n".join(lines)` vs `"\n".join(lines)`** — using the two-character escape (literal backslash-n) instead of a real newline in report/email output breaks all cron messages and email formatting. Always use a real newline for line joins. This was the root cause of the July 2026 fleet monitor formatting bug.
- **`--with-deps` hangs in cron** — always use `npx playwright install chromium` without `--with-deps`. System deps are usually already installed.
- **Jest is too slow on WSL** — TypeScript compilation over /mnt/c is ~35s per test file. With 95 test files, full Jest takes 30-60 min. **Use Vitest instead** (`npm run test:unit` which runs `vitest run`). Vitest's native TypeScript support is faster. Jest is kept as `npm run test` runs both (`jest --passWithNoTests && vitest run`) for CI parity, but the cron runner should use `npm run test:unit` directly.
- **Backend tests may not need RDS** — check `conftest.py` first. Many projects (e.g. AMLHive backend) use in-memory SQLite for tests. If SQLite-backed, backend pytest works fine on WSL without Docker or RDS access. Always verify before skipping backend tests. Full pattern and discovery story: [sqlite-inmemory-testing.md](sqlite-inmemory-testing.md).
- **No `.venv` pytest** — check for system-level pytest as fallback: `Path(subprocess.run(["which", "pytest"], capture_output=True, text=True).stdout.strip())`.
- **Git merge conflicts** — always `git stash` before `git pull` in CI runners (working copies with real local edits) or use mirror fetch+reset semantics (a pure test mirror). Previous test runs may leave modified files. See [git-sync-and-credentials.md](git-sync-and-credentials.md) and [mirror-sync-and-false-green-guards.md](mirror-sync-and-false-green-guards.md).
- **Playwright browser install timeout** — first run downloads ~300MB. Allow 2-3 min. Set `timeout=120` in the install subprocess.
- **Playwright webServer config handles server lifecycle** — `npm run test:e2e` uses Playwright's built-in `webServer` option in `playwright.config.ts` to auto-start the Next.js dev server. No separate `uvicorn` or `npm run dev` needed. The server starts on `PORT=3005` and is killed after tests.
- **Vitest replaces Jest for WSL frontend testing** — The AMLHive frontend uses Vitest as its primary unit test runner. `npm run test:unit` runs `vitest run`. Jest is still in `package.json` for CI parity (`npm run test` runs both) but is too slow for WSL cron. Always use `npm run test:unit` for cron runners.
- **`run_tests()` env kwarg** — see the Runner Script Skeleton note above; missing `env=None` in the signature raises a `TypeError` the first time a call site passes `env={...}`.
- **Production guard breaks existing mocks** — When a new production guard is added (e.g. `if not is_postmark_configured(): return`), ALL existing unit tests that mock the downstream HTTP client will fail because the service returns early before the mock is ever invoked. The fix is an `autouse` fixture that bypasses the guard in test:

```python
@pytest.fixture(autouse=True)
def _patch_postmark_token(monkeypatch):
    """Bypass is_postmark_configured() guard — all tests here mock httpx anyway."""
    from app.services import postmark_service
    monkeypatch.setattr(postmark_service.settings, "POSTMARK_API_TOKEN", "test-postmark-token")
```

  **Pattern:** Any new `if not configured: return` guard added mid-pipeline will silently break every test that mocks downstream of that point. The fix is always an `autouse` fixture that sets the guard's prerequisite. Apply this to Postmark, Stripe, SMTP, or any external service where the test mocks the HTTP layer and the production code adds a token/credentials check before the HTTP call. Two more pydantic-settings-specific traps (including why `monkeypatch.setenv` is too late) are documented in [postmark-pydantic-settings-trap.md](postmark-pydantic-settings-trap.md).
- **Docker Desktop inaccessible from WSL** — the Docker CLI binary from Windows is on PATH, but the daemon socket (`/var/run/docker.sock`) doesn't exist in WSL unless Docker Desktop's WSL2 integration is enabled or Docker Engine is installed natively in WSL. Backend test Docker Compose setups won't work without this.
- **Frontend async-latch race in mocked tests** — a shared mocked `Response` object across concurrent test calls can produce a race in code under test (e.g. a "short-circuit concurrent signout calls" latch). See [frontend-shared-response-race.md](frontend-shared-response-race.md) for the specific symptom and fix.
