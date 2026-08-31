# Workspace Rules: skills-rules-repo

- Ensure all new skills follow the directory convention: `skills/<skill-name>/SKILL.md`.
- Ensure all YAML frontmatter in `SKILL.md` defines `name` and `description`.
- Test any updates with `python3 scripts/validate.py` before committing.
- Keep `SKILL.md` concise and put detailed reference guides into `references/` within the skill folder.
