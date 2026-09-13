# Mirror Sync, Dependency Sync, and False-Green Guards

The three highest-severity gotchas in this skill: a stale mirror silently running against old code, a stale venv/node_modules silently failing collection, and a runner reporting ✅ when nothing actually ran. All three produce the same failure signature — a cron job that "passes" while testing nothing real. Read this before touching any mirror-sync, dependency-install, or pass/fail-reporting logic in a runner.

## Contents

- [Dependency Sync After Mirror Reset](#dependency-sync-after-mirror-reset)
- [Mirror Semantics: fetch + reset --hard, never stash/pop](#mirror-semantics-fetch--reset---hard-never-stashpop)
- [False-Green Guard: 0 Tests Ran = Error](#false-green-guard-0-tests-ran--error)
- [Related Incident Write-Ups](#related-incident-write-ups)

## Dependency Sync After Mirror Reset

**🔴 CRITICAL (Aug 2026):** A feature merge (e.g. C413 cross-entity v0.5.92) can add a dependency to `backend/pyproject.toml` (`rapidfuzz = "^3.14.5"`). The mirror reset updates source but NEVER reinstalls the venv → pytest fails at **collection** with `ERROR tests/...` + `Interrupted: 54 errors during collection` + `0 passed`. Symptoms look like a test regression but are pure import failures. The frontend has the same class of bug when `package.json`/`package-lock.json` changes (vitest `Cannot find module`).

**Fix (baked into `amlhive_daily_test_runner.py` after the mirror sync):** hash `pyproject.toml` + `poetry.lock` (and `package.json` + `package-lock.json`) into a marker under `~/.hermes/state/`; when the hash changes, run `python -m pip install -e .` (ensurepip first — poetry-managed venvs have no pip) for backend and `npm ci` for frontend. Hash-based, not mtime-based: the git reset touches mtimes every run.

```python
def _dep_hash(paths):
    import hashlib
    h = hashlib.sha256()
    for p in paths:
        if p.exists():
            h.update(p.read_bytes())
    return h.hexdigest()

# _sync_backend_deps(): ensurepip --upgrade → pip install -e . → write marker
# _sync_frontend_deps(): npm ci → write marker
```

Also keep a manual fallback: `source backend/.venv/bin/activate && python -m pip install -e .`

**Known trap in the hash itself**: the raw-`read_bytes()` version above over-fires on files where a formatting-only diff (e.g. ruff reformatting whitespace in `pyproject.toml`) changes the hash without changing any actual dependency — see [dep-sync-version-strip-hash.md](dep-sync-version-strip-hash.md) for the fix (strip to the dependency-relevant lines before hashing).

## Mirror Semantics: fetch + reset --hard, never stash/pop

**🔴 CRITICAL (Aug 2026):** The old stash→pull→pop flow has a **fatal bug**: `git stash push` silently creates NO stash when there are no tracked changes, but the runner sets `stashed=True` anyway → `git stash pop` then pops **stash@{0}** (an UNRELATED old WIP stash) → merge conflicts → the index is re-corrupted **every single run**. This corrupted `backend/pyproject.toml` + `frontend/package.json` with conflict markers, making pytest/npm unable to even parse configs → **0 tests ran but the runner printed ✅** (false green). The WSL copy is a **test mirror**; real work lives in the Windows copy + origin. Use:

```python
print("📡 Syncing to origin/dev (mirror semantics)...", flush=True)
try:
    fetch = subprocess.run(["git", "fetch", "origin"], cwd=str(REPO),
                           capture_output=True, text=True, timeout=120)
    if fetch.returncode != 0:
        print(f"   ❌ git fetch failed: {(fetch.stderr or fetch.stdout)[:200]}")
    else:
        reset = subprocess.run(["git", "reset", "--hard", "origin/dev"], cwd=str(REPO),
                               capture_output=True, text=True, timeout=120)
        if reset.returncode != 0:
            print(f"   ❌ git reset failed: {(reset.stderr or reset.stdout)[:200]}")
        else:
            head = subprocess.run(["git", "log", "--oneline", "-1"], cwd=str(REPO),
                                  capture_output=True, text=True, timeout=5)
            print(f"   ✅ Synced to: {head.stdout.strip()}")
except Exception as e:
    print(f"   ⚠️  Could not sync: {e}")
```

This self-heals any dirty index before testing. Never `git stash pop` in a **mirror** runner — it pops the TOP of the stash stack which may be unrelated WIP. (Note: a *non-mirror* working copy that genuinely carries local edits should use the stash-pull-pop pattern instead — see [git-sync-and-credentials.md](git-sync-and-credentials.md).)

**Predecessor pattern (superseded by the above):** the original, simpler "always pull latest" step baked into the runner before the mirror-semantics fix was a plain `git pull --ff-only origin dev`, logging "Already up to date" or the new HEAD, with a soft warning (not a hard failure) on error:

```python
print("📡 Pulling latest code from origin/dev...", flush=True)
try:
    r = subprocess.run(["git", "pull", "--ff-only", "origin", "dev"],
                       cwd=str(REPO), capture_output=True, text=True, timeout=30)
    if r.returncode == 0:
        out = (r.stdout + r.stderr).strip()
        if "Already up to date" in out:
            print("   ✅ Already up to date")
        else:
            head = subprocess.run(["git", "log", "--oneline", "-1"],
                                  cwd=str(REPO), capture_output=True, text=True, timeout=5)
            print(f"   ✅ Pulled: {head.stdout.strip()}")
    else:
        print(f"   ⚠️  Pull failed: {(r.stderr or r.stdout)[:200]}")
except Exception as e:
    print(f"   ⚠️  Could not pull: {e}")
```

This plain-pull version doesn't self-heal a dirty index the way fetch+reset does — prefer the mirror-semantics pattern above for any new runner.

## False-Green Guard: 0 Tests Ran = Error

**🔴 CRITICAL (Aug 2026):** `parse_pytest`/`parse_vitest` default to `0 passed` when the output contains no count line (e.g. pyproject.toml invalid → pytest exits before collecting). That made broken runs look green. Every parsed run must carry a `ran` flag and a guard must turn "no count markers" into an error:

```python
def guard_no_tests(label, r, res):
    """False-green guard: no test-count markers at all (couldn't start / config error /
    zero collected) = ERROR. If tests ran (counts parsed) but exit non-zero, keep the
    REAL counts — normal failed/errors accumulation handles them."""
    if not res.get("ran", False):
        tail = "\n".join(r["output"].splitlines()[-6:]) if r["output"] else "(no output)"
        print(f"   ❌ {label} did NOT actually run tests (exit_code={r['exit_code']}). Tail:")
        for ln in tail.splitlines():
            print(f"      {ln}")
        res = {"passed": 0, "failed": 0, "skipped": 0, "errors": 1, "ran": False}
        return res, 1
    return res, 0
```

Call it right after every `parse_*`, add the increment to `overall_errors`, and make the summary icon `❌ if (failed>0 or errors>0)`. Also give `parse_vitest` an `"errors": 0` key — the summary reads `res["errors"]` and KeyErrors otherwise (caused "⚪ Error: 'errors'" in the Playwright section).

**A2Square's own instance of this bug (root-caused 01 Sep 2026):** four Mondays of `0/31` were actually 31 pytest COLLECTION errors (build/deps smell — `pytest-timeout` missing etc.) that the runner reported as ✅: it only counted `failed` in the exit code and never counted `errors`, and there was no no-tests guard. Fixed in `a2square_weekly_test_runner.py` (01 Sep): (a) no-tests guard — no `passed/failed/error` markers + non-zero exit → `errors=1`; (b) exit code and OVERALL line now include `errors` (`overall_failures += failed + errors`); (c) diagnosis routes on `errors` too. **Lesson**: a runner that parses `N error` must treat errors as failures in its EXIT code, or a broken environment looks green for weeks. Mirror this guard in ANY multi-repo runner. This mandate is also codified generally (any `no_agent` script, not just test runners) — see [no-fake-pass-guard.md](no-fake-pass-guard.md).

## Related Incident Write-Ups

- [cron-script-timeout-and-dep-sync-trap.md](cron-script-timeout-and-dep-sync-trap.md) — a real "script timed out" cron alert that traced back to this same dep-sync version-bump trap.
- [dep-sync-version-strip-hash.md](dep-sync-version-strip-hash.md) — why the raw-hash `_dep_hash` above over-fires and the stripped-hash fix.
- [no-fake-pass-guard.md](no-fake-pass-guard.md) — the general "never report PASS when the check didn't happen" mandate for all cron monitor/sync scripts.
