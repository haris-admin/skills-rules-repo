# AML Hive AWS Credential Loading

## Source of Truth

Credentials live in the Windows `.env` file at:
```
/mnt/c/Users/habib/.hermes/.env
```

The monitor script reads these env vars:
```
AWS_ACCESS_KEY_ID_AMLHIVE=AKIA...   (IAM user: IAM_MONITOR)
AWS_SECRET_ACCESS_KEY_AMLHIVE=hhXY...
AWS_ACCOUNT_ID_AMLHIVE=560205084533
```

## Using via Python

The monitor script's own `load_aws_creds()` function handles reading the file and returning an `os.environ` dict. Import and use it:

```python
import sys
sys.path.insert(0, '/home/habib/.hermes/scripts')
from amlhive_prod_monitor import load_aws_creds, REGION
import subprocess

env = load_aws_creds()
if not env:
    print("NO CREDS — check /mnt/c/Users/habib/.hermes/.env")
    sys.exit(1)

result = subprocess.run(
    ["aws", "ec2", "describe-instances", "--region", REGION, ...],
    env=env, capture_output=True, text=True, timeout=30
)
```

## Using via CLI directly

When the access key is available, set both env vars:
```bash
AWS_ACCESS_KEY_ID=AKIA... AWS_SECRET_ACCESS_KEY=hhXY... \\
  aws ec2 describe-instances --region ap-southeast-2 ...
```

## Important

- These are **read-only** IAM credentials (IAM_MONITOR) — can describe/list but not create/modify resources.
- The IAM user is `IAM_MONITOR` under account `560205084533`.
- The credentials are NOT in `~/.aws/credentials` — they're only sourced from the Windows `.env` file.
