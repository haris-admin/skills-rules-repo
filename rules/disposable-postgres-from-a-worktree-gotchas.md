# Disposable Postgres from a git worktree: gotchas

Building a throwaway PG17 for integration tests from a worktree has traps that make tests fail or pass for the wrong reason.

**Scope:** any agent running `-m integration` tests on a disposable database from a git worktree.

## Why this exists

AMLHive C543 and C505, 8 Nov 2026. A setup script with relative paths migrated the main checkout's revisions instead of the worktree's; an empty `AWS_PROFILE=` made botocore raise inside the migration subprocess and 14 tests failed for no code reason; the downgrade under test refused on a database that already held one ledger row.

## Core Directives

1. **Point the setup at the worktree's `backend/` explicitly** (a copy of the script is fine) and print the applied revision after the build.
2. **Unset `AWS_PROFILE`, never set it to an empty string.** Pass dummy keys and `AWS_EC2_METADATA_DISABLED=true`; do not redirect credential files.
3. **Use the CI role split:** restricted `amlhive_app`, non-superuser migrator, and a disposable SUPERUSER as the admin URL for privileged downgrades.
4. **Rebuild the container fresh before each full run**, on a port nobody else uses, and remove only your own container afterwards. Other containers belong to other projects.
5. **Zero skips is the bar.** Export every variable a skipped test needs before calling a lane green.
6. **Scratch copies come from `git archive` with every `.env*` deleted** (assert a find count of 0).
7. **A new worktree has no gitignored `.env`.** Without it settings validation fails and a full run shows hundreds of false failures. Copy the project's `backend/.env`, set `DATABASE_URL` and `TEST_DATABASE_URL` to the disposable database, blank `SENTRY_DSN`, never print the file, and delete the copy with the worktree (Tap-Ease POS, 15 Nov 2026: 204 false failures until the file was copied; 1,454 passed after).
8. **Never stop at the first failure (`-x`).** Read every failure, then check each on the clean base commit.
