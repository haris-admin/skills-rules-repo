# Mercury Fleet Skill Import — 31 Aug 2026 (11 skills)

First full import of the 6 Windows Mercury agent profile skills into
skills-rules-repo. Commit `c9bdc4a` on `main`. This is the reference recipe and
record for the class of work; the umbrella SKILL.md has the generic workflow.

## What was imported

**6 agent-protocol skills** (one per Mercury agent; each defines that agent's
operating method):

| Agent | Skill | Repo category |
|-------|-------|---------------|
| Aurora | aurora-content-engine | research |
| Caduceus | caduceus-compliance-watch | compliance |
| Lumen | lumen-palace-keeper | note-taking |
| Sol | sol-strategy-engine | research |
| Vigil | vigil-watch-protocol | devops |
| Vulcan | vulcan-build-protocol | software-development |

**5 shared tool skills** (identical copies exist in all 6 profiles; canonical
source used: aurora profile):

| Skill | Repo category |
|-------|---------------|
| llm-wiki | research |
| codebase-inspection | software-development |
| node-inspect-debugger | software-development |
| python-debugpy | software-development |
| simplify-code | software-development |

Plus `fleet-agents.md` (agent → skill registry) at repo root.

## How it was done

1. Enumerated each profile's skills:
   `find /mnt/c/Users/habib/AppData/Local/hermes/profiles/<agent>/skills -name SKILL.md`
2. Checked the repo for each name (`find . -maxdepth 3 -type d -name "<skill>"`)
   to find missing ones. Note: `skills/` flat dir and `.archive/` hold older
   copies (e.g. `nano-pdf`, `claude-code`, `opencode`, `sketch`) — those were
   NOT re-imported; only genuinely missing active skills were.
3. Copied SKILL.md + any `references/ scripts/ templates/` subdirs into the
   repo's category dir. Category mapping followed the repo's existing convention
   (devops/, research/, compliance/, note-taking/, software-development/).
4. Verified: `git status --short`, then commit + push to `main`.

## Profile-specific skills NOT in repo (already archived elsewhere)

`apple/apple-notes|apple-reminders|findmy|imessage` and `sketch` live in the
profiles but are platform-specific (macOS/Apple); they stayed in
`.archive/`-style locations rather than active categories. If Haris wants the
full Apple suite versioned, they need a dedicated category.

## Recurring check (cheap, run when touching fleet skills)

```bash
for s in llm-wiki codebase-inspection node-inspect-debugger python-debugpy simplify-code; do
  echo "== $s =="; find /mnt/c/Users/habib/AppData/Local/hermes/profiles/*/skills -type d -name "$s" | wc -l
done
# 6 = present in all profiles; <6 = some profile missing the shared skill
```
