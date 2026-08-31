# Codex CLI invocation pitfalls on WSL (Aug 2026)

Two dispatch-burning failures hit in one session; both are durable environment
facts on HarisHomeLab01, NOT one-off errors.

## 1. WSL `codex` on PATH may resolve to a BROKEN Windows npm shim

Symptom: a background `codex exec ...` job dies instantly with
`Error: No such file or directory (os error 2)` — or `codex exec --help`
prints `/mnt/c/Users/habib/AppData/Roaming/npm/node_modules/node/bin/node:
1: This: not found`.

Root cause: `/mnt/c/Users/habib/AppData/Roaming/npm` is on the WSL PATH (via
the Windows PATH inheritance) and its `codex` is a Windows `.cmd` shim that
cannot run inside WSL. `which -a codex` shows BOTH
`/mnt/c/Users/habib/AppData/Roaming/npm/codex` (broken, first) and the nvm
binary.

Fix — always use the nvm binary explicitly:
```bash
export PATH="$HOME/.nvm/versions/node/v24.18.0/bin:$PATH"
codex --version   # confirm it's the nvm one BEFORE dispatching
```
Check `which -a codex` first if in doubt. A broken shim fails in ~1s, so
verify with `codex --version` before starting any long `codex exec` job —
otherwise you burn a dispatch cycle on an instant failure.

## 2. `codex exec` has NO `-C` cwd flag

`codex exec -C <name> "prompt"` errors (`No such file or directory`). Codex
exec does not take a `-C`/cwd flag. Instead `cd` into the trusted directory
first:

```bash
cd ~/code/amlhive1          # trusted dir satisfies git-repo check
codex exec --json -m gpt-5.6-terra "prompt..."
```

Running from `~/code/amlhive1` also avoids
"Not inside a trusted directory and --skip-git-repo-check was not specified."

## Verification recipe

```bash
which -a codex                    # look for the /mnt/c/... shim
export PATH="$HOME/.nvm/versions/node/v24.18.0/bin:$PATH"
codex --version                   # must print a real version, not "This: not found"
cd ~/code/amlhive1 && codex exec --json -m gpt-5.6-terra "echo ok"
```
