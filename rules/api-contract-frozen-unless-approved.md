# API contract is frozen unless approved (all agents, all repos)

Applies to any change to an existing HTTP route in any repository.

## Why this exists

**26 Oct 2026, Tap-Ease RCA0046:** while making provider errors clearer, the first design also changed HTTP status
codes (a provider refusal passed through as 422, provider 401/403/5xx turned into 502 on other routes). Haris stopped it:
"Don't change the contract. Keep the contract the same."

## Rules

1. The HTTP status code and the response fields of an existing route do not change as a side effect of a fix, a refactor
   or a message improvement. Message text, logging and documentation may change.
2. If a fix seems to need a status or field change, propose it with the reason and the clients affected, and wait for approval.
3. Pin the existing status in a test before changing the message. A test that asserts only text lets a status change slip through.
4. Known risks you notice but must leave alone (for example a provider 401 reaching a frontend as a 401) are written down
   as open items, not fixed silently.

## How to apply

Find each call site, keep its current status expression (a small `legacy_status` helper kept every route's old status
in Tap-Ease), and list in the PR what was deliberately left unchanged.
