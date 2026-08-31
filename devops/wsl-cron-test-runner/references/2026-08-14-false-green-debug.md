# 2026-08-14 — AMLHive Daily Test Suite: false-green + repo corruption debug

## Symptoms
- Cron output showed `✅ 0 passed, 0 failed` for backend, vitest, Playwright — but tests were NOT actually running.
- `git pull` failed: "Pulling is not possible because you have unmerged files" / "needs merge".
- `backend/pyproject.toml` and `frontend/package.json` contained `<<<<<<<` conflict markers → pytest/npm cannot even parse config → 0 tests collected → parser defaulted to "0 passed" → ✅.

## Root-cause chain (two stacked runner bugs)
1. **Stash-pop corruption (runner bug):** old flow did `git stash push` then `git stash pop` unconditionally. When there were NO tracked changes, `git stash push` silently creates NO stash — but the runner still set `stashed=True` — so `git stash pop` popped `stash@{0}` (an UNRELATED old agent WIP stash) → merge conflicts → the index was re-corrupted EVERY single run.
2. **False-green (runner bug):** `parse_pytest()`/`parse_vitest()` default to `0 passed` when the output contains no count line (config-parse-error path) → broken runs looked green.

## Fixes (now in `amlhive_daily_test_runner.py`)
1. **Mirror semantics:** `git fetch origin` + `git reset --hard origin/dev` — NEVER stash/pop in a runner. The WSL copy is a test mirror; real work lives in the Windows copy + origin. This self-heals any dirty index before testing.
2. **`guard_no_tests(label, r, res)`:** if `res.get("ran")` is falsy (no `N passed`/`N failed` markers in output) → print ❌ + last 6 output lines, return `errors=1` result. Call after EVERY `parse_*`. Non-zero exit with REAL counts is NOT an error-guard case — keep the real counts (the `failed`/`errors` accumulation handles them).
3. `parse_vitest()` must also return `"errors": 0` — the summary reads `res["errors"]` and KeyErrors otherwise (symptom: `⚪ Error: 'errors'` in the Playwright section).
4. Summary icon: `❌ if (res["failed"] > 0 or res["errors"] > 0)` — a section with errors must not show ✅.

## Repo recovery from a corrupted index
- `git reset --hard origin/dev` (HEAD already equal to origin/dev) cleared the conflict markers.
- **Dropped-stash recovery:** `git fsck --unreachable` + `git fsck --lost-found` found dangling commits containing the LOST fix — the runner's old auto-stash from Aug 6 carried an autouse `_patch_postmark_token` fixture for the Postmark tests. git keeps blobs until gc; staged/committed-then-dropped content IS recoverable. `git show <dangling-sha>` to inspect.

## Postmark 9-failure fix (production guard vs mocks)
The service gained `if not is_postmark_configured(): return` (logs "Postmark send skipped (unconfigured token)") which breaks every test that mocks httpx downstream — the mock never gets called, `mock_client.post` is None → `AttributeError: 'NoneType' object has no attribute 'kwargs'`. Fix = autouse fixture in BOTH test files:

```python
@pytest.fixture(autouse=True)
def _patch_postmark_token(monkeypatch):
    """Bypass is_postmark_configured() guard — all tests here mock httpx anyway."""
    from app.services import postmark_service
    monkeypatch.setattr(postmark_service.settings, "POSTMARK_API_TOKEN", "test-postmark-token")
```

Apply to `test_postmark_service.py` AND `test_postmark_billing_templates.py`. Verified: 32 passed.

## Frontend race (api.test.ts, 1 consistent failure)
`signOutInFlight = false` is reset inside `supabase.auth.signOut().then()` → with a mocked (instantly-resolving) signOut, the 2nd concurrent 401 handler sees `false` and calls signOut again → `expected "vi.fn()" to be called 1 times, but got 2 times`. Test is correct; the implementation has a race. Fix direction: keep the flag latched until after the redirect (page reload resets module state anyway), or reset it only after `window.location.replace`.

## Lessons for future debugging
- A "0 passed / 0 failed ✅" cron result is a FALSE GREEN until you verify the command actually collected tests (check exit code + count markers in raw output).
- Before concluding a PAT is dead on a single 401, verify the token LIVE (`curl` or `gh run list` with GH_TOKEN) and check the .env mtime — a transient GitHub API blip with no retry will page you once and never repeat.
