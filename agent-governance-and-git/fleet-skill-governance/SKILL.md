---
name: fleet-skill-governance
description: Mirror skill changes to the fleet repo + Mercury profiles.
version: 1.0.0
author: Pluto
license: MIT
---

# Fleet Skill Governance (skills-rules-repo + Windows Mercury profiles)

Every skill change is a FLEET change. The canonical, deployed skill library lives in
the `haris-admin/skills-rules-repo` (remote `https://github.com/haris-admin/skills-rules-repo`),
and six Windows-native Hermes agents (the **Mercury fleet**) carry their own copies of
shared skills in their profile folders. A skill updated in only one place drifts the
fleet — agents run different procedures for the same task.

## Hard rule (Haris, 31 Aug 2026)

> Any skill we modify → check whether other agents use it; if relevant, modify their
> copies too. Bring Windows-side sub-agent skills into the repo and check them in.

So after EVERY `skill_manage` write:
1. **Mirror to the repo** — copy the changed skill into
   `/mnt/c/Code/github/haris-admin/skills-rules-repo/<category>/<skill>/`, commit, push
   to `main`. (Windows path: `C:\Code\github\haris-admin\skills-rules-repo`.)
2. **Check the Mercury fleet** — if the same skill exists in a Windows agent profile
   (`/mnt/c/Users/habib/AppData/Local/hermes/profiles/<agent>/skills/...`) or is
   agent-relevant, update those copies too.
3. **Registry** — keep `fleet-agents.md` at the repo root accurate (agent → protocol
   skill mapping, shared-skill list).

## Repo layout (the category convention)

Category directories hold Hermes-native skills (e.g. `devops/`, `research/`,
`pluto-operations/`, `compliance/`, `software-development/`, `note-taking/`), each
skill a subdir with `SKILL.md` + optional `references/` `scripts/` `templates/`.
There is also a flat `skills/` dir (install.sh globs it) — prefer category dirs for
Hermes/Pluto skills; use flat only for install.sh-driven tool skills.

## Mercury fleet — the 6 Windows agents

Profiles live at `/mnt/c/Users/habib/AppData/Local/hermes/profiles/<agent>/` (each has
`SOUL`, `AGENT.md`, `.env`, `memory`, `skills/`). Launch: `powershell .\venv\Scripts\python.exe hermes -p <agent> chat -q` from the hermes-agent dir.

| Agent | Role | Protocol skill (repo category) |
|-------|------|--------------------------------|
| Aurora | Content & authority | `research/aurora-content-engine` |
| Caduceus | Compliance & payments watch | `compliance/caduceus-compliance-watch` |
| Lumen | Mempalace/knowledge-base health | `note-taking/lumen-palace-keeper` |
| Sol | Strategy synthesis & gating | `research/sol-strategy-engine` |
| Vigil | Monitoring & escalation | `devops/vigil-watch-protocol` |
| Vulcan | Build protocol (TDD/Codex) | `software-development/vulcan-build-protocol` |

Shared tool skills identical across all 6 profiles (canonical source: aurora profile):
`llm-wiki`, `codebase-inspection`, `node-inspect-debugger`, `python-debugpy`,
`simplify-code`.

## Workflow: sync a modified/imported skill

```bash
REPO=/mnt/c/Code/github/haris-admin/skills-rules-repo
PROF=/mnt/c/Users/habib/AppData/Local/hermes/profiles

# 1. copy skill into repo category dir (match repo's category conventions)
cp ~/.hermes/skills/<cat>/<skill>/SKILL.md "$REPO/<cat>/<skill>/SKILL.md"
cp -r ~/.hermes/skills/<cat>/<skill>/references "$REPO/<cat>/<skill>/" 2>/dev/null || true
cp -r ~/.hermes/skills/<cat>/<skill>/scripts "$REPO/<cat>/<skill>/" 2>/dev/null || true

# 2. propagate to any Windows agent profile that carries it
for agent in aurora caduceus lumen sol vigil vulcan; do
  if [ -d "$PROF/$agent/skills" ]; then
    cp ~/.hermes/skills/<cat>/<skill>/SKILL.md "$PROF/$agent/skills/<cat>/<skill>/SKILL.md" 2>/dev/null || true
  fi
done

# 3. commit + push repo
cd "$REPO" && git add -A && git commit -m "feat(skills): sync <skill>" && git push origin main
```

## Importing a new fleet skill (profile → repo)

When a Windows profile has a skill the repo lacks:
1. Read the profile copy first (`cat $PROF/<agent>/skills/<...>/SKILL.md`).
2. Pick the natural category (`research/`, `compliance/`, `note-taking/`, `devops/`,
   `software-development/`).
3. Copy SKILL.md + linked files; use the aurora profile copy as canonical when a
   shared skill appears identically in all 6 profiles.
4. Update `fleet-agents.md` if it's an agent-protocol skill; commit + push.

## Pitfalls

- **Always commit with a PATHSPEC — a bare `git commit` lands the whole index, not what you just staged.**
  In this repo the index is routinely dirty from other agents' work-in-progress, and `git pull
  --rebase --autostash` makes it worse: the autostash **restores previously-modified files as STAGED**.
  Verified 2026-09-18: a mirror commit of two skills also pushed 104 insertions/104 deletions of pure
  CRLF churn in an unrelated `autonomous-ai-agents/github-copilot-sdk/SKILL.md` that the autostash had
  re-staged. It had to be reverted in a follow-up commit. So: `git add -- <paths>` **and**
  `git commit -- <paths>`, or check `git diff --cached --name-only` immediately before committing.
  **Order matters when you also pass `-m`: `git commit -m "msg" -- <paths>`.** Everything AFTER the
  `--` is a pathspec, so `git commit -- <paths> -m "msg"` fails with
  `error: pathspec '-m' did not match any file(s) known to git` and commits NOTHING — the staged files
  stay staged and a subsequent bare `git push` reports `Everything up-to-date`, which reads as a
  successful mirror while nothing left the box. Verify the exit/HEAD (`git log -1 --format='%h %s'`)
  before claiming a mirror landed.
  When you do land churn by accident, prove it was churn before deciding (`git show <sha>:<path> | tr -d
  '\r'` vs the worktree copy — identical means line-endings only) and revert it rather than leaving a
  104-line phantom in the history. See `git-working-tree-hygiene` for the CRLF discipline itself.
- **A rebase can silently MERGE the same file you just mirrored.** If upstream changed the skill you
  are pushing, `git pull --rebase` merges both edits and the REPO copy becomes a SUPERSET of your WSL
  copy (verified 2026-09-18: upstream's new `amlhive-asic-sync` "Issue 374" section landed alongside
  the local addition). `diff` the pair after every push and merge the repo-only block INTO the WSL
  skill — re-copying WSL over the repo at that point would delete upstream's content.
- **Push auth:** the remote embeds the haris-admin-capable operator PAT directly in
  `origin`'s URL, and `git push origin main` works (verified 2026-09-16: `eba3fba..67d6d25`,
  `git ls-remote origin main` == local HEAD). An earlier note claiming pushes were BLOCKED
  since 3 Sep 2026 was wrong and caused agents to skip the mirror and report "push pending"
  — do not repeat it. The real trap is the reverse: the remote URL can end up with a
  DUPLICATED token (`https://oauth2:TOK@oauth2:TOK@github.com/...`), which makes git parse
  the second copy as host:port and fail with "Port number was not a decimal number".
  Check before pushing with `git config --get remote.origin.url | grep -o '@' | wc -l`
  (expect exactly 1); never print the token itself.
- **WSL↔Windows path:** repo on WSL is `/mnt/c/Code/github/haris-admin/skills-rules-repo`;
  Windows sees `C:\Code\github\haris-admin\skills-rules-repo`. Use the /mnt/c form in
  bash. Branch is `main`.
- **The security filter blocks memory entries that mention fleet profile paths** —
  the pattern `profiles/<agent>/skills` triggers `agent_config_mod` on the memory
  tool. Keep fleet-path details in the skill/repo docs; keep memory entries to the
  repo path + pointer to `fleet-agents.md`.
- **A mirrored skill/rule file must be LOADABLE, not merely present.** A pointer `SKILL.md` with no
  YAML frontmatter reads fine to a human but is invisible to a skill loader — mirror the canonical
  counterpart's `name` + `description` rather than inventing them. A rule file can also carry the
  right fields and still be malformed if the opening/closing `---` fences are missing, so check the
  FENCES, not just the field names. Run this after any mirror write, and treat a hit as a fleet-wide
  capability loss (every agent that tries to load that skill silently falls back to guessing):

  ```bash
  for f in $(find <skill-dir> \( -name 'SKILL.md' -o -name '*.mdc' \)); do
    head -c3 "$f" | grep -q -- '---' || echo "NO FRONTMATTER: $f"
  done
  ```

- **A drifted VALUE can sit in the repo copy while the WSL copy is already correct — and nothing
  surfaces it.** Mirroring is usually described as "don't let the repo lose content", but the failure
  runs both ways: a path/contract/id fixed in `~/.hermes/skills/...` during a prior session stays
  WRONG in `skills-rules-repo` until someone mirrors it, and the stale copy is the one agents on other
  boxes read. A doc-note recording the drift ("skill expects X, ours lives at Y — reconcile later")
  makes it worse, because it reads as *known and handled* while both copies quietly disagree. So when
  you correct a referenced path, endpoint, cron id or contract name, do not stop at the file you are
  editing — **grep every copy for the OLD string and require zero hits**, then push the repo copy:

  ```bash
  OLD='~/.hermes/watches/old-name.json'   # the value you just corrected
  grep -rn -- "$OLD" ~/.hermes/skills/ "$REPO" 2>/dev/null   # expect NO hits
  ```

  A hit in `.git/` (e.g. `COMMIT_EDITMSG`) is your own commit message, not a live reference — check the
  path before chasing it. And delete the drift note once resolved rather than leaving it as history;
  a "reconcile when next editing" line survives long after the reconciliation.
- **Not every skill is fleet-shared.** WSL/Pluto-only skills (e.g. `date-gated-crons`,
  `pluto-monthly-strategy-review`, `amlhive-asic-sync`) are repo skills but do NOT
  exist in Windows profiles — no propagation needed, just the repo mirror. Check
  before copying into 6 profiles.
- **Verify after copy** — `git status --short` may show no diff when the repo copy
  already matched (e.g. a prior import). `git diff --stat` to confirm before assuming
  a write happened.
- **A mirror is a MERGE, not an overwrite — the repo copy often carries content the WSL
  copy lost.** Copying `~/.hermes/skills/<cat>/<skill>/SKILL.md` over the repo file blindly
  DELETES whatever only the repo has: the frontmatter `description` (the repo version often
  keeps the full "Use when ..." trigger clause that skill discovery depends on) and entries in
  the "Linked Reference Files" block. Before committing a mirror, read the repo-only lines and
  keep the valuable ones:

  ```bash
  diff "$REPO/<cat>/<skill>/SKILL.md" ~/.hermes/skills/<cat>/<skill>/SKILL.md | grep '^<'
  ```

  Classify each repo-only line: renumbering noise and superseded text (an old value, a stale
  schedule a later fix corrected) — drop; trigger clauses, reference pointers, and anything the
  WSL copy simply never had — merge INTO the WSL copy first, then re-mirror. Verified 2026-09-16:
  a blind overwrite of `pluto-daily-maintenance` and `tapease-fleet-monitor` would have dropped
  both trigger clauses and a `daily-transaction-export.md` pointer. The same caution applies to
  a CRLF-dirty repo: clear it with `git restore .` first (see `git-working-tree-hygiene`), never
  by committing.

## Related

- `pluto-skill-extraction` — daily discovery of new reusable patterns → proposed skills
- `hermes-agent-profiles` — spawning/launching named Hermes sub-agent profiles
- Repo registry: `fleet-agents.md` (source of truth for agent → skill mapping)
- `references/fleet-import-2026-08-31.md` — record of the first 11-skill fleet import (commit c9bdc4a), category mapping, and the recurring shared-skill presence check
