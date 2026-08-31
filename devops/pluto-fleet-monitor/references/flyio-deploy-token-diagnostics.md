# Fly.io Deploy Token Diagnostics (Jun 2026)

## Token Format

The AML Hive deploy token is stored in `.env` as a single string with two comma-separated parts:

```
FLY_IO_TOKEN=*** FlyV1 fm2_lJPECAAAAAAAE7B6xBAJ...==,fm2_lJPETgG4NF...
```

- **Prefix**: `FlyV1` — indicates a Fly.io deploy token
- **Part 1**: `fm2_lJPECAAAAAAAE...` — primary deploy token
- **Part 2**: `fm2_lJPETgG4NF...` — secondary/scoped portion (separated by comma)

Both parts together form the complete credential. DO NOT split on comma when passing to flyctl.

## How to Copy from Windows to WSL (Verified Jun 24)

The `***` output masking in Hermes terminal output breaks shell-based extraction (grep/sed with the token value). Use Python:

```python
#!/usr/bin/env python3
"""Copy FLY_IO_TOKEN from Windows .env to WSL .env"""
import os

win_env = "/mnt/c/Users/habib/.hermes/.env"
wsl_env = os.path.expanduser("~/.hermes/.env")

with open(win_env) as f:
    content = f.read()

token = None
for line in content.splitlines():
    if "FLY_IO_TOKEN" in line:
        raw_val = line.split("=", 1)[1].strip()
        # Handle any '***' prefix that may be literal in file
        if raw_val.startswith("*** "):
            raw_val = raw_val[4:]
        token = raw_val
        break

if not token:
    print("ERROR: FLY_IO_TOKEN not found")
    exit(1)

# Read existing WSL env, update or add
lines = []
found = False
try:
    with open(wsl_env) as f:
        lines = f.readlines()
except FileNotFoundError:
    pass

with open(wsl_env, "w") as f:
    for l in lines:
        if l.strip().startswith("FLY_IO_TOKEN") or l.strip().startswith("export FLY_IO_TOKEN"):
            f.write(f"FLY_IO_TOKEN={token}\n")
            found = True
        else:
            f.write(l)
    if not found:
        f.write(f"FLY_IO_TOKEN={token}\n")

print("OK")
```

## Verification

```bash
python3 -c "
import os, subprocess
with open(os.path.expanduser('~/.hermes/.env')) as f:
    for line in f:
        if 'FLY_IO_TOKEN' in line:
            raw = line.split('=', 1)[1].strip()
            break
env = {**os.environ, 'FLY_API_TOKEN': raw}
r = subprocess.run(['flyctl', 'apps', 'list'], env=env, capture_output=True, text=True)
print('OK' if r.returncode == 0 else 'FAIL: ' + r.stderr[:200])
"
```

Expected output: lists `amlhive-api` app.

## What the Token Can Access

| Capability | Works? | Command |
|-----------|--------|---------|
| List apps | ✅ | `flyctl apps list` |
| App status | ✅ | `flyctl status -a amlhive-api` |
| Logs (no-tail) | ✅ | `flyctl logs -a amlhive-api -n` |
| Releases | ✅ | `flyctl releases -a amlhive-api` |
| Machine list | ✅ | `flyctl machine list -a amlhive-api` |
| Postgres list | ❌ | `flyctl postgres list` |
| Org metrics | ❌ | Always emits "Metrics token unavailable" |
| auth whoami | ✅ | Identity: `196d910c-3979-56de-a046-d634bd24e81f@tokens.fly.io` |

## Bug History

- **Pre-Jun 24:** Script used `second_token` (part after comma) as `FLY_API_TOKEN` — caused silent auth failure
- **Jun 24:** Fixed to use full raw token. Fleet monitor now shows Fly.io as ✅ Operational
