# No-Fake-Pass Guard for Cron Monitor/Sync Scripts

User mandate (Aug 2026, "put a rule to not to do the fake pass"): **a cron
monitor/sync script must NEVER report ✅ PASS when the check didn't actually
happen.** Encode this in every `no_agent` script that posts to an internal API
or runs a probe.

## The bug class

Scripts that treat a "skipped" / "no change" / empty response as success:

- `amlhive_asic_sync.py` treated EVERY `skipped=true` response as a pass.
  The backend returns three semantically different skip reasons:
  - `NO_CHANGE` — source probed, fingerprint unchanged → legit skip, PASS
  - `FILE_NOT_YET_PUBLISHED` — expected timing (data.gov.au lags ~1wk) → PASS
  - `DATASET_SOURCE_UNAVAILABLE` — **sync never happened** (URL unconfigured)
    → must be ❌ ALERT, exit 1
- `amlhive_daily_test_runner.py` treated "0 tests ran" as ✅ PASS because the
  regex defaulted missing counts to 0. A pytest config parse error (conflict
  markers in pyproject.toml) → `0 passed, 0 failed` → green. MUST be an error.

## The rule

1. Classify responses by REASON, never by a single `skipped` boolean.
2. Any outcome meaning "the work did not happen" (unavailable source, unconfigured
   URL, zero tests collected, non-zero exit) flips the overall verdict to ❌/ALERT
   and exits non-zero.
3. Known-intentional exceptions are allowed ONLY when explicitly logged in the
   script (e.g. `asic-registered-schemes` DATASET_SOURCE_UNAVAILABLE is a quiet
   skip by standing order — no bulk source exists). The exception must be
   dataset/component-scoped, never blanket.
4. Parsers must carry a `ran`/count-present flag; missing count markers → error,
   not zero.

## Implementation pattern (test runner)

```python
def guard_no_tests(label, r, res):
    """False-green guard: no test-count markers at all = ERROR, never a pass."""
    if not res.get("ran", False):
        print(f"   ❌ {label} did NOT actually run tests (exit_code={r['exit_code']})")
        res = {"passed": 0, "failed": 0, "skipped": 0, "errors": 1, "ran": False}
        return res, 1
    return res, 0
```

Call it right after every `parse_*`, add the increment to `overall_errors`, and
make the summary icon `❌ if (failed>0 or errors>0)`.

## Implementation pattern (sync script)

```python
if skipped:
    if reason == "DATASET_SOURCE_UNAVAILABLE":
        print(f"   ❌ NOT SYNCED: {reason} — dataset did not update")
        overall_alert = True
    elif reason in ("NO_CHANGE", "FILE_NOT_YET_PUBLISHED"):
        print(f"   ⏭️ Skipped (no change): {reason}")
    else:
        print(f"   ⏭️ Skipped: {reason}")
```

## Cron "provider timeout" mislabel

A no_agent cron alert that says "provider timeout. Fallback chain was exhausted"
does NOT mean the LLM provider failed — it is often the generic wrapper text for
`script exited with code 1`. ALWAYS read the cron output file first:
`ls -t ~/.hermes/cron/output/<job_id>/ | head -1` then cat the latest `.md`.
The real cause is usually a script exit-1 (git conflict, test failure, alert
verdict), not a provider outage.
