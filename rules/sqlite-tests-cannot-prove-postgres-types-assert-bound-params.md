# SQLite tests cannot prove PostgreSQL type rules: assert bound parameter types (all agents)

Applies to any project whose unit tests run on SQLite (or any dialect other than production) while production runs PostgreSQL, whenever a change binds a value into raw SQL (`COALESCE`, `CASE`, comparisons, `UNION`).

## Why this exists

30 Oct 2026, Tap-Ease Lambda ETL, release 0.10.10. The Gold devices update bound an integer into `COALESCE(:terminal_prefix, terminal_prefix_clover)` where the column is text. PostgreSQL rejects `COALESCE(integer, character varying)`; SQLite accepts it. All 1018 tests passed, the release went live, and every device update in the fleet rolled back on every run for about 20 minutes while the log line "serial changed" repeated 168 times per run. It was caught only because a person asked "check that lambda is updated" and the second run logged the same 168 changes. Hotfix 0.10.11 bound the value as text.

## Core Directives

1. **Green on SQLite is not proof for PostgreSQL typing.** For every new or changed bound parameter in raw SQL, say which column type it meets in production.
2. **Assert the bound types in a test.** Spy on `session.execute` and assert each parameter that meets a typed column is the right Python type (for a text column: `str` or `None`). The assertion fails on SQLite for the right reason, which satisfies Red before Green.
3. **Cast or convert at the boundary, not in the SQL.** Convert the Python value (`str(x)`), or add an explicit `CAST(... AS text)` when the type cannot be controlled.
4. **After a release that writes data, prove persistence in the second run, not the first.** A write that is logged before it is executed (or a swallowed per-row error) looks identical to success in run one. Require: run one logs the change, run two logs none, and a read-only query shows the new value.
5. **Per-row errors need a visible home.** When a savepoint rollback hides a failure, the only trace may be a status column (`processed_comments`). Read it as part of verification.

## Patterns to Avoid

- Passing a number into `COALESCE` with a text column because "it works in the tests".
- Declaring a data-writing release verified from the first run's log lines alone.
- Verifying a deploy with a loose log filter; match the exact version field.
