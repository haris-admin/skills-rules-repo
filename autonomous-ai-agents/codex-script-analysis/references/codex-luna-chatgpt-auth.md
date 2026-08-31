# Codex CLI + ChatGPT auth for premium (Luna) models — full setup

## When this path is needed

The `pluto-monthly-strategy` job (and any script needing a paid premium model)
must call e.g. `openai/gpt-5.6-luna`. The OpenRouter key
(`OPENROUTER_API_KEY_OPENCLAW`) is **free tier**: `is_free_tier: true`,
$25 limit, and returns **HTTP 402 "This request requires more credits, or fewer
max_tokens. You requested up to 65536 tokens, but can only afford 6458"** on
any paid model. Topping up the key's limit does NOT help — free-tier keys
cannot spend on paid models at all. The working path is Codex CLI
authenticated via ChatGPT (`codex login`), whose subscription covers Luna.

## One-time setup (per machine)

1. WSL side:
   ```bash
   codex login            # opens ChatGPT auth page in browser
   codex login status     # → "Logged in using ChatGPT"
   ```
   Verify Luna works (must run inside a trusted git dir):
   ```bash
   cd ~/code/amlhive1 && echo "Reply with exactly: LUNA_OK" | codex exec --json -m gpt-5.6-luna
   ```
2. Windows side (if the executor is Windows Python):
   ```bash
   npm install -g @openai/codex@latest    # ≥0.146.0 required for Luna
   codex login                            # Windows has its own auth.json
   ```
3. Config fixes (each one was a real failure):
   - `~/.codex/config.toml`: remove any `[model_providers.openai]` block —
     "model_providers contains reserved built-in provider IDs: `openai`.
     Built-in providers cannot be overridden."
   - Windows `~/.codex/config.toml`: remove `service_tier = "default"` —
     "unknown variant `default`, expected `fast` or `flex`". Remove the line
     entirely (Luna rejected `flex` too: "Unsupported service_tier: flex").
   - A models-cache warning (`unknown variant `max`, expected one of `none`…`)
     is non-fatal — Codex still runs.

## Invocation from Windows Python

`subprocess.run(["codex", ...])` fails with `WinError 2` because Windows
resolves `codex` to `codex.CMD` and bare subprocess cannot exec batch files.
Resolve explicitly:

```python
import shutil, os, subprocess
exe = shutil.which("codex") or shutil.which("codex.cmd") or "codex"
cmd = [exe] if os.name == "nt" and exe.lower().endswith(".cmd") else [exe]
# BARE model id — not openai/... prefix
proc = subprocess.run(cmd + ["exec", "--json", "-m", "gpt-5.6-luna"],
                      input=prompt.encode("utf-8"),
                      capture_output=True, timeout=1500)
```

- Wrong model id `openai/gpt-5.6-luna` → 400 "The 'openai/gpt-5.6-luna' model
  is not supported when using Codex with a ChatGPT account."
- Old CLI 0.130.0 with `gpt-5.6-luna` → 400 "requires a newer version of Codex".

## Parsing `codex exec --json` output

Output is JSONL. The answer lives in `item.completed` lines' `item.text`:

```python
import json, re
for line in proc.stdout.splitlines():
    obj = json.loads(line)
    if obj.get("type") == "item.completed":
        text = obj["item"].get("text", "")
        if text:
            text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text.strip(), flags=re.I)
            return json.loads(text)   # or keep raw text
```

Also watch for `{"type":"error",...}` lines (model/config problems) and
`turn.failed`.

## Real failure sequence (Aug 2, 2026) — what each error meant

| Error | Cause | Fix |
|-------|-------|-----|
| HTTP 400 on `openai-codex/gpt-5.4` | model id not on OpenRouter at all | use a real id |
| HTTP 402 on `openai/gpt-5.4` / `gpt-5.6-luna` via OpenRouter | free-tier key can't spend on paid models | switch to Codex CLI + ChatGPT auth |
| `model_providers contains reserved built-in provider IDs: openai` | config.toml overrode built-in | remove `[model_providers.openai]` |
| `unknown variant 'default', expected 'fast' or 'flex'` in service_tier | stale Windows config | remove service_tier line |
| `Unsupported service_tier: flex` | Luna rejects flex too | remove line entirely |
| `The 'openai/gpt-5.6-luna' model is not supported when using Codex with a ChatGPT account` | OpenRouter-style prefix not accepted | use bare `gpt-5.6-luna` |
| `The 'gpt-5.6-luna' model requires a newer version of Codex` | CLI 0.130.0 too old | `npm install -g @openai/codex@latest` (→0.146.0) |
| `WinError 2` from subprocess | `codex` = codex.CMD, bare exec fails | resolve via shutil.which |

## Model routing rule in the executor

`MONTHLY_STRATEGY_MODEL=openai/gpt-5.6-luna` (env) → executor strips prefix for
the Codex call, prefers Codex CLI for luna/codex/gpt-5.x model names, falls back
to OpenRouter only for `*:free` models. The result JSON/MD lands in
`~/.hermes/research_outputs/monthly_strategy/YYYY-MM/`.
