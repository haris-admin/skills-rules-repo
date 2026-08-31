# Ideas→Development Flow

**Version:** 1.0 | **Date:** June 2, 2026 | **First used:** PayLicence AU

## Overview

The Ideas→Development pipeline transforms an MVP idea repo (docs-only, rough code) into a production-ready project with Open Spec, Architecture docs, TDD tests, extracted modules, integration tests, and a two-round Brainy review. This is the standard post-ideation development workflow.

## When to Use

- After a new `ideas-*` repo is created and the MVP scaffold is built (Phase 1 cron job done)
- When Haris says "proceed," "work on [project]," or "push to development"
- As a follow-up to the portfolio ideation build queue

## Pipeline (7 Phases)

### Phase 1: Open Spec
Create `docs/OPEN_SPEC.md` with:
- Component breakdown table (file, responsibility, test priority P1/P2/P3)
- Dependency graph showing imports/relationships
- TDD build order with bite-sized tasks (2-5 min each)
- Quality gates checklist

### Phase 2: Architecture
Create `docs/ARCHITECTURE.md` with:
- C4 Level 1: System Context
- C4 Level 2: Container Architecture (frontend ↔ backend)
- C4 Level 3: Component Detail (full directory tree)
- Data Flow diagram (e.g., AnswerStore → PSPCategoryEngine → ReportFetcher → FastAPI)
- ERD for key data structures
- Deployment diagram (dev/prod environments)

### Phase 3: TDD Infrastructure
- Write `pytest.ini` with `testpaths` and `pythonpath`
- Create `tests/conftest.py` with path setup
- Write unit tests following RED-GREEN-REFACTOR
- Run RED phase (watch failures) → fix tests → run GREEN
- Goal: 15-20 unit tests passing before extractions

### Phase 4: Extract Core Logic
Extract tightly-coupled inline code to independent modules:
- **Backend:** Data dictionaries → `categories.py`, Pydantic models → `models.py`
- **Frontend:** PSP definitions → `lib/psp-categories.ts`, storage → `lib/answer-store.ts`
- Update imports in all consumers
- Run full test suite after each extraction
- Commit after each successful extraction

### Phase 5: Integration Tests
Write FastAPI TestClient tests for all endpoints:
- 200 OK with valid payloads
- 422 validation errors (empty answers, bad IDs)
- Content assertions (sections present, company name in report)
- Edge cases (all "no" answers, missing fields with defaults)
- Goal: 15-20 integration tests

### Phase 6: Brainy Review (Round 1)
Delegate to a subagent acting as "Brainy" with:
- Read all key files (README, PRD, ASSESSMENT, OPEN_SPEC, ARCHITECTURE, source, tests)
- Produce: star rating (1-10), strengths, issues with file paths, fixes prioritized P0/P1/P2, architecture score, test coverage score, production readiness score
- Brainy acts as strategic analyst — be specific, cite files, give concrete fixes

### Phase 7: Fix & Re-Review
- Fix all P0 items first (runtime bugs, broken flows)
- Fix P1 items (data integrity, security)
- Fix P2 items (dead code, cleanup)
- Run full test suite after each batch
- Commit after each batch
- Re-engage Brainy for second review
- Compare ratings — each round should move the needle

## Pitfalls

- **Patch tool with large blocks:** When old_string spans 170+ lines, the patch tool fails. Write the entire file fresh with `write_file` instead.
- **Import mismatch:** When extracting functions, check that ALL consumers use the same import pattern. The `{ AnswerStore }` vs `saveAnswers()` mismatch is a classic extraction bug.
- **Obligation/matrix gaps:** Data dictionaries with string-keyed lookups are fragile. After extraction, verify ALL strings in categories appear in the matrix. Add missing keys.
- **Hardcoded samples:** Report/preview pages that show fake data are the #1 sign of an incomplete pipeline. Wire them to the real API before review.
- **Two-round reviews catch different things:** Round 1 finds architecture + flow issues. Round 2 finds import bugs and data gaps. Don't skip the second round.
- **CORS `*` in production:** Restrict to known origins (`localhost:3000`, production domain) before deployment.

## Example: PayLicence AU (June 2, 2026)

| Phase | Deliverable | Tests |
|-------|------------|-------|
| Open Spec | 3-phase build order + dependency graph | — |
| Architecture | C4 diagrams + data flow + ERD | — |
| TDD Setup | pytest.ini + 18 unit tests | 18/18 GREEN |
| Extraction | categories.py, models.py, psp-categories.ts, answer-store.ts | 18/18 GREEN |
| Integration | 19 API tests (5 endpoint suites) | 48/48 GREEN |
| Brainy R1 | 6/10 — report disconnected, vitest broken, duplication | — |
| Fixes | API wiring, vitest fix, report-fetcher.ts, obligation matching | 48/48 GREEN |
| Brainy R2 | 7/10 → 8/10 after P0 fixes | — |

**Result:** 48 tests, 16 commits, API-connected end-to-end flow, honest UX.
