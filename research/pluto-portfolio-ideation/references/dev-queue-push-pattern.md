# Ideas→Development Pipeline

**Version:** 2.0 | **Date:** 2026-06-02

## When to Use

After Gumby 1000-point assessment, when an idea scores ≥700 (Grade A or A-/B+), push it through the Ideas→Development pipeline. This elevates a rough MVP into a production-ready project with Open Spec, Architecture, TDD, and automated CI.

## The Full Pipeline (6 Phases)

### Phase 0: Design Before Build (mandatory — user expects this)
> **HARD RULE:** Design before code. Produce architecture + Open Spec BEFORE any implementation work.

1. Write `docs/ARCHITECTURE.md` — C4 diagrams (System Context, Container, Component, Data Flow, ERD)
2. Write `docs/OPEN_SPEC.md` — Component breakdown, dependency graph, and 3-phase TDD build order
3. (Optional) Write `docs/SECURITY_AUDIT.md` — OWASP + ASD E8 + Privacy Act
4. User reviews the design map → approves → then build begins

### Phase 1: TDD Infrastructure Setup
1. Create `tests/unit/` directory with pytest infrastructure (`conftest.py`, `pytest.ini`)
2. Write tests for core data integrity (categories, obligations, validation models)
3. Run RED phase — watch tests fail for expected reasons
4. Fix test expectations to match actual code (the code is the MVP, tests document it)
5. Run GREEN phase — all tests pass
6. Commit: `feat(dev): Add TDD test suite — N/N GREEN`

### Phase 2: Core Logic Extraction
Follow the Open Spec extraction plan. For each module:

1. **Backend extraction:** PSP_CATEGORIES → `categories.py`, Pydantic models → `models.py`
   - Write failing test for new module → RED → create module → GREEN → update imports
   - Verify all existing tests still pass after extraction
2. **Frontend extraction:** PSP categories → `lib/psp-categories.ts`, Answer storage → `lib/answer-store.ts`
3. **Clean the original files:** Remove inline data blocks, replace with imports
4. **Patch tool limitation:** When replacing 170+ line blocks, `patch()` may produce syntax errors from partial replacements. Fall back to `write_file()` to rewrite the entire file cleanly.
5. Commit after each extraction: `refactor(extract): Extract X to independent module`

### Phase 3: Integration Tests
1. Write `tests/integration/test_api.py` — test FastAPI endpoints
2. Test POST `/api/generate-report` returns 200 with valid payload
3. Test 422 on empty answers, 200 on GET `/api/categories`, etc.
4. Commit: `test(integration): Add API endpoint tests`

### Phase 4: Ideas→Development Cron Job
Create a reusable cron job that automates this entire pipeline for any idea repo:

```bash
cronjob action=create \
  name="Ideas→Development Pipeline" \
  schedule="1m" \
  repeat=1 \
  deliver="origin" \
  enabled_toolsets=["terminal","file","skills"] \
  prompt="[Self-contained instructions: load skills → verify repo → run TDD → extract → test → commit → push]"
```

The cron job prompt should reference the Open Spec for the specific project and follow TDD strictly.

### Phase 5: Push to GitLab
```bash
TOKEN="glpat-..."  # Read from /mnt/c/Users/habib/.hermes/.env
cd /mnt/c/Code/gitlab/ideas-<project-slug>
git remote add origin "https://oauth2:${TOKEN}@gitlab.com/hhsiddiqui/ideas-<project-slug>.git"
git push -u origin master
```

### Phase 6: Feed MemPalace
```bash
/home/habib/.hermes/venv/bin/python3 /home/habib/.hermes/scripts/pluto_mempalace_feeder.py \
  --input /home/habib/.hermes/research_outputs/<project>_dev_queue_YYYY-MM-DD.json \
  --topic "<Project> — Development Queue" \
  --tags "<tags>" \
  --source "pluto_dev_queue"
```

## Legacy: 5-Step Quick Push (for Phase 1 MVP only)

The original 5-step pattern still applies for the initial MVP build (before the Ideas→Development upgrade):

## Prerequisites

- Idea has been scored with Gumby 1000-point assessment
- Full PRD written (Phase 4 of pluto-portfolio-ideation)
- Decision matrix confirms build priority

## 5-Step Push Pattern

### Step 1: Create Repo

```bash
# CORRECT location — C:\Code\gitlab\, NOT C:\Users\habib\
mkdir -p /mnt/c/Code/gitlab/ideas-<project-slug>
cd /mnt/c/Code/gitlab/ideas-<project-slug>
git init
git config user.email "pluto@hermes.fleet"
git config user.name "Pluto"
mkdir -p src docs
```

**Location rule:** All ideas repos live under `/mnt/c/Code/gitlab/ideas-*`. This is `C:\Code\gitlab\` from Windows. Do NOT use `/mnt/c/Users/habib/` for new repos — that was the old location.

### Step 2: Write Core Docs

Write these files immediately:
- **README.md** — project overview with badges (score, grade, MVP budget), tech stack, quick start
- **PRD.md** — full product requirements from Codex ideation output
- **ASSESSMENT.md** — copy of the 1000-point scorecard

### Step 3: Git Commit

```bash
cd /mnt/c/Code/gitlab/ideas-<project-slug>
git add -A
git commit -m "Initial: <Project Name> (Grade X, NNN/1000)"
```

### Step 4: Create Cron Build Job

```bash
# Create a cron job that builds Phase 1 MVP
# enabled_toolsets: terminal, file, web
# schedule: 1m (fires once, immediately)
# repeat: 1 (one-shot)
```

The build job prompt must include:
- Project context (what, why, gumby score)
- MVP budget constraint (AUD $250)
- Repo path (absolute `/mnt/c/Code/gitlab/ideas-<slug>/`)
- Phase 1 deliverables (concrete, bite-sized)
- Git commit instructions
- Delivery report requirements

### Step 5: Feed MemPalace

```bash
# Write JSON with build_status: "queued"
# Feed via pluto_mempalace_feeder.py
/home/habib/.hermes/venv/bin/python3 /home/habib/.hermes/scripts/pluto_mempalace_feeder.py \
  --input /home/habib/.hermes/research_outputs/<project>_dev_queue_YYYY-MM-DD.json \
  --topic "<Project> — Development Queue" \
  --tags "<tags>" \
  --source "pluto_dev_queue"
```

### Step 6: Push to GitLab

Use the GitLab token from `/mnt/c/Users/habib/.hermes/.env` (`GITLAB_PAT_OPENCLAW`):

```bash
TOKEN="glpat-..."
cd /mnt/c/Code/gitlab/ideas-<project-slug>
git remote add gitlab "https://oauth2:${TOKEN}@gitlab.com/hhsiddiqui/ideas-<project-slug>.git"
git push -u gitlab master
```

## Example: ExitLens AU Push

```bash
# Step 1
mkdir -p /mnt/c/Code/gitlab/ideas-exitlens
cd /mnt/c/Code/gitlab/ideas-exitlens
git init && mkdir -p src docs

# Step 2
# Write README.md, PRD.md, ASSESSMENT.md
# Write architecture docs + Open Spec (Phase 0 design)

# Step 3
git add -A && git commit -m "Initial: ExitLens AU (Grade A, 800/1000)"

# Step 4
cronjob action=create name="Build: ExitLens AU — Phase 1 MVP" ...

# Steps 5-6
# Feed MemPalace + push to GitLab
```

## Pitfalls

- **Location mistake:** Creating repos under `/mnt/c/Users/habib/` instead of `/mnt/c/Code/gitlab/`. User corrected this — always use `C:\\Code\\gitlab\\`.
- **GitLab auth:** Token must be read from `.env` each time, not hardcoded. Token format: `glpat-...` with `oauth2:` username.
- **Repo creation:** GitLab auto-creates the project on first push if it doesn't exist and the token has `api` scope.
- **Missing docs:** Don't skip README/PRD/ASSESSMENT — these are the minimum viable repo content.
- **Build job prompt:** Too vague → Codex won't produce useful output. Be specific about deliverables.
- **Stagger cron jobs:** When pushing 3+ projects simultaneously, stagger their `schedule` by 1-minute intervals (`1m`, `2m`, `3m`). Each build job runs in its own repo workdir so they don't share state, but staggering avoids WSL → cmd.exe → Codex resource contention and prevents concurrent git operations from conflicting.
