# Testing Guidelines & Verification Standards

Guidelines for writing resilient, maintainable, and high-coverage automated tests.

## Core Testing Principles

1. **AAA Pattern (Arrange, Act, Assert)**:
   - Structure tests clearly into three distinct blocks.
   - Keep assertions focused on the behavior under test.

2. **Test Independence & Isolation**:
   - Each test must run independently in any order without relying on leftover state from previous tests.
   - Mock external network services, third-party APIs, and non-deterministic sources (timestamps, random generators).

3. **Boundary Condition & Edge Case Coverage**:
   - Test empty collections, single-item collections, and large datasets.
   - Test invalid inputs, type mismatches, null values, and out-of-range parameters.
   - Test failure modes: timeouts, network disconnection, database transaction rollbacks.

4. **Descriptive Test Names**:
   - Follow a readable pattern: `should_return_404_when_user_does_not_exist` or `test_calculate_tax_applies_discount_correctly`.

5. **Fast Feedback**:
   - Keep unit test suites blazing fast (< few seconds) so developers and agents can execute them continuously during development.
