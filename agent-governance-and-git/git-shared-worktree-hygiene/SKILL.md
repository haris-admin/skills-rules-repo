---
name: git-shared-worktree-hygiene
description: Safe git workflows for multi-agent environments: pathspec-only staging, milestone commits, and push protection. Use when an agent is about to run git add, git commit, or git push in a shared or multi-agent worktree.
---

# Git Shared Worktree Hygiene

## Mandates
1. **Pathspec Staging**: Never run bare `git add .` or `git commit -a`. Always explicitly specify the exact files you modified (`git add <file1> <file2>`).
2. **Milestone Local Commits**: Commit locally after completing logical milestones (phases/components) to maintain clean restore points.
3. **No Unprompted Pushes**: Never push to remote (`git push origin <branch>`) without an explicit user instruction.
4. **Commit Message Quality**: Use structured conventional commits (`feat:`, `fix:`, `chore:`, `test:`, `docs:`).
5. **Another agent's hunk in a file you must commit**: when a file holds your lines and another agent's uncommitted lines (Tap-Ease 2026-11-09: `context.md`), do not commit the whole file and do not revert theirs. Build a zero-context patch (`git diff -U0 <file>`), drop the hunks that are not yours, and stage the rest with `git apply --cached --unidiff-zero <patch>`. Their lines stay in the working tree. Before committing, read their diff once: if it is complete and tested, say so and commit it separately as their work instead of leaving it stranded.
6. **Run the suite on the tree you are about to commit**, including their uncommitted files, and say so in the report ("passed with the other agent's edits in the tree").

