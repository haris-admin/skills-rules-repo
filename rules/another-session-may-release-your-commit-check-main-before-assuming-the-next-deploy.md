# Another session may release your commit: check main before assuming the next deploy

Applies after any push to a branch that a manual deploy workflow builds from, when more than one session or agent works in the repository.

**Scope:** all agents; HandleDispute (push to `main` does not deploy, the owner starts the workflow).

---

## Why this exists

HandleDispute, 16 Nov 2026: a ClamAV fix was pushed to `main` as release 0.270.2 and the agent waited for the owner to start the deploy. Another session had built release 0.270.03 on top of it and deployed; the fix went live inside that release. The live check found it, not the plan. The same session left the shared checkout on its own release branch.

## Core Directives

1. **After a push, fetch and read:** `git fetch`, `git log origin/main --oneline -8` and `gh run list --branch main`. Say what is actually at the tip and what ran.
2. **Verify the live version from outside** (`/health`, `/health/ready`, a route that must answer 401) before saying a release is or is not live.
3. **A version label is part of the release.** If another session's version breaks the project's format rule, report it; do not "fix" it with an unrequested release.
4. **Work in your own worktree.** Do not switch the shared checkout's branch; if you find it on another session's branch, leave it until the owner asks, and report it.
5. **Check ancestry before deleting a branch:** `git merge-base --is-ancestor <branch> dev`.
