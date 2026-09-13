# SSM Fallback: Reading Local Logs When CloudWatch Is Down

When the CloudWatch agent is running but not shipping logs — or logs went silent days/weeks ago — the local log files on the EC2 instance are **still there**. Use SSM Run Command to grep them directly. This is a critical fallback when CloudWatch shows 28+ days of silence but the application is definitely running.

## Pattern

```bash
# 1. Find local log files and their freshness
aws ssm send-command --region ap-southeast-2 \
  --instance-ids i-XXXX --document-name AWS-RunShellScript \
  --parameters '{"commands":["ls -lt /home/ec2-user/app/backend/app/log/ 2>/dev/null | head -10"]}'

# 2. Search for specific patterns in today's log
aws ssm send-command --region ap-southeast-2 \
  --instance-ids i-XXXX --document-name AWS-RunShellScript \
  --parameters '{"commands":["grep -i \"error\\\\|forgot\\\\|reset\" /home/ec2-user/app/backend/app/log/$(date +%Y%m%d)*.log 2>/dev/null | tail -30"]}'

# 3. Check systemd journal for app errors
aws ssm send-command --region ap-southeast-2 \
  --instance-ids i-XXXX --document-name AWS-RunShellScript \
  --parameters '{"commands":["sudo journalctl --no-pager -n 100 | grep -iE \"(error|reset|password|email|forgot)\" | tail -30"]}'
```

## SSM Command Workflow

1. Send the command → capture `CommandId` from the output
2. Wait **8-15 seconds** (SSM execution is slow — commands with long-running processes need more time)
3. Poll with `get-command-invocation`:

```bash
aws ssm get-command-invocation --region ap-southeast-2 \
  --command-id <cmd-id> --instance-id i-XXXX \
  --query 'StandardOutputContent' --output text
```

If you get `InvocationDoesNotExist`, the command is still running or timed out. Retry after 5 more seconds.

## Key Signals to Grep For

| Signal | grep Pattern | What It Means |
|--------|-------------|---------------|
| App alive | `uvicorn` in `ps aux` | FastAPI process running |
| Auth failures | `forgot-password\|reset\|password\|email` | Password reset requests, email sends, login attempts |
| SES success | `sent successfully` | Email was accepted by SES for delivery |
| SES failure | `Failed to send\|error.*email` | SES rejected the send request |
| App errors | `error\|exception\|traceback` (exclude `expected_error` noise) | Application-level failures |
| Queued emails | `Queued.*email` | App's internal email batching queue working |

## Filter Out Noise

Many applications log "expected_error" events (4xx API responses that are normal operational patterns). Always exclude these from error searches:

```bash
grep -i "error\|fail\|exception" logfile.log | grep -v "expected_error\|suppressed"
```

## Trace the Full Email Flow

Combine all signals to trace the chain: API call → token generation → SES client init → SES send → delivery status:

```bash
grep -i "forgot\|send_email\|SES\|sent successfully\|Failed to send" /path/to/log/*.log
```

## When CloudWatch Went Silent

If `describe-log-streams` shows `lastEventTimestamp` >7 days old and `storedBytes: 0` on all streams, but the instance is `running` with the application active:

1. **Check agent restart time** — `sudo systemctl status amazon-cloudwatch-agent` shows `Active: active (running) since` timestamp
2. **Check agent log** — `/opt/aws/amazon-cloudwatch-agent/logs/amazon-cloudwatch-agent.log` — look for `[logagent] piping log from` lines to confirm what files it's tailing
3. **Just restarted?** — logs appear in CloudWatch within ~1 minute of the agent start. If a system update or cron restart happened, the gap is explained
4. **Running but no log piping lines?** — config is missing log file entries (see RPM Upgrade Recovery in the main skill)
5. **Use SSM to grep local logs as bridge** — until CloudWatch catches up, live-read via SSM
