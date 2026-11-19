---
name: repo-cleanup-and-checkin
description: >-
  Clean up a repository, bring its documentation and agent context up to date
  (rewrite and archive history when bloated), remove stale files, and check the
  code in as local commits. Use when Haris says "clean up the repo", "update
  the docs and context", "rewrite the context", "remove stale files", "check in
  the code", "tidy up and commit", or any mix of these. Asking for it grants
  authority to edit, delete provably stale files, and make LOCAL commits. Never
  pushes, deploys, merges other people's work, or touches secrets unless
  explicitly asked. For a read-only closeout report that must not commit, use
  session-closeout instead.
---

# Repo cleanup and check-in

Report facts, not hopes: say what was skipped or failed. No em dashes in anything written (docs, commits, messages).
Companion skill: `session-closeout` (same checks, but it never commits). This one does, because the ask grants it.

## Authority

Granted by the ask: edit docs and context, archive historical bloat, delete stale files that pass the tests below, remove
merged branches and worktrees that this session created, make local commits (pathspec commits, conventional prefixes).
NOT granted, ask first: `git push` (unless explicitly included in the ask), deploys, workflow runs, merging a branch into
another, force anything, deleting data or files that fail the stale tests, editing or committing another session's
uncommitted work, anything touching secrets, production, providers or email. Pushing `main` (or a production release branch)
is a release and always needs its own explicit ask. A subagent is never given these rights implicitly; give it a
denial-of-authority clause and verify its branch afterwards.

## Step 0: Orient (read before touching)

1. `git branch --show-current`, `git status --short`, `git worktree list`, `git branch -vv`, `git log origin/<branch>..HEAD --oneline`.
2. Read the project `AGENTS.md` for its branch rules (e.g. land on `dev` first; `main` gets approved work only), CI gates,
   and Remaining work register before deciding what is stale.
3. Other sessions: a dirty tree you did not make, a branch checked out by an implementer, or sibling checkouts. List files by
   owner. Never commit, revert or clean another session's files. Use pathspec commits for yours.
4. Measure core doc sizes up front: `wc -l -c AGENTS.md context.md current-progress.md` (or the repo's equivalent context files).

## Step 1: Verify before you commit

Never check in red. Run the project gates that the changes touch and READ the output before committing (a pipe into `tail`
hides a failing tool; run, read, then commit as a separate step). Read the repo's `AGENTS.md` / CI workflow for its exact
gates (for example: format/lint like `ruff`, security scans like `bandit`, contract or snapshot guards, relevant `pytest` /
`vitest` / `tsc --noEmit` / `gradlew` tests, or `terraform fmt -check`). If a shared test database looks stale, verify
failures against clean `dev` before calling them pre-existing. State what was run and what was NOT run.

## Step 2: Clean up (delete only what passes the tests)

A tracked file is STALE only if ALL are true: no live inbound reference (`grep -rIlF <name>`), not listed in an index or
register (or the index entry is updated in the same cleanup), not required by a test, build, deploy script or spec, and either
superseded by a named newer file/decision or a generated artifact. Historical records (closed specs, `docs/project-history.md`)
citing a removed draft do not block deletion if marked superseded. Untracked files: classify keep (commit), ignore
(`.gitignore`), or delete.

- Delete without asking: this session's scratch files, `.DS_Store`, `.orig`, debug prints, stray logs, `__pycache__` noise,
  temp SQL, superseded draft handoffs with no live refs, and merged branches/worktrees this session created
  (`git worktree remove`, `git branch -d`, never `-D` on unmerged work).
- List and ask first: any tracked file you did not create that fails the stale tests, anything with live inbound references,
  or anything older than the session that is not provably superseded or generated.
- Handoff scripts Haris was asked to run (e.g. `~/*.sh`): remind him to `rm` them; delete only if he says the run succeeded and asks.
- Dead links: check each document index (`AGENTS.md`, `README.md`, `docs/archive/README.md`, `openspec/INDEX.md`) for targets
  that do not exist.
- Secrets: pattern-scan the diff for key-like strings; report file and line only, never the value.
- History is not deleted. Removing a file removes it from the tree; git keeps it. Do deletions in their own commit (or alongside
  the doc index update that removes their pointers).

## Step 3: Documents and context (rewrite when bloated)

Update what changed from the code and verified live state, not from memory: version lines, route/test counts, staging and
production release state, `infra/README.md`, `current-progress.md`, the Remaining work register in `context.md` (close
finished rows with the commit hash and verification timestamp; add new rows with the next free `RW-nn` id; each row must
stand alone for an agent with no chat history), technical debt, OpenSpec indexes, release notes, and prod-issue files. Record
owner decisions verbatim (question, selected option, what it decides); an agent recommendation is a recommendation. Label
interpretations "my reading". Use absolute dates. Do not pin volatile counts or rosters in tests.

**Bloat test and rewrite.** A context or rules file (`context.md`, `AGENTS.md`, `docs/**/current-state.md`) is bloated if it
exceeds ~25 KB (or risks system-prompt truncation), if a fresh agent cannot read it in one pass to find current rules and live
state, or if it carries stale status (old versions, closed `RW-nn` rows, "in progress" for finished work, duplicated
paragraphs, per-session diaries). If bloated, REWRITE to a lean live-state doc (target `<25 KB`), do not keep appending:
1. Commit the current file first as a restore point (`docs: snapshot before context rewrite`) when rewriting a large file.
2. Move resolved history, closed `RW-nn` rows, and dated session logs into `docs/project-history.md` or
   `docs/archive/<name>-<date>.md` (kept and linked from the index) so nothing is lost. Never drop an open register row, an
   owner decision, or a live guardrail; those move to the archive only when superseded or closed.
3. Structure the rewritten live doc as: purpose, verified current state (branch, staging, production), standing rules
   (numbered, short, stated once), the open `RW-nn` register, and links to specs/archives/code. Prefer pointers over copies.
4. Re-verify every number, version, path, commit hash, and setting name you kept against code or the live system.
5. Report the before/after byte and line sizes and exact archive paths to Haris.

Rules and skills that were edited: keep `skills-rules-repo` and installed global copies (`~/.gemini/config/skills`,
`~/.claude/skills`, `~/.Codex/skills`) identical (`diff -r`); repo copy wins.
Memory notes: update an existing note before creating one; save durable facts only.

## Step 4: Check in

1. Group changes by purpose; one logical commit each, in this order: fixes that unblock CI, then code with its tests (test
   commit before fix commit when written red first), then deletions, then documents.
2. Before committing production code, simplify recent changes if appropriate (not needed for docs or tests). Use conventional
   prefixes (`spec:`, `test:`, `feat:`, `fix:`, `docs:`, `chore:`).
3. Pathspec commits only: `git add -- <paths>` then `git commit -m "..." -- <paths>`. Never `git add -A` in a shared tree.
4. After every commit: `git show --stat HEAD` and `git log --oneline -5` to verify what actually landed and confirm nothing
   foreign went in.
5. Do not push unless Haris explicitly asked to push in this turn. Report commits ahead of remote; if `main` (or a production
   release branch) should move, state plainly that pushing it is a release, list `git log origin/<branch>..<sha>`, and ask.

## Step 5: Decisions and report

Open decisions go to Haris as structured questions (one batch at a time, each with options and a recommendation); free text
that conflicts with an earlier answer is asked again, not assumed. Then output:

```
## Cleanup and check-in, <date>
Verified:        <commands run and results; what was NOT run>
Cleaned:         <deleted: files, branches, worktrees>   Needs your OK: <list>
Docs:            <updated / rewritten (size before and after) / archived to>
Committed:       <hash and subject per commit>   Left uncommitted (not mine): <files and owner>
Ahead of remote: <n commits, branch>   Push needed: <yes/no and plain warning if release branch>
Open decisions:  <list or none>   Register: <RW ids touched>
Safe to close:   yes / no, because <reason>
```

"Safe to close" is `no` while any gate is red, a foreign file was touched, a decision is unrecorded, the register is stale,
or a handoff script has not been confirmed run.
