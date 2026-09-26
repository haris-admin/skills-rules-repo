# Incremental local commits after each task (restore points)

**Scope:** every agent. **Always apply.** Mirrors: `.cursor/rules/incremental-local-commits.mdc`
(Cursor), `.agents/rules/incremental-local-commits.md` (Antigravity). Summarised in `AGENTS.md`,
`AGENTS.md`, `GEMINI.md`. If a mirror drifts, this file wins.

**Human decision recorded 22 Aug 2026 (the project lead, in-session):** *"create rules that llm to checkin
the code after every task or small chunks. so that there is something to go back to."* This
reverses the previous default ("wait to be asked before committing"). **Pushing is unchanged** —
still requires an explicit ask in the current message.

This workspace rule also supersedes the generic Cursor user-rule "only create commits when
requested" **for this repository's local commits**. A same-message "don't commit" from the human
overrides this rule for that turn.

## Why this exists

Uncommitted work has vanished from this tree more than once (Change 83: `.pyc` on disk, source
gone; C325 skill files written and never committed). C413's concurrent-edit failure happened
*before any commit existed* to reveal the conflict. `openspec/changes/README.md` makes
`status: implemented` mean "there is a commit" — zero commits is unfalsifiable WIP, not a restore
point. A shared, multi-agent working tree needs named snapshots so a human or the next agent can
go back.

## Default — do this without being asked

Commit **locally on `dev`** when any of these is true:

1. An OpenSpec task (`Txxx.nn`) just went **Green** (the task's cited tests pass for the spec
   reason).
2. A small, independently-revertible chunk is Green (one migration + its test; one service
   function + its tests; one UI wiring test + the control it covers).
3. You are about to stop or hand off and you have Green uncommitted work **you** created this
   session.

Do **not** batch an entire change into one commit "to keep history tidy." The point is a restore
point per task. One commit per Green task is the default grain. Two tightly-coupled files that
cannot compile/import without each other go in the **same** commit.

## Two gates — incremental vs closeout

Requiring the full `pre-checkin-definition-of-done.md` list (unfiltered backend pytest, frontend
suites, coverage floors) before **every** small commit is why agents skip committing. That gate
is for shipping a change, not for a restore point.

| Gate | When | What you must have run |
|------|------|------------------------|
| **Incremental** | Each Green task / small chunk | The tests **for this task** Green; `ruff check` on *your* files (or frontend equivalent); code collects/parses; `git status --short` hygiene; subject satisfies `commit-message-quality.md` and names the task ID |
| **Closeout** | Last task of the change, OpenSpec closeout, or before a **requested** push | The full `pre-checkin-definition-of-done.md` list, including unfiltered pytest + frontend + `tsc` |

An incremental commit is allowed with `status: partial` still on the proposal. Do **not** set
`status: implemented` on an incremental commit unless `git log` already shows the change on
shared `dev` per `openspec/changes/README.md`.

**Human clarification, 28 Aug 2026 (the project lead, in-session):** for a logical / OpenSpec change
delivered as a unit, commit at milestone points (per phase / component, ~2–4 per change — a large
phased change may have one per phase), not one commit per task — 7–8 check-ins for a single change
is not wanted. Per-task evidence still goes in the `tasks.md` completion log (the exact command +
counts for every task). Version increments follow the two-tier milestone/defect standard (`incremental-version-bumping`).

## How — hygiene is not optional

The *when* is this file. The *how* is unchanged:

- Pathspec the commit: `git commit -m "…" -- <path> <path>`. Never bare, never `-a`, never
  `git add -A` / `git add .` (`git-commit-hygiene-shared-worktree.md`).
- Only paths **you** created or edited this session. Other sessions' files stay uncommitted
  (`shared-file-commit-resolution.md` if you had to edit a shared file).
- Subject names the task and survives losing the diff (`commit-message-quality.md`). Body has
  the evidence (the test command and pass count for **this** task).
- After committing, re-run `git status --short` and confirm other sessions' files are untouched.

- **Confirm the commit landed.** A pre-commit hook that blocks the commit can print pages of
  output that look like success. After every commit run `git log -1 --oneline` and check the
  subject is yours; if the old subject is still there, read the hook's message and fix it.
- **Pass file lists as arrays in zsh.** zsh does not word-split a scalar: `F="a b"; git add $F`
  hands git one path named `a b`, and `node scripts/check-style.js $F` silently checks nothing.
  Use `F=(a b); git add "${F[@]}"` (Simplifii-OS, 26 Sep 2026: a style check and a commit both
  no-opped this way).

## Do not

- **Do not push.** A local restore point is not a push and does not imply one.
- **Do not commit** a syntax error, collection error, or half-edited file that does not parse.
  A valid Red test may sit in the working tree until Green; do **not** leave `dev` with a
  known-broken collection that will fail every other session's pytest in this worktree.
- **Do not commit** secrets, `.env`, `*.tfvars`, credential files.
- **Do not commit** when the current message says "don't commit" / "I'll commit this."
- **Do not** use progress-note subjects ("checking in the files", "WIP", "Saving …").

## Related

- `docs/agent_rules/git-commit-hygiene-shared-worktree.md` — which files
- `docs/agent_rules/commit-message-quality.md` — the subject
- `docs/agent_rules/shared-file-commit-resolution.md` — a file that is both yours and theirs
- `docs/agent_rules/pre-checkin-definition-of-done.md` — closeout gate (not the per-task gate)


## Incremental Version Bumping Integration

All atomic check-ins, defect fixes, and capability milestones follow the strict two-tier convention in `incremental-version-bumping`:

$$\text{Milestone Base: } 0.F0.00 \quad \longrightarrow \quad \text{Defect / Increment: } 0.F0.NN$$

Where:
* $F$ is the Feature / Capability number ($1, 2, 3, 4, 5, 6, 7$).
* $NN$ is the zero-padded two-digit defect fix / patch increment ($01, 02, 03, \dots, 99$).

Whenever an incremental atomic check-in or feature milestone is made, update the version synchronously across all relevant manifests:
- **Node / React / Web platforms** (e.g. Simplifii-OS): `.version`, `package.json`, `package-lock.json`
- **Python / FastAPI backends**: `pyproject.toml`, `app/__init__.py`, `app/main.py`
- Always use explicit pathspecs (e.g. `git add .version package.json package-lock.json <changed-files>`), never bare `git add .`.
