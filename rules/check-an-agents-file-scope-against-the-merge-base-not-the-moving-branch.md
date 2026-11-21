# Check an agent's file scope against the merge base, not the moving branch

A diff against a branch that moved since the agent's branch was cut shows other people's changes as if the agent made them.

**Scope:** coordinators verifying a subagent's worktree before merging.

---

## Core Directives

1. **Diff against `git merge-base HEAD <branch>`**, not against the branch tip.
2. **Check three things**: files outside the allowed paths, protected files, and whether any remote branch contains the commits.
3. **Read the commits, not only the report**: a report is the agent's claim.
4. **Re-check after the agent is resumed**: it may have worked in the same worktree again.

## Why this exists

**21 Nov 2026 (HandleDispute):** a scope check against `dev` listed version files and research documents as outside scope because `dev` had moved after the agent's branch was cut. The merge-base diff showed only the agent's own files.
