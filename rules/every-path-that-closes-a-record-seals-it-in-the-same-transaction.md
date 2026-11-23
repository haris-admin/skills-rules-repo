# Every path that closes a record writes its sealed record in the same transaction

When closing a case or document also produces an immutable sealed record, status change, timeline row, audit entry and the sealed record commit together or not at all, on every route, job and admin tool.

**Scope:** backend services with a state machine and a tamper evident record (disputes, filings, approvals).

## Why this exists

**23 Nov 2026 (HandleDispute, specs 05a and 05b):** the sealed Case Resolution Record was written in a second transaction after the close, so a failed seal left a closed case with no record (the issuer lookup found nothing). Five concurrent closes all succeeded because the read was unlocked. After the first fix, a blind review found three more close paths that bypassed it (admin transition, a customer's escalate answer, a manual escalate that wrote the status directly), and a scan that shared one session rolled back an earlier case's notice when a later case failed.

## Rules

1. The state machine reads the row `FOR UPDATE` (`populate_existing` when the object may be loaded), flushes the caller's pending changes first, and seals inside the same commit; on any failure roll back and re-raise.
2. Give the state machine default seals for every closing state; a state that needs data it cannot know (a resolution type and amount) has no default and is refused on the generic route.
3. Send notices only after the commit.
4. A scan over many items commits each item before the next, so one failure rolls back only itself; raise one alert per scan with the exception type and the count, never case data.
5. Set `resolved_at` (and similar fields) inside the locked transition, never before it and never restored from a value read before the lock.
6. Test each path: success commits once; a failing seal leaves status, timeline, activity and records unchanged; two concurrent closes give one winner; an earlier item survives a later failure.
