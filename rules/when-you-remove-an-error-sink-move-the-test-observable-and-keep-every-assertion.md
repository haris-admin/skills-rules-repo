# When you remove an error sink, move the tests' observable and keep every assertion

If a requirement removes where errors go (for example backend Sentry), the failures and alerts must still be raised, now somewhere else, and the tests must still prove it.

**Scope:** any change that disables or replaces an observability sink (Sentry, a metrics client, an alert channel).

## Why this exists

Tap-Ease C84, 15 Nov 2026. Backend Sentry was turned off to save the plan's event quota. The first version of the change rewrote the failure-reporting tests to assert "Sentry is not called" and silently dropped the checks for payment method, outcome, diagnostic code and serial that the Sentry tags used to carry. Fifteen integration tests that patched `sentry_sdk` were not touched and failed at setup. The full suite caught them.

## Core Directives

1. **Get the owner's decision first** (the requirement changed, so tests may change with it) and record it verbatim in the spec.
2. **Pick the new observable** (the log line at WARNING or ERROR with the same ids) and make every old assertion check it. Do not replace a positive check with "nothing was sent".
3. **Add one negative check** that the old sink is gone (`not hasattr(module, "sentry_sdk")`, no SDK init).
4. **Run the whole suite**, not only the files you edited: other tests may patch the sink by name.
5. **Remove the unused imports** the change leaves behind in test files, or the lint gate fails.

## Patterns to Avoid

- Deleting assertions together with the code they exercised.
- Declaring done after running only the unit tests of the touched module.
