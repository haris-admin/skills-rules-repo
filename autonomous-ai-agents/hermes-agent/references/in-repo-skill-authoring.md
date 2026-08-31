# Authoring In-Repo Skills (for hermes-agent development)

## Overview

Two places a SKILL.md can live:
1. **User-local:** `~/.hermes/skills/<category>/<name>/SKILL.md` — created via `skill_manage(action='create')`
2. **In-repo:** `hermes-agent/skills/<category>/<name>/SKILL.md` — committed, shipped with the package. Use `write_file` + `git add`.

## When to Use

- You're committing a reusable workflow that should ship with hermes-agent
- You're editing an existing skill under `hermes-agent/skills/`

## Required Frontmatter

```yaml
---
name: my-skill-name               # lowercase, hyphens, ≤64 chars
description: Use when <trigger>. <one-line behavior>.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [short, descriptive, tags]
    related_skills: [other-skill, another-skill]
---
```

**Hard requirements:** `---` at byte 0, `name` present, `description` present (≤1024 chars), non-empty body.
**Size limits:** ≤100,000 chars total (aim for 8-15k). Split large content into `references/*.md`.

## Directory Placement

```
skills/<category>/<name>/SKILL.md
```

Existing categories: `autonomous-ai-agents`, `creative`, `data-science`, `devops`, `dogfood`, `email`, `gaming`, `github`, `mcp`, `media`, `mlops/*`, `note-taking`, `productivity`, `red-teaming`, `research`, `smart-home`, `social-media`, `software-development`.

## Workflow

1. Survey peers in the target category (`ls skills/<category>/`)
2. Draft with `write_file` to `skills/<category>/<name>/SKILL.md`
3. Validate locally:
   ```python
   import yaml, re, pathlib
   content = pathlib.Path("skills/<category>/<name>/SKILL.md").read_text()
   assert content.startswith("---")
   m = re.search(r'\n---\s*\n', content[3:])
   fm = yaml.safe_load(content[3:m.start()+3])
   assert "name" in fm and "description" in fm
   assert len(fm["description"]) <= 1024
   assert len(content) <= 100_000
   ```
4. `git add` + `git commit`

## Peer-Matched Structure

```
# <Title>

## Overview — what and why

## When to Use — bulleted triggers, counter-triggers

## <Topic sections>
- Quick-reference tables
- Code blocks with exact commands

## Common Pitfalls — numbered list

## Verification Checklist
- [ ] Checkbox list
```

## Editing Existing In-Repo Skills

- **Small fix:** `skill_manage(action='patch', name=..., old_string=..., new_string=...)`
- **Major rewrite:** `write_file` the whole SKILL.md
- **Adding files:** `write_file` to `skills/<category>/<name>/references/<file>.md`
- **Always commit** — in-repo skills are source, not runtime state

## Common Pitfalls

1. Using `skill_manage(action='create')` for an in-repo skill (writes to `~/.hermes/skills/`, not repo). Use `write_file`.
2. Leading whitespace before `---` (validator checks byte 0).
3. Description too generic — start with "Use when ...".
4. Current session won't see the new skill until restart (cached at session start).
5. Linking to user-local skills from in-repo skills breaks for other clones.
