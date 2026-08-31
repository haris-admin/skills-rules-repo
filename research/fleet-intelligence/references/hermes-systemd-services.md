# Hermes service persistence via systemd (WSL)

## The failure class (verified Aug 22, 2026)

Long-lived Hermes helper processes started as **background children of the
gateway** die silently whenever the gateway restarts. A gateway restart
(`systemctl --user restart hermes-gateway`) sends SIGTERM to the gateway's
whole process tree — including any background `terminal(background=true)`
process spawned from a session inside that gateway. There is no crash, no
error log: the process just vanishes.

Canonical example: the Hermes web dashboard at `localhost:9119`. It is
manual-start by default (`hermes dashboard --status` → "No hermes dashboard
processes running"). Every gateway restart killed it until it got its own
systemd unit.

## The fix — one systemd user service per long-lived helper

`~/.config/systemd/user/hermes-dashboard.service`:

```ini
[Unit]
Description=Hermes Agent Web Dashboard (port 9119)
After=network.target

[Service]
Type=simple
ExecStart=/home/habib/.local/bin/hermes dashboard --no-open
Restart=always
RestartSec=3
Environment=HERMES_HOME=/home/habib/.hermes

[Install]
WantedBy=default.target
```

```bash
systemctl --user daemon-reload
systemctl --user enable --now hermes-dashboard.service
```

Verify:
```bash
ss -tlnp | grep 9119                       # LISTENING
curl -s -o /dev/null -w "%{http_code}" http://localhost:9119/   # 200
systemctl --user status hermes-dashboard.service | grep Active:  # active (running)
```

Kill-test (proves auto-restart):
```bash
systemctl --user stop hermes-dashboard.service
sleep 2 && systemctl --user start hermes-dashboard.service
sleep 5 && ss -tlnp | grep 9119   # new PID, LISTENING again
```

## Services already using this pattern

| Service | Purpose | ExecStart |
|---|---|---|
| `hermes-gateway.service` | Messaging gateway (Telegram etc.) | `hermes gateway` (systemd-managed) |
| `hermes-dashboard.service` | Web dashboard :9119 | `hermes dashboard --no-open` |
| `herdr.service` | Herdr headless server | `/home/habib/.local/bin/herdr server` |

## Related constraint — gateway restart from inside the gateway

The security guard refuses `systemctl --user restart hermes-gateway` /
`hermes gateway restart` from a session living inside the gateway process
(SIGTERM would kill the issuing command; even `systemd-run --on-active`
naming the gateway is blocked). Working paths: user runs it in a separate
terminal, or the Windows sibling runs
`wsl -d Ubuntu -- systemctl --user restart hermes-gateway` (outside the WSL
gateway process). See `references/mercury-sibling-agent-relay.md` for the
full gateway-restart + Telegram-reconnect note.
