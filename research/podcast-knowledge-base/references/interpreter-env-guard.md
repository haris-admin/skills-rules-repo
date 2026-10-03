### pydantic/ABI-mix failure — LIVE cause and the env guard (2026-10-03)

The gateway exports a `PYTHONPATH` entry pointing at a FOREIGN interpreter's `site-packages`
(`~/.hermes/installs/<install>/environments/<gen>/venv/lib/python3.14/site-packages`). PYTHONPATH is
PREPENDED to `sys.path`, so directory shadows the running venv's packages:

```
ModuleNotFoundError: No module named 'pydantic_core._pydantic_core'
  chromadb  -> ~/.hermes/venv/lib/python3.13/site-packages
  pydantic  -> ~/.hermes/installs/<i>/environments/<gen>/venv/lib/python3.14/site-packages
```

Why the old guard misses it: `find_spec('chromadb')` SUCCEEDS (chromadb is found; its dependency is
what fails), and re-execing alone does not help because PYTHONPATH survives `exec`.

**Env guard — put at the TOP of the caller, immediately BEFORE the feeder/chromadb import.** Never
inside `pluto_mempalace_feeder.py`: a library must not re-exec, or every importer re-execs.

```python
_ver = f"python{sys.version_info.major}.{sys.version_info.minor}"
_pp = os.environ.get("PYTHONPATH")
if _pp and "site-packages" in _pp:
    os.environ["PYTHONPATH"] = os.pathsep.join(
        p for p in _pp.split(os.pathsep) if p and "site-packages" not in p)
sys.path[:] = [p for p in sys.path if not ("site-packages" in p and _ver not in p)]
_vpy = "/home/habib/.hermes/venv/bin/python3"
if os.path.exists(_vpy) and os.path.realpath(sys.executable) != os.path.realpath(_vpy):
    os.execv(_vpy, [_vpy, os.path.abspath(__file__), *sys.argv[1:]])
```

Applied + verified 2026-10-03: `mempalace_watcher.py`, `mempalace_health.py`,
`sc_watch_to_mempalace.py`, `podcast_pipeline_daily.py`, `pluto_chamber_refresh.py`,
`amlhive_daily_test_runner.py`. Verification = re-run each under a deliberately poisoned
`PYTHONPATH`; the pre-change scripts (backup: `~/.hermes/backups/scripts_20261003_140801/`) fail 100%
of the time, the patched ones pass.

Also confirmed the same day: that injected entry reached every `subprocess.run(...)` CHILD (children
inherit `os.environ`), which is how it produced 243 pytest collection errors in the AMLHive backend
suite while the same venv collected 7833 tests clean by hand.

Still guard-less (not cron-wired; safe until they are): `gumby_mempalace_query.py`,
`mempalace_dedup_podcast.py`, `pluto_mempalace_feeder.py`, `rebuild_drawers.py`, `seed_chambers.py`.
Full write-up: `~/.hermes/ops/environment.md` -> "Cron env guard — foreign PYTHONPATH injection".
