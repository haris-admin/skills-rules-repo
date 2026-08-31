# Honcho Memory Provider — Setup & Configuration

**Date configured:** May 23, 2026
**Package:** `honcho-ai==2.0.1`
**Plugin:** `plugins/memory/honcho/` → `HonchoMemoryProvider`

## Current Configuration

### config.yaml
```yaml
memory:
  memory_enabled: true
  user_profile_enabled: true
  memory_char_limit: 2200
  user_char_limit: 1375
  provider: honcho
```

### ~/.honcho/config.json
```json
{
  "contextTokens": null,
  "contextCadence": 1,
  "dialecticCadence": 3,
  "dialecticDepth": 1,
  "dialecticReasoningLevel": "low",
  "dialecticDynamic": true,
  "dialecticMaxChars": 600,
  "recallMode": "hybrid",
  "writeFrequency": "async",
  "saveMessages": true,
  "observationMode": "directional",
  "messageMaxChars": 25000,
  "dialecticMaxInputChars": 10000,
  "sessionStrategy": "per-session"
}
```

### API Key
`HONCHO_API_KEY` in `~/.hermes/.env`. **Key source:** Haris placed the key in `C:\Users\habib\.hermes\.env` (Windows side), not in the WSL `.env`. From WSL, the Windows path is `/mnt/c/Users/habib/.hermes/.env`. This is a recurring pattern — always check BOTH locations.

## Setup Steps (if redoing)
1. `pip install honcho-ai==2.0.1` in the Hermes venv
2. Add `provider: honcho` to `memory:` section in `config.yaml`
3. Create `~/.honcho/config.json` with `recallMode: hybrid`
4. Add `HONCHO_API_KEY=sk-...` to `~/.hermes/.env`
5. Verify: `hermes memory setup` (interactive wizard alternative to steps 2-4)

## What Honcho Adds
- **Dialectic reasoning:** After every N turns, Honcho analyzes the exchange and derives insights about user preferences, habits, goals
- **Session summaries:** Awareness of what was discussed in the current session
- **Multi-agent isolation:** Pluto and Gumby get separate peer profiles
- **Recall modes:** `hybrid` (auto-inject + tools), `context` (inject only), `tools` (tools only)
- **Session strategy:** `per-session` — clean start each run

## Peer Map

Three peers configured for Honcho (self-hosted, v2.0.1, < 3.x — no peer cards supported):

| Env Var | Peer ID | Agent |
|---------|---------|-------|
| `HONCHO_REMOTE_PEER` | `pluto` | Hermes agent (Pluto) |
| `HONCHO_REMOTE_OPENCLAW_PEER` | `habibi` | OpenClaw agent (Gumby) |
| `HONCHO_REMOTE_HUMAN_PEER` | `haris` | Human user (Habib) |

All three peers respond to `honcho_context`, `honcho_search`, and `honcho_reasoning`. Peer cards are NOT supported in self-hosted Honcho < 3.x — `honcho_profile` returns empty/placeholder for all peers. This is expected, not an error. Use `honcho_context(peer="...")` to verify a peer is live.

**Env var placement:** These peer vars should go in `~/.hermes/.env`. As of May 25, 2026 they are not yet in `.env` or `config.yaml` — they're configured via Honcho's own config at `~/.honcho/config.json`.

## Tool-Level Read/Write Asymmetry (discovered May 25, 2026)

**Key finding:** Honcho tool reads work — writes do NOT. This is a persistent configuration gap, not a transient error.

| Tool | Status | Behavior |
|------|--------|----------|
| `honcho_context` | 🟢 | Works for all 3 peers. Returns recent messages. |
| `honcho_search` | 🟢 | FTS5 search across peer messages. Works. |
| `honcho_reasoning` | 🟢 | Synthesized answers. Works. |
| `honcho_conclude` | 🔴 | **Fails 100%.** "Failed to save conclusion" on all attempts. |

**Root cause (May 25, 2026 diagnosis):**
- **No local Honcho server running** — `ps aux` shows no fastapi/uvicorn/honcho process
- **No `config.toml`** — Only `config.toml.example` exists at `/home/habib/honcho/`
- **Hermes config: `honcho: {}`** — Empty Honcho config block in Hermes `config.yaml`
- **Read path works** because it goes through the memory provider plugin (`honcho-ai==2.0.1`), which injects context on every turn. The write path (`honcho_conclude`) needs the Honcho server's `/v3/.../conclusions` API endpoint — which isn't reachable without a running server.

**Current workaround:** Use Pluto's built-in `memory` tool and `skill_manage` for persistence. Honcho's dialectic layer still auto-injects context from recent messages (the hybrid recall mode handles this). Conclusion writing is non-functional until the Honcho server is configured and running.

**If fixing in future:** See Honcho CLAUDE.md at `/home/habib/honcho/CLAUDE.md` for server setup (`uv run fastapi dev src/main.py` + deriver worker). Needs: Postgres DB, Redis, config.toml with connection URIs, and auth config.

## Pitfalls
- **Key location mismatch:** Haris puts API keys in Windows-side `.env` (`C:\Users\habib\.hermes\.env`), not WSL-side. Always check `/mnt/c/Users/habib/.hermes/.env` when a key is missing.
- **`honcho-ai` must be in Hermes venv** — the system pip won't find it. Use `/home/habib/.hermes/venv/bin/pip install`.
- **First activation requires restart** — the Honcho plugin loads at Hermes startup.
- **SDK API changed in v2.0:** `Honcho(app_id=...)` no longer works. The plugin handles this internally — don't use the SDK directly unless you read the v2.0.1 docs.
- **honcho_conclude always fails** — see "Tool-Level Read/Write Asymmetry" section above. Don't rely on it for persistence; use built-in memory/skills instead until the Honcho server is running.
