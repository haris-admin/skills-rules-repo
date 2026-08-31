# Codex CLI invocation from WSL — pitfalls (learned Aug 2026)

Proven working invocation for running Codex analysis jobs from WSL (synergy scans,
deep product analysis, monthly strategy). All pitfalls hit live on 2026-08-20.

## The broken PATH shim

`codex` on the default PATH resolves to a broken Windows npm shim:

```
/mnt/c/Users/habib/AppData/Roaming/npm/codex
# running it fails with: /mnt/c/Users/habib/AppData/Roaming/npm/node_modules/node/bin/node: 1: This: not found
```

**Always use the nvm binary** — export PATH first:

```bash
export PATH="$HOME/.nvm/versions/node/v24.18.0/bin:$PATH"
which codex   # → /home/habib/.nvm/versions/node/v24.18.0/bin/codex
```

## Correct invocation

```bash
cd ~/code/amlhive1                    # must be inside the trusted repo dir
codex exec --json -m gpt-5.6-terra "task prompt"
```

- `--json` for machine-readable output
- `-m gpt-5.6-terra` (or `gpt-5.6-luna`) — paid bare Codex IDs
- Run from `~/code/amlhive1` — Codex refuses to start from untrusted dirs
  ("Not inside a trusted directory")

## Pitfalls

### `-C <dir>` is NOT a cwd flag
`codex exec -C amlhive1 "..."` fails with `No such file or directory (os error 2)`.
`cd` first, then exec. There is no cwd flag.

### MCP tool times out at 300s but the job keeps running
The `mcp__codex__codex` tool returns a TimeoutError after 300s on deep multi-repo
jobs — but the Codex session keeps running server-side and completes. **After a
timeout, poll for the output file** (`ls -la <expected output path>`) instead of
assuming failure. The report appeared ~2 min after the timeout in the Aug 20 run.

### Sandbox write policy — reports land in /tmp
`codex exec` sandbox only permits writes in the repo and `/tmp`. Asking it to
write to `~/.hermes/research_outputs/` results in:
> "The requested Hermes path could not be written because the workspace policy
> only permits writes in the repo and /tmp."
...and the file appears at `/tmp/<name>` instead. **Always check /tmp and copy
back** to `~/.hermes/research_outputs/` after the run.

### `rm -rf` cleanup commands are rejected
The sandbox rejects `rm -f`/`rm -rf` style commands ("rm -f style commands are
not permitted. Use a safer approach"). Harmless — the analysis completes and the
report is written; the run just ends with ERROR lines about the failed cleanup.
Don't treat those ERROR lines as failure.

## Long-running job pattern (recommended)

For multi-minute analysis jobs (reads codebases + ChromaDB + websites):

```bash
cd ~/code/amlhive1 && export PATH="$HOME/.nvm/versions/node/v24.18.0/bin:$PATH"
codex exec --json -m gpt-5.6-terra "..."   # via terminal background=true + notify_on_complete=true
```

The completion notification arrives when done; then copy the report from /tmp.

## Evidence-pack pattern (proven Aug 20, 2026)

1. Write a detailed task prompt to `~/.hermes/scripts/<name>_prompt.md`:
   - sources to read (mempalace ChromaDB path + chamber list, live site URLs,
     codebase service/model inventory)
   - questions to answer, ranked
   - required output format + output path
2. `codex exec --json -m gpt-5.6-terra "Read <prompt file> and execute the job"`
3. After completion, `cp /tmp/<output> ~/.hermes/research_outputs/`
4. Verify the file exists + read it before delivering.

Both deep-analysis jobs on 2026-08-20 (synergy analysis + product analysis) used
this pattern successfully. Monthly strategy job (Windows-side
`pluto_monthly_strategy_job.py`) uses the same `codex exec --json -m` core with
OpenRouter `*:free` fallback.
