# Long gate runs start in their own process session and record the exit code

A full test suite that takes about half an hour must not share the agent shell's process group, and its result must be read from a file, not from a notification.

**Scope:** any agent or engineer starting a long background run (full test suite, CI gate script) from an agent shell.

## Why this exists

Tap-Ease Portal 4.60.01, 20 Nov 2026. The first full-suite gate was started with `nohup bash gate.sh &` from the agent shell. It died near the end with exit 143 (SIGTERM) and no test result, 28 minutes in, after the shell's process group was cleaned up. The run had to be repeated. The second run, started with Python `subprocess.Popen(..., start_new_session=True)` and all three standard streams redirected, survived. macOS has no `setsid` command.

## Core Directives

1. **Start it in a new session:** `python3 -c "import subprocess,sys; subprocess.Popen(['bash',sys.argv[1]], stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)" gate.sh`. A bare `nohup ... &` is not enough.
2. **Write `echo exit=$? >> <log>` after each command and a `done` marker file at the end.** Read the summary line and the exit code, never the "completed (exit code 0)" of a watcher, which is the exit of the last command in the line.
3. **Use a fresh scratch database per run and drop it at the end.** Do not delete the previous run's logs until the new run has finished: they are the only evidence of why it died.
4. **An exit 143 is a kill, not a test result.** Do not read the partial progress as pass or fail; restart.
5. **Compare against a clean baseline.** When the full suite is red, run the same suite on a clean worktree of the deployed commit (with `.env` copied in) and compare failure ids with `comm`. Only failures absent from the baseline are yours.
