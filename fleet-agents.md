# Mercury Fleet — Windows Agent Skills (canonical registry)

The **Mercury fleet** runs as six Windows-native Hermes profiles on
`/mnt/c/Users/habib/AppData/Local/hermes/profiles/<agent>/`. Each profile carries
the shared Hermes skill library **plus one agent-protocol skill** that defines that
agent's operating method. These agent-protocol skills are checked in here so the
fleet's rules are version-controlled and deployable.

| Agent | Role | Protocol skill (this repo) | Category |
|-------|------|-----------------------------|----------|
| **Aurora** | Content & authority engine | `research/aurora-content-engine` | research |
| **Caduceus** | Compliance & payments watch | `compliance/caduceus-compliance-watch` | compliance |
| **Lumen** | Mempalace/knowledge-base health | `note-taking/lumen-palace-keeper` | note-taking |
| **Sol** | Strategy synthesis & gating | `research/sol-strategy-engine` | research |
| **Vigil** | Monitoring & escalation | `devops/vigil-watch-protocol` | devops |
| **Vulcan** | Build protocol (TDD/Codex) | `software-development/vulcan-build-protocol` | software-development |

## Sync rule

- Any change to a shared or agent-protocol skill MUST be mirrored here
  (`/mnt/c/Code/github/haris-admin/skills-rules-repo`) and pushed to
  `origin/main` (remote: `https://github.com/haris-admin/skills-rules-repo`).
- When a skill is modified, check whether other agents use it and update their
  copies in the profiles too (the profile skill dirs are the deployed targets).
- Canonical source for shared tool skills (identical across profiles) is the
  `aurora` profile copy; propagate changes to all 6 profile skill dirs.

## Shared tool skills (identical across all 6 profiles)

Checked in from the fleet (canonical: aurora profile):

| Skill | Category |
|-------|----------|
| `llm-wiki` | research |
| `codebase-inspection` | software-development |
| `node-inspect-debugger` | software-development |
| `python-debugpy` | software-development |
| `simplify-code` | software-development |

Profile launch (Windows PowerShell, from hermes-agent dir):
`powershell .\venv\Scripts\python.exe hermes -p <agent> chat -q`
