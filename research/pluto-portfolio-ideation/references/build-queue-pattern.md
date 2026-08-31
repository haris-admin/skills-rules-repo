# Build Queue Pattern (Codex CLI via Cron)

How to push ideation/build tasks to the "build queue" using cron jobs wrapping Codex CLI.

## Pattern Overview

Haris uses a "build queue" metaphor — instead of running tasks inline, push them as cron jobs that fire autonomously. This is the preferred approach for:
- Portfolio ideation (Codex reviews research → generates ideas)
- Phase 1 MVP builds (Codex scaffolds project files)

## WSL → Codex Invocation

Codex is installed on Windows (npm global). From WSL, invoke via `cmd.exe /c`. The prompt must be piped via stdin to avoid shell escaping issues:

```bash
# Write prompt to file first
cat > /mnt/c/Users/habib/.hermes/codex-ideation/PROMPT.txt << 'EOF'
Review the CONTEXT.md file and all JSON files in reports/...
EOF

# Pipe to Codex via cmd.exe
cat /mnt/c/Users/habib/.hermes/codex-ideation/PROMPT.txt | \
  cmd.exe /c "codex exec -C C:\Users\habib\.hermes\codex-ideation --sandbox workspace-write -" 2>&1
```

**Key flags:**
- `-C <dir>` — set working directory (Windows path)
- `--sandbox workspace-write` — auto-approve file changes in workspace (replaces deprecated `--full-auto`)
- `-` — read prompt from stdin (avoids shell quoting issues)
- `pty=true` in terminal() calls — Codex is an interactive app

**CRITICAL:** Do NOT pass the prompt as a command-line argument. Codex parses the first word as an argument, so "Read CONTEXT.md..." becomes `unexpected argument 'CONTEXT.md'`. Always use stdin piping.

## Workspace Setup

Codex requires a git repo. Create a self-contained workspace:

```bash
mkdir -p /mnt/c/Users/habib/.hermes/codex-ideation
cd /mnt/c/Users/habib/.hermes/codex-ideation
git init
git config user.email "pluto@hermes.fleet"
git config user.name "Pluto"
```

**Must use Windows-accessible path** (`/mnt/c/Users/...`). WSL-only paths (`/tmp/...`) fail with UNC path errors when `cmd.exe` is invoked.

## Context File Pattern

Always include a `CONTEXT.md` with:
- Fleet status and existing portfolio (DO NOT duplicate list)
- Key research signals (cross-domain patterns, recurring signals, latest findings)
- Market timing windows
- Constraints (AUD $250 budget, Australian-first, no overlap)
- Output format instructions

## Cron Job Creation

```bash
cronjob action=create \
  name="Codex X.X — {Task Description}" \
  schedule="2m" \
  repeat=1 \
  deliver="origin" \
  enabled_toolsets=["terminal","file","web"] \
  prompt="[Self-contained instructions: verify workspace → run Codex → collect results → deliver]"
```

The job self-cleans (fires once, delivers, completes). Remove manually if already run inline.

## Pitfalls

- Single quotes in bash `cmd.exe /c` commands are NOT quoting characters in cmd.exe — use double quotes or stdin piping
- `--full-auto` is deprecated as of Codex v0.130.0 — use `--sandbox workspace-write`
- Codex needs a git repo — `git init` in the workspace before running
- Workspace must be on Windows filesystem, not WSL-only paths
- When running via `terminal()`, always set `pty=true`
- **False "FAILED" cron status:** The cron scheduler flags any output containing "Error", "RuntimeError", or "Traceback" as FAILED. Always verify build success by checking `git log --oneline` and file inventory in the repo — do not trust the cron status label alone. Build reports should avoid leading with error-like words.
- Stagger multiple build jobs by 1-minute intervals (1m, 2m, 3m) to avoid resource contention
