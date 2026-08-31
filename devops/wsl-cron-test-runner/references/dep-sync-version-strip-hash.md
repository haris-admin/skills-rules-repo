# SKILL.md dep-sync example is the OLD raw-hash version (Aug 2026)

The `## 🔴 CRITICAL: Dependency sync after mirror` section in this skill's
SKILL.md still shows the FIRST version of `_dep_hash` (raw `read_bytes()`
hash). That version over-fires: `pyproject.toml` / `package.json` /
`package-lock.json` all carry the ROOT `version` field which changes on EVERY
release, so `pip install -e .` + `npm ci` re-ran almost daily, adding 10+ min
and pushing the suite past the cron wrapper cap ("script timed out" alerts on
Aug 22-23 2026).

**Use the version-stripped hash instead** (baked into
`amlhive_daily_test_runner.py`):

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

Key points:
- Strip ONLY the root version field (top-level `version` + `packages[""].version`
  for JSON). Do NOT strip dependency versions — those are real change signals.
- Verification gotcha: temp test files MUST keep the original filename
  (`p.name == "pyproject.toml"` only fires if the file is actually named that).
- After changing the hash function, RE-WRITE the markers under
  `~/.hermes/state/` (amlhive_backend_deps.sha / amlhive_frontend_deps.sha) or
  the next run reinstalls once. Helper: `~/.hermes/scripts/write_dep_markers.py`.
- Verified: v0.5.100/101/102 all hash to `6e990ff86cb8ca66` (backend) and
  `f3bffd037eac3903` (frontend) with the strip; a real dep addition still
  changes the hash.

Full story incl. the cron wrapper cap (`hermes config set
cron.script_timeout_seconds 7200` — config.yaml is write-protected from the
agent, direct patch is refused, use the CLI):
[references/cron-script-timeout-and-dep-sync-trap.md](references/cron-script-timeout-and-dep-sync-trap.md)
