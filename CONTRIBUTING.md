# Contributing to skills-rules-repo

Thank you for contributing to the repository! We welcome new skills, rules, templates, and improvements.

## Adding a New Skill

1. Copy the skill template:
   ```bash
   cp -r templates/skill-template skills/<your-skill-name>
   ```
2. Edit `skills/<your-skill-name>/SKILL.md`:
   - Set `name: <your-skill-name>` matching the folder name exactly.
   - Write a detailed `description` specifying trigger conditions.
   - Provide clear, actionable instructions and verification steps.
3. If the skill needs references, scripts, or examples, add them to `references/`, `scripts/`, or `examples/`.
4. Validate your skill:
   ```bash
   python3 scripts/validate.py
   ```

## Adding a New Rule

1. Copy the rule template:
   ```bash
   cp templates/rule-template.md rules/<your-rule-name>.md
   ```
2. Use lowercase hyphenated naming (e.g. `rules/react-best-practices.md`).
3. Start with an `# H1` title and outline directives, positive examples, and anti-patterns.
4. Validate your rule:
   ```bash
   python3 scripts/validate.py
   ```

## Validation & CI

All pull requests run automated validation with `scripts/validate.py`. Ensure that `python3 scripts/validate.py` passes locally before submitting a PR.
