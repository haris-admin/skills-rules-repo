# Local runs never report to production Sentry or other production observability (all agents)

Applies to all local runs, tests, and debugging probes; default settings to non-production environments with no Sentry DSN to prevent leaking local events into production observability.

## Why this exists
**8 Nov 2026, Tap-Ease:** a review probe imported the app with local settings that said `environment=production` and a Sentry DSN set. Sentry reported "attempting to send 2 pending events". Production Sentry was already over quota (PI-012).

## Rules
1. Local and test settings default to a non-production environment with no DSN. A test asserts no Sentry init when the environment is local.
2. Until that is true, run probes with the DSN unset, and say in the report if an event may have been sent.
3. Check configuration with booleans (set or not), never print the DSN.
