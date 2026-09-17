# Candidate Skill & Rule Intake Audit Checklist

Use this checklist before accepting, merging, or committing any skill or rule originating from another repository.

---

## 1. Skill Intake Checklist (`<category>/<name>/SKILL.md`)

- [ ] **Folder Naming**: Lowercase alphanumeric and hyphens only (`^[a-z0-9-]+$`).
- [ ] **Frontmatter Present**: Begins with `---` and ends with `---`.
- [ ] **`name:` Field**: Matches the folder name exactly. Max 64 characters. No reserved words (`claude`, `anthropic`) or vague terms (`helper`, `tools`).
- [ ] **`description:` Field**: Written in third person (never *"I can help with..."*). Contains explicit trigger phrases (*"Use when..."*, *"Trigger on..."*). Less than 1024 characters. Uses folded scalar `>-`.
- [ ] **Body Conciseness**: `SKILL.md` is concise (<500 lines). Detailed manuals, templates, and schemas are separated into `references/` or `examples/`.
- [ ] **Relative Links**: All markdown links resolve locally within the skill directory (`./references/doc.md`).
- [ ] **Secrets & Paths**: No hardcoded API keys, tokens, or local machine paths (`/Users/...`, `/home/...`).
- [ ] **Category Placement**: Valid domain category assigned (or placed in `skills/`).

---

## 2. Rule Intake Checklist (`rules/<name>.md`)

- [ ] **File Naming**: Lowercase alphanumeric and hyphens only (`^[a-z0-9-]+.md$`).
- [ ] **File Location**: Directly in `rules/` (not in subfolders).
- [ ] **Header Format**: Line 1 starts immediately with `# <H1 Title>`.
- [ ] **No YAML Frontmatter**: Strictly zero `---` blocks in `rules/*.md`.
- [ ] **Summary Paragraph**: Non-empty overview paragraph immediately follows the `# Title` heading for README catalog generation.
- [ ] **Cursor Twin**: If applicable, companion `cursor-rules/<name>.mdc` is created with valid Cursor frontmatter.

---

## 3. Pre-Commit Verification Gate

- [ ] `python3 scripts/validate.py` passes with zero errors.
- [ ] `python3 scripts/generate_catalog.py` completes with zero warnings.
- [ ] `python3 scripts/generate_catalog.py --check` exits with 0.
- [ ] `README.md` catalog updates are staged and committed in the same atomic commit.
