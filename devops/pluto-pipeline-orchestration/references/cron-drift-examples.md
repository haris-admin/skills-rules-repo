# Cron Documentation Drift — Examples (June 9, 2026)

Examples of documentation drift caught by cross-referencing `hermes cron list` against
MEMORY.md and pluto-pipeline-orchestration SKILL.md.

## Ghost Cron (in docs, not in reality)

**"5:03 CompIntel"** — Listed in MEMORY.md cron chain but no such cron exists.
Competitor Intel actually runs at 5:07 AM (`1a13a2d49682`). The "5:03" was likely a
planned time that was changed to 5:07 before creation, but the memory was never updated.

## Wrong Times

| Documented | Actual | Cron |
|---|---|---|
| 6:15 AM Moonshots Learning | **8:15 PM** (`15 20 * * *`) | `0fb6bf47f704` |
| briefing_improver.py at 5:05 AM | **5:20 AM** (`20 5 * * *`) | `7cc81d64613a` |

## Missing Crons (in reality, not in docs)

| Cron | Schedule | Missing From |
|---|---|---|
| Podcast Chunking `79c8ad5b9465` | 2:00 AM daily | Both MEMORY.md and pipeline SKILL.md |
| Competitor Intel `1a13a2d49682` | 5:07 AM daily | Pipeline SKILL.md (was in memory as "5:03") |

## Cross-Reference Technique

```bash
# 1. Get ground truth
hermes cron list > /tmp/crons-actual.txt

# 2. Extract documented schedule from memory
grep -o 'Crons.*' ~/.hermes/memories/MEMORY.md

# 3. For each documented time, verify the cron exists with that schedule
# 4. For each actual cron, verify it appears in the documented chain
# 5. Patch everything that doesn't match
```

**Rule:** After ANY `hermes cron create`, `hermes cron delete`, or `hermes cron update`,
immediately update both this skill AND MEMORY.md with the new schedule.
