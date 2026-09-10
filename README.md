# Skills & Rules Repository 🚀

A centralized, standardized catalog of AI agent skills, workspace rules, plugins, and authoring templates designed for **Antigravity**, **Claude Code**, **Cursor**, and modern AI pair-programming workflows.

[![Validate Skills and Rules](https://github.com/haris-admin/skills-rules-repo/actions/workflows/validate.yml/badge.svg)](https://github.com/haris-admin/skills-rules-repo/actions/workflows/validate.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](./LICENSE)

---

## 📑 Table of Contents

- [Overview](#-overview)
- [Repository Structure](#-repository-structure)
- [Early-Stage Startup Collection](#-early-stage-startup-collection)
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

## 🌱 Early-Stage Startup Collection

For idea validation, market sizing, customer discovery, competitor research,
pricing, pitch refinement, pilot planning, and founder/partner follow-up, use
the [Early-Stage Startup Collection](./collections/early-stage-startup.md).
It maps each startup question to the existing reusable skills without moving or
duplicating them. The index is plain Markdown with repository-relative links,
so it remains a shared discovery surface for Claude, Cursor, Codex, and
Hermes/Pluto.

---

## 📦 Skills Catalog

| Skill Name | Description | References |
| :--- | :--- | :--- |
| **[10-star-quality-gate](./core-methodology/10-star-quality-gate/SKILL.md)** | Review user experience and software workflows against an 8-dimension, 1-10 quality rubric inspired by Airbnb's product design framework. | - |
| **[1password](./skills/1password/SKILL.md)** | Set up and use 1Password CLI (op). Use when installing the CLI, enabling desktop app integration, signing in (single or multi-account), or… | [Cli Examples](./skills/1password/references/cli-examples.md) |
| **[accessibility](./skills/accessibility/SKILL.md)** | Design, implement, and audit inclusive digital products using WCAG 2.2 Level AA standards. Use this skill to generate semantic ARIA for Web and… | - |
| **[adversarial-reviewer](./core-methodology/adversarial-reviewer/SKILL.md)** | Perform deep, critical reviews assuming the proposed architecture or code contains subtle edge-case failures, race conditions, or security flaws. | - |
| **[agent-tooling-secrets](./agent-governance-and-git/agent-tooling-secrets/SKILL.md)** | Set up and maintain multi-agent ignore files (.cursorignore, .geminiignore, permissions.deny) to protect credentials. | - |
| **[ai-governance-framework](./compliance/ai-governance-framework/SKILL.md)** | "Use when adding/changing AI features, agents, or skills." | - |
| **[ai-regression-testing](./skills/ai-regression-testing/SKILL.md)** | Regression testing strategies for AI-assisted development. Sandbox-mode API testing without database dependencies, automated bug-check workflows, and… | - |
| **[airtable](./productivity/airtable/SKILL.md)** | Airtable REST API via curl. Records CRUD, filters, upserts. | - |
| **[alembic-migration-hygiene](./backend-and-database/alembic-migration-hygiene/SKILL.md)** | Best practices for writing zero-downtime, reversible database migrations with SQLAlchemy and Alembic. | - |
| **[alexandria-refinery](./devops/alexandria-refinery/SKILL.md)** | Operating procedure for the Alexandria knowledge-vault refinery — the 4-tier markdown curation pipeline that keeps the shared fleet vault… | [Tier And Frontmatter Contract](./devops/alexandria-refinery/references/tier-and-frontmatter-contract.md) |
| **[alt-funding-sparktoro-model](./skills/alt-funding-sparktoro-model/SKILL.md)** | Evaluate and draft SparkToro-style alternative funding — a non-VC angel raise (profit-share LLC/unit structure, capital-back-first waterfall, no… | [Australian Structuring Notes](./skills/alt-funding-sparktoro-model/references/australian-structuring-notes.md) |
| **[aml-ubo-investigation](./compliance/aml-ubo-investigation/SKILL.md)** | "AUSTRAC/FATF-compliant UBO investigation methodology using ASIC extracts, ABN Lookup, and corporate structure analysis" | - |
| **[amlhive-ai-authority](./growth/amlhive-ai-authority/SKILL.md)** | "Build AI discoverability and recommendation authority for AMLHive across ChatGPT, Claude, Gemini, and Perplexity — backlinks, review platforms… | [Ai Skepticism Pattern](./growth/amlhive-ai-authority/references/ai-skepticism-pattern.md) |
| **[amlhive-asic-sync](./devops/amlhive-asic-sync/SKILL.md)** | Use when running/debugging the AML Hive ASIC/ref-DB sync. | - |
| **[amlhive-content-drafting](./research/amlhive-content-drafting/SKILL.md)** | Use when drafting AMLHive blog posts or compliance guides. | - |
| **[amlhive-content-writing](./growth/amlhive-content-writing/SKILL.md)** | "Write AMLHive public copy within brand and CTA guardrails." | [Amlhive Content Guardrails](./growth/amlhive-content-writing/references/amlhive-content-guardrails.md) |
| **[amlhive-daily-business-report](./daily-reports/amlhive-daily-business-report/SKILL.md)** | "AML Hive Daily System Report — 9AM→9PM AEST window tracking agencies, users, screenings, KYC/KYB, matters, clients, CDD, audit, user activity with… | [Amlhive Prod Rds Schema](./daily-reports/amlhive-daily-business-report/references/amlhive-prod-rds-schema.md) |
| **[amlhive-daily-test-runner](./devops/amlhive-daily-test-runner/SKILL.md)** | Use when running the AML Hive daily test suite. | - |
| **[amlhive-prod-monitor](./devops/amlhive-prod-monitor/SKILL.md)** | AmLHive direct AWS production monitor — 4x daily script that checks EC2, Docker, RDS, CloudWatch, Sentry, and public endpoints. Produces plain-text… | [Alert Email Module](./devops/amlhive-prod-monitor/references/alert-email-module.md) |
| **[api-design](./skills/api-design/SKILL.md)** | Design RESTful APIs, OpenAPI/Swagger specifications, GraphQL schemas, and RPC interfaces following modern API design standards. Use when creating… | [Rest Guidelines](./skills/api-design/references/rest-guidelines.md) |
| **[api-endpoints](./skills/api-endpoints/SKILL.md)** | Canonical reference for every Tap-Ease API base URL — which host serves what, which one to hand to the iOS/Android/M2M teams, which one the frontend… | - |
| **[apple-notes](./skills/apple-notes/SKILL.md)** | Manage Apple Notes via the `memo` CLI on macOS (create, view, edit, delete, search, move, and export notes). Use when a user asks OpenClaw to add a… | - |
| **[apple-reminders](./skills/apple-reminders/SKILL.md)** | Manage Apple Reminders via the `remindctl` CLI on macOS (list, add, edit, complete, delete). Supports lists, date filters, and JSON/plain output. | - |
| **[architecture-diagram](./creative/architecture-diagram/SKILL.md)** | "Dark-themed SVG architecture/cloud/infra diagrams as HTML." | - |
| **[arxiv](./research/arxiv/SKILL.md)** | "Search arXiv papers by keyword, author, category, or ID." | - |
| **[ascii-art](./creative/ascii-art/SKILL.md)** | "ASCII art: pyfiglet, cowsay, boxes, image-to-ascii." | - |
| **[ascii-video](./creative/ascii-video/SKILL.md)** | "ASCII video: convert video/audio to colored ASCII MP4/GIF." | [Architecture](./creative/ascii-video/references/architecture.md) |
| **[au-sovereignty-alignment-audit](./compliance/au-sovereignty-alignment-audit/SKILL.md)** | Recurring audit that AMLHive's (and the wider portfolio's) SHIPPED solutions stay aligned with current and incoming Australian data-sovereignty… | [Au Incoming Regulation Register](./compliance/au-sovereignty-alignment-audit/references/au-incoming-regulation-register.md) |
| **[audio-transcription-wsl](./media/audio-transcription-wsl/SKILL.md)** | Transcribe .ogg notes on WSL via Whisper + Windows ffmpeg. | - |
| **[aurora-content-engine](./research/aurora-content-engine/SKILL.md)** | Aurora's content & authority engine — blog/LinkedIn drafting from Mempalace signals, citation SOV, SEO discipline. Use for any content task. | - |
| **[aws-cloudwatch-agent](./devops/aws-cloudwatch-agent/SKILL.md)** | Monitor and diagnose AWS infrastructure (EC2, Docker, CloudWatch logs/alarms) via SSM remote commands — covers CloudWatch Agent RPM recovery… | [Amlhive Account](./devops/aws-cloudwatch-agent/references/amlhive-account.md) |
| **[aws-ec2-fleet-monitoring](./aws/aws-ec2-fleet-monitoring/SKILL.md)** | "Class-level skill for EC2 fleet monitoring that survives instance recycling. Tag-based auto-discovery, SSM execution, and credential management… | [Alert Email Module](./aws/aws-ec2-fleet-monitoring/references/alert-email-module.md) |
| **[aws-toolkit-efficiency](./cloud-and-aws/aws-toolkit-efficiency/SKILL.md)** | Manage AWS cloud infrastructure, IAM profiles, CloudWatch telemetry, and EC2/ECS deployments with safety and cost-efficiency. | - |
| **[backend-diagnostics](./backend-and-database/backend-diagnostics/SKILL.md)** | Systematic protocol for isolating 500 errors, database connection failures, migration locks, and auth token exchange issues. | - |
| **[backend-doctor](./backend-and-database/backend-doctor/SKILL.md)** | Diagnose a Python backend (FastAPI, Django, Flask, or similar) that won't start, fails auth/JWT verification, can't reach its database, or fails a… | - |
| **[baoyu-infographic](./creative/baoyu-infographic/SKILL.md)** | "Infographics: 21 layouts x 21 styles (信息图, 可视化)." | [Analysis Framework](./creative/baoyu-infographic/references/analysis-framework.md) |
| **[bear-notes](./skills/bear-notes/SKILL.md)** | Create, search, and manage Bear notes via grizzly CLI. | - |
| **[bing-webmaster-tools](./devops/bing-webmaster-tools/SKILL.md)** | "Use when working with Bing Webmaster API or IndexNow pings." | - |
| **[bird](./skills/bird/SKILL.md)** | X/Twitter CLI for reading, searching, posting, and engagement via cookies. | - |
| **[blocked-page-recovery](./web/blocked-page-recovery/SKILL.md)** | "Use when a fetch fails: 403/429, paywall, WAF, bot wall." | - |
| **[blogwatcher](./research/blogwatcher/SKILL.md)** | "Monitor blogs and RSS/Atom feeds via blogwatcher-cli tool." | - |
| **[blucli](./skills/blucli/SKILL.md)** | BluOS CLI (blu) for discovery, playback, grouping, and volume. | - |
| **[bluebubbles](./skills/bluebubbles/SKILL.md)** | Build or update the BlueBubbles external channel plugin for OpenClaw (extension package, REST send/probe, webhook inbound). | - |
| **[box](./productivity/box/SKILL.md)** | Box manages cloud files, sharing, search, and metadata. | [Bulk Operations](./productivity/box/references/bulk-operations.md) |
| **[briefing-improver](./research/briefing-improver/SKILL.md)** | Pluto's self-improving morning briefing engine — action-first format, portfolio heatmaps, regulatory pulse, checklist generation, and feedback-driven… | - |
| **[building-an-exo](./skills/building-an-exo/SKILL.md)** | Apply ExO 3.0, the Intelligence Stack, and the REWRITE Playbook (OS Outline v25) to redesign a firm around AI. Use when a founder or CEO rebuilds as… | [Cold Start Learning Feeds](./skills/building-an-exo/references/cold-start-learning-feeds.md) |
| **[business-value-gems](./research/business-value-gems/SKILL.md)** | "Use when mining business/IT-value thinkers for stack ideas." | - |
| **[buy-australian-ai-partnership-watch](./research/buy-australian-ai-partnership-watch/SKILL.md)** | Standing intelligence watch on the Stone & Chalk / National AI Centre "Buy Australian AI Partnership" — its founding enterprise partners (ANZ, CBA… | [Roster](./research/buy-australian-ai-partnership-watch/references/roster.md) |
| **[caduceus-compliance-watch](./compliance/caduceus-compliance-watch/SKILL.md)** | "Use for compliance watch: PSP reform, guardrails, mapping." | - |
| **[camsnap](./skills/camsnap/SKILL.md)** | Capture frames or clips from RTSP/ONVIF cameras. | - |
| **[canvas](./skills/canvas/SKILL.md)** | Display HTML content, games, interactive visualizations, and dashboards on connected OpenClaw nodes (Mac app, iOS, Android). Use when presenting web… | - |
| **[chief-of-staff](./chief-of-staff-os/chief-of-staff/SKILL.md)** | The orchestrator — runs your daily operating rhythm, coordinates across tasks, communications, and follow-ups. Use for daily briefings, end-of-day… | - |
| **[citation-share-of-voice](./research/citation-share-of-voice/SKILL.md)** | "Measure which vendors get named by search and AI engines." | - |
| **[claude-design](./creative/claude-design/SKILL.md)** | Design one-off HTML artifacts (landing, deck, prototype). | - |
| **[clawhub](./skills/clawhub/SKILL.md)** | Use the ClawHub CLI to search, install, update, and publish agent skills from clawhub.com. Use when you need to fetch new skills on the fly, sync… | - |
| **[cloud-provider-account-research](./research/cloud-provider-account-research/SKILL.md)** | "Cloud signup research: types, verification, free tiers." | [Alibaba Cloud International](./research/cloud-provider-account-research/references/alibaba-cloud-international.md) |
| **[cloudflare-r2](./devops/cloudflare-r2/SKILL.md)** | "General-purpose Cloudflare R2 (S3-compatible object storage) operations — credential management, boto3/AWS CLI setup, public access, custom domain… | [Bing Webmaster Api](./devops/cloudflare-r2/references/bing-webmaster-api.md) |
| **[cloudflare-worker-deploy](./cloud-and-aws/cloudflare-worker-deploy/SKILL.md)** | Deploy, route, and manage Cloudflare Workers, KV bindings, and R2 storage buckets. | - |
| **[code-review](./skills/code-review/SKILL.md)** | Conduct thorough, structured code reviews and diff analysis. Use when the user asks for a code review, PR audit, pull request feedback, or code… | [Checklist](./skills/code-review/references/checklist.md) |
| **[codebase-inspection](./software-development/codebase-inspection/SKILL.md)** | "Inspect codebases w/ pygount: LOC, languages, ratios." | - |
| **[codebase-memory](./skills/codebase-memory/SKILL.md)** | Build and query a persistent mental model of the codebase — architecture, patterns, dependencies, and conventions — so future work starts informed… | - |
| **[codex-script-analysis](./autonomous-ai-agents/codex-script-analysis/SKILL.md)** | Use Codex CLI from within Python scripts for inline AI-powered diagnosis, report generation, and structured analysis — not task delegation, but… | [Chamber Consolidation 2026 07 25](./autonomous-ai-agents/codex-script-analysis/references/chamber-consolidation-2026-07-25.md) |
| **[coding-agent](./skills/coding-agent/SKILL.md)** | Run Codex CLI, Claude Code, OpenCode, or Pi Coding Agent via background process for programmatic control. | - |
| **[coding-agent-delegation](./autonomous-ai-agents/coding-agent-delegation/SKILL.md)** | Delegate coding tasks to external autonomous coding agent CLIs — Claude Code, OpenAI Codex, or OpenCode. PTY/tmux orchestration, background… | [Claude Code](./autonomous-ai-agents/coding-agent-delegation/references/claude-code.md) |
| **[comfyui](./creative/comfyui/SKILL.md)** | Generate images, video, and audio via diffusion workflows. | [Official Cli](./creative/comfyui/references/official-cli.md) |
| **[competitor-news-monitor](./research/competitor-news-monitor/SKILL.md)** | "Watch named companies for material news; cited digests." | - |
| **[compound-engineering](./core-methodology/compound-engineering/SKILL.md)** | Capture insights, drift scores, retrospectives, and learned rules from every feature to compound development velocity and reliability. | - |
| **[computer-use](./autonomous-ai-agents/computer-use/SKILL.md)** | "Drive the desktop background-first; escalate on signal." | - |
| **[copywriting](./content-growth-and-media/copywriting/SKILL.md)** | Write marketing copy for any page type: landing pages, product pages, about pages, sales pages, ads, and more. Trigger phrases: "write copy"… | - |
| **[crap-score](./core-methodology/crap-score/SKILL.md)** | Calculate and reduce Change Risk Anti-Patterns (CRAP) by measuring cyclomatic complexity against automated test coverage. | - |
| **[cross-model-review](./agent-governance-and-git/cross-model-review/SKILL.md)** | For a security- or compliance-critical design/spec review, prefer engaging a genuinely different underlying model, not just a fresh context window of… | - |
| **[daily-task-manager](./chief-of-staff-os/daily-task-manager/SKILL.md)** | Manage the canonical task file — add tasks, mark items done, reorganize priorities, review what needs doing. Use when: "add a task," "what's on my… | [Task File Format](./chief-of-staff-os/daily-task-manager/references/task-file-format.md) |
| **[daily-task-prep](./chief-of-staff-os/daily-task-prep/SKILL.md)** | Nightly task preparation — enriches tomorrow's task list with recurring items, due-date promotions, and calendar events. Designed to run… | - |
| **[data-sovereignty-market-screen](./compliance/data-sovereignty-market-screen/SKILL.md)** | Run against EVERY new idea, opportunity, venture, feature, market entry, vendor, or AI model before it gets built or before real data touches it… | [Jurisdiction Obligations](./compliance/data-sovereignty-market-screen/references/jurisdiction-obligations.md) |
| **[date-gated-crons](./devops/date-gated-crons/SKILL.md)** | "Use when a cron must fire only on a calendar condition." | - |
| **[db-performance-audit](./backend-and-database/db-performance-audit/SKILL.md)** | Inspect query execution plans, missing indexes, connection pooling health, and cache hit ratios. | - |
| **[debugging-hermes-tui-commands](./software-development/debugging-hermes-tui-commands/SKILL.md)** | "Debug Hermes TUI slash commands: Python, gateway, Ink UI." | - |
| **[deep-research](./skills/deep-research/SKILL.md)** | Conduct thorough multi-source research on a topic using web search, academic sources, and codebase exploration to produce a synthesised… | - |
| **[deploy-frontend](./skills/deploy-frontend/SKILL.md)** | The sanctioned procedure for deploying the Tap-Ease frontend to production and verifying it is actually serving. Use when asked to "deploy", "ship"… | - |
| **[design-md](./creative/design-md/SKILL.md)** | Author/validate/export Google's DESIGN.md token spec files. | - |
| **[discord](./skills/discord/SKILL.md)** | Use when you need to control Discord from OpenClaw via the discord tool: send messages, react, post or upload stickers, upload emojis, run polls… | - |
| **[doc-coauthoring](./skills/doc-coauthoring/SKILL.md)** | Co-author documents with the student — essays, reports, lab write-ups — using scaffolded collaboration that builds their writing while respecting… | - |
| **[document-to-action-items](./productivity/document-to-action-items/SKILL.md)** | "Extract cited obligations, deadlines, tasks from documents." | - |
| **[docx](./productivity/docx/SKILL.md)** | Create, read, edit, template, and review Word .docx files. | [Revisions And Comments](./productivity/docx/references/revisions-and-comments.md) |
| **[dogfood](./software-development/dogfood/SKILL.md)** | "Exploratory QA of web apps: find bugs, evidence, reports." | [Issue Taxonomy](./software-development/dogfood/references/issue-taxonomy.md) |
| **[e2e-testing](./skills/e2e-testing/SKILL.md)** | Playwright E2E testing patterns, Page Object Model, configuration, CI/CD integration, artifact management, and flaky test strategies. | - |
| **[eightctl](./skills/eightctl/SKILL.md)** | Control Eight Sleep pods (status, temperature, alarms, schedules). | - |
| **[email-inbox-triage](./email/email-inbox-triage/SKILL.md)** | "Triage an inbox: prioritize threads, draft replies safely." | - |
| **[excalidraw](./creative/excalidraw/SKILL.md)** | "Hand-drawn Excalidraw JSON diagrams (arch, flow, seq)." | [Colors](./creative/excalidraw/references/colors.md) |
| **[executive-assistant](./chief-of-staff-os/executive-assistant/SKILL.md)** | Triage inbox, draft emails, manage calendar, schedule meetings, handle routine communications. Use when: "check my inbox," "draft a reply," "schedule… | [Authority Framework](./chief-of-staff-os/executive-assistant/references/authority-framework.md) |
| **[external-api-integration](./backend-and-database/external-api-integration/SKILL.md)** | Mandatory contract validation and error handling for third-party API providers (Stripe, Dilisense, Veriff, SendGrid, etc.). | - |
| **[facebook-ads](./content-growth-and-media/facebook-ads/SKILL.md)** | Create Facebook and Meta ad campaigns, write ad copy, define audiences, and plan budgets. Use when the user asks about Facebook Ads, Instagram Ads… | - |
| **[fastapi-field-propagation](./software-development/fastapi-field-propagation/SKILL.md)** | "Add a new field end-to-end through a FastAPI backend: Pydantic model → router → service → database. Covers the 3-layer propagation pattern and… | [A2Square Dob Field Addition](./software-development/fastapi-field-propagation/references/a2square-dob-field-addition.md) |
| **[fleet-intelligence](./research/fleet-intelligence/SKILL.md)** | Cross-agent fleet intelligence gathering — how Pluto rapidly acquires context about the Gumby+Pluto dual-agent infrastructure, queries foreign agent… | [About Haris Briefing Discovery](./research/fleet-intelligence/references/about-haris-briefing-discovery.md) |
| **[food-order](./skills/food-order/SKILL.md)** | Reorder Foodora orders + track ETA/status with ordercli. Never confirm without explicit user approval. Triggers: order food, reorder, track ETA. | - |
| **[frontend-design](./skills/frontend-design/SKILL.md)** | Design and implement React UI components with Tailwind CSS, following the Sovereign OS design system and ADHD-friendly principles. | - |
| **[frontend-design-system](./frontend-and-ux/frontend-design-system/SKILL.md)** | Enforce design token consistency, component reuse, and strict WCAG 4.5:1 (text) and 3:1 (non-text) contrast compliance. | - |
| **[frontend-jack](./skills/frontend-jack/SKILL.md)** | Senior frontend developer specializing in React, Next.js, Vue, TypeScript, Tailwind CSS, and modern web development. Use for building UI components… | - |
| **[gemini](./skills/gemini/SKILL.md)** | Gemini CLI for one-shot Q&A, summaries, and generation. | - |
| **[gemini-image-generation](./content-growth-and-media/gemini-image-generation/SKILL.md)** | Generate high-quality, text-free editorial hero images and campaign visuals using Gemini Image Generation. | - |
| **[genspark-agent-orchestration](./devops/genspark-agent-orchestration/SKILL.md)** | How Pluto directs, monitors, and integrates with Genspark Claw agents (Gumby GC, etc.) — communication protocol, task delegation, credit management… | [Amlhive Social Accounts](./devops/genspark-agent-orchestration/references/amlhive-social-accounts.md) |
| **[gif-search](./media/gif-search/SKILL.md)** | "Search/download GIFs from Tenor via curl + jq." | - |
| **[gifgrep](./skills/gifgrep/SKILL.md)** | Search GIF providers with CLI/TUI, download results, and extract stills/sheets. | - |
| **[git-shared-worktree-hygiene](./agent-governance-and-git/git-shared-worktree-hygiene/SKILL.md)** | Safe git workflows for multi-agent environments: pathspec-only staging, milestone commits, and push protection. | - |
| **[git-sync](./devops/git-sync/SKILL.md)** | Multi-org Git sync pipeline — parallel pulls across GitLab (hhsiddiqui + hhsiddiqui-group) and GitHub (haris-admin) to /mnt/c/Code/gitlab/. Use when… | - |
| **[git-workflow](./skills/git-workflow/SKILL.md)** | Manage git operations, semantic commit generation, atomic branch creation, and PR descriptions. Use when the user asks to create commits, make a… | [Conventional Commits](./skills/git-workflow/references/conventional-commits.md) |
| **[github](./software-development/github/SKILL.md)** | "GitHub via gh CLI: PRs, issues, reviews, repos, auth." | [Auth](./software-development/github/references/auth.md) |
| **[github-auth](./github/github-auth/SKILL.md)** | "GitHub auth setup: HTTPS tokens, SSH keys, gh CLI login." | [Token Extraction Patterns](./github/github-auth/references/token-extraction-patterns.md) |
| **[github-code-review](./github/github-code-review/SKILL.md)** | "Review PRs: diffs, inline comments via gh or REST." | [Review Output Template](./github/github-code-review/references/review-output-template.md) |
| **[github-issue-to-pr](./github/github-issue-to-pr/SKILL.md)** | "Carry a GitHub issue to a verified PR with honest CI state." | - |
| **[github-issues](./github/github-issues/SKILL.md)** | "Create, triage, label, assign GitHub issues via gh or REST." | - |
| **[github-pr-workflow](./github/github-pr-workflow/SKILL.md)** | "GitHub PR lifecycle: branch, commit, open, CI, merge." | [Ci Troubleshooting](./github/github-pr-workflow/references/ci-troubleshooting.md) |
| **[github-repo-management](./github/github-repo-management/SKILL.md)** | "Clone/create/fork repos; manage remotes, releases." | [Codebase Inspection](./github/github-repo-management/references/codebase-inspection.md) |
| **[github-repo-pipeline](./devops/github-repo-pipeline/SKILL.md)** | Multi-org GitHub repo sync, test, and reporting pipeline. PAT-based auth, unified git sync, Docker-based test execution, weekly reporting. Use when… | - |
| **[gmail-health-check](./devops/gmail-health-check/SKILL.md)** | Use when diagnosing Gmail IMAP/credential failures. | - |
| **[godmode](./red-teaming/godmode/SKILL.md)** | "Jailbreak LLMs: Parseltongue, GODMODE, ULTRAPLINIAN." | [Jailbreak Templates](./red-teaming/godmode/references/jailbreak-templates.md) |
| **[gog](./skills/gog/SKILL.md)** | Google Workspace CLI for Gmail, Calendar, Drive, Contacts, Sheets, and Docs. | - |
| **[google-workspace](./productivity/google-workspace/SKILL.md)** | "Gmail, Calendar, Drive, Docs, Sheets via gws CLI or Python." | [Gmail Search Syntax](./productivity/google-workspace/references/gmail-search-syntax.md) |
| **[google-workspace-access](./devops/google-workspace-access/SKILL.md)** | "Use when Google Sheets/Drive access blocked or needs setup." | [Cdp Sheets Access](./devops/google-workspace-access/references/cdp-sheets-access.md) |
| **[goplaces](./skills/goplaces/SKILL.md)** | Query Google Places API (New) via the goplaces CLI for text search, place details, resolve, and reviews. Use for human-friendly place lookup or JSON… | - |
| **[grill-me](./skills/grill-me/SKILL.md)** | This skill should be used when the user runs "/grill-me", asks to "grill me", "quiz me", "test my knowledge", "prep me for the… | - |
| **[grounded-citations](./research/grounded-citations/SKILL.md)** | "Ground answers and documents in cited, verifiable sources." | [Citation Formats](./research/grounded-citations/references/citation-formats.md) |
| **[growth-tool-chain](./content-growth-and-media/growth-tool-chain/SKILL.md)** | Multi-stage research pipeline: Perplexity (discover/cite) → Antigravity (orchestrate/challenge) → IDE (implement/verify). | - |
| **[habib-cfo](./skills/habib-cfo/SKILL.md)** | Startup CFO and financial analyst for business cases, pre-revenue pricing and packaging, unit economics, pilot economics, runway planning, cost… | - |
| **[habibi](./skills/habibi/SKILL.md)** | Cloud Solution Architect for AWS/Azure/GCP architecture design, scaling strategies, security patterns, infrastructure as code, and cost optimization… | - |
| **[haris-serial-entrepreneur](./skills/haris-serial-entrepreneur/SKILL.md)** | Serial entrepreneur and strategic advisor for Australian fintech/payments. Expert in pitch refinement, business-model validation, founder-market fit… | - |
| **[herdr-agent-runtime](./autonomous-ai-agents/herdr-agent-runtime/SKILL.md)** | "Use when driving coding agents headlessly via Herdr." | - |
| **[hermes-agent](./autonomous-ai-agents/hermes-agent/SKILL.md)** | "Configure, extend, or contribute to Hermes Agent." | [In Repo Skill Authoring](./autonomous-ai-agents/hermes-agent/references/in-repo-skill-authoring.md) |
| **[hermes-agent-profiles](./autonomous-ai-agents/hermes-agent-profiles/SKILL.md)** | Use when spawning named Hermes sub-agent profiles. | [Engaging Profile Agents](./autonomous-ai-agents/hermes-agent-profiles/references/engaging-profile-agents.md) |
| **[himalaya](./email/himalaya/SKILL.md)** | "Himalaya CLI: IMAP/SMTP email from terminal." | [Configuration](./email/himalaya/references/configuration.md) |
| **[honest-failure](./skills/honest-failure/SKILL.md)** | "Detect and block any code path that converts broken, missing, or truncated data into a rendered success state. ALWAYS load when reviewing CC-T diffs… | - |
| **[hourly-version-check](./devops/hourly-version-check/SKILL.md)** | Use when diagnosing the hourly AML Hive version check. | - |
| **[html-mockup](./creative/html-mockup/SKILL.md)** | "Throwaway HTML mockups: 2-3 design variants to compare." | - |
| **[huggingface-hub](./mlops/huggingface-hub/SKILL.md)** | "HuggingFace hf CLI: search/download/upload models, datasets." | - |
| **[humanizer](./creative/humanizer/SKILL.md)** | "Humanize text: strip AI-isms and add real voice." | - |
| **[ideation](./creative/ideation/SKILL.md)** | "Generate project ideas via creative constraints." | [Full Prompt Library](./creative/ideation/references/full-prompt-library.md) |
| **[implementer-neutral-handover](./agent-governance-and-git/implementer-neutral-handover/SKILL.md)** | Write build-handover notes addressed to "whichever agent implements this," and file your own review/critique findings inside the artifact's own… | - |
| **[imsg](./skills/imsg/SKILL.md)** | iMessage/SMS CLI for listing chats, history, watch, and sending. | - |
| **[inspecting-hermes-desktop-dom](./software-development/inspecting-hermes-desktop-dom/SKILL.md)** | "Read the live Hermes desktop DOM/CSS over CDP." | - |
| **[jeff-dean-latency-audit](./frontend-and-ux/jeff-dean-latency-audit/SKILL.md)** | Audit web application performance across the full stack using latency-budget hierarchies (L1 cache -> Memory -> Redis -> DB -> Network). | - |
| **[jim](./skills/jim/SKILL.md)** | Content reviewer and editor specializing in blog posts, thought leadership, technical writing, Australian English, and viral content creation. Use… | - |
| **[jupyter-live-kernel](./data-science/jupyter-live-kernel/SKILL.md)** | "Iterative Python via live Jupyter kernel (hamelnb)." | - |
| **[kanban-codex-lane](./autonomous-ai-agents/kanban-codex-lane/SKILL.md)** | Use when a Hermes Kanban worker wants to run Codex CLI as an isolated implementation lane while Hermes keeps ownership of task lifecycle… | - |
| **[kanban-orchestrator](./devops/kanban-orchestrator/SKILL.md)** | Decomposition playbook + anti-temptation rules for an orchestrator profile routing work through Kanban. The "don't do the work yourself" rule and the… | - |
| **[kanban-worker](./devops/kanban-worker/SKILL.md)** | Pitfalls, examples, and edge cases for Hermes Kanban workers. The lifecycle itself is auto-injected into every worker's system prompt as… | - |
| **[knowledge-base-maintenance](./devops/knowledge-base-maintenance/SKILL.md)** | "Use when deduping or auditing a vector knowledge base." | [Mempalace Dedup Audit 2026 08](./devops/knowledge-base-maintenance/references/mempalace-dedup-audit-2026-08.md) |
| **[lighthouse-performance-gate](./frontend-and-ux/lighthouse-performance-gate/SKILL.md)** | Enforce strict performance, accessibility, best practices, and SEO benchmarks on frontend builds. | - |
| **[lineage-auditor](./skills/lineage-auditor/SKILL.md)** | Trace every value rendered on screen back to its named data source, and flag any two surfaces showing contradictory values for the same fact. ALWAYS… | - |
| **[linear](./productivity/linear/SKILL.md)** | "Linear: manage issues, projects, teams via GraphQL + curl." | - |
| **[llm-cost-routing](./mlops/llm-cost-routing/SKILL.md)** | "Pick cost-effective LLM fallbacks across providers." | [Alibaba Cloud Qwen Access](./mlops/llm-cost-routing/references/alibaba-cloud-qwen-access.md) |
| **[llm-provider-evaluation](./mlops/llm-provider-evaluation/SKILL.md)** | "Pick LLM providers for Hermes: pricing, access, free tiers, hosted inference providers (DeepInfra/SiliconFlow/Novita/Together), Qwen/QAN ecosystem… | [Hosted Provider Survey 2026 08](./mlops/llm-provider-evaluation/references/hosted-provider-survey-2026-08.md) |
| **[llm-wiki](./research/llm-wiki/SKILL.md)** | "Karpathy's LLM Wiki: build/query interlinked markdown KB." | - |
| **[local-places](./skills/local-places/SKILL.md)** | Search for places (restaurants, cafes, etc.) via Google Places API proxy on localhost. | - |
| **[lumen-palace-keeper](./note-taking/lumen-palace-keeper/SKILL.md)** | Lumen's mempalace health protocol — ingestion QA, dedup, synthesis, daily learning. Use for any knowledge-base or mempalace task. | - |
| **[manim-video](./creative/manim-video/SKILL.md)** | "Manim CE animations: 3Blue1Brown math/algo videos." | [Animation Design Thinking](./creative/manim-video/references/animation-design-thinking.md) |
| **[maps](./productivity/maps/SKILL.md)** | "Geocode, POIs, routes, timezones via OpenStreetMap/OSRM." | - |
| **[mcporter](./skills/mcporter/SKILL.md)** | Use the mcporter CLI to list, configure, auth, and call MCP servers/tools directly (HTTP or stdio), including ad-hoc servers, config edits, and… | - |
| **[meeting-action-items](./productivity/meeting-action-items/SKILL.md)** | "Turn meeting notes into cited decisions, owners, tickets." | - |
| **[merge-reconciler](./autonomous-ai-agents/merge-reconciler/SKILL.md)** | "Neutral third-party resolution of agent merge conflicts." | - |
| **[minecraft-modpack-server](./gaming/minecraft-modpack-server/SKILL.md)** | "Host modded Minecraft servers (CurseForge, Modrinth)." | - |
| **[model-usage](./skills/model-usage/SKILL.md)** | Use CodexBar CLI local cost usage to summarize per-model usage for Codex or Claude, including the current (most recent) model or a full model… | [Codexbar Cli](./skills/model-usage/references/codexbar-cli.md) |
| **[my-defender-claude](./skills/my-defender-claude/SKILL.md)** | Security and compliance expert for code security reviews, vulnerability assessment, compliance gap analysis, and threat modeling. Expertise in OWASP… | - |
| **[nano-banana-pro](./skills/nano-banana-pro/SKILL.md)** | Generate or edit images via Gemini 3 Pro Image (Nano Banana Pro). | - |
| **[nano-pdf](./skills/nano-pdf/SKILL.md)** | Edit PDFs with natural-language instructions using the nano-pdf CLI. | - |
| **[native-mcp](./mcp/native-mcp/SKILL.md)** | "MCP client: connect servers, register tools (stdio/HTTP)." | - |
| **[neurodiverse-visual-specs](./skills/neurodiverse-visual-specs/SKILL.md)** | Author multi-modal, visual-first change companions, simple slide presentations, and executive visual reports for technical proposals, security… | - |
| **[nginx-change](./skills/nginx-change/SKILL.md)** | How to safely change the production edge nginx config for tapease.com.au — add a location/route, change an upstream, adjust headers/SSL/redirects… | - |
| **[node-inspect-debugger](./software-development/node-inspect-debugger/SKILL.md)** | "Debug Node.js via --inspect + Chrome DevTools Protocol CLI." | - |
| **[notification-coverage-audit](./observability-and-sentry/notification-coverage-audit/SKILL.md)** | Audit event notifications, email alerts, and in-app trays to ensure 100% deep-link completeness and trigger coverage. | - |
| **[notion](./productivity/notion/SKILL.md)** | "Notion API + ntn CLI: pages, databases, markdown, Workers." | [Block Types](./productivity/notion/references/block-types.md) |
| **[obsidian](./note-taking/obsidian/SKILL.md)** | Read, search, create, and edit notes in the Obsidian vault. | - |
| **[ocr-and-documents](./productivity/ocr-and-documents/SKILL.md)** | "Extract text from PDFs/scans (pymupdf, marker-pdf)." | - |
| **[openai-image-gen](./skills/openai-image-gen/SKILL.md)** | Batch-generate images via OpenAI Images API. Random prompt sampler + `index.html` gallery. | - |
| **[openai-whisper](./skills/openai-whisper/SKILL.md)** | Local speech-to-text with the Whisper CLI (no API key). | - |
| **[openai-whisper-api](./skills/openai-whisper-api/SKILL.md)** | Transcribe audio via OpenAI Audio Transcriptions API (Whisper). | - |
| **[openhue](./smart-home/openhue/SKILL.md)** | "Control Philips Hue lights, scenes, rooms via OpenHue CLI." | - |
| **[openspec-workflow](./core-methodology/openspec-workflow/SKILL.md)** | Structure complex multi-agent features into structured proposals, design documents, executable tasks, and verification gates. | - |
| **[oracle](./skills/oracle/SKILL.md)** | Best practices for using the oracle CLI (prompt + file bundling, engines, sessions, and file attachment patterns). | - |
| **[ordercli](./skills/ordercli/SKILL.md)** | Foodora-only CLI for checking past orders and active order status (Deliveroo WIP). | - |
| **[p5js](./creative/p5js/SKILL.md)** | "p5.js sketches: gen art, shaders, interactive, 3D." | [Animation](./creative/p5js/references/animation.md) |
| **[pdf](./productivity/pdf/SKILL.md)** | "PDF files: create, read, merge, fill, OCR, edit text." | [Forms](./productivity/pdf/references/forms.md) |
| **[peekaboo](./skills/peekaboo/SKILL.md)** | Capture and automate macOS UI with the Peekaboo CLI. | - |
| **[petdex](./productivity/petdex/SKILL.md)** | Install and select animated petdex mascots for Hermes. | - |
| **[pixel-art](./creative/pixel-art/SKILL.md)** | "Pixel art w/ era palettes (NES, Game Boy, PICO-8)." | [Palettes](./creative/pixel-art/references/palettes.md) |
| **[plan](./software-development/plan/SKILL.md)** | Write a markdown plan to .hermes/plans/; no execution. | - |
| **[pluto-amlhive-operating-contract](./pluto-operations/pluto-amlhive-operating-contract/SKILL.md)** | "Canonical operating contract for Pluto — AMLHive SEO, AI discovery, blog and social operations" | [Ai Visibility Check](./pluto-operations/pluto-amlhive-operating-contract/references/ai-visibility-check.md) |
| **[pluto-autonomous-research](./research/pluto-autonomous-research/SKILL.md)** | Pluto's autonomous deep research pipeline — web search, synthesize, structure, and feed into ChromaDB mempalace. Use when doing self-directed… | [Anti Regulation Signal Sources](./research/pluto-autonomous-research/references/anti-regulation-signal-sources.md) |
| **[pluto-communication-protocol](./devops/pluto-communication-protocol/SKILL.md)** | Pluto's Telegram communication protocol — strict 3-tier message format (ACTION/DECISION/FYI), digest batching, and anti-flood rules. Use for EVERY… | - |
| **[pluto-content-firewall](./research/pluto-content-firewall/SKILL.md)** | Content firewall rules for all agents working on Haris Habib's blog content. Defines what can and cannot be mentioned in harishabib.au blog posts… | [Compliance Sweep](./research/pluto-content-firewall/references/compliance-sweep.md) |
| **[pluto-crap-score-runner](./devops/pluto-crap-score-runner/SKILL.md)** | Use when running the AMLHive weekly CRAP score scan. | - |
| **[pluto-daily-learning](./pluto-operations/pluto-daily-learning/SKILL.md)** | "Daily learning cron. Query Supabase, dedup, teach, quiz." | - |
| **[pluto-daily-maintenance](./devops/pluto-daily-maintenance/SKILL.md)** | Pluto's lightweight daily maintenance engine — 4-task health check (skills, memory, cron, scripts) run at 2:00 PM AEST. Focus on keeping things… | - |
| **[pluto-fleet-monitor](./devops/pluto-fleet-monitor/SKILL.md)** | "★ Pluto Fleet Monitor — AMLHive AWS Production. EC2, Docker, RDS, CloudWatch, Sentry, public endpoints. Fly.io + Vercel RETIRED Aug 2026 — checks… | [Alert Patterns And Sources](./devops/pluto-fleet-monitor/references/alert-patterns-and-sources.md) |
| **[pluto-gmail-signal-ingestion](./research/pluto-gmail-signal-ingestion/SKILL.md)** | Pluto's Gmail signal ingestion pipeline — pulls Perplexity Tasks and other briefing emails via Python imaplib, extracts signals, and feeds to the… | [Env Credential Pattern](./research/pluto-gmail-signal-ingestion/references/env-credential-pattern.md) |
| **[pluto-honcho-signal-bridge](./devops/pluto-honcho-signal-bridge/SKILL.md)** | Pluto's Honcho signal bridge — pushes structured [pluto] signal cards to Honcho memory layer, tracks push state, and handles duplicate prevention… | - |
| **[pluto-linkedin-content-engine](./research/pluto-linkedin-content-engine/SKILL.md)** | Pluto's LinkedIn and blog content ideation engine — generates social media post drafts and blog ideas from research signals, mapped to Haris's… | [Amlhive Content Workflow](./research/pluto-linkedin-content-engine/references/amlhive-content-workflow.md) |
| **[pluto-mempalace-bridge](./devops/pluto-mempalace-bridge/SKILL.md)** | Pluto-Mempalace dual-agent knowledge bridge — ChromaDB feeder, Gumby query interface, and autonomous research pipeline. Use when working with the… | [16 Chamber Architecture](./devops/pluto-mempalace-bridge/references/16-chamber-architecture.md) |
| **[pluto-monthly-strategy](./pluto-operations/pluto-monthly-strategy/SKILL.md)** | Package Pluto's monthly Honcho and Mempalace intelligence for the authenticated AMLHive strategy review job. Use at month end or when asked for a… | [Source Collection](./pluto-operations/pluto-monthly-strategy/references/source-collection.md) |
| **[pluto-monthly-strategy-review](./pluto-operations/pluto-monthly-strategy-review/SKILL.md)** | "Monthly strategy review: evidence, gaps, ≤3 priorities." | [Evidence Map](./pluto-operations/pluto-monthly-strategy-review/references/evidence-map.md) |
| **[pluto-morning-briefing](./research/pluto-morning-briefing/SKILL.md)** | Pluto's morning briefing compilation and delivery — the output-side of the research pipeline. Use when compiling the daily brief, writing… | [Daily Learning Format](./research/pluto-morning-briefing/references/daily-learning-format.md) |
| **[pluto-morning-briefing-v2](./research/pluto-morning-briefing-v2/SKILL.md)** | Pluto's redesigned morning briefing — action-first, scannable, self-improving. Uses briefing_improver.py engine. The "Option C" briefing that wows. | [Design Rationale](./research/pluto-morning-briefing-v2/references/design-rationale.md) |
| **[pluto-performance-tracker](./devops/pluto-performance-tracker/SKILL.md)** | Pluto Daily Performance Tracker — collects cron health, pipeline output counts, error rates, and repo status into weekly JSON snapshots for the… | - |
| **[pluto-pipeline-orchestration](./devops/pluto-pipeline-orchestration/SKILL.md)** | Pluto's 35-stage cron pipeline orchestration — the full morning-to-night chain from Podcast Ingestion through Git Sync, Gmail, Research, Synthesis… | [Alert Email Pattern](./devops/pluto-pipeline-orchestration/references/alert-email-pattern.md) |
| **[pluto-portfolio-ideation](./research/pluto-portfolio-ideation/SKILL.md)** | Pluto's portfolio ideation engine — generates new startup/project ideas from research signals by mapping market gaps against existing portfolio. Use… | [Brainy Strategic Review](./research/pluto-portfolio-ideation/references/brainy-strategic-review.md) |
| **[pluto-skill-extraction](./research/pluto-skill-extraction/SKILL.md)** | Pluto's daily skill extraction engine — scans session history, research outputs, and scripts for reusable patterns, then proposes new skills. Use… | [Data Sources](./research/pluto-skill-extraction/references/data-sources.md) |
| **[pluto-voice-overview](./research/pluto-voice-overview/SKILL.md)** | Pluto's voice overview pipeline — converts daily research JSON outputs to spoken MP3 briefings via OpenAI TTS (Nova voice) and delivers them on… | [Tts Voice Migration](./research/pluto-voice-overview/references/tts-voice-migration.md) |
| **[pluto-weekly-review](./research/pluto-weekly-review/SKILL.md)** | Pluto's weekly operational self-assessment — reviews cron health, pipeline performance, research quality, and produces honest report with… | [Cron Diagnostics](./research/pluto-weekly-review/references/cron-diagnostics.md) |
| **[podcast-knowledge-base](./research/podcast-knowledge-base/SKILL.md)** | Podcast transcript ingestion pipeline — YouTube channels → Supabase pgvector knowledge base with AU relevance scoring. Use when building, querying… | [Aie Ingestion Log](./research/podcast-knowledge-base/references/aie-ingestion-log.md) |
| **[pokemon-player](./gaming/pokemon-player/SKILL.md)** | "Play Pokemon via headless emulator + RAM reads." | - |
| **[popular-web-designs](./creative/popular-web-designs/SKILL.md)** | 54 real design systems (Stripe, Linear, Vercel) as HTML/CSS. | - |
| **[postgres-rls-isolation](./backend-and-database/postgres-rls-isolation/SKILL.md)** | Implement airtight multi-tenant data isolation using native PostgreSQL Row-Level Security (RLS) and session context variables. | - |
| **[powerpoint](./productivity/powerpoint/SKILL.md)** | Create, read, edit .pptx decks with python-pptx. | - |
| **[pretext](./creative/pretext/SKILL.md)** | Build creative browser demos with DOM-free text layout. | [Patterns](./creative/pretext/references/patterns.md) |
| **[prod-issue-management](./observability-and-sentry/prod-issue-management/SKILL.md)** | Maintain a unified global production issue register with structured investigation templates and verification evidence. | - |
| **[product-price-monitor](./productivity/product-price-monitor/SKILL.md)** | "Watch product, flight, or listing prices; alert on target." | - |
| **[professional-html-email-pipeline](./devops/professional-html-email-pipeline/SKILL.md)** | Purelymail HTML report email, rendering + SMTP pitfalls. | [Monthly Strategy After Action Format](./devops/professional-html-email-pipeline/references/monthly-strategy-after-action-format.md) |
| **[prompt-audit](./agent-governance-and-git/prompt-audit/SKILL.md)** | Analyze agent conversation trajectories to identify prompt ambiguities, high-correction loops, and rework patterns. | - |
| **[prompt-crafting](./skills/prompt-crafting/SKILL.md)** | Design, author, and optimize agent skills, workspace rules, custom prompts, and AI agent instructions. Use when creating or refining skills, rules… | [Skill Authoring](./skills/prompt-crafting/references/skill-authoring.md) |
| **[python-debugpy](./software-development/python-debugpy/SKILL.md)** | "Debug Python: pdb REPL + debugpy remote (DAP)." | - |
| **[react-patterns](./skills/react-patterns/SKILL.md)** | React 18/19 patterns including hooks discipline, server/client component boundaries, Suspense + error boundaries, form actions, data fetching, state… | - |
| **[react-testing](./skills/react-testing/SKILL.md)** | React component testing with React Testing Library, Vitest/Jest, MSW for network mocking, accessibility assertions with axe, and the decision… | - |
| **[refactoring-clean-code](./skills/refactoring-clean-code/SKILL.md)** | Refactor complex code into modular, maintainable, and clean code while preserving functionality. Use when asked to refactor, simplify, clean up… | [Code Smells](./skills/refactoring-clean-code/references/code-smells.md) |
| **[reference-data-ingestion](./data-science/reference-data-ingestion/SKILL.md)** | "Australian government reference data ingestion — ASIC (companies, business names), ACNC (charities), ABN Lookup. Weekly/monthly CSV sync from… | [Cloudflare 524 Verify After Timeout](./data-science/reference-data-ingestion/references/cloudflare-524-verify-after-timeout.md) |
| **[relationship-manager](./chief-of-staff-os/relationship-manager/SKILL.md)** | Track follow-ups, manage outreach cadence, monitor relationship health, ensure no important conversation falls through the cracks. Use when: "who do… | [Follow Up Cadence](./chief-of-staff-os/relationship-manager/references/follow-up-cadence.md) |
| **[requesting-code-review](./software-development/requesting-code-review/SKILL.md)** | "Pre-commit review: security scan, quality gates, auto-fix." | - |
| **[research-paper-writing](./research/research-paper-writing/SKILL.md)** | "Write ML papers for NeurIPS/ICML/ICLR: design→submit." | [Autoreason Methodology](./research/research-paper-writing/references/autoreason-methodology.md) |
| **[resilience-tester](./skills/resilience-tester/SKILL.md)** | Recalculates the Burrito Path when life events interfere with the schedule (illness, burnout, lost time). | - |
| **[sag](./skills/sag/SKILL.md)** | ElevenLabs text-to-speech with mac-style say UX. | - |
| **[sdlc-review](./devops/sdlc-review/SKILL.md)** | Review Kanban handoffs and route verified outcomes. | - |
| **[secret-and-credential-safety](./cloud-and-aws/secret-and-credential-safety/SKILL.md)** | Absolute mandate against reading, printing, logging, or exposing API keys, connection strings, or cloud credentials. | - |
| **[security-audit](./skills/security-audit/SKILL.md)** | Perform automated and static security audits, vulnerability assessments, secret detection, and OWASP Top 10 compliance checks. Use when asked to… | [Owasp Top 10](./skills/security-audit/references/owasp-top-10.md) |
| **[sentry-setup](./devops/sentry-setup/SKILL.md)** | "Set up Sentry error monitoring for Python (FastAPI) and Next.js projects — DSN configuration, SDK installation, config files, test events, and build… | [Homelab Config](./devops/sentry-setup/references/homelab-config.md) |
| **[sentry-triage](./observability-and-sentry/sentry-triage/SKILL.md)** | Systematic protocol for triaging incoming Sentry issues, filtering 3rd-party noise, and resolving first-party regressions. | - |
| **[seo-geo-metadata-audit](./frontend-and-ux/seo-geo-metadata-audit/SKILL.md)** | Ensure perfect structured data (JSON-LD), OpenGraph tags, canonical links, and AI search (GEO) crawlability. | - |
| **[ses-transactional-email](./cloud-and-aws/ses-transactional-email/SKILL.md)** | Ensure high email deliverability, MIME RFC-2047 subject encoding, DKIM/SPF verification, and template consistency. | - |
| **[session-librarian](./productivity/session-librarian/SKILL.md)** | "Organize sessions by prompt: find, rename, archive, prune." | - |
| **[session-logs](./skills/session-logs/SKILL.md)** | Search and analyze your own session logs (older/parent conversations) using jq. | - |
| **[sherpa-onnx-tts](./skills/sherpa-onnx-tts/SKILL.md)** | Local text-to-speech via sherpa-onnx (offline, no cloud) | - |
| **[simplify-code](./software-development/simplify-code/SKILL.md)** | "Parallel 4-agent cleanup of recent code changes." | - |
| **[skill-creator](./skills/skill-creator/SKILL.md)** | Create or update AgentSkills. Use when designing, structuring, or packaging skills with scripts, references, and assets. | - |
| **[slack](./skills/slack/SKILL.md)** | Use when you need to control Slack from OpenClaw via the slack tool, including reacting to messages or pinning/unpinning items in Slack channels or… | - |
| **[social-content](./content-growth-and-media/social-content/SKILL.md)** | Create and publish social media posts for Reddit, Twitter/X, LinkedIn, Instagram, Facebook, and TikTok. Platform-specific formats, character limits… | - |
| **[social-media-engine](./content-growth-and-media/social-media-engine/SKILL.md)** | Transform single core insights into tailored, high-performing posts across LinkedIn, X, Reddit, and Facebook. | - |
| **[socratic-concept-bridge](./skills/socratic-concept-bridge/SKILL.md)** | Teases out understanding when the user is stuck rather than providing answers. | - |
| **[sol-strategy-engine](./research/sol-strategy-engine/SKILL.md)** | Sol's strategy synthesis engine — weekly review, monthly strategy, Gumby 1000-point gating, adversarial Sunday. Use when producing strategy packs for… | - |
| **[songsee](./media/songsee/SKILL.md)** | "Audio spectrograms/features (mel, chroma, MFCC) via CLI." | - |
| **[songwriting-and-ai-music](./creative/songwriting-and-ai-music/SKILL.md)** | "Songwriting craft and Suno AI music prompts." | [Heartmula](./creative/songwriting-and-ai-music/references/heartmula.md) |
| **[sonoscli](./skills/sonoscli/SKILL.md)** | Control Sonos speakers (discover/status/play/volume/group). | - |
| **[spec-oracle](./core-methodology/spec-oracle/SKILL.md)** | Establish formal specifications as the definitive source of truth across agent sessions and human-in-the-loop workflows. | - |
| **[spike](./software-development/spike/SKILL.md)** | "Throwaway experiments to validate an idea before build." | - |
| **[spotify](./media/spotify/SKILL.md)** | "Spotify: play, search, queue, manage playlists and devices." | - |
| **[spotify-player](./skills/spotify-player/SKILL.md)** | Terminal Spotify playback/search via spogo (preferred) or spotify_player. | - |
| **[structured-outputs-first](./skills/structured-outputs-first/SKILL.md)** | Any AI endpoint that must return JSON uses Anthropic tool use (structured outputs), never text generation plus regex parsing. ALWAYS load when… | - |
| **[subagent-driven-development](./software-development/subagent-driven-development/SKILL.md)** | "Execute plans via delegate_task subagents (2-stage review)." | [Context Budget Discipline](./software-development/subagent-driven-development/references/context-budget-discipline.md) |
| **[subagent-verification](./agent-governance-and-git/subagent-verification/SKILL.md)** | Verification protocol for orchestrator agents when managing parallel worker subagents. | - |
| **[summarize](./skills/summarize/SKILL.md)** | Summarize or extract text/transcripts from URLs, podcasts, and local files (great fallback for “transcribe this YouTube/video”). | - |
| **[systematic-debugging](./software-development/systematic-debugging/SKILL.md)** | "4-phase root cause debugging: understand bugs before fixing." | [Node Inspect Debugging](./software-development/systematic-debugging/references/node-inspect-debugging.md) |
| **[tapease-backend-deploy](./skills/tapease-backend-deploy/SKILL.md)** | The sanctioned procedure for cutting a Tap-Ease backend release (tapease_portal_fastapi_a2square) and deploying it to the dev / staging environment… | - |
| **[tapease-daily-settlement](./daily-reports/tapease-daily-settlement/SKILL.md)** | "Tapease Daily Settlement Report — queries trans_clover_transaction_payments, sends HTML email with card scheme breakdown, raw transactions, refunds… | [Cron Robustness Patterns](./daily-reports/tapease-daily-settlement/references/cron-robustness-patterns.md) |
| **[tapease-db-access](./skills/tapease-db-access/SKILL.md)** | How to connect to a Tap-Ease Postgres from a workstation — which local port is the dockerised local DB, which is an SSM tunnel to the dev/staging DB… | - |
| **[tapease-fleet-monitor](./devops/tapease-fleet-monitor/SKILL.md)** | "★ TapEase Fleet Monitor — Direct AWS Production. Account 707843605914. EC2, SSM process checks, nginx logs, CloudWatch alarms, Lambda, RDS. Runs 4x… | [Daily Transaction Export](./devops/tapease-fleet-monitor/references/daily-transaction-export.md) |
| **[tapease-pos-clover-shift-sync](./skills/tapease-pos-clover-shift-sync/SKILL.md)** | How the Tap-Ease POS terminal integration (PAUSE / Clover partner) syncs driver shifts to the Clover Platform REST API, and how to debug it. Use when… | - |
| **[tdd-mandate](./core-methodology/tdd-mandate/SKILL.md)** | Enforce strict Test-Driven Development (TDD) where every implementation traces to an explicit requirement and passes exhaustive tests before shipping. | - |
| **[teams-meeting-pipeline](./productivity/teams-meeting-pipeline/SKILL.md)** | Teams meeting summaries, job replay, Graph subscriptions. | - |
| **[terraform-safety](./cloud-and-aws/terraform-safety/SKILL.md)** | Rigorous safeguards for Terraform infrastructure changes to prevent accidental destruction, drift, or state file leaks. | - |
| **[test-driven-development](./software-development/test-driven-development/SKILL.md)** | "TDD: enforce RED-GREEN-REFACTOR, tests before code." | - |
| **[things-mac](./skills/things-mac/SKILL.md)** | Manage Things 3 via the `things` CLI on macOS (add/update projects+todos via URL scheme; read/search/list from the local Things database). Use when a… | - |
| **[tmux](./skills/tmux/SKILL.md)** | Remote-control tmux sessions for interactive CLIs by sending keystrokes and scraping pane output. | - |
| **[touchdesigner-mcp](./creative/touchdesigner-mcp/SKILL.md)** | Control TouchDesigner via twozero MCP. | [3D Scene](./creative/touchdesigner-mcp/references/3d-scene.md) |
| **[trello](./skills/trello/SKILL.md)** | Manage Trello boards, lists, and cards via the Trello REST API. | - |
| **[tui-widgets](./productivity/tui-widgets/SKILL.md)** | Author live widget apps for the Hermes TUI dock. | - |
| **[ui-casing-microcopy](./frontend-and-ux/ui-casing-microcopy/SKILL.md)** | Standardize UI casing (Sentence/Title Case), eliminate screaming uppercase strings, and enforce executive microcopy. | - |
| **[vercel-monitoring](./devops/vercel-monitoring/SKILL.md)** | "⚠️ RETIRED Aug 2026 — Vercel no longer used; cron removed, script archived. Historical reference for the watchdog pattern (script-as-cron… | [Purelymail Module](./devops/vercel-monitoring/references/purelymail-module.md) |
| **[verification-loop](./skills/verification-loop/SKILL.md)** | "A comprehensive verification system for Claude Code sessions." | - |
| **[video-frames](./skills/video-frames/SKILL.md)** | Extract frames or short clips from videos using ffmpeg. | - |
| **[video-voiceover-pipeline](./content-growth-and-media/video-voiceover-pipeline/SKILL.md)** | Produce high-converting short video assets, product walkthroughs, and narrated social reels. | - |
| **[vigil-watch-protocol](./devops/vigil-watch-protocol/SKILL.md)** | Vigil's monitoring & escalation protocol — fleet monitors, cron health, test watch, RED/YELLOW/GREEN alerting. Use for any monitoring task. | - |
| **[voice-call](./skills/voice-call/SKILL.md)** | Start voice calls via the OpenClaw voice-call plugin. | - |
| **[voice-coach](./skills/voice-coach/SKILL.md)** | Developmental Voice and Quality Coach for the student's OWN Tier 3 writing (surface name "Your Voice, Stronger"). It is NOT a detector and NOT a… | - |
| **[vulcan-build-protocol](./software-development/vulcan-build-protocol/SKILL.md)** | Vulcan's build protocol — TDD, OpenSpec, Codex delegation, evidence-based delivery. Use for any product build or test failure triage. | - |
| **[wacli](./skills/wacli/SKILL.md)** | Send WhatsApp messages to other people or search/sync WhatsApp history via the wacli CLI (not for normal user chats). | - |
| **[weather](./skills/weather/SKILL.md)** | Get current weather and forecasts (no API key required). | - |
| **[webhook-subscriptions](./devops/webhook-subscriptions/SKILL.md)** | "Webhook subscriptions: event-driven agent runs." | - |
| **[website-uptime-monitor](./devops/website-uptime-monitor/SKILL.md)** | "HTTP health checks: status, SSL, response times." | [Amlhive Website Monitor](./devops/website-uptime-monitor/references/amlhive-website-monitor.md) |
| **[weekly-ai-brief](./research/weekly-ai-brief/SKILL.md)** | Weekly AI brief - releases, security, policy. | - |
| **[weekly-review-planning](./productivity/weekly-review-planning/SKILL.md)** | "Weekly reset: commitments, stalled work, next-week plan." | - |
| **[windows-bridge-management](./devops/windows-bridge-management/SKILL.md)** | Manage the OpenClaw Research Bridge (Express/Node.js service on Windows port 18796) — find PID, kill/restart, edit endpoints, fix script paths, test… | [Cross Fleet Monitoring](./devops/windows-bridge-management/references/cross-fleet-monitoring.md) |
| **[windows-update-wsl](./devops/windows-update-wsl/SKILL.md)** | "Use when managing Windows Updates from WSL/Hermes cron." | - |
| **[wizard-cycle](./skills/wizard-cycle/SKILL.md)** | The default build cadence for every Simplifii-OS code change: an 8-phase plan, explore, test, implement, verify, document, attack, gate loop that… | - |
| **[writing-plans](./software-development/writing-plans/SKILL.md)** | "Write implementation plans: bite-sized tasks, paths, code." | [Extraction Tdd Workflow](./software-development/writing-plans/references/extraction-tdd-workflow.md) |
| **[wsl-cron-test-runner](./devops/wsl-cron-test-runner/SKILL.md)** | "Run Playwright + pytest test suites from Hermes cron jobs on WSL — handles git stash, browser install, per-repo config, and WSL-specific constraints… | [2026 08 14 False Green Debug](./devops/wsl-cron-test-runner/references/2026-08-14-false-green-debug.md) |
| **[xlsx](./productivity/xlsx/SKILL.md)** | Create, read, edit Excel .xlsx workbooks and CSVs. | [Restructuring](./productivity/xlsx/references/restructuring.md) |
| **[xurl](./social-media/xurl/SKILL.md)** | "X/Twitter via xurl CLI: raw post search, posting, DM, media." | - |
| **[youtube-content](./media/youtube-content/SKILL.md)** | "YouTube transcripts to summaries, threads, blogs." | [Output Formats](./media/youtube-content/references/output-formats.md) |
| **[zain-dreamer](./skills/zain-dreamer/SKILL.md)** | Business opportunity analyst for Australian market gaps, business cases, TAM/SAM/SOM, competitor mapping, customer discovery, pricing hypotheses, and… | - |
| **[zero-click-content](./content-growth-and-media/zero-click-content/SKILL.md)** | Create high-value social media posts and newsletters that provide complete standalone value without forcing link clicks. | - |

---

## 📋 Rules Catalog

| Rule File | Scope & Summary |
| :--- | :--- |
| **[`backend/alembic/` shadows the real installed `alembic` PyPI package (all agents)](./rules/alembic-package-name-shadowing.md)** | - |
| **[ACR evidence-capture standard (all agents)](./rules/acr-evidence-capture-standard.md)** | **Blocking, not guidance.** Requirement A429.12 in `openspec/changes/429-acr-annual-compliance-report-real-estate/` (proposal + design). |
| **[Admin binary-download endpoints need `adminFetchBlob`, not `adminFetch` (all agents)](./rules/admin-fetch-binary-response-contract.md)** | Applies whenever adding, calling, or debugging an `/admin/v1/*` endpoint that returns a file (CSV, PDF, any `StreamingResponse`/non-JSON body) — or… |
| **[Agent Collaboration & Pair Programming Guidelines](./rules/agent-collaboration.md)** | Guidelines for AI agents (Antigravity, Claude, Cursor, Windsurf) working with human engineers and multi-agent systems. |
| **[Agent handoff direction artifact (all agents)](./rules/agent-handoff-direction-artifact.md)** | Applies whenever one agent (typically Claude Code) produces feedback, a review, an architecture direction, or a plan that a **different** agent or… |
| **[Agent rule — YourApp frontend design system](./rules/frontend-design-system.md)** | **Status:** Canonical · **Created:** 4 August 2026 (C381) · **Applies to:** every agent surface **Mirrors:**… |
| **[Agent tooling secrets protection — ignore files per tool (all agents, all repos)](./rules/agent-tooling-secrets-protection.md)** | Applies whenever setting up or materially touching agent-tooling configuration in **any** repository, not just this one. `.gitignore` controls what… |
| **[AWS profile discipline and lost-secret recovery (all agents)](./rules/aws-profile-and-secret-recovery.md)** | Applies whenever an agent runs `aws`/`terraform`/any AWS SDK command against this repo's infrastructure, or is asked to recover a secret that appears… |
| **[Backend Engineering: Python & FastAPI Guidelines](./rules/backend-python-fastapi.md)** | Guidelines for building high-performance, robust, and maintainable backend services with Python and FastAPI. |
| **[Backend startup / config diagnostics (all agents)](./rules/backend-diagnostics.md)** | Applies when the backend won't start, a preflight/settings check fails, auth works client-side but every backend call 401s, or a DB/migration error… |
| **[Claude Code specs it, designated implementer builds it (all agents)](./rules/claude-code-spec-only-implementer-builds.md)** | **Canonical rule.** Mirrors: `.cursor/rules/claude-code-spec-only-implementer-builds.mdc` (Cursor)… |
| **[Cloudflare R2 two-account credential trap (all agents)](./rules/cloudflare-r2-two-account-credential-trap.md)** | Applies whenever debugging staleness, `AccessDenied`, or write failures against `content.yourapp.com.au` or any R2-backed blog/content storage path. |
| **[Commit message quality — commits are evidence, not labels](./rules/commit-message-quality.md)** | **Scope:** every agent-authored commit. Promoted 12 Aug 2026 from a section inside `git-commit-hygiene-shared-worktree.md` to its own rule, because… |
| **[Common Coding Standards](./rules/common-coding-standards.md)** | Universal development principles, code hygiene, and architectural guidelines for all projects. |
| **[Concurrent-Session Decision Conflicts](./rules/concurrent-session-decision-conflicts.md)** | When more than one agent session shares the same repo/workspace and works on overlapping specs at the same time, each session can independently ask… |
| **[CRAP score (Change Risk Anti-Patterns)](./rules/crap-score.md)** | Applies when reviewing whether a function is safe to change — not when checking the repo-wide coverage floor. Total-% coverage can hide a 40-branch… |
| **[Credential rotation safety (all agents)](./rules/credential-rotation-safety.md)** | Applies whenever an agent generates, rotates, or reads back a production credential (DB password, API token, auth token, etc.) via CLI/scripting… |
| **[Data retention + audit trail — HARD RULE for every check-in (all agents)](./rules/data-retention-and-audit-trail-mandate.md)** | **CORE RULE OF THE SYSTEM.** Every activity — user or system, success or denial (including 401/404) — must leave a durable audit row. Sentry noise… |
| **[Deployed-vs-local code parity (all agents)](./rules/deployed-vs-local-code-parity.md)** | Applies before writing "done"/"fixed" in any OpenSpec completion log or prod-issue doc for a change that touches a Lambda, worker, or any artifact… |
| **[DevOps & Deployment Safety Guidelines](./rules/devops-and-deployment.md)** | Guidelines for infrastructure management, deployment automation, Docker containerization, and release safety. |
| **[Form Validation & Error Surfacing Standards](./rules/form-validation-and-error-surfacing.md)** | **Canonical rule.** Applies to all frontend and backend forms, user profile updates, authentication endpoints, and API proxies. |
| **[Frontend Engineering: Next.js & React Guidelines](./rules/frontend-nextjs-react.md)** | Guidelines for building fast, accessible, and scalable React and Next.js applications. |
| **[Git commit hygiene in a shared, concurrently-edited working tree (all agents)](./rules/git-commit-hygiene-shared-worktree.md)** | - |
| **[Git Conventions & Commit Guidelines](./rules/git-conventions.md)** | Standardized Git workflow, commit messages, and branch naming conventions for repositories. |
| **[Git Workflow & Version Control Hygiene](./rules/git-workflow-hygiene.md)** | Guidelines for clean commit histories, branching strategies, and repository cleanliness. |
| **[Incremental local commits after each task (restore points)](./rules/incremental-local-commits.md)** | **Scope:** every agent. **Always apply.** Mirrors: `.cursor/rules/incremental-local-commits.mdc` (Cursor)… |
| **[Investigate every error immediately — including pre-existing/old ones (all agents)](./rules/immediate-error-investigation.md)** | Human decision, 7 Aug 2026, from this session's `npx tsc --noEmit` run: a real type error in `frontend/lib/auditTrailDisplay.ts:272`… |
| **[Knowledge-vault write contract — Alexandria (all agents)](./rules/knowledge-vault-write-contract.md)** | Applies whenever any agent (Claude, Codex, Gemini/Antigravity, Hermes/Pluto/Mercury/Gumby) writes to the shared fleet knowledge vault… |
| **[Lighthouse performance gate (all agents) — blocking, not guidance](./rules/frontend-lighthouse-performance-gate.md)** | Human decision, 7 Aug 2026, prompted by `frontend/prod_issues/issue-246-turnstile-csp-block-and-lighthouse-perf-regression.md`: two live Lighthouse… |
| **[Moved](./rules/claude-code-spec-only-cursor-implements.md)** | This rule has been renamed to… |
| **[Neurodiverse Visual-First Rule (Mandatory Visual Companions & Simple Presentations)](./rules/neurodiverse-visual-first.md)** | **Authority**: Required for all engineering proposals, OpenSpec change sets, technical debt reviews, and stakeholder presentations. |
| **[New public-page registration checklist (all agents)](./rules/new-public-page-registration-checklist.md)** | Applies when adding a brand-new public (unauthenticated) route under `frontend/app/`, e.g. the `/product`, `/security`, `/austrac-compliance`… |
| **[No email delivery to A2 Square / AnotherCompany accounts (all agents)](./rules/no-a2square-emails.md)** | Applies whenever sending, drafting, or configuring any YourApp email — SES after-action reports, operational alerts, test emails, error reports, or… |
| **[No fabricated "Human decision" log entries (all agents)](./rules/no-fabricated-human-decisions.md)** | Applies whenever an agent is tempted to write a "Human decision" / "Human product decision" / "confirmed by [user]" heading into any spec, proposal… |
| **[No hardcoded "current state" literals in checks (all agents)](./rules/no-hardcoded-current-state-literals.md)** | - |
| **[No root or unbounded credentials for agents (all agents, all repos)](./rules/no-root-or-unbounded-credentials-for-agents.md)** | Applies to **every** agent surface — Claude Code, Codex, Cursor, Gemini/Antigravity, and any browser-automation tool — whenever an agent touches a… |
| **[No secret masking — treat credential-shaped fields as opaque (all agents)](./rules/no-secret-masking.md)** | Applies whenever an agent needs to display, log, or reason about a value that might contain a secret (a connection string, API key, token, password)… |
| **[Notification / reminder coverage audit (all agents)](./rules/notification-coverage-audit.md)** | Applies when adding a new `event_type` to `ComplianceCalendarEvent`, a new `notification_type` to the Notification Centre, a new… |
| **[Observability And Error Management (all agents)](./rules/observability-and-error-management.md)** | **Canonical rule.** Mirrors: `.cursor/rules/observability-and-error-management.mdc` (Cursor), `.agents/rules/observability-and-error-management.md`… |
| **[OpenSpec + TDD Delivery Mandate (all agents)](./rules/openspec-tdd-mandate.md)** | **Canonical rule.** Mirrors: `.cursor/rules/openspec-tdd-mandate.mdc` (Cursor), `.agents/rules/openspec-tdd-mandate.md` (Antigravity). Summarised in… |
| **[POS / transaction datetimes are stored and compared as UTC (Tap-Ease backend)](./rules/pos-datetime-utc-normalization.md)** | Applies to any code in `tapease_portal_fastapi_a2square` that reads, writes, or filters a `TIMESTAMP WITHOUT TIME ZONE` column… |
| **[Pre-check-in definition of done](./rules/pre-checkin-definition-of-done.md)** | **Scope:** every agent. Two gates, not one: an **incremental** restore-point commit at milestone points (per phase / component, not one per task —… |
| **[Privilege-change blast-radius audit (all agents)](./rules/privilege-change-blast-radius-audit.md)** | Applies whenever a change alters *which role/identity* an application, worker, or job connects with — not just what that role can do for the one code… |
| **[Prod issue numbering (all agents)](./rules/prod-issue-numbering.md)** | Applies when creating or renaming files under `prod_issues/`, `backend/prod_issues/`, or `frontend/prod_issues/`. |
| **[Public claim audit (all agents)](./rules/public-claim-audit.md)** | Applies when adding, editing, or reviewing any public-facing copy (homepage, landing pages, `frontend/lib/ai-discovery.ts` / `/llms.txt` /… |
| **[Public discoverability and crawler access (all agents)](./rules/public-discoverability-crawler-access.md)** | Applies when adding or editing any public page, public route handler, public content file, structured data, sitemap route, robots policy, footer/nav… |
| **[Public page SEO metadata (all agents)](./rules/public-page-seo-metadata.md)** | Applies when adding or editing public/marketing routes in `frontend/app/` that appear in `sitemapRoutes`. |
| **[Python Style Guide & Best Practices](./rules/python-style-guide.md)** | Standards and conventions for writing clean, Pythonic, and type-hinted code. |
| **[Redirect / alias testing completeness (all agents)](./rules/redirect-alias-testing-completeness.md)** | Applies when adding, editing, or testing any redirect, rewrite, alias, or proxy rule — Next.js `redirects()`/`rewrites()` in `next.config.ts`… |
| **[Regulated-market & data-sovereignty screen (all agents)](./rules/new-vendor-and-model-data-sovereignty-check.md)** | Applies whenever evaluating, integrating, or requesting access to **any new opportunity, market, external vendor, or AI model**. It is mandatory… |
| **[Scheduled/automated task placement: GitHub Actions vs. Pluto (all agents)](./rules/scheduled-automation-placement.md)** | Applies whenever proposing new recurring or scheduled automation in this repo — a lint check, a test suite, a security scan, a metrics report, a… |
| **[Security & Secrets Management](./rules/security-and-secrets.md)** | Universal security protocols, secrets hygiene, and credential protection. |
| **[Security Guardrails & Safe Coding Guidelines](./rules/security-guardrails.md)** | Enforce baseline security standards across all codebases and AI-assisted workflows. |
| **[Sentry frontend noise resilience (all agents)](./rules/sentry-frontend-noise.md)** | Applies when triage'ing or fixing production `javascript-nextjs` Sentry events, editing `frontend/sentry.client.config.ts`… |
| **[SES after-action email encoding (agent rule)](./rules/ses-after-action-email-encoding.md)** | Canonical helper: `scripts/send_after_action_email.py` |
| **[Shared-file commit resolution — a file that is both yours and another session's](./rules/shared-file-commit-resolution.md)** | **Scope:** every agent, every commit. Companion to `docs/agent_rules/git-commit-hygiene-shared-worktree.md`, which governs *what gets committed*… |
| **[Supabase dev/prod project split and platform-admin bootstrap (all agents)](./rules/supabase-project-split-and-admin-bootstrap.md)** | Applies whenever an agent is asked to create/modify a platform admin (`AMLHIVE_ADMIN`), run any script under `backend/scripts/` that talks to… |
| **[Tap-Ease prod deploy boundary (all agents)](./rules/tapease-prod-deploy-boundary.md)** | Applies to any deploy, container restart, migration, or DB mutation for the Tap-Ease stack (`tapease_portal_fastapi_a2square` backend, the `tapease`… |
| **[Terraform prod-apply safety (all agents)](./rules/terraform-prod-apply-safety.md)** | Applies to any `terraform plan` or `terraform apply` run against `infra/aws/environments/prod` (or any other live environment directory). |
| **[Test doubles vs. assertions — the only case where touching a passing-then-failing test is allowed](./rules/test-doubles-vs-assertions.md)** | **Scope:** every agent, every change that refactors how existing code calls the database or any collaborator. Narrow exception to… |
| **[Testing Guidelines & Verification Standards](./rules/testing-guidelines.md)** | Guidelines for writing resilient, maintainable, and high-coverage automated tests. |
| **[TypeScript Style Guide & Standards](./rules/typescript-style-guide.md)** | Best practices and rules for modern, type-safe TypeScript codebases. |
| **[UI Casing & Microcopy Standards (all agents)](./rules/ui-casing-and-microcopy-standards.md)** | Canonical: `docs/agent_rules/ui-casing-and-microcopy-standards.md` · Antigravity: `.agents/rules/ui-casing-and-microcopy-standards.md` · Cursor… |
| **[Valid Red, and guard tests that are not vacuous](./rules/red-for-the-right-reason.md)** | **Scope:** every TDD cycle, every agent. Detail for `docs/agent_rules/openspec-tdd-mandate.md` §4, which owns the Red → Green → Refactor mandate… |
| **[Verifying a dispatched subagent's work, not just its self-report](./rules/subagent-verification-protocol.md)** | - |
| **[Verifying live-state and absence claims (all agents)](./rules/verify-external-agent-reports.md)** | Applies whenever any report — from another agent/tool, or self-generated — makes a "live state," "critical/urgent," or "X is missing/absent from… |

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
