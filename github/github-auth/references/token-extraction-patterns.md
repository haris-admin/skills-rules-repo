# Token Extraction Patterns

## Problem

Tokens contain special characters (`$`, `!`, `{`, etc.) that get mangled by shell expansion when embedded in f-strings inside `execute_code()` or `terminal()`.

## Solution: Python-Based Extraction (execute_code)

Use Python's file I/O directly instead of shell pipelines:

```python
from hermes_tools import terminal

# Read token in Python (safe — no shell expansion)
with open("/path/to/.env", "r") as f:
    for line in f:
        if "GITHUB_PAT_CLASSIC_AMLHIVE_AGENT" in line:
            token = line.split("=", 1)[1].strip()
            break

# Write to temp file for shell commands
with open("/tmp/gh_token.txt", "w") as f:
    f.write(token)

# Use in terminal — read from file, never inline
result = terminal("cat /tmp/gh_token.txt | gh auth login --with-token")

# Clean up
import os
os.remove("/tmp/gh_token.txt")
```

## Shell-Based Extraction (terminal only)

For pure shell contexts where `execute_code` isn't needed:

```bash
FULL_TOKEN=$(grep "^GITHUB_PAT_CLASSIC_AMLHIVE_AGENT=" /mnt/c/Users/habib/.hermes/.env | cut -d'=' -f2 | tr -d '\n\r')
```

**Caveats:**
- The `cut -d'=' -f2` approach is safe as long as the token doesn't contain `=` (GitHub PATs don't)
- `tr -d '\n\r'` strips any Windows CRLF artifacts
- Always verify length: `echo "${#FULL_TOKEN}"` — classic PATs are 40 chars
