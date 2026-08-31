# Testing Patterns & Mocking Best Practices

## Test Pyramid
1. **Unit Tests (70-80%)**: Fast, isolated, test pure functions and domain logic in memory.
2. **Integration Tests (15-20%)**: Test interactions between components, database queries, or external adapters.
3. **End-to-End Tests (5-10%)**: Test critical end-to-end user flows across the full stack.

## Test Doubles Terminology
- **Dummy**: Passed around but never actually used (e.g. fill parameter lists).
- **Stub**: Provides canned answers to calls made during the test.
- **Spy**: Records information about how it was called (e.g. invocation count, arguments).
- **Mock**: Objects pre-programmed with expectations which form a specification of the calls they are expected to receive.
- **Fake**: Has working implementation, but takes shortcuts (e.g. in-memory database).

## Mocking Rules of Thumb
- **Mock at the boundaries**: Mock external network calls, third-party SDKs, and payment gateways.
- **Don't mock what you don't own**: Prefer wrapping third-party libraries in thin adapter interfaces, and mock your own adapter.
- **Verify state over interaction**: Assert on outputs and return values rather than asserting every internal private call order.
