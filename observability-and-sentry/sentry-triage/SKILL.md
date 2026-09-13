---
name: sentry-triage
description: Systematic protocol for triaging incoming Sentry issues, filtering 3rd-party noise, and resolving first-party regressions. Use when triaging new Sentry issues, classifying an error as third-party noise vs a real first-party defect, or deciding whether to log a production issue and write a regression test.
---

# Sentry Triage Protocol

## Classification Matrix
1. **Third-Party Extension Noise**: Browser extensions, ad blockers, translation tools → Add dropper in `sentry-event-policy`.
2. **Operational / Handled Errors**: User validation failures (400, 422) → Filter or downgrade log severity.
3. **First-Party Code Defects**: Unhandled TypeErrors, null references, broken state → Log production issue, write failing test, fix code.
4. **Infrastructure / Deploy Artifacts**: Stale chunk loads during deploys → Route to deployment mismatch policy.

