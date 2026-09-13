# Skill quality audit — 2026-09-13

A full pass over every skill in this repo against Anthropic's official Skill-authoring
rubric, cross-checked against OpenAI's Custom-GPT instruction guidance and the public
`anthropics/skills` reference repo. This complements, not replaces, `scripts/validate.py`
(structural minimums required for CI to pass) — a skill can pass `validate.py` and still
fail several of these checks, which is what this audit found at scale.

**Sources used:** [Claude Docs — Skill authoring best
practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices),
[Anthropic Engineering — Equipping agents for the real world with Agent
Skills](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills),
[`anthropics/skills`](https://github.com/anthropics/skills) (public reference repo),
OpenAI Custom-GPT instruction-writing guidance (for cross-provider corroboration, since
`sync.sh` ships these same files to Codex and Gemini too).

**Method:** `scripts/audit_skill_quality.py` (committed alongside this report — rerun it
any time for the current numbers; the counts below are a snapshot, not a permanently
frozen list, since fixing findings changes them). 297 skills discovered (the same
discovery glob `sync.sh`/`generate_catalog.py` use).

## Headline finding: the CI gate only ever checked 29% of skills

`scripts/validate.py`'s `validate_skills()` walked `ROOT_DIR / "skills"` only — the 85
skills in the flat `skills/` folder. The other 213 skills, living under 30 category
directories (`devops/`, `research/`, `compliance/`, `backend-and-database/`, etc.), have
**never** been checked by CI since the tool existed, even though `sync.sh` ships all of
them and `generate_catalog.py` already discovers all of them correctly (its
`discover_skill_dirs()` was fixed for this exact gap on 2026-09-05, per
`TECHNICAL_DEBT.md` — `validate.py` was never updated to match). **Fixed in this pass**
— `validate.py` now mirrors `generate_catalog.py`'s discovery glob and validates all 297
skills (confirmed still green: `python3 scripts/validate.py` passes with the widened
scope, since nothing newly in view happens to trip its current — fairly loose — checks).

No skill-name collisions across categories were found (`sync.sh --global` copies by
folder name into a single flat `~/.claude/skills/<name>/`, so a same-named skill in two
categories would silently overwrite one on sync — checked, zero instances).

## Findings, by category

| Check | Count | Severity | Effort to fix |
|---|---:|---|---|
| Description has no explicit trigger condition | 198 / 297 (67%) | High — this is the single field Claude uses to select a skill among 100+ | Per-skill rewrite; see prioritization below |
| Bundled file(s) SKILL.md never mentions at all | 56 skills | Medium — dead weight, or a real reference Claude will never discover | Per-skill: either link it or delete it |
| Body over the 500-line guideline | 13 skills | Medium — the guideline exists because every token in a loaded SKILL.md competes with conversation history | Split into reference files (progressive disclosure) |
| Name uses a reserved word (`claude`/`anthropic`) | 2 skills | Low locally; blocks upload via Claude's API/skill-upload flow if ever exported | Rename directory + frontmatter `name` |
| Reference file linked from SKILL.md that itself links to a further file (2+ levels deep) | 1 skill | Low | Flatten to link both files directly from SKILL.md |
| Frontmatter missing/malformed | 0 | — | — |
| `name` != directory name | 0 (outside the template placeholder) | — | — |

### 1. Descriptions that don't say *when* to use the skill (198 skills)

Per the official guidance: *"The description is critical for skill selection: Claude
uses it to choose the right Skill from potentially 100+ available Skills... Your
description must provide enough detail for Claude to know when to select this Skill."*
Two verified real examples (not heuristic false positives — manually checked):

```yaml
# agent-governance-and-git/subagent-verification/SKILL.md
description: Verification protocol for orchestrator agents when managing parallel worker subagents.
```
States what it is, never says "use this when you are an orchestrator dispatching
subagents and need to verify their reports" — a routing model has to infer the trigger
from a noun phrase.

```yaml
# agent-governance-and-git/cross-model-review/SKILL.md
description: For a security- or compliance-critical design/spec review, prefer engaging a genuinely different underlying model, not just a fresh context window of the same model.
```
This is phrased as a *directive to follow once already invoked*, not a *routing
condition for when to invoke it* — contrast with the security-audit rewrite done
earlier this session: `"...Use when asked to audit security, scan for secrets, or
review code for vulnerabilities."`

This is the highest-value fix in the whole audit — a skill with a vague description
simply won't fire when it should, no matter how good the body content is — but 198 is
too many to rewrite in one pass. Suggested prioritization, not attempted here:
1. Skills you or your team actually invoke by name/slash-command regularly (check your
   own usage — the skills already reviewed this session, `nginx-change`,
   `api-endpoints`, `tapease-db-access`, `security-audit`, already have solid
   descriptions and don't need this pass).
2. Skills with the most content behind them (the 13 over-500-line skills below) — a long,
   well-built skill that never fires is the most wasted effort.
3. Everything else, opportunistically as each skill is next touched.

### 2. Orphaned files (56 skills)

Per the official guidance: *"If Claude never accesses a bundled file, it might be
unnecessary or poorly signaled."* Example, verified directly (the string genuinely does
not appear anywhere in the SKILL.md, confirmed with `grep`):

```
aws/aws-ec2-fleet-monitoring/SKILL.md never mentions its own bundled README.md
```

Two-line fix per instance: either add one line to SKILL.md pointing at the file
(`See [X](path) for ...`), or delete the file if it's genuinely stale/superseded.

### 3. Skills over the 500-line guideline (13 skills)

```
   1611  research/research-paper-writing
   1016  autonomous-ai-agents/hermes-agent
    989  devops/pluto-pipeline-orchestration
    885  devops/wsl-cron-test-runner
    709  research/pluto-autonomous-research
    639  creative/claude-design
    634  creative/humanizer
    585  creative/comfyui
    570  devops/aws-cloudwatch-agent
    552  research/pluto-weekly-review
    547  creative/p5js
    509  github/github-repo-management
    505  software-development/systematic-debugging
```

Fix is the progressive-disclosure pattern the official guidance describes directly:
split into `SKILL.md` (overview + navigation) plus topic-specific reference files
Claude loads only when needed, with a table of contents if any single reference file
exceeds 100 lines. `research-paper-writing` at 3.2x the guideline is the standout case.

### 4. Reserved-word names (2 skills)

`creative/claude-design` and `skills/my-defender-claude` both use `claude` in the `name`
field, which the platform's frontmatter validation explicitly rejects (`name` "cannot
contain reserved words: anthropic, claude"). No local impact today, but either skill
would be rejected outright if ever uploaded through Claude's official skill-upload flow.
Rename both the directory and the frontmatter `name` (e.g. `claude-design` →
`canvas-design` or similar, `my-defender-claude` → `my-defender`).

### 5. Nested reference chain (1 skill)

`productivity/box/SKILL.md` links directly to `references/oauth-setup.md` and
`references/search-and-ai.md`, each of which links to further files
(`cli-guide.md`; `hubs.md`, `bulk-operations.md`) not linked directly from SKILL.md
itself. Per the guidance, Claude may only partially read a file reached this way
(`head -100`-style preview) rather than in full. Fix: link all four leaf files directly
from SKILL.md instead of chaining through the two intermediate ones.

## What was checked and ruled out

- **Windows-style backslash paths** — initially flagged 10 skills, all false positives
  on manual check: either legitimate content for skills whose entire subject is a
  Windows machine (`devops/windows-bridge-management`, `devops/pluto-pipeline-orchestration`),
  or regex-escape sequences (`app\.tsx`) misread as paths. Dropped from the final script.
- **Name collisions across category dirs** — 0 found (see above).
- **Vague/generic skill names** (`helper`, `utils`, `tools`, etc.) — 0 found; naming
  in this repo is consistently specific.
- **Frontmatter parsing / missing name-description** — 0 found across all 297 (the
  known `validate.py` plain-multiline-scalar parser bug, tracked separately in
  `TECHNICAL_DEBT.md`, affects only `skills/accessibility/SKILL.md` and is a parsing
  bug, not a content issue with that skill's actual description).

## Re-running this audit

```bash
python3 scripts/audit_skill_quality.py            # full per-skill breakdown
python3 scripts/audit_skill_quality.py --summary  # just the aggregate counts
```
