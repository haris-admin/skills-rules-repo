---
name: upstream-skill-rule-intake
description: >-
  Audit, normalize, validate, and ingest compliant skills and rules from external repositories into skills-rules-repo. Use when importing a new skill or rule from another project (e.g. Simplifii-OS, AMLHive, Tapease), upstreaming custom agent behaviors, or verifying that candidate skills and rules pass repo CI, naming conventions, and catalog requirements.
---

# Upstream Skill & Rule Intake Protocol

A standardized procedure for auditing, sanitizing, placing, and validating skills and rules originating from external repositories into the canonical `skills-rules-repo` catalog.

## When to Use

- When an agent or developer has created a working skill or rule in an external project repository (e.g., `Simplifii-OS-Main/.agents/skills/`, `amlhive/.claude/skills/`, or `.cursor/rules/`) and wants to contribute it to the global catalog.
- When migrating local or ad-hoc agent instructions into shared, version-controlled repository assets.
- When validating that candidate skills or rules comply with frontmatter, directory structure, and CI catalog constraints.

---

## Intake Procedure

### Step 1: Preflight Audit against the Rubric
Review the candidate file or directory against the [Compliance Rubric](./references/compliance-rubric.md):
1. **For Skills**:
   - Must contain a `SKILL.md` with valid YAML frontmatter (`name`, `description`).
   - Description must be in third person and include explicit trigger conditions (*"Use when..."*).
   - Verify folder name matches frontmatter `name:` and is globally unique across the repo.
   - Verify all relative links (`./references/...`) resolve properly.
2. **For Rules**:
   - Must be plain Markdown in `rules/<rule-name>.md`.
   - **Line 1 must be `# <Title>`**.
   - **Zero YAML frontmatter**. If the source has a `---` frontmatter block, strip it.
   - The line/paragraph immediately following the H1 must be a concise summary.
   - Check if a companion `cursor-rules/<rule-name>.mdc` is needed.

### Step 2: Sanitization and Generalization
1. **Secrets & Credentials**: Verify zero hardcoded tokens, API keys, or private passwords.
2. **Path Generalization**: Strip machine-specific paths (e.g., `/Users/username/...` or `/home/user/...`). Use environment variables or project-relative references.
3. **Progressive Disclosure**: If `SKILL.md` exceeds ~500 lines, extract checklists, schemas, and templates into `references/` or `examples/`.

### Step 3: Placement via Taxonomy
Consult the [Category Directory Taxonomy](./references/category-taxonomy.md) to place the asset:
- Enterprise domain skills $\rightarrow$ `<category-dir>/<name>/` (e.g. `backend-and-database/`, `compliance/`, `core-methodology/`).
- General OS/CLI tool skills $\rightarrow$ `skills/<name>/`.
- Workspace rules $\rightarrow$ `rules/<name>.md`.
- Cursor rules $\rightarrow$ `cursor-rules/<name>.mdc`.

### Step 4: Automated Import & Verification
You can use the helper script to automate the placement, stripping, and catalog generation:
```bash
# Ingest an external skill
python3 scripts/import_skill_or_rule.py --source /path/to/external/skill --type skill --category <category>

# Ingest an external rule (auto-strips frontmatter if present)
python3 scripts/import_skill_or_rule.py --source /path/to/external/rule.md --type rule
```

Alternatively, copy manually and run the validation suite:
```bash
# 1. Structural check
python3 scripts/validate.py

# 2. Regenerate catalog table in README.md
python3 scripts/generate_catalog.py

# 3. Verify CI gate passes
python3 scripts/generate_catalog.py --check

# 4. Run quality rubric audit
python3 scripts/audit_skill_quality.py --summary
```

### Step 5: Atomic Commit
Commit both the new asset and the regenerated `README.md` in a single conventional commit:
```bash
git add README.md <path-to-imported-skill-or-rule>
git commit -m "feat(skills): add <skill-name> from <repo-name>"
```

### Step 5b: Importing a Whole Upstream Plugin, and Installing It

For a multi-skill upstream plugin (for example EveryInc's compound-engineering, imported 26 Sep 2026 as `compound-engineering/`):
- Import it as its own category folder with the upstream `LICENSE` and a `PROVENANCE.md` (release tag, commit, local changes, the security review done at import).
- Security-review before import: scan for secrets, pipe-to-shell installs, force pushes, destructive commands and network calls, and read the core skills in full. Note in `PROVENANCE.md` any skill that pushes or deploys on its own.
- Rewrite plugin-namespaced invocations (`plugin:skill`) to the plain skill name, since the skills run standalone. Record that as the only local change.
- Install only that category (copy each new folder into `~/.claude/skills`, skipping names that already exist). Do not run `./sync.sh --global` for one import: it overwrites every skill in `~/.claude`, `~/.Codex` and `~/.gemini` with the repo copy.
- A project mirror of third-party docs may need `--no-verify` if the project's style hook rejects upstream prose (for example em dashes). Say so in the commit and to the user.

### Step 6: Prevent Post-Import Drift (ongoing, not one-time)

Once a skill exists in both `skills-rules-repo` (canonical) and its originating project (local
mirror, e.g. `amlhive1/.agents/skills/<name>/`), **`skills-rules-repo` is the source of truth** —
the project copy must never silently diverge from it. This is standing policy, not a preference:

1. **Add a canonical-source note to the local mirror's `SKILL.md`** (right after the H1, before
   `## Purpose`): name the exact `skills-rules-repo` path and state that any edit to either copy
   must be copied to the other in the same session, with `validate.py` +
   `generate_catalog.py` re-run afterward.
2. **Before authoring a new skill in a project, check `skills-rules-repo` first** for one that
   already does the job (search by topic, not just exact name — a differently-named skill can
   cover the same ground). Two independently-created skills converging on the same design is a
   sign a shared skill already needed to exist, not confirmation that a second one is fine to
   keep. Merge into the existing one and retire the duplicate rather than running both.
3. **If you edit a skill in the project copy, sync it back to `skills-rules-repo` in the same
   session** — don't leave it as a follow-up. A local-only edit is exactly the drift this step
   exists to prevent, even if it "still works" from the project.

Worked incident: 17-18 Sep 2026, `amlhive1` — a Claude Code session built out
`assets/blog-migration/<slug>/social/haris-linkedin-carousel.md` and a companion skill
(`amlhive-blog-linkedin-push`) end-to-end; separately, a Gemini Antigravity session in the same
shared worktree independently created a second, narrower skill (`haris-linkedin-carousel`)
covering the same job with genuinely good ideas of its own. Both had already diverged before
either was checked against the other or against `skills-rules-repo`. Resolution: merged the
stronger specifics from the narrower skill into the canonical one, retired the duplicate, and
added the canonical-source note this step now requires by default.

---

## References

- [Compliance Rubric](./references/compliance-rubric.md) — Detailed specifications, character limits, and error fixes.
- [Category Directory Taxonomy](./references/category-taxonomy.md) — Directory index and placement decision rules.
