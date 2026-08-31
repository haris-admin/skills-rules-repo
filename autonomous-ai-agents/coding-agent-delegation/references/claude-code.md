# Claude Code CLI Reference

## Prerequisites

- **Install:** `npm install -g @anthropic-ai/claude-code`
- **Auth:** `claude auth login` (browser OAuth) or `claude auth login --console` (API key)
- **Check:** `claude auth status` or `claude doctor`

## Print Mode (`-p`) — Non-Interactive (PREFERRED)

```bash
terminal(command="claude -p 'Add error handling to API calls' --allowedTools Read,Edit --max-turns 10", workdir="/path/to/project", timeout=120)
```

## Interactive PTY via tmux — Multi-Turn

```bash
terminal(command="tmux new-session -d -s claude-work -x 140 -y 40")
terminal(command="tmux send-keys -t claude-work 'cd /path/to/project && claude' Enter")
# Dialog 1 (trust): Enter
terminal(command="sleep 4 && tmux send-keys -t claude-work Enter")
# Dialog 2 (permissions, only with --dangerously-skip-permissions): Down, Enter
terminal(command="sleep 3 && tmux send-keys -t claude-work Down && sleep 0.3 && tmux send-keys -t claude-work Enter")
# Send task
terminal(command="tmux send-keys -t claude-work 'Refactor auth module' Enter")
# Monitor
terminal(command="sleep 15 && tmux capture-pane -t claude-work -p -S -50")
# Exit
terminal(command="tmux send-keys -t claude-work '/exit' Enter")
```

## Key Flags

| Flag | Effect |
|------|--------|
| `-p, --print` | Non-interactive one-shot |
| `-c, --continue` | Resume most recent session |
| `-r, --resume <id>` | Resume specific session |
| `--model <alias>` | sonnet/opus/haiku or full name |
| `--effort <level>` | low/medium/high/max/auto |
| `--max-turns <n>` | Limit loops (print mode only!) |
| `--max-budget-usd <n>` | Cap spend |
| `--dangerously-skip-permissions` | Auto-approve all tool use |
| `--allowedTools <tools...>` | Whitelist: Read, Edit, Write, Bash, WebSearch |
| `--output-format <fmt>` | text/json/stream-json |
| `--json-schema <schema>` | Structured JSON output |
| `--bare` | Skip plugins, MCP, OAuth (needs ANTHROPIC_API_KEY) |
| `--worktree` / `-w` | Isolated git worktree mode |
| `--from-pr <number>` | Review linked to a PR |
| `--fork-session` | New session ID when resuming |

## Session & Slash Commands

| Command | Purpose |
|---------|---------|
| `/compact [focus]` | Compress context |
| `/review` | Code review |
| `/plan [desc]` | Plan mode |
| `/model [name]` | Switch model |
| `/effort [level]` | Set reasoning depth |
| `/mcp` | Manage MCP servers |
| `/agents` | Manage subagents |
| `/exit` or Ctrl+D | End session |

## Cost Tips

1. Use `--max-turns` to prevent runaway
2. `--effort low` for simple tasks, `high`/`max` for complex reasoning
3. `/compact` when context >70%
4. Pipe input instead of having Claude read files
5. `--model haiku` for cheap tasks
6. `--fallback-model haiku` for overload handling
