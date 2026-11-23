# Every writer of a state goes through one helper with a guard test

Applies when an entity's state or stage is changed from more than one place (HandleDispute case status, 18 Nov 2026).

**Scope:** services, schedulers, API routes and scripts that set a status.

---

## Why this exists

An investigation of the case journey found six code paths that set the case status without the transition matrix (proposal, escalate route, SLA scheduler, outreach, intake and an unused escalation method). A history or graph built on one writer therefore had gaps, and the only record of the journey table (`case_process_metrics`) was never written at all.

## Core Directives

1. **One helper owns the write.** It records the history row, the audit activity and the new state in the caller's transaction.
2. **A guard test fails any other writer.** It scans for direct assignments with an allow-list that carries a reason per entry.
3. **Closed states are defined once.** Schedulers and routes derive "closed" from that one definition, never from a hand-written list of two statuses.
4. **A history table is append only** and is the source of any timeline, count or graph.
5. **Backfill is labelled** so history before the helper is not mistaken for recorded history.
