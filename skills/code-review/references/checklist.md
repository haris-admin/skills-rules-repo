# Comprehensive Code Review Checklist

Use this checklist during code review audits.

## 1. Architecture & Design
- [ ] Does the change follow established architectural patterns in the codebase?
- [ ] Are concerns properly separated (UI, business logic, data persistence)?
- [ ] Are interfaces clean and minimal?
- [ ] Is over-engineering avoided (YAGNI principle)?

## 2. Security & Compliance
- [ ] No hardcoded secrets, API tokens, passwords, or connection strings.
- [ ] External inputs are validated, typed, and sanitized.
- [ ] Sensitive data is not logged in plain text.
- [ ] Authorization checks are performed on every protected endpoint.

## 3. Reliability & Error Handling
- [ ] Errors are captured and handled gracefully.
- [ ] Network requests have sensible timeouts and retry strategies.
- [ ] Database transactions are used where atomicity is required.
- [ ] Resources (file descriptors, sockets, streams) are properly closed.

## 4. Performance
- [ ] No unintentional quadratic loops or N+1 queries.
- [ ] Large datasets are paginated or streamed.
- [ ] Heavy operations are offloaded from synchronous main loops.

## 5. Testing & Verification
- [ ] Unit tests added or updated for new business logic.
- [ ] Edge cases (empty sets, maximum bounds, negative values) tested.
- [ ] All automated tests pass.
