# Common Coding Standards

Universal development principles, code hygiene, and architectural guidelines for all projects.

## Core Engineering Principles

1. **Simplicity and Readability**:
   - Write clean, self-documenting code. Favor descriptive naming over excessive commenting.
   - Avoid premature abstraction. Implement solutions for existing requirements, not speculative futures (YAGNI).
   - Functions should do one thing well and maintain single responsibility.

2. **Defensive Programming & Error Handling**:
   - Never swallow errors silently or use bare `except:` / `catch {}` blocks.
   - Always log meaningful error messages with context (parameters, identifiers, timestamps).
   - Validate and sanitize external inputs at system boundaries using schemas (e.g. Zod, Pydantic).

3. **Immutability & Pure Functions**:
   - Prefer immutable data structures and pure functions where practical.
   - Minimize shared mutable state across components or concurrent threads.

4. **Testing Standards**:
   - Write automated unit tests for business logic, utilities, and edge cases.
   - Ensure tests are deterministic, independent, and do not rely on hardcoded wall-clock time or external networks.

5. **Documentation Integrity**:
   - Maintain up-to-date documentation alongside code changes.
   - Preserve existing architectural comments and rationale during refactors.
