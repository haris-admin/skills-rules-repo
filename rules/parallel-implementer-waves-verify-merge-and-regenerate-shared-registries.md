# Parallel implementer waves: verify, merge one at a time, regenerate shared registries

Applies to a coordinator that builds one feature with several subagent implementers in parallel worktrees, and to anyone merging their branches.

**Scope:** all agents that dispatch implementers; HandleDispute spec 85 (17 Nov 2026) is the worked example.

---

## Why this exists

HandleDispute, spec 85: 17 implementer branches in five waves built about 40 000 lines. Every wave touched the same registries (the router list in `api.py`, the audit catalogue, its snapshot and label review), two waves wrote a test fixture file with the same name, and a finished agent was re-announced as "waiting on background work" more than ten times. Verifying and merging by a fixed routine kept the tree green: 3781 backend tests passed after the last merge.

## Core Directives

1. **One shared rules file plus a short prompt per implementer.** The file holds the contract pointer, test-first rule, gates, safe local run and the denial of authority; each prompt names the worktree, branch, base commit, the tasks and what not to build.
2. **Verify every report before merging:** `git status`, `git log base..HEAD`, `git diff --name-only` filtered against the forbidden paths, `git branch -r --contains HEAD` (nothing pushed), then run its tests yourself. A report is a claim.
3. **Merge in dependency order, one branch at a time.** Fast-forward when the integration branch is an ancestor.
4. **Shared registries are regenerated, never hand merged.** Keep both sides of router imports and includes and run the import sorter. For an append-only catalogue take the integration side, append only the entries the incoming branch writes, then regenerate the snapshot and the generated review document with the project scripts and run the snapshot check.
5. **Each wave appends only the catalogue entries its own code writes** when a guard requires every entry to have a writer.
6. **Two files with one name:** rename the later file and fix its importers in the merge commit.
7. **After the last merge run the whole suite on a fresh test database** (see the shared test database rule), then the lint, format, contract and snapshot gates, each read before the commit.
8. **A repeated completion notice is not a running process.** Check the process table before acting, and say so to the owner.

## Patterns to Avoid

- Merging branches in parallel into one worktree.
- Editing a generated snapshot or document by hand.
- Trusting an implementer's "green" without running its tests.
- Letting an implementer edit the contract, the digest or another wave's files.
