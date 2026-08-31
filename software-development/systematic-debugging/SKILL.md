---
name: systematic-debugging
description: "4-phase root cause debugging: understand bugs before fixing."
version: 1.1.0
author: Hermes Agent (adapted from obra/superpowers)
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [debugging, troubleshooting, problem-solving, root-cause, investigation]
    related_skills: [test-driven-development, writing-plans, subagent-driven-development]
---

# Systematic Debugging

## Overview

Random fixes waste time and create new bugs. Quick patches mask underlying issues.

**Core principle:** ALWAYS find root cause before attempting fixes. Symptom fixes are failure.

**Violating the letter of this process is violating the spirit of debugging.**

## The Iron Law

```
NO FIXES WITHOUT ROOT CAUSE INVESTIGATION FIRST
```

If you haven't completed Phase 1, you cannot propose fixes.

## When to Use

Use for ANY technical issue:
- Test failures
- Bugs in production
- Unexpected behavior
- Performance problems
- Build failures
- Integration issues

**Use this ESPECIALLY when:**
- Under time pressure (emergencies make guessing tempting)
- "Just one quick fix" seems obvious
- You've already tried multiple fixes
- Previous fix didn't work
- You don't fully understand the issue

**Don't skip when:**
- Issue seems simple (simple bugs have root causes too)
- You're in a hurry (rushing guarantees rework)
- Someone wants it fixed NOW (systematic is faster than thrashing)

## The Four Phases

You MUST complete each phase before proceeding to the next.

---

## Phase 1: Root Cause Investigation

**BEFORE attempting ANY fix:**

### 1. Read Error Messages Carefully

- Don't skip past errors or warnings
- They often contain the exact solution
- Read stack traces completely
- Note line numbers, file paths, error codes

**Action:** Use `read_file` on the relevant source files. Use `search_files` to find the error string in the codebase.

### 2. Reproduce Consistently

- Can you trigger it reliably?
- What are the exact steps?
- Does it happen every time?
- If not reproducible → gather more data, don't guess

**Action:** Use the `terminal` tool to run the failing test or trigger the bug:

```bash
# Run specific failing test
pytest tests/test_module.py::test_name -v

# Run with verbose output
pytest tests/test_module.py -v --tb=long
```

### 3. Check Recent Changes

- What changed that could cause this?
- Git diff, recent commits
- New dependencies, config changes

**Action:**

```bash
# Recent commits
git log --oneline -10

# Uncommitted changes
git diff

# Changes in specific file
git log -p --follow src/problematic_file.py | head -100
```

### 4. Gather Evidence in Multi-Component Systems

**WHEN system has multiple components (API → service → database, CI → build → deploy):**

**BEFORE proposing fixes, add diagnostic instrumentation:**

For EACH component boundary:
- Log what data enters the component
- Log what data exits the component
- Verify environment/config propagation
- Check state at each layer

Run once to gather evidence showing WHERE it breaks.
THEN analyze evidence to identify the failing component.
THEN investigate that specific component.

### 5. Trace Data Flow

**WHEN error is deep in the call stack:**

- Where does the bad value originate?
- What called this function with the bad value?
- Keep tracing upstream until you find the source
- Fix at the source, not at the symptom

**Action:** Use `search_files` to trace references:

```python
# Find where the function is called
search_files("function_name(", path="src/", file_glob="*.py")

# Find where the variable is set
search_files("variable_name\\s*=", path="src/", file_glob="*.py")
```

### 6. Check for Cache Masking (.pyc, .pytest_cache, node_modules/.cache)

**WHEN tests pass but you suspect the source code is broken (e.g., after a refactor/extraction):**

Python (and some JS tools) cache compiled bytecode. Tests can pass from stale cache even when the source `.py` file is syntactically invalid.

**Symptoms of cache masking:**
- All tests pass but a direct import fails: `python3 -c "from module import thing"` → SyntaxError
- You deleted a function but tests still find it
- A refactor you're certain removed code, yet tests are green

**Action — Clear and re-verify:**
```bash
# Clear Python caches
rm -rf __pycache__ .pytest_cache tests/**/__pycache__ src/**/__pycache__

# Re-run tests from clean state
pytest tests/ -q

# ALSO: direct import check
python3 -c "import sys; sys.path.insert(0, 'src/backend'); from module import thing; print('OK')"
```

**If tests now fail:** The source was broken all along. The cache was hiding it. Fix the source.

**If direct import fails but pytest passes:** pytest is loading from a different cache. Check for `.pyc` files in unexpected locations or a stale virtual environment.

### 7. Multi-Branch & Cross-Version Error Tracing

**WHEN a bug is reported from a deployed/remote version but the code on your current branch doesn't match:**

The deployed version may have features (endpoints, services, models) that don't exist in your workspace. **Do not assume the bug is in the code you have checked out.**

**Procedure:**

1. **Identify the deployed version** — Check the running instance:
   ```bash
   # From the deployed API docs or /openapi.json
   web_extract(urls=["https://deployed-instance/docs"])
   # Look for: "Version: X.Y.Z" or "API Version: X.Y.Z"
   ```

2. **Find the feature branch** — List remote branches to locate the version that matches:
   ```bash
   git fetch origin
   git branch -r
   git tag -l | sort -V  # Tags often match release versions
   ```
   Look for branch names containing feature keywords (`card`, `integration`, etc.) or matching the version prefix.

3. **Check if the feature exists on your branch** — Search your current branch first:
   ```bash
   search_files(pattern="endpoint_path_or_function_name", path="app/", file_glob="*.py")
   ```
   If nothing found, the feature is on a different branch.

4. **Read code from the feature branch** — `git show` reads files from any branch without switching:
   ```bash
   git show origin/feature-branch:path/to/file.py
   ```
   Use this to read routers, services, models, and config from the branch that has the deployed code.

5. **Trace the error through the feature branch** — Follow the same technique as single-branch debugging but executed through `git show` pipes. Read the full chain: router → model validation → service call → external API call.

6. **Check DI container registration** — When the error is about an "unknown protocol" or "unsupported protocol", look at:
   - The dependency injection container: `app/dependencies/container.py`
   - The service protocol: `app/services/protocols.py`
   - The startup registration: `app/asgi.py` imports
   - The service module's bottom (where `Container.register()` is called)
   
   An `"UnsupportedProtocol"` error often means httpx received an empty/malformed base URL because the config for the external service (CARD_SERVICE_BASE_URL, etc.) is missing or empty.

7. **Determine fix location** — Decide whether to:
   - Fix on your branch and request a forward-merge to the feature branch
   - Cherry-pick the fix to the feature branch
   - Alert the user that the fix needs to go into a specific branch

### 8. Error Cascade Analysis — Tracing Through Dependent Stages

**WHEN a user reports multiple errors that appear to be separate bugs (e.g., A fails, then B fails, then C fails):**

The errors are often NOT independent — one validation failure at an earlier stage blocks everything downstream. Fix the root validation, and the cascade resolves itself.

**Procedure:**

1. **Map the dependency chain** — Read the errors in reverse order. Identify which step depends on which:
   ```
   C fails ("no card assigned") → depends on B succeeding
   B fails ("missing KYC fields") → depends on A providing those fields
   A fails ("extra inputs not permitted for dob") → FIELD NOT ACCEPTED BY VALIDATION
   ```
   Root cause is stage A. Fixing A unblocks B, which unblocks C.

2. **Classify each error in the cascade:**
   - **Direct error** — The actual root cause (validation rejection, missing config, etc.)
   - **Downstream error** — A consequence of the root cause that looks like a separate bug
   - **Symptom error** — The user-facing error that triggered the report

3. **Verify the chain** — For each downstream error, confirm the prerequisite:
   ```python
   # B's code checks for field from A
   if not user["dob"]:  # ← This will always be None if A doesn't save it
       missing_fields.append("dob")
   ```
   When every downstream error traces back to the same root validation failure, you have a confirmed cascade.

4. **Fix at the source** — Address the root validation/acceptance issue. Do NOT patch downstream checks — they are correct guardrails. The fix belongs at the stage where the data is first rejected.

**Example from a real session:**
| Error | Looks Like | Actually Is |
|-------|-----------|-------------|
| `"/admin/cards/5/kyc" → "No card assigned"` | Card assign bug | Downstream — card assign never ran |
| `"/admin/cards/assign" → "Missing KYC fields: dob"` | KYC validation bug | Downstream — `dob` was never saved |
| `"/admin/update_user_profile" → "Extra inputs not permitted" on dob` | Validation bug | **ROOT CAUSE** — model had `extra="forbid"` & no `dob` field |

**BEFORE diagnosing the last error in the chain, trace backward to find the first error.** Fix the first one, re-test the flow, and the rest often vanish.

### 9. DI Container / Protocol Registration Debugging

**WHEN the error message contains "UnsupportedProtocol", "No factory registered", or mentions a service protocol by name:**

The dependency injection container doesn't have the required service registered. This is a startup/configuration issue, not a runtime logic bug.

**Common causes:**
- The service module is not imported at startup (check `app/asgi.py` for the import)
- The service module's `Container.register()` call at module bottom didn't execute
- The service requires config (`base_url`, `client_id`, etc.) that's empty or missing
- The container's `get()` raises `ValueError` when no factory is registered

**Trace path:**
- Check the container registration (`app/dependencies/container.py`)
- Check the service module bottom for `Container.register()`
- Check startup import in `asgi.py`
- Check the protocol definition in `app/services/protocols.py`
- Check config defaults (empty string = httpx "UnsupportedProtocol")

"UnsupportedProtocol" from httpx specifically means the `base_url` is an empty string. The config defaults to `""` when the env var is not set, and httpx raises this when trying to make a request to an empty URL.

### Phase 1 Completion Checklist

- [ ] Error messages fully read and understood
- [ ] Issue reproduced consistently
- [ ] Recent changes identified and reviewed
- [ ] Evidence gathered (logs, state, data flow)
- [ ] Problem isolated to specific component/code
- [ ] Root cause hypothesis formed
- [ ] **Multi-branch:** Confirmed which branch(es) contain the affected code
- [ ] **Multi-branch:** Read the full error chain from the correct branch

**STOP:** Do not proceed to Phase 2 until you understand WHY it's happening.

---

## Phase 2: Pattern Analysis

**Find the pattern before fixing:**

### 1. Find Working Examples

- Locate similar working code in the same codebase
- What works that's similar to what's broken?

**Action:** Use `search_files` to find comparable patterns:

```python
search_files("similar_pattern", path="src/", file_glob="*.py")
```

### 2. Compare Against References

- If implementing a pattern, read the reference implementation COMPLETELY
- Don't skim — read every line
- Understand the pattern fully before applying

### 3. Identify Differences

- What's different between working and broken?
- List every difference, however small
- Don't assume "that can't matter"

### 4. Understand Dependencies

- What other components does this need?
- What settings, config, environment?
- What assumptions does it make?

---

## Phase 3: Hypothesis and Testing

**Scientific method:**

### 1. Form a Single Hypothesis

- State clearly: "I think X is the root cause because Y"
- Write it down
- Be specific, not vague

### 2. Test Minimally

- Make the SMALLEST possible change to test the hypothesis
- One variable at a time
- Don't fix multiple things at once

### 3. Verify Before Continuing

- Did it work? → Phase 4
- Didn't work? → Form NEW hypothesis
- DON'T add more fixes on top

### 4. When You Don't Know

- Say "I don't understand X"
- Don't pretend to know
- Ask the user for help
- Research more

---

## Phase 4: Implementation

**Fix the root cause, not the symptom:**

### 1. Create Failing Test Case

- Simplest possible reproduction
- Automated test if possible
- MUST have before fixing
- Use the `test-driven-development` skill

### 2. Implement Single Fix

- Address the root cause identified
- ONE change at a time
- No "while I'm here" improvements
- No bundled refactoring

### 3. Verify Fix

```bash
# Run the specific regression test
pytest tests/test_module.py::test_regression -v

# Run full suite — no regressions
pytest tests/ -q
```

### 4. If Fix Doesn't Work — The Rule of Three

- **STOP.**
- Count: How many fixes have you tried?
- If < 3: Return to Phase 1, re-analyze with new information
- **If ≥ 3: STOP and question the architecture (step 5 below)**
- DON'T attempt Fix #4 without architectural discussion

### 5. If 3+ Fixes Failed: Question Architecture

**Pattern indicating an architectural problem:**
- Each fix reveals new shared state/coupling in a different place
- Fixes require "massive refactoring" to implement
- Each fix creates new symptoms elsewhere

**STOP and question fundamentals:**
- Is this pattern fundamentally sound?
- Are we "sticking with it through sheer inertia"?
- Should we refactor the architecture vs. continue fixing symptoms?

**Discuss with the user before attempting more fixes.**

This is NOT a failed hypothesis — this is a wrong architecture.

---

## Red Flags — STOP and Follow Process

If you catch yourself thinking:
- "Quick fix for now, investigate later"
- "Just try changing X and see if it works"
- "Add multiple changes, run tests"
- "Skip the test, I'll manually verify"
- "It's probably X, let me fix that"
- "I don't fully understand but this might work"
- "Pattern says X but I'll adapt it differently"
- "Here are the main problems: [lists fixes without investigation]"
- Proposing solutions before tracing data flow
- **"One more fix attempt" (when already tried 2+)**
- **Each fix reveals a new problem in a different place**

**ALL of these mean: STOP. Return to Phase 1.**

**If 3+ fixes failed:** Question the architecture (Phase 4 step 5).

## Common Rationalizations

| Excuse | Reality |
|--------|---------|
| "Issue is simple, don't need process" | Simple issues have root causes too. Process is fast for simple bugs. |
| "Emergency, no time for process" | Systematic debugging is FASTER than guess-and-check thrashing. |
| "Just try this first, then investigate" | First fix sets the pattern. Do it right from the start. |
| "I'll write test after confirming fix works" | Untested fixes don't stick. Test first proves it. |
| "Multiple fixes at once saves time" | Can't isolate what worked. Causes new bugs. |
| "Reference too long, I'll adapt the pattern" | Partial understanding guarantees bugs. Read it completely. |
| "I see the problem, let me fix it" | Seeing symptoms ≠ understanding root cause. |
| "One more fix attempt" (after 2+ failures) | 3+ failures = architectural problem. Question the pattern, don't fix again. |

## Language-Specific Debugger References

This skill covers the **methodology** for debugging. For **tool-level** guidance (exact commands, recipes, Hermes-specific scenarios):

- `references/python-debugging.md` — Python pdb, debugpy, remote-pdb, testing under pytest-xdist, Hermes gateway/tui debugging
- `references/node-inspect-debugging.md` — Node.js `node inspect`, CDP, TypeScript sourcemaps, ui-tui debugging

Load these references when you need a specific command or recipe for the language you're debugging.

## Quick Reference

| Phase | Key Activities | Success Criteria |
|-------|---------------|------------------|
| **1. Root Cause** | Read errors, reproduce, check changes, gather evidence, trace data flow | Understand WHAT and WHY |
| **2. Pattern** | Find working examples, compare, identify differences | Know what's different |
| **3. Hypothesis** | Form theory, test minimally, one variable at a time | Confirmed or new hypothesis |
| **4. Implementation** | Create regression test, fix root cause, verify | Bug resolved, all tests pass |

## Hermes Agent Integration

### Investigation Tools

Use these Hermes tools during Phase 1:

- **`search_files`** — Find error strings, trace function calls, locate patterns
- **`read_file`** — Read source code with line numbers for precise analysis
- **`terminal`** — Run tests, check git history, reproduce bugs
- **`web_search`/`web_extract`** — Research error messages, library docs

### With delegate_task

For complex multi-component debugging, dispatch investigation subagents:

```python
delegate_task(
    goal="Investigate why [specific test/behavior] fails",
    context="""
    Follow systematic-debugging skill:
    1. Read the error message carefully
    2. Reproduce the issue
    3. Trace the data flow to find root cause
    4. Report findings — do NOT fix yet

    Error: [paste full error]
    File: [path to failing code]
    Test command: [exact command]
    """,
    toolsets=['terminal', 'file']
)
```

### With test-driven-development

When fixing bugs:
1. Write a test that reproduces the bug (RED)
2. Debug systematically to find root cause
3. Fix the root cause (GREEN)
4. The test proves the fix and prevents regression

## Real-World Impact

From debugging sessions:
- Systematic approach: 15-30 minutes to fix
- Random fixes approach: 2-3 hours of thrashing
- First-time fix rate: 95% vs 40%
- New bugs introduced: Near zero vs common

**No shortcuts. No guessing. Systematic always wins.**
