# Local Build Queue Structure

The local build queue lives at `~/.hermes/mempalace-inputs/.build-queue/` and provides a filesystem-based project registry that doesn't depend on cron jobs or external systems.

## Directory Layout

```
.build-queue/
├── BUILD_QUEUE.md     ← Registry with all projects, scores, status
├── active/            ← Currently building (max 2 at once)
├── staged/            ← Ready to build, next in line
├── completed/         ← Shipped and live
└── archived/          ← Frozen ideas (revisit later)
```

## BUILD_QUEUE.md Format

```markdown
# Pluto Build Queue — Active Registry
**Last Updated:** YYYY-MM-DD HH:MM AEST
**Total Slots:** 5 active / 10 staged

## 🔴 ACTIVE (In Progress)
| # | Project | Score | Domain | Status |
|---|---------|-------|--------|--------|

## 🟡 STAGED (Ready to Build)
## ⚪ QUEUED (New Suggestions)
## ❄️ FREEZE (Not now — revisit Q3 2026)

## ⚡ Rules of the Queue
1. Max 2 active builds at once
2. Content-first for new entries — $250 MVP, validate before SaaS
3. Portfolio synergy wins
4. Timing window is everything
```

## When to Use

- When Haris asks "what's in the build queue?" or "what are we working on?"
- When moving a project from ideation → staged → active → completed
- When presenting new ideas from a research sweep — add them to QUEUED section
- When freezing an idea that's not right for now — move to FREEZE section

## Relationship to Other Systems

- **MemPalace** stores research signals → ideation mines those signals → queue holds the resulting projects
- **Cron jobs** can be created FROM queue items (e.g., a cron job that builds TokenPilot Phase 1)
- **GitLab repos** are the canonical code location for staged/active items
- This queue is the **human-readable registry** — not an execution engine. It exists so Haris and Pluto can quickly align on priorities.
