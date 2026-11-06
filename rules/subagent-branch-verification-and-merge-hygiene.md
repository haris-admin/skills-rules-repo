# Verify a subagent's branch before merging, and merge it carefully

A subagent's final report is model output. Check its branch, its scope and its test results yourself, then merge and re-verify the merged tree.

**Scope:** an orchestrating agent that dispatches subagents into git worktrees.

---

## Core Directives

1. **Dispatch with limits**: one worktree per agent, an explicit denial-of-authority clause (no push, deploy, workflow trigger, send, secrets, deletes), and the files it must not touch.
2. **Verify before merging**: `git log base..branch`, `git diff --stat base...branch`, `git ls-remote --heads origin` (nothing pushed), and read the files outside its stated scope.
3. **Expect doc conflicts**: `openspec/INDEX.md`, `tasks.md` and the debt register conflict between agents; keep both sides, renumber duplicate ids (for example two TD-056 rows), and do not over-replace ids in unrelated rows.
4. **Shared test database**: agents running the suite against one local Postgres collide; use unique fixture values, clean only your own rows, and run the quiet-database check before a major dependency release.
5. **Worktrees can start from an older commit**: fast-forward the agent branch to the current base inside its own worktree, never rewrite shared history.
6. **Re-run on the merged tree**: formatter, linter, scanner, full suites and guards, then remove the worktree and branch.

## Why this exists

**6 Nov 2026 (HandleDispute):** a dozen subagents delivered the security, audit trail and backup work. Merges hit conflicts in the spec index and debt register, a duplicate debt id, an agent running tests on the shared database at the same time as another, and a merged tree that needed a final format pass.
