# A wait-then-degrade design must surface its first failure (all agents)

Applies when a pipeline waits for an enrichment, retries for a window, or defers a record, and after the window writes a degraded result instead of failing.

## Why this exists

Tap-Ease, 9 Nov 2026 (Lambda 0.10.14 to 0.10.15). Silver defers a payment while its extended payload is missing and, after `EXTENDED_WAIT_MAX_AGE_SECONDS` (3600 s), writes a thin row so payouts are never blocked. A Clover 403 on the extended fetch meant every payment of a newly approved OAuth merchant waited an hour and then lost its payment method, card type and order total. The money was right, so nothing alarmed. The error was logged by a different logger from the list fetches, was not counted as a fetch failure, and appeared in no run summary. A person noticing a missing $1 payment found it, about an hour in.

## Rule

1. A wait, retry or deferral window is a hiding place. The first failure inside it must be visible at once: one WARNING per merchant and record with the status, a count in the run summary, and the same in the alert email.
2. Degraded output must say it is degraded: a status or comment on the row, not a quiet blank.
3. State the window in the spec ("an extended fetch error is visible within one run, the row degrades after 3600 s") and test both halves.
4. Never log a token or a response body to achieve this.

## How to apply

When reviewing a design with "retry later" or "defer until", ask what a person sees in the first five minutes if the dependency is refused. If the answer is nothing, the design is incomplete. Related: skill `honest-failure`, `a-log-search-proves-absence-only-for-the-window-it-covers.md`.
