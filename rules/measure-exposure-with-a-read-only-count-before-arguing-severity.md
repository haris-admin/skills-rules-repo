# Measure exposure with a read-only count before arguing severity

When a defect lets the wrong role do something costly, count whether it ever happened before debating how bad it is.

**Scope:** security and permission defects with a production data trail (audit rows, provider-call ledgers).

## Why this exists

AMLHive issue 482, 8 Nov 2026: AUDITOR users could start paid screenings through the API. A counts-only, read-only production script (audit rows by actor role and month, matching provider calls, plus the number of users who could sign in) showed zero such screenings. That turned an open-ended severity argument into a recorded fact and let the fix ship as an ordinary isolated hotfix.

## Core Directives

1. **Write the script, do not run it against production yourself.** The human authorises it in the current conversation and runs it.
2. **Read-only transaction, counts only.** No names, ids, emails, hashes, payloads or connection strings in output; query errors print the exception class only.
3. **Include controls** (counts for the permitted roles) so a zero is meaningful.
4. **Dry-run the script first** (stops before the remote call) and record the result verbatim in the issue file.
5. **A zero today is not a reason to skip the fix.** It sets urgency and the release shape, not whether to fix.
