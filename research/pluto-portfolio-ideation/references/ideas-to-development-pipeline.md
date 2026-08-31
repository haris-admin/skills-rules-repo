# Ideas→Development Pipeline

**Version:** 1.0 | **Date:** June 2, 2026 | **Parent Skill:** pluto-portfolio-ideation

## Purpose

A reusable cron job pattern that elevates an idea repo from rough MVP to production-ready development standards. Automates Open Spec documentation, TDD test infrastructure, logic extraction, and frequent commits.

## Cron Job Template

```yaml
name: "Ideas→Development Pipeline"
schedule: "1m"      # One-shot — fires once
repeat: 1
deliver: "origin"
enabled_toolsets: ["terminal", "file", "skills"]
```

## Pipeline Steps

### 1. Verify Repo
```bash
cd /mnt/c/Code/gitlab/ideas-{slug}/
git status
ls docs/ src/ tests/
```

### 2. Load Open Spec
Read `docs/OPEN_SPEC.md` for component breakdown, dependency graph, and TDD build order.

### 3. Run Existing Tests (RED phase baseline)
```bash
cd /mnt/c/Code/gitlab/ideas-{slug}
python3 -m pytest tests/ -q
```
Record failures — these identify real code gaps.

### 4. Extract Core Logic (TDD)
For each extraction task in the Open Spec:
- Write failing test → Run to verify RED → Write minimal code → Run to verify GREEN → Commit
- Commit format: `feat(extract): {description}`

### 5. Integration Tests
Test API endpoints against running FastAPI server:
```bash
cd src/backend && uvicorn main:app --host 0.0.0.0 --port 8000 &
pytest tests/integration/ -q
```

### 6. Security Audit
Verify `docs/SECURITY_AUDIT.md` exists and covers OWASP Top 10 + ASD Essential Eight + Australian Privacy Act.

### 7. Build Verification
```bash
npm run build       # Frontend must compile clean
python3 -m pytest tests/ -q  # All tests must pass
```

### 8. Push
```bash
git push origin master
```

## Project-Specific Instructions

The cron job prompt should include the project slug so the pipeline knows which repo to target:

```text
You are the Ideas→Development pipeline. Your job is to elevate the ideas-{slug} repo...

Workflow:
1. Verify repo at /mnt/c/Code/gitlab/ideas-{slug}/
2. Read docs/OPEN_SPEC.md for build order
3. Extract core logic via TDD (test first, watch it fail, then code)
4. Commit after each extraction
5. Push to gitlab.com/hhsiddiqui/ideas-{slug}
```

## Rules

- **TDD strictly enforced:** test first, watch it fail, minimal code, watch it pass, commit
- **Commit after every completed extraction or test suite**
- **Never skip the RED phase**
- **Keep AUD $250 MVP constraint** — don't over-engineer
- **Australian-first:** React/Next.js frontend, Python/FastAPI backend

## PayLicence AU Example (June 2, 2026)

First run produced:
- `docs/OPEN_SPEC.md` — 4-phase TDD build order, dependency graph, 18 tasks
- `docs/ARCHITECTURE.md` — C4 container/component/data flow diagrams
- `tests/unit/test_categories.py` — 8 tests for PSP category data integrity
- `tests/unit/test_report_generator.py` — 10 tests for report generation
- `pytest.ini` + `tests/conftest.py` — Test infrastructure
- **18/18 tests GREEN** on first run after fixing 3 expected failures (category key mismatch, threshold mismatch, edge case keyword expansion)

## Pitfalls

- **Do NOT run the pipeline on repos that lack a working `npm run build`** — the build verification step will fail and cascade
- **extract before you build new features** — the pipeline upgrades existing code; new features come after
- **The conftest.py must use absolute path insertion** for backend modules that live outside the test directory:
  ```python
  import sys, os
  sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src", "backend")))
  ```
- **pytest.ini requires `pythonpath` for non-standard module locations** when conftest.py sys.path alone isn't enough:
  ```ini
  [tool:pytest]
  testpaths = tests
  pythonpath = src/backend
  ```
