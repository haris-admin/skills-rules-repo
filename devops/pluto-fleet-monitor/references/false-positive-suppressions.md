# False Positive Suppression — Log Pattern Matching

## Why Needed

The `amlhive_prod_monitor.py` scans CloudWatch log groups for patterns. Several
common log sources produce messages that match alert-worthy patterns but are
**not** application defects:

| Pattern | False Positive Source | Example |
|---------|---------------------|---------|
| ` 503` | nginx upstream timeout behind Cloudflare | `GET /_next/static/... HTTP/1.1" 503` from scanner traffic shows as real 503 |
| `SSL` | Scanner SSL handshake failures in nginx | `SSL_do_handshake() failed (SSL: error:0A000172...)` |
| `/.env` | Bot/probe GET requests for `.env` files | `"GET /.env HTTP/1.1" 404` |
| ` 307` | Cloudflare challenge redirects for scanner paths | `"GET /wp-admin.php HTTP/1.1" 307` |
| `retry_failed_notifications` | Routine ARQ worker retry, not a failure | `retry_failed_notifications ... sent 1 retry` |
| `Failed to find Server Action` | Stale deployment artifact | `Failed to find Server Action "x"` |
| Sentry smoke tests | Deliberate test events | `AMLHive backend Sentry smoke test 2026-...` |

## Two-Layer Approach

### Layer 1: NOISE_SUPPRESSIONS (log-scan level)

Defined at module level in `amlhive_prod_monitor.py`. These patterns are
**completely excluded** from the pattern matching loop — they never appear
in the found-patterns output at all:

```python
NOISE_SUPPRESSIONS = {
    "SSL": ["ssl_do_handshake", "ssl routines", "error:0", "error:14"],
    "/.env": [],
    "error_log.php": [],
    "Failed to find Server Action": [],
    " 307": [],
    "retry_failed_notifications": [],
}
```

When the list is empty (`[]`), the pattern ITSELF is considered noise — ANY
match is suppressed. When the list has substrings, only messages containing
those substrings are suppressed (allowing legitimate matches through).

The `_is_noise(pat, msg)` function in `check_cloudwatch_logs()` applies this:
- If `NOISE_SUPPRESSIONS[pat]` is empty → always noise, skip immediately
- If `NOISE_SUPPRESSIONS[pat]` has substrings → only noise if any substring
  appears in the lowercased log message

### Layer 2: ALERT_PATTERNS (alert-gate level)

After patterns are found and displayed in the report, only patterns in
`ALERT_PATTERNS` generate actual alerts. Everything else is shown as
"scanner traffic" (grey, no alert):

```python
ALERT_PATTERNS = {
    "Traceback", "ProgrammingError", "UndefinedColumn", "arq_job_failed",
    " 500", " 502", " 503", " 504",
    "database is locked", "OOM", "Killed",
    "OOMKilled", "RestartCount",
    "outcome=error",
    "CRITICAL",
    "PII_ENCRYPTION", "Failed to decrypt PII",
    "BrevoIpBlockedError", "connection refused",
}
```

## OpenSSL Error Codes

nginx error logs use format
`[crit] ... SSL_do_handshake() failed (SSL: error:<HEX>:<library>:...)`.
The hex codes follow OpenSSL's error numbering:
- `error:0A*` — SSL routines
- `error:14*` — TLS/SSL connection errors
- `error:1*` — miscellaneous system errors

The suppression uses `"error:0"`, `"error:14"` as catch-all substrings.
These are broad enough to catch all OpenSSL variants without suppressing
genuine application ERROR messages.

## Server Action Mismatch

Next.js deployment version mismatches produce `"Failed to find Server
Action"`. These are transient deployment artifacts — not app defects.
Suppressed at the noise level.

## Sentry Smoke Tests

In `check_sentry()` — events with `"smoke test"` or `"smoke_test"` in the
title are skipped entirely. Deliberate verification events, never real errors.

## Adding New Suppressions

1. Identify the exact log message substring that distinguishes the false
   positive from a real match
2. Add to `NOISE_SUPPRESSIONS` if it's always noise (empty list) or
   conditionally noise (substring list)
3. Add to `ALERT_PATTERNS` if it should produce alerts — DON'T if it's
   display-only
4. Test against real CloudWatch samples
5. Update this file

## Verifying Suppression Works

Run the monitor and check:
- Display-only patterns show as `⚫ {pat} × {count} — scanner traffic`
- Alert-worthy patterns show as `🔴 {pat} × {count} (Source: CloudWatch Logs)`
- Alert count should show `0 P0, 0 P1` when only scanner traffic exists
