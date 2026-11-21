# Parallel full test suites on one machine contaminate each other

Two full suites that share a database, a proof file, a lock file or an upload folder produce failures that belong to neither branch.

**Scope:** agents comparing a branch against a baseline, or running two worktrees at once.

---

## Core Directives

1. **Run full suites one at a time** on one machine unless the suite is proven to isolate its database and files.
2. **A failure count that differs between two parallel runs is the contamination signal**: discard both runs and repeat sequentially.
3. **Compare a failing test on its own** on both branches, then run the full suite on each in turn.
4. **Say which runs were discarded** in the report so nobody reads a contaminated number as evidence.

## Why this exists

**21 Nov 2026 (HandleDispute):** a branch run and a clean baseline run, started together, failed 20 and 26 tests in different places. The same suite run alone passed all but one test, which passed on its own on both branches.
