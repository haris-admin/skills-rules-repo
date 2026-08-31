---
name: codex
description: "Delegate coding to OpenAI Codex CLI (features, PRs)."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [Coding-Agent, Codex, OpenAI, Code-Review, Refactoring]
    related_skills: [claude-code, hermes-agent]
---

# Codex CLI

Delegate coding tasks to [Codex](https://github.com/openai/codex) via the Hermes terminal. Codex is OpenAI's autonomous coding agent CLI.

## When to use

- Building features
- Refactoring
- PR reviews
- Batch issue fixing

Requires the codex CLI and a git repository.

## Prerequisites

- Codex installed: `npm install -g @openai/codex`
- OpenAI auth configured: either `OPENAI_API_KEY` or Codex OAuth credentials
  from the Codex CLI login flow
- **Must run inside a git repository** — Codex refuses to run outside one
- Use `pty=true` in terminal calls — Codex is an interactive terminal app

For Hermes itself, `model.provider: openai-codex` uses Hermes-managed Codex
OAuth from `~/.hermes/auth.json` after `hermes auth add openai-codex`. For the
standalone Codex CLI, a valid CLI OAuth session may live under
`~/.codex/auth.json`; do not treat a missing `OPENAI_API_KEY` alone as proof
that Codex auth is missing.

## WSL + Windows Codex (Cross-Platform)

When Hermes runs inside WSL but Codex is installed via **Windows npm** (not WSL npm), calling `codex` directly fails with "Missing optional dependency @openai/codex-linux-x64". The Windows global npm binary works via `cmd.exe /c`:

```bash
# Verify Codex is accessible from WSL
cmd.exe /c "codex --version"
# Expected: codex-cli 0.x.x

# Run Codex from WSL — workspace MUST be on a Windows-accessible path.
# Prefer stdin piping (Method 2 above) for complex prompts.
cmd.exe /c "cd /d C:\Users\habib\.hermes\codex-workspace && codex exec --sandbox workspace-write 'simple prompt'"
```

**Workspace location rule:** `cmd.exe` started from WSL cannot use UNC paths (`\\wsl.localhost\...`). Always place the git workspace under `/mnt/c/Users/<name>/...` so both WSL (`/mnt/c/...`) and Windows (`C:\...`) can access it. `/tmp/` workspaces are invisible to `cmd.exe`.

**Build Queue pattern (cron job + Codex):** Use a cron job as a build queue consumer that fires Codex via `cmd.exe /c`. The cron job runs in WSL, Codex runs on Windows, and the shared workspace on `/mnt/c/...` bridges them. Use `--full-auto` so Codex auto-approves file writes without hanging on interactive prompts. See `pluto-portfolio-ideation` for a worked example of this pattern.

## Prompt Passing — Three Methods

**Method 1: Inline (simple prompts only)**
```
terminal(command="codex exec -C /path/to/repo 'Add dark mode toggle to settings'", workdir="~/project", pty=true)
```
⚠️ Avoid this method when the prompt starts with a filename-like word (e.g. "Read CONTEXT.md..."). Codex v0.130+ parses the first word as a potential file argument and fails with "unexpected argument 'CONTEXT.md'".

**Method 2: stdin piping (preferred for complex prompts, cross-platform)**
```bash
# Write prompt to a file first, then pipe it
cat /mnt/c/Users/habib/.hermes/codex-workspace/PROMPT.txt | \
  cmd.exe /c "codex exec -C C:\Users\habib\.hermes\codex-workspace --sandbox workspace-write -"
```
The trailing `-` tells Codex to read the prompt from stdin. This avoids all shell quoting issues and the file-argument parsing bug. Always use this pattern for prompts longer than a sentence, containing filenames, or crossing WSL→Windows boundaries.

**Method 3: Pipe with pty (WSL-native Codex)**
```
terminal(command="cat prompt.txt | codex exec -C /path/to/repo --sandbox workspace-write -", pty=true)
```

## One-Shot Tasks

```
terminal(command="codex exec -C ~/project 'Add dark mode toggle to settings'", workdir="~/project", pty=true)
```

For scratch work (Codex needs a git repo):
```
terminal(command="cd $(mktemp -d) && git init && codex exec --sandbox workspace-write 'Build a snake game in Python'", pty=true)
```

## Background Mode (Long Tasks)

```
# Start in background with PTY
terminal(command="codex exec --sandbox workspace-write 'Refactor the auth module'", workdir="~/project", background=true, pty=true)
# Returns session_id

# Monitor progress
process(action="poll", session_id="<id>")
process(action="log", session_id="<id>")
```

## Key Flags

| Flag | Effect |
|------|--------|
| `exec "prompt"` | One-shot execution, exits when done |
| `--sandbox workspace-write` | Sandboxed, auto-approves file changes in workspace (replaces deprecated `--full-auto` as of v0.130+) |
| `--sandbox read-only` | Agent can read but not write (safest for review tasks) |
| `--dangerously-bypass-approvals-and-sandbox` | No sandbox, no approvals (fastest, most dangerous; replaces `--yolo`) |
| `-C <DIR>` | Set working directory (useful for cross-platform invocations) |
| `-m <MODEL>` | Override model (e.g. `-m gpt-5.5`) |
| `-` (as prompt) | Read prompt from stdin instead of as a CLI argument |

## PR Reviews

Clone to a temp directory for safe review:

```
terminal(command="REVIEW=$(mktemp -d) && git clone https://github.com/user/repo.git $REVIEW && cd $REVIEW && gh pr checkout 42 && codex review --base origin/main", pty=true)
```

## Parallel Issue Fixing with Worktrees

```
# Create worktrees
terminal(command="git worktree add -b fix/issue-78 /tmp/issue-78 main", workdir="~/project")
terminal(command="git worktree add -b fix/issue-99 /tmp/issue-99 main", workdir="~/project")

# Launch Codex in each
terminal(command="codex exec --sandbox workspace-write 'Fix issue #78: <description>. Commit when done.'", workdir="/tmp/issue-78", background=true, pty=true)
terminal(command="codex exec --sandbox workspace-write 'Fix issue #99: <description>. Commit when done.'", workdir="/tmp/issue-99", background=true, pty=true)

# Monitor
process(action="list")

# After completion, push and create PRs
terminal(command="cd /tmp/issue-78 && git push -u origin fix/issue-78")
terminal(command="gh pr create --repo user/repo --head fix/issue-78 --title 'fix: ...' --body '...'")

# Cleanup
terminal(command="git worktree remove /tmp/issue-78", workdir="~/project")
```

## Batch PR Reviews

```
# Fetch all PR refs
terminal(command="git fetch origin '+refs/pull/*/head:refs/remotes/origin/pr/*'", workdir="~/project")

# Review multiple PRs in parallel
terminal(command="codex exec 'Review PR #86. git diff origin/main...origin/pr/86'", workdir="~/project", background=true, pty=true)
terminal(command="codex exec 'Review PR #87. git diff origin/main...origin/pr/87'", workdir="~/project", background=true, pty=true)

# Post results
terminal(command="gh pr comment 86 --body '<review>'", workdir="~/project")
```

## Rules

1. **Always use `pty=true`** — Codex is an interactive terminal app and hangs without a PTY
2. **Git repo required** — Codex won't run outside a git directory. Use `mktemp -d && git init` for scratch
3. **Use `exec` for one-shots** — `codex exec "prompt"` runs and exits cleanly
4. **`--sandbox workspace-write` for building** — auto-approves file changes within the workspace (replaces deprecated `--full-auto`)
5. **Background for long tasks** — use `background=true` and monitor with `process` tool
6. **Don't interfere** — monitor with `poll`/`log`, be patient with long-running tasks
7. **Parallel is fine** — run multiple Codex processes at once for batch work
8. **WSL → call via `cmd.exe /c`** — when Codex is installed on Windows npm, use `cmd.exe /c "cd /d C:\path && codex exec ..."`. Workspace must be on `/mnt/c/...`, never `/tmp/`.
