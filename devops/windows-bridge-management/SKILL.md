---
name: windows-bridge-management
description: Manage the OpenClaw Research Bridge (Express/Node.js service on Windows port 18796) — find PID, kill/restart, edit endpoints, fix script paths, test via curl. Use when the bridge is down, needs updates, or monitoring jobs fail.
allowed-tools: [terminal, read_file, write_file, patch]
---

# Windows Bridge Management

## When to Use

- Bridge at `http://localhost:18796` is not responding
- Adding new endpoints or fixing broken ones in `research_bridge.js`
- Restarting the Node.js process after editing the source
- Debugging why TapEase monitoring jobs fail (bridge dependency)
- Investigating "broken pipe" or "connection refused" errors on bridge-dependent crons

## Bridge Overview

**Source:** `C:\Code\gitlab\n8n-habibi-integration\bridge\research_bridge.js`
**Port:** 18796
**Service:** OpenClaw Research Bridge (Express/Node.js)
**Host:** Windows (native, NOT WSL — runs as a Windows Node.js process)
**PID:** Variable (find via netstat)
**Startup:** Manual (no Windows service — started from cmd.exe or Node.js)

### Endpoints (June 14, 2026 — v2)

| Endpoint | Method | Purpose |
|---|---|---|
| `/health` | GET | Health check |
| `/research` | POST | Fire-and-forget research via Perplexity/Comet |
| `/perplexity-session` | GET | Check Perplexity Pro login status |
| `/cloudwatch-monitor` | POST | Lambda CloudWatch monitor (async) |
| `/ec2-backend-monitor` | POST | EC2/S3 monitor (async) |
| `/tapease/monitor` | POST | **SYNC** — Runs Lambda + EC2 monitors, returns combined report |
| `/pluto/deliver` | POST | Cross-agent message relay (Pluto↔Gumby) |
| `/pluto/messages` | GET | Retrieve relayed messages |
| `/pluto/fleet` | GET | Fleet overview with endpoint list |
| `/execute` | POST | Run arbitrary Windows/PowerShell commands |

## Finding the Bridge

The bridge runs as a Windows Node.js process. It does NOT show up in WSL's `ss -tlnp` because `ss` only shows WSL-side sockets. Use these instead:

```bash
# From WSL — find the Windows PID
cmd.exe /c "netstat -ano | findstr 18796"

# Expected output:
#   TCP    0.0.0.0:18796          0.0.0.0:0              LISTENING       10996
#   TCP    [::]:18796             [::]:0                 LISTENING       10996
```

The PID is the last column (e.g., `10996`).

```bash
# Verify it responds
curl -s http://localhost:18796/health
# → {"status":"ok","service":"OpenClaw Research Bridge"}
```

## Killing and Restarting

```bash
# Kill old process
cmd.exe /c "taskkill /PID <PID> /F"

# Wait for port to free up
sleep 2

# Start new bridge
cmd.exe /c "start /B node C:\Code\gitlab\n8n-habibi-integration\bridge\research_bridge.js"

# Wait for it to bind
sleep 2

# Verify
curl -s http://localhost:18796/health
```

## Editing Endpoints

The bridge source is on the Windows filesystem, readable/writable from WSL:

```bash
# Read the full source
cat /mnt/c/Code/gitlab/n8n-habibi-integration/bridge/research_bridge.js

# Edit with write_file or patch
patch(path="/mnt/c/Code/gitlab/n8n-habibi-integration/bridge/research_bridge.js", ...)
```

**After editing, ALWAYS restart the process** — Node.js doesn't auto-reload.

## Pitfalls

### 🔴 Bridge Can Run Stale Code (Most Common TapEase Failure — Fixed Jun 26, 2026)

**Symptom:** `curl http://localhost:18796/health` returns `200 OK` but `POST /tapease/monitor` (or any newer endpoint) returns `404 Cannot POST /tapease/monitor`. All TapEase cron jobs show `last_status: error`.

**Root cause:** The `research_bridge.js` source file was updated on disk, but the running **Windows Node.js process was never restarted** — it's still running the old code that doesn't have the newer routes registered.

**Fix:**
```bash
# 1. Find current PID
cmd.exe /c "netstat -ano | findstr 18796"
# → TCP 0.0.0.0:18796 LISTENING 123832

# 2. Kill it (bridge auto-restarts via Windows process management)
cmd.exe /c "taskkill /PID 123832 /F"

# 3. Wait for new process to bind
sleep 2

# 4. Verify new PID is listening AND new endpoints work
cmd.exe /c "netstat -ano | findstr 18796"   # New PID should appear
curl -s -X POST http://localhost:18796/tapease/monitor -H "Content-Type: application/json" -d '{"lookback_hours": 6}' | head -3
# → {"status":"ok","timestamp":"...","lambda":{...},"ec2":{...}}
```

**Prevention:** After ANY edit to `research_bridge.js`, immediately kill and restart the bridge. Node.js does not auto-reload.

**Diagnostic chain:** If ALL TapEase cron jobs (5AM, 11AM, 5PM, 11PM) show `last_status: error`, 90% of the time it's this stale bridge issue — not a problem with the PowerShell scripts or AWS API. Check `/health` first, then `/tapease/monitor` directly.

### 🔴 Script Paths Are at `scripts/system/`, Not Workspace Root

The original bridge (`research_bridge.js`) had hardcoded paths pointing to the workspace root:

```javascript
// WRONG (old):
const cmd = `powershell ... -File ${path.join(WORKSPACE, 'cloudwatch_monitor_unified.ps1')}`
// This file doesn't exist at the workspace root

// RIGHT (fixed):
const cmd = `powershell ... -File "${path.join(WORKSPACE, 'scripts', 'system', 'lambda_monitor_unified.ps1')}"`
```

**When adding new endpoints or fixing broken ones, verify the script paths.** The actual PowerShell scripts live at:
- `C:\Users\habib\.openclaw\workspace\scripts\system\lambda_monitor_unified.ps1`
- `C:\Users\habib\.openclaw\workspace\scripts\system\ec2_backend_monitor_unified.ps1`

Not at the workspace root. The `enhanced_bridge.js` at the same directory (stale, not the active one) had correct paths — use it as reference for proper path structure.

### 🔴 Bridge Is Invisible to WSL Process Tools

```bash
# This will NOT find the bridge:
ss -tlnp | grep 18796  # ❌ Returns nothing

# Use this instead:
cmd.exe /c "netstat -ano | findstr 18796"  # ✅
```

The bridge is a Windows-native Node.js process. WSL tools cannot see its command line or process details. Only `netstat` from `cmd.exe` reveals the PID.

### 🔴 Bridge /tapease/monitor Returns HTML Instead of JSON

**Symptom:** `curl -X POST http://localhost:18796/tapease/monitor` returns an HTML
error page (or times out after 30+ seconds) while `/health` returns `200 OK`.
All 4 TapEase cron jobs fail with `JSONDecodeError`.

**Root cause:** The Express route handler for `/tapease/monitor` on the Windows
side is throwing an unhandled error (broken PowerShell script path, missing
dependency, or uncaught exception in the route).

**Fix:** Restart the bridge process (see "Killing and Restarting" above). If that
doesn't work, debug the Express route registration in `research_bridge.js`.

**When the bridge won't cooperate, go direct to AWS.** See
`references/direct-aws-debugging.md` for the full AWS CLI + SSM fallback procedure —
it bypasses the bridge entirely and talks to CloudWatch, EC2, SES, and SSM directly.

### 🔴 Sync Endpoint Timeouts & Double-Email Side Effect

The `/tapease/monitor` sync endpoint runs BOTH Lambda and EC2 monitors in parallel via `Promise.all()`. Each PowerShell script can take 30-60 seconds for AWS API calls. The bridge's `execPromise` helper has a 300s (5 min) timeout, which is sufficient. But if calling from a Hermes cron job, ensure the cron's `script_timeout_seconds` is set high enough (900s minimum, per global config).

**Known double-email issue (June 15, 2026):** The `tapease_monitor_runner.py` script that calls this endpoint has its own `send_email()` function which duplicates the email that the PowerShell pipeline (`lambda_monitor_unified.ps1` → `unified_delivery.ps1` → `professional_email_unified.ps1`) already sends. This means every TapEase cron run produces TWO emails to the same recipients — one clean HTML (from PowerShell) and one raw plain-text (from Python). See `pluto-pipeline-orchestration` skill's TapEase section for the full chain and fix recommendation.

### 🔴 PowerShell Unicode Encoding

When modifying PowerShell scripts that contain emoji/Unicode characters (✅, ❌, ⚠️, —), save the file with **UTF-8 BOM** (byte order mark). Without it, PowerShell's parser chokes on the Unicode characters when run through Node.js `child_process.exec()`:

```bash
# Add UTF-8 BOM to a .ps1 file:
python3 -c "
with open('/path/to/script.ps1', 'rb') as f:
    content = f.read()
if content[:3] != b'\\xef\\xbb\\xbf':
    with open('/path/to/script.ps1', 'wb') as f:
        f.write(b'\\xef\\xbb\\xbf' + content)
"
```

This was the root cause of `Unexpected token 'Lambda' in expression or statement` errors on `lambda_monitor_unified.ps1` line 211. The em dash (—) character was getting corrupted. Fixed by adding BOM.

### 🔴 Test Crons Without `deliver: origin`

When manually testing a cron job that has `deliver: origin`, the test run WILL deliver to Telegram. To avoid spamming the user, either:
- Temporarily change deliver to `local` before testing, then change back
- Or test the underlying script directly (not via `cronjob run`)
- Or explain to the user that the test output will appear as a separate message

## Cross-Agent Message Relay

The bridge serves as a lightweight message bus between Pluto (WSL) and Gumby (Windows). Messages are stored in-memory (not persistent — lost on bridge restart).

### Sending a Message

```bash
curl -X POST http://localhost:18796/pluto/deliver \
  -H "Content-Type: application/json" \
  -d '{"from": "pluto", "to": "gumby", "subject": "Research summary ready", "body": "Key findings from today...", "priority": "info"}'
```

Fields: `from`, `to` (pluto/gumby/relay), `subject`, `body`, `priority` (info/low/medium/high/critical).

### Retrieving Messages

```bash
# All messages for a specific target
curl http://localhost:18796/pluto/messages?target=gumby

# Recent messages since a timestamp
curl http://localhost:18796/pluto/messages?since=2026-06-15T00:00:00Z&limit=10
```

### Fleet Status

```bash
curl http://localhost:18796/pluto/fleet
# Returns: uptime, memory, message queue count, all registered endpoints
```

This replaces the file-based handoff mechanism (`gumby-brief-input.md`, `actions_*.json`) for real-time agent-to-agent communication. Use for: urgent signals, cross-agent alerts, brief handoff confirmations.

## Related

- `pluto-pipeline-orchestration` — Contains the TapEase Fleet Monitoring cron schedule that depends on this bridge
- `fleet-intelligence` — Cross-agent fleet context acquisition; references this bridge for cron schedule and job IDs
- Reference: `references/direct-aws-debugging.md` — Direct AWS CLI + SSM debugging of TapEase when the bridge is unresponsive (region scanning, CloudWatch silence detection, SES audit, app code tracing)
- Reference: `references/perplexity-browser-debug.md` — Chrome remote debugging setup for Perplexity Pro integration
- Reference: `references/cross-fleet-monitoring.md` — Full pattern for adding and managing cross-fleet AWS monitors
