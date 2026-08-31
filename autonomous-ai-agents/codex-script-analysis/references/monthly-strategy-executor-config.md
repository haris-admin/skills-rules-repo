# Monthly Strategy Executor Config & Model Routing (Aug 2026)

Decision table captured after the Aug 2, 2026 July-review run — each row cost a
debug round. The executor is `C:\Users\habib\.hermes\scripts\pluto_monthly_strategy_job.py`
(runs under Windows `py.exe`; there is NO WSL copy).

## Config keys (Windows `~/.hermes/.env`)

| Key | Value | Notes |
|-----|-------|-------|
| `MONTHLY_STRATEGY_MODEL` | `gpt-5.6-luna` (bare Codex ID) | NOT `openai/gpt-5.6-luna` — ChatGPT-auth Codex rejects the provider prefix |
| `PLUTO_MONTHLY_STRATEGY_JOB_TOKEN` or `FLY_IO_SYNCH_API_KEY_PLUTO` | 64-char token | Read into handoff JSON locally; never print |
| `MONTHLY_STRATEGY_EMAIL_TO` | hhsiddiqui@gmail.com | single copy; do NOT send a second |
| SMTP_* | Purelymail smtp.purelymail.com:587 | `.env` is authoritative — see env-shadowing pitfall |
| `OPENROUTER_API_KEY` / `OPENROUTER_API_KEY_OPENCLAW` | free-tier | fallback only for `*:free` models |

## Model routing decision

```
model name contains luna/codex/gpt-5.x  → Codex CLI `codex exec --json -m <bare-id>` (ChatGPT auth)
else                                   → OpenRouter (free-tier OK for *:free)
```

- Luna is PAID. OpenRouter free-tier key returns HTTP 402 ("can only afford N
  tokens") — that is NOT a credits problem; free-tier keys cannot spend on paid
  models. Route through Codex CLI authenticated via `codex login` (ChatGPT
  subscription covers Luna).
- Windows Codex CLI must be ≥ 0.146.0 (`npm install -g @openai/codex@latest`
  on the Windows side). 0.130.0 errors "model requires a newer version of Codex".
- `subprocess.run(["codex", ...])` from Windows Python → WinError 2. Resolve
  `shutil.which("codex") or shutil.which("codex.cmd")` and pass the full path.
- `codex exec --json` prints JSONL; parse `item.completed` → `item.text`, strip
  ``` fences, then `json.loads`. Model returns schema-drift JSON — renderers
  must be tolerant (see professional-pdf-export.md and the markdown renderer's
  `_flat_lines` which now uses `extend` not `append`).

## Config file landmines

- `~/.codex/config.toml` must NOT define `[model_providers.openai]` (reserved
  built-in; Codex refuses to load).
- Windows `~/.codex/config.toml` must not contain `service_tier = "default"`
  (unknown variant; must be `fast`/`flex` or removed).
- Stale models-cache warning (`unknown variant 'max'` for reasoning effort) is
  non-fatal.

## Env-shadowing pitfall (SMTP)

A leftover `SMTP_PASSWORD` in Windows user env (`HKCU\Environment`) is inherited
by every Windows `py.exe` process and overrides the .env value → SMTP 535
Authentication Failed even though direct login with the .env value works.
Fixes: (a) `reg delete HKCU\Environment /v SMTP_PASSWORD /f` (spawn fresh
processes; already-running process trees keep it), (b) in `executor_config()`
make `.env` authoritative for `{SMTP_PASSWORD, SMTP_USERNAME, SMTP_SERVER,
SMTP_PORT, EMAIL_FROM}` — skip os.environ merge for those keys.

## Windows-vs-WSL path visibility

Windows `py.exe` cannot see `/home/...` WSL paths. Before running:
1. Copy dated research/synthesis/actions files to
   `C:\Users\habib\.hermes\research_outputs\` so the executor auto-collects them.
2. Install job deps on the Windows interpreter too (`py -m pip install chromadb`
   for mempalace collection).
3. Handoff JSON must be at a Windows-visible path.

## Verification sequence

```
aws sts get-caller-identity            # AMLHive account = 560205084533 (IAM_MONITOR)
aws secretsmanager list-secrets        # amlhive/prod/rds EXISTS with password 44 chars
aws secretsmanager get-secret-value    # keys: password, username, host, dbname, engine, port
```

Do NOT confuse with Tapease account 707843605914 — its `tapease/rds/credentials-production`
is a different RDS instance; `amlhive_daily_report.py` fetch_pw() tries it FIRST
which is a known fallback-order pitfall for the 9:15 PM report.
