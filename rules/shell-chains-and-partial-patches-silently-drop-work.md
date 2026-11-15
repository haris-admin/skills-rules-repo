# Shell chains and partial patches silently drop work

Three small traps made a commit not happen, a file list not split, and half a change not move. Check the result after each.

**Scope:** any agent committing, patching or moving changes between worktrees from zsh.

## Why this exists

Tap-Ease, 15 and 16 Nov 2026. (1) `git add -A . ':!backend/.env'` printed a hint about an ignored path and returned an error, so the `&&` chain stopped and the production commit did not happen; the next push said "Everything up-to-date". (2) In zsh an unquoted `$FILES` is one word, so a `git diff -- $FILES` produced an empty patch. (3) A patch built from `git diff --cached` carried only the staged half of files marked `MM`; the unstaged half (comments and test names that cite the right change id) was left behind and found only in the closeout.

## Core Directives

1. **After every commit run `git log -1`** and compare the hash with what you expect before pushing.
2. **Do not exclude ignored paths in `git add`.** A gitignored file needs no exclusion.
3. **In zsh use an array** (`FILES=(a b)` and `"${FILES[@]}"`) or `${=VAR}`; check that a generated patch is not empty (`wc -l`).
4. **Moving changes between worktrees:** use `git diff HEAD` (staged and unstaged) or copy whole files, and compare each file with the destination afterwards.
5. **A worktree needs its own gitignored `.env`:** copy it for tests, never commit it, and delete the worktree (and the copy) when done.
6. **Do not chain a commit after a pipe to `tail`:** the exit code is `tail`'s.

## Patterns to Avoid

- Trusting "nothing printed" as success.
- Moving only the staged diff of a half-staged file.
