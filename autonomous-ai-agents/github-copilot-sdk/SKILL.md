---
name: github-copilot-sdk
description: Embed GitHub Copilot's agentic runtime (the engine behind Copilot CLI) into a custom app via the GitHub Copilot SDK — Node/TS, Python, Go, .NET, Java, or Rust, talking JSON-RPC to a `copilot` CLI server. Use when a user wants an agent reachable from a custom app, mobile client, or cloud service rather than only inside an IDE, when evaluating "build vs. embed" for agent orchestration, or when asked about GitHub Copilot SDK, BYOK, or Build26 BRK206.
version: 1.0.0
author: Haris Habib
license: MIT
metadata:
  hermes:
    tags: [github-copilot, copilot-sdk, agent-runtime, multi-client, multi-device, byok, json-rpc]
    related_skills: [coding-agent-delegation, hermes-agent, native-mcp]
---

# GitHub Copilot SDK

Reference for the GitHub Copilot SDK (`github/copilot-sdk`, GA 1.0) — a way to
embed Copilot's production agent runtime directly into an application instead
of building your own orchestration loop. Captured from Microsoft Build 2026
session **BRK206: "Your agent, anywhere: MultiClient, MultiDevice with GitHub
Copilot SDK"**.

## What it is

- Exposes the **same engine behind GitHub Copilot CLI** as an embeddable
  runtime. Copilot handles planning, tool invocation, and file edits — you
  don't write your own agent loop.
- SDKs in 6 languages: Node.js/TypeScript, Python, Go, .NET, Java, Rust.
- Architecture: `Your Application → SDK Client → JSON-RPC → Copilot CLI
  (server mode)`. The SDK manages the CLI process lifecycle, or you can point
  it at an external CLI server.
- Supports custom agents, skills, tools, hooks, and MCP servers — same
  extension points as Copilot CLI itself.

## When to Use

- A user wants an agent embedded in their own app/product (not just usable
  inside VS Code/JetBrains/Visual Studio) — mobile, custom UI, cloud service,
  multi-device.
- Evaluating whether to build a custom agent orchestration loop vs. embedding
  an existing production-tested one.
- Question mentions "Copilot SDK", "BRK206", "embed Copilot", or "agent
  runtime portability".

**Don't use for:** in-IDE-only workflows (just use Copilot CLI/extension
directly) — the SDK's value is specifically *embedding* the runtime in a
third-party app.

## Authentication Options

| Method | Notes |
|---|---|
| GitHub signed-in user | Stored OAuth credentials from `copilot` CLI login |
| OAuth GitHub App | Pass user tokens from your own GitHub OAuth app |
| Env vars | `COPILOT_GITHUB_TOKEN`, `GH_TOKEN`, `GITHUB_TOKEN` |
| BYOK (bring your own key) | Your own API keys (OpenAI, Microsoft Foundry, Anthropic) — **no GitHub auth or subscription required in this mode**. Key-based only; no Entra ID/managed identity support. |

## Installation

```bash
npm install @github/copilot-sdk          # Node/TS
pip install github-copilot-sdk            # Python
go get github.com/github/copilot-sdk/go   # Go
dotnet add package GitHub.Copilot.SDK      # .NET
cargo add github-copilot-sdk               # Rust
# Java: com.github:copilot-sdk-java (Maven/Gradle)
```

Node.js, Python, and .NET bundle the Copilot CLI automatically. Go, Java, and
Rust require `copilot` installed separately and on `PATH` (or use their
application-level CLI bundling features).

## Billing

Same model as Copilot CLI — each prompt counts toward the Copilot usage
allowance, unless running in BYOK mode against your own provider keys.

## How This Relates to This Repo

`skills-rules-repo` and the Copilot SDK solve **orthogonal halves** of "agents
everywhere":

| | Copilot SDK | This repo |
|---|---|---|
| Portable unit | The agent runtime/engine | The skill/rules catalog |
| Fixed | Copilot's planning engine (BYOK swaps the model, not the orchestrator) | Nothing — designed to sync into any tool |
| Varies | Host app / device / client | Underlying agent runtime (Claude Code, Cursor, Antigravity, …) |
| Distribution | Language-native SDK install, JSON-RPC to a CLI server | `scripts/install.sh` sync/symlink into `.claude/`, `.cursor/`, etc. |

A Copilot-SDK-embedded agent supports custom skills — so this catalog could in
principle feed the same skill content into a Copilot-SDK app that it already
feeds into Claude Code/Cursor via `scripts/install.sh`, without the catalog
itself needing to know or care which runtime executes it.

## Further Reading

- [Copilot SDK repo](https://github.com/github/copilot-sdk) — all 6 language SDKs, getting-started guide, architecture docs
- [BRK206 session repo](https://github.com/microsoft/Build26-BRK206-your-agent-anywhere-multiclient-multidevice-with-github-copilot-sdk)
- [Copilot SDK cookbooks](https://github.com/github/awesome-copilot) — custom agents, instructions, skills, hooks, workflows, plugins

## Verification Checklist

- [ ] Confirmed the use case needs runtime *embedding* (custom app/device), not just in-IDE Copilot usage
- [ ] Picked the right language SDK and confirmed CLI bundling vs. manual install
- [ ] Decided auth method — GitHub OAuth vs. BYOK — based on whether a Copilot subscription is available
- [ ] Checked whether custom skills/tools/MCP need registering with the embedded runtime
