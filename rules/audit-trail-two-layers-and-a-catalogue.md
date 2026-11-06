# Audit trail: sealed ledger plus a customer-facing activity table, with a catalogue and coverage guards

A tamper-evident ledger records everything; a separate activity table, written in the same transaction, gives each audience its own safe view. A catalogue defines every activity and guards enforce coverage.

**Scope:** products that must show admins, merchants and customers an audit trail (privacy-sensitive, multi-party).

---

## Core Directives

1. **Two layers**: keep the hash-chained append-only ledger unchanged; add an append-only activity table linked to it, with scope columns (case, merchant, cardholder) and a bounded safe summary. Never join free-form ledger ids to scope a view.
2. **Catalogue in code**: stable code, stage, audiences, customer-safe label, outcomes. Codes are appended, never renamed; a snapshot file and a prefix-stable test enforce it; an AST guard fails on any audit write with an unregistered code.
3. **Coverage guard**: a test walks every mutating route and fails unless the route writes a catalogued activity or is on a written exemption list with a reason; every stage must have a writer.
4. **Per-audience schemas**: separate response models with `extra=forbid`; privacy tests over every catalogue entry (a merchant never sees a cardholder identifier; customers never see hashes, sequence numbers, correlation ids or other parties' ids).
5. **Write refusals too**: use an isolated transaction for denials so a rolled-back request still leaves a row; never store attempted secrets or free text.
6. **Audit viewing and exporting**: each admin view and export writes a row; neutralise spreadsheet formula injection in CSV; provide a verify route that recomputes the chain, with a cap and a rate limit.
7. **A flag hides only the customer views**: never ingestion, retention, verification or admin access.

## Why this exists

**6 Nov 2026 (HandleDispute, OpenSpec 31a to 31d):** the earlier ledger had free-form action codes, no list endpoint and sample data in the merchant screen. The rebuild produced 96 catalogued activities, 74 covered routes, and 541 data-driven privacy cases.
