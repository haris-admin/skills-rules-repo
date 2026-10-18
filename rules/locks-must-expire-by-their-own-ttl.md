# A lock must expire by its own TTL (all agents, all repos)

Applies to any job lock stored in a database or key-value store (DynamoDB, Redis, a Postgres row) that guards a scheduled
function, cron or worker.

## Why this exists

14 Oct 2026, Tap-Ease Clover sync Lambda. The lock was written with `ConditionExpression="attribute_not_exists(lockID)"` and a
`ttl` attribute, but the acquire step never looked at the TTL. It relied on DynamoDB's background TTL sweeper to delete the
item. A run that hit the 600 second function timeout was killed before its `finally` block, so the lock stayed. The lock's TTL
expired at the moment the run was killed, yet every run for the next ~18 minutes logged "Previous sync job is still running" and
did nothing, until the sweeper happened to remove the item. The sweeper is not a timer: deletion can lag expiry (historically up
to 48 hours; check the current documentation before relying on any figure).

## Rules

1. **Acquire with the TTL in the condition:** `attribute_not_exists(lockID) OR #ttl < :now`. Never depend on a sweeper to
   free a lock.
2. **Assume the holder can die without releasing.** Timeouts, out-of-memory kills and hard deploys skip `finally`. Set the lock TTL
   above the function's maximum runtime and the function timeout below it, or heartbeat the lock.
3. **A skipped run is a signal.** Log it at WARNING with the lock's age, and alert after N consecutive skips.
4. **Test with a fake clock:** an expired lock is taken over, a live lock is respected, and two concurrent acquires give exactly one winner.
5. **Do not delete a lock by hand without a condition.** Use `delete-item` with `--condition-expression "#ttl < :now"`, so a live
   lock is never removed. If the condition fails, the lock is live or already gone.

## Related

- Rules: `integration-config-change-verify-and-rollback.md`, `deploy-state-needs-independent-reads.md`
