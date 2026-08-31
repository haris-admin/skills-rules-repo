# .env Credential Reading Pattern

## Problem
Hardcoded credentials in scripts:
- Fragile when passwords rotate
- Exposed in diffs and logs
- Different across environments (Windows vs WSL paths)
- Missed during credential rotation

## Solution: Read from .env at Runtime

```python
from pathlib import Path

def load_credential(env_var_name):
    """Load a credential from .hermes/.env across Windows/WSL paths."""
    for p in [
        "/mnt/c/Users/habib/.hermes/.env",       # Windows (WSL mount)
        str(Path.home() / ".hermes" / ".env"),    # Linux/WSL home
        str(Path.home() / ".openclaw" / ".env"),  # OpenClaw fallback
    ]:
        try:
            with open(p) as f:
                for line in f:
                    if env_var_name in line and "=" in line and not line.startswith("#"):
                        return line.split("=", 1)[1].strip()
        except FileNotFoundError:
            continue
    return None
```

## Usage

```python
APP_PASSWORD = load_credential("GOOGLE_GMAIL_APP_PASSWORD_MACARTHUR")
if not APP_PASSWORD:
    raise RuntimeError("Gmail app password not found in .env")
```

## Testing

```bash
python3 -c "
from pathlib import Path
# Test that credential loads
for p in ['/mnt/c/Users/habib/.hermes/.env', str(Path.home() / '.hermes' / '.env')]:
    try:
        with open(p) as f:
            for line in f:
                if 'GOOGLE_GMAIL_APP_PASSWORD_MACARTHUR' in line and '=' in line and not line.startswith('#'):
                    print(f'Found in {p}')
                    pw = line.split('=',1)[1].strip()
                    print(f'Password length: {len(pw)}')
                    break
    except: pass
"
```

## Verification that Credential Works

After loading, test connectivity:
```python
import imaplib
mail = imaplib.IMAP4_SSL("imap.gmail.com", 993)
mail.login("macarthurgarments@gmail.com", APP_PASSWORD)
mail.select("INBOX")
print(f"Connected. {len(mail.search(None, 'ALL')[1][0].split())} emails")
mail.logout()
```

## Benefits vs Hardcoding

| Aspect | Hardcoded | .env dynamic |
|--------|-----------|--------------|
| Rotation | Edit script + redeploy | Edit .env only |
| Diff exposure | Password in git/blame | Never committed |
| Cross-platform | Manual per platform | Auto-detects paths |
| Audit | Hard to find | Single source of truth |
