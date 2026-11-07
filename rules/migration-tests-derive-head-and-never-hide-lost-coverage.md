# Migration tests derive the head and never hide lost coverage

A migration-chain test must not pin today's head, and a skip must not hide a coverage loss.

**Scope:** every Alembic (or similar) migration test, and any test whose precondition changes when a later migration lands.

## Why this exists

AMLHive, 8 Nov 2026 (C505 EP-15 after C543's a248). The test asserted `current == ["a247"]`, so the day a248 existed it could only skip, and the a247 down and up round trip lost its only coverage while the suite stayed green.

## Core Directives

1. **Assert a single head, assert the parent link (`a246 -> a247`), and compare the applied revision to `heads` read at run time.** Never a literal head.
2. **If the round trip cannot run once later revisions exist, run it through the privileged role the later downgrade needs** (here a SUPERUSER admin URL), downgrade to the parent, assert, then upgrade back to head in `finally`.
3. **Skip only for a named missing precondition** (admin URL unset, ledger rows present) with an explicit message. A supplied but unprivileged fixture fails, it does not skip.
4. **A skip is not a pass.** A closeout run lists every environment variable a skipped test needs and runs with all of them set, with zero skips.
5. **Prove it:** make the downgrade a no-op in a scratch copy and confirm the test fails; unset the admin URL and confirm the skip message.

## Anti-patterns

- `assert current == ["a247"]` after a later migration exists.
- A bare `pytest.skip` with no reason that names the missing precondition.
