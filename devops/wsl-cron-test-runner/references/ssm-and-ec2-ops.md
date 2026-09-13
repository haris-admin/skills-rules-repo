# SSM Send-Command Pattern and EC2 Credential/Version Lookups

How the test runner and related monitoring scripts reach EC2/RDS from WSL when there's no direct network path (RDS is VPC-bound), plus the per-project credential and instance-ID reference tables.

## Contents

- [Core SSM Pattern](#core-ssm-pattern)
- [Project Credentials \& RDS Passwords](#project-credentials--rds-passwords)
- [Instance ID Variables](#instance-id-variables)
- [EC2 Version-Fetch Pattern](#ec2-version-fetch-pattern)

## Core SSM Pattern

The test runner and related monitoring scripts use AWS SSM send-command to run SQL queries on EC2 instances. This avoids needing a direct network path to the RDS (which may be VPC-bound from WSL).

```python
def ssm_run(env, cmd, instance_id=None):
    """Run a shell command on a remote EC2 via SSM and return stdout."""
    iid = instance_id or DEFAULT_BACKEND_ID
    cmds_j = json.dumps([cmd])
    r = subprocess.run(
        ["aws", "ssm", "send-command", "--instance-ids", iid,
         "--document-name", "AWS-RunShellScript",
         "--parameters", f"commands={cmds_j}",
         "--output", "json", "--region", REGION],
        capture_output=True, text=True, timeout=30, env=env)
    cid = json.loads(r.stdout)["Command"]["CommandId"]
    time.sleep(3)
    for _ in range(30):
        r2 = subprocess.run(
            ["aws", "ssm", "get-command-invocation",
             "--command-id", cid, "--instance-id", iid,
             "--output", "json", "--region", REGION],
            capture_output=True, text=True, timeout=10, env=env)
        d = json.loads(r2.stdout)
        if d.get("Status") in ("Success", "Failed", "TimedOut"):
            if d["Status"] != "Success":
                err = d.get("StandardErrorContent", "").strip()
                if err: raise RuntimeError(f"SSM: {err[:300]}")
            return d.get("StandardOutputContent", "")
        time.sleep(2)
    raise RuntimeError("SSM timed out")
```

## Project Credentials & RDS Passwords

| Project | AWS Creds Function | Secret ID | DB Host | Notes |
|---------|------------------|-----------|---------|-------|
| **AMLHive** | `load_aws_creds()` from `amlhive_prod_monitor` | ✅ **`amlhive/prod/rds-admin` FIRST** (RLS bypass), then `amlhive/prod/rds` | from secret `host` field (NOT hardcoded) | Verified Aug 2026 in account **560205084533** (IAM_MONITOR, ap-southeast-2). **rds-admin is required for cross-agency aggregate queries** — the app user (`amlhive/*` from `amlhive/prod/rds`) is RLS-scoped to ONE agency and returns zeros on counts. **Never hardcode `-U amlhive`** — the secret's `username` is a 16-char admin name; hardcoding produces `FATAL: password authentication failed for user "amlhive"` even with the correct password. `fetch_creds()` should return username/password/host/port/dbname all from the secret. DO NOT use `tapease/rds/credentials-production` for AMLHive — it holds `tapease_admin` creds for the Tapease RDS host. |
| **Tapease** | `make_aws_env()` from `tapease_prod_monitor` | `tapease/rds/credentials-production` | `tapease-postgres-production.c9aso80ocbn0.ap-southeast-2.rds.amazonaws.com` | Both use same secret. Password field: `.get("password") or .get("Password")` |

**Historical note:** the AMLHive secret name changed once (July 2026) — `amlhive/prod/rds` was deleted and the backend `.env` pointed at `tapease/rds/credentials-production` via `RDS_SECRET_NAME` for a period. See [rds-secret-migration.md](rds-secret-migration.md) for what changed and how it was detected; the table above reflects the current (post-migration) state.

## Instance ID Variables

| Pattern | AWS instance ID | Source |
|---------|---------------|--------|
| **AMLHive backend** | auto-discovered via `get_instance_id("amlhive-prod-backend", "i-0b111b75d3c70fcb7")` | Name tag |
| **Tapease backend** | `i-062b8ef5437ea6e2f` | Memory |
| **Tapease frontend** | `i-0aca7e109d0f6e773` | Memory |

## EC2 Version-Fetch Pattern

To get deployed version numbers from EC2 instances (used in Tapease payout email reports):

```python
def fetch_versions(env):
    """Get backend and frontend version from EC2 instances."""
    be_ver, fe_ver = "?", "?"
    try:
        out = ssm_run(env, "grep '^VERSION' /home/ec2-user/app/backend/app/config.py 2>/dev/null || echo '?'")
        m = re.search(r'VERSION\s*=\s*["\']?([\d.]+)', out)
        if m: be_ver = m.group(1)
    except: pass
    try:
        out = ssm_run(env, "grep '\"version\"' /home/ec2-user/app/package.json 2>/dev/null || echo '?'",
                      instance_id="i-0aca7e109d0f6e773")  # frontend EC2
        m = re.search(r'"version":\s*"([\d.]+)', out)
        if m: fe_ver = m.group(1)
    except: pass
    return be_ver, fe_ver
```

**Paths:**
- **Backend version:** `/home/ec2-user/app/backend/app/config.py` contains `VERSION = "X.Y.Z"`
- **Frontend version (Tapease):** `/home/ec2-user/app/package.json` on its own EC2 (`i-0aca7e109d0f6e773`)
