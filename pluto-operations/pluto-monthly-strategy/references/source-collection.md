# Source collection recipes (WSL side)

Use these existing local bridges when a direct export is not already available.
Run them with Pluto's normal runtime so their configured secrets stay local.

## Honcho

Pluto has built-in Honcho tools (honcho_search / honcho_context /
honcho_reasoning) available in-session. Query the month's relevant threads with
the local bridge as an alternative:

```bash
python3 ~/.hermes/scripts/pluto_honcho_bridge.py --status
```

For raw peer history, use the in-session `honcho_search` tool with a
month-scoped query (e.g. "July 2026 AMLHive customer feedback, competitors,
growth signals, decisions, opportunities"). Keep only items whose source date is
in the review month and preserve the original date/type in `honcho_export`. If
the representation is not date-specific, label it as a summary and include the
limitation in `context`.

Never print or paste `HONCHO_REMOTE_API_KEY`, workspace credentials, or `.env`
contents into the handoff.

## Mempalace

Check collections and search the most relevant monthly themes with the existing
bridge:

```bash
python3 ~/.hermes/scripts/pluto_mempalace_feeder.py --status
python3 ~/.hermes/scripts/pluto_mempalace_feeder.py --query "July 2026 AMLHive customer experience growth" --n-results 20
python3 ~/.hermes/scripts/pluto_mempalace_feeder.py --query "July 2026 opportunities product ideas" --n-results 20
```

ChromaDB palace path (WSL): `/mnt/c/Users/habib/.mempalace/palace` (12 chambers:
regulatory-ai, startup-vc, aie-podcast, pluto_research, fintech-aml,
cloud-infra, critical-infra, agentic-security, payments-npp, sovereign-ai,
agent-architecture, digital-identity).

For daily summaries, query each relevant date or use the local ChromaDB export
path when available. Convert each selected result into the `mempalace` record
shape in the main skill, retaining collection/chamber, date metadata, title or
topic, and document content. Include both strong positive signals and
contradictions.

## Local files

The executor automatically scans dated `research_*.json`, `synthesis_*.json`,
and `actions_*.json` files under `research_outputs/` and
`codex-ideation/reports/`. Pluto may send a compact summary in `context` while
leaving the raw dated files in place.

## Executor invocation (WSL)

```bash
python3 /mnt/c/Users/habib/.hermes/scripts/pluto_monthly_strategy_job.py < july-pluto-handoff.json
# dry run:
python3 /mnt/c/Users/habib/.hermes/scripts/pluto_monthly_strategy_job.py --dry-run < july-pluto-handoff.json
```

The executor reads its own config from `~/.hermes/.env` on the WSL side
(PLUTO_MONTHLY_STRATEGY_JOB_TOKEN or FLY_IO_SYNCH_API_KEY_PLUTO as token,
MONTHLY_STRATEGY_MODEL, SMTP creds). Outputs land in
`~/.hermes/research_outputs/monthly_strategy/YYYY-MM/`.

## Model routing (Luna/Terra via Codex CLI) — CRITICAL

`MONTHLY_STRATEGY_MODEL=gpt-5.6-luna` or `gpt-5.6-terra` are **paid** models (bare Codex IDs —
the OpenRouter-style `openai/gpt-5.6-luna` is rejected by ChatGPT-auth Codex).
The executor routes Luna-class models through the **Codex CLI** (`codex exec --json -m <model>`)
authenticated via ChatGPT (`codex login`), which covers them under the ChatGPT subscription.
Override per-run: `MONTHLY_STRATEGY_MODEL=gpt-5.6-terra python3 .../pluto_monthly_strategy_job.py`.
Any model containing `gpt-5.6`/`gpt-5.5`/`gpt-5.4`/`gpt-5.3`/`luna`/`terra`/`codex` routes to Codex CLI.
The `OPENROUTER_API_KEY_OPENCLAW` key is **free tier** ($25 cap) and cannot
afford Luna (HTTP 402). The executor routes Luna-class models through the
**Codex CLI** (`codex exec --json -m gpt-5.6-luna`) authenticated via ChatGPT
(`codex login`), which covers Luna under the ChatGPT subscription. OpenRouter is
only a fallback for `*:free` models.

Setup once per machine:
1. `codex login` (opens ChatGPT auth page) — WSL side
2. Confirm `codex login status` → "Logged in using ChatGPT"
3. Verify with: `echo "Reply with: LUNA_OK" | codex exec --json` (trusted git dir)

Pitfalls:
- `~/.codex/config.toml` must NOT define a `[model_providers.openai]` block —
  built-in providers cannot be overridden (Codex fails to load config).
- The `model = "gpt-5.6-luna"` line in config.toml is used by interactive
  Codex; the strategy job passes `-m gpt-5.6-luna` and relies on ChatGPT auth.
- Codex (ChatGPT auth) needs **bare model IDs** (`gpt-5.6-luna`), not
  OpenRouter-style `openai/gpt-5.6-luna` (rejected: "not supported when using
  Codex with a ChatGPT account").
- Windows Codex CLI must be ≥0.146.0 for Luna (`npm install -g @openai/codex@latest`);
  old 0.130.0 errors "model requires a newer version of Codex". Windows Python
  also needs the full `codex.CMD` path (bare `codex` → WinError 2).
- Windows `~/.codex/config.toml` must not contain `service_tier = "default"`
  (unknown variant, must be `fast`/`flex` or removed).
- `markdown_report` is schema-tolerant (handles dict/string/nested lists from
  Luna's richer JSON). Don't "fix" it back to strict lists.
