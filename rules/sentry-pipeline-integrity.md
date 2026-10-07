# Sentry Pipeline Integrity

Keep an error-reporting pipeline from silently losing, over-sharing or mis-filtering events: drop rules, size and privacy, process initialisation, test fixtures and what "Sentry saw nothing" has to mean.

<!-- IMPORTANT: Do NOT include YAML frontmatter (---) in rules/*.md. Rules must begin with an H1 title on line 1. -->

**Scope:** All agents, any service that reports errors to Sentry from a backend worker, web server or browser client.

---

## Core Directives

1. **Every drop rule has a paired test.** A drop fixture and a keep fixture (the same text with a 5xx, an outage cause or a first-party frame). Every HTTP drop checks the status in every branch. Match the outermost exception, never a marker anywhere in the chain (`CancelledError` sits in the chain of every timeout).
2. **Never drop an outage class** (key or secret mismatch, webhook signature failure, storage or provider outage, timeout). Report at warning level with a rate-limited fingerprint.
3. **Initialise Sentry at import time**, in web and worker alike, never inside a worker's startup hook, so integrations wrap every job. Set `include_local_variables=False`, a low `max_value_length` and `max_breadcrumbs`, and scrub frame vars, breadcrumbs and exception values. Personal information must not reach Sentry or the log store.
4. **A raising `before_send` loses the event silently.** Guard the hook, return a fail-safe event rather than nothing, and bound the event size with the SDK's own wire encoder (non-ASCII text encodes larger than its UTF-8 length).
5. **A warning log is not reporting.** A handled failure reports, re-raises or carries a one-line reason. A failure that is logged and returned (for example a webhook route returning 400) never reaches Sentry at all.
6. **A delivery loss is an incident.** Usage Stats outcome `invalid` or `send_error` above zero is investigated; `network_error` and `rate_limited` above a set threshold are too. Never write "none surfaced in Sentry" without checking Usage Stats by outcome.
7. **Transactions are a second pipeline.** In the JavaScript SDK a transaction bypasses `beforeSend` and needs `beforeSendTransaction`. It carries the scope's breadcrumbs, `extra`, `tags` and `contexts`, span `http.query` and `url.full`, and `request.headers.Referer`, so a scrub covering only error events leaks on the sampled share of page loads. Probe against the real client, not a stub.
8. **A scrubber that edits its input in place makes a shared test fixture vacuous.** Build each fixture with a factory per call, and never pass one object to two configs or two calls. Fail closed by returning a new minimal event carrying a countable tag, not by deleting from the original.
9. **SDK process-global state leaks between tests.** Some integrations add to a global ignored-logger set once per process, so a test asserting that set is unchanged is order-dependent. Assert the absence of the names you must not ignore, and reset the current, isolation and global scopes with `set_client(None)` after closing the client, because a transportless init still leaves an active client.
10. **A derived roster cannot catch a deliberate reclassification** (for example an hour added to a minute-only cron). Pin per-job schedules in that job's own requirement, never in a roster test.

---

## Patterns to Follow

- Probe each SDK claim with a scratch script against the installed SDK version before writing it into a spec.
- Measure the real event size with the wire encoder against a budget below the ingest limit.
- Record the Usage Stats outcome table in any verification note that claims an event did or did not arrive.

## Patterns to Avoid

- Adding a filter without a keep fixture, or an outage class to an expected-noise list.
- Initialising Sentry inside `on_startup`.
- Turning frame locals back on, or raising the value length, without the size and privacy tests passing.

---

## Verification & Guardrails

- Run the size, privacy and filter tests, and the Usage Stats check (Settings, Stats, 14 days, group by outcome and reason), before calling a change done.
- Related: `rules/sentry-frontend-noise.md`, `rules/observability-and-error-management.md`, `rules/no-secret-masking.md`.
- Origin: a one October 2026 blind-spot review (events rejected as too large, job failures never reported, outage classes dropped) and the C527 to C530 review rounds that followed.
