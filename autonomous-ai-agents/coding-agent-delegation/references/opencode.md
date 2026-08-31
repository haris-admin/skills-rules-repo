# OpenCode CLI Reference

## Prerequisites

- **Install:** `npm i -g opencode-ai@latest` or `brew install anomalyco/tap/opencode`
- **Auth:** `opencode auth login` or set provider env vars (OPENROUTER_API_KEY, etc.)
- **Verify:** `opencode auth list` shows at least one provider
- `pty=true` for interactive TUI sessions

## Binary Resolution

```bash
# Check for multiple binaries
which -a opencode
opencode --version

# Pin explicit path if needed
$HOME/.opencode/bin/opencode run '...'
```

## One-Shot Tasks (`opencode run`)

```bash
terminal(command="opencode run 'Add retry logic to API calls'", workdir="~/project")

# With context files
terminal(command="opencode run 'Review for security' -f config.yaml -f .env.example", workdir="~/project")

# Show thinking
terminal(command="opencode run 'Debug CI failure' --thinking", workdir="~/project")

# Force a model
terminal(command="opencode run 'Refactor auth module' --model openrouter/anthropic/claude-sonnet-4", workdir="~/project")
```

## Interactive Sessions (Background)

```bash
terminal(command="opencode", workdir="~/project", background=true, pty=true)

# Send a prompt
process(action="submit", session_id="<id>", data="Implement OAuth refresh flow")

# Monitor
process(action="poll", session_id="<id>")
process(action="log", session_id="<id>")

# Follow-up
process(action="submit", session_id="<id>", data="Now add error handling")

# Exit — Ctrl+C (NOT /exit!)
process(action="write", session_id="<id>", data="\x03")
```

## Key Flags

| Flag | Use |
|------|-----|
| `run 'prompt'` | One-shot execution |
| `--continue` / `-c` | Continue last session |
| `--session <id>` / `-s` | Resume specific session |
| `--agent <name>` | Choose agent (build or plan) |
| `--model provider/model` | Force specific model |
| `--thinking` | Show model thinking |
| `--file <path>` / `-f` | Attach files |
| `--variant <level>` | Reasoning effort (high, max, minimal) |

## TUI Keybindings

| Key | Action |
|-----|--------|
| `Tab` | Switch agents (build/plan) |
| `Ctrl+P` | Command palette |
| `Ctrl+X L` | Switch session |
| `Ctrl+X M` | Switch model |
| `Ctrl+C` | Exit OpenCode |

## Resuming Sessions

```bash
terminal(command="opencode -c", workdir="~/project", pty=true)           # Last session
terminal(command="opencode -s ses_abc123", workdir="~/project", pty=true) # Specific
```

## PR Review

```bash
terminal(command="opencode pr 42", workdir="~/project", pty=true)

# Or in temp clone:
REVIEW=$(mktemp -d) && git clone https://github.com/user/repo.git $REVIEW && cd $REVIEW && opencode run 'Review this PR vs main' -f $(git diff origin/main --name-only | head -20)
```

## Pitfalls

- `/exit` is NOT a valid command — opens agent selector. Use Ctrl+C.
- Interactive TUI requires `pty=true`. `opencode run` does NOT need pty.
- Enter may need to be pressed twice in TUI.

## Smoke Test

```bash
terminal(command="opencode run 'Respond with: OPENCODE_SMOKE_OK'")
# Expect output containing "OPENCODE_SMOKE_OK"
```
