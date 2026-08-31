# AMLHive AWS Account Reference

Account: `560205084533`
Region: `ap-southeast-2`
IAM User: `IAM_MONITOR`
Credentials: `AWS_ACCESS_KEY_ID_AMLHIVE` / `AWS_SECRET_ACCESS_KEY_AMLHIVE` in Windows `.env`

## EC2 Instances

| Instance | Type | Private IP | Public IP | State | Launch Time |
|---|---|---|---|---|---|
| amlhive-prod (i-02276d537152046d9) | t3.medium | 172.31.13.73 | 54.79.38.76 | running | 2026-07-12T14:08:07Z |
| amlhive-frontend (i-0cf88f6d601f8d4a9) | t3.small | 172.31.14.73 | 54.253.77.49 | running | 2026-07-12T14:08:07Z |

VPC: `vpc-0ba2ae2b55c6e7e80` | Subnet: `subnet-0532f6ad9b74fef18` | AZ: `ap-southeast-2a`

## Docker Setup

### Backend (amlhive-prod)
- Compose file: `/home/ec2-user/amlhive/docker-compose.prod.yml`
- Service: `app` (port 8000)
- Image: `560205084533.dkr.ecr.ap-southeast-2.amazonaws.com/amlhive-backend:latest`
- Supervisor manages `api` + `worker` processes inside container
- Nginx reverse proxy in front (warn: conflicting server name "_" on 0.0.0.0:80)

### Frontend (amlhive-frontend)
- Container: `amlhive-frontend` (port 3000)
- Image: `560205084533.dkr.ecr.ap-southeast-2.amazonaws.com/amlhive-frontend:latest`
- Next.js 16.2.7

Both instances have a stale `ecs-agent` container (Exited 1) — legacy from ECS, harmless.

## CloudWatch Log Groups

| Log Group | Size | Content |
|---|---|---|
| `/amlhive/backend` | 3.79 MB | Supervisor + app logs (API requests, cron jobs) |
| `/amlhive/backend-system` | 0.38 MB | nginx + bootstrap provisioning |
| `/amlhive/frontend` | 0.01 MB | Next.js startup messages |
| `/amlhive/frontend-system` | 0.50 MB | nginx + bootstrap provisioning |
| `/aws/rds/instance/amlhive-prod/postgresql` | 0.41 MB | PG 16.13 logs |
| `/aws/rds/instance/amlhive-prod/upgrade` | 0.07 MB | RDS upgrade events |

## CloudWatch Alarms

| Alarm | State | Since | Reason |
|---|---|---|---|
| amlhive-backend-status-check-failed | 🔴 ALARM | 2026-07-05T14:14:14Z | "no datapoints received for 2 periods" |
| amlhive-frontend-status-check-failed | 🔴 ALARM | 2026-07-05T14:14:52Z | "no datapoints received for 2 periods" |

**Diagnosis:** Instances launched at 14:08 UTC. Alarms fired at 14:14 UTC (6-minute gap). Current EC2 status checks show OK (System: ok, Instance: ok). These are stale alarms from the bootstrap window — the metric had a gap during provisioning. The "treat missing data as breaching" alarm setting prevents auto-resolution.

**Alarm history:**
- Backend: OK → ALARM at 2026-07-05T14:14:14Z (previous OK at 2026-07-01T04:27:37Z)
- Frontend: OK → ALARM at 2026-07-05T14:14:52Z (previous OK at 2026-07-01T04:27:27Z)

## SSM Agents

Both instances Online, Agent v3.3.4624.0, Amazon Linux 2023.

## Health Metrics (2026-07-05 ~18:50 UTC)

| Instance | Disk | Memory | CWA Status |
|---|---|---|---|
| amlhive-prod | 4.6G/30G (16%) | 832Mi/3.7Gi (22%) | active (running) |
| amlhive-frontend | 3.9G/30G (13%) | 485Mi/1.9Gi (25%) | active (running) |

## Credential Access Pattern

These creds live in the Windows `.env` file, NOT `~/.aws/credentials`. Access pattern:

```python
ENV_FILE = "/mnt/c/Users/habib/.hermes/.env"
creds = {"AWS_DEFAULT_REGION": "ap-southeast-2"}
with open(ENV_FILE) as f:
    for line in f:
        line = line.strip()
        if "AWS_ACCESS_KEY_ID_AMLHIVE" in line and "=" in line:
            creds["AWS_ACCESS_KEY_ID"] = line.split("=", 1)[1]
        elif "AWS_SECRET_ACCESS_KEY_AMLHIVE" in line and "=" in line:
            creds["AWS_SECRET_ACCESS_KEY"] = line.split("=", 1)[1]
```

Do NOT `source` the whole `.env` file — it contains non-exportable tokens.
