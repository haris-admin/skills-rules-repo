---
name: test-driven-development
description: >-
  Implement features using the Red-Green-Refactor Test-Driven Development (TDD) cycle. Use when the user requests TDD, test-first development, or creating unit test suites.
---

# Test-Driven Development (TDD) Skill

Guides the agent in executing disciplined Red-Green-Refactor development cycles.

## Workflow

1. **Step 1: Write a Failing Test (RED)**
   - Define the expected behavior or public interface.
   - Write a unit test asserting the expected outcome.
   - Run test runner to verify the test fails for the expected reason (and not due to a syntax error or typo).

2. **Step 2: Implement Minimal Code (GREEN)**
   - Write the simplest possible code to make the test pass.
   - Avoid implementing future or speculative requirements.
   - Run test runner to confirm test passes.

3. **Step 3: Refactor Cleanly (REFACTOR)**
   - Eliminate duplication, improve naming, optimize structure.
   - Run test runner to ensure no regressions occurred.

4. **Step 4: Repeat with Edge Cases**
   - Repeat the cycle for boundaries, error states, and corner cases.

## Reference

- [Testing Patterns & Mocking Best Practices](./references/testing-patterns.md)
