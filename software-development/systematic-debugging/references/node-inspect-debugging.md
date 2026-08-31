# Node.js Inspect Debugger

When `console.log` isn't enough, drive Node's built-in V8 inspector from the terminal. Two tools:

- **`node inspect`** -- built-in, zero install, CLI REPL. Best for quick poking.
- **CDP via `chrome-remote-interface`** -- scriptable; best for automation.

**Prefer `node inspect` first.**

## `node inspect` REPL Quick Reference

Launch paused on first line:
```
node inspect path/to/script.js
node --inspect-brk $(which tsx) path/to/script.ts   # TypeScript via tsx
```

| Command | Action |
|---|---|
| `c` / `cont` | continue |
| `n` / `next` | step over |
| `s` / `step` | step into |
| `o` / `out` | step out |
| `pause` | pause running code |
| `sb('file.js', 42)` | set breakpoint at file.js line 42 |
| `sb(42)` | set breakpoint at line 42 of current file |
| `sb('functionName')` | break when function is called |
| `cb('file.js', 42)` | clear breakpoint |
| `breakpoints` | list all breakpoints |
| `bt` | backtrace (call stack) |
| `list(5)` | show 5 lines of source around current position |
| `repl` | drop into REPL in current scope (Ctrl+C to exit) |
| `exec expr` | evaluate expression once |
| `restart` | restart script |
| `kill` | kill the script |
| `.exit` | quit debugger |

## Attaching to a Running Process

```
kill -SIGUSR1 <pid>
node inspect -p <pid>
# or by WebSocket URL
node inspect ws://127.0.0.1:9229/<uuid>
```

## Debugging Hermes ui-tui

```
hermes --tui &
TUI_PID=$(pgrep -f 'ui-tui/dist/entry' | head -1)
kill -SIGUSR1 "$TUI_PID"
curl -s http://127.0.0.1:9229/json/list | jq -r '.[0].webSocketDebuggerUrl'
node inspect ws://127.0.0.1:9229/<uuid>
```

## Common Pitfalls

1. **Wrong line numbers in TS source.** Breakpoints hit emitted JS, not `.ts`. Use `node --enable-source-maps` with CDP.
2. **`--inspect` vs `--inspect-brk`.** `--inspect-brk` pauses on first line so you can set breakpoints before code runs.
3. **Port collisions.** Default 9229. Multiple Node processes = pass `--inspect=0` for random port.
4. **Child processes.** `--inspect` on parent does NOT inspect children. Use `NODE_OPTIONS='--inspect-brk'` to propagate.
5. **Background kills.** If you Ctrl+C out of `node inspect` while target is paused, the target stays paused.
6. **`node inspect` through agent terminal.** Use terminal(pty=true) or background=true for interactive stepping.
7. **Security.** Always bind to 127.0.0.1 (default) -- `--inspect=0.0.0.0` exposes arbitrary code execution.
