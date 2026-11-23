# A retired or unconfirmed payment needs a follow-up check and an alarm (all payment projects)

Applies to any system where a client reports a payment outcome that the server cannot prove (retired recovery, timeout, unknown, inconclusive).

## Why this exists

Tap-Ease POS, 21 Nov 2026 (PI-016). In 24 hours of production logs 27 trips ended with `recovery_retired` (the terminal could not find the card payment). 14 were paid
later, 7 were cancelled, 6 had no final event, and the backend stored each retirement exactly as reported. Nothing asked Clover whether the card was charged, nothing flagged
the trip, there was no alarm, and every retirement carried `reason=None`. It was found only by a manual log search. Three trips were retired together within two seconds after the
app lost its session (two recovery-status calls were rejected with 401 before that).

## Rule

1. An outcome the server cannot prove (retired, timed out, inconclusive) is "unresolved", never "failed" and never "paid". Record it as unresolved with a reason.
2. Every unresolved payment gets a scheduled check that lists it with terminal, driver, amount and age, and a defined way to resolve it against the provider.
3. Alarm on the count of unresolved payments older than a stated time. A manual log search is not monitoring.
4. Evidence reports (recovery status, observations) must still be accepted or logged with context when the client token has expired. Losing them in the uncertain window is a defect.
5. Never write "no customer was charged" from logs. Say what was checked and ask for the database and provider check.
6. Do not fix this by changing an existing route's status codes. The API contract is frozen unless approved (`api-contract-frozen-unless-approved.md`).

## How to apply

Tell the owner the gap and add it to the backlog first (`requirements-backlog-first`). Related: `a-log-search-proves-absence-only-for-the-window-it-covers.md`,
`regression-tests-at-the-layer-where-the-bug-lives.md`.
