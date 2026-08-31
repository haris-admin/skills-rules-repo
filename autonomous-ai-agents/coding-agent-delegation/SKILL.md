---
name: coding-agent-delegation
description: Delegate coding tasks to external autonomous coding agent CLIs — Claude Code, OpenAI Codex, or OpenCode. PTY/tmux orchestration, background monitoring, PR review, parallel instances. Use when you need an external agent to implement, refactor, or review code.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [coding-agent, delegation, autonomous, claude-code, codex, opencode, orchestration]
    related_skills: [hermes-agent, subagent-driven-development]
---

# Coding Agent Delegation

Delegate coding tasks to an external autonomous coding agent CLI via Hermes terminal/process tools. This umbrella skill covers the shared orchestration pattern; see `references/` for CLI-specific details on Claude Code, OpenAI Codex, and OpenCode.

## Architecture

```
Hermes Agent
  │
  ├── Mode 1: Print mode (one-shot, non-interactive)
  │     claude -p "task"           read stdin, write result
  │     codex exec "task"          sandbox workspace
  │     opencode run "task"        -f for context files
  │
  └── Mode 2: Interactive PTY via tmux (multi-turn)
        tmux new-session -d -s <name>
        tmux send-keys -t <name> '...command...' Enter
        tmux capture-pane -t <name> -p -S -50
```

## When to Use

- User explicitly names a tool (Claude Code, Codex, OpenCode)
- Complex coding task that benefits from a dedicated agent (full feature, refactor across many files)
- Long-running implementation with progress checks
- Parallel task execution in isolated workdirs/worktrees
- PR review (quick via piping the diff, or deep via worktree)

**Don't use for:** small edits (use `patch`/`write_file` directly), research that doesn't need code, or tasks under 2 minutes (setup overhead isn't worth it).

## Choosing a Tool

| If user says... | Use | Notes |
|----------------|-----|-------|
| "Use Claude Code" | `claude-code` reference | Anthropic's agent — best for Anthropic models |
| "Use Codex" | `codex` reference | OpenAI's agent — best for OpenAI models |
| "Use OpenCode" | `opencode` reference | Provider-agnostic, open-source |
| No preference | `claude` -p (most mature CLI) | Falls back to whichever is installed |

## Shared Orchestration Pattern

### Phase 1: Check readiness

```bash
# Verify the CLI is installed
which claude 2>/dev/null && claude --version
which codex 2>/dev/null && codex --version
which opencode 2>/dev/null && opencode --version

# Check auth
claude auth status 2>/dev/null
opencode auth list 2>/dev/null
```

### Phase 2: Choose mode

| Criterion | Mode |
|-----------|------|
| One-shot task (bounded, <20 turns) | Print mode (`-p` / `exec` / `run`) |
| Multi-turn iterative work | Interactive via tmux |
| User wants to follow along | Interactive |
| CI/automation | Print mode |
| Large refactors (many files, many turns) | Interactive |

### Phase 3a: Print mode (preferred for most tasks)

```bash
terminal(command="claude -p 'Fix the auth bug in src/auth.py' --allowedTools Read,Edit --max-turns 10", workdir="/project", timeout=120)
```

Key flags shared across all tools:
- `--max-turns N` — prevents runaway loops (print-mode only)
- `--allowedTools` / `--sandbox workspace-write` — restrict capabilities
- Pipe input: `cat file.txt | claude -p "summarize this"`
- Always set `workdir` to the project directory

### Phase 3b: Interactive PTY via tmux (multi-turn)

```bash
# 1. Create tmux session
terminal(command="tmux new-session -d -s coding-agent -x 140 -y 40")

# 2. Launch tool inside it
terminal(command="tmux send-keys -t coding-agent 'cd /project && claude' Enter")

# 3. Handle first-launch dialogs (see CLI-specific references)
# Wait for startup, send Enter for trust prompt, Down+Enter for permissions

# 4. Send the task
terminal(command="tmux send-keys -t coding-agent 'Refactor auth module to use JWT' Enter")

# 5. Monitor progress
terminal(command="sleep 15 && tmux capture-pane -t coding-agent -p -S -50")

# 6. Send follow-up
terminal(command="tmux send-keys -t coding-agent 'Now add unit tests' Enter")

# 7. Exit cleanly
terminal(command="tmux send-keys -t coding-agent '/exit' Enter; sleep 2; tmux kill-session -t coding-agent")
```

### Phase 4: Background mode (long tasks)

**Codex exec** is headless — use `background=true` with `notify_on_complete=true`, NOT `pty=true`:

```bash
# Start in background (codex exec is headless — no PTY needed)
terminal(command="codex exec --sandbox workspace-write --ephemeral 'Refactor auth module'",
  workdir="~/project", background=true, notify_on_complete=true, timeout=600)

# Claude Code / OpenCode may still need PTY for interactive TUI
terminal(command="claude -p 'Refactor auth'",
  workdir="~/project", background=true, pty=true)
```

**Key timeout guidance:** complex reviews or large refactors need generous timeouts (300-600s minimum). Codex exec with `gpt-5.6-sol` and high reasoning effort can take 2-5 minutes on non-trivial tasks. Set `timeout=600` for safety.

**`notify_on_complete=true` is strongly preferred over polling.** It auto-notifies you when the background process finishes, so you can keep working instead of manually calling `process(action="poll")`.

**Capturing output from background exec:**
```bash
# For codex exec with --json, stdout is the result
terminal(command="codex exec --json --sandbox workspace-write --ephemeral 'task'",
  workdir="~/project", background=true, notify_on_complete=true, timeout=600)
# Result arrives as a notification on completion — read via process(action="log")
```

### Phase 5: Parallel instances (background codex exec)

Use separate workdirs/worktrees to avoid collisions:

```bash
# Task A
terminal(command="tmux new-session -d -s taskA && tmux send-keys -t taskA 'cd /tmp/taskA && claude -p \"Fix bug\"' Enter")
# Task B
terminal(command="tmux new-session -d -s taskB && tmux send-keys -t taskB 'cd /tmp/taskB && claude -p \"Add test\"' Enter")

# Monitor both
terminal(command="sleep 30 && for s in taskA taskB; do echo '=== '$s' ==='; tmux capture-pane -t $s -p -S -5; done")
```

### Phase 6: PR review

```bash
# Quick review (pipe the diff)
terminal(command="git diff main...HEAD | claude -p 'Review for bugs, security, style' --max-turns 1", timeout=60)

# Deep review with worktree
terminal(command="tmux new-session -d -s review && tmux send-keys -t review 'cd /project && claude -w pr-review' Enter")
# Handle dialogs, send review prompt, capture results
```

## Cleanup

```bash
# Kill tmux sessions
tmux kill-session -t <name>

# Clean up worktrees
git worktree remove /tmp/worktree-name
```

## Codex Review Pattern (Non-Code Analysis)

The user may ask you to "use Codex to double-check" non-code work — AML assessments, research reports, document analysis, findings validation. Use `codex review` with stdin for this:

```bash
codex review - << 'EOF'
Your review prompt here with all context embedded inline.
Include explicit questions you want Codex to answer.
EOF
```

### Behavioral Notes

1. **Codex review operates differently from code delegation** — it runs in a sandbox with read-only access to the current directory. It can read files but not modify them.
2. **Codex will try to fetch external sources** during review. DNS resolution may fail (Temporary failure in name resolution is common) — Codex handles this gracefully and proceeds without.
3. **Codex outputs findings with P1/P2 priority labels:**
   - `[P1]` — Critical finding. Must be addressed before proceeding.
   - `[P2]` — Important nuance. Should be incorporated.
4. **Timeout consideration** — Codex with `gpt-5.6-sol` and `xhigh reasoning` takes 2-5 minutes. Set `timeout=300` minimum.
5. **Git repo required or stdin mode** — Use `git init 2>/dev/null` in a temp dir, or use stdin mode which doesn't need git.

### Example: AML/UBO Review
```bash
codex review - << 'EOF'
You are an expert AUSTRAC/FATF AML specialist. Review the following findings...
Q1: Is the UBO determination correct? Q2: What was missed?
EOF
```

## Pitfalls (shared)

1. **Interactive tools need PTY.** All three tools are TUI apps. Use `pty=true` or tmux. Without it, they hang or produce garbled output.

2. **First-launch dialog handling.** All three tools prompt for workspace trust/permissions on first use in a directory. Handle with `tmux send-keys`: Enter for trust (default=accept), Down then Enter for permissions (default=reject).

3. **Git repo required.** All three tools require a git repo to operate. Use `mktemp -d && git init` for scratch work.

4. **Background processes persist.** `tmux kill-session` or `process(action="kill")` when done.

5. **Monitor, don't interfere.** Check progress with `capture-pane`/`poll`/`log`. Don't send new instructions until the current task finishes or is stuck.

6. **Set max-turns/limits.** Print mode can run away. Always set `--max-turns N` (Claude) or its equivalent.

7. **Cross-platform WSL:** If the CLI is installed via Windows npm, use `cmd.exe /c` from WSL. Workspace must be on `/mnt/c/...` (visible from both systems), never `/tmp/`.

8. **Cleanup worktrees after review.** `git worktree remove` when done — they accumulate in `.git/worktrees/`.

## CLI-Specific References

| Reference | Covers |
|-----------|--------|
| `references/claude-code.md` | Full Claude Code CLI reference: all flags, dialog handling, settings, hooks, MCP, cost tips |
| `references/codex.md` | Codex CLI: prompt passing methods, `--sandbox` flags, WSL cross-platform, parallel worktrees |
| `references/opencode.md` | OpenCode CLI: `run` vs interactive, TUI keybindings, session management |

## Verification Checklist

- [ ] Tool CLI is available (`which <tool>`)
- [ ] Auth is configured (`<tool> auth status`)
- [ ] Inside a git repo (for code tasks)
- [ ] Print mode: one-shot task with `--max-turns` set
- [ ] Interactive: tmux session created, dialogs handled
- [ ] Background: `notify_on_complete=true` set
- [ ] Cleanup: tmux killed, worktrees removed
- [ ] Results reported: files changed, tests passed, next steps
