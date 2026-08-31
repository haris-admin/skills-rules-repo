# Perplexity Pro Browser Debug Setup

## Goal
Enable the Research Bridge to connect to a Chrome browser with Perplexity Pro logged in, so `POST /research` with `use_perplexity: true` works.

## How It Works

The bridge's `perplexity_bridge_session.py` script uses **Playwright** to connect to Chrome via Chrome DevTools Protocol (CDP) on port 9222. It:
1. Connects to `http://localhost:9222` via `playwright.chromium.connect_over_cdp()`
2. Checks if Perplexity has a Pro badge (`has_pro: true`)
3. If logged in, executes research queries through the browser session
4. Saves session cookies + localStorage to `.perplexity_session.pkl` (72h expiry)

## Setup Steps

### 1. Launch Chrome with Debug Port

The critical requirement: Chrome MUST be launched with `--remote-debugging-port=9222` AND a dedicated user data directory (to avoid conflicting with the user's main Chrome profile):

```powershell
& "C:\Program Files\Google\Chrome\Application\chrome.exe" `
  --remote-debugging-port=9222 `
  --user-data-dir="$env:USERPROFILE\.chrome-debug-profile" `
  --new-window https://www.perplexity.ai
```

**Why `--user-data-dir` is required:** Chrome is single-instance by default. If the user already has Chrome running, a second launch without `--user-data-dir` reuses the existing instance and ignores the `--remote-debugging-port` flag. A separate profile forces a truly independent Chrome process that binds to port 9222.

### 2. Log In to Perplexity Pro

In the new Chrome window:
- Navigate to https://www.perplexity.ai
- Log in with the Pro subscription account
- Verify the Pro badge appears (top-right user menu)

### 3. Verify Bridge Connection

```powershell
curl http://localhost:18796/perplexity-session
```

**Expected result when working:**
```json
{"status":"ok","logged_in":true,"has_pro":true,"url":"https://www.perplexity.ai/..."}
```

**Common failure states:**

| Response | Meaning | Fix |
|---|---|---|
| `{"error":"Could not connect to browser on port 9222."}` | No Chrome listening on 9222 | Launch Chrome with `--remote-debugging-port=9222` |
| `{"status":"not_logged_in","requires_manual_action":true}` | Chrome on 9222 but not logged into Perplexity | Log in manually |
| `{"logged_in":true,"has_pro":false}` | Logged into free account, not Pro | Log in with Pro account |

### 4. Session Persistence

Once logged in, the bridge saves session data to:
- `C:\Users\habib\.openclaw\workspace\.perplexity_session.pkl`
- `C:\Users\habib\.openclaw\workspace\.perplexity_cookies.json`

Session is valid for **72 hours**. After expiry, the user just needs to log in again in the same Chrome window.

## Triggering Research

After Pro is set up:

```bash
curl -X POST http://localhost:18796/research \
  -H "Content-Type: application/json" \
  -d '{"topic": "your research query", "use_perplexity": true}'
```

Response is fire-and-forget (`{"status":"started"}`). Results returned via `callback_url` if provided, otherwise logs to console.

## If the Window Disappears

The Chrome window with `--user-data-dir` runs as a normal visible window. If it gets closed or the user can't find it:
1. Kill any Chrome on 9222: `cmd.exe /c "netstat -ano | findstr 9222"` → `taskkill /PID <PID> /F`
2. Relaunch using the same command as Step 1 (the `--user-data-dir` profile persists)

## Known Issues

- **Perplexity session `has_pro: false` even with Pro subscription:** The session pickle may have saved a pre-Pro login state. Solution: clear session files (`del .perplexity_session.pkl .perplexity_cookies.json`) and log in fresh while Pro is active.
- **Comet app doesn't work reliably:** The Perplexity Comet desktop app cannot be relied on for this flow. Chrome with `--remote-debugging-port` is more predictable.
- **Research is fire-and-forget:** The bridge returns immediately with `{"status":"started"}` and runs research asynchronously. There is no sync equivalent. Use `callback_url` if you need the result back.
