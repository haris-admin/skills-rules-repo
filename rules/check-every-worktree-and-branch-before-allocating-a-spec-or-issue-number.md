# Check every worktree and branch before allocating a spec or issue number

Numbers for specs and prod issues are allocated from the committed tree, but other sessions hold unmerged ones in their own worktrees.

**Scope:** any agent creating `openspec/changes/<n>-...` or `prod-issues/issue-<n>-...`, and any agent briefing another agent to do so.

---

## Core Directives

1. **List the folders in every worktree** (`git worktree list`, then each `openspec/changes` and `prod-issues`) and the branches, then take the next free number above all of them.
2. **Reserve a block** when briefing an agent to write several specs, and tell it to stop if a number is taken.
3. **Search for an existing issue about the same defect** before opening a new one; add the plan to it.
4. **Renumber before merge**, not after: references in specs, tasks, briefs and registers all cite the number.

## Why this exists

**21 Nov 2026 (HandleDispute):** an agent named a spec 98 (the business directory already held 98 in another worktree) and four issues from 104 (104 was held by another session's uncommitted issue, and one duplicated ISSUE-098). All were renumbered after the fact across about 20 files.
