---
name: git-workflow
description: >-
  Structures git work: atomic commits, conventional commit messages, branch naming, restore points, worktrees, pull request descriptions, change summaries, and release tagging with a human changelog. Use when committing, branching, splitting a messy working tree into clean commits, writing a commit message or PR description, resolving a conflict, preparing a release or changelog entry, or organising parallel streams of work, even when the diff is pasted inline and the message looks easy to write.
---

# Git Workflow

Source: trunk-based, save-point and change-summary guidance adapted from `addyosmani/agent-skills` `git-workflow-and-versioning` (MIT, (c) 2025 Addy Osmani), merged with this repo's rules. Where they differ, this repo's rules win: `rules/incremental-local-commits.md`, `rules/commit-message-quality.md`, `rules/release-tags-are-additive-never-moved.md`, `rules/personal-agent-folders-never-tracked.md`.

**Push, deploy and tag publication are never implied.** A commit is local and reversible; a push to a shared branch may deploy. Push only when asked in the current message, and say so plainly when `main` deploys.

## Workflow

1. **Check state.** `git status`, `git diff --staged`, `git diff`. In a shared working tree another tool may be editing; read `rules/shared-working-tree-another-tool-may-be-editing.md` before staging.
2. **Stage atomically.** Group by one logical change. Never `git add .` blindly. Keep out secrets, generated files, build output and personal agent folders (`.claude`, `.cursor`, `.codex`, `CLAUDE.md` and similar stay gitignored).
3. **Write the message** in Conventional Commits form, `type(scope): imperative summary`, per [the guide](./references/conventional-commits.md). The first line stands alone in history ("Delete the FizzBuzz RPC", not "Fixes"). The body says what and why, with the ticket, benchmark or spec link, and admits known shortcomings. Anti-patterns: "fix bug", "WIP", "phase 1", "moving code from A to B". Follow the end-of-message attribution lines the session specifies.
4. **Separate concerns.** Refactor and feature are different commits. Formatting-only changes are their own commit. Do not mix a dependency bump with a behaviour change.
5. **Size it.** About 100 changed lines is good, 300 acceptable for one logical change, 1000 too large; split by stack, file group, or vertical slice.
6. **Open the PR** with: Summary, Motivation and context, Testing and verification actually performed, Screenshots or logs where visual.

## Restore points (save-point pattern)

Commit at milestones (per phase or component), not only at the end, so a human or the next agent has something to go back to. After each increment: test passes, commit, continue; test fails, return to the last commit and investigate. The lighter milestone gate is in `rules/incremental-local-commits.md`; the full closeout gate is `rules/pre-checkin-definition-of-done.md`. Never `git reset --hard` or force anything on work you did not make; ask first.

## Branching

Keep `main` deployable. Prefer short-lived branches that merge back in days, and feature flags over long-lived branches. A release branch is acceptable to stabilise while `main` moves, and production may be running one (`rules/production-may-run-a-release-branch-read-the-box-before-you-push.md`). Name branches `type/short-description` (`feat/`, `fix/`, `chore/`, `docs/`). When on the default branch, branch before committing.

## Worktrees

Use a worktree to run parallel streams or a subagent without sharing a tree. Give each stream its own branch and directory, verify its `git log` and `git diff --stat` before merging, expect conflicts in index and register files, and keep both sides (`rules/subagent-branch-verification-and-merge-hygiene.md`, `rules/git-commit-hygiene-shared-worktree.md`).

## Change summary after any modification

```
CHANGES MADE:        file: what changed
DID NOT TOUCH:       file: why it was left alone (out of scope)
POTENTIAL CONCERNS:  assumptions, new dependencies, behaviour to confirm
```
"Did not touch" proves scope discipline and surfaces unintended edits.

## Pre-commit hygiene

Run the repo's CI gate commands locally (`rules/ci-gate-commands-run-locally-before-push.md`), scan staged diffs for secrets without printing any value, check for stray debug output, and do not chain a commit after a pipe, because the exit code is the last command's (`rules/ci-pipes-hide-failures-use-pipefail.md`). Do not commit generated files unless the repo tracks them.

## Using git to debug

`git bisect` finds the commit that broke it; `git blame` gives context for a line; `git log -S` finds when a string appeared. Read `git log` for the intent before changing old code.

## Releases and versioning

- Semantic versioning: patch for fixes, minor for backward-compatible features, major for breaking changes (`incremental-version-bumping` for the bump routine).
- **Tag each build and never move a tag.** A replaced build gets a new tag; the old one stays (`rules/release-tags-are-additive-never-moved.md`). The tag is the source of truth for what shipped.
- Before a push that carries commits, list `git log origin/main..<sha>` and tell the owner what goes with it.
- Keep a human changelog, grouped Added, Changed, Fixed, Deprecated, Removed, Security, newest first, phrased around user impact. It is not `git log`.

## Common rationalizations

| Excuse | Reality |
|---|---|
| "I will commit it all at the end" | One bad step loses everything. Commit at milestones. |
| "The message does not matter" | Commits are evidence; `git log` is how status is checked. |
| "Small fix, push straight away" | Pushing is a separate ask, and `main` may deploy. |
| "One big commit is simpler" | Unreviewable, unrevertable. Split it. |

## Red flags

- A commit chained after a piped command.
- Personal agent folders or secrets staged.
- Force operations, or a moved tag.
- A push nobody asked for.
- Mixed refactor and feature in one commit.
- Subjects like "files to be added".

## Verification

- [ ] Each commit is one logical change with a conventional, standalone subject.
- [ ] No secrets, generated output or personal agent folders staged.
- [ ] CI gate commands ran locally with their real exit codes read.
- [ ] No push, tag move or force operation happened without an explicit ask.
- [ ] A change summary lists what was and was not touched.

## Reference

- [Conventional Commits Specification Reference](./references/conventional-commits.md)
