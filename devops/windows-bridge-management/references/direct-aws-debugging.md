# Direct AWS Debugging — TapEase Fallback (when bridge is down)

## When to Use This

The n8n Bridge at `localhost:18796` responds on `/health` but `POST /tapease/monitor`
times out or returns an HTML error page instead of JSON. Do NOT keep retrying the
bridge — go direct to AWS.

## Prerequisites

AWS CLI is configured with a `tapease` profile in `~/.aws/credentials`:

```
[tapease]
aws_access_key_id = ...
aws_secret_access_key = ...
```

The profile uses the `IAM_GRAFANA` user in account `707843605914`.

## Step 1: Find the Right Region

The Tapease profile's default region (`ap-south-1`) is WRONG for application logs.
TapEase infrastructure runs in **ap-southeast-2** (Sydney).

Scan all regions to find TapEase log groups:

```bash
for region in ap-southeast-1 ap-southeast-2 us-east-1 us-west-2 eu-west-1 eu-west-2 ap-south-1; do
  echo "=== $region ==="
  aws --profile tapease logs describe-log-groups --region "$region" --query 'logGroups[].logGroupName' --output text 2>&1
done
```

**TapEase log groups (ap-southeast-2):**
| Log Group | Source |
|---|---|
| `/tapease/production/backend` | FastAPI application logs |
| `/tapease/production/backend-otel` | OpenTelemetry traces |
| `/tapease/production/frontend` | Frontend app logs |
| `/tapease/production/frontend-error` | Frontend error events |
| `/tapease/production/frontend-pm2` | PM2 process manager logs |
| `/aws/ec2/backend/tapease-production` | EC2 CloudWatch agent (backend) |
| `/aws/ec2/frontend/tapease-production` | EC2 CloudWatch agent (frontend) |
| `/aws/lambda/tapease-clover-sync-production` | Lambda execution logs |
| `/tapease/production/frontend-structured` | Structured frontend logs |

## Step 2: Detect Silent Log Gaps

`filter-log-events` returns empty for recent queries even when log groups exist.
The *real* signal is `lastEventTimestamp` on log **streams**.

```bash
# Check when the backend LAST logged anything
aws --profile tapease logs describe-log-streams \
  --region ap-southeast-2 \
  --log-group-name /tapease/production/backend \
  --order-by LastEventTime --descending --max-items 5 \
  --query 'logStreams[*].[logStreamName,lastEventTimestamp,storedBytes]' \
  --output table
```

**Convert the epoch (ms):**
```python
import datetime
ts = 1780189647222 / 1000.0
print(datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S'))
```

A lastEventTimestamp > 7 days old with `storedBytes: 0` means the CloudWatch agent
on the EC2 instance has stopped shipping logs — even if the app is still running
and writing to local files.

## Step 3: SSM — On-Instance Debugging

When CloudWatch is stale, use AWS SSM Run Command to check the actual application
on the EC2 instance.

### Find EC2 instances

```bash
aws --profile tapease ec2 describe-instances \
  --region ap-southeast-2 \
  --query 'Reservations[*].Instances[*].[InstanceId,PublicIpAddress,PrivateIpAddress,State.Name,Tags[?Key==`Name`].Value|[0]]' \
  --output table
```

**TapEase instances:**
| Instance | Name | Private IP | Public IP |
|---|---|---|---|
| `i-062b8ef5...` | `tapease-backend-production` | `10.0.2.161` | None (NAT/bastion only) |
| `i-0aca7e10...` | `tapease-frontend-production` | `10.0.1.130` | `13.210.208.34` |
| `i-0c9a14c4...` | `tapease-nat-instance-production` | — | — |
| `i-06c24009...` | `tapease-bastion-production` | — | — |

### Check SSM agent status

```bash
aws --profile tapease ssm describe-instance-information \
  --region ap-southeast-2 \
  --filters "Key=InstanceIds,Values=i-062b8ef5437ea6e2f"
```

Both TapEase instances run Amazon Linux with SSM agent `3.3.3598.0`.

### Send commands (use cli-input-json to avoid shell quoting hell)

Write commands to a JSON file to bypass shell quote conflicts:

```bash
cat > /tmp/ssm_cmd.json << 'JSONEOF'
{
  "DocumentName": "AWS-RunShellScript",
  "InstanceIds": ["i-062b8ef5437ea6e2f"],
  "Parameters": {
    "commands": [
      "curl -s http://localhost:8000/health",
      "echo ==APP==",
      "ps aux | grep uvicorn | grep -v grep",
      "echo ==LOGS==",
      "ls -lt /home/ec2-user/app/backend/app/log/*.log | head -5",
      "echo ==RECENT_ERRORS==",
      "grep -i error /home/ec2-user/app/backend/app/log/$(date +%%Y%%m%%d)-PROD*.log 2>/dev/null | grep -v expected_error | tail -10"
    ]
  }
}
JSONEOF

aws --profile tapease ssm send-command \
  --cli-input-json file:///tmp/ssm_cmd.json \
  --region ap-southeast-2 \
  --output text --query 'Command.CommandId'
```

Get the output:
```bash
aws --profile tapease ssm get-command-invocation \
  --region ap-southeast-2 \
  --command-id <COMMAND_ID> \
  --instance-id i-062b8ef5437ea6e2f \
  --output text --query 'StandardOutputContent'
```

### Things to check via SSM

| Check | Command |
|---|---|
| App process | `ps aux \| grep uvicorn` |
| App listening | `sudo ss -tlnp \| grep -E "8000\|443\|80"` |
| Nginx status | `sudo systemctl status nginx` |
| CloudWatch agent | `sudo systemctl status amazon-cloudwatch-agent` |
| Local log files | `ls -lt /home/ec2-user/app/backend/app/log/` |
| Journald app logs | `sudo journalctl --no-pager -u app-* -n 50 2>/dev/null \| grep -iE "error\|reset\|email"` |
| Health check | `curl -s http://localhost:8000/health` |
| Password reset | `curl -s http://localhost:8000/auth/forgot-password -X POST -H "Content-Type: application/json" -d '{"email":"test@example.com"}'` |

## Step 4: SES Deliverability Audit

Even when the backend logs say "password reset email sent successfully," the email
may not reach the user. Check SES directly.

### Verified identities

```bash
aws --profile tapease ses list-identities --region ap-southeast-2
aws --profile tapease ses get-identity-verification-attributes \
  --region ap-southeast-2 \
  --identities tapease.com.au help@tapease.com.au
```

**TapEase SES identities (all verified ✅):**
- `tapease.com.au` (domain)
- `help@tapease.com.au` (sender email)
- `shoaib.habib@a2square.com.au`, `haris.habib@a2square.com.au`

### Sending limits

```bash
aws --profile tapease ses get-send-quota --region ap-southeast-2
```

Production level: **50,000/day** (not sandbox mode).
Monitor `SentLast24Hours` — 298 as of June 28, well within limits.

### DKIM status — THE MOST COMMON ISSUE

```bash
aws --profile tapease ses get-identity-dkim-attributes \
  --region ap-southeast-2 --identities tapease.com.au
```

**If `DkimEnabled: false`**, SES sends the email but receiving servers
(Gmail, Outlook) may classify it as spam. DKIM must be enabled and the 3 CNAME
records published in DNS:

```bash
aws ses set-identity-dkim-enabled \
  --region ap-southeast-2 \
  --identity tapease.com.au \
  --dkim-enabled
```

DKIM tokens (add as CNAME records):
```
oceqbnlzjdvxewqe4nbgmogr2k6ztsip._domainkey.tapease.com.au
vekkzrg3bxge3nogbzo6olwvdla4gce3._domainkey.tapease.com.au
hz6ai7dkyciqld7m6oix2oif3ajhpdqz._domainkey.tapease.com.au
```

### MAIL FROM domain

```bash
aws --profile tapease ses get-identity-mail-from-domain-attributes \
  --region ap-southeast-2 --identities tapease.com.au
```

TapEase uses `mail.tapease.com.au` — status should be `Success`.

### Bounce/complaint configuration

```bash
aws --profile tapease ses get-identity-notification-attributes \
  --region ap-southeast-2 --identities tapease.com.au
```

`ForwardingEnabled: true` means bounces go to the identity's email inbox.
No SNS topic configured — consider setting one up for proactive notifications.

## Step 5: Application Code Tracing

The password reset flow lives in the backend app running on the EC2 instance:

```
/home/ec2-user/app/backend/
├── app/
│   ├── routers/
│   │   └── auth.py          ← /forgot-password and /reset-password endpoints
│   ├── email_utils.py       ← EmailService class, SES client init, email sending
│   └── config.py            ← Settings (EMAIL_FROM, SES_REGION, EMAIL_URL)
├── .env                     ← All config vars (EMAIL_FROM=help@tapease.com.au, EMAIL_URL=https://tapease.com.au)
└── venv/bin/uvicorn         ← Running since Jun 9 (PID 54833)
```

### Password reset code path

1. **`auth.py:1173`** — `@router.post("/forgot-password")`
2. Queries `auth_users` table for the email
3. If found: generates a JWT with `create_access_token(data={"type": "reset_password", ...}, expires_delta=1h)`
4. **`auth.py:1232`** — Calls `email_service.send_password_reset_email(email, first_name, user_id)`
5. **`email_utils.py:1014`** — Builds reset URL: `{settings.EMAIL_URL}/reset-password?token={reset_token}`
6. Sends via SES with sender `help@tapease.com.au`
7. Logs success or failure

### Key config values from .env

```
EMAIL_FROM=help@tapease.com.au
EMAIL_FROM_NAME=Tapease
EMAIL_URL=https://tapease.com.au
SES_REGION=ap-southeast-2
SES_USE_IAM_ROLE=true
```

### Local log location

The app writes daily log files — NOT shipped to CloudWatch if the agent is down:
```
/home/ec2-user/app/backend/app/log/20260628-PROD-TAPEASE_BACKEND.log
/home/ec2-user/app/backend/app/log/20260628-PROD-TAPEASE_BACKEND_OTEL.log
```

These are the canonical source of truth when CloudWatch is stale.

## Pitfalls

- **Default region is wrong.** The tapease profile defaults to `ap-south-1`.
  All TapEase application resources are in `ap-southeast-2`. Always override with
  `--region ap-southeast-2`.

- **SSM commands with JSON payloads.** AWS CLI v1 chokes on single quotes and
  embedded JSON in `--parameters`. Always use `--cli-input-json file:///tmp/file.json`
  to pass multi-command payloads to SSM.

- **IAM_GRAFANA user has limited permissions.** Can describe CloudWatch log groups
  and EC2 instances, send SSM commands, read SES identities/quota. Cannot access
  SES send statistics, identity policies, or account-level settings. For full SES
  debugging, use the EC2 instance role (`tapease-backend-role-production`) via SSM.

- **CloudWatch silence ≠ app down.** In June 2026, CloudWatch logs showed no events
  for 28 days but the app was running fine (uvicorn PID, serving traffic). Always
  check via SSM before concluding the app is dead.

- **Health endpoint at the wrong path.** The real health endpoint is `GET /health`
  (no `/api/` prefix). `GET /api/health` and `GET /` return 404 or the frontend
  page. When verifying, test BOTH paths.

- **DKIM disabled = sent but not delivered.** SES returns 200 OK for the API call
  even when DKIM is disabled. The email leaves AWS but receiving servers drop or
  spam-folder it. The backend log will say "sent successfully" — that only confirms
  SES accepted it, not that the user received it.
