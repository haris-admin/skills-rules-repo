# AmLHive Production Monitor Specification

> Source of truth for the AmLHive AWS production fleet monitor behaviour.
> Defined by Haris on 6 July 2026.

## Mission

Monitor AMLHive production on AWS and report emerging patterns across:

- AWS EC2 backend/frontend health
- Docker container uptime and restarts
- CloudWatch alarms
- CloudWatch backend/frontend/system logs
- RDS health and Postgres logs
- Sentry backend/frontend error trends
- Public API/frontend availability

## AWS Account

- Account: 560205084533
- Region: ap-southeast-2
- IAM user: IAM_MONITOR

If the active AWS account is not 560205084533, stop and alert:
> Wrong AWS account/profile. AMLHive monitor cannot be trusted.

## Production Hosts

| Role | Name | Instance ID | Type |
|------|------|-------------|------|
| Backend | amlhive-prod | i-0abe6a7923fa0dec2 | t3.medium |
| Frontend | amlhive-frontend | i-0ac2e7df9409d50fd | t3.small |

**⚠️ Instance IDs change when EC2 instances are replaced.** If SSM commands return `InvalidInstanceId`, verify current IDs via `describe-instances` with name-tag filter. Update in amlhive_prod_monitor.py constants and amlhive_aws_health.py check_docker() instance_names.

Both must be: running, EC2 status ok, SSM reachable, Docker container running.

## Public Health Checks

Check every cycle:
- `https://api.amlhive.com.au/health` — expect HTTP 200, body contains `{"status":"ok"}`
- `https://amlhive.com.au` — expect HTTP 200

Alert P0 if either fails twice in a row.

## Docker Checks

On backend: verify container running, restart count not unexpectedly increased, uptime stable, no repeated boot loops / DB connection failures / Redis failures / migration errors / 5xx bursts.

On frontend: verify container running, uptime stable, no repeated Next.js crashes, routing errors, MIME errors, API proxy failures.

Flag P1 if container uptime resets between cycles without a known deploy.

## CloudWatch Alarms

List all alarms with prefix `amlhive`.

Stale/orphaned alarm detection: if ALARM because "no datapoints were received" / "missing datapoints were treated as Breaching", check the alarm dimension InstanceId. If InstanceId is not a current production instance ID, classify as:

> Stale CloudWatch alarm attached to deleted/replaced instance, not live outage.

**Known stale alarms** (suppress as production-outage signals):
- `amlhive-backend-status-check-failed` — points at old instance `i-0ce168df329f256a4`
- `amlhive-frontend-status-check-failed` — points at old instance `i-053d13d8e19b7ff47`
- Matching high-CPU alarms may also point at old IDs

Report them under "Observability drift / cleanup required". Do NOT mark overall production unhealthy if current EC2 statuses and public health checks are OK.

## RDS Checks

- Identifier: amlhive-prod
- Engine: Postgres 17.x
- Status: available
- Region: ap-southeast-2

Check: DB status, CPU, connections, free storage, Postgres logs for auth failures, connection exhaustion, SSL errors, migration/alembic errors, restart messages.

CloudWatch RDS dimensions must use DB identifier `amlhive-prod`, not DB resource ID.

## CloudWatch Logs

Review these log groups every cycle with a **10-hour lookback window** (overlap guarantees no gaps between 6-hour cron cycles):
- /amlhive/backend, /amlhive/backend-system
- /amlhive/frontend, /amlhive/frontend-system
- /aws/rds/instance/amlhive-prod/postgresql, /aws/rds/instance/amlhive-prod/upgrade

**CRITICAL:** `filter-log-events` without `--start-time`/`--end-time` returns events in ascending order (oldest first), not newest. Always include explicit time range parameters. Without them, the monitor will scan logs from the beginning of the log stream (possibly days old) and miss recent errors entirely.

Search patterns: ERROR, CRITICAL, Traceback, Exception, 502, 503, 504, connection refused, timeout, no pg_hba.conf, SSL, database is locked, Redis, CROSSSLOT, OOM, Killed, permission denied, AccessDenied, InvalidToken, JWT, agency_id, current_agency_id, RLS, Sentry, ABN, Stripe, Veriff, Dilisense, ProgrammingError, UndefinedColumn, arq_job_failed, Brevo, PII_ENCRYPTION, PII, refresh_token_not_found, socket hang up, ECONNRESET, upstream sent too big header, buffered to a temporary file.

Report repeated patterns, not isolated noise.

**Regression tracking:** Five known issues were resolved on 07 Jul 2026. The monitor tracks `KNOWN_RESOLVED_PATTERNS` (ProgrammingError, UndefinedColumn, arq_job_failed, BrevoIpBlockedError, Failed to decrypt PII) and alerts P1 immediately if any reappear — this ensures previously-fixed issues are caught at the first cycle they return.

## Sentry

Check both projects: python-fastapi (backend), javascript-nextjs (frontend).

**Token scope limitation:** The `SENTRY_AUTH_TOKEN` has only `project:read` scope. The `/issues/` endpoint requires `event:read` and returns HTTP 403. **Workaround:** Use `/events/?full=true&limit=20` endpoint instead — it works with `project:read` and returns full event details (title, level, message, groupID). Group events by `groupID` to reconstruct unique issues.

**Frontend handling:** The Next.js app is a static export (`output: "export"`) — there is no server runtime, so server-side Sentry hooks never trigger. Only client-side JavaScript errors from real user browsers produce events. 0 events is the expected normal state. Do not flag as P2 silence. Server-side frontend errors (Next.js proxy failures, nginx issues, Supabase auth errors) appear in CloudWatch `/amlhive/frontend` and `/amlhive/frontend-system` — those are the correct source for frontend server monitoring.

Report for python-fastapi: event count + grouped issue details (title, level, sample message, count).
Report for javascript-nextjs: event count only, with note "static export — client-side errors only".

If 0 events for python-fastapi for 24h AND API health returns 200: flag P2 possible DSN/telemetry issue.

## Severity Rules

| Severity | Criteria |
|----------|----------|
| **P0** | Public API fails twice; frontend non-200 twice; current EC2 impaired; backend container down/boot-looping; RDS unavailable; 5xx spike; security/tenant-isolation errors |
| **P1** | Container restarted unexpectedly; repeated log errors; Sentry regression/spike; RDS connection pressure; SSM lost; disk >80%; memory >85% |
| **P2** | Stale/orphaned CloudWatch alarms; Sentry silence without corroborating errors; log growth anomaly; non-critical warning patterns |

## Output Format — 10 Sections

1. Overall status: Healthy / Attention / Incident
2. Public health summary
3. EC2 + Docker summary
4. CloudWatch alarm summary
5. Backend log patterns
6. Frontend log patterns
7. RDS/log patterns
8. Sentry patterns
9. Emerging patterns section
10. Actions recommended section

Every alert must include: severity, evidence, affected resource, whether it is live-impacting or observability drift, recommended next action.

## Current Known Issue (6 July 2026)

The two EC2 status-check alarms are stale because they point to replaced instance IDs and use TreatMissingData=breaching. Do not page as production down if current EC2 instances are OK and public health is OK. Report as:

> Observability drift: stale CloudWatch alarms need Terraform/import cleanup under 00g/T00g.05 and 00h/T00h.01.
