---
name: codex-script-analysis
description: Use Codex CLI from within Python scripts for inline AI-powered diagnosis, report generation, and structured analysis — not task delegation, but lightweight callouts from test runners, fleet monitors, and report scripts
version: 1.1.0
author: Pluto
license: MIT
---

# LLM-from-Script Analysis (OpenRouter primary, Codex exec for premium models)

Using LLM API calls from within Python scripts for AI-powered diagnosis, report generation, and analysis. **OpenRouter free/cheap models are the PRIMARY approach** for routine callouts. **Codex CLI exec (ChatGPT auth) is REQUIRED for premium paid models** (e.g. `gpt-5.6-luna`) that the free-tier OpenRouter key cannot afford — see "Codex CLI for premium models (Luna)" below. The OpenRouter key is free-tier ($25 cap, `is_free_tier: true`) and returns **HTTP 402** on any paid model; that is NOT a credits problem you can fix by topping up — free-tier keys simply cannot spend on paid models.

## When to Use

- A script collects raw monitoring/operational data (AWS, Docker, Sentry, DB queries) and needs AI to analyze it
- Test runner output needs root-cause diagnosis beyond simple pass/fail parsing
- Weekly code reviews that previously used codex exec
- Any structured data better analyzed by an LLM than parsed by hand-coded heuristics

## Architecture (Current — OpenRouter Primary)

```
Python script (cron / no_agent)
  │
  ├── Collects raw data (AWS API, subprocess, file I/O)
  ├── Calls: chat_with_fallback(prompt, max_tokens=2048)
  │     └── curl to OpenRouter API → response text
  └── Diagnosis written to ~/.hermes/reviews/<name>.log
```

## Core Helper Module: `~/.hermes/scripts/or_free.py`

Three-phase fallback chain — no auth maintenance needed:

**Phase 1 — Truly free models** (zero cost):
1. `google/gemma-4-31b-it:free`
2. `nvidia/nemotron-3-super-120b-a12b:free`
3. `nvidia/nemotron-3-ultra-550b-a55b:free`
4. `openrouter/free`

**Phase 2 — Cheap coding models** (< $0.0003/tok — MiniMax, Qwen, DeepSeek):
5. `qwen/qwen3-coder-30b-a3b-instruct` — coding specialist
6. `qwen/qwen3-coder-next`
7. `qwen/qwen3-coder-flash` — 1M context
8. `minimax/minimax-m2.5` — 204k context
9. `deepseek/deepseek-v4-flash` — 1M context

**Phase 3 — Our DeepSeek API** (paid, reliable):
10. `deepseek-v4-pro` via api.deepseek.com

```python
# One-line replacement for any codex exec call:
from or_free import chat_with_fallback

result = chat_with_fallback(
    f"Analyze this test failure:\n{test_output[:6000]}",
    max_tokens=1024
)
# Returns raw response text, never hangs on auth
```

Uses `OPENROUTER_API_KEY_OPENCLAW` for OpenRouter (phase 1-2) and `DEEPSEEK_API_KEY` for DeepSeek API (phase 3). Both keys already exist in `.env`.

## MCP Codex Tool Sessions (mcp__codex__codex) — translation/adaptation work

For one-shot interactive Codex sessions (NOT script callouts), use the MCP tool `mcp__codex__codex` instead of the CLI — it runs locally in WSL, no PATH/auth-in-cron issues, no Windows cmd wrapper. Verified working Aug 2026 for porting an external repo's patterns into Pluto's skills/workspaces.

Working parameter pattern:
```
approval-policy: "never"          # non-interactive
sandbox: "workspace-write"        # lets Codex edit files in cwd
model: "gpt-5.6-luna"             # or bare ID per ChatGPT-auth rules below
cwd: <project dir>                # relative resolves against server cwd
prompt: <fully self-contained task spec>
```

**The repo-translation pattern** (used for TheCraigHewitt/hermes-chief-of-staff → Pluto):
1. Clone/fetch the source repo yourself; read README + key files to extract mechanics BEFORE delegating.
2. Give Codex ONE self-contained prompt containing: source paths to read, target paths to create/modify, exact new sections to produce, real project facts to seed with, and a hard constraints list ("additive only — DO NOT touch X, Y, Z"; "do NOT modify cron jobs or production scripts").
3. Demand a REPORT BACK contract in the prompt: list of absolute paths created/modified + 3-5 line summary.
4. **Verify afterward yourself** — read the created files / grep for the new section. Codex's report is a self-report, not proof.
5. `mcp__codex__codex_reply` continues the same thread by `threadId` for follow-up edits.

If the MCP tool returns a 401 (auth), diagnose via the pitfall below (WSL Codex auth), NOT by abandoning the approach.

## Legacy: Codex exec (not recommended)

Codex CLI (`codex exec`) was the original approach but has been deprecated for script-level callouts because:
1. **Auth expires** — ChatGPT device tokens need manual re-login every few weeks
2. **Not on cron PATH** — systemd PATH doesn't include nvm node bins; requires absolute CODEX_BIN path
3. **npm install -g doesn't survive nvm version switches** — must reinstall after every `nvm install`
4. **Hangs on "Reading additional input from stdin..."** when auth is stale — blocks cron jobs for 15+ minutes

If Codex exec must be used (e.g., for interactive file-access analysis), the absolute binary path and CODEX_HOME env var are mandatory:

```python
CODEX_BIN = "/home/habib/.nvm/versions/node/v24.18.0/bin/codex"
subprocess.run(
    [CODEX_BIN, "exec", "--skip-git-repo-check", prompt],
    capture_output=True, text=True, timeout=120,
    env={**os.environ, "CODEX_HOME": str(Path.home() / ".codex")}
)
```

## Codex CLI for premium models (Luna) — REQUIRED path, Aug 2026

When a script must call a **paid premium model** (e.g. `openai/gpt-5.6-luna`, the
monthly strategy reviewer), OpenRouter free-tier 402s. The working path is the
**Codex CLI authenticated via ChatGPT** (`codex login` → ChatGPT subscription
covers Luna). Full setup, invocation, and failure transcript:
`references/codex-luna-chatgpt-auth.md`.

Key rules (each one cost a debugging round in Aug 2026):
1. **Windows Python cannot exec `codex` bare** — it resolves to `codex.CMD`;
   `subprocess.run(["codex", ...])` raises `WinError 2`. Resolve the full path:
   `exe = shutil.which("codex") or shutil.which("codex.cmd") or "codex"`.
2. **Codex with ChatGPT auth takes BARE model IDs** — `-m gpt-5.6-luna`, NOT
   OpenRouter-style `openai/gpt-5.6-luna` (rejected: "not supported when using
   Codex with a ChatGPT account").
3. **Windows Codex CLI must be ≥0.146.0** for Luna; 0.130.0 errors "model
   requires a newer version of Codex". Upgrade: `npm install -g @openai/codex@latest`
   (Windows side). WSL CLI was already 0.145+.
4. **`~/.codex/config.toml` must not define `[model_providers.openai]`** —
   built-in provider IDs are reserved; Codex refuses to load the config.
5. **Windows `~/.codex/config.toml` must not contain `service_tier = "default"`**
   (unknown variant — must be `fast`/`flex` or removed). A stale models cache
   warning (`unknown variant 'max'` for reasoning effort) is non-fatal.
6. **`codex exec --json` emits JSONL** — parse the `item.completed` lines and
   read `item.text`; strip ``` fences if present, then `json.loads`.

```python
def call_codex_luna(model, prompt):
    exe = shutil.which("codex") or shutil.which("codex.cmd") or "codex"
    exe = [exe] if os.name == "nt" and exe.lower().endswith(".cmd") else [exe]
    codex_model = model.split("/", 1)[-1] if "/" in model else model  # bare ID
    proc = subprocess.run(exe + ["exec", "--json", "-m", codex_model],
                          input=prompt.encode("utf-8"),
                          capture_output=True, timeout=1500)
    for line in proc.stdout.splitlines():
        obj = json.loads(line)
        if obj.get("type") == "item.completed":
            text = obj["item"].get("text", "")
            if text:  # strip ```json fences, then json.loads
                return json.loads(re.sub(r"^```(?:json)?\s*|\s*```$", "", text.strip(), flags=re.I))
    raise RuntimeError("codex returned no agent_message")
```

## Scripts Using This Pattern

| Script | Purpose | Approach |
|--------|---------|----------|
| `amlhive_daily_test_runner.py` | Daily pytest + diagnosis | OpenRouter via `or_free.chat_with_fallback()` |
| `a2square_weekly_test_runner.py` | Weekly pytest + Playwright + diagnosis | OpenRouter via `or_free.chat_with_fallback()` |
| `weekly_amlhive_codex_review.py` | Fri 2AM code review | Python data collection + OpenRouter analysis |
| `weekly_tapease_codex_review.py` | Tue 2AM code review | Python data collection + OpenRouter analysis |
| `amlhive_prod_monitor.py` | Fleet monitor (5/11/17/23) | `codex_report.generate_report()` → OpenRouter |
| `codex_report.py` | Fleet diagnosis helper | OpenRouter via `chat_with_fallback()` |

## Test Runner Architecture Update (July 25, 2026)

The AMLHive daily test runner was updated to use a 3-suite architecture:

**1. Backend:** `poetry run pytest tests/ -q --no-header --tb=line` (600s timeout)
   - Falls back to `.venv/bin/pytest` when `poetry` not found
   - Poetry not installed on WSL — install via `pipx install poetry` (adds `~/.local/bin` to PATH; the official installer also works). The venv fallback (`backend/.venv/bin/pytest`) is acceptable and passes identically, but the cron output shows `⚪ 'poetry' not found` noise every run — installing poetry removes it. User preference (Aug 2026): install poetry rather than accept the fallback.

**2. Frontend (Vitest):** `npm run test:unit` (300s timeout, ~30-60s typical)
   - Vitest, NOT Jest. Jest is kept in `package.json` for CI parity but is too slow on WSL.
   - No longer skipped on WSL — the repo move to native ext4 (`~/code/`) makes it viable.

**3. Playwright E2E:** `npm run test:e2e` (300s timeout, uses webServer auto-start)
   - Playwright config (`playwright.config.ts`) handles server lifecycle via `webServer` config
   - No separate `uvicorn` or `npm run dev` needed
   - First run installs Chromium: `npx playwright install chromium`

**All three run in sequence in a single script** — each has its own try/except block so a failure in one doesn't block the others. Exit code = 0 only if ALL pass.

**Repo path:** Now at `~/code/amlhive1/` (native WSL ext4) for 3x faster test execution vs `/mnt/c/`. The Windows-side repo at `/mnt/c/Code/github/amlhive-tech/amlhive1` is kept for IDE editing via VS Code WSL extension. Keep both in sync with `rsync -a /mnt/c/Code/.../ ~/code/.../`.

**Cron config:** Job `044c0bc41e31` → `workdir: /home/habib/code/amlhive1`, `script: amlhive_daily_test_runner.py`, `no_agent: true`, `deliver: origin`.

## Integration Patterns

### Test Runner Failure Diagnosis
```python
from or_free import chat_with_fallback

def codex_diagnose(label, test_output):
    prompt = (
        f"AMLHive {label} test failure. Analyze and identify root cause.\n"
        f"Reply: 1) Root cause 2) Fix steps 3) Which files\n\n{test_output[:6000]}"
    )
    diagnosis = chat_with_fallback(prompt, max_tokens=1024)
    with open(Path.home() / ".hermes" / "reviews" / "test_diagnoses.log", "a") as f:
        f.write(f"\n[{timestamp}] {label} FAILURE:\n{diagnosis}\n{'─'*60}\n")
    return diagnosis
```

### Fleet Monitor Failure Diagnosis + Exit Threshold
```python
# At end of main():
p0_count = sum(1 for a in all_alerts if a.get("severity") == P0)
p1_count = sum(1 for a in all_alerts if a.get("severity") == P1)
should_exit_1 = (p0_count > 0) or (p1_count > 15)

if should_exit_1:
    from or_free import chat_with_fallback
    dx = chat_with_fallback(f"Analyze fleet data:\n{json.dumps(data, default=str)[:8000]}")
    with open(Path.home() / ".hermes" / "reviews" / "fleet_diagnoses.log", "a") as f:
        f.write(f"\n[{timestamp}] FAILURE:\n{dx}\n{'─'*60}\n")
```

### Weekly Code Review (Data Collection + Analysis)
```python
# Phase 1: Collect repo data deterministically
data = {}
data["branch"] = subprocess.run(["git", "branch", "--show-current"], ...)
data["recent_commits"] = subprocess.run(["git", "log", "--oneline", "-20"], ...)
data["backend_pytest"] = subprocess.run([pytest_bin, "tests/", "-q", ...], ...)

# Phase 2: Send to OpenRouter for analysis
from or_free import chat_with_fallback
prompt = f"Review this codebase data:\n{json.dumps(data, default=str)[:6000]}"
report = chat_with_fallback(prompt, max_tokens=2048)
print(report)  # Stdout for cron delivery
```

## Design Decisions

| Decision | Why |
|----------|-----|
| `or_free.py` not `codex exec` | Zero auth maintenance; works from cron; no PATH issues |
| 3-phase fallback | Free→cheap coding→DeepSeek: never a single point of failure |
| `curl` in subprocess (not `requests`) | No pip dependency — works from any Python env |
| `max_tokens=1024` for diagnosis | Quick 15s response; code reviews get `2048` |
| Trim fields to 6000 chars | Controls cost while preserving signal |
| `~/.hermes/reviews/` log dir | Central archive, keeps cron delivery clean |
| `no_agent: true` cron scripts | Script runs directly — no LLM token waste on cron agent |

## Requirements

- `OPENROUTER_API_KEY_OPENCLAW` in `.env` (for OpenRouter phases)
- `DEEPSEEK_API_KEY` in `.env` (for DeepSeek fallback phase)
- Log dir: `mkdir -p ~/.hermes/reviews/`
- `or_free.py` at `~/.hermes/scripts/` (importable from any script)
- Codex CLI (legacy only): `npm install -g @openai/codex` + reinstall after every nvm Node upgrade

## Pitfalls

1. **Codex CLI auth expires periodically** — The "refresh_token_reused" error kills all codex-exec pipelines silently. Solution: use OpenRouter via `or_free.py` instead. If Codex is absolutely needed: `rm -f ~/.codex/auth.json && codex login --device-auth` + approve in browser within 15 min.
2. **"Cannot reach Pluto/WSL" from Windows Codex is usually a false problem** — When someone says the Windows-side Codex keys are valid but the failure is "on Pluto's WSL environment, unreachable (no SSH route)", check WSL itself FIRST: Codex CLI is already installed inside WSL (`/home/habib/.nvm/versions/node/v24.18.0/bin/codex`) and the MCP tool (`mcp__codex__codex`) runs locally there. The real failure is almost always **WSL Codex is not authenticated**: `codex login status` → "Not logged in", no `~/.codex/auth.json`, and the config has no `[model_providers]` block — so the MCP call 401s against `api.openai.com` with "Missing basic authentication". Diagnosis order: (a) `codex login status`, (b) `ls ~/.codex/auth.json`, (c) check `~/.codex/config.toml` for a provider block, (d) verify the key actually authenticates: `curl -s -o /dev/null -w "%{http_code}" https://openrouter.ai/api/v1/key -H "Authorization: Bearer $KEY"` → 200 means the key is fine and the problem is Codex's config, not the network. No SSH setup is needed — run Codex directly inside WSL.
2. **Cron/systemd doesn't inherit nvm PATH** — If using codex exec (legacy), always pass absolute CODEX_BIN path AND `CODEX_HOME` env var explicitly. OpenRouter path has no such issue.
3. **npm install -g doesn't survive nvm version switches** — When you `nvm use` a different Node version, global packages aren't carried over. If using Codex, reinstall: `npm install -g @openai/codex` after every nvm upgrade.
4. **Timeouts** — OpenRouter free models: 60-120s. DeepSeek API: 30-60s. Set generous timeouts in `subprocess.run()`.
5. **No sudo** — Cron scripts can't sudo. Design around this.
6. **Output size** — Keep raw data under 6K chars per call (truncate large fields).
7. **OpenRouter rate limits** — Free tier has rate limits. Fine for 4x-daily fleet monitors and weekly reviews. Not for real-time or bursty calls.
8. **Pollution of stdout** — Write diagnoses to files, not stdout, to avoid corrupting cron delivery (which delivers stdout content).
9. **Code review data collection runs from WSL** — Repos are at `/mnt/c/Code/github/...`. Some tools (npm, npx) are on the Windows side. Test runners use subprocess with cwd pointing to the Windows mount and set generous timeouts.
10. **Model availability changes** — OpenRouter's free model list changes frequently. Periodically re-check: `curl -s https://openrouter.ai/api/v1/models | python3 -c "import sys,json;[print(m['id']) for m in json.load(sys.stdin)['data'] if m['pricing']['prompt']=='0']"`
11. **Hardcoded timeout messages in test runners** — The exception handler in `amlhive_daily_test_runner.py` prints `"   ⚪ Timed out (300s)"` regardless of the actual timeout passed. If you change `timeout=600`, the message is still wrong. Fix: use f-string with the actual timeout variable.
12. **Chamber consolidation reduced 27→12 chambers** — July 25, 2026: 15 tiny ChromaDB chambers (<15 docs each) were deleted. Gmail feeder routing was updated to avoid recreating sparse chambers. See `references/chamber-consolidation-2026-07-25.md`.
13. **`poetry` vs `uv` venv mismatch** — The project backend (`pyproject.toml`) requires Python ≥3.13.12 but WSL 24.04 ships Python 3.11. Install with `uv python install 3.13 && uv venv --python 3.13`. The `dev` extras group uses Poetry format (`[tool.poetry.group.dev.dependencies]`), so `uv pip install ".[dev]"` won't work — install test deps explicitly: `uv pip install pytest pytest-asyncio pytest-timeout httpx fakeredis aiosqlite respx freezegun alembic`.
14. **Stale Windows user env vars shadow `.env` in Windows-side Python** — A leftover `HKCU\Environment` variable (e.g. an old `SMTP_PASSWORD` with the wrong value) is inherited by Windows `py.exe` processes and **overrides** the correct value in `~/.hermes/.env`, because `executor_config()` merged `os.environ` last. Symptom: direct SMTP login works, but the job fails `535 Authentication Failed`. Fixes: (a) delete the stale key `reg delete HKCU\Environment /v SMTP_PASSWORD /f` (note: already-spawned process trees keep it — spawn fresh), and (b) make `.env` authoritative for SMTP keys in `executor_config()`: skip env-var merge for `{SMTP_PASSWORD, SMTP_USERNAME, SMTP_SERVER, SMTP_PORT, EMAIL_FROM}`. General rule: treat `.env` as the source of truth for credential-shaped keys; only merge other env vars.
15. **Windows Python can't see WSL paths** — When an executor runs under Windows `py.exe`, `/home/...` paths are invisible. Copy July/dated input files to `C:\\Users\\habib\\.hermes\\research_outputs\\` before running, and pass the token/prompt via a Windows-visible temp path. Also install Python deps the job needs on the Windows interpreter too (`py -m pip install chromadb`) — a "module not installed" on the WSL venv does not help a Windows-spawned job.
16. **Auto-stash before `git pull` in cron runners** — A cron test runner that does `git pull --ff-only origin dev` dies with "cannot pull with rebase: You have unstaged changes" whenever a previous run left local edits (e.g. agent-applied test fixes). Fix the runner, not the workflow: before pulling, check `git status --porcelain`; if dirty, `git stash push -m "auto-stash before pull"`, pull, then `git stash pop` (best-effort). This keeps the 03:00 suite green even when uncommitted local fixes exist.
17. **Windows Python strftime: `%-d` is Linux-only** — `datetime.strftime('%-d %b %Y')` raises `ValueError: Invalid format string` on Windows `py.exe`. Use `strftime('%d %b %Y').lstrip('0')` instead. Any format-code portability bug that appears only when a script runs under the Windows interpreter (not WSL) belongs in this class: test date/path formatting on the actual interpreter the cron uses.
18. **Flatten nested LLM-JSON lists with `extend`, not `append`** — When rendering LLM-JSON sections to markdown, `out.append(_flat_lines(sub_list, key_map))` pushes the whole sub-list as ONE element → the report shows raw Python lists (`- ['item1', 'item2']`). Use `out.extend(...)`. Symptom seen in the monthly strategy "Next 7 days" section; verify with a regex scan for `\[.+?, .+?\]` in the final markdown.
19. **Match the project's established output format for report sections** — AMLHive reports use the "AMLHive Production After-Action — vX.Y.Z (backfilled D Mon YYYY)" heading with bold `Day N:` + indented action bullets for plan sections. When a report section has a house format, render to it; do not invent a generic `## Next 7 days` heading or dump raw structures. The after-action version/backfill can be overridden via fields on the input handoff (`after_action_version`, `after_action_backfill`).

## Reference Files

- `references/chamber-consolidation-2026-07-25.md` — 27→12 chamber consolidation (July 25, 2026)
- `references/codex-luna-chatgpt-auth.md` — Codex CLI + ChatGPT auth for premium (Luna) models: setup, invocation from Windows Python, JSONL parsing, real failure transcript (Aug 2026)
- `references/professional-html-email-pattern.md` — branded HTML email via `purelymail_sender` builders (WSL python3, NOT Windows py.exe), PDF attachment on the same MIME message, duplicate-Subject + /mnt/c path pitfalls (Aug 2026)
- `references/professional-pdf-export.md` — reportlab branded PDF export from structured/LLM JSON: header band, footers, per-structure renderers, color conversion + escaping pitfalls, vision verification loop (Aug 2026)
- `references/monthly-strategy-executor-config.md` — executor `.env` keys and the model routing decision table for the monthly strategy job (Aug 2026)
