# TapEase CloudWatch Agent Configuration Reference

## Backend Instance: i-062b8ef5437ea6e2f

Application base: `/home/ec2-user/app/backend/`
Log directory: `/home/ec2-user/app/backend/app/log/`
Log pattern: `PROD-TAPEASE_BACKEND*.log` (daily rotation)
App server: FastAPI/uvicorn on port 8000 (PID 54833)
Nginx reverse proxy: Port 80 → 8000
Amazon Linux, t4g.medium

**Expected log config in `amazon-cloudwatch-agent.json`:**
```json
{
  "file_path": "/home/ec2-user/app/backend/app/log/*.log",
  "log_group_name": "/tapease/production/backend",
  "log_stream_name": "app-{instance_id}",
  "timezone": "UTC"
}
```

**Nginx access logs also captured:**
```json
{
  "file_path": "/var/log/nginx/access.log",
  "log_group_name": "/tapease/production/backend",
  "log_stream_name": "nginx-access-{instance_id}",
  "timezone": "UTC"
}
```

## Frontend Instance: i-0aca7e109d0f6e773

Public IP: 13.210.208.34
Amazon Linux, t4g.small

**Frontend log groups:**
- `/tapease/production/frontend` — Next.js application logs
- `/tapease/production/frontend-error` — Structured error events
- `/tapease/production/frontend-pm2` — PM2 process manager
- `/tapease/production/frontend-structured` — Structured log format

## CloudWatch Agent Location

Config file: `/opt/aws/amazon-cloudwatch-agent/etc/amazon-cloudwatch-agent.json`
Agent log: `/opt/aws/amazon-cloudwatch-agent/logs/amazon-cloudwatch-agent.log`
Systemd unit: `amazon-cloudwatch-agent.service`
Binary: `/opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent`

## Known Issues

- After `yum update`, the JSON config is deleted. Must be redeployed.
- Agent may restart after system updates, causing a log gap.
- The agent can report `configstatus: configured` but only collect metrics (no logs)
  if the JSON config is missing the `logs.logs_collected.files` section.
