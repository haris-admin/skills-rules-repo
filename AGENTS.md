# Agent Guidelines for skills-rules-repo

Welcome to `skills-rules-repo`, the centralized catalog of reusable AI agent skills, workspace rules, plugins, and authoring templates.

## Principles & Repository Standards

1. **Standardized Directory Structure**:
   - Skills live in `skills/<skill-name>/` and MUST contain a `SKILL.md` with valid YAML frontmatter (`name`, `description`).
   - Bulky documentation and guidelines within skills belong in `references/` or `examples/` subdirectories to facilitate progressive disclosure.
   - Reusable rules live in `rules/` and are written in clean Markdown.
   - Reusable plugins live in `plugins/<plugin-name>/` with a `plugin.json` manifest.
   - Authoring templates live in `templates/`.

2. **Quality & Validation**:
   - All skills, rules, and scripts must pass `./scripts/validate.py`.
   - Markdown documents must use valid syntax, clear heading hierarchy, and working relative links.
   - Shell scripts must be executable and follow defensive scripting practices (`set -euo pipefail`).

3. **Writing High-Quality Skills**:
   - Focus on distinct workflows, procedures, and runbooks.
   - Clearly state triggers in the `description` field (e.g. "Use this skill when the user asks to...").
   - Prefer progressive disclosure over dumping massive context in `SKILL.md`.
