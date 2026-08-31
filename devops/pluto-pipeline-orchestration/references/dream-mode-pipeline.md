# Weekly Self-Improvement Pipeline (DREAM MODE)

**Cron:** `159702fe072c`, Saturday 12:00 AM AEST
**Trigger:** Runs after the Friday weekly review (`cc5ca5690d05`, Fri 11:05 PM AEST)
**Input:** `~/.hermes/reviews/weekly/weekly-review-{DATE}.md`
**Outputs:** `~/.hermes/reviews/weekly/improvements-{DATE}.md`, `~/.hermes/reviews/weekly/dreams-{DATE}.md`

## Overview

The DREAM MODE is Pluto's autonomous self-healing loop. It's the implementation half of the weekly review cycle: Friday review identifies problems → Saturday DREAM MODE fixes them.

Five phases run in sequence, each covering a different domain:

## Phase 1: 🧹 Stale Data Cleanup (Supabase pgvector)

**Goal:** Find and remove bad data from the podcast knowledge base.

**Connection:**
```bash
PGPASSWORD='***' PGSSLMODE=require psql \
  -h aws-1-ap-southeast-2.pooler.supabase.com \
  -p 6543 \
  -U postgres.vyqagemgwxfscppkfswq \
  -d postgres
```

**Checks (5 dimensions):**
1. Episodes where `transcript_text LIKE '%YouTube is blocking%'` → IP-blocked garbage, safe to delete
2. Duplicate episodes: `SELECT podcast_id, youtube_id, count(*) ... HAVING count(*) > 1`
3. Episodes with `length(transcript_text) < 100` → failed downloads stored as error text
4. Episodes older than 90 days with `au_relevance_score IS NULL` → unrated backlog
5. Orphaned chunks: `SELECT ... FROM podcast_kb.chunks c LEFT JOIN podcast_kb.episodes e ON c.episode_id = e.id WHERE e.id IS NULL`

**Rules:**
- DELETE items that are safe to re-ingest (IP-blocked garbage, short transcripts)
- Report counts only for items needing human review (duplicates, orphans)
- Always use single-quoted password to avoid `!` shell expansion

**First run (June 13, 2026):** 0 issues found. 214 episodes, 501 chunks, all clean.

## Phase 2: 🧠 MemPalace Update

**Goal:** Verify the knowledge base and archive system are healthy.

**Checks:**
```bash
# ChromaDB health
python3 -c "
import chromadb
c = chromadb.PersistentClient(path='/mnt/c/Users/habib/.mempalace/palace')
cols = sorted(c.list_collections(), key=lambda x: x.name)
print(f'Total collections: {len(cols)}')
[print(f'  {x.name}: {x.count()} docs') for x in cols]
"

# Cleanup state
cat ~/.hermes/research_outputs/.cleanup_state.json

# Files older than 7 days
find ~/.hermes/research_outputs/ -maxdepth 1 -type f -mtime +7 | wc -l
```

**Rules:**
- If cleanup cron (`0fc5019948be`) has been working, there should be 0 files older than 7 days
- Check archive directory `~/.hermes/archive/research/` for archived file count
- Consolidate daily synthesis files into a weekly summary if gaps exist

## Phase 3: 🔧 Skill Rewriting

**Goal:** Find and fix stale, outdated, or incorrect skill documentation.

**Checks:**
1. Load ALL skills via `skills_list`
2. For each Pluto-specific skill, `skill_view` and audit for:
   - Outdated repo names (e.g., `ideas-*-au` → `ideas-*`)
   - Old cron schedules that changed
   - Broken commands or dead file paths
   - Missing pitfalls discovered during the week
3. Search for known stale patterns: `grep -r "5:20 PM" ~/.hermes/skills/`, `grep -r "ideas-.*-au" ~/.hermes/skills/`
4. Patch with `skill_manage(action='patch')`
5. Flag skills needing full rewrites (too many issues to patch)

**First run (June 13, 2026):** 1 stale reference found in `pluto-portfolio-ideation/references/honcho-bridge-limitations.md` — cron time "5:20 PM AEST" → "6:00 AM AEST". All 99 other skills current.

## Phase 4: 🔗 Rewire Connections

**Goal:** Fix broken cron jobs, stale references, and script vulnerabilities.

**Checks from `~/.hermes/cron/jobs.json`:**
1. **Error crons** — classify each: BrokenPipe → needs wrapper, timeout → increase limit, exit 1 false-positive → fix script
2. **Never-executed crons** — `last_run_at: null` + `enabled: true` = scheduler bug
3. **Paused crons** — check reason, determine if re-enable is safe
4. **Name/schedule mismatches** — display name doesn't match actual cron time

**BrokenPipeError wrapper pattern** (apply to any `no_agent: true` script missing it):
```python
# For scripts with main():
if __name__ == '__main__':
    try:
        main()
    except BrokenPipeError:
        sys.exit(0)

# For scripts with top-level execution:
try:
    # ... all execution ...
except BrokenPipeError:
    sys.exit(0)
```

**First run (June 13, 2026):** Applied wrapper to `skill_extractor.py` and `pluto_feedback_processor.py`. 4 never-executed crons flagged. 1 paused cron needs human decision.

## Phase 5: 🌙 Dreaming — Speculative Improvements

**Goal:** Think creatively about what COULD be better, based on the week's failures.

**Process:**
1. Read the Friday review's "What Didn't Work" section
2. For each failure, brainstorm 2-3 alternative approaches
3. Propose at least ONE new capability Pluto doesn't have yet
4. Write proposals to `~/.hermes/reviews/weekly/dreams-{DATE}.md`

**Dream proposal format:**
```
## Dream #N: [Title]
**What:** One-line description
**Why:** Evidence from this week's data
**How:** Implementation approach (concrete steps)
**Cost:** Low / Medium / High (with justification)
```

**First run (June 13, 2026):** 4 proposals:
1. YouTube proxy rotation for podcast ingestion (Medium)
2. Cron scheduler health monitor (Low)
3. Automated skill creation from long-pending proposals (Low)
4. DeepSeek alternative provider for high-context crons (Medium)

## Output Files

| File | Content |
|------|---------|
| `improvements-{DATE}.md` | Full report: findings, fixes applied, proposals, human review items |
| `dreams-{DATE}.md` | Standalone dream proposals (short format, actionable) |

## Relationship to Other Crons

```
Daily Extraction (2d33c8f9a89c, 11:00 AM)
  → skill-proposals_YYYY-MM-DD.md
  → Patterns identified daily
        ↓
Friday Review (cc5ca5690d05, Fri 11:05 PM)
  → weekly-review-YYYY-MM-DD.md
  → Aggregates extraction reports + pipeline health
        ↓
Saturday DREAM MODE (159702fe072c, Sat 12:00 AM)  ← THIS MODE
  → improvements-YYYY-MM-DD.md + dreams-YYYY-MM-DD.md
  → Implements fixes, creates skills, proposes improvements
```

If any link in this chain breaks, skill debt and operational debt accumulate indefinitely.
