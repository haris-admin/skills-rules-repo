# Supabase migrations: compare by name, probe objects, never `db push` blindly

Checking or applying SQL migration files against a Supabase project (production, staging or a workshop copy). Applies to any repo whose `supabase/migrations/*.sql` filenames do not equal the versions recorded in `supabase_migrations.schema_migrations`.

**Scope:** database release steps and read-only audits (Simplifii-OS, 5 Oct 2026).

---

## Why this exists

A comparison of 81 migration files against a project that had 105 recorded versions reported all 81 as "not applied", because migrations applied through the SQL editor or connector are recorded with the apply time, not the file prefix. Compared by name, only 17 were unrecorded, and probing the real objects showed 12 of those already existed, 3 were unused legacy backup tables, 2 were DRAFTs, and 2 were never to be run. Nothing needed applying. Running `supabase db push` would have tried to reapply everything.

## Core Directives

1. **Compare by name, not by version.** Strip the timestamp prefix from the file and match the name against `supabase_migrations.schema_migrations.name`.
2. **Then probe the objects.** For each unrecorded file, check the tables, columns, indexes, functions, triggers and buckets it creates (`information_schema`, `pg_proc`, `pg_indexes`, `storage.buckets`). A structure copied from another project has the objects without the ledger rows.
3. **Never `supabase db push`** where versions and prefixes differ. Apply one reviewed file at a time with the SQL editor or the connector's `apply_migration`, and verify afterwards from `information_schema` and row counts.
4. **Read first, with the management API.** `POST /v1/projects/{ref}/database/query` with a personal access token can run `select` statements. Use it for audits. Writes are a separate, explicit step.
5. **Do not run what is marked unsafe.** Skip `*_DRAFT*` files and any migration the team has ruled out (for example one with a hard-coded email bypass, or an integration that is switched off).
6. **Respect existing CHECK constraints.** A new failure or status code that the column's constraint does not allow makes the insert fail. Reuse an existing code or add a migration; do not invent a value in code.
7. **Production waits for the release word.** Apply additive migrations to production before the code that needs them, only on the owner's go, and record the applied names.
8. **Know the key types.** Legacy `anon` and `service_role` keys are JWTs (`eyJ...`); new `sb_publishable_` and `sb_secret_` keys are different and some server code that sends the key as a Bearer token does not accept them. A 401 on both the right and the wrong project means a stale or foreign key. Never print any of them.

---

## Patterns to Follow

```sql
select version, name from supabase_migrations.schema_migrations order by version;
select 1 from information_schema.columns where table_schema='public' and table_name='crisis_events' and column_name='alert_status';
```

## Patterns to Avoid

- "81 of 81 missing" from a version comparison.
- Applying a backfill or parity file just because its row is absent.
- Treating a copied project's missing ledger rows as missing schema.
