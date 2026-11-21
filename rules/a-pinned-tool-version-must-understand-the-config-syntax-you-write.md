# A pinned tool version must understand the config syntax you write

A config key from a newer release is silently ignored by an older pinned binary, so the check you configured never applies.

**Scope:** scanner, linter and formatter configuration in CI (gitleaks, Ruff, Semgrep and similar).

---

## Core Directives

1. **Run the pinned image or binary on the real repository** before you tick a task that says the gate is configured, and record the result.
2. **Compare findings before and after the config change**: if the count did not move, the config is not being read.
3. **Read the version of the syntax in the tool's release notes** when you copy an example from its documentation.
4. **Keep the verification task open** until the gate has run green in CI.

## Why this exists

**21 Nov 2026 (HandleDispute):** a gitleaks allowlist used a top-level `[[allowlists]]` with `targetRules`, which needs 8.25 or newer, while CI pinned 8.21.2. The weekly gate failed for days. The task that would have caught it (run the pinned image over full history) had never been ticked. A per-rule `[[rules.allowlists]]` cut the local findings from 49 to 18.
