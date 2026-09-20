---
name: prod-issue-management
description: Maintain a unified global production issue register with structured investigation templates and verification evidence. Use when logging a new production defect, writing up root-cause analysis for a bug, recording the fix and verification evidence for a resolved production issue, or when a user reports a deployed fix "still isn't working" / "didn't work" and you need to tell a broken fix apart from a self-healing job that's still catching up on a backlog.
---

# Production Issue Management

## Issue Document Template
Each defect document (`issue-NNN-<slug>.md`) must contain:
1. **Header**: ID, Layer (Frontend/Backend/Infra), Severity (P1/P2/P3), Status (Investigating/In Progress/Resolved).
2. **Sentry Event / Trace**: Timestamp, route, error message, stack trace.
3. **Root Cause Analysis**: Why the issue occurred and why automated tests didn't catch it previously.
4. **Fix & Prevention**: Code changes, regression tests added, and standing rules updated.
5. **Verification Evidence**: Test commands and logs demonstrating resolution.

## Long-running incidents: one doc, numbered sections — not a new file per check-in

When an incident stays open across multiple sessions (root cause unconfirmed,
a fix is deployed but needs hours/days to fully take effect, or the user
keeps coming back to re-check), keep it as **one file** and append dated,
numbered sections (`## 10. ...`, `## 11. ...`) chronologically rather than
opening a new issue doc per follow-up. Each new section states what was
re-checked, what changed since the last section, and what's still open. This
kept `2026-09-20_extended_payload_race_recurrence.md` (portal_backend_lambda_eventbridge)
coherent across a same-day root-cause investigation, a fix, a live-verification
gap found in the fix, a generalized fix, and two follow-up "did it actually
work" checks hours apart — a reader can follow the whole arc in one place
instead of hunting across files with the numbering scheme from `prod-issue-numbering`.

## Diagnosing "the fix still isn't working" — stuck vs. slow vs. actually broken

A user reporting a deployed fix "isn't working" is not the same as the fix
being wrong. Before concluding the code is broken, check these three things
in order, against the live system, not just the user's report:

1. **Does the source of truth already have the correct data?** If the fix is
   supposed to propagate a value from A to B (e.g. a corrected Silver-layer
   field that should flow into a Gold-layer reconciliation), check A directly.
   If A is already correct, the fix's *logic* is not the problem — go to (2).
2. **Is the process actually advancing?** Take two point-in-time measurements
   of the remaining backlog (or a "frontier" marker like the lowest unfixed
   row ID) a few minutes apart. A shrinking backlog / advancing frontier means
   the fix is running and working, just not finished. A flat backlog with no
   forward motion means it's actually stuck — that's a real bug.
3. **What's the ETA from backlog ÷ throughput?** Once you've confirmed it's
   advancing, size the total backlog and the per-cycle throughput (batch size
   × cycles per hour) to give a concrete "clears in ~N hours" answer instead
   of a vague "give it time." If the backlog is large relative to how the
   original bug report was scoped, say so — undercounting the backlog size is
   itself a finding worth writing up, not just the ETA.

Report back with the measured numbers (backlog size, rows fixed per interval,
ETA), not just a restated assumption that "it should be working." This
sequence caught a real case where step 1 and 2 both checked out clean, and
the actual answer was "the fix is correct, the backlog was 36,187 rows against
a 500-row/cycle throughput, wait ~6 hours" rather than a code defect —
confirmed by re-measuring hours later and seeing the backlog shrink and the
frontier advance exactly as predicted (`2026-09-20_extended_payload_race_recurrence.md`
§11–§12, portal_backend_lambda_eventbridge).

See `tapease-db-access` for the DB-connection and write-SQL-validation
mechanics used to do this kind of live check safely against a
SELECT-only production connection.

