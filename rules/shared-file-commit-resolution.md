# Shared-file commit resolution — a file that is both yours and another session's

**Scope:** every agent, every commit. Companion to
`docs/agent_rules/git-commit-hygiene-shared-worktree.md`, which governs *what gets committed*.
This rule governs the one case that rule could not answer.

## Why this exists

Added 12 Aug 2026 (C405). `git-commit-hygiene-shared-worktree.md` rule 3 says: unfamiliar
staged/modified files belong to another session — leave them alone. That works when a file is
*entirely* someone else's. It gives no answer to the case that actually recurs:

> **A file you legitimately must edit that already contains another session's uncommitted changes.**

C405 hit this on `CLAUDE.md`. The change needed to update the skills-catalog row and the
shared-pointer list. The same file already held another session's in-flight vendor-sovereignty rule
rows. Leaving the file alone meant not doing the work. Committing the file meant sweeping their
unfinished work into a commit describing something else — and onto `dev`.

Both obvious moves are wrong. That is why this is its own rule.

## Update 6 Oct 2026: stage only your own hunks (preferred)

Interactive `git add -p` is unavailable, but a non-interactive equivalent works and is now preferred:
`git diff -U0 -- <file>`, keep only your hunks, `git apply --cached --unidiff-zero <mine.diff>`,
`git diff --cached --stat`, then `git commit` **without a pathspec** and `git show --stat HEAD`. The
full procedure, and the `git reset --soft HEAD~1` recovery for a commit that swept in another
session's hunks, is in `rules/git-commit-hygiene-shared-worktree.md`. The steps below are the
fallback when your hunks cannot be separated from theirs.

## The rule (fallback)

1. **Make your edit.** Sharing a file with another session is not a reason to skip your own work,
   and not a reason to hold the rest of your change hostage.
2. **Do not commit that file.** Commit every *other* file in your change normally, by exact path.
3. **Say so in two places** — the commit message body (so the history explains why an obviously
   related file is absent) and your reply to the user (so it reaches a human who can see both
   sessions).
4. **Hand the decision over.** The human decides whether to commit it once the other work lands,
   split it another way, or tell you to proceed. It is not an agent's call.

## Never do these to force a clean commit

- **`git stash` / `git stash -k` another session's work.** It silently removes changes from a tree
  someone else is actively working in, and a stash they did not create is one they will never
  think to look for.
- **`git checkout --` / `git restore` the file** to drop their hunks and re-apply yours. That is
  data loss with extra steps.
- **Reconstruct "just their part" by hand** and commit the rest. You cannot know their work is
  finished, and a half-committed hunk is worse than an uncommitted one.
- **Block your whole change on it.** Deliver everything else; report the one file.

## `git add -p` is not an escape hatch

Interactive git flags (`git add -i`, `git add -p`, `git rebase -i`) are unsupported by the Bash tool.
Hunk-level staging is still possible non-interactively through `git apply --cached --unidiff-zero`
on a filtered `git diff -U0` (see the update above), but only when you filter the diff from the
current tree and verify `git diff --cached --stat` before committing. Do not hand-write a patch
against a tree another session is still changing and skip that verification.

## Validated in practice

Within the same session this rule was written, another session committed
`cda89ba5 "checking in the files."`, sweeping its own 13 files — and the `CLAUDE.md` edits this
rule had told C405 to leave uncommitted were picked up cleanly alongside them. Nothing was lost,
because nothing had been stashed or restored. Had C405 "tidied up" instead, that session's
in-progress work would have been damaged.

(The commit subject itself violates
`docs/agent_rules/commit-message-quality.md` — a separate matter, deliberately not rewritten
because `dev` is shared.)

## Related

- `docs/agent_rules/git-commit-hygiene-shared-worktree.md` — what gets committed, pathspec
  discipline, never a bare `git commit`
- `docs/agent_rules/commit-message-quality.md` — commits as evidence
- `docs/agent_rules/pre-checkin-definition-of-done.md` — what must be true before any commit
