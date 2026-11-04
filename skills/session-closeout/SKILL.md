---
name: session-closeout
description: >
  End-of-session check-in. Documents the session's changes, updates AGENTS.md
  and the context and progress docs, updates release and API documentation,
  cleans up the repo and temporary handoff files, and lists the work still
  required before the session can close. Use when asked to "check in", "close
  out", "wrap up", "end the session", "session closeout", or "what is left
  before we stop". Runs regularly. Never commits, pushes, deploys or deletes
  without the explicit ask.
---

# Session Closeout

Run this in order. Report facts, not hopes: if something was skipped or failed, say so.
Do not use em dashes in any prose written into docs, commits or messages.

## Authority boundary (read first)

- This skill edits files and reports. It does NOT commit, push, deploy, send, rotate
  credentials or delete data unless Haris asks for that specific action in this turn.
- Pushing `main` deploys production. Say so plainly before offering it.
- Never print secrets, tokens or fragments of them. Compare with booleans.
- If dispatching subagents, give each an explicit denial-of-authority clause and verify
  branch state afterwards (`git log origin/<branch>..HEAD --oneline`).

## Step 1: Establish what changed

1. `git status --short`, `git diff --stat`, `git log origin/<branch>..HEAD --oneline`,
   and `git log --since=<session start> --oneline`.
2. List external side effects of the session (secret edits, restarts, deploys, DB
   writes, emails drafted or sent). Source: conversation history, not memory.
3. Write a short "what changed and why" list. Group by: code, config/secrets, infra,
   data, docs.

## Step 1b: Find and fix conflicts

Look for every kind of conflict before documenting, and resolve what can be resolved
safely. Escalate the rest as open decisions.

1. **Merge conflicts:** `git diff --name-only --diff-filter=U` and a grep for conflict
   markers (`<<<<<<<`, `>>>>>>>`) in changed files. Resolve by reading both sides and the
   requirement, never by blindly taking one side. Re-run the touched tests after.
2. **Behind the remote:** `git fetch`, then `git rev-list --left-right --count origin/<branch>...HEAD`.
   If behind, integrate (fast-forward or rebase) only when the tree is clean or the changes
   are safely stashed or committed. Never force anything. Do not push.
3. **Mixed work in one tree:** changes from different tasks or sessions sharing the working
   tree. Group files by task and propose separate commits (`git add -p` or explicit paths).
   A fix that unblocks CI is committed on its own, ahead of unrelated feature work.
4. **Branch mismatch:** compare the current branch with the one the session started on and
   with the project's branch rules. Flag any difference; do not switch branches silently.
5. **Doc versus code disagreement:** version lines, route lists or counts in docs that no
   longer match code (`pyproject.toml`, config VERSION, `/health`). Fix docs to match the
   code unless the code is wrong, then raise the gap.
6. **Ignored or untracked docs:** `git check-ignore -v` on every doc you edit. If a doc is
   gitignored, say so in the report, because the edit will not reach other machines.
7. **Skill and rule copies:** if a skill or rule was edited, make sure the repo copy
   (`skills-rules-repo`) and the installed copy (`~/.claude/skills/...`) are identical
   (`diff -r`). Resolve in favour of the repo copy, then re-sync.

Anything that needs a design decision, or where two sources conflict on what is
required, goes to Step 5 as a structured question. Record both answers.

## Step 2: Verify before documenting

- Run the project's quick checks that the session touched (lint, type check, the
  relevant tests). State exactly what was run and what was not.
- Confirm the Requirement, Test, Implementation chain: every behaviour change has a
  requirement (OpenSpec change, RCA, or explicit instruction) and a test that cites it.
  A change with no test is "not implemented" for closeout purposes. List it as a gap.
- Confirm the API contract was not changed as a side effect (status codes, response fields).

## Step 3: Update documentation

Update only what the session actually changed. Read each file before editing.

| Target | Update when |
|---|---|
| `AGENTS.md` | A new domain rule, gotcha, guardrail or procedure was learned. Add to the right numbered section, do not append a diary. |
| `docs/context.md` | Version, architecture, integrations, endpoints or operational facts changed. Keep the version line current. |
| `current-progress.md` (or `docs/current_progress.md`) | Status of in-flight work, what is done, what is next. |
| `CHANGELOG.md`, `RELEASE_NOTES.md` | A release or user-visible change shipped or is staged. |
| `docs/api_version_tracking.md` and API/frontend guides | Any route or response shape changed. |
| `prod_issues/` (RCA files) | A defect was investigated or fixed. Search existing RCAs first. |
| `openspec/` | A requirement changed. Tests and spec change together, with Haris confirming. |
| Memory (`~/.claude/projects/.../memory/`) | Durable facts, decisions or feedback. Update an existing memory before creating a new one. Do not save what the repo already records. |

Rules for what you write:
- Record Haris's decisions verbatim: the question, the selected option, what it decides.
  Record an agent recommendation as a recommendation, never as a decision.
- Label interpretations of free or voice text as "my reading".
- Do not hardcode values a person might change. Do not pin counts or rosters in tests or docs.
- Dates absolute (e.g. 2026-11-05), never "today" or "last week".

## Step 4: Clean up

Look at each target before removing it. Present deletions as a list for approval
unless the item is clearly one of this session's own temporary files.

- Handoff scripts Haris was asked to run (e.g. `~/*.sh`): remind him to delete them
  (rule: he runs `rm`), or delete only if he confirmed the run succeeded and asked.
- Scratch files, debug prints, `.orig`, `__pycache__` noise, stray logs, temp SQL.
- Untracked files: classify as keep (commit), ignore (.gitignore), or delete.
- Stale branches and worktrees created in the session (`git branch -vv`, `git worktree list`).
- Anything in the scratchpad directory is disposable; anything in the repo is not
  until checked.
- Confirm no secrets landed in the working tree (`git diff` scan for key-like strings
  using a pattern match that reports file and line only, never the value).

## Step 5: Open items and decisions

1. List every open decision as a structured question with options and a recommendation
   (use AskUserQuestion). Do not relay status while decisions are pending.
2. List remaining work, each with: what, why it matters, blocker, owner (Haris, agent,
   third party).
3. Flag review debt: requirement changes void reviews of the changed scope.
4. Flag release state: version bumped in all files? CI gate run? Production push
   needed, and if so the plain warning that pushing `main` deploys.
5. Flag follow-ups that depend on external parties (providers, partners). Drafts of
   emails stay drafts; never send.

## Step 6: Closeout report

Output, concise and skimmable:

```
## Session closeout, <date>
Changed:        <grouped list>
Verified:       <commands run and results; what was NOT run>
Conflicts:      <found, fixed, escalated>
Docs updated:   <files>
Docs skipped:   <files and why>
Cleaned:        <items>   Needs your OK to delete: <items>
Uncommitted:    <count and summary>   Unpushed commits: <count>
Open decisions: <list or "none">
Remaining work: <list>
Safe to close:  yes / no, because <reason>
```

"Safe to close" is "no" while any of these is true: unresolved conflicts, failing checks, uncommitted work
Haris has not chosen to leave, undocumented contract change, unrecorded decision,
or a handoff command not yet confirmed run.
