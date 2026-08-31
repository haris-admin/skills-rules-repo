# Mercury — sibling Windows Hermes agent (webhook relay bridge)

A second Hermes Agent instance installed on Windows (via Hermes Desktop MSI)
can connect to Pluto with **zero shared state** through a webhook subscription.
This makes them connected siblings: Mercury hands tasks/context from Windows,
Pluto relays results to the user's Telegram.

## Architecture

```
Mercury (Hermes Desktop, Windows)            Pluto (Hermes, WSL)
       │  POST /webhooks/mercury-relay             │
       │  {"message": "..."} + HMAC signature      │  gateway/webhook.py
       ▼                                           ▼
http://localhost:8644/webhooks/mercury-relay → agent run → deliver: telegram DM 5273126730
```

- Receiver side (Pluto): webhook platform enabled on port 8644 with a global
  HMAC secret in `~/.hermes/config.yaml` (`platforms.webhook.extra.secret`).
- Subscription: `hermes webhook subscribe mercury-relay --prompt "Message from
  Mercury (your sibling agent on Windows): {payload.message}" --deliver telegram
  --deliver-chat-id "5273126730"` — or `--deliver-only` for verbatim relay
  with no agent loop.
- Sender side (Mercury/Windows): needs the webhook URL + the same HMAC secret.
  From Windows, `wsl -d Ubuntu -- <cmd>` reaches Pluto's WSL shell; direct
  HTTP POST to localhost:8644 works because WSL2 ports are forwarded by
  default (mirrored/host networking), so Mercury on the same host can POST.

## Manual test (verified Aug 2026)

```python
import hmac, hashlib, json, urllib.request
secret = "<webhook secret from config.yaml>"
payload = json.dumps({"message": "test"}).encode()
sig = hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()
req = urllib.request.Request(
    "http://localhost:8644/webhooks/mercury-relay",
    data=payload,
    headers={"Content-Type": "application/json", "X-Webhook-Signature": sig},
    method="POST")
# expect HTTP 202 {"status":"accepted","route":"mercury-relay","delivery_id":"..."}
```

## Pitfalls

- **Signature scheme matters** — a bare `curl -X POST ... -d '{"message":"x"}'`
  returns 401 `{"error":"Invalid signature"}`. Generic V1 header is
  `X-Webhook-Signature: <hex HMAC-SHA256 of raw body>`. V2 (recommended) is
  `X-Webhook-Signature-V2` of `"<unix_ts>.<body>"` + `X-Webhook-Timestamp`
  (must be within ±300s). GitHub `X-Hub-Signature-256`, GitLab
  `X-Gitlab-Token`, Linear `linear-signature` also accepted — see
  `gateway/platforms/webhook.py::_validate_signature`.
- **Gateway restart cannot be issued from inside the gateway process** —
  the security guard blocks `systemctl --user restart hermes-gateway` /
  `hermes gateway restart` from a session living inside the gateway (SIGTERM
  would kill the issuing command; even `systemd-run --on-active` naming the
  gateway is blocked). Working paths: user runs it in a separate terminal,
  or the Windows sibling runs `wsl -d Ubuntu -- systemctl --user restart
  hermes-gateway` (outside the WSL gateway process).
- **Don't run two gateways on the same Telegram bot token** — WSL gateway is
  primary (owns cron + fleet wiring); the Windows instance is CLI/desktop +
  a separate profile.
- After a gateway restart, Telegram reconnects automatically in ~5s; verify
  with `hermes gateway status`.
