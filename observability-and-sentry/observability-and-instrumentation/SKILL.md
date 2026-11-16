---
name: observability-and-instrumentation
description: >-
  Instruments code so production behaviour is visible and diagnosable: structured logs, metrics, traces and alerts chosen from the questions on-call will ask. Use when adding logging, metrics, tracing or alerting, when shipping a feature, job or integration that runs in production, when reviewing a pull request that adds I/O, retries, queues or cross-service calls, or after an incident where the available data could not say what happened.
---

# Observability and Instrumentation

Source: adapted from `addyosmani/agent-skills` `observability-and-instrumentation` (MIT, (c) 2025 Addy Osmani), rewritten for this repo's rules. It adds method; the binding rules stay in `rules/observability-and-error-management.md` and `rules/external-calls-logged-request-and-response-mask-secrets.md`.

If it can fail, its failure must be visible without a customer reporting it. For a failure happening right now use `systematic-debugging`; this skill is what makes that fast next time.

## Process

### 1. Define "working" before instrumenting
Write 2 to 4 questions an on-call engineer will ask, and let every signal answer one of them.
```
FEATURE: payment retry
QUESTIONS: 1) share of payments that succeed first time vs after retry?
           2) when one fails permanently, why (provider, timeout, validation)?
           3) is the provider slower than usual?
```
If you cannot name the questions, you will log everything and learn nothing.

### 2. Pick the signal
| Signal | Answers | Cost |
|---|---|---|
| Structured log | What happened in this case, and why | per event, grows with traffic |
| Metric | How often or how fast, in aggregate | fixed per series, cheap to query |
| Trace | Where did the time go across services | per request, usually sampled |

Metrics say **that** something is wrong, traces **where**, logs **why**.

### 3. Structured logs
Log events with a stable name and machine-readable fields, not interpolated prose: `{event: "payment_failed", paymentId, provider, errorCode, attempt}`.

| Level | Meaning | Action |
|---|---|---|
| error | invariant broken | investigate |
| warn | degraded but handled (retry worked, fallback used) | watch trend |
| info | significant business event | none |
| debug | diagnostic detail, off in production | none |

- **Correlation ID is mandatory.** Accept or create a request ID at the boundary, attach it to every log line, span and outbound call, return it in a response header, and carry it across queues.
- **Name the entry point** when one job can start from a scheduler, a replay endpoint or a CLI. Log `entryPoint` and the run ID on every line, and pass both across the same boundaries as the correlation ID. Use `entryPoint`, not `source` (ECS reserves `source.*` for network fields).
- **Secrets never appear** in logs, queries or traces: tokens, passwords, keys, full card numbers, one-time codes, and secrets in query strings (`rules/secrets-in-query-strings-never-logged.md`). Mask by field name, ending in token, secret or password, and check what a field means before masking it.
- **Personal data follows the project's recorded decision.** Where the owner has decided that personal data is logged in full (Tap-Ease, 6 and 11 Nov 2026), log it in full and mask only secrets and card numbers. Where no decision exists, ask; do not assume either way.
- Every external request and response is logged through one shared helper (`rules/external-calls-logged-request-and-response-mask-secrets.md`).
- Never swallow an exception. Log it with context and surface it.

### 4. Metrics
For each request-driven endpoint and each external dependency, track **RED**: rate, errors, duration as a histogram. For queues and workers track depth, age of the oldest item, and failures. Report percentiles (p50, p95, p99), never averages.

**Cardinality is the failure mode.** Every label combination is a separate series. Labels come from small fixed sets: route template, status class, provider name. Never a user ID, email, request ID, full URL or error text.

### 5. Traces
Use OpenTelemetry for a vendor-neutral path; auto-instrumentation covers HTTP, gRPC and common database clients. Propagate context through queues. Sample, but always keep errors and slow requests.

### 6. Alerts
Alert on symptoms users feel (error rate, latency, a missed schedule), not on every cause. Every alert has an owner, a runbook link and a tested path to actually fire: an alarm stuck on INSUFFICIENT_DATA is not an alarm (`rules/alert-fanout-and-suppression-check.md`, and the `monitoring-alert-verification` skill). Failures invisible from inside the app, such as a proxy rejecting requests before app code runs, need an outside-in probe.

### 7. Keep local runs out of production telemetry
Local and test runs must not report to production Sentry, logs or metrics (`rules/local-runs-must-not-report-to-production-observability.md`).

## Common rationalizations

| Excuse | Reality |
|---|---|
| "We will add logging when something breaks" | The first outage is the one you cannot explain. |
| "Log everything, filter later" | Cost and noise bury the one line you need. |
| "Average latency is fine" | The average hides the 1% having a terrible time. |
| "A user ID label is useful" | It creates millions of series and takes the metrics store down. |
| "The alarm exists" | Has it ever fired? Prove it can. |

## Red flags

- A new integration or job with no log, metric or alert.
- Log lines built by string interpolation.
- No correlation ID, or one lost at a queue.
- A high-cardinality metric label.
- Secrets or tokens anywhere in telemetry.
- An alarm that has only ever reported INSUFFICIENT_DATA.
- An empty `catch` or `except: pass`.

## Verification

- [ ] The on-call questions are written and each signal answers one.
- [ ] Logs are structured with a stable event name, correlation ID and entry point.
- [ ] RED metrics exist for each endpoint and dependency, with bounded labels.
- [ ] No secrets in telemetry; personal data handled per the recorded project decision.
- [ ] Each alert has an owner, a runbook and a proof that it can fire.
- [ ] Local runs do not report to production.

## See also

`observability-and-sentry/sentry-triage`, `observability-and-sentry/notification-coverage-audit`, `observability-and-sentry/prod-issue-management`, `shipping-and-launch`.
