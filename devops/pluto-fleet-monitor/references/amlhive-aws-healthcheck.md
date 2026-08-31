# AmLHive AWS Health Check Architecture

## Overview

AmLHive AWS infrastructure (account `560205084533`) has two monitoring paths:

1. **Integrated fleet monitor** — `pluto_fleet_monitor.py` includes AWS in its combined report (Fly.io + Sentry + Vercel + AWS). Emailed via `purelymail_sender.py` branded HTML.

2. **Dedicated runner** — `amlhive_aws_runner.py` (TapEase-style, plain text with ━━━ dividers). Emailed via raw smtplib to the 4-recipient list. 4 independent cron jobs.

Both share the `amlhive_aws_health.py` module as the source of truth for AWS data.

## ⚠️ Instance ID Drift — Known Failure Mode

**When an EC2 instance is replaced (manual re-creation, launch template update, ASG replacement), its InstanceId changes.** The `amlhive_prod_monitor.py` script hardcodes instance IDs in constants. If these aren't updated after replacement, SSM commands silently fail (`InvalidInstanceId`) and the Docker/disk/memory sections produce false empty-OK results.

**Pattern to use for survival:** Use `describe-instances` with name-tag filters, as `amlhive_aws_health.py` does for EC2 status checks, instead of hardcoded IDs. The `check_docker()` function in `amlhive_aws_health.py` was the last remaining hardcoded-ID holdout and was fixed on 07 Jul 2026.

**If the monitor reports "No containers found via SSM":**
1. Verify current instance IDs: `aws ec2 describe-instances --filters "Name=tag:Name,Values=amlhive-prod,amlhive-frontend" --query "Reservations[].Instances[].[InstanceId,InstanceType,State.Name]" --output json`
2. Update `BACKEND_INSTANCE_ID` and `FRONTEND_INSTANCE_ID` in `amlhive_prod_monitor.py`
3. Update `instance_names` dict in `amlhive_aws_health.py`'s `check_docker()` function

## Module: `amlhive_aws_health.py`

Path: `~/.hermes/scripts/amlhive_aws_health.py`

### Exported Functions

| Function | Returns | Purpose |
|----------|---------|---------|
| `run_aws_check()` | `{status, account, user, sections: {ec2, cloudwatch, rds, docker}, alerts}` | Runs all checks, returns structured dict |
| `format_aws_report(result)` | markdown string | Formats for fleet monitor integration |

### Check Functions

- `check_ec2(env)` — EC2 status, disk/memory via SSM. **Dynamically discovers instances** via `describe-instances` with name-tag filter (no hardcoded IDs).
- `check_cloudwatch(env)` — CloudWatch alarms + log group sizes
- `check_rds(env)` — RDS instance status
- `check_docker(env)` — Docker containers via SSM. **Historically hardcoded IDs** — update when instances are replaced.

## Credential Loading Pattern

The AWS creds (`AWS_ACCESS_KEY_ID_AMLHIVE`, `AWS_SECRET_ACCESS_KEY_AMLHIVE`) live in the Windows `.env` at `/mnt/c/Users/habib/.hermes/.env`.

**Critical:** Do NOT use `source /mnt/c/Users/habib/.hermes/.env` in bash — the file contains Fly.io deploy tokens with special characters (`fm2_xxx...,fm2_yyy...` base64-like values) that break shell parsing. Always extract specific variables.

### Safe Python approach (used in amlhive_aws_health.py):

```python
creds = {"AWS_DEFAULT_REGION": "ap-southeast-2"}
with open("/mnt/c/Users/habib/.hermes/.env") as f:
    for line in f:
        line = line.strip()
        if "AWS_ACCESS_KEY_ID_AMLHIVE" in line and "=" in line:
            creds["AWS_ACCESS_KEY_ID"] = line.split("=", 1)[1]
        elif "AWS_SECRET_ACCESS_KEY_AMLHIVE" in line and "=" in line:
            creds["AWS_SECRET_ACCESS_KEY"] = line.split("=", 1)[1]
env = os.environ.copy()
env.update(creds)
```

### Safe bash approach (one-liner, for ad-hoc use):

```bash
ENV_FILE="/mnt/c/Users/habib/.hermes/.env"
AWS_AK_ID=$(grep -oP '^AWS_ACCESS_KEY_ID_AMLHIVE=\K.*' "$ENV_FILE")
AWS_SAK=$(grep -oP '^AWS_SECRET_ACCESS_KEY_AMLHIVE=\K.*' "$ENV_FILE")
export AWS_ACCESS_KEY_ID="$AWS_AK_ID"
export AWS_SECRET_ACCESS_KEY="$AWS_SAK"
export AWS_DEFAULT_REGION=ap-southeast-2
```

## SSM Command Pattern

Running commands on EC2 instances via AWS SSM requires a two-step dance:

```python
def ssm_shell(env, instance_id, shell_cmd, wait=6):
    # Step 1: Send the command
    params = json.dumps({"commands": [shell_cmd]})
    cp = subprocess.run(
        ["aws", "ssm", "send-command", "--instance-ids", instance_id,
         "--document-name", "AWS-RunShellScript", "--parameters", params,
         "--output", "json"],
        capture_output=True, text=True, timeout=20, env=env
    )
    cmd_id = json.loads(cp.stdout).get("Command", {}).get("CommandId", "")
    if not cmd_id:
        return ""

    # Step 2: Wait then fetch results
    import time
    time.sleep(wait)
    cp2 = subprocess.run(
        ["aws", "ssm", "list-command-invocations", "--command-id", cmd_id,
         "--details", "--query", "CommandInvocations[0].CommandPlugins[0].Output",
         "--output", "text"],
        capture_output=True, text=True, timeout=15, env=env
    )
    return cp2.stdout.strip() if cp2.returncode == 0 else ""
```

### SSM Pitfalls
- **Timeout:** Always sleep at least 5-6 seconds between send and fetch. Short commands (<1s) return quickly, but the SSM API needs time to execute.
- **Wait time:** For `docker compose logs` or `docker ps` (sub-second), 5s is enough. For `docker compose pull` or package installs, use 15-30s.
- **`--output text` vs `--output json`:** `list-command-invocations` with `--output text` returns raw text output from the shell. Do NOT try to parse it as JSON.
- **`--query` is critical:** Without it, `list-command-invocations` returns a verbose JSON structure. The `[0].CommandPlugins[0].Output` path extracts just the shell output.
- **SSM Agent must be online:** Check via `aws ssm describe-instance-information` before sending commands.
- **`InvalidInstanceId` means the instance was replaced, not a transient error.** Don't retry — go find the new instance ID.

## Dual Runner Architecture

The fleet has TWO parallel 4x-daily email pipelines at 5/11/17/23 AEST:

| Runner | Script | Email Style | Recipients | Cron Jobs |
|--------|--------|-------------|------------|-----------|
| **TapEase** | `tapease_monitor_runner.py` | Plain text ━━━ | 4 addresses (shoaib.habib@a2square, admin@harishabib, hhsiddiqui, habibshoaib841) | `dbd3cb1b5bd3`, `582bd225ddd1`, `1086e6405da1`, `be81c61778a8` |
| **AmLHive AWS** | `amlhive_aws_runner.py` | Plain text ━━━ (same style) | Same 4 addresses | `4f4dc2487b98`, `6728be78d1bf`, `d52fa74ab6c1`, `be5061d19a5a` |
| **Fleet Monitor** | `pluto_fleet_monitor.py` | HTML branded (purelymail_sender) | hhsiddiqui + shoaib@amlhive | `a0b1f0f642af` (single combined) |

The TapEase + AmLHive AWS runners use the **same SMTP pattern** — raw smtplib, plain text only, reading creds from `.openclaw/.env` with `.hermes/.env` fallback. They exit 0 on all-healthy, 1 on issues.

## Infrastructure Reference (Current as of 07 Jul 2026)

| Resource | Identifier | Details |
|----------|------------|---------|
| **AWS Account** | `560205084533` | IAM_MONITOR user via creds `AWS_*_AMLHIVE` |
| **Region** | `ap-southeast-2` | Sydney |
| **Prod EC2 (Backend)** | `i-0abe6a7923fa0dec2` | t3.medium, amlhive-prod, runs FastAPI + ARQ |
| **Frontend EC2** | `i-0ac2e7df9409d50fd` | t3.small, amlhive-frontend, runs Next.js 16.2.7 |
| **RDS** | `amlhive-prod` | postgres 17.9, db.t4g.small, endpoint: `amlhive-prod.ch4ykiy82n3q.ap-southeast-2.rds.amazonaws.com` |
| **ECR** | `560205084533.dkr.ecr.ap-southeast-2.amazonaws.com` | amlhive-backend:latest, amlhive-frontend:latest |
| **Docker** | Raw `docker run` (no compose) | Backend container `amlhive-app-1`, frontend `amlhive-frontend` |
| **Backend log driver** | `awslogs` → `/amlhive/backend` (stream: `app`) | Sends container stdout/stderr directly to CloudWatch |
| **Frontend log driver** | `json-file` (local) | nginx logs sent via CloudWatch agent |
| **CWA** (CloudWatch Agent) | Systemd `amazon-cloudwatch-agent` | Running on both instances. Sends system logs (nginx, system messages) to `/amlhive/{backend,frontend}-system` |

### Container Configuration Notes

- **Backend** uses `awslogs` Docker log driver that pushes directly to CloudWatch `/amlhive/backend` (stream: `app`). Does NOT need CloudWatch agent for app logs.
- **Frontend** uses default `json-file` log driver. nginx access/error logs are forwarded to CloudWatch via the CloudWatch Agent.
- **No docker-compose.yml** on either instance. Containers were started with raw `docker run` commands.
- **Backend CMD:** `supervisord -c /app/supervisord.conf -n`
- **Frontend Sentry DSN** is set via `NEXT_PUBLIC_SENTRY_DSN` env var (project: `javascript-nextjs`, DSN: `https://004932f784dba8b737e7fbcbde51c56c@o4511291833516032.ingest.us.sentry.io/4511291872706560`)
- **Static Next.js export** means no server-side Sentry events. Only client-side JS errors in user browsers trigger events. Server-side issues (proxy failures, nginx) appear in CloudWatch log groups only.

## Stale Alarm Pattern (Jul 2026)

Both `amlhive-backend-status-check-failed` and `amlhive-frontend-status-check-failed` alarms are in ALARM state. These point at **old** instance IDs (`i-0ce168df329f256a4` and `i-053d13d8e19b7ff47` respectively) that were terminated when instances were replaced.

- **Current EC2 status checks:** System=ok, Instance=ok on both instances.
- **Impact:** None — stale alarms pointing at terminated instances.
- **Monitor handling:** Classified as observability drift (P2), not production outage (P0).
- **Fix:** Update alarm dimensions to point at current instance IDs, or remove/recreate alarms.
