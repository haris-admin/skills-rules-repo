---
name: agent-tooling-secrets
description: Set up and maintain multi-agent ignore files (.cursorignore, .geminiignore, permissions.deny) to protect credentials. Use when initializing a repo, onboarding a new AI coding tool/agent, or auditing a repo for exposed secrets/env/credential files before granting agent file access.
---

# Agent Tooling Secrets Protection

## Implementation
Ensure every repository contains:
- `.gitignore`: Standard git exclusions.
- `.cursorignore`: Cursor indexing exclusions.
- `.geminiignore` / `.antigravityignore`: Gemini/Antigravity file viewing exclusions.
- Block all `*.env*`, `*.pem`, `*credentials*`, and `*.tfstate` files across all agents.

