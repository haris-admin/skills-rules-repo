# Optional reporting fields on a critical endpoint are parsed leniently

A field that only reports information (counts, a flag, diagnostics) must never be able to make a critical operation fail, and must not change the API contract.

**Scope:** adding an optional field to an existing endpoint whose job matters more than the report (closing a shift, taking a payment).

## Why this exists

Tap-Ease C83A, 15 Nov 2026. Haris asked the terminal to send, on shift close, a flag that a report would not be printed because it was too long, "an optional field ... backward compatible". The close route took no body at all, and callers such as the operator override and the automatic payout retry call the function directly with no HTTP request. A normal request model would have returned 422 on a bad value and could have blocked a driver from closing a shift.

## Core Directives

1. **Read the body by hand** and validate it with a small pure function that returns (value, nothing, or a fixed reason). Never raise from it.
2. **A bad value is ignored and logged once** with a fixed reason that does not echo the submitted value.
3. **Nothing is stored or returned** unless the owner asks: no new response field, no status change.
4. **Log after the operation has committed**, inside a guard, so a logging fault cannot fail a close that already succeeded, and a retry does not log twice.
5. **Keep direct callers working:** make the new request parameter optional.
6. **Test the contract:** the same status and the same response keys with and without the field, a repeat call, the old no-body call.

## Patterns to Avoid

- A strict model on a route that older clients call with no body.
- Echoing the rejected value into the log.
