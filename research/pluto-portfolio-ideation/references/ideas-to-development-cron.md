# Ideas→Development Cron Job Pattern

**Last used:** June 2, 2026 | **Job ID:** 51643dd88fc5

## Purpose

Reusable cron job that automates the full Ideas→Development pipeline for any `ideas-*` repo. Takes an MVP and elevates it to production standards:
- Open Spec (component breakdown + dependency graph + TDD build order)
- Architecture (C4 diagrams)
- TDD test suite (pytest, 18+ tests)
- Core logic extraction (separate data from logic)
- Integration tests
- GitLab push

## Cron Job Template

```bash
cronjob action=create \
  name="Ideas→Development Pipeline" \
  schedule="1m" \
  repeat=1 \
  deliver="origin" \
  enabled_toolsets=["terminal","file","skills"] \
  prompt="You are the Ideas→Development pipeline. Your job is to elevate an idea repo from MVP to production-ready development standards.

**Workflow for ideas-<project-slug>:**

1. **Verify repo exists** — Check /mnt/c/Code/gitlab/ideas-<project-slug>/
2. **Load Open Spec** — Read docs/OPEN_SPEC.md for component breakdown and TDD build order
3. **Run existing tests** — pytest tests/ -q
4. **Extract core logic** — Follow the Open Spec extraction plan:
   - Extract data definitions to standalone modules
   - Extract validation models
   - Extract client-side logic to lib/
5. **Write tests first (TDD)** — For each extraction:
   - Write failing test → Run to verify RED → Write code → Run to verify GREEN
   - Commit after each extraction
6. **Write integration tests** — Test API endpoints
7. **Build verification** — npm run build passes, all tests pass
8. **Commit + push** — Push to gitlab.com/hhsiddiqui/ideas-<project-slug>

**Rules:**
- TDD strictly enforced: test first, watch it fail, minimal code, watch it pass, commit
- Commit after every completed extraction or test suite
- Never skip the RED phase
- Keep the AUD $250 MVP constraint in mind — don't over-engineer
- Australian-first, React/Next.js frontend, Python/FastAPI backend"
```

## Running for a Specific Project

To trigger the pipeline for a specific idea:

```bash
cronjob action=run job_id=51643dd88fc5
```

Or create a fresh one-shot per project with the project-specific prompt above.

## Verified Output (PayLicence AU, June 2 2026)

From a rough MVP (5 commits, inline data, no tests), produced:
- `docs/OPEN_SPEC.md` — 4-phase TDD build order
- `docs/ARCHITECTURE.md` — C4 diagrams
- `tests/unit/test_categories.py` — 8 tests
- `tests/unit/test_report_generator.py` — 10 tests
- `src/backend/categories.py` — Extracted PSP_CATEGORIES
- `src/backend/models.py` — Extracted Pydantic models
- `src/lib/psp-categories.ts` — Client-side definitions
- `src/lib/answer-store.ts` — sessionStorage wrapper
- 18/18 tests GREEN, 10 commits, pushed to GitLab
