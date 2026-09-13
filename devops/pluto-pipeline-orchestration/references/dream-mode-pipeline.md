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

## Run History

**Week 5 (July 18, 2026) — Best Implementation Cycle Yet:**
- **Phase 1:** Supabase pristine — 481 episodes, 501 chunks, 0 stale records. 46 legacy episodes >90 days without AU scores (carried from W26). **Fixed 3 instances of `created_at` → `published_date` column name bug** in supabase-stale-data-queries.md (this bug burned every DREAM MODE cycle since creation — now fixed permanently with a Column Name Pitfalls section).
- **Phase 2:** MemPalace healthy — 27 collections, 3,165 docs (+1,490 vs June W26). Nightly cleanup cron active (469 archived). ChromaDB growing steadily.
- **Phase 3:** No skills patched — remarkably, all 106 skills are current. `pluto-weekly-review` was already patched with W28 findings during the Friday review.
- **Phase 4:** **3 fixes applied** (highest single-cycle implementation): (1) Daily Learning cron prompt patched — now saves to `research_outputs/daily-learning-YYYY-MM-DD.md` to close 100% false negative. (2) `gmail_health_check.py` created — pre-flight IMAP login test, P0 alert to mempalace on failure, BrokenPipeError-safe. (3) `competitor_intel.py --debug` flag added for diagnosing 43% empty-output rate. Also: guardrail-scan investigated and confirmed healthy — Friday review claim was false (verified against 8 consecutive sync runs all showing "already current"). Two transient errors (Hermes Update + Podcast Ingestion — both Gateway shutdown).
- **Phase 5:** 5 dream proposals: Pipeline Health in Briefing (3rd week stalled — now CRITICAL at 5 weeks of Gmail darkness), Cron Output Path Validator (NEW), Intelligence Health Scorecard, Auto-Register Gmail Health Cron (NEW), Batch AU Re-Scorer (3rd week stalled).
- **Key result:** Implementation rate hit **60%** (3/5 dreams implemented) — best ever. Dream pipeline improving: W23=0% → W24=25% → W25=37.5% → W28=60%. The key shift was prioritizing LOW-cost, self-contained fixes over multi-step orchestration dreams. Gmail Health Monitor script created but not yet registered as cron (Dream #4 — 5 min task).
- **Skills updated:** `pluto-weekly-review` (guardrail-scan verification pitfall, Supabase column name pitfall), `pluto-pipeline-orchestration/references/supabase-stale-data-queries.md` (3x `created_at`→`published_date` fixes, Column Name Pitfalls section added).

**Week 3 (June 20, 2026):**
- **Phase 1:** Supabase pristine — 275 episodes, 501 chunks, 0 stale records. 34 legacy episodes with zero AU relevance scores (valid transcripts, pre-scoring ingestions) — deferred to Dream Proposal #1 for batch re-scoring.
- **Phase 2:** MemPalace healthy — 27 collections (3 new emergent: `market-signals`, `quantum-computing`, `space-tech`), 1,675+ docs. Nightly cleanup cron confirmed working (194 archived). 3 state files >7 days old (benign — actively referenced).
- **Phase 3:** 2 skills patched (pipeline-orchestration, vercel-monitoring). No skills flagged for full rewrite.
- **Phase 4:** 3 scripts fixed: `vercel_monitor.py` (BLOCKED verification), `pluto_performance_tracker.py` (tool_warnings field), `git_sync.py` (skip dead repos). All 31 crons verified healthy. 2 skills patched.
- **Phase 5:** 6 dream proposals: AU re-scorer (LOW), podcast chunking lite (MEDIUM), chamber auto-documenter (LOW), insight extractor auth fix (LOW), Sunday engagement prompt (LOW), cron output auto-prune (LOW).
- **Key result:** First zero-error week continues — all 31 crons `last_status: ok`.

**(Week 2 — header missing in source):**
- **Phase 1:** Supabase pristine — 214 episodes, 501 chunks, 0 stale records (clean 2 weeks running)
- **Phase 2:** MemPalace healthy — 24 collections, 1,023+ docs, cleanup cron working (112 archived)
- **Phase 3:** 1 skill flagged for full rewrite (`pluto-autonomous-research` pipeline table pre-June-12). No patches needed.
- **Phase 4:** 2 timeout fixes applied (podcast crons 120s → 300s). All script paths valid. No stale memory.
- **Phase 5:** 6 dream proposals (provider migration, scheduler monitor, proxy rotation, credential monitor, auto-skill-creation, competitor confidence tiers)

**Week 1 (June 13, 2026 — inaugural run):**
- **Phase 1:** Supabase clean (0 IP-blocked, 0 duplicates, 0 orphans, 214 episodes)
- **Phase 2:** MemPalace healthy (24 collections, cleanup cron working, 112 files archived)
- **Phase 3:** 1 stale reference found (honcho-bridge-limitations.md: "5:20 PM" → "6:00 AM")
- **Phase 4:** 2 BrokenPipeError wrappers added (skill_extractor.py, pluto_feedback_processor.py)
- **Phase 5:** 4 dream proposals (proxy rotation, scheduler monitor, auto-skill-creation, provider migration)
