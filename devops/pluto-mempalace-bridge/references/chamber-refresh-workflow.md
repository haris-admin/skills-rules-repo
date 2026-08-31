# Chamber Refresh Workflow (v1.0 — June 12, 2026)

## Overview

The chamber refresh system (`pluto_chamber_refresh.py`) is the cross-source knowledge bridge that feeds ALL new content from the morning pipeline into ChromaDB chambers, then triggers cross-chamber synthesis.

## Flow

```
Gmail/Perplexity (4:55 AM)
    ↓ files in mempalace-inputs/
Podcast transcripts (Supabase, last 24h)
    ↓ via SQL query
Research findings (research_YYYY-MM-DD.json)
    ↓
pluto_chamber_refresh.py (5:25 AM)
    ↓ JSON conversion → feeder JSON format
pluto_mempalace_feeder.py --chamber <auto-routed>
    ↓
ChromaDB chambers (24 collections)
    ↓
Pluto Cross-Chamber Synthesis → enriched briefing
```

## What It Feeds

### 1. Gmail/Perplexity Briefings
- Source: `~/.hermes/mempalace-inputs/gmail-briefing-*.md`
- Dedup: checks both state file and existing files on disk
- Chamber routing: content keyword matching (ai+regulation→regulatory-ai, payment→payments-npp, startup→startup-vc)

### 2. Podcast Transcripts
- Source: Supabase `podcast_kb.episodes` (last 24h, filtered by `transcript_text` not null)
- Dedup: tracks ingested episode IDs in state file
- Chamber routing: show name matching (a16z→startup-vc, Lenny's→startup-vc, AI Engineer→regulatory-ai, Prof G→regulatory-ai)

### 3. Research Findings
- Source: `research_outputs/research_YYYY-MM-DD.json`
- Chamber routing: portfolio_hit mapping (AML Hive→fintech-aml, PayLicence→payments-npp, ExitLens→startup-vc, FinAI File→regulatory-ai)

## Cron
- **Job ID:** `0959371eec17`
- **Schedule:** 25 5 * * * (5:25 AM AEST daily)
- **Type:** no_agent script
- **Script:** `pluto_chamber_refresh.py`
- **State file:** `~/.hermes/research_outputs/.chamber_refresh_state.json`

## Key Files
- `~/.hermes/scripts/pluto_chamber_refresh.py` — main script
- `~/.hermes/scripts/pluto_mempalace_feeder.py` — feeder called by refresh script
- `~/.hermes/research_outputs/.chamber_refresh_state.json` — dedup state

## Pitfalls
- Feeder expects JSON, not markdown. Temp JSON files are built in `mempalace-inputs/` and cleaned up after each feed.
- Podcast routing by show name only — if a new show is added, update the routing conditions in `feed_podcast_transcripts()`.
- The script skips research findings without a matching portfolio_hit.
