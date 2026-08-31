# TDD Extraction Workflow: Monolith → Modules

**Version:** 1.0 | **Date:** 2026-06-02 | **Source:** PayLicence AU build (Pluto)

## When to Use

When an existing project has logic embedded in monolithic files and needs to be extracted to standalone, testable modules following an Open Spec component breakdown. This is the *refactoring-with-safety* pattern — every extraction is verified by tests that existed before the move.

## The Pattern

```
READ Open Spec → IDENTIFY embedded code → WRITE failing test → EXTRACT module → VERIFY green → COMMIT → REPEAT
```

## Step-by-Step

### 1. Map the Monolith

Read the monolithic file and identify what's embedded:

| What | Where it lives now | Where it should go (per Open Spec) |
|------|--------------------|-----------------------------------|
| PSP_CATEGORIES dict | `report_generator.py:14-157` | `categories.py` |
| Pydantic models | `main.py:32-50` | `models.py` |
| Category mapping fn | `page.tsx:153-354` | `src/lib/psp-categories.ts` |
| Answer storage logic | *(new)* | `src/lib/answer-store.ts` |

### 2. Write the Test First (RED)

Even though the code already exists in the monolith, write a test that imports from the *new* target module:

```python
# tests/unit/test_categories.py — BEFORE extraction
from categories import PSP_CATEGORIES  # This file doesn't exist yet!

def test_all_10_categories_present():
    assert len(PSP_CATEGORIES) == 10
```

Run it — it should fail with `ModuleNotFoundError`. This proves the test is testing the extraction, not the old code.

### 3. Extract with Import Swap

Create the new module with the extracted code. Then update the old monolith to import from the new module:

```python
# OLD: report_generator.py had the dict inline
# NEW: report_generator.py imports from categories
from categories import PSP_CATEGORIES, OBLIGATION_MATRIX
```

**Critical:** Remove ALL duplicated data/code from the old file. A half-done extraction (import added but old data left behind) creates a corrupted source file where tests may pass from `.pyc` cache while the source is syntactically broken. See pitfall below.

### 4. Verify GREEN

```bash
# Run the specific test first
pytest tests/unit/test_categories.py -v

# Then the full suite
pytest tests/ -q
```

### 5. Commit Immediately

```bash
git add src/backend/categories.py src/backend/report_generator.py tests/
git commit -m "refactor(backend): Extract PSP_CATEGORIES to categories.py"
```

One extraction = one commit. Never bundle extractions.

### 6. Repeat for Next Extraction

Move to the next embedded piece. Each follows the same cycle.

## The RED→GREEN→COMMIT Extraction Cycle

| Phase | Action | Proof |
|-------|--------|-------|
| RED | Write test importing from new module path | `ModuleNotFoundError` or `ImportError` |
| GREEN | Create module, update old file's imports, run tests | All tests pass from source (not cache) |
| COMMIT | `git add` + `git commit` with `refactor(scope):` prefix | One extraction per commit |

## Cross-Language Extraction

This session extracted from BOTH Python (backend) and TypeScript (frontend):

**Backend (Python/FastAPI):**
- `report_generator.py` → `categories.py` (data)
- `main.py` → `models.py` (Pydantic schemas)

**Frontend (Next.js/TypeScript):**
- `page.tsx` → `src/lib/psp-categories.ts` (category engine, ~240 lines)
- *(new)* → `src/lib/answer-store.ts` (sessionStorage wrapper)

Same pattern for both: write test → watch it fail → create module → watch it pass → commit.

## Pitfalls

### .pyc Cache False Positive

**Symptom:** Tests pass even though the source file is syntactically broken.

**Cause:** Python imports from `.pyc` cache in `__pycache__/`. If the `.pyc` was compiled before the file was corrupted, tests will pass from cache while the actual `.py` file is unimportable.

**Detection:** Always run a direct import check after structural changes:
```bash
python3 -c "from new_module import Thing; print('OK:', Thing)"
```

**Fix:** Clear caches and re-run:
```bash
rm -rf __pycache__ .pytest_cache
pytest tests/ -q
```

### Half-Done Extraction

**Symptom:** Import added to monolith (`from categories import PSP_CATEGORIES`) but the old inline data was NOT deleted.

**Result:** The file has both the import AND a duplicate of the data (possibly garbled). The import works, but the file is bloated and fragile.

**Fix:** After adding the import, DELETE every line of the duplicated data. Verify the file is shorter by approximately the size of the extracted block.

### Frontend Test Path Resolution in WSL

**Symptom:** `npx vitest run` can't find test files at `../tests/frontend/*.test.ts` when run from `src/`.

**Cause:** WSL `/mnt/c/` mount paths interact badly with vitest's module resolution when tests are outside the `src/` directory.

**Fix:** Place frontend tests INSIDE `src/__tests__/` and point vitest at `include: ['__tests__/**/*.test.ts']`. This keeps everything within the same filesystem subtree that node_modules lives in.

## Quality Gates Per Extraction

Before marking an extraction complete:

- [ ] New module created at target path
- [ ] Old file imports from new module (no duplicate data)
- [ ] Test file imports from new module path
- [ ] `python3 -c "from new_module import Thing"` succeeds directly (no cache)
- [ ] Full test suite passes: `pytest tests/ -q`
- [ ] For frontend: `npx tsc --noEmit` passes
- [ ] Committed with `refactor(scope):` prefix
