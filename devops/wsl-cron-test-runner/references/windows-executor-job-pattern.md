# Windows-Executor Job Pattern (running a Windows-hosted job from WSL)

Verified 2026-08-02 while running `pluto_monthly_strategy_job.py` (lives at
`C:\Users\habib\.hermes\scripts\`) from the WSL session. Reusable for any
Windows-hosted Python executor that Hermes on WSL must drive.

## Core rules

1. **Run with the Windows interpreter, not WSL python.** The job calls
   `Path.home()/.hermes/.env` for its config. From WSL that resolves to
   `~/.hermes/.env` (missing MONTHLY_STRATEGY_*, SMTP, etc.); with
   `/mnt/c/Windows/py.exe` it resolves to `C:\Users\habib\.hermes\.env` where
   all executor keys live.
   ```bash
   /mnt/c/Windows/py.exe C:/Users/habib/.hermes/scripts/<job>.py < /path/handoff.json
   ```
2. **WSL-side files are invisible to the Windows executor.** The job scans
   `Path.home()/.hermes/research_outputs/` — on Windows that is
   `C:\Users\habib\.hermes\research_outputs\`. Before running, copy the period's
   dated files there:
   ```bash
   mkdir -p /mnt/c/Users/habib/.hermes/research_outputs
   cp ~/.hermes/research_outputs/{research,synthesis,actions,competitor_intel}_2026-07-*.json \
      /mnt/c/Users/habib/.hermes/research_outputs/
   ```
   Otherwise the job reports "No dated Pluto research outputs were found".
3. **Windows Python may lack libs the job needs** (e.g. chromadb). Install once:
   `/mnt/c/Windows/py.exe -m pip install chromadb`. Without it the job reports
   "Mempalace unavailable: ChromaDB is not installed for this executor".
4. **Verify the configured model ID against the live OpenRouter catalog before
   running.** Docs go stale: `openai-codex/gpt-5.4` returned HTTP 400 — it does
   NOT exist. Fetch `https://openrouter.ai/api/v1/models` and grep for the exact
   ID. Current valid large-context IDs include `openai/gpt-5.6-luna` (1.05M ctx),
   `openai/gpt-5.6-luna-pro`, `openai/gpt-5.4*`.

## OpenRouter free-tier 402 trap

- A free-tier key (`is_free_tier: true`, e.g. `OPENROUTER_API_KEY_OPENCLAW`)
  **cannot spend on paid models** even with `limit_remaining: $24.99`.
  OpenRouter returns `HTTP 402 "can only afford 6458 tokens"` — a credit-tier
  gate, not a balance problem. The first call can slip through; retries 402.
- Escapes: (a) point the job at a `:free` model the key can afford (e.g.
  `nvidia/nemotron-3-ultra-550b-a55b:free` 1M ctx, `openrouter/free` 200k ctx);
  (b) use a ChatGPT-authenticated Codex CLI (`C:\Users\habib\.codex\auth.json`,
  auth_mode=chatgpt) which reaches real OpenAI models — but note that invoking
  Windows `cmd.exe`/`codex exec` from a Hermes session triggers the terminal
  approval gate and needs user consent.

## Renderer/schema drift in LLM-driven jobs

- Large models return richer schemas than the job's renderer expects:
  `executive_summary` as dict instead of str, `growth_plan`/`measurement_plan`
  as dicts instead of lists of dicts with `action` keys, `next_7_days` items
  using `day_range`/`actions`.
- Symptom: `AttributeError: 'str' object has no attribute 'get'` in the
  markdown renderer — AFTER the model call succeeded and the JSON result was
  written to disk. Check `research_outputs/monthly_strategy/<period>/<run_id>.json`
  for the full model decision even when the run reported failed.
- Fix: make the renderer schema-tolerant (flatten str/dict/list items, pick
  first non-empty key from a key_map, fall back to JSON dump).

## Handoff hygiene

- Read the job token into the handoff JSON from the executor .env WITHOUT
  printing it; after writing, regex-scan the file for credential-shaped strings
  (`sk-or-v1-`, `gh[pousr]_`, `hch-v3-`) — must be zero matches.
- The job emails its report itself on success. Do NOT send a second copy from
  the agent.

## Stale Windows user env vars shadow .env in Windows-spawned Python

Verified 2026-08-02: the strategy job's final step (email) kept failing
`535 Authentication Failed` even though a direct `smtplib.login()` with the
same .env values succeeded. Root cause: a **leftover Windows user environment
variable** (`HKCU\Environment\SMTP_PASSWORD`, old wrong value) was inherited by
every Windows `py.exe` process, and the executor's `executor_config()` merged
`os.environ` AFTER `.env`, so the stale value won.

Diagnosis:
- `py -c "import os; print('SMTP_PASSWORD' in os.environ)"` → True (job sees
  the stale value even though the .env has the right one).
- Compare `job.executor_config()['SMTP_PASSWORD'][-4:]` vs the .env value —
  mismatch means an env var is shadowing.
- Check `cmd.exe /c "reg query HKCU\Environment /v SMTP_PASSWORD"`.

Fixes (do BOTH):
1. Delete the stale key: `cmd.exe /c "reg delete HKCU\Environment /v SMTP_PASSWORD /f"`.
   Note: already-spawned process trees keep the old value — spawn fresh.
2. Harden `executor_config()` so `.env` is authoritative for credential-shaped
   keys: skip the `os.environ` merge for
   `{SMTP_PASSWORD, SMTP_USERNAME, SMTP_SERVER, SMTP_PORT, EMAIL_FROM}`.

General rule for any Windows-hosted executor: treat `.env` as the source of
truth for credential-shaped keys; only let other env vars through. This bug
also explains silent SMTP failures in other Windows-side cron jobs (e.g. the
AMLHive daily business report).

## Codex+Luna routing summary (premium model path)

For the full setup and failure transcript see the `codex-script-analysis`
skill, `references/codex-luna-chatgpt-auth.md`. The one-paragraph version:
free-tier OpenRouter keys 402 on paid models, so premium models
(`gpt-5.6-luna`) must be called through the ChatGPT-authenticated Codex CLI
(`codex exec --json -m gpt-5.6-luna`) — bare model ID (no `openai/` prefix),
Windows CLI ≥0.146.0, `codex.CMD` resolved via `shutil.which`, and no
`[model_providers.openai]` / `service_tier` in config.toml.
