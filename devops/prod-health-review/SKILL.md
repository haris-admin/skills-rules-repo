---
name: prod-health-review
description: >-
  Run a read-only production health review of an AWS-hosted stack: CloudWatch
  alarms not in OK (including composite alarms), endpoint timings, Synthetics
  canaries, Logs Insights error and status-code counts, and identification of
  scheduled probes that look like attacks. Use when asked for a health check,
  "is prod healthy", a post-deploy or post-apply review, or context for an alarm
  or error-tracker spike. Never mutates anything.
---

# Production Health Review (read-only)

Read-only. No restarts, deploys, alarm changes or writes. Every `aws` command carries an explicit
`--profile` and `--region` (a bare command can hit another company's account). Never print secrets.

## Steps

1. **Alarms not OK.** `aws cloudwatch describe-alarms --state-value ALARM` and
   `--state-value INSUFFICIENT_DATA`, with `--alarm-types CompositeAlarm MetricAlarm` so composite
   alarms are included. `INSUFFICIENT_DATA` is itself a finding. A silenced alarm is reported with its
   reason; a Terraform apply re-enables alarm actions (`rules/terraform-prod-apply-safety.md`). Run
   the repo's alarm dimension audit to prove no alarm is blind, allowing about 10 minutes after an
   instance replacement before trusting `blind=0`.
2. **Endpoints with timings.** `curl -s -o /dev/null -w '%{http_code} %{time_total}s\n' <url>` for the
   health, readiness and main public routes. Use the readiness endpoint for dependency health; a
   dependency-free health endpoint stays green through a database outage.
3. **Canaries.** `aws synthetics describe-canaries` and `get-canary-runs`: state, last result and age.
   A canary that never started is a finding.
4. **Logs Insights, not `filter-log-events`.** For any window over a few hours use
   `aws logs start-query` and `get-query-results` with **epoch seconds** (`filter-log-events` uses
   milliseconds and can silently truncate, so an empty result looks like "no matches"). Query the
   backend, frontend and web-server groups for error counts by message, status-code counts, and the
   top 401 and 403 paths.
   - Log messages can contain quotes that break a naive JSON parse. Parse the results with
     `json.loads(text, strict=False)` and treat fields as strings.
   - Message bodies may be in local time while query bounds are UTC epoch seconds. Never mix them.
5. **Identify scheduled probes before calling anything an attack.** Match a repeating path and interval
   against canaries, CI schedules and probe workflows. Worked example (AMLHive): a login canary sends
   an unauthenticated `GET /api/v1/users/me` every 15 minutes, which returns 401 and writes an
   "Api Auth Denied" audit row by design.
6. **Error tracker.** Check delivery outcomes (usage stats by outcome), not only the issue list, before
   writing "none surfaced".
7. **Report.** One table: area, check, command, real result, status (OK, finding, unknown). State what
   was not checked. Log findings through the issue process; do not fix inside the review.

## Never

- Never run a write, restart or apply from this skill.
- Never call a finding resolved because one clean snapshot looked fine (`rules/verify-external-agent-reports.md`).
- Never widen a token or use root to obtain a missing reading (`rules/no-root-or-unbounded-credentials-for-agents.md`).
