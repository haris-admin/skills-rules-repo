# An in-process rate limiter is only correct with one process: guard it with a test

A limiter that keeps its counters in process memory enforces N times the limit with N workers and resets on restart. Make that assumption a failing test, not a comment.

**Scope:** API rate limits, export limits and audit-row limits implemented without a shared store.

---

## Core Directives

1. **State the limit in the design**: single process per host, counters bounded, expiry of old clients, injected clock in tests.
2. **Add a guard test**: fail if the Dockerfile `CMD`, `WEB_CONCURRENCY`, gunicorn config or the deploy script runs more than one worker or more than one API container, unless the limiter has a shared store; the failure message names the design document.
3. **Take the client IP safely**: behind a proxy use the Nth entry from the right of `X-Forwarded-For`, never the leftmost; document the hop count as a setting.
4. **Limit work, not truth**: a limiter that protects an audit table writes one summary row per client per minute when over the limit, instead of dropping events silently.

## Why this exists

**6 Nov 2026 (HandleDispute):** the receipt parse route took uploads without login; the limiter shipped with a test that fails if a second worker or container appears.
