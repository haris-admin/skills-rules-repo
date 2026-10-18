# Building the Clover OAuth broker: lessons (14 Oct 2026)

Milestones M1 (config, crypto, migration), M2 (broker, row lock), M3 (callback, state store), M7 (merchant key check). Full suite on the final
tree: 3061 passed, 0 failed, against a clean baseline of 2784 passed, 0 failed.

## Process that worked

- **Spec first, decisions verbatim.** Every question to the product owner was a structured question and its answer was recorded word for word
  in `design.md` (decisions 1 to 35), with an append-only `CLAUDE_FEEDBACK.md`. A requirement change was recorded as a superseding entry.
- **Stub, then RED, then GREEN.** A stub module that raises `NotImplementedError` makes the first run fail on behaviour, not on an import error.
  Passing-at-RED tests were listed and justified (guards true by construction).
- **Mutation pass after GREEN** (`rules/prove-new-security-tests-bite-with-mutations.md`) found three real test gaps.
- **Real database where it matters.** The per-merchant `SELECT ... FOR UPDATE` lock, the `DELETE ... RETURNING` single-use state and the
  rollback-before-raise ordering were each tested against a local Postgres, with two service instances sharing one database.
- **One baseline in a clean worktree**, one run on the final tree, compared by test id.

## Things that surprised

- The repo's `.env` pointed the tests at an SSM tunnel to the shared dev DB (`rules/verify-test-database-target-before-first-run.md`).
- FastAPI 0.141 keeps included routers as lazy objects: `app.routes` does not list them. Check `app.openapi()["paths"]` instead.
- The app's trace middleware wrote query parameters to the API-call log and to `session_logs`; uvicorn's access log printed them too
  (`rules/secrets-in-query-strings-never-logged.md`).
- A global security-headers middleware overwrote a route's own `Referrer-Policy`; the fix is "keep one the route already set".
- A raise inside `async with conn.transaction()` rolls the status write back, so commit `needs_reauth` first and raise after leaving the lock.
- A refresh token is single use: if saving the new pair fails, do not mark the merchant `needs_reauth`; the old token may still work as a
  recovery token for up to two weeks.
- `docker restart` does not re-read a compose `env_file`; recreate the container. `docker exec` needs `-i` to read a script from stdin, and a
  script run by path needs `PYTHONPATH` set to the app directory.
- Build SSM `--parameters` with `python3 -c 'import json...'` from a file; a shell that expands `$(...)` inside a quoted string runs it locally.
