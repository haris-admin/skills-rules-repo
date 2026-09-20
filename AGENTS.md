# Agent Guidelines for skills-rules-repo

Welcome to `skills-rules-repo`, the centralized catalog of reusable AI agent skills, workspace
rules, plugins, and authoring templates. **This file is the single canonical instructions file for
every agent working on this repo — Claude Code, Codex, Cursor, Gemini/Antigravity, and the
Hermes/Pluto fleet alike.** `CLAUDE.md` was retired 20 Sep 2026 (its content is merged in below);
Claude Code reads `AGENTS.md` natively as a fallback whenever no `CLAUDE.md` is present (native
support added v2.1.277, 18 Sep 2026), so no stub file is needed.

## What this repo is

A **content repository**, not an application. It is the canonical, version-controlled catalog of
AI-agent **skills**, workspace **rules**, **plugins**, authoring **templates**, and
**collections**, distributed to multiple agent tools (Claude Code, Codex, Cursor, Gemini/
Antigravity, Hermes/Pluto fleet). There is no build step and no runtime — the only executable code
is three Python 3 helper scripts and two Bash sync scripts.

## Commands

```bash
# Validate structure + frontmatter (skills, rules, plugins, templates). Run before every commit.
python3 scripts/validate.py

# Regenerate the README Skills/Rules catalog tables from filesystem content.
python3 scripts/generate_catalog.py            # rewrite README.md in place
python3 scripts/generate_catalog.py --check    # exit 1 if README.md is stale (CI gate)

# Audit skills against Anthropic's Skill-authoring rubric (stricter than validate.py; not a CI gate).
python3 scripts/audit_skill_quality.py             # full per-skill report
python3 scripts/audit_skill_quality.py --summary   # aggregate counts only

# Distribute skills/rules to agent tools
./sync.sh --global                 # ~/.claude/skills, ~/.Codex/skills, ~/.gemini/config/{skills,rules}
./sync.sh --project <dir>          # <dir>/.agents, <dir>/.claude/skills, <dir>/.cursor/rules
./scripts/install.sh --list        # list skills/rules/plugins
./scripts/install.sh --workspace <dir> [--skill NAME] [--rule NAME] [--copy]   # symlink by default
```

CI (`.github/workflows/validate.yml`, on push/PR to `main`) runs `validate.py` **and**
`generate_catalog.py --check`. Any PR that adds, removes, or renames a skill/rule without
regenerating the README fails the build.

There are no unit tests; `validate.py` is the test suite. To check one skill, run `validate.py`
(it validates all and lists per-item results) or eyeball the specific `SKILL.md` frontmatter.

## Repository architecture

### Skills live in category directories, not just `skills/`

297 skills are spread across ~40 topic-category top-level directories (`research/`, `devops/`,
`compliance/`, `backend-and-database/`, `software-development/`, `productivity/`, `creative/`, …)
**plus** the flat `skills/` directory. The canonical path shape is
`<category-dir>/<skill-name>/SKILL.md`.

`scripts/validate.py`, `scripts/generate_catalog.py`, `sync.sh`, and `install.sh` all discover
skills the same way: `*/*/SKILL.md` across every non-hidden top-level dir except
`SKIP_TOP_LEVEL_DIRS` (`.git`, `.github`, `.archive`, `node_modules`, `templates`), deduplicated by
resolved `SKILL.md` path. `validate.py`'s `discover_skill_dirs()` and `generate_catalog.py`'s copy
are meant to stay identical — if you widen one's scope (category dirs, skip-list), widen the other
the same way, or CI structural checks and the catalog/sync surface silently diverge again (this
happened once: `validate.py` only walked flat `skills/*` until 2026-09-13, so the ~213 category-dir
skills got zero CI structural validation for months — see `TECHNICAL_DEBT.md`).

### SKILL.md contract

YAML frontmatter requires `name` (must match the folder name exactly) and `description` (trigger
conditions, third person, "Use when…"). Keep `SKILL.md` concise; push bulk into `references/`,
`scripts/`, `examples/` subdirs (progressive disclosure). The catalog links the first
`references/*.md` file if present.

**Frontmatter gotcha:** `validate.py`'s `parse_frontmatter()` has a known latent bug (see
`TECHNICAL_DEBT.md`) — a plain unquoted multi-line scalar silently loses its first line.
`generate_catalog.py` carries its own *corrected* copy of the parser. Write `description:` as a
folded scalar (`>-`) as the template does, not a bare wrapped string.

`validate.py` only checks structural minimums (frontmatter present, `name` matches folder,
`description` non-trivial). `scripts/audit_skill_quality.py` checks the stricter Anthropic
Skill-authoring rubric that a skill can pass `validate.py` while still failing: a `description`
that states what the skill does but never *when* to use it, a body over ~500 lines, bundled files
`SKILL.md` never links to, reference chains more than one level deep, or `name`/folder using a
reserved word (`claude`, `anthropic`). It's not a CI gate — run it manually after adding/editing
skills.

### Skill folder names must be globally unique

`sync.sh` and `install.sh` flatten skills to `<basename>/` in the target
(`~/.claude/skills/<name>/`), collapsing the category prefix. Two skills with the same folder name
in different category dirs collide on sync; `generate_catalog.py` emits a duplicate-name warning
and keeps only the first.

### Rules

Flat `rules/*.md`, plain Markdown, lowercase-hyphenated filename, must start with an `# H1` title.
The catalog uses the first blockquote or paragraph after the H1 as the summary — include one (four
rules currently lack it, tracked in `TECHNICAL_DEBT.md`). **Rules MUST NOT contain YAML
frontmatter** (`---`) — that's a `validate.py` failure (see the intake workflow below).

### Cursor rules are separate and hand-maintained

`cursor-rules/*.mdc` use Cursor's format (frontmatter: `description`, `globs`, `alwaysApply`). They
are **not generated** from `rules/` — the two sets are maintained in parallel and overlap only
partly. `sync.sh --project` copies `cursor-rules/*.mdc` into `<dir>/.cursor/rules/`. When you
change a rule that has an `.mdc` counterpart, update both.

### Other top-level pieces

- `plugins/<name>/plugin.json` — bundle manifest (`name`, `description`, `version`, `author`).
- `templates/` — `skill-template/SKILL.md`, `rule-template.md`, `plugin-template/`,
  `AGENTS.md.template`, `GEMINI.md.template`. Skipped by catalog discovery.
- `collections/*.md` — plain-Markdown discovery maps (repo-relative links) that route a question
  to existing skills without moving or duplicating them. `collections/early-stage-startup.md` is
  the model.
- `fleet-agents.md` + `.agents/skills.json` — the **Mercury fleet** registry: 6 Hermes Windows
  profiles (Aurora, Caduceus, Lumen, Sol, Vigil, Vulcan), each pinned to one agent-protocol skill in
  this repo. Changes to those skills (and to the shared tool skills listed there) must be mirrored
  back to the deployed profile dirs.
- `.archive/` — retired skills, ignored by all tooling.
- `GEMINI.md` — Gemini/Antigravity's own entrypoint (directory conventions, run `validate.py`
  before committing); kept as a thin, tool-specific pointer alongside this file rather than
  duplicating its content.

## Adding or changing a skill / rule

1. `cp -r templates/skill-template <category-dir>/<name>` (or `cp templates/rule-template.md
   rules/<name>.md`).
2. Edit; keep `name` == folder name; write trigger-focused `description`.
3. `python3 scripts/validate.py`
4. `python3 scripts/generate_catalog.py` and commit the README change in the same commit.
5. If a rule has a `cursor-rules/*.mdc` twin, update it too.

## Upstream skill/rule intake from external repos

Canonical: `rules/upstream-skill-and-rule-intake.md` (skill:
`agent-governance-and-git/upstream-skill-rule-intake/SKILL.md`). Every agent or engineer
contributing or importing skills/rules from external codebases (e.g. `Simplifii-OS`, `amlhive`,
`tapease`, `openclaw`) must follow that intake workflow: preflight audit, normalization (strip
repo-specific paths and secrets, strip YAML frontmatter if it's a rule), placement, validation, and
an atomic commit that includes the regenerated README. Note that a source project's own canonical
rules file can change over time (e.g. `amlhive`'s canonical file moved from `CLAUDE.md` to
`AGENTS.md` on 20 Sep 2026) — an imported reference that cites a source project's rules file by
name should be re-checked against that project's current setup, not assumed stable.

## Conventions

- Commits: Conventional Commits with a scope — `feat(skills):`, `feat(rules):`, `fix(catalog):`,
  `ci:`, `docs(technical-debt):`.
- Shell scripts: `set -euo pipefail`, executable, LF line endings (enforced by `.gitattributes` for
  `*.sh`/`*.py`).
- Naming: lowercase-hyphenated for skill folders and rule files (validator enforces
  `^[a-z0-9-]+$`).
- Track known gaps in `TECHNICAL_DEBT.md` (dated table: Item / Status / Notes) rather than leaving
  them implicit.

## Global TDD mandate

`~/.claude/CLAUDE.md` (Haris's personal, machine-level global instructions — separate from any
project's own rules file) imposes a non-negotiable Requirement → Test → Implementation chain on all
work on this machine. In this repo that maps to: a change is driven by a stated requirement,
`validate.py` / `generate_catalog.py --check` are the executable encoding of the structural
requirements, and a failing check means the content is wrong — fix the content, not the check,
unless the requirement itself changed (confirm with the human first). Several skills and rules here
(`core-methodology/tdd-mandate`, `rules/openspec-tdd-mandate.md`, `rules/red-for-the-right-reason.md`)
restate this pattern and should stay consistent with the global rule.

## Quality & Validation (summary)

- All skills, rules, and scripts must pass `./scripts/validate.py`.
- Markdown documents must use valid syntax, clear heading hierarchy, and working relative links.
- Shell scripts must be executable and follow defensive scripting practices (`set -euo pipefail`).
- Focus skills on distinct workflows, procedures, and runbooks; state triggers in the `description`
  field in third person ("Use when…"); prefer progressive disclosure over dumping massive context
  into `SKILL.md`.
