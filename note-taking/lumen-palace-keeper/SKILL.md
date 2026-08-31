---
name: lumen-palace-keeper
description: Lumen's mempalace health protocol — ingestion QA, dedup, synthesis, daily learning. Use for any knowledge-base or mempalace task.
---

# Lumen Palace Keeper

## Trigger
Any mempalace task: health check, ingestion QA, dedup, synthesis, daily learning, backfill.

## Method

1. **Health check** (daily):
   - Watcher status: all input files processed, 0 pending
   - Chamber counts: flag unexpected drops/empties
   - Palace paths: `/mnt/c/Users/habib/.mempalace/palace` (note: Mercury MCP now uses `mempalace_drawers` view)
2. **Ingestion QA**:
   - Gmail ingestor (4:55 AM cron) — verify Perplexity + Claude Daily Research files exist
   - ⚠️ DETECTION RULE: cron reports 0 processed for 2+ days while emails arrive → parser format changed → re-test `extract_claude_signals()` against a live email BEFORE anything else
3. **Dedup** (only on evidence):
   - `python3 ~/.hermes/scripts/mempalace_optimize.py` (dry-run first)
   - Delete only: same chamber + title + content hash; keep earliest
   - June 7 incident reference: double-feed created 2,765 dupes — check for 1-min-apart identical feeds
4. **Synthesis** (weekly, 60-day window):
   - `pluto_cross_chamber_synthesizer.py --days 60`
   - Deliver patterns + contradictions to Sol (adversarial Sunday material)

## Operating Rules
- Preserve source/date/confidence metadata.
- Never surface uncited/stale material to customers.
- Backfill historic emails when gaps found (IMAP search without date window).

## Delivery
- Health reports: counts + pending + anomalies. Numbers, not adjectives.
- 🔴ACTION/🟡DECISION/🟢FYI framing.
