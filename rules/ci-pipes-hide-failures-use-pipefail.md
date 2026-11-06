# A pipe hides a failing tool: use pipefail and never chain after tail

In CI shells and in the terminal, the exit status of `tool | tee file` or `tool | tail` is the last command's. A failing scanner or test then looks like success.

**Scope:** GitHub Actions and other CI `run:` steps, shell scripts, and any agent chaining commands with `&&`.

---

## Core Directives

1. **Set pipefail**: in GitHub Actions use `defaults.run.shell: bash` (which runs `bash -e -o pipefail`), and add a test that pins it for every workflow that pipes into `tee`.
2. **Do not chain a commit after a pipeline ending in `| tail`**: `pytest | tail && git commit` commits even when pytest failed. Capture the exit status first or use `set -o pipefail`.
3. **Prove a gate can fail**: when adding a gate, run it once on a known-bad input or read the log for the exit code, so a green run means something.

## Why this exists

**6 Nov 2026 (HandleDispute):** the first scheduled quality run passed with a critical `npm audit` finding because `| tee` masked the exit code. In the same session a commit went in with one failing test because the test run ended in `| tail`.
