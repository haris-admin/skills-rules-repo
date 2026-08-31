# Honcho Signal Bridge — Pluto → Gumby Push Channel

## Overview

The Honcho Signal Bridge is a **push-based** communication channel from Pluto to Gumby via Honcho messaging. It complements the existing **pull-based** channel where Gumby reads Pluto's files via WSL (`wsl cat gumby-brief-input.md`). The bridge pushes structured `[pluto]` signals directly into Honcho, where Gumby's message pull pipeline picks them up.

## Architecture

```
Pluto (Hermes, WSL)                    Gumby (OpenClaw, Windows)
  |                                         |
  |  research_outputs/*.json                |  message pull pipeline
  |  gumby-brief-input.md  ──pull──→        |  (reads Honcho messages)
  |                                         |
  └── pluto_honcho_bridge.py ──push──→ Honcho ──pull──→ Gumby brief
       pluto_action_bridge.py (patched)
```

**Two channels, different purposes:**
- **File pull (gumby-brief-input.md):** Long-form markdown briefs for Gumby's morning report
- **Honcho push ([pluto] signals):** Structured, scannable signal cards for Gumby's action queue

## Scripts

### 1. `pluto_honcho_bridge.py` (268 lines)
Main bridge script. Reads Pluto's research outputs and pushes them as `[pluto]` messages to Honcho.

**Location:** `~/.hermes/scripts/pluto_honcho_bridge.py`

**Usage:**
```bash
python3 ~/.hermes/scripts/pluto_honcho_bridge.py              # Today's outputs
python3 ~/.hermes/scripts/pluto_honcho_bridge.py --days 3     # Last 3 days
python3 ~/.hermes/scripts/pluto_honcho_bridge.py --list       # List pending only
```

**Signal types mapped to Honcho message types:**
| Source file | Honcho message type |
|------------|---------------------|
| `synthesis_*.json` | `research-synthesis` |
| `actions_*.json` | `action-extraction` |
| `gumby-action-brief-*.md` | `action-brief` |
| `gumby-brief-input.md` | `brief-input` |
| `research_*.json` | `research-finding` |

**Deduplication:** State tracked in `~/.hermes/research_outputs/.honcho_bridge_state.json`. Each file hash is recorded after push. If the state file is deleted, ALL past signals will be re-pushed.

**Signal format:**
```
[pluto] FOUND:<msg_type> DATA:<truncated preview>
```
Max signal length: 400 characters (to keep Honcho messages scannable).

### 2. `pluto_honcho_patch.py` (221 lines)
Patches `pluto_action_bridge.py` to call `push_honcho_message()` after generating actions. Idempotent — will not re-patch if the function already exists.

**Location:** `~/.hermes/scripts/pluto_honcho_patch.py`

**Usage:**
```bash
python3 ~/.hermes/scripts/pluto_honcho_patch.py
```

## Operational Flow

1. Pluto research pipeline completes → `research_*.json`, `gumby-brief-input.md`
2. Synthesis cron runs → `synthesis_*.json`
3. Action bridge runs (now patched) → `actions_*.json` + Honcho push (real-time)
4. Honcho bridge runs (separate cron or inline) → pushes remaining outputs
5. Gumby's message pull pipeline reads `[pluto]` signals from Honcho
6. Gumby annotates with USED:/SKIPPED: markers in feedback cycle

## First Operational Cycle (May 29, 2026)

**Result:** 8 of 11 signals delivered via Honcho bridge. Gumby marked all USED (100% utilization).

**Signal breakdown from Gumby's feedback (`from_gumby_2026-05-29.json`):**
- Signals #1-3: Pulled from file channel (credentials, CloudWise, prototypes)
- Signals #4-6: `[pluto]` action bridge signals (CRITICAL/HIGH actions)
- Signals #7-11: `[pluto]` FOUND signals (research findings, synthesis, actions, briefs)

## Verification

Check if signals are flowing through the bridge:
```bash
# Check bridge state (which files have been pushed)
cat ~/.hermes/research_outputs/.honcho_bridge_state.json

# Check Gumby's feedback for [pluto] signals
grep "\[pluto\]" ~/.hermes/research_outputs/feedback/from_gumby_*.json

# Count signals by channel
# File channel: signals without [pluto] prefix
# Honcho channel: signals with [pluto] prefix
```

## Pitfalls

- **Honcho credentials:** Must be set in `.env`. `honcho_conclude` silently fails without gateway restart after env changes.
- **State file integrity:** Deleting `.honcho_bridge_state.json` causes all past signals to re-push as duplicates.
- **Action bridge patch idempotency:** The patch script checks for `push_honcho_message` function before patching. Safe to re-run.
- **Signal length cap:** Messages truncated to 400 chars. Full content remains in the source files for Gumby's file pull.
- **Honcho down:** Bridge fails gracefully — signals stay in files for next run. No data loss.
