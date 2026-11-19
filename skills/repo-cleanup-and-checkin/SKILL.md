---
name: repo-cleanup-and-checkin
description: >
  Clean up a repository, bring its documentation and agent context up to date
  (rewrite them when bloated), remove stale files, and check the code in as
  local commits. Use when Haris says "clean up the repo", "update the docs and
  context", "rewrite the context", "remove stale files", "check in the code",
  "tidy up and commit", or any mix of these. Asking for it is the authority to
  edit, delete provably stale files and make LOCAL commits. It never pushes,
  deploys, merges other people's work or touches secrets. For a plain
  end-of-session report that must not commit, use session-closeout instead.
---

# Repo cleanup and check-in

Report facts, not hopes: say what was skipped or failed. No em dashes in anything written (docs, commits, messages).
Companion skill: `session-closeout` (same checks, but it never commits). This one does, because the ask grants it.

## Authority

Granted by the ask: edit docs and context, delete stale files that pass the tests below, remove merged branches and
worktrees that this session created, make local commits (pathspec commits, conventional prefixes, attribution trailer).
NOT granted, ask first: `git push`, deploys, workflow runs, merging a branch into another, force anything, deleting data or
files that fail the stale tests, editing or committing another session's uncommitted work, anything touching secrets,
production, providers or email. Pushing `main` is a release and needs its own ask. A subagent is never given these rights
implicitly; give it a denial-of-authority clause and verify its branch afterwards.

## Step 0: Orient (read before touching)

1. `git branch --show-current`, `git status --short`, `git worktree list`, `git branch -vv`, `git log origin/<branch>..HEAD --oneline`.
2. Note the branch rule for the project (HandleDispute: everything lands on `dev` first; `main` gets approved work only).
3. Other sessions: a dirty tree you did not make, a branch checked out by an implementer, or sibling checkouts. List files by owner.
   Never commit, revert or clean another session's files. Use pathspec commits for yours.
4. Read the project `AGENTS.md` rules and the Remaining work register before deciding what is stale.

## Step 1: Verify before you commit

Never check in red. Run the project gates that the changes touch and READ the output before committing
(a pipe into `tail` hides a failing tool; run, read, then commit as a separate step).
HandleDispute: `ruff format --check . ../scripts`, `ruff check . ../scripts`, Bandit 1.8.6 under Python 3.13 (`/tmp/hd-bandit/bin/bandit`
if present), `scripts/api_contract_guard.py check`, `scripts/audit_catalogue_snapshot.py check`, related pytest files with
`source "How It Works/local-env.sh"`, `tsc --noEmit` and Vitest for frontend changes. The shared test database can be stale; a
failure is checked against clean `dev` before it is called pre-existing. State what was NOT run.

## Step 2: Clean up (delete only what passes the tests)

A tracked file is STALE only if ALL are true: no inbound reference (`grep -rIlF <name>`), not listed in an index or register,
not required by a test, a build, a deploy script or a spec, and either superseded by a named newer file or a generated artifact.
Untracked files: classify keep (commit), ignore (`.gitignore`), or delete.

- Delete without asking: this session's scratch files, `.orig`, debug prints, stray logs, `__pycache__` noise, temp SQL, merged
  branches and worktrees this session created (`git worktree remove`, `git branch -d`, never `-D` on unmerged work).
- List and ask first: any tracked file you did not create, anything with inbound references, anything older than the session
  that is not provably generated.
- Handoff scripts Haris was asked to run (`~/hd-*.sh`): remind him to `rm` them; delete only if he says the run succeeded and asks.
- Dead links: check each document index (`AGENTS.md`, `README`, `openspec/INDEX.md`) for targets that do not exist.
- Secrets: pattern-scan the diff for key-like strings, report file and line only, never the value.
- History is not deleted. Removing a file removes it from the tree; git keeps it. Do deletions in their own commit.

## Step 3: Documents and context (rewrite when bloated)

Update what changed, from the code and the live system, not from memory:
version lines, route and audit counts, release state, the Remaining work register (close finished rows with the commit hash;
add new rows with the next free id; each row must stand alone for an agent with no chat history), technical debt, the OpenSpec
INDEX, release notes, prod-issue files. Record owner decisions verbatim (question, selected option, what it decides);
an agent recommendation is a recommendation. Label interpretations "my reading". Absolute dates. No pinned counts or rosters in tests.

**Bloat test.** A context file (AGENTS.md, CONTEXT.md, `docs/**/current-state.md`) is bloated if a fresh agent cannot read it in one
pass and find the current rules, or if it carries dated status that has gone stale (old versions, closed rows, "in progress"
for finished work, duplicated paragraphs, per-session diaries). If bloated, REWRITE, do not append:
1. Commit the current file first as a restore point (`docs: snapshot before context rewrite`).
2. Move historical detail to `docs/archive/<name>-<date>.md` (kept, linked from the index). Never drop an open register row,
   an owner decision or a rule; those move or stay.
3. Write the new file as: purpose, current facts (verified), standing rules (numbered, short), the open work register, and links.
   Prefer pointers to the spec or code over copies of them. Keep each rule once.
4. Re-verify every number and name you kept (versions, counts, paths, setting names) against code or the live system.
5. Show Haris the size change and what moved where.

Rules and skills that were edited: the repo copy and the installed copy must be identical (`diff -r`); repo copy wins.
Memory (`~/.claude/projects/.../memory`): update an existing note before creating one; save durable facts only.

## Step 4: Check in

1. Group changes by purpose; one logical commit each, in this order: fixes that unblock CI, then code with its tests (test commit
   before the fix commit when you wrote them red first), then deletions, then documents.
2. Before a commit of production code run `/simplify` (not for docs or tests). Conventional prefixes: `spec:`, `test:`, `feat:`,
   `fix:`, `docs:`, `chore:`. End every message with the attribution trailer the session gives.
3. Pathspec commits only: `git commit -m "..." -- <paths>`. New files must be `git add`ed first. Never `git add -A` in a shared tree.
4. After every commit: `git show --stat HEAD` and `git log --oneline -5` to see what actually landed. Another session may commit
   your files; confirm nothing foreign went in.
5. Do not push. Say how many commits are ahead of the remote and, if `main` should move, that pushing `main` is a release
   (list `git log origin/main..<sha>` and ask).

## Step 5: Decisions and report

Open decisions go to Haris as structured questions (AskUserQuestion), one batch at a time, each with a recommendation and its
options; free text that conflicts with an earlier answer is asked again, not assumed. Then:

```
## Cleanup and check-in, <date>
Verified:      <commands run and results; what was NOT run>
Cleaned:       <deleted: files, branches, worktrees>   Needs your OK: <list>
Docs:          <updated / rewritten (size before and after) / archived to>
Committed:     <hash and subject per commit>   Left uncommitted (not mine): <files and owner>
Ahead of remote: <n commits, branch>   Push needed: <yes/no and the plain warning>
Open decisions: <list or none>   Register: <RW ids touched>
Safe to close: yes / no, because <reason>
```

"Safe to close" is no while any gate is red, a foreign file was touched, a decision is unrecorded, the register is stale,
or a handoff script has not been confirmed run.
