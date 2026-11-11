# In a shared checkout, another tool may be editing it: look before you switch, and never discard (all agents, all repos)

A working tree that was clean a few minutes ago can fill with another tool's uncommitted work (Antigravity, Codex, an IDE). Never switch branches over it, stash it, reset it or clean it. Branch from where you are and commit what is there only when the owner asks.

## Why this exists
**11 Nov 2026, Tap-Ease POS repo:** a `git checkout main` was refused because 52 files had changed since the last check. Antigravity was open on the repo and had written three new OpenSpec changes and edits across about 40 files. A forced switch would have destroyed that work. The same session had earlier switched this checkout to the release branch while it was clean, which is how the other tool came to build on top of it.

## Rules
1. Before any branch switch, commit, reset or clean in a shared checkout, run `git status --short` and read it. Files you did not touch are someone else's work.
2. A checkout that git refuses is a warning, not an obstacle: do not stash, force or discard to get past it.
3. To move a branch name without touching the tree, use `git branch -f <name> <commit>` (only for a pure fast-forward and only when no worktree has that branch checked out).
4. To save another tool's work, create a new branch from the current commit (`git switch -c ...`), which carries the changes, and commit per ticket there, labelled work in progress with the true test status. Do this only when the owner asks.
5. Do release builds in a separate worktree off a named commit, so another tool's edits cannot enter the build. Say in the report which commit the build came from.
6. Check for running editors or agents (`ps`) when files change that you did not edit.
