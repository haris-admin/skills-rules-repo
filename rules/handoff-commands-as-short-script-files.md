# Handoff commands as short script files

When the user must run a command themselves, create a short executable script file at a short path and give only that path.

**Scope:** every agent, on every machine, whenever a command has to be run by the human (for example `! cmd` after a permission block, or a step that reads a secret).

## Why this exists

Added 18 Oct 2026 (Haris). Long paths wrapped and split in his terminal and a relative path failed after the shell moved directory. One command took four attempts.

## Core Directives

1. **Make the script first.** Write `~/<short-name>.sh` with absolute paths inside, `set -euo pipefail` where safe, and no reliance on the current directory.
2. **Check it.** Run `bash -n` on it before handing it over.
3. **Give only the short command.** For example `! ~/stg-probe.sh`.
4. **Never put secrets in the script or its output.** Print status and shapes only.
5. **Say what the output means and tell the user to delete the file when done.**

6. **A script that prompts for a password cannot run through `! <cmd>`.** That shell has no keyboard input, so the prompt closes at once (apksigner: "standard input closed"). Give `! open -a Terminal ~/<name>.sh` instead, read the password in the script with `read -r -s`, strip whitespace and non-printing characters (a pasted password arrived as "not ASCII"), pass it by environment variable (`--ks-pass env:VAR`), `unset` it after use, `tee` only non-secret output to a log the agent can read, and end with `read -r -p "Press Return to close."` so the window stays open. Running `open` twice opens two windows waiting at the same prompt; tell the user to use one.

## Verification & Guardrails

- If the user reports a wrapped or split command, the fix is a shorter path, not repeating the long one.
