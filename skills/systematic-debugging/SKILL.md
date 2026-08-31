---
name: systematic-debugging
description: Four-phase root-cause analysis debugging methodology — reproduce, isolate, name, fix. No symptom patches.
---

# Systematic Debugging Skill

## When to use
Invoke when a bug is reported, a test fails, or unexpected behaviour is observed. This skill enforces the Sovereign Constitution's debugging rule.

## The Four Phases

### Phase 1: Reproduce
- Run the failing scenario exactly as described.
- Capture the full error output (stack trace, console logs, HTTP status).
- If it cannot be reproduced, document the conditions tried and ask the user for more context.
- **Gate:** Do not proceed until the failure is reliably triggered.

### Phase 2: Isolate
- Find the smallest input, state, or code path that triggers the failure.
- Comment out or bypass surrounding code to narrow the scope.
- Use binary search on recent commits (`git bisect`) if the bug is a regression.
- Check: Is this a data issue, a logic issue, or an environment issue?
- **Gate:** The failure must be traceable to a single module or function.

### Phase 3: Name the Root Cause
- State the root cause in one sentence: "X happens because Y does Z when condition W is true."
- If the root cause cannot be named after reasonable investigation, say so explicitly and ask — do not guess.
- Distinguish between the **symptom** (what the user sees) and the **cause** (why it happens).
- **Gate:** The one-sentence cause must explain all observed symptoms.

### Phase 4: Minimal Fix
- Propose the smallest change that addresses the root cause.
- No "just add try/catch" patches. No fixing symptoms while the cause persists.
- No drive-by refactoring — fix only what is broken.
- Write or update a test that would have caught the bug.
- Run the full test suite to confirm no regressions.

## Anti-Patterns (never do these)
- Wrapping errors in generic catch blocks without understanding them.
- Adding defensive null checks everywhere instead of fixing the source of nulls.
- Blaming "race conditions" without proving the timing issue.
- Changing multiple things at once so you cannot tell which one fixed it.

## Output Format
After completing all four phases, summarise:
```
Bug: [one-line description]
Symptom: [what the user saw]
Root cause: [one sentence]
Fix: [what was changed and why]
Test: [what test covers this]
```
