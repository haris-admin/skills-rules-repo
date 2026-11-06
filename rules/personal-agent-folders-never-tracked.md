# Personal agent, skill and rule folders are never committed to a project repository

Agent, skill, rule and assistant instruction folders belong to the owner's machine and the skills-and-rules repository, not to project repositories.

**Scope:** all agents and all project repositories.

---

## Core Directives

1. **Gitignore them**: `.agents/`, `.claude/`, `.codex/`, `.cursor/`, `.cursorrules`, `.windsurf/`, `.gemini/`, `.antigravity/`, `.hermes/`, `CLAUDE.md`, `CLAUDE.local.md`, `GEMINI.md`, `/skills/`, `/rules/`.
2. **Track only what the team needs**: `AGENTS.md` (the engineering guide) and `.github/` (workflows, Dependabot) stay tracked; confirm with the owner before untracking `.github`, because removing it stops CI and deploys.
3. **Untrack without deleting**: `git rm -r --cached <folders>`; the owner's local files stay; do not delete local copies unless asked.
4. **Fix dangling links**: remove references to untracked folders from `AGENTS.md` and docs; keep the rule text inline if the guide depends on it.

## Why this exists

**6 Nov 2026 (HandleDispute):** the owner decided not to check in the agents, Claude and Hermes folders any more; 17 files were untracked and the ignore list extended.
