# Category Directory Taxonomy

`skills-rules-repo` organizes skills into domain categories alongside a flat `skills/` root folder. Use this taxonomy when deciding where to place an imported skill.

---

## Domain Category Index

| Category Directory | Domain Focus & Core Skill Types | Example Skills |
|:---|:---|:---|
| `agent-governance-and-git/` | Agent handoffs, worktree hygiene, cross-model review, prompt audits, intake standards | `implementer-neutral-handover`, `subagent-verification` |
| `autonomous-ai-agents/` | Agent runtimes, CLI drivers, profiles, autonomous delegation, background loops | `herdr-agent-runtime`, `coding-agent-delegation` |
| `backend-and-database/` | SQL, Postgres, RLS, Alembic migrations, Redis, backend diagnostics | `postgres-rls-isolation`, `alembic-migration-hygiene` |
| `chief-of-staff-os/` | Daily rhythms, calendar scheduling, task triage, inbox operations | `daily-task-manager`, `executive-assistant` |
| `cloud-and-aws/` | AWS architecture, IAM, S3, RDS, CloudWatch, Terraform safety | `habibi`, `terraform-safety` |
| `compliance/` | AML/CTF, AUSTRAC, ASIC, sanctions screening, regulatory registers | `caduceus-compliance-watch`, `amlhive-asic-sync` |
| `content-growth-and-media/` | Copywriting, social media, editorial engines, zero-click content | `copywriting`, `social-media-engine`, `humanizer` |
| `core-methodology/` | TDD, CRAP score, 10-star quality, OpenSpec, OODA loop, spec oracle | `crap-score`, `spec-oracle`, `tdd-mandate` |
| `creative/` | Mockups, design tokens, Excalidraw, popular web designs, ideation | `excalidraw`, `popular-web-designs`, `design-md` |
| `devops/` | CI/CD, credential remediation, Cloudflare Workers, uptime monitors | `credential-exposure-remediation`, `cloudflare-worker-deploy` |
| `frontend-and-ux/` | React, Next.js, accessibility, Lighthouse gates, design systems, ADHD UX | `react-patterns`, `lighthouse-performance-gate` |
| `gaming/` | Emulators, RAM inspection, game engines | `pokemon-player` |
| `github/` | PR workflows, code reviews, issue triaging, GitHub API | `github-pr-workflow`, `github-issues` |
| `growth/` | B2B SaaS metrics, customer retention, market mapping, startup economics | `amlhive-ai-authority`, `a16z-startup-metrics` |
| `observability-and-sentry/` | Error triage, Sentry noise filtering, production issue registers | `sentry-triage`, `prod-issue-management` |
| `productivity/` | Notion, Airtable, Apple Notes, Things 3, Google Workspace, Excel | `notion`, `airtable`, `gog`, `xlsx` |
| `research/` | Deep research, arXiv papers, podcast knowledge bases, vector search | `deep-research`, `arxiv`, `podcast-knowledge-base` |
| `security-and-compliance/` | OWASP, vulnerability scanning, security audits, privacy regulations | `my-defender`, `security-audit` |
| `software-development/` | Debugging, inspection, clean code refactoring, TUI development | `systematic-debugging`, `refactoring-clean-code` |
| `skills/` | Standalone CLI tools, wrappers, local desktop utilities | `gemini`, `ffmpeg`, `peekaboo`, `bird` |

---

## Placement Decision Rule

1. If the skill maps to a specialized enterprise domain (e.g. database, compliance, frontend, agent governance), place it in `<category-dir>/<name>/`.
2. If the skill is a general-purpose CLI or OS tool wrapper (e.g. `ffmpeg`, `gog`, `peekaboo`), place it in `skills/<name>/`.
3. Never invent a new top-level category without verifying `SKIP_TOP_LEVEL_DIRS` and ensuring it won't collide with future tools.
