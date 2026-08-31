# Alert Patterns & Source Labels

## ALERT_PATTERNS — What Generates Alerts

Only these patterns trigger P0/P1/P2 alerts. Everything else from
`LOG_PATTERNS` is displayed as scanner traffic (grey, no alert):

| Pattern | Severity | Source Label | Description |
|---------|----------|-------------|-------------|
| `Traceback` | P1 | CloudWatch Logs | Python traceback in backend |
| `ProgrammingError` | P1 | CloudWatch Logs | SQLAlchemy query error |
| `UndefinedColumn` | P1 | CloudWatch Logs | Missing DB column |
| `arq_job_failed` | P1 | CloudWatch Logs | ARQ worker job failure |
| ` 500` / ` 502` / ` 503` / ` 504` | P0 | CloudWatch Logs | HTTP 5xx responses |
| `database is locked` | P0 | CloudWatch Logs | SQLite contention |
| `OOM` / `Killed` | P0 | CloudWatch Logs | Out of memory / SIGKILL |
| `OOMKilled` | P0 | Docker inspect | Container OOM from Docker |
| `RestartCount` | P0 | Docker inspect | Container restart count > 0 |
| `outcome=error` | P1 | CloudWatch Logs | Explicit error outcome |
| `CRITICAL` | P1 | CloudWatch Logs | Logging.critical() |
| `PII_ENCRYPTION` | P1 | CloudWatch Logs | PII encryption failure |
| `Failed to decrypt PII` | P1 | CloudWatch Logs | PII decryption failure |
| `BrevoIpBlockedError` | P1 | CloudWatch Logs | Brevo email blocked |
| `connection refused` | P1 | CloudWatch Logs | Network connection failure |

## Source Labels — Per-Section

Each report section carries a `Source:` label:

| Section | Label |
|---------|-------|
| Public Health | *(none — direct HTTP check)* |
| Docker Health | `Source: Docker inspect` |
| CloudWatch Alarms | `Source: CloudWatch Alarm` |
| CloudWatch Log Errors | `Source: CloudWatch Logs` |
| Sentry | `Source: Sentry` |
| RDS | `Source: CloudWatch / RDS` |

## Sentry Project Severity

| Project | Classification | Rationale |
|---------|---------------|-----------|
| `python-fastapi` | 🔴 P0/P1 live-impacting | Backend errors affect all users |
| `javascript-nextjs` | 🟡 P2 observability drift | Client-side browser errors only (static export) |

Smoke test events (title contains "smoke test") are filtered out entirely.

## Evidence Counts Header

Every report starts with:

```
━━━ EVIDENCE COUNTS ━━━
   Docker restarts: {N} | OOM killed: {true/false}
   CloudWatch active alarms: {N}
   Backend CW 500/traceback/programming errors: {N} in 10h
   Frontend CW 500/traceback errors: {N} in 10h
```

These are collected via `count_log_errors()` which checks every found pattern
against `ALERT_PATTERNS` and aggregates by log group name matching "backend"
vs "frontend".

## Smart Title Logic

The overall status title is computed in `build_report()` with this priority:

1. P0 alerts exist → `"Fleet Monitor: LIVE INCIDENT"`
2. P1 alerts exist → `"Fleet Monitor: Issues require attention"`
3. Sentry issues but no CloudWatch/Docker problems → `"Fleet Monitor: AWS/Docker healthy; Sentry warnings present"`
4. CloudWatch/Docker issues → `"Fleet Monitor: CloudWatch/Docker errors detected"`
5. Only P2 drift → `"Fleet Monitor: All systems healthy; minor drift"`
6. Nothing → `"Fleet Monitor: All systems healthy"`

This ensures a Sentry DataCloneError never produces a red "ATTENTION" title
when EC2, Docker, and CloudWatch are all clean.
