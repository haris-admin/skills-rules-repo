---
name: herdr-agent-runtime
description: "Use when driving coding agents headlessly via Herdr."
version: 1.0.0
author: Pluto
license: MIT
metadata:
  hermes:
    tags: [herdr, agent-runtime, codex, claude-code, orchestration, persistent-sessions, telegram]
    related_skills: [coding-agent-delegation, hermes-agent, pluto-amlhive-operating-contract]
---

# Herdr Agent Runtime

Herdr (herdr.dev, GitHub `herdrdev/herdr`) is a **free, Apache-2.0, YC-backed**
"runtime your coding agents live on". A background server owns real PTYs;
agent CLIs (Codex, Claude Code, Hermes, Gemini, opencode, Grok — 19 detected
kinds) run inside panes. Work survives lid-close, network drop, and reboot
(layout resumes). Every UI (TUI, CLI, plain SSH) is just a client of the server.

This is the modern replacement for the raw-tmux pattern in
`coding-agent-delegation` (user-owned; if that skill is unavailable, this one
carries the full workflow): same persistent-terminal idea, but agent-aware
(blocked/working/done states) with a headless CLI + socket API, so Hermes/Pluto
can drive it from Telegram or cron without any TTY.

## When to use

- Long agent runs that must survive disconnect/reboot (Codex strategy reviews,
  big builds, test suites) — the monthly-strategy 1500s Codex run is the
  canonical case.
- Driving agents headlessly from Telegram/cron — user messages Pluto, Pluto
  runs `herdr agent` commands, reports output back.
- Multi-agent orchestration: Codex + Claude Code side by side, each marked
  blocked/working/done.

## Install (WSL/Linux)

```bash
curl -fsSL https://herdr.dev/install.sh -o /tmp/herdr_install.sh && sh /tmp/herdr_install.sh
export PATH="$HOME/.local/bin:$PATH"
herdr --version   # e.g. 0.8.0
```

**Pricing: FREE — no paid tier (verified Aug 2026).** No /pricing page (SPA
fallback: /pricing, /plans, /billing all render the homepage), Apache-2.0,
sponsorship program closed, YC-funded. A future cloud product is teased
("where do agents run while you sleep?") but not released. **Always call it
"free"** — Haris corrected Pluto for implying cost on a free tool; he verifies
pricing claims at source.

## Start the server (the key gotcha)

The `herdr` TUI **panics without a real TTY**:
`failed to initialize terminal: No such device or address` (ratatui init).

**Two working ways to run the server:**

1. **Headless daemon (preferred for persistence) — `herdr server`** (v0.8.0):
   runs the server with NO TUI, no TTY needed. This is the correct ExecStart
   for systemd (see next section). Verify: `herdr status` →
   `server: status: running`; CLI commands work over the socket
   (`/home/habib/.config/herdr/herdr.sock`).
2. **Interactive TUI (needs a TTY):** start once via Hermes background + PTY,
   then use the headless CLI from any other shell:
   ```
   terminal(command="export PATH=$HOME/.local/bin:$PATH && herdr",
            background=true, pty=true)
   ```
   The TUI can keep running or be ignored; the server survives independently.
   A background NON-PTY `herdr` process dies with the owning shell session —
   use the headless `herdr server` or systemd for anything that must persist.

## Reboot persistence — systemd user service (WIRED 16 Aug 2026)

Unit file `~/.config/systemd/user/herdr.service`:

```ini
[Unit]
Description=Herdr agent runtime server
After=network.target

[Service]
Type=simple
Environment=PATH=/home/habib/.local/bin:/usr/local/bin:/usr/bin:/bin
ExecStart=/home/habib/.local/bin/herdr server
Restart=always
RestartSec=3

[Install]
WantedBy=default.target
```

Enable + start:

```bash
systemctl --user daemon-reload
systemctl --user enable herdr.service
systemctl --user start herdr.service
# verify:
systemctl --user status herdr.service   # Active: active (running)
herdr status                            # server: running
```

- **Must be `ExecStart=... herdr server`** — bare `herdr` (TUI) exits 101 under
  systemd (no TTY → ratatui panic) and loops forever on Restart=always.
- Restart resilience is automatic: `herdr server stop` → systemd brings it back
  in ~1s (verified 16 Aug 2026, new PID).
- WSL: systemd IS available on HarisHomeLab01 (`systemctl --user status` works,
  200+ units). User services start at login; no root needed.
- Agents/workspaces are sessions, NOT part of the server — a restart does not
  restore running agent panes. If you see `server: not running`, restart the
  service, then re-create workspace/agent as needed.

## Headless driving loop (what a Telegram "run X" becomes)

1. **Create a workspace** (returns `pane_id`, e.g. `w2:p1`):
   ```bash
   herdr workspace create --label "Pluto Lab" --cwd /home/habib/code/amlhive1
   ```
2. **Start an agent in the pane** (kinds: codex, claude, hermes, gemini,
   opencode, pi, cursor, grok, kimi, copilot, ...):
   ```bash
   herdr agent start codex --kind codex --pane w2:p1
   # -> agent_status: idle, interactive_ready: true
   ```
3. **Answer first-launch trust prompt** (Codex asks "Do you trust the contents
   of this directory?" — Enter accepts):
   ```bash
   herdr agent send-keys codex Enter
   ```
4. **Submit a prompt — POSITIONAL args only**:
   ```bash
   herdr agent prompt codex "Reply with exactly: HERDR_LOOP_OK"
   # NOT --prompt: "herdr agent prompt --prompt ..." fails with "unknown option"
   ```
5. **Read output / check state**:
   ```bash
   herdr agent read codex        # tail of terminal output
   herdr agent get codex         # agent_status: idle|working|done|blocked
   ```
6. **Wait for completion (agent-native, better than polling)**:
   ```bash
   herdr agent wait codex --state done
   ```

## Command surface (v0.8.0)

```
herdr agent list|get|read|prompt|send-keys|wait|start|rename|focus|attach|explain
herdr workspace list|create|get|focus|rename|close
herdr pane list|get|layout|resize|zoom
herdr session list|attach|stop|delete
herdr status [server|client] · herdr api snapshot · herdr server stop|reload-config
```

- `send-keys` keys: `Enter`, `esc`/`escape`, arrows, etc.
- Agent states: `idle`, `working`, `done`, `blocked` — detected semantically,
  not just process-alive.

## Pitfalls

1. **TUI needs a TTY.** Start the server via `background=true, pty=true`;
   never run bare `herdr` in a non-PTY background process (it panics).
2. **`agent prompt` is positional** (`herdr agent prompt <target> <text>`),
   not `--prompt <text>` — the flag form errors with "unknown option".
3. **First-launch trust dialog** (Codex/Claude) blocks the first prompt — send
   `Enter` first, then prompt.
4. **Windows is beta.** Run Herdr on the WSL/Linux side; the Windows binary is
   not production-ready for us.
5. **It doesn't wrap agents** — no model access, no new capabilities. It only
   owns/persists terminals. Use `codex exec` / `claude -p` print mode for
   one-shots; Herdr for long interactive sessions.
6. **Reboot persistence** — WIRED 16 Aug 2026 via systemd user service
   (`~/.config/systemd/user/herdr.service`, `ExecStart=herdr server`, enabled).
   If `herdr status` shows `server: not running`, the service may be stopped —
   `systemctl --user restart herdr.service` and re-create agent panes.
7. **MCP codex tool times out at 300s but the session keeps working (Aug 2026).**
   The `mcp__codex__codex` call returns `TimeoutError: MCP call timed out after
   300.0s` for deep multi-repo analysis — but the Codex session is NOT
   cancelled; it keeps running and writes its output artifact. After a timeout,
   CHECK for the expected output file and a live `codex` process BEFORE treating
   it as failed or re-dispatching. A 15KB report was written after the MCP call
   timed out (16 Aug 2026). For jobs likely to exceed ~5 min, prefer `codex
   exec` via `terminal(background=true, notify_on_complete=true)` — or a Herdr
   pane — over the MCP tool.

## Telegram architecture (Pluto bridge)

```
User (Telegram) -> Pluto (Hermes) -> herdr CLI -> agent panes (Codex/Claude/Hermes)
```

The user talks to Pluto on Telegram; Pluto runs the `herdr agent` commands and
reports output/state back. Sessions persist even if the user's client
disconnects — the whole point of a runtime instead of a foreground terminal.

## Verified smoke test (Aug 2026, v0.8.0, WSL)

- Installed to `~/.local/bin/herdr`
- Server started via PTY background; `herdr status` → running
- Workspace "Pluto Lab" created in `~/code/amlhive1` (w2)
- `herdr agent start codex --kind codex --pane w2:p1` → interactive_ready: true
- `send-keys Enter` (trust) → `prompt codex "Reply with exactly: HERDR_LOOP_OK"`
  → `read` returned `HERDR_LOOP_OK`; state tracked done
- **Persistent setup (16 Aug 2026):** systemd user service enabled + running;
  kill/`server stop` auto-restart verified (~1s). PTY background process died
  with its owning shell session — that's exactly why the systemd service exists.
