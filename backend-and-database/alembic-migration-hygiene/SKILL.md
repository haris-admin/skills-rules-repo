---
name: alembic-migration-hygiene
description: Best practices for writing zero-downtime, reversible database migrations with SQLAlchemy and Alembic. Use when writing, reviewing, or running an Alembic migration — new column, constraint, native enum, or backfill — before merging it or applying it to a database.
---

# Alembic Migration Hygiene

## Standards
1. **Reversibility**: Every `upgrade()` must have a fully implemented, working `downgrade()`.
2. **Online Schema Changes**: Add columns as nullable first; backfill in chunks; add constraints subsequently.
3. **Package Isolation**: Prevent module namespace shadowing between local migration folders and third-party packages.
4. **Native Enums**: Create and register database-native enum types explicitly in migration scripts.
5. **Concurrent indexes on live tables**: `CREATE INDEX` on a large, write-heavy table (an audit log) takes a SHARE lock and
   blocks writes for the whole build. Use `op.create_index(..., postgresql_concurrently=True, if_not_exists=True)` inside
   `with op.get_context().autocommit_block():`. `if_not_exists` makes a re-run after a failed concurrent build safe.
6. **`autocommit_block()` needs Alembic to own the transaction**: if `env.py` executes anything on the connection before
   `context.configure()` (e.g. `SET lock_timeout`), SQLAlchemy 2.0 autobegins a transaction Alembic does not own, and
   `autocommit_block()` fails with `AssertionError: self._transaction is not None`. Call `connection.commit()` after those
   session-level `SET`s (they survive the commit). Prove it on real Postgres: upgrade from the production head, the full
   chain from an empty database, and a downgrade and re-upgrade.
7. **Run migration lints locally, not only in the deploy workflow**: a lint that only runs inside the deploy job is found by a
   failed production deploy (2026-09-24: 8 non-concurrent indexes across 3 migrations from another agent's lane reached
   the deploy gate because local suites never ran the lint).
