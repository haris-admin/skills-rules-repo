# Cron suite "script timed out" + dep-sync version-bump trap (Aug 2026)

## Symptom

`★ AMLHive Daily Test Suite (03:00 AM)` cron alert:
`⚠️ Cron ... failed: script timed out. No model was invoked.`
The cron output `.md` contains only:
`Script timed out after 3600s: .../amlhive_daily_test_runner.py`
(8 lines, NO stdout — the wrapper killed the whole process).

Runs on Aug 20-21 completed in ~46-47 min; Aug 22-23 hit the cap. The suite
itself was fine — the wrapper was the killer.

## Root cause 1 — cron wrapper cap vs runner budget

`config.yaml` has `cron.script_timeout_seconds: 3600` (default 1h) — the
HARD cap for `no_agent` script jobs. The runner's OWN internal timeouts sum
to ~9600s (backend 5400 + vitest 600 + playwright 3600), so the wrapper can
kill a healthy long run. This is the "script timed out" alert.

**Fix:** `hermes config set cron.script_timeout_seconds 7200` (config.yaml is
write-protected from the agent — direct `patch` is refused; use the CLI, then
verify with `grep script_timeout_seconds ~/.hermes/config.yaml`).

Rule: the runner's total budget must stay BELOW the wrapper cap, or the run
dies with zero output. After raising the cap, keep the runner phases as-is but
watch total wall-time.

## Root cause 2 — dep-sync over-firing on every release bump

The Aug 18 dep-sync hashed `pyproject.toml` + `poetry.lock` (backend) and
`package.json` + `package-lock.json` (frontend) RAW. But `pyproject.toml` /
`package.json` / `package-lock.json` all carry the ROOT `version` field, which
changes on EVERY release (v0.5.100 → 101 → 102 landed over 3 days in Aug
2026). Result: `pip install -e .` + `npm ci` re-ran almost daily, adding
10+ min → pushed the suite past the 3600s cap.

**Fix (baked into `amlhive_daily_test_runner.py`):** strip ONLY the root
version field before hashing; real dependency changes (new package entries,
lockfile dep versions) still change the hash:

```python
def _dep_hash(paths):
    import hashlib, json
    def _root_stripped_bytes(p):
        raw = p.read_bytes()
        if p.name == "pyproject.toml":
            import re
            return re.sub(rb'(?m)^version\s*=\s*"[^"]*"\s*$', b'version = ""', raw)
        if p.name.endswith(".json"):
            try:
                data = json.loads(raw)
                if isinstance(data, dict):
                    data.pop("version", None)
                    pkgs = data.get("packages")
                    if isinstance(pkgs, dict) and "" in pkgs and isinstance(pkgs[""], dict):
                        pkgs[""].pop("version", None)
                    return json.dumps(data, sort_keys=True).encode()
            except Exception:
                pass
        return raw
    h = hashlib.sha256()
    for p in paths:
        if p.exists():
            h.update(_root_stripped_bytes(p))
    return h.hexdigest()
```

**Verification gotcha:** when testing the strip against historical commits,
the temp file MUST keep the original filename — `p.name == "pyproject.toml"`
only fires if the file is actually named that. A tempfile named
`backend_pyproject.toml` silently bypasses the TOML branch and makes the hash
look version-unstable. Verified: v0.5.100/101/102 all hash to
`6e990ff86cb8ca66` (backend) and `f3bffd037eac3903` (frontend) with the strip.

**Markers:** `~/.hermes/state/amlhive_backend_deps.sha` +
`amlhive_frontend_deps.sha`. After changing the hash function, RE-WRITE the
markers or the next run reinstalls once (harmless but slow). Helper:
`~/.hermes/scripts/write_dep_markers.py`.

## Related

- SKILL.md "CRITICAL: Dependency sync after mirror" — the raw-hash example there
  is the OLD version; use the version-stripped hash above.
- references/postmark-pydantic-settings-trap.md — stale full-suite results
  (suite started before a fix landed = old failures in the report).
