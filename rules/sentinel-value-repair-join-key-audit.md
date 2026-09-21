# Sentinel-value data repairs must audit every table that stores or joins on the column, not just the one the symptom touched

A repair that clears a sentinel value (`'unknown'`, `NULL`, a placeholder ID) in one table but leaves
it in a sibling table that joins on the same logical value silently breaks any later code that relies
on that join matching — with no error, just permanent exclusion from whatever the join was gating.

**Scope:** All agents. Applies whenever a data repair, backfill, or migration corrects a sentinel or
placeholder value that other tables also store a copy of, or that anything joins/filters on.

---

## Core Directives

1. **Before writing a repair, grep every model/table for the same column name** (or the same logical
   value under a different column name) across the whole codebase — not just the table the bug
   report or symptom happened to surface. A denormalized value (the same merchant ID, customer ID,
   status, etc. copied into several tables) is repaired in *all* of its homes in the same pass, or
   the gap is documented as a known follow-up, never left implicit.
2. **Check what joins or filters on that column**, not just what selects it. A `SELECT` reading a
   stale value degrades a query's output; a `JOIN`/`WHERE` condition on a stale value silently
   excludes rows from matching at all — often the more dangerous failure, because nothing errors and
   nothing looks obviously wrong downstream.
3. **When a partial repair is later found**, the newly-discovered gap is a *by-product* of the same
   sentinel value, not a new, unrelated bug — cross-reference the original repair's issue doc rather
   than writing up root cause from scratch.
4. **Sizing the gap**: once a further-along data quality pass fixed the "easy" tables, don't assume
   a downstream reconciliation job aimed at that data is now clean. Re-measure the actual backlog
   size against the *table nothing has touched yet* directly — it is often bigger than the original
   fix's scope suggested, because the original fix was scoped to whatever tables the symptom made
   visible.

---

## Patterns to Follow

```sql
-- Before considering a merchant_id_clover = 'unknown' repair "done", check every table:
SELECT table_name FROM information_schema.columns WHERE column_name = 'merchant_id_clover';
-- ...then confirm the repair was applied to ALL of them, or explicitly scope + document which
-- ones were intentionally left for a follow-up.
```

## Patterns to Avoid

```text
Repair silver_transactions_payments.merchant_id_clover and bronze_payments.merchant_id_clover,
declare the "unknown merchant" incident resolved, and never check bronze_transactions --
which a later, unrelated reconciliation job joins on. The join silently excludes every affected
row from repair, forever, with no error anywhere.
```

---

## Worked incident

`portal_backend_lambda_eventbridge`, 2026-09-20/21: a historical `merchant_id_clover = 'unknown'`
batch (Feb-Mar 2026) was repaired in `silver_transactions_payments` and `bronze_payments`, and the
incident was treated as closed. A newer Silver self-healing reconciliation
(`_reconcile_thin_payments`) added later joined `bronze_transactions` to `silver_transactions_payments`
on exact `merchant_id_clover` equality — `bronze_transactions` had never been touched by the original
repair, so **9,743 historical rows** were silently excluded from a reconciliation that would
otherwise have fixed them, discovered only because 1,028 Gold rows still showed a blank `card_mid`
weeks later. 9,651 of those 9,743 had their real merchant recoverable from the already-repaired
sibling tables (fixed by writing the value back, not fabricating one); 92 had no recoverable value
anywhere and needed an explicit human decision (the existing `DEFAULT_MERCHANT_ID` fallback) rather
than a guess. Full write-up: `2026-09-20_bronze_transactions_unknown_merchant_blocks_reconciliation.md`.

---

## Verification & Guardrails

- Before declaring a sentinel-value repair complete, run the `information_schema.columns` grep above
  and list every table found, with the repair status of each (fixed / not applicable / intentionally
  deferred with a reason).
- See the `prod-issue-management` skill's "stuck vs. slow vs. actually broken" section for how to
  diagnose whether a downstream job that depends on the repaired value is still catching up on a
  now-larger-than-expected backlog vs. genuinely broken.
