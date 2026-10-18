# Verify which database the tests will touch before the first run (all agents)

Applies to any agent about to run a test suite, migration or seed in a repo whose `.env` or settings define a database URL.

## Why this exists

14 Oct 2026, Tap-Ease backend. The repo's `.env` set `DATABASE_URL` to `localhost:5435`. That port was an **SSM tunnel to the shared dev
EC2**, not a local database. The test suite's fixtures run the migration runner at session start and set up a pool per test, so a plain
`pytest` would have run against the shared dev database. Notes from an earlier session said the tunnel was on 5433; ports drift, and one
port number can be both a Docker container and a tunnel (`tapease-db-access`).

## Rules

1. **Print the target before the first run:** host, port and database name only, never the credentials. Parse the URL, do not `cat` the file.
2. **Find out what is listening there:** `lsof -nP -iTCP:<port> -sTCP:LISTEN`, and `ps aux | grep session-manager-plugin` for tunnels.
   A `session-manager-plugin` process means a remote database.
3. **Run tests through a wrapper** that sets an explicit disposable `TEST_DATABASE_URL` (a throwaway database inside a local container)
   and refuses the tunnel and production ports. Make the repo's conftest honour `TEST_DATABASE_URL` over `.env`.
4. **Mark tests that need no database** so the per-test pool and migrations are skipped, and put a guard at the top of every DB test that
   asserts the URL is not a tunnel or production port.
5. **Take the baseline in a clean `git worktree` of HEAD** on its own database, so your edits cannot affect it, and remove the worktree
   afterwards (`git worktree remove --force`, then `git worktree prune`).
6. **Compare failures by test id** between the baseline and your tree; a suite that was green stays green.

## Related

- Skills: `tapease-db-access`, `test-driven-development`
- Rules: `testing-guidelines.md`, `deploy-state-needs-independent-reads.md`
