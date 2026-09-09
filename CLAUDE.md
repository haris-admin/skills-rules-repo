# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

A **content repository**, not an application. It is the canonical, version-controlled catalog of AI-agent **skills**, workspace **rules**, **plugins**, authoring **templates**, and **collections**, distributed to multiple agent tools (Claude Code, Codex, Cursor, Gemini/Antigravity, Hermes/Pluto fleet). There is no build step and no runtime — the only executable code is three Python 3 helper scripts and two Bash sync scripts.

## Commands

```bash
# Validate structure + frontmatter (skills, rules, plugins, templates). Run before every commit.
python3 scripts/validate.py

# Regenerate the README Skills/Rules catalog tables from filesystem content.
python3 scripts/generate_catalog.py            # rewrite README.md in place
python3 scripts/generate_catalog.py --check    # exit 1 if README.md is stale (CI gate)

# Distribute skills/rules to agent tools
./sync.sh --global                 # ~/.claude/skills, ~/.Codex/skills, ~/.gemini/config/{skills,rules}
./sync.sh --project <dir>          # <dir>/.agents, <dir>/.claude/skills, <dir>/.cursor/rules
./scripts/install.sh --list        # list skills/rules/plugins
./scripts/install.sh --workspace <dir> [--skill NAME] [--rule NAME] [--copy]   # symlink by default
```

CI (`.github/workflows/validate.yml`, on push/PR to `main`) runs `validate.py` **and** `generate_catalog.py --check`. Any PR that adds, removes, or renames a skill/rule without regenerating the README fails the build.

There are no unit tests; `validate.py` is the test suite. To check one skill, run `validate.py` (it validates all and lists per-item results) or eyeball the specific `SKILL.md` frontmatter.

## Repository architecture

### Skills live in category directories, not just `skills/`

~290 skills are spread across ~40 topic-category top-level directories (`research/`, `devops/`, `compliance/`, `backend-and-database/`, `software-development/`, `productivity/`, `creative/`, …) **plus** the flat `skills/` directory. The canonical path shape is `<category-dir>/<skill-name>/SKILL.md`.

**Two discovery mechanisms with different scope — know which you're dealing with:**

| Consumer | Scope |
| :-- | :-- |
| `scripts/validate.py` | **only** `skills/*/SKILL.md` (flat dir) |
| `scripts/generate_catalog.py`, `sync.sh`, `install.sh` (`--list` is flat) | `*/*/SKILL.md` across **all** non-hidden top-level dirs except `templates/` (see `SKIP_TOP_LEVEL_DIRS`) |

So a skill added under a category dir passes `validate.py` trivially (it's not checked) but is still picked up by the catalog and sync. The catalog generator is the real structural check for category-dir skills.

### SKILL.md contract

YAML frontmatter requires `name` (must match the folder name exactly) and `description` (trigger conditions, third person, "Use when…"). Keep `SKILL.md` concise; push bulk into `references/`, `scripts/`, `examples/` subdirs (progressive disclosure). The catalog links the first `references/*.md` file if present.

**Frontmatter gotcha:** `validate.py`'s `parse_frontmatter()` has a known latent bug (see `TECHNICAL_DEBT.md`) — a plain unquoted multi-line scalar silently loses its first line. `generate_catalog.py` carries its own *corrected* copy of the parser. Write `description:` as a folded scalar (`>-`) as the template does, not a bare wrapped string.

### Skill folder names must be globally unique

`sync.sh` and `install.sh` flatten skills to `<basename>/` in the target (`~/.claude/skills/<name>/`), collapsing the category prefix. Two skills with the same folder name in different category dirs collide on sync; `generate_catalog.py` emits a duplicate-name warning and keeps only the first.

### Rules

Flat `rules/*.md`, plain Markdown, lowercase-hyphenated filename, must start with an `# H1` title. The catalog uses the first blockquote or paragraph after the H1 as the summary — include one (four rules currently lack it, tracked in `TECHNICAL_DEBT.md`).

### Cursor rules are separate and hand-maintained

`cursor-rules/*.mdc` use Cursor's format (frontmatter: `description`, `globs`, `alwaysApply`). They are **not generated** from `rules/` — the two sets are maintained in parallel and overlap only partly. `sync.sh --project` copies `cursor-rules/*.mdc` into `<dir>/.cursor/rules/`. When you change a rule that has an `.mdc` counterpart, update both.

### Other top-level pieces

- `plugins/<name>/plugin.json` — bundle manifest (`name`, `description`, `version`, `author`).
- `templates/` — `skill-template/SKILL.md`, `rule-template.md`, `plugin-template/`, `AGENTS.md.template`, `GEMINI.md.template`. Skipped by catalog discovery.
- `collections/*.md` — plain-Markdown discovery maps (repo-relative links) that route a question to existing skills without moving or duplicating them. `collections/early-stage-startup.md` is the model.
- `fleet-agents.md` + `.agents/skills.json` — the **Mercury fleet** registry: 6 Hermes Windows profiles (Aurora, Caduceus, Lumen, Sol, Vigil, Vulcan), each pinned to one agent-protocol skill in this repo. Changes to those skills (and to the shared tool skills listed there) must be mirrored back to the deployed profile dirs.
- `.archive/` — retired skills, ignored by all tooling.
- `AGENTS.md`, `GEMINI.md` — this repo's own agent instructions (directory conventions, run `validate.py` before committing).

## Adding or changing a skill / rule

1. `cp -r templates/skill-template <category-dir>/<name>` (or `cp templates/rule-template.md rules/<name>.md`).
2. Edit; keep `name` == folder name; write trigger-focused `description`.
3. `python3 scripts/validate.py`
4. `python3 scripts/generate_catalog.py` and commit the README change in the same commit.
5. If a rule has a `cursor-rules/*.mdc` twin, update it too.

## Conventions

- Commits: Conventional Commits with a scope — `feat(skills):`, `feat(rules):`, `fix(catalog):`, `ci:`, `docs(technical-debt):`.
- Shell scripts: `set -euo pipefail`, executable, LF line endings (enforced by `.gitattributes` for `*.sh`/`*.py`).
- Naming: lowercase-hyphenated for skill folders and rule files (validator enforces `^[a-z0-9-]+$`).
- Track known gaps in `TECHNICAL_DEBT.md` (dated table: Item / Status / Notes) rather than leaving them implicit.

## Global TDD mandate

`~/.claude/CLAUDE.md` imposes a non-negotiable Requirement → Test → Implementation chain on all work on this machine. In this repo that maps to: a change is driven by a stated requirement, `validate.py` / `generate_catalog.py --check` are the executable encoding of the structural requirements, and a failing check means the content is wrong — fix the content, not the check, unless the requirement itself changed (confirm with the human first). Several skills and rules here (`core-methodology/tdd-mandate`, `rules/openspec-tdd-mandate.md`, `rules/red-for-the-right-reason.md`) restate this pattern and should stay consistent with the global rule.
