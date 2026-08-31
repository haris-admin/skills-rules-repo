---
name: crap-score
description: Calculate and reduce Change Risk Anti-Patterns (CRAP) by measuring cyclomatic complexity against automated test coverage.
---

# CRAP Score Analysis

## Definition
`CRAP(m) = comp(m)^2 * (1 - cov(m))^3 + comp(m)`
- `comp(m)`: Cyclomatic complexity of method `m`.
- `cov(m)`: Test coverage of method `m` (0.0 to 1.0).

## Thresholds
- **CRAP <= 30**: Acceptable risk.
- **CRAP > 30**: High risk — requires immediate refactoring (breaking into smaller pure functions) or increasing unit test coverage.

