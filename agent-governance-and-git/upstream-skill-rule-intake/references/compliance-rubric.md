# Upstream Skill & Rule Compliance Rubric

This rubric defines the precise acceptance criteria required when auditing, sanitizing, and importing skills or rules from external codebases into `skills-rules-repo`.

---

## 1. Skill Rubric (`SKILL.md`)

| Area | Requirement | Failure Mode | Fix |
|:---|:---|:---|:---|
| **Location** | Must live in `<category-dir>/<name>/` or `skills/<name>/`. | Skill placed in root or unindexed folder. | Move to appropriate domain category or `skills/`. |
| **Directory Name** | Lowercase, alphanumeric, hyphenated (`^[a-z0-9-]+$`), max 64 chars. | `MySkill_v2/` or uppercase letters. | Rename folder to lowercase hyphenated (`my-skill-v2`). |
| **Frontmatter Name** | Matches folder name identically. | Folder is `foo-bar` but frontmatter has `name: foo_bar`. | Align `name:` with folder name. |
| **Reserved Names** | Must not contain `anthropic`, `claude`, or vague names (`helper`, `tools`, `misc`). | Name is `claude-helper`. | Rename to descriptive purpose name (`prompt-optimizer`). |
| **Description** | Folded scalar `>-`, third person, $\le 1024$ chars, contains explicit trigger (*"Use when..."*). | Starts with *"I will..."* or has no trigger condition. | Rewrite in 3rd person: *"Use when asked to..."*. |
| **Length** | `SKILL.md` body ideally under 500 lines. | Massive single-file dump of 1,200 lines. | Split out runbooks into `references/` or `examples/`. |
| **Relative Links** | All markdown links in `SKILL.md` must resolve to local files. | Broken `[guide](./missing.md)` or external local links. | Fix relative link paths or bundle the target reference. |
| **Nesting Depth** | Direct 1-hop links from `SKILL.md` to reference files. | Deep 3-level chain of nested `.md` files. | Make all key references directly reachable from `SKILL.md`. |
| **Sanitization** | Zero hardcoded user paths (`/Users/foo/`), tokens, or credentials. | Hardcoded `ghp_...` or local absolute path. | Replace with env vars (`$WORKSPACE_DIR`, `GITHUB_TOKEN`). |

---

## 2. Rule Rubric (`rules/*.md`)

| Area | Requirement | Failure Mode | Fix |
|:---|:---|:---|:---|
| **Location** | Flat in `rules/<name>.md`. | Placed in subfolders or category dirs. | Place directly in `rules/`. |
| **File Name** | Lowercase, alphanumeric, hyphenated with `.md` extension. | `CodingStandards.md` or `git_hygiene.md`. | Rename to `coding-standards.md`. |
| **Title Header** | Line 1 **MUST** start with `# <H1 Title>`. | Starts with frontmatter `---` or empty line. | Ensure line 1 is `# Title`. |
| **YAML Frontmatter** | **STRICTLY PROHIBITED** in `rules/*.md`. | File starts with `--- name: ... ---`. | Delete frontmatter entirely; move description into body. |
| **Summary Paragraph** | First non-empty paragraph or blockquote following `# Title` is the summary. | Section header `## Directive` immediately follows `# Title`. | Insert a 1-2 sentence overview paragraph directly under `# Title`. |
| **Cursor Twin** | If applicable, mirrored in `cursor-rules/<name>.mdc`. | `.mdc` file missing or out of sync. | Create/update `cursor-rules/<name>.mdc` with Cursor YAML frontmatter. |

---

## 3. Catalog & Validation Gate

Before any PR or commit is ready:
1. `python3 scripts/validate.py` $\rightarrow$ must report `✅ SUCCESS: All skills, rules, templates, and plugins validated successfully!`.
2. `python3 scripts/generate_catalog.py` $\rightarrow$ must report `No parsing warnings` and update `README.md`.
3. `python3 scripts/generate_catalog.py --check` $\rightarrow$ must exit 0.
4. `python3 scripts/audit_skill_quality.py --summary` $\rightarrow$ inspect for rubric warnings.
