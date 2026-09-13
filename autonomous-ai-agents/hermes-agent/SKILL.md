---
name: hermes-agent
description: "Configure, run, and extend Hermes Agent, the open-source multi-platform AI agent framework by Nous Research. Use when installing or setting up Hermes, finding the right hermes CLI command or slash command, spawning additional Hermes instances/subagents, configuring providers/toolsets/security/voice, troubleshooting gateway or skill issues, or contributing code to the hermes-agent project."
version: 2.1.0
author: Hermes Agent + Teknium
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [hermes, setup, configuration, multi-agent, spawning, cli, gateway, development]
    homepage: https://github.com/NousResearch/hermes-agent
    related_skills: [claude-code, codex, opencode]
---

# Hermes Agent

Hermes Agent is an open-source AI agent framework by Nous Research that runs in your terminal, messaging platforms, and IDEs. It belongs to the same category as Claude Code (Anthropic), Codex (OpenAI), and OpenClaw — autonomous coding and task-execution agents that use tool calling to interact with your system. Hermes works with any LLM provider (OpenRouter, Anthropic, OpenAI, DeepSeek, local models, and 15+ others) and runs on Linux, macOS, and WSL.

What makes Hermes different:

- **Self-improving through skills** — Hermes learns from experience by saving reusable procedures as skills. When it solves a complex problem, discovers a workflow, or gets corrected, it can persist that knowledge as a skill document that loads into future sessions. Skills accumulate over time, making the agent better at your specific tasks and environment.
- **Persistent memory across sessions** — remembers who you are, your preferences, environment details, and lessons learned. Pluggable memory backends (built-in, Honcho, Mem0, and more) let you choose how memory works.
- **Multi-platform gateway** — the same agent runs on Telegram, Discord, Slack, WhatsApp, Signal, Matrix, Email, and 10+ other platforms with full tool access, not just chat.
- **Provider-agnostic** — swap models and providers mid-workflow without changing anything else. Credential pools rotate across multiple API keys automatically.
- **Profiles** — run multiple independent Hermes instances with isolated configs, sessions, skills, and memory.
- **Extensible** — plugins, MCP servers, custom tools, webhook triggers, cron scheduling, and the full Python ecosystem.

People use Hermes for software development, research, system administration, data analysis, content creation, home automation, and anything else that benefits from an AI agent with persistent context and full system access.

**This skill helps you work with Hermes Agent effectively** — setting it up, configuring features, spawning additional agent instances, troubleshooting issues, finding the right commands and settings, and understanding how the system works when you need to extend or contribute to it.

**Docs:** https://hermes-agent.nousresearch.com/docs/

## Quick Start

```bash
# Install
curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash

# Interactive chat (default)
hermes

# Single query
hermes chat -q "What is the capital of France?"

# Setup wizard
hermes setup

# Change model/provider
hermes model

# Check health
hermes doctor
```

---

## CLI Reference

Global flags: `--resume/-r`, `--continue/-c`, `--worktree/-w` (parallel
agents), `--skills/-s`, `--profile/-p`, `--yolo`, `--pass-session-id`. No
subcommand defaults to `chat`.

| Command group | What it's for |
|---------------|----------------|
| `hermes chat` | Interactive or one-shot (`-q`) chat |
| `hermes setup` / `config` / `model` / `auth` / `doctor` / `status` | Configuration, providers, credentials, health |
| `hermes tools` / `skills` | Enable/disable toolsets, install/manage skills |
| `hermes mcp` | Add/list/test MCP servers (see [Native MCP Client](references/native-mcp.md)) |
| `hermes gateway` | Run/install/restart the messaging gateway (Telegram, Discord, Slack, WhatsApp, Signal, Email, SMS, Matrix, Mattermost, Home Assistant, DingTalk, Feishu, WeCom, BlueBubbles, Weixin, API Server, Webhooks) |
| `hermes sessions` | List/browse/export/prune sessions |
| `hermes cron` | Create/edit/pause/run scheduled jobs |
| `hermes webhook` | Subscribe/list/test webhook routes (see [Webhook Subscriptions](references/webhooks.md)) |
| `hermes profile` | Create/clone/use/export named profiles |
| `hermes auth` | Credential pools — add/list/remove/reset per provider |
| `hermes insights` / `update` / `plugins` / `memory` / `acp` / `uninstall` | Analytics, updates, plugin & memory management, IDE integration |

Every subcommand's full flags, plus the complete slash-command list
(`/help` in-session is the live source of truth): see
[CLI & Slash Command Reference](references/cli-and-slash-command-reference.md).

---

## Key Paths & Config

```
~/.hermes/config.yaml       Main configuration
~/.hermes/.env              API keys and secrets
$HERMES_HOME/skills/        Installed skills
~/.hermes/sessions/         Gateway routing index, transcripts
~/.hermes/state.db          Canonical session store (SQLite + FTS5)
~/.hermes/logs/             Gateway and error logs
~/.hermes/auth.json         OAuth tokens and credential pools
~/.hermes/hermes-agent/     Source code (if git-installed)
```

Profiles use `~/.hermes/profiles/<name>/` with the same layout. Edit config
with `hermes config edit` or `hermes config set section.key value` — key
sections: `model`, `agent`, `terminal`, `compression`, `display`, `stt`,
`tts`, `memory`, `security`, `delegation`, `checkpoints`. 20+ model providers
are supported (OpenRouter, Anthropic, Nous Portal, OpenAI Codex, GitHub
Copilot, Gemini, DeepSeek, xAI, and more), each via an API key env var or
`hermes auth`. Toolsets (`web`, `browser`, `terminal`, `file`,
`code_execution`, `vision`, `memory`, `delegation`, `cronjob`, `kanban`, …)
are enabled per-platform via `hermes tools`; changes take effect on `/reset`
only — they do NOT apply mid-conversation, to preserve prompt caching.

Full config section table, the full provider table, and the full toolset
catalog: see [Configuration & Environment Reference](references/configuration-and-environment.md).

---

## Security & Privacy Toggles

Common "why is Hermes doing X to my output / tool calls / commands?" toggles.
Most need a fresh session (`/reset`, or a new `hermes` invocation) because
they're read once at startup:

- **Secret redaction** (`security.redact_secrets`, default **on**) — scans
  all tool output for API-key/token-like strings before it enters context
  or logs. Snapshotted at import time — toggling it mid-session has no
  effect on the running process; this is deliberate, so an LLM can't flip
  it on itself mid-task.
- **PII redaction** (`privacy.redact_pii`, default **off**) — gateway-only;
  hashes user IDs and strips phone numbers before they reach the model.
- **Command approval** (`approvals.mode`) — `manual` (default, always
  prompt on destructive commands), `smart` (auxiliary LLM auto-approves
  low-risk), or `off` (equivalent to `--yolo`/`HERMES_YOLO_MODE=1`). YOLO
  does NOT disable secret redaction — they're independent.
- **Shell hooks allowlist** — `~/.hermes/shell-hooks-allowlist.json`,
  prompted interactively the first time a hook wants to run.
- **Disabling web/browser/image-gen tools** — `hermes tools`, per platform;
  takes effect on next `/reset`.

Exact commands for each toggle and the full rationale: see
[Security & Privacy Toggles](references/security-and-privacy-toggles.md).

---

## Voice & Transcription

Voice messages from messaging platforms are auto-transcribed (STT); replies
can be spoken back (TTS). STT provider priority: local faster-whisper (free)
→ Groq Whisper → OpenAI Whisper → Mistral Voxtral. TTS defaults to free Edge
TTS, with ElevenLabs/OpenAI/MiniMax/Mistral/NeuTTS as alternatives. Voice
commands: `/voice on` (voice-to-voice), `/voice tts` (always voice), `/voice off`.

Provider setup, config keys, env vars, and troubleshooting: see
[Voice & Transcription](references/voice-and-transcription.md).

---

## Spawning Additional Hermes Instances

Run additional Hermes processes as fully independent subprocesses — separate sessions, tools, and environments.

### When to Use This vs delegate_task

| | `delegate_task` | Spawning `hermes` process |
|-|-----------------|--------------------------|
| Isolation | Separate conversation, shared process | Fully independent process |
| Duration | Minutes (bounded by parent loop) | Hours/days |
| Tool access | Subset of parent's tools | Full tool access |
| Interactive | No | Yes (PTY mode) |
| Use case | Quick parallel subtasks | Long autonomous missions |

One-shot fire-and-forget uses `hermes chat -q "..."` (optionally
`background=true`); interactive multi-turn spawning needs tmux, since Hermes
uses prompt_toolkit and requires a real PTY. Prefer `-w` (worktree mode) for
any spawned agent that edits code, and prefer `delegate_task` over a full
spawned process for quick subtasks. For scheduled/recurring work use the
`cronjob` tool instead of spawning — it handles delivery and retry.

Full one-shot, tmux interactive-PTY, multi-agent coordination, and session-resume
recipes: see [Spawning Additional Instances](references/spawning-additional-instances.md).

---

## Durable & Background Systems

Four systems run alongside the main conversation loop:

- **Delegation** (`delegate_task`) — synchronous subagent spawn; parent
  waits for the child's summary. Not durable (cancelled if parent is
  interrupted); `leaf` vs `orchestrator` roles.
- **Cron** — durable scheduler (`cronjob` tool / `hermes cron` / `/cron`).
  Schedules as duration, "every" phrase, 5-field cron, or ISO timestamp;
  per-job skills/model/script/context-chaining/workdir options.
- **Curator** — background lifecycle manager for agent-created skills only
  (tracks usage, archives stale ones, never deletes, pinned skills exempt).
- **Kanban** — durable SQLite work-queue board for multi-profile/worker
  collaboration, driven by `hermes kanban` and a gated `kanban_*` toolset.

Full config knobs, CLI verbs, invariants, and isolation model for each
system: see [Durable & Background Systems](references/durable-background-systems.md).
Full developer notes also live in `AGENTS.md`, user-facing docs under
`website/docs/user-guide/features/`.

---

## Windows-Specific Quirks

Hermes runs natively on Windows (PowerShell, cmd, Windows Terminal, git-bash
mintty, VS Code integrated terminal), but a handful of Win32/POSIX
differences have bitten contributors: Alt+Enter not inserting a newline (use
Ctrl+Enter), a UTF-8 BOM in `config.yaml` causing "No models provided",
WinError 10106 from the sandbox's env scrubber dropping `SYSTEMROOT`,
`scripts/run_tests.sh` assuming a POSIX venv layout, and CRLF/line-ending
warnings.

Full explanations, workarounds, and diagnostic commands for each: see
[Windows-Specific Quirks](references/windows-quirks.md).

---

## Troubleshooting

### Voice not working
1. Check `stt.enabled: true` in config.yaml
2. Verify provider: `pip install faster-whisper` or set API key
3. In gateway: `/restart`. In CLI: exit and relaunch.

### Tool not available
1. `hermes tools` — check if toolset is enabled for your platform
2. Some tools need env vars (check `.env`)
3. `/reset` after enabling tools

### Model/provider issues
1. `hermes doctor` — check config and dependencies
2. `hermes auth` — re-authenticate OAuth providers (or `hermes auth add <provider>`)
3. Check `.env` has the right API key
4. **Copilot 403**: `gh auth login` tokens do NOT work for Copilot API. You must use the Copilot-specific OAuth device code flow via `hermes model` → GitHub Copilot.

### Changes not taking effect
- **Tools/skills:** `/reset` starts a new session with updated toolset
- **Config changes:** In gateway: `/restart`. In CLI: exit and relaunch.
- **Code changes:** Restart the CLI or gateway process

### Skills not showing
1. `hermes skills list` — verify installed
2. `hermes skills config` — check platform enablement
3. Load explicitly: `/skill name` or `hermes -s name`

### Gateway issues
Check logs first:
```bash
grep -i "failed to send\|error" ~/.hermes/logs/gateway.log | tail -20
```

Common gateway problems:
- **Gateway dies on SSH logout**: Enable linger: `sudo loginctl enable-linger $USER`
- **Gateway dies on WSL2 close**: WSL2 requires `systemd=true` in `/etc/wsl.conf` for systemd services to work. Without it, gateway falls back to `nohup` (dies when session closes).
- **Gateway crash loop**: Reset the failed state: `systemctl --user reset-failed hermes-gateway`

### Platform-specific issues
- **Discord bot silent**: Must enable **Message Content Intent** in Bot → Privileged Gateway Intents.
- **Slack bot only works in DMs**: Must subscribe to `message.channels` event. Without it, the bot ignores public channels.
- **Windows-specific issues** (`Alt+Enter` newline, WinError 10106, UTF-8 BOM config, test suite, line endings): see the dedicated **Windows-Specific Quirks** section above.

### Auxiliary models not working
If `auxiliary` tasks (vision, compression, session_search) fail silently, the `auto` provider can't find a backend. Either set `OPENROUTER_API_KEY` or `GOOGLE_API_KEY`, or explicitly configure each auxiliary task's provider:
```bash
hermes config set auxiliary.vision.provider <your_provider>
hermes config set auxiliary.vision.model <model_name>
```

---

## Where to Find Things

| Looking for... | Location |
|----------------|----------|
| Config options | `hermes config edit` or [Configuration docs](https://hermes-agent.nousresearch.com/docs/user-guide/configuration) |
| Available tools | `hermes tools list` or [Tools reference](https://hermes-agent.nousresearch.com/docs/reference/tools-reference) |
| Slash commands | `/help` in session or [Slash commands reference](https://hermes-agent.nousresearch.com/docs/reference/slash-commands) |
| Skills catalog | `hermes skills browse` or [Skills catalog](https://hermes-agent.nousresearch.com/docs/reference/skills-catalog) |
| Provider setup | `hermes model` or [Providers guide](https://hermes-agent.nousresearch.com/docs/integrations/providers) |
| Platform setup | `hermes gateway setup` or [Messaging docs](https://hermes-agent.nousresearch.com/docs/user-guide/messaging/) |
| MCP servers | `hermes mcp list` or [MCP guide](https://hermes-agent.nousresearch.com/docs/user-guide/features/mcp) |
| Profiles | `hermes profile list` or [Profiles docs](https://hermes-agent.nousresearch.com/docs/user-guide/profiles) |
| Cron jobs | `hermes cron list` or [Cron docs](https://hermes-agent.nousresearch.com/docs/user-guide/features/cron) |
| Memory | `hermes memory status` or [Memory docs](https://hermes-agent.nousresearch.com/docs/user-guide/features/memory) |
| Env variables | `hermes config env-path` or [Env vars reference](https://hermes-agent.nousresearch.com/docs/reference/environment-variables) |
| CLI commands | `hermes --help` or [CLI reference](https://hermes-agent.nousresearch.com/docs/reference/cli-commands) |
| Gateway logs | `~/.hermes/logs/gateway.log` |
| Session files | `hermes sessions browse` (reads state.db) |
| Source code | `~/.hermes/hermes-agent/` |

---

## Contributor Quick Reference

For occasional contributors and PR authors. Project layout in brief:
`run_agent.py` (core loop), `toolsets.py`, `cli.py`, `agent/` (prompt
builder, compression, memory, routing), `hermes_cli/` (CLI + slash
commands), `tools/` (one file per tool + `registry.py`), `gateway/`
(platform adapters), `cron/`, `tests/` (~3000 pytest tests).

Key rules: never break prompt caching (don't change context/tools/system
prompt mid-conversation); never two assistant or two user messages in a
row; use `get_hermes_home()` for all paths; config in `config.yaml`,
secrets in `.env`; every new tool needs a `check_fn`. Commit style:
`type: subject` (`fix:`, `feat:`, `refactor:`, `docs:`, `chore:`).

Full project layout, step-by-step guides for adding a tool or slash
command, the agent loop diagram, the test suite (including the Windows
venv workaround and cross-platform skip-guard patterns), and the
execution-environment prompt-builder internals: see
[Contributor Guide](references/contributor-guide.md) — which also links
[Authoring In-Repo Skills](references/in-repo-skill-authoring.md) for
writing or updating a bundled SKILL.md in this repo.
