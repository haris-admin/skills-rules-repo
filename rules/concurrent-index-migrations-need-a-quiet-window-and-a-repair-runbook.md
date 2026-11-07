# Concurrent-index migrations need a quiet window and a repair runbook

A migration that builds indexes CONCURRENTLY, in autocommit blocks, can fail half-way and leave a partial schema. Plan for it before the deploy.

**Scope:** any migration with `CREATE INDEX CONCURRENTLY`, `NOT VALID` then `VALIDATE`, or other multi-step DDL, run by an automatic deploy.

## Why this exists

AMLHive C543 (migration a248), 8 Nov 2026. `CREATE INDEX CONCURRENTLY` waits for every older transaction in the database, and the migration role had `lock_timeout` of 5 seconds. Reproduced: one idle-in-transaction session open for 25 seconds made the deploy fail between the column add and the constraints, leaving the column committed and an INVALID index behind. The rerun was refused by the catalog preflight (correct), auto-rollback restored the old image, and the next deploy stayed refused until an operator repaired the database.

## Core Directives

1. **Write a catalog preflight** that refuses a partial or wrong-shaped state before any DDL, with a fixed marker (`<CHANGE> MIGRATION REPAIR REQUIRED stage=<token> object=<name>`) and no chained raw duplicate-object error.
2. **Write the repair SQL into the release runbook and test it** on a disposable copy: drop the invalid indexes concurrently, drop the added column, then redeploy once.
3. **Pre-deploy check, read-only, counts only:** no transaction older than the lock timeout, including idle-in-transaction sessions. Deploy in a quiet window.
4. **Measure the lock window** on a synthetic table of production scale (rows and bytes) and record it; accept it explicitly or order a fully online version.
5. **Take a manual database snapshot first**, and plan rollback by image tag, not by a production downgrade (make the downgrade privileged and lock-protected).
6. **State the old image's compatibility with the new schema** (nullable column, nothing new NOT NULL) so rollback is safe.
