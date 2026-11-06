# Renamed archive tables keep their foreign keys: rehearse downgrade and upgrade on real data

PostgreSQL keeps a renamed table's foreign keys, so a downgrade that archives data by renaming can block an earlier migration from dropping the parent. Rehearse the full cycle on a populated copy before every release with a migration.

**Scope:** Alembic (or any migration tool) on PostgreSQL where downgrades keep data in `*_downgrade_archive` tables.

---

## Core Directives

1. **Run the round trip**: `upgrade head`, `downgrade base`, `upgrade head` on a scratch database in a real test, not only the last migration.
2. **Rehearse on a populated copy before a release with a migration**: create the scratch database from a populated template, downgrade to the previous revision, upgrade again, compare row counts, drop the scratch database. State plainly that it is a rehearsal on test data, not on production data.
3. **Fix centrally**: when many migrations archive by rename, detach the archive tables' foreign keys in one place (an `on_version_apply` hook in `alembic/env.py` that records the dropped definitions and restores them on upgrade) rather than editing released migrations.
4. **New tables are additive**: ship the new migration as create-only with a clean-drop downgrade, no backfill, and reserve revision numbers other specs have claimed.

## Why this exists

**6 Nov 2026 (HandleDispute):** the scheduled migration job failed with `DependentObjectsStillExist` on `cardholder_sessions`; eight migrations archived tables that way. The hook fixed it, and the audit trail migration was rehearsed on a copy with 19,056 cases before release.
