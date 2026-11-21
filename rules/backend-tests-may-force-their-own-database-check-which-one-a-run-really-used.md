# Backend tests may force their own database: check which one a run really used

A test suite whose conftest overwrites `DATABASE_URL` ignores the one you set. A run you believe is on a fresh scratch database may be on the shared one.

**Scope:** any agent running a backend suite on a machine that shares one local test database across worktrees and sessions.

---

## Core Directives

1. **Read the conftest first**: look for `os.environ.update` or a constant that pins the database URL before you trust an environment override.
2. **Prove the database**: print the URL the tests resolved (a one-line check at the top of the run) and look at that database after the run, not at the one you created.
3. **Never edit the shared conftest to point at a scratch database and leave it uncommitted**: it hides in the worktree and is easy to commit by accident. Add a documented override variable through a spec instead, or recreate the shared database (rename the old one, create fresh, migrate).
4. **Migrating a scratch database proves nothing about the run**: run the migration against the database the tests really use.

## Why this exists

**21 Nov 2026 (HandleDispute):** four full runs were started with `DATABASE_URL` set to fresh scratch databases and the migration run there, but the conftest pinned the tests to `handledispute_security_test`. Two runs started in parallel then contaminated each other (20 and 26 failures on unrelated tests, including a clean baseline) because they shared one database. Two other sessions had already patched their conftest to scratch names and left the edit uncommitted.
