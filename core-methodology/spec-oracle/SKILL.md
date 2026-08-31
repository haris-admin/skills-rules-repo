---
name: spec-oracle
description: Establish formal specifications as the definitive source of truth across agent sessions and human-in-the-loop workflows.
---

# Spec Oracle

## Principle
When code, tests, and documentation disagree, the **Specification** is the authoritative oracle.

## Decision Flow
1. **Spec is Clear, Implementation Fails**: Fix the implementation.
2. **Spec is Ambiguous**: Stop and request a structured human decision. Never guess or fabricate decisions.
3. **Spec Conflict**: Surface the specific conflicting clauses across files and wait for human resolution.
4. **Recorded Decisions are Final**: Never re-decide, second-guess, or revert an approved architectural decision within an agent session.

