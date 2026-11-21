# A shell snippet must not rely on word splitting of unquoted variables

zsh does not split an unquoted variable on spaces or newlines the way bash does, so a loop or a command built from a string variable breaks without an obvious error.

**Scope:** commands an agent runs through a tool that uses the user's login shell (zsh on macOS).

---

## Core Directives

1. **Use arrays or explicit lists** (`for f in a b c`) instead of a string variable that is split later.
2. **Put anything non-trivial in a script with a bash shebang** and run it with `bash`, then check it with `bash -n`.
3. **Read the first error literally**: "No such file" with several paths joined in one message means the variable was not split.

## Why this exists

**21 Nov 2026 (HandleDispute):** two loops over a pair of values and a file list failed in zsh because the strings were not split (a database name was empty, and a path list reached `sed` as one argument). The fix was a helper script run with bash.
