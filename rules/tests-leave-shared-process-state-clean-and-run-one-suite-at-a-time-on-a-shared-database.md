# Tests leave shared process state clean, and one suite runs at a time on a shared test database

A new test that records a failure against an in-process limiter or lockout key can fail an older test later in the same run, and two agents running database tests together corrupt each other.

**Scope:** backend test suites with in-process singletons or one fixed test database.

## Why this exists

**23 Nov 2026 (HandleDispute):** a new login test recorded one failed secret attempt against the process wide lockout key; in a 4,000 test run `test_admin_login_with_secret_key` then answered 401. The test passed alone. Separately, the test database name is fixed in `conftest.py`, so a second implementer could not run backend tests while another did.

## Rules

1. A test that touches a shared singleton (limiter, lockout guard, snapshot) resets it in a `try/finally` or a fixture.
2. After writing a test, run it together with the older tests that share the singleton, not only alone, and run the wide family before committing.
3. Read the log's summary line and `exit=`, never a background notification, before saying a suite is green.
4. With one shared test database, one pytest process at a time. When a second implementer is added, give it only work that needs no database (script shim tests), or hand it the database for the whole run and stop running backend tests yourself.
5. Check a failing test on a clean tree (a second worktree at the base commit, never `git stash` in a shared checkout) before calling it pre-existing.
