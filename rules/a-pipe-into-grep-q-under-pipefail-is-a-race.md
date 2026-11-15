# A pipe into `grep -q` under pipefail is a race; read all the output (all agents, all repos)

Applies when an agent writes or reviews a shell script that checks for a container, file or line with `command | grep -q`, under `set -o pipefail`.

## Why this exists
**15 Nov 2026, HandleDispute first deploy in its own AWS account (OpenSpec 53d):** the production workflow stopped at the tests gate. `docker ps -a --format '{{.Names}}' | grep -qx db` exits at the first match and closes the pipe; the writer gets a broken pipe (exit 141, or 120 for a Python shim), and `pipefail` reports the whole check as failed, so an existing container was read as missing and the script tried to create it again. The test had failed intermittently for a week and was dismissed as flaky; it was a real race that depends on how much output is still to be written.

## Rules
1. In a script with `pipefail`, test for a match with `... | grep -x NAME >/dev/null` (reads all input) or capture the output first (`names="$(cmd)"; grep -qx NAME <<<"$names"`). Never `cmd | grep -q`.
2. Write a test that makes the writer's output huge (hundreds of thousands of lines, the wanted line first) so the race fails every time, and a static guard against the pattern.
3. An intermittent test failure is a defect until a cause is found. Run it in a loop, read the error, and reproduce it deterministically before calling it flaky.
4. Check the CI log for the real exit code and error text before assuming the test is at fault; a deploy gate that fails once is evidence, not noise.
