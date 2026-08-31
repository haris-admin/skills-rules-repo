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
| **[`api-design`](./skills/api-design/SKILL.md)** | RESTful API design, HTTP status codes, schema consistency, OpenAPI/Swagger specifications. | [REST Guidelines](./skills/api-design/references/rest-guidelines.md) |
| **[`code-review`](./skills/code-review/SKILL.md)** | Structured code reviews, PR audits, logic/security/performance evaluation. | [Review Checklist](./skills/code-review/references/checklist.md) |
| **[`git-workflow`](./skills/git-workflow/SKILL.md)** | Semantic commit messages (Conventional Commits), atomic staging, branch workflows, and PR drafting. | [Commit Specs](./skills/git-workflow/references/conventional-commits.md) |
| **[`prompt-crafting`](./skills/prompt-crafting/SKILL.md)** | Authoring custom agent skills, workspace rules, and prompt optimization. | [Authoring Guide](./skills/prompt-crafting/references/skill-authoring.md) |
| **[`refactoring-clean-code`](./skills/refactoring-clean-code/SKILL.md)** | Safe micro-refactoring, code smell detection, SOLID principles, and clean code techniques. | [Code Smells](./skills/refactoring-clean-code/references/code-smells.md) |
| **[`security-audit`](./skills/security-audit/SKILL.md)** | Secret detection, injection checks, input validation, and OWASP Top 10 compliance audits. | [OWASP Top 10](./skills/security-audit/references/owasp-top-10.md) |
| **[`test-driven-development`](./skills/test-driven-development/SKILL.md)** | Disciplined Red-Green-Refactor TDD cycle, test doubles, mocking best practices. | [Testing Patterns](./skills/test-driven-development/references/testing-patterns.md) |

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
