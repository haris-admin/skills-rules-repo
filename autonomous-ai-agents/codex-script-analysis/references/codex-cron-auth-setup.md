# Codex Auth for Cron Scripts

Cron jobs don't inherit interactive shell environment. Codex auth needs special handling.

## The Problem

When a `no_agent: true` cron script runs `codex exec`, it fails with:
```
Error: Your refresh token has already been used...
Error: Not logged in
```

This happens because:
1. The cron job's environment doesn't have `CODEX_HOME` set
2. Even with `CODEX_HOME` set, the auth token may have expired
3. ChatGPT auth tokens (OAuth refresh tokens) expire every ~12 days and can't be refreshed headlessly

## Solution: CODEX_HOME + Explicit env

In every script that calls `codex exec`, pass the env:

```python
import subprocess
from pathlib import Path

def run_codex(prompt):
    r = subprocess.run(
        ["codex", "exec", "--skip-git-repo-check", prompt],
        capture_output=True, text=True, timeout=120,
        env={
            **os.environ,
            "CODEX_HOME": str(Path.home() / ".codex"),
        }
    )
    return r.stdout
```

This ensures Codex finds the auth.json regardless of which user/profile runs the cron.

## Re-auth When Token Expires

When `codex exec` returns "401 Unauthorized" or "refresh token reused":

```bash
# From interactive shell (not cron):
codex login --device-auth
# → Visit https://auth.openai.com/codex/device
# → Enter the one-time code
```

The auth file is at `~/.codex/auth.json`. Valid tokens show:
```bash
codex login status  # → "Logged in using ChatGPT"
```

## Token Lifecycle

| Event | Frequency | Action |
|-------|-----------|--------|
| Fresh install | Once | `codex login --device-auth` |
| Token expiry | ~12 days | Re-run `codex login --device-auth` |
| After Hermes/NVM upgrade | One-time | Re-auth (path change may break) |
| Codex version update | Monthly | `npm install -g @openai/codex` (may need re-auth) |

## Diagnostics

Cron script can include a pre-flight check:

```python
import subprocess, os, json
from pathlib import Path

codex_home = str(Path.home() / ".codex")
auth_file = Path(codex_home) / "auth.json"
if not auth_file.exists():
    print("⚠️ Codex auth.json not found — diagnoses will be skipped")

# Quick auth test
r = subprocess.run(
    ["codex", "login", "status"],
    capture_output=True, text=True, timeout=10,
    env={**os.environ, "CODEX_HOME": codex_home}
)
if "Not logged in" in r.stdout:
    print("⚠️ Codex not authenticated — re-run codex login --device-auth")
```
