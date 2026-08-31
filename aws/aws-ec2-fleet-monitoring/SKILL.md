---
name: aws-ec2-fleet-monitoring
description: "Class-level skill for EC2 fleet monitoring that survives instance recycling. Tag-based auto-discovery, SSM execution, and credential management patterns."
version: 1.0.0
author: Pluto
tags: [aws, ec2, ssm, monitoring, fleet, auto-discovery]
---

# AWS EC2 Fleet Monitoring

## Core Problem
EC2 instance IDs change every time instances are recycled. Monitoring scripts that hardcode instance IDs break silently and require manual patching every time.

## Solution: Tag-Based Auto-Discovery
Query EC2 by **Name tag** at runtime instead of hardcoding IDs. Cache the result per script invocation.

```python
import subprocess, json, functools

@functools.lru_cache(maxsize=4)
def get_instance_id(name_tag, hardcoded_fallback=None):
    """Discover running EC2 instance ID by Name tag. Cached per script run."""
    try:
        r = subprocess.run([
            "aws","ec2","describe-instances",
            "--filters",f"Name=tag:Name,Values={name_tag}",
                     "Name=instance-state-name,Values=running",
            "--query","Reservations[*].Instances[*].[InstanceId]",
            "--region","ap-southeast-2","--output","json"
        ], capture_output=True, text=True, timeout=15)
        data = json.loads(r.stdout)
        if data and data[0] and data[0][0]:
            return data[0][0][0]
    except Exception:
        pass
    return hardcoded_fallback  # Only used if EC2 is unreachable
```

## SSM Execution Pattern
AWS Systems Manager (SSM) is required to run commands on EC2 instances inside a VPC. RDS is also VPC-only and must be reached through SSM.

### Prerequisites
- **IAM role:** Instance must have `AmazonSSMManagedInstanceCore` attached
- **psql:** Amazon Linux 2023 requires `sudo yum install -y postgresql15` (not apt-get)
- **Session Manager Plugin:** For `start-session` port forwarding, install `session-manager-plugin` on the client

### Running Commands via SSM send-command
```python
# Send command
cj = json.dumps(["your shell command here"])
r = subprocess.run(["aws","ssm","send-command",
    "--instance-ids", instance_id,
    "--document-name","AWS-RunShellScript",
    "--parameters",f"commands={cj}",
    "--output","json",
    "--region","ap-southeast-2"
], capture_output=True, text=True, timeout=30, env=aws_env)
cid = json.loads(r.stdout)["Command"]["CommandId"]

# Poll for result
time.sleep(3)
r2 = subprocess.run(["aws","ssm","get-command-invocation",
    "--command-id", cid, "--instance-id", instance_id,
    "--region","ap-southeast-2","--output","json"
], capture_output=True, text=True, timeout=15, env=aws_env)
result = json.loads(r2.stdout)
status = result.get("Status")  # "Success", "Failed", "TimedOut"
output = result.get("StandardOutputContent", "")
```

### Common SSM Pitfalls
| Symptom | Root Cause | Fix |
|---------|-----------|-----|
| `InvalidInstanceId` | Instance not registered with SSM | Check IAM role has `AmazonSSMManagedInstanceCore` |
| `command not found: psql` | psql not installed on Amazon Linux 2023 — this does NOT survive instance replacement | `sudo yum install -y postgresql15` (NOT apt-get) |
| `sudo: apt-get: command not found` | Instance is Amazon Linux, not Ubuntu | Use `yum` or `dnf` not `apt-get` |
| `InstanceInformationList: []` | SSM agent not running or no IAM role | Attach IAM profile, wait 2-3 min for registration |
| SSM command stuck "Pending" | SSM agent registered but command execution delayed | Wait up to 30s; if persistent, check SSM agent logs on instance |

## Credential Management
- **AWS credentials:** Read from environment via `load_aws_creds()` pattern (reads `AWS_ACCESS_KEY_ID_AMLHIVE` + `AWS_SECRET_ACCESS_KEY_AMLHIVE` from `.env`)
- **Never hardcode:** All secrets read from `.env` at runtime
- **Fallback chain:** Windows `.hermes/.env` → WSL `~/.hermes/.env`

## Script Architecture for Fleet Monitors
1. **Auto-discover** instances by Name tag at module load (cached)
2. **Fall back** to hardcoded last-known-ID only when EC2 unreachable
3. **Exit non-zero** only for P0 issues (instances not found after discovery)
4. **P1/P2 issues** are reported but don't trigger cron failure status
5. **State files** in `~/.hermes/research_outputs/.attribution_probe/` for persistent counters (threshold tracking across hourly runs)

## Report Formatting — Professional Output

### 🚨 Critical: `"\\n"` vs `"\n"` in Report Assembly
When building multi-line report strings, **never use `"\\n".join(lines)`** — this produces literal backslash-n characters (`\n`) instead of real newlines. The output renders as a single unreadable line in both cron messages and emails.

**Correct:** `report = "\n".join(lines)` — real newlines, renders properly
**Wrong:** `report = "\\n".join(lines)` — literal backslash-n, renders as `\n`

### Professional Formatting Guidelines
- Use **real newlines** (not `\\n` literal sequences)
- Build output as a **list of strings** then `"\n".join()` at the end
- Send email as **`MIMEText(report, "plain")`** — plain text is sufficient
- Use consistent section headers: `━━━ TITLE ━━━`
- Use emoji for status: ✅ healthy, ⚠️ warning, 🔴 alert, ❌ failure, ⚪ skipped
- Keep the report scannable: summary at top, detail section below
- **Never print raw escaped characters** — always verify output renders correctly

### Alert Email Module
For urgent notifications, use `alert_email.py`:
```python
from alert_email import send_alert
send_alert("Subject", "Summary", "<p>HTML body...</p>")
```
The module sends dark-themed RED HTML emails via Purelymail SMTP.

## Version Check — GitHub Dev Branch API

The hourly production version check (`hourly_version_check.py`) reads `.version` from the GitHub dev branch API FIRST — only falling back to the local clone if the API is unreachable.

**Critical per the Pluto operating contract:**
- Prefer reading `.version` live from `https://raw.githubusercontent.com/amlhive-tech/amlhive1/dev/.version`
- Fall back to local working-copy clone only when GitHub API fails
- If GitHub API fails with an auth error (expired PAT, 401/403), **alert immediately** via `alert_email.py` — do NOT silently fall back
- The daily dev-branch fetch (`daily_repo_sync.py` at 02:30) keeps the local clone within 1 day of fresh if the API path is down

**Architecture:**
```
GitHub raw API (PAT auth) ── success → live .version
    │ fail ──→ alert on auth failure
    ▼
Local clone (/mnt/c/Code/github/almhive-tech/amlhive1/.version)
    │ refreshed daily at 02:30 via git fetch+reset origin/dev
    ▼
Compare with API version → MATCH (ok) | STALE_BUILD (alert)
```

**Key insight (Jul 2026):** AMLHive EC2 tag names changed from `amlhive-prod` → `amlhive-prod-backend` and `amlhive-frontend` → `amlhive-prod-frontend` after instance recycles. The auto-discovery tag must match the CURRENT tag on running instances. The `Dev` branch is spelled lowercase `dev` — `Dev` returns 404.

## Common Pitfalls

- **`"\\\\n".join(lines)` — literal backslash-n bug:** Using `"\\\\n".join(lines)` produces the two-character sequence `\\n` instead of actual newline bytes. All cron messages and emails render as a single unreadable line. Always use `"\\n".join(lines)`. This was the root cause of the July 2026 fleet monitor formatting bug.
- **SSM Agent stuck `Pending`:** Instance shows `PingStatus=Online` in `describe-instance-information` but commands hang at `Pending` forever. The SSM agent is registered but command execution is delayed — this can be transient after instance launch or when the agent is under heavy load. Wait 30-60s; if persistent, the AMI may need the SSM agent updated or reinstalled.
- **Instance recycling changes Name tags:** In the July 2026 AMLHive backend recycle, the tag changed from `amlhive-prod` to `amlhive-prod-backend` without notice. Always verify current tags after any instance replacement by running `aws ec2 describe-tags --resource-id <new-id>`.
- **PostgreSQL needs reinstall on each replacement:** Amazon Linux 2023 does NOT ship with `psql` pre-installed. Installing `postgresql15` via yum does NOT survive instance replacement. Every new instance must have psql reinstalled: `sudo yum install -y postgresql15`. This is needed for the daily business report's SSM-based SQL queries.

### Report Formatting — User Preference (Professional)

The user has explicitly requested that ALL email and cron messages follow the **Fleet Monitor formatting standard**. This is a durable user-preference that applies to every report, alert, and summary produced.

The reference template (user-approved):

```
★ Fleet Monitor — AMLHive AWS Production
  Sunday 19 July 2026, 11:00 PM AEST  ·  Window: 10-hour lookback

━━━ EVIDENCE COUNTS ━━━
   Docker restarts: 3 | OOM killed: false
   CloudWatch active alarms: 0
   Backend CW 500/traceback/programming errors: 0 in 10h
   Frontend CW 500/traceback errors: 0 in 10h

━━━ OVERALL STATUS ━━━
   Fleet Monitor: Issues require attention
   7 alert(s): 0 P0, 4 P1, 3 P2
   3 live-impacting • 4 observability drift
```

**Format rules:**
1. **Header line:** `★ [Service] — [Description]` with star emoji
2. **Subheader:** Date, time, window on the next line
3. **Section headers:** `━━━ TITLE ━━━` (em-dash boxes)
4. **Status icons:** ✅ healthy, ⚠️ warning, 🔴 alert, ❌ failure, ⚪ skipped, 🟡 drift
5. **Key-value pairs:** `Label: value | Label: value`
6. **Detail sections:** Summary at top, `━━━ 📋 DETAIL ━━━` below for expanded info
7. **Footer:** `★ Fleet Monitor · Generated [date]` with version
8. **No raw escaped characters** — always verify output renders as real newlines
9. **Plain text email** — `MIMEText(report, "plain")`. No HTML wrapper needed (except for urgent alerts which use `alert_email.py`)
10. **Avoid markdown** — plain text with box-drawing characters is the approved format

## Reference Files
- `references/ssm-psql-connection.md` — Full SSM + psql setup and troubleshooting
- `references/ec2-discover-command.md` — Exact AWS CLI commands for instance discovery
- `references/alert-email-module.md` — Urgent alert email escalation
- `references/asic-ref-db-sync.md` — ASIC/ref-db sync procedure for Pluto as Hivey named agent
- `templates/fleet-monitor-report.md` — User-approved report format template (use this for ALL automated reports)
