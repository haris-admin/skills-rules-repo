# Postmark / pydantic-settings test traps + stale full-suite results (Aug 2026)

## Trap 1: `monkeypatch.setenv` is TOO LATE for pydantic-backed settings

When production code adds a guard like `if not is_postmark_configured(): return`
before the HTTP call, every test that mocks the downstream client breaks: the
service short-circuits before the mock is ever invoked ("Postmark send skipped
(unconfigured token)" + `Expected 'post' to have been called once. Called 0
times.`).

**Naive fix that FAILS:** an autouse fixture doing `monkeypatch.setenv(...)`.
`app.core.config.settings` is a pydantic `Settings` instance loaded/cached at
**module import time** — by fixture time the env var is already baked in, so
`setenv` has zero effect. Verified 2026-08-18: 9 failures persisted with
`setenv`; the exact same tests went 32/32 pass only after switching to the
object patch.

**Correct fix — patch the settings OBJECT, not the env:**

```python
@pytest.fixture(autouse=True)
def _patch_postmark_token(monkeypatch):
    """Bypass is_postmark_configured() guard — tests mock httpx anyway."""
    from app.services import postmark_service
    monkeypatch.setattr(
        postmark_service.settings, "POSTMARK_API_TOKEN", "test-token-bypass-guard"
    )
```

Key detail: `postmark_service` imports `settings` from `app.core.config`, so
patch `postmark_service.settings` (the object the service reads), not a
freshly-imported config copy. Applies to Postmark, Stripe, SMTP, or any
external service where tests mock the HTTP layer and production adds a
token/credentials check before the call.

## Trap 2: full-suite results can be STALE — check the run start time vs your fix time

A full backend suite takes ~18 min. If you apply a fix while a suite is already
running, the completed report shows the OLD failures: pytest collected the test
files at startup, before your edit landed. 2026-08-18: suite started 15:54,
fixture fix applied 15:58 → run finished "9 failed" even though the fix was
verified 32/32 in isolation minutes earlier. The 9 failures were the pre-fix
state, not a regression.

**Rule:** before treating a full-suite failure as real, compare the suite's
start time (`ls -lt ~/.hermes/cron/output/<job_id>/` or the process start) with
the mtime of the files you changed. If the suite started BEFORE the fix,
re-run — don't diagnose the stale output. When in doubt, `git diff` the changed
test files against HEAD to confirm the fix is actually on disk in the run's
checkout (a cron mirror `reset --hard` may have wiped it).

## Related

- `wsl-cron-test-runner` SKILL.md → "Production guard breaks existing mocks"
  pitfall (the object-patch pattern, plus the setenv warning).
- 03:00 mirror `reset --hard origin/dev` wipes uncommitted local test fixes —
  verified fixes must be committed + pushed to survive (see mirror semantics).
