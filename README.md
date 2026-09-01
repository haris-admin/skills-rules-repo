# Skills & Rules Repository 🚀

A centralized, standardized catalog of AI agent skills, workspace rules, plugins, and authoring templates designed for **Antigravity**, **Claude Code**, **Cursor**, and modern AI pair-programming workflows.

[![Validate Skills and Rules](https://github.com/haris-admin/skills-rules-repo/actions/workflows/validate.yml/badge.svg)](https://github.com/haris-admin/skills-rules-repo/actions/workflows/validate.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](./LICENSE)

---

## 📑 Table of Contents

- [Overview](#-overview)
- [Repository Structure](#-repository-structure)
- [Skills Catalog](#-skills-catalog)
- [Rules Catalog](#-rules-catalog)
- [Quick Start & Installation](#-quick-start--installation)
  - [Sync to a Workspace Project](#1-sync-to-a-workspace-project)
  - [Sync Globally to Machine](#2-sync-globally-to-machine)
- [Authoring Guide](#-authoring-guide)
  - [Creating a New Skill](#creating-a-new-skill)
  - [Creating a New Rule](#creating-a-new-rule)
- [Validation & Testing](#-validation--testing)
- [Contributing](#-contributing)
- [License](#-license)

---

## 🌟 Overview

As AI coding assistants and agentic IDEs evolve, team productivity depends on modular, reusable, and version-controlled instructions. This repository provides:

- **Skills**: Step-by-step operational runbooks and workflows activated dynamically on-demand.
- **Rules**: Static guidelines, code standards, and security constraints applied across workspaces.
- **Plugins**: Bundles packaging related skills, rules, hooks, and MCP servers into single units.
- **Automation**: Validation tools and sync scripts to install and link customizations into local repositories or global configs.

---

## 🗂 Repository Structure

```text
skills-rules-repo/
├── .agents/                 # Workspace agent customizations
├── .github/workflows/       # GitHub Actions CI validation
├── plugins/                 # Packaged bundles (skills + rules + configs)
│   └── developer-essentials/
├── rules/                   # Reusable workspace guidelines
│   ├── common-coding-standards.md
│   ├── git-conventions.md
│   ├── python-style-guide.md
│   ├── security-guardrails.md
│   ├── testing-guidelines.md
│   └── typescript-style-guide.md
├── scripts/                 # Management & validation tools
│   ├── install.sh           # Sync/link script for workspaces or global configs
│   └── validate.py          # Frontmatter and structure validator
├── skills/                  # Modular on-demand agent skills
│   ├── api-design/
│   ├── code-review/
│   ├── git-workflow/
│   ├── prompt-crafting/
│   ├── refactoring-clean-code/
│   ├── security-audit/
│   └── test-driven-development/
├── templates/               # Templates for authoring new skills & rules
│   ├── plugin-template/
│   ├── rule-template.md
│   └── skill-template/
├── AGENTS.md                # Agent instruction file
├── GEMINI.md                # Workspace rule configuration
├── CONTRIBUTING.md          # Contribution guidelines
├── LICENSE                  # MIT License
└── README.md                # Repository documentation
```

---

## 📦 Skills Catalog

| Skill Name | Description | References |
| :--- | :--- | :--- |
| **[](./skills/1password/SKILL.md)** | Set up and use 1Password CLI (op). Use when installing the CLI, enabling desktop app integration, signing in (single ... | [Cli Examples](./skills/1password/references/cli-examples.md) |
| **[](./skills/accessibility/SKILL.md)** | Design, implement, and audit inclusive digital products using WCAG 2.2 Level AA | - |
| **[](./skills/ai-regression-testing/SKILL.md)** | Regression testing strategies for AI-assisted development. Sandbox-mode API testing without database dependencies, au... | - |
| **[](./skills/api-design/SKILL.md)** | >- | [Rest Guidelines](./skills/api-design/references/rest-guidelines.md) |
| **[](./skills/api-endpoints/SKILL.md)** | > | - |
| **[](./skills/apple-notes/SKILL.md)** | Manage Apple Notes via the `memo` CLI on macOS (create, view, edit, delete, search, move, and export notes). Use when... | - |
| **[](./skills/apple-reminders/SKILL.md)** | Manage Apple Reminders via the `remindctl` CLI on macOS (list, add, edit, complete, delete). Supports lists, date fil... | - |
| **[](./skills/bear-notes/SKILL.md)** | Create, search, and manage Bear notes via grizzly CLI. | - |
| **[](./skills/bird/SKILL.md)** | X/Twitter CLI for reading, searching, posting, and engagement via cookies. | - |
| **[](./research/blogwatcher/SKILL.md)** | Monitor blogs and RSS/Atom feeds for updates using the blogwatcher CLI. | - |
| **[](./skills/blucli/SKILL.md)** | BluOS CLI (blu) for discovery, playback, grouping, and volume. | - |
| **[](./skills/bluebubbles/SKILL.md)** | Build or update the BlueBubbles external channel plugin for OpenClaw (extension package, REST send/probe, webhook inb... | - |
| **[](./skills/camsnap/SKILL.md)** | Capture frames or clips from RTSP/ONVIF cameras. | - |
| **[](./skills/canvas/SKILL.md)** | Display HTML content, games, interactive visualizations, and dashboards on connected OpenClaw nodes (Mac app, iOS, An... | - |
| **[](./skills/clawhub/SKILL.md)** | Use the ClawHub CLI to search, install, update, and publish agent skills from clawhub.com. Use when you need to fetch... | - |
| **[](./skills/code-review/SKILL.md)** | >- | [Checklist](./skills/code-review/references/checklist.md) |
| **[](./skills/codebase-memory/SKILL.md)** | Build and query a persistent mental model of the codebase — architecture, patterns, dependencies, and conventions — s... | - |
| **[](./skills/coding-agent/SKILL.md)** | Run Codex CLI, Claude Code, OpenCode, or Pi Coding Agent via background process for programmatic control. | - |
| **[](./skills/deep-research/SKILL.md)** | Conduct thorough multi-source research on a topic using web search, academic sources, and codebase exploration to pro... | - |
| **[](./skills/deploy-frontend/SKILL.md)** | > | - |
| **[](./skills/discord/SKILL.md)** | Use when you need to control Discord from OpenClaw via the discord tool: send messages, react, post or upload sticker... | - |
| **[](./skills/doc-coauthoring/SKILL.md)** | Co-author documents with the student — essays, reports, lab write-ups — using scaffolded collaboration that builds th... | - |
| **[](./productivity/docx/SKILL.md)** | Read, parse, and work with DOCX/Word documents — extract content, convert to Markdown, and integrate into project wor... | - |
| **[](./skills/e2e-testing/SKILL.md)** | Playwright E2E testing patterns, Page Object Model, configuration, CI/CD integration, artifact management, and flaky ... | - |
| **[](./skills/eightctl/SKILL.md)** | Control Eight Sleep pods (status, temperature, alarms, schedules). | - |
| **[](./skills/food-order/SKILL.md)** | Reorder Foodora orders + track ETA/status with ordercli. Never confirm without explicit user approval. Triggers: orde... | - |
| **[](./skills/frontend-design/SKILL.md)** | Design and implement React UI components with Tailwind CSS, following the Sovereign OS design system and ADHD-friendl... | - |
| **[](./skills/frontend-jack/SKILL.md)** | Senior frontend developer specializing in React, Next.js, Vue, TypeScript, Tailwind CSS, and modern web development. ... | - |
| **[](./skills/gemini/SKILL.md)** | Gemini CLI for one-shot Q&A, summaries, and generation. | - |
| **[](./skills/gifgrep/SKILL.md)** | Search GIF providers with CLI/TUI, download results, and extract stills/sheets. | - |
| **[](./skills/git-workflow/SKILL.md)** | >- | [Conventional Commits](./skills/git-workflow/references/conventional-commits.md) |
| **[](./software-development/github/SKILL.md)** | "Interact with GitHub using the `gh` CLI. Use `gh issue`, `gh pr`, `gh run`, and `gh api` for issues, PRs, CI runs, a... | - |
| **[](./skills/gog/SKILL.md)** | Google Workspace CLI for Gmail, Calendar, Drive, Contacts, Sheets, and Docs. | - |
| **[](./skills/goplaces/SKILL.md)** | Query Google Places API (New) via the goplaces CLI for text search, place details, resolve, and reviews. Use for huma... | - |
| **[](./skills/grill-me/SKILL.md)** | This skill should be used when the user runs "/grill-me", asks to "grill me", "quiz me", "test my knowledge", "prep m... | - |
| **[](./skills/habib-cfo/SKILL.md)** | Startup CFO and financial analyst for business case evaluation, unit economics, runway planning, cost optimization, a... | - |
| **[](./skills/habibi/SKILL.md)** | Cloud Solution Architect for AWS/Azure/GCP architecture design, scaling strategies, security patterns, infrastructure... | - |
| **[](./skills/haris-serial-entrepreneur/SKILL.md)** | Serial entrepreneur and strategic advisor for Australian fintech/payments. Expert in pitch deck review, business mode... | - |
| **[](./email/himalaya/SKILL.md)** | "CLI to manage emails via IMAP/SMTP. Use `himalaya` to list, read, write, reply, forward, search, and organize emails... | [Message Composition](./skills/himalaya/references/message-composition.md) |
| **[](./skills/honest-failure/SKILL.md)** | "Detect and block any code path that converts broken, missing, or truncated data into a rendered success state. ALWAY... | - |
| **[](./skills/imsg/SKILL.md)** | iMessage/SMS CLI for listing chats, history, watch, and sending. | - |
| **[](./skills/jim/SKILL.md)** | Content reviewer and editor specializing in blog posts, thought leadership, technical writing, Australian English, an... | - |
| **[](./skills/lineage-auditor/SKILL.md)** | Trace every value rendered on screen back to its named data source, and flag any two surfaces showing contradictory v... | - |
| **[](./skills/local-places/SKILL.md)** | Search for places (restaurants, cafes, etc.) via Google Places API proxy on localhost. | - |
| **[](./skills/mcporter/SKILL.md)** | Use the mcporter CLI to list, configure, auth, and call MCP servers/tools directly (HTTP or stdio), including ad-hoc ... | - |
| **[](./skills/model-usage/SKILL.md)** | Use CodexBar CLI local cost usage to summarize per-model usage for Codex or Claude, including the current (most recen... | [Codexbar Cli](./skills/model-usage/references/codexbar-cli.md) |
| **[](./skills/my-defender-claude/SKILL.md)** | Security and compliance expert for code security reviews, vulnerability assessment, compliance gap analysis, and thre... | - |
| **[](./skills/nano-banana-pro/SKILL.md)** | Generate or edit images via Gemini 3 Pro Image (Nano Banana Pro). | - |
| **[](./skills/nano-pdf/SKILL.md)** | Edit PDFs with natural-language instructions using the nano-pdf CLI. | - |
| **[](./skills/nginx-change/SKILL.md)** | > | - |
| **[](./productivity/notion/SKILL.md)** | Notion API for creating and managing pages, databases, and blocks. | - |
| **[](./note-taking/obsidian/SKILL.md)** | Work with Obsidian vaults (plain Markdown notes) and automate via obsidian-cli. | - |
| **[](./skills/openai-image-gen/SKILL.md)** | Batch-generate images via OpenAI Images API. Random prompt sampler + `index.html` gallery. | - |
| **[](./skills/openai-whisper/SKILL.md)** | Local speech-to-text with the Whisper CLI (no API key). | - |
| **[](./skills/openai-whisper-api/SKILL.md)** | Transcribe audio via OpenAI Audio Transcriptions API (Whisper). | - |
| **[](./smart-home/openhue/SKILL.md)** | Control Philips Hue lights/scenes via the OpenHue CLI. | - |
| **[](./skills/oracle/SKILL.md)** | Best practices for using the oracle CLI (prompt + file bundling, engines, sessions, and file attachment patterns). | - |
| **[](./skills/ordercli/SKILL.md)** | Foodora-only CLI for checking past orders and active order status (Deliveroo WIP). | - |
| **[](./productivity/pdf/SKILL.md)** | Read, parse, and extract content from PDF files for use in the project workflow. | - |
| **[](./skills/peekaboo/SKILL.md)** | Capture and automate macOS UI with the Peekaboo CLI. | - |
| **[](./skills/prompt-crafting/SKILL.md)** | >- | [Skill Authoring](./skills/prompt-crafting/references/skill-authoring.md) |
| **[](./skills/react-patterns/SKILL.md)** | React 18/19 patterns including hooks discipline, server/client component boundaries, Suspense + error boundaries, for... | - |
| **[](./skills/react-testing/SKILL.md)** | React component testing with React Testing Library, Vitest/Jest, MSW for network mocking, accessibility assertions wi... | - |
| **[](./skills/refactoring-clean-code/SKILL.md)** | >- | [Code Smells](./skills/refactoring-clean-code/references/code-smells.md) |
| **[](./skills/resilience-tester/SKILL.md)** | Recalculates the Burrito Path when life events interfere with the schedule (illness, burnout, lost time). | - |
| **[](./skills/sag/SKILL.md)** | ElevenLabs text-to-speech with mac-style say UX. | - |
| **[](./skills/security-audit/SKILL.md)** | >- | [Owasp Top 10](./skills/security-audit/references/owasp-top-10.md) |
| **[](./skills/session-logs/SKILL.md)** | Search and analyze your own session logs (older/parent conversations) using jq. | - |
| **[](./skills/sherpa-onnx-tts/SKILL.md)** | Local text-to-speech via sherpa-onnx (offline, no cloud) | - |
| **[](./skills/skill-creator/SKILL.md)** | Create or update AgentSkills. Use when designing, structuring, or packaging skills with scripts, references, and assets. | - |
| **[](./skills/slack/SKILL.md)** | Use when you need to control Slack from OpenClaw via the slack tool, including reacting to messages or pinning/unpinn... | - |
| **[](./skills/socratic-concept-bridge/SKILL.md)** | Teases out understanding when the user is stuck rather than providing answers. | - |
| **[](./media/songsee/SKILL.md)** | Generate spectrograms and feature-panel visualizations from audio with the songsee CLI. | - |
| **[](./skills/sonoscli/SKILL.md)** | Control Sonos speakers (discover/status/play/volume/group). | - |
| **[](./skills/spotify-player/SKILL.md)** | Terminal Spotify playback/search via spogo (preferred) or spotify_player. | - |
| **[](./skills/structured-outputs-first/SKILL.md)** | Any AI endpoint that must return JSON uses Anthropic tool use (structured outputs), never text generation plus regex ... | - |
| **[](./skills/summarize/SKILL.md)** | Summarize or extract text/transcripts from URLs, podcasts, and local files (great fallback for “transcribe this YouTu... | - |
| **[](./skills/tapease-backend-deploy/SKILL.md)** | The sanctioned procedure for cutting a Tap-Ease backend release (tapease_portal_fastapi_a2square) and deploying it to the dev / staging environment on EC2. Use when asked to "release", "cut a version", "deploy the backend"... | - |
| **[](./skills/tapease-pos-clover-shift-sync/SKILL.md)** | How the Tap-Ease POS terminal integration (PAUSE / Clover partner) syncs driver shifts to the Clover Platform REST API, and how to debug it. Use when a partner reports that POST /v1/pos/shifts/start or /close returns clover_shift_id: null... | - |
| **[](./software-development/systematic-debugging/SKILL.md)** | Four-phase root-cause analysis debugging methodology — reproduce, isolate, name, fix. No symptom patches. | - |
| **[](./software-development/test-driven-development/SKILL.md)** | >- | [Testing Patterns](./software-development/test-driven-development/references/testing-patterns.md) |
| **[](./skills/things-mac/SKILL.md)** | Manage Things 3 via the `things` CLI on macOS (add/update projects+todos via URL scheme; read/search/list from the lo... | - |
| **[](./skills/tmux/SKILL.md)** | Remote-control tmux sessions for interactive CLIs by sending keystrokes and scraping pane output. | - |
| **[](./skills/trello/SKILL.md)** | Manage Trello boards, lists, and cards via the Trello REST API. | - |
| **[](./skills/verification-loop/SKILL.md)** | "A comprehensive verification system for Claude Code sessions." | - |
| **[](./skills/video-frames/SKILL.md)** | Extract frames or short clips from videos using ffmpeg. | - |
| **[](./skills/voice-call/SKILL.md)** | Start voice calls via the OpenClaw voice-call plugin. | - |
| **[](./skills/voice-coach/SKILL.md)** | Developmental Voice and Quality Coach for the student's OWN Tier 3 writing (surface name "Your Voice, Stronger"). It ... | - |
| **[](./skills/wacli/SKILL.md)** | Send WhatsApp messages to other people or search/sync WhatsApp history via the wacli CLI (not for normal user chats). | - |
| **[](./skills/weather/SKILL.md)** | Get current weather and forecasts (no API key required). | - |
| **[](./skills/wizard-cycle/SKILL.md)** | > | - |
| **[](./skills/zain-dreamer/SKILL.md)** | Business opportunity analyst who finds potential in problems. Expert in Australian market gaps, business case develop... | - |

---

## 📋 Rules Catalog

| Rule File | Scope & Summary |
| :--- | :--- |
| **[`common-coding-standards.md`](./rules/common-coding-standards.md)** | Core software engineering quality, single responsibility, defensive programming, dead code elimination. |
| **[`git-conventions.md`](./rules/git-conventions.md)** | Conventional commit format, imperative mood, branch naming schemas (`feature/*`, `fix/*`). |
| **[`security-guardrails.md`](./rules/security-guardrails.md)** | Zero hardcoded secrets, input sanitization, least privilege, safe AI tool execution. |
| **[`testing-guidelines.md`](./rules/testing-guidelines.md)** | AAA pattern (Arrange-Act-Assert), test isolation, boundary conditions, edge case coverage. |
| **[`typescript-style-guide.md`](./rules/typescript-style-guide.md)** | Strict type safety, interface vs type rules, immutability, modern ECMAScript idioms. |
| **[`python-style-guide.md`](./rules/python-style-guide.md)** | PEP 8, PEP 484/585/604 type annotations, context managers, Google/NumPy docstrings. |

---

## 🚀 Quick Start & Installation

Use the provided [`scripts/install.sh`](./scripts/install.sh) utility to sync skills and rules to your projects or global configurations.

### 1. Sync to a Workspace Project
Link all skills and rules into a target project's `.agents/` folder:
```bash
# Link all skills and rules to the current project
./scripts/install.sh --workspace /path/to/my-project

# Or install a specific skill only
./scripts/install.sh --workspace /path/to/my-project --skill code-review
```

### 2. Sync Globally to Machine
Link customizations into your global agent directory (`~/.gemini/config/`):
```bash
./scripts/install.sh --global
```

### 3. List Available Items
```bash
./scripts/install.sh --list
```

---

## ✍️ Authoring Guide

### Creating a New Skill
1. Copy the skill template:
   ```bash
   cp -r templates/skill-template skills/<my-new-skill>
   ```
2. Edit `skills/<my-new-skill>/SKILL.md` with:
   - `name`: Matches folder name.
   - `description`: Trigger instructions for the agent.
   - Numbered step-by-step procedures.

### Creating a New Rule
1. Copy the rule template:
   ```bash
   cp templates/rule-template.md rules/<my-new-rule>.md
   ```
2. Add clear directives, code patterns to follow, and anti-patterns to avoid.

---

## 🧪 Validation & Testing

Validate all skills, rules, templates, and manifests before committing:

```bash
python3 scripts/validate.py
```

---

## 🤝 Contributing

Contributions are welcome! Please check out [CONTRIBUTING.md](./CONTRIBUTING.md) for details on our workflow and guidelines.

---

## 📄 License

This repository is licensed under the [MIT License](./LICENSE).
