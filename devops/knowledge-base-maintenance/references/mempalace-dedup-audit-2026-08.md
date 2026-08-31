# Mempalace Dedup Audit — 16 Aug 2026

## Full-palace duplicate analysis

2,765 of 4,779 docs (62%) were TRUE duplicates (same chamber + same title +
same content, fed twice).

| Chamber | Dup docs | Notes |
|---|---|---|
| regulatory-ai | 2,472 | bulk titled `finding`; June 7 double-feed (identical 135-char content, ids 1 min apart) |
| startup-vc | 91 | 23x `perplexity briefing signal` |
| fintech-aml | 87 | 50x `finding`, 9x `perplexity briefing signal` |
| pluto_research | 43 | TAM/SAM/MVP/PRD template docs fed 3x |
| aie-podcast | 8 | podcast episode double-feeds |
| cloud-infra, payments-npp, sovereign-ai, critical-infra | smaller | |

## Result after execute

4,779 → 2,014 docs (−58%). `regulatory-ai` 2920 → 448 unique. All 12 chambers
healthy; 0 generic-titled dups remaining in regulatory-ai.

## Verification before delete

A `finding` dup pair checked via `coll.get(include=['documents'])` had
IDENTICAL document content — not just identical metadata — before deleting
85% of a chamber. Always verify content equality, not metadata equality.

## Sampling-order failure (the cautionary tale)

First freshness audit sampled `get(limit=60)` per chamber → all June dates →
wrong conclusion "palace stopped being fed in June". Full-metadata histogram
showed July/Aug entries in every chamber. ChromaDB `get()` returns insertion
order (oldest first); always pull all metadatas and histogram dates.

## Prevention

The double-feed class means a watcher/refresh retry can silently duplicate an
entire batch. After any manual or bulk feed, spot-check the target chamber for
duplicate (title, content) pairs — the feeder's "Fed N new item(s)" count
counts successful inserts, not unique content.
