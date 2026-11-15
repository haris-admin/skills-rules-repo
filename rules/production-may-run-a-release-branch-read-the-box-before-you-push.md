# Production may run a release branch, not main: read the box before you push

Before any production deploy, find out which branch and commit production is really running, and build the release from that, not from the default branch.

**Scope:** any agent preparing a deploy where production is updated by a script on the host that pulls a named branch (Tap-Ease POS backend and similar).

## Why this exists

Tap-Ease POS backend, 15 and 16 Nov 2026. Haris asked for the Sentry change in production "in version 1.12". `main` was the 1.1.13 start commit and `dev` carried C77 (a database migration), the C83 print limit and C83A, none of which were approved for production. A live `/health` read showed `1.1.12.c40a`, and a read-only look at the box showed branch `release/1.1.12-c40a`. Pushing `main` would have shipped the wrong code. A narrow branch (the live branch plus only the approved commits) shipped cleanly twice (C84, C85), with the full suite green on that exact tree.

## Core Directives

1. **Read production first, independently:** the public `/health` version and, read-only over SSM, `git rev-parse --abbrev-ref HEAD`, the HEAD commit, whether the tree is dirty, and the container status.
2. **Name the branch the host pulls.** If it is not `main`, a push to `main` is not the deploy, and may be a different, larger change than the owner asked for.
3. **Build a narrow release branch:** the live branch plus only the approved commits (cherry-pick, resolve conflicts by reading both sides), run the full suite on that exact tree, push it as a fast-forward, then deploy with the sanctioned script.
4. **List the commits between the live branch and the release** and tell the owner before pushing. Say plainly that the deploy restarts the live service.
5. **Verify afterwards from outside and on the box:** `/health` version and flags, the box HEAD equals the pushed commit, an unauthenticated protected route still answers 401, and log counts (not content) for errors.
6. **Record the reconciliation debt:** the same change now exists on two branches. Put it in the register so the next merge happens once.

## Patterns to Avoid

- Assuming production tracks `main`.
- Reading "version X" in the owner's request as the default branch's current version.
- Deploying a change that carries a database migration the owner did not approve.
