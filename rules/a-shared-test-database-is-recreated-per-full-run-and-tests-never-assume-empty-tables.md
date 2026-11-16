# A shared test database is recreated per full run, and tests never assume an empty table

Applies when several agents, sessions or waves run a test suite against one pinned database name.

**Scope:** all agents running backend tests; HandleDispute pins `handledispute_security_test` in `tests/conftest.py`.

---

## Why this exists

HandleDispute, 17 Nov 2026: after five waves of parallel test runs the pinned database held 53 stale PENDING jobs and about 15 600 audit rows. A test that claims "the next job" never reached its own row, and the audit export test failed on its 10 000 row limit. Neither was a code defect. A fresh database and data-derived loop bounds fixed both.

## Core Directives

1. **Recreate the database before a full run.** Rename the old one (`alter database x rename to x_stale_<date>`), create a fresh one, run `alembic upgrade head` and run the suite. Never drop a database you did not create; tell the owner the stale one exists.
2. **A test never assumes an empty table.** Derive loop bounds from a count, scope queries by your own ids, and use unique fixture values.
3. **Clean only your own rows.** Never truncate or delete rows you did not create, and never use a fixture that deletes a whole table.
4. **Do not change an assertion because the database is dirty.** Fix the test's isolation (bound, scope) and say so in the commit.
5. **A populated copy rehearses a migration:** `create database copy template stale`, downgrade one revision, upgrade, compare row counts, drop the copy.
6. **Read the exit line.** `pytest ... > log 2>&1; echo exit=$?`, then the summary line.
