# Python Debugging: pdb + debugpy

Three tools, picked by situation:

| Tool | When |
|---|---|
| **`breakpoint()` + pdb** | Local, interactive, simplest. Add `breakpoint()` in the source, run normally, get a REPL at that line. |
| **`python -m pdb`** | Launch an existing script under pdb with no source edits. Useful for quick poking. |
| **`debugpy`** | Remote / headless / "attach to already-running process." Talks DAP, scriptable from terminal, works for long-lived processes (gateway, daemon, PTY children). |

**Start with `breakpoint()`.** It's the cheapest thing that works.

## pdb Quick Reference

Inside any pdb prompt (`(Pdb)`):

| Command | Action |
|---|---|
| `h` / `h cmd` | help |
| `n` | next line (step over) |
| `s` | step into |
| `r` | return from current function |
| `c` | continue |
| `unt N` | continue until line N |
| `j N` | jump to line N (same function only) |
| `l` / `ll` | list source around current line / full function |
| `w` | where (stack trace) |
| `u` / `d` | move up / down in the stack |
| `a` | print args of the current function |
| `p expr` / `pp expr` | print / pretty-print expression |
| `display expr` | auto-print expr on every stop |
| `b file:line` | set breakpoint |
| `b func` | break on function entry |
| `b file:line, cond` | conditional breakpoint |
| `cl N` | clear breakpoint N |
| `tbreak file:line` | one-shot breakpoint |
| `!stmt` | execute arbitrary Python (assignments included) |
| `interact` | drop into full Python REPL in current scope (Ctrl+D to exit) |
| `q` | quit |

## Debugging Hermes Processes

### Tests under pytest
Always add `-p no:xdist` (pdb doesn't work under xdist). Run:
```
scripts/run_tests.sh tests/path/to/test_file.py::test_name --pdb -p no:xdist
```

### tui_gateway subprocess / _SlashWorker
Use `remote-pdb` for the cleanest agent-friendly debugging:
```
pip install remote-pdb
```
In your code:
```python
from remote_pdb import set_trace
set_trace(host="127.0.0.1", port=4444)
```
Then from terminal: `nc 127.0.0.1 4444` for a (Pdb) prompt.

### Remote debug with debugpy
```
python -m debugpy --listen 127.0.0.1:5678 --wait-for-client your_script.py
```
Attach from VS Code via a launch.json `"request": "attach"` config.

## Recipe: Post-mortem on any exception
```python
import pdb, sys
try:
    run_the_thing()
except Exception:
    pdb.post_mortem(sys.exc_info()[2])
```

## Common Pitfalls
1. pdb under pytest-xdist silently does nothing -- use `-p no:xdist` or `-n 0`.
2. `breakpoint()` in CI/TTY contexts hangs -- never commit it.
3. `PYTHONBREAKPOINT=0` disables all `breakpoint()` calls.
4. `scripts/run_tests.sh` strips credentials -- bugs depending on config won't reproduce.
5. Threads: pdb only debugs the current thread. Use debugpy for multithreaded scenarios.
