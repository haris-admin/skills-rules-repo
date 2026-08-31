---
name: prompt-crafting
description: >-
  Design, author, and optimize agent skills, workspace rules, custom prompts, and AI agent instructions. Use when creating or refining skills, rules, or system prompts.
---

# Agent Prompt & Skill Crafting Skill

Guides the agent in designing effective, token-efficient, and precise instructions for AI coding assistants and agents.

## Workflow

1. **Step 1: Choose Customization Type**
   - **Rules** (`rules/*.md` or `GEMINI.md`/`AGENTS.md`): For static constraints, formatting rules, or stylistic guidelines.
   - **Skills** (`skills/<name>/SKILL.md`): For complex, multi-step runbooks and on-demand specialized workflows.
   - **Plugins** (`plugins/<name>/`): For packaging skills, rules, hooks, and MCP servers into a shareable bundle.

2. **Step 2: Crafting Precise Trigger Descriptions**
   - In `SKILL.md`, the frontmatter `description` determines when the model invokes the skill.
   - Use clear third-person phrasing stating triggers, contexts, and actions (e.g., `Conduct thorough, structured code reviews... Use when the user asks for...`).

3. **Step 3: Structure for Progressive Disclosure**
   - Keep the main `SKILL.md` file focused on core steps and procedures.
   - Offload large tables, catalogs, specifications, or examples into `references/` or `examples/`.

4. **Step 4: Validate**
   - Run `python3 scripts/validate.py` to ensure valid frontmatter and link syntax.

## Reference

- [Authoring Guide for Antigravity & Agent Customizations](./references/skill-authoring.md)
