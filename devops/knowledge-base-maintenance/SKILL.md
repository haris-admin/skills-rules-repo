---
name: knowledge-base-maintenance
description: "Use when deduping or auditing a vector knowledge base."
version: 1.0.0
author: Pluto
tags: [chromadb, knowledge-base, dedup, freshness, vector-db, maintenance]
---

# Knowledge-Base (ChromaDB) Maintenance

Dedup, freshness auditing, and safe cleanup for vector knowledge bases (the
mempalace ChromaDB at `/mnt/c/Users/habib/.mempalace/palace` and similar).
Use when asked to "clean up / optimize / restructure" the knowledge base, remove
stale or duplicate entries, or check whether it is being updated regularly.

## Scope — two fleet knowledge bases

| KB | What | Skill |
|---|---|---|
| **mempalace ChromaDB** (`/mnt/c/Users/habib/.mempalace/palace`) | vector store, per-agent retrieval | **this skill** |
| **Alexandria markdown vault** (`github.com/haris-admin/alexandria`) | shared, versioned, Obsidian-compatible; agents push 4+×/day | **`alexandria-refinery`** |

The **safe-dedup rule** and the **freshness-sampling pitfall** below apply to both. The Alexandria
side adds a 4-tier lifecycle, a frontmatter contract, and eviction of cron exhaust to
`alexandria-ops` — see the `alexandria-refinery` skill and the `knowledge-vault-write-contract`
rule. When asked to "clean up the knowledge base", check which one is meant.

## Safe dedup rule (verified Aug 2026)

Only delete where **(chamber, title, content-hash) is EXACTLY identical** and
there are ≥2 copies. Keep the earliest-inserted id, delete the rest. **Never
delete on title alone** — a chamber full of generic titles (`finding`, `signals
extracted`, `perplexity briefing signal`) is a *labeling* weakness, not proof
of duplication.

Before executing on a large deletion, verify a sample dup pair has identical
`documents` (not just metadata) — confirmed safe before deleting 85% of a
chamber in Aug 2026.

Script: `~/.hermes/scripts/mempalace_optimize.py`
- `--dry-run` (default) prints what would be removed; `--execute` deletes
- Writes `research_outputs/mempalace_optimization_YYYY-MM-DD.md`

## PITFALL — freshness sampling order (critical)

`collection.get(limit=N)` returns docs in **insertion order (oldest first)**.
Sampling the first N docs to answer "is this chamber stale?" is WRONG — it
shows only old dates even when the chamber is actively fed. (First audit pass
concluded "palace stopped in June"; the real histogram showed July/Aug entries
in every chamber.)

**Correct freshness check:** pull ALL metadatas
(`coll.get(include=['metadatas'])` with `limit=count`) and histogram the `date`
field by month — or sample the TAIL (offset near count-N), not the head.

## Audit recipe

```python
import chromadb
from collections import Counter
c = chromadb.PersistentClient(path='/mnt/c/Users/habib/.mempalace/palace')

# 1. Collection overview
cols = sorted(c.list_collections(), key=lambda x: x.count(), reverse=True)
for x in cols:
    print(f'{x.name}: {x.count()}')

# 2. Freshness (ALL metadatas, histogram by month — not a head sample)
for colname in ['regulatory-ai', 'fintech-aml']:
    coll = c.get_collection(colname)
    data = coll.get(limit=coll.count(), include=['metadatas'])
    months = Counter(str((m or {}).get('date', '?'))[:7] for m in data['metadatas'])
    print(colname, dict(sorted(months.items())))

# 3. Duplicate-title groups
for colname in [...]:
    coll = c.get_collection(colname)
    data = coll.get(limit=coll.count(), include=['metadatas'])
    titles = Counter(str((m or {}).get('title', '')).strip().lower() for m in data['metadatas'])
    dups = {t: cnt for t, cnt in titles.items() if cnt > 1}
    print(colname, dups)
```

## Interpreting results

- **Freshness:** dated content lagging >30 days while the feed cron claims to
  run → check the feeder/watcher actually stored items (feed footer says
  "Fed N new item(s)", not just cron `last_status: ok`).
- **Duplicate root causes:** a feeder/watcher retry double-ingesting the same
  batch (observed: identical docs 1 min apart from a June 7 double-feed).
- **Generic titles are a separate problem:** they reduce retrievability but
  aren't duplicates; fix labeling upstream, don't delete on title.

## Blind-spot audit (chamber-level) — from Lumen's 2026-08-22 audit

Beyond dedup/freshness, a full blind-spot audit answers "what do we NOT know?"
The proven recipe (Lumen's audit of `mempalace_drawers`, 2,209 docs → 5-section
report in 5m34s) adds four checks to the audit:

1. **Chamber census with staleness** — for EVERY chamber: count, date range,
   last-doc date, days-stale. A chamber with docs but nothing since >60-70 days
   is frozen (observed: digital-identity 89d, sovereign-ai 70d, aie-podcast 75d).
   Report as a table — this drives the "thaw or archive" decision.
2. **Contradiction scan** — same finding family, different numbers, no
   reconciliation note (observed: "83% of CIOs cloud repatriation" vs "86%",
   both high confidence). Search for the stat, group by finding family, flag
   divergent values. Also catch **dating contamination** (docs dated Aug 19
   carrying "07 Jun 2026" topics — backfill re-dating).
3. **Provenance / URL check** — count empty `url` metadata. 88% empty in the
   2026-08 audit = "never surface uncited material" violated at scale. Also
   check source-tagging consistency (0 docs with source=perplexity but 37
   content mentions; 9 source=claude_daily_research vs 256 claude-tagged).
4. **Confidence distribution anomaly** — high 1258 / medium 946 / low 5. A
   healthy KB flags uncertainty; ~0.2% low-confidence means the pipeline never
   records doubt. Flag as a pipeline-hygiene issue, not a content issue.

Also worth reporting: placeholder records ("Untitled" topics, "Finding"-titled
stubs that contain raw prompts, truncated titles), duplicate-cluster signatures
(content-hash pairs from double-feed ingestion runs), and per-chamber source
mix (a catch-all chamber like regulatory-ai at 614 docs can mask thinness
elsewhere). Method artifacts from the proven run: `lumen_audit_stage1-3.py`
pattern — stage 1 schema/peek, stage 2 full dump + distributions, stage 3
word-boundary keyword coverage (use `\bterm\b`, not substring — "asic" matches
"basic"/"physical").

## Known pitfalls

- Two ChromaDB locations exist: real palace at
  `/mnt/c/Users/habib/.mempalace/palace` (post-2026-08-22 migration it is a
  SINGLE `mempalace_drawers` collection with a `chamber` metadata field — the
  old 12-collection layout is legacy) vs empty WSL-side
  `~/.hermes/mempalace/chromadb/`. Always query the Windows path. When the
  palace was rebuilt by a cross-version writer (Mercury MCP, 22 Aug 2026),
  `collection.get()` can fail with a metadata-segment decode error from the
  WSL reader — see `hermes-agent-profiles` SKILL.md pitfall #7 for the
  corruption + repair path.
- `pluto-mempalace-bridge` / `pluto-autonomous-research` skills hold the
  feed-side operational detail (user-owned as of Aug 2026).
- Python stdout in cron/background: use `python3 -u` to avoid buffered silence.
