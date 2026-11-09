# An acceptance check must exercise the trigger, not a quiet run (all agents)

Applies when a requirement says "after change X, no error Y in one run" or "verify Z after the permission, config or credential change".

## Why this exists

Tap-Ease, 9 Nov 2026. Lambda 0.10.14 had requirement 6.2: after the Clover app permissions are removed, one full run must log no 401 or 403. It passed. It still missed that `expand=metadata` is refused for an OAuth token, because the 403 only happens when a payment of an OAuth merchant is expanded, and no such payment was in that run. The same fault surfaced two days later on the first real payments of two new terminals.

## Rule

1. Write the acceptance check as an action: "fetch one payment of an OAuth merchant with every field and get 200", not "see no errors in a run".
2. A quiet run proves nothing unless the log or database shows the trigger occurred in that window (a payment, a refund, a login).
3. After a permission or credential change, test each call with the real credential on a canary, GET only, printing status codes and never the secret.
4. Record in the spec which trigger the check covers and which it does not.

## How to apply

Reword any "no 401 or 403 in one run" criterion into a named call plus an expected status. Related: `oauth-token-expanded-fields-need-every-permission.md`, `a-log-search-proves-absence-only-for-the-window-it-covers.md`, `release-claims-and-spec-ticks-need-evidence.md`.
