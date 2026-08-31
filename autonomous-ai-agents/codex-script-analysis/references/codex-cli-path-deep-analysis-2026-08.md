# Codex CLI — PATH trap + deep-analysis background job pattern (Aug 2026)

Two verified learnings from running multi-repo/knowledge-base analysis jobs
(AMLHive × Tapease × Mempalace synergy analysis, 20 Aug 2026).

## PITFALL — `codex` on PATH resolves to a broken Windows npm shim

`which codex` in WSL can return `/mnt/c/Users/habib/AppData/Roaming/npm/codex`
(a Windows npm shim) when the Windows npm dir is ahead of the nvm bin dir on
PATH. Running it fails with:

- `This: not found` (the shim tries to exec a Windows path)
- or `No such file or directory (os error 2)` for a bare invocation

**Fix — always prepend the nvm bin dir:**

```bash
export PATH="$HOME/.nvm/versions/node/v24.18.0/bin:$PATH"
codex exec --json -m gpt-5.6-terra "..."
```

Also: `codex exec` has **no `-C <dir>` flag** — passing `-C amlhive1` errors
`No such file or directory`. Instead `cd` into the trusted repo dir
(`~/code/amlhive1`) BEFORE invoking, since Codex requires a trusted directory
for file access.

## Deep-analysis background job pattern (verified)

For a multi-repo / knowledge-base analysis job (read codebases + query
ChromaDB + write a report), the working pattern:

1. **Write a self-contained task file** (`codex_*_prompt.md`) with: access
   paths, evidence inventory, the exact questions, output format, and where to
   write the report.
2. **Run via background terminal, NOT the MCP tool** (MCP `mcp__codex__codex`
   times out at 300s on deep jobs — the session keeps running but you lose the
   handle):
   ```bash
   terminal(command="cd ~/code/amlhive1 && export PATH=\"$HOME/.nvm/versions/node/v24.18.0/bin:$PATH\" && codex exec --json -m gpt-5.6-terra \"Read <prompt file> and execute...\" 2>&1 | tail -8", background=true, notify_on_complete=true, timeout=1800)
   ```
3. **The sandbox writes to /tmp, NOT the Hermes path you asked for.** Codex's
   workspace policy permits writes only in the repo cwd and `/tmp` — so the
   report lands at `/tmp/<name>.md` even when the prompt says
   `~/.hermes/research_outputs/...`. The final `item.completed` agent_message
   names the actual path. After the run completes, copy it yourself:
   ```bash
   cp /tmp/<name>.md ~/.hermes/research_outputs/
   ```
4. **Don't trust `-C` or PATH** — check `which codex` first; use the nvm
   binary explicitly.

## Diagnostic order for a failed/fast-exit codex run

1. `which codex` — if it points at `/mnt/c/...`, that's the shim trap.
2. Re-run with the nvm PATH export.
3. Check the log for `item.completed` — the report path is in the final
   agent_message.
4. If the report is at `/tmp/<name>.md`, copy it to research_outputs.
