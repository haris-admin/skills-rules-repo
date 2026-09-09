---
name: pluto-honcho-signal-bridge
description: Pluto's Honcho signal bridge — pushes structured [pluto] signal cards to Honcho memory layer, tracks push state, and handles duplicate prevention. Use when managing, debugging, or running the Honcho bridge.
allowed-tools: [terminal, read_file, write_file, execute_code]
---

# Pluto Honcho Signal Bridge

> **⚠️ Alexandria mirror check (2026-09-09):** the whole-vault audit
> (`alexandria/vault/_refinery/rationalisation-2026-09-09/`) found `alexandria/vault/honcho/` is a
> **single README stub** describing a "raw archive" that was never populated — the bridge cron
> runs but writes nothing into the Alexandria mirror, and the Honcho workspace itself is
> near-empty (~220 B/peer). Open question (NEEDS HARIS): populate `vault/honcho/` (wire this
> bridge to write there) or deprecate Honcho and retire the cron.

## When to Use
- Running the Honcho bridge manually after a pipeline run
- Debugging why signals weren't pushed
- Checking pending signal files
- Understanding the dual-channel (Honcho + file) handoff to Gumby

## Architecture

The bridge pushes structured signal cards to Honcho's message stream. Gumby's message pull pipeline picks these up as scannable `[pluto]` signal cards alongside the full briefing.

**Script:** `~/.hermes/scripts/pluto_honcho_bridge.py`
**Cron:** `pluto_honcho_bridge_daily`, schedule `30 5 * * *` AEST (5:30 AM)
**Mode:** `no-agent` — script stdout delivered directly
**State:** `~/.hermes/research_outputs/.honcho_bridge_state.json`
**Deliver:** `local`

## Operations

### Manual Run
```bash
cd ~/.hermes && /home/habib/.hermes/repo/venv/bin/python3 scripts/pluto_honcho_bridge.py
```

### Check Pending Files
```bash
python3 ~/.hermes/scripts/pluto_honcho_bridge.py --list
```

### Check State
```bash
cat ~/.hermes/research_outputs/.honcho_bridge_state.json
```

### Force Push Specific Files
```bash
python3 ~/.hermes/scripts/pluto_honcho_bridge.py --force
```

## Signal Card Format
Each pushed signal is a `[pluto]` prefixed message:
```
[pluto] 🚨 AUSTRAC Tranche 2 — consultation closes June 15
Confidence: HIGH | Source: treasury.gov.au
>> For Haris: Review AML Hive compliance gaps before deadline
```

## State Tracking

`.honcho_bridge_state.json` structure:
```json
{
  "last_run": "2026-06-05T06:01:00+10:00",
  "pushed_files": ["research_2026-06-05.json", ...],
  "total_pushed": 31
}
```

Duplicate prevention: file names are tracked. Same file won't be pushed twice.

## Pitfalls

- **`last_status: ok` is misleading** — the script can exit 0 but fail to push (state tracking bug, June 3: 7 files unpushed despite "ok" status). Always verify with `--list`.
- **Windows credentials:** Honcho API key may be in `/mnt/c/Users/habib/.hermes/.env` not `~/.hermes/.env`.
- **Cron path bug (historical):** The cron initially had doubled `scripts/` in its path. Fixed — now uses just the filename. If cron stops working, check for path concatenation bugs.
- **Schedule alignment:** Bridge runs at 5:30 AM AEST — 15 minutes after Action Bridge, 40 minutes before Feedback Loop. This gives the pipeline time to complete before signals are pushed.

## Relationship to Other Skills
- **`pluto-mempalace-bridge`** — The Honcho bridge is the push half of the dual-channel handoff. The `gumby-brief-input.md` file is the pull half.
- **`fleet-intelligence`** — Full Honcho architecture docs in `references/honcho-signal-bridge.md`.
