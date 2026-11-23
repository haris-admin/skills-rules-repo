---
name: parallel-implementer-handoff
description: >-
  Use when the owner wants a second implementer agent (Antigravity, Codex, Cursor, another Claude) to build part of the work in parallel. Covers choosing what to hand over,
  writing the spec and an implementation brief with a denial-of-authority clause, making a worktree, getting a Plane ticket to Todo through a subagent and a cold-start check,
  start lines for the owner, and verifying and merging the branch afterwards. Trigger on "hand over to Antigravity", "give it to another agent", "work in parallel", "assign to
  the other agent". Do NOT use to implement the work yourself or to push or deploy anything.
---

# Parallel implementer handoff

Claude specs, the named implementer builds, Claude verifies and merges, the owner pushes and deploys. Learned on HandleDispute, 23 Nov 2026.

## 1. Choose what to hand over
- Hand over work that has a spec (proposal, design, tasks naming their test file) and needs no decision from the owner. A finding with no spec is NOT handed over; write the spec first.
- Shared test database: if the suite uses one fixed database, only one pytest process may run. Give the second implementer either only work that needs no database (script shim tests, docs) or the database for a whole sequence while you stop running backend tests.
- Give each piece its own worktree made by you from the tip of the integration branch (`git worktree add -b feature/<id> ../<name> dev`). Pieces on one branch run in a stated order.

## 2. Write the brief (`docs/handover/IMPLEMENTATION_BRIEF_<tool>-<topic>-<date>.md`)
Files it may change, files it must not touch, the process (red first, green, gates, read the summary line and `exit=`), commit rules (pathspec; its own co-author trailer), the database rule, and a denial-of-authority clause: no push, no deploy or workflow, no merge, no external service, no secret, no data or branch deletion, no `git stash`, no rebase or force, no Plane state change; silence is a denial; out-of-scope findings go in "Found outside scope". Require a final report (branch, commit list, diff stat, commands with summary lines and exit codes, ticked tasks with evidence). Give the owner a SHORT symlink to the brief (`~/hd-ag-brief.md`) and tell the owner to delete it afterwards.

## 3. Get the ticket to Todo (the owner wants a Todo ticket for every handoff)
1. Create the Plane ticket (a sync script from the specs), still Backlog.
2. Dispatch a subagent with the `backlog-to-todo-agent-ready` skill. Authority: read-only on the repo except one scratchpad file; the only Plane write is a PATCH of that ticket's description; no state, priority, labels or comments; no secret printed.
3. Cold-start check: a fresh small-model agent (Haiku) reads ONLY the ticket and reports blockers (read-only, confirms cited paths exist). Fix the real defects and repeat. Expected non-defects: a preflight that stops until an earlier ticket in the sequence is committed.
4. Preflight in the ticket: the worktree must contain the integration tip (`git merge-base --is-ancestor <hash> HEAD`); fast-forward the worktree right before dispatch because the integration branch moves.
5. Move the state with a script that PATCHes only the named tickets (never a bulk tracker that also writes comments). Only after the cold-start check passes.

## 4. Questions the ticket agents raise
Answer small ones yourself and say so; anything that changes behaviour goes to the owner as a structured question with a recommendation. If the owner chooses against the recommendation, rewrite the ticket and the spec (see the rule on owner decisions).

## 5. Start lines and verification
Give the owner one start line per ticket (`Read ~/<link> and follow it exactly. Your ticket is [id] in Plane (Todo).`). When a branch is reported: verify from the merge base (`git log`, `git diff --stat`, remote branches, that nothing was pushed), re-run its tests yourself (the full suite on a fresh database), expect conflicts in index and register files and keep both sides, then merge into the integration branch. Never trust the report alone.
