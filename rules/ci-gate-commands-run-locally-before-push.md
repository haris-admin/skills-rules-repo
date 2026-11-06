# Run the CI gate commands locally before every push

Every check a CI or deploy gate runs must be run locally, with the CI tool versions, before pushing. A gate that fails on something you could have seen costs a release attempt.

**Scope:** all agents and developers on any repository with CI or deploy gates.

---

## Core Directives

1. **Run the exact gate commands**: formatter in check mode (for example `ruff format --check`), the linter, the security scanner, the API contract guard, snapshot and catalogue checks, then the tests.
2. **Use the CI interpreter version**: Bandit 1.8.6 crashed under Python 3.14 and passed under 3.13; check the scanner with the Python the workflow uses.
3. **Format after the last edit**: any file touched after the last formatter run (tests appended last) is the usual cause of a gate failure.
4. **Report what was not run**: if a gate could not be run locally (database revision mismatch, missing tool), say so and name the CI job that will run it.

## Why this exists

**6 Nov 2026 (HandleDispute):** the first deploy of 0.240.23 stopped at the new Ruff gate because one test file written after the last format run was unformatted. The gate worked, but the release was delayed by one run.
