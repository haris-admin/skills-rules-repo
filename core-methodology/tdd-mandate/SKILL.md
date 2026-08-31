---
name: tdd-mandate
description: Enforce strict Test-Driven Development (TDD) where every implementation traces to an explicit requirement and passes exhaustive tests before shipping.
---

# Test-Driven Development (TDD) Mandate

## Chain of Authority
`Requirement (Spec / User Request) → Test Cases (Executable Requirement) → Implementation (Must pass tests; no exceptions)`

## Core Rules

1. **Spec-Driven Tests**: Tests come from requirements, not from code. Every test must trace to an explicit requirement (task ID, design doc clause, or user instruction). A requirement with no test is not implemented.
2. **Fix Implementation, Not Tests**: If a test case fails and is aligned with the requirement, **fix the implementation**. Never alter or loosen the test to accommodate the implementation.
3. **Requirement Changes are Explicit**: Tests change ONLY when requirements change. If implementation cannot satisfy the requirement without architectural drift, pause and resolve the requirement change first.
4. **Exhaustive Coverage**: Happy path alone is never done. Tests must cover boundary conditions, invalid inputs, edge cases, error handlers, and failure modes.
5. **Red → Green → Done**: Never skip the Red phase. Write the failing test first and confirm it fails for the expected reason before writing production code.
6. **No Spec Leakage**: Do not test implementation details (internal private helpers); test observable behavior and contract boundaries.

