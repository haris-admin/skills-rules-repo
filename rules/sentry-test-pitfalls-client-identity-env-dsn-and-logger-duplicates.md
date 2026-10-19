# Sentry test pitfalls client identity env dsn and logger duplicates

Tests around the Sentry SDK must not compare no-op clients by identity, must clear the ambient DSN before a DSN-less init, and must expect a logger event beside an integration event.

**Scope:** every agent writing or reviewing tests that initialise or capture through sentry-sdk.

## Why this exists

Added 19 Oct 2026 (AMLHive C528 Red tests). Six worker tests failed for reasons that were test or spec defects, not code defects.

## Core Directives

1. **No identity check on a no-op client.** With no active client, `sentry_sdk.get_client()` returns a new `NonRecordingClient` each call, so `is before` never holds. Assert `isinstance` and `is_active() is False`.
2. **`sentry_sdk.init()` reads the environment.** A bare init picks up `SENTRY_DSN` loaded from `.env`, so a DSN-less client has a DSN. The test must clear the variable first.
3. **Integration plus logger gives two events.** arq's own error log (`arq.worker`) adds a second event beside the integration capture. Decide the logger ignore list deliberately, and note who owns that list.
4. **A classifier that needs worker startup state fails in a test that never starts the worker.** If a test expects a cause derived from startup context, the test must supply that context or the spec must say where else it comes from.

## Verification & Guardrails

- Prove a Sentry test non-vacuous by running it against the unmodified code and reading the actual event list, not only the count.
