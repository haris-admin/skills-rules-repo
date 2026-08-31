---
name: refactoring-clean-code
description: >-
  Refactor complex code into modular, maintainable, and clean code while preserving functionality. Use when asked to refactor, simplify, clean up technical debt, or improve code quality.
---

# Refactoring & Clean Code Skill

Guides the agent in safely improving code structure, readability, and performance without introducing functional regressions.

## Workflow

1. **Step 1: Baseline & Safety Verification**
   - Ensure an existing test suite covers the area being refactored.
   - Run tests before making any modifications to establish green baseline.
   - If tests are missing, author baseline characterization tests first.

2. **Step 2: Identify Code Smells**
   - Spot long methods, god objects, duplicate logic, primitive obsession, or deeply nested conditionals (see [Code Smells Catalog](./references/code-smells.md)).

3. **Step 3: Stepwise Micro-Refactoring**
   - Apply single refactoring techniques in small, incremental steps:
     - **Extract Function / Method**: Decompose large routines.
     - **Replace Conditional with Polymorphism / Strategy Pattern**.
     - **Introduce Parameter Object**: Replace overly long argument lists.
     - **Inline Unnecessary Temporary Variables**.
   - Run test suite after each atomic step to verify behavior is preserved.

4. **Step 4: Verification & Walkthrough**
   - Confirm all tests pass.
   - Verify code readability, documentation, and types.

## Reference

- [Catalog of Common Code Smells & Refactorings](./references/code-smells.md)
