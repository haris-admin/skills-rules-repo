# Compound Engineering (upstream import)

Imported unmodified from EveryInc/compound-engineering-plugin, release
`compound-engineering-v3.29.0` (commit `4043703d32c5df9e35f22757dee22f3a72a99c66`,
25 Sep 2026), MIT licence (see LICENSE in this folder). Imported 26 Sep 2026.

## Local changes

- Plugin-namespaced invocations (`compound-engineering:ce-plan`) rewritten to
  the plain skill name (`ce-plan`), because these run as standalone skills, not
  as the plugin. No other edits to upstream files.
- Two local shortcut skills, not from upstream: `ce-draft` (runs
  `ce-brainstorm`) and `ce-execute` (runs `ce-work`), so every step of the
  loop has a `ce-` name.

## Core loop

| Call | Upstream skill | Does |
|---|---|---|
| draft | `ce-draft` (runs `ce-brainstorm`) | Turns an idea into a requirements-only plan (the WHAT) |
| plan | `ce-plan` | Adds the HOW to that plan; never writes code |
| execute | `ce-execute` (runs `ce-work`) | Builds and verifies the plan |
| review | `ce-code-review` | Reviews the diff before shipping |
| compound | `ce-compound` | Records the lesson so the next run is faster |
| all of it | `lfg` | Runs the loop end to end, hands off |

## Security review at import (26 Sep 2026)

No secrets, no pipe-to-shell installs, no raw force pushes. `ce-optimize`
runs `reset --hard` only inside its own experiment worktree. The brainstorm and
prototype web servers bind to 127.0.0.1. `ce-polish` calls OpenAI only when an
OpenAI key is set. `ce-babysit-pr`, `ce-commit-push-pr` and `lfg` commit and push
as part of their job: invoking them is the authorisation, so do not invoke them
on a repo where pushing needs a separate go (for example Simplifii-OS, where
`main` deploys).

## Updating

Replace the skill folders from a newer upstream release, re-apply the one
local change above, bump the release and commit here, then run
`python3 scripts/validate.py` and `python3 scripts/generate_catalog.py`.
