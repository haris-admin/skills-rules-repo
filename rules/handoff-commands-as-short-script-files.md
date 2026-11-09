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

7. **Make the name typo-proof.** On 3 Nov 2026 `~/hd-ses-apply.sh` was typed with a trailing comma, and `~/hd-` and `~/hd` were sent twice as truncated fragments. Prefer a name of 10 characters or fewer, give a second short alias (`ln -s`) when the first fails, and tell the user the exact command with no trailing punctuation.
8. **Infrastructure applies are always handed over.** The auto-mode classifier blocks agent `terraform apply`. Save the plan with `-out`, show the summary, then write a script that applies that exact plan file. Never chain a dry run and its apply into one command (see `dry-run-output-read-before-apply`).
9. **Tell the user which scripts are finished** and to delete them (token and apply scripts are one-time).
10. **One command per line, no trailing punctuation.** On 9 Nov 2026 `~/prod-tunnel.sh` and `open` pasted on two lines ran as two commands (the second was the macOS `open`), and `~/chk-stuck.sh,` with a trailing comma failed three times. Give each command on its own single line. If a stray name keeps recurring, a symlink with that exact name is a harmless way to unblock.
11. **Do not assume a port or a process pattern.** Let the script find the tunnel (`lsof -nP -iTCP -sTCP:LISTEN`, the `session-manager-plugin` row). A `pkill -f` pattern that does not match leaves the production tunnel open.
12. **Close what you opened before deleting the script that closes it.** When a tunnel script is deleted first, give the user the PID and `kill <pid>`, then ask them to confirm the port is silent.

## Verification & Guardrails

- If the user reports a wrapped or split command, the fix is a shorter path, not repeating the long one.

7. **One script path per `!` line.** `! ~/a.sh, ~/b.sh` is read as the single file name `~/a.sh,` and nothing runs (AMLHive, 8 Nov 2026). Give one command per line, in order, and wait for each result.
8. **Never test a gate through a truncating pipe.** A push script that ran `check | tail -3` and then `grep -q "RESULT: PASS"` refused a passing release. Send the full output to a file, show the part you want, and grep the file.
9. **A script that makes many API calls (Plane closes) outlasts the 120 second foreground limit** and moves to the background. Tell the user not to start a second copy and report from its output file.
10. **macOS bash 3.2 mishandles a quoted heredoc inside `$( ... )`.** Write the remote script to a file with a top-level `cat > "$F" <<'EOF'`, substitute placeholders with Python, and give the script a dry-run switch that stops before any remote call. Run the dry run before handing it over.
11. **Delete handoff scripts of a release once it is live and verified**, and remove its worktree (`git worktree remove`, never force). The branch stays.
