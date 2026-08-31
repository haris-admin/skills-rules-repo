# Operational Findings & Pending Skills Tracker

> Updated: 2026-06-03. Reference for daily skill extraction runs.

## Persistent Operational Issues

### 1. Honcho Bridge Cron Misconfiguration
- **First observed:** May 29, 2026
- **Cycles failed:** 3 (May 29, 30, 31). No runs attempted since.
- **Root cause:** Cron command doubles the `scripts/` directory path. The `no_agent` script mode prepends the scripts dir, but the command already contains `scripts/pluto_honcho_bridge.py`, producing `scripts/scripts/pluto_honcho_bridge.py`.
- **Error:** "Script not found: /home/habib/.hermes/scripts/python3 /home/habib/.hermes/scripts/pluto_honcho_bridge.py"
- **Fix needed:** Change cron command to just `python3 /home/habib/.hermes/scripts/pluto_honcho_bridge.py` or remove the `scripts/` prefix from the command field.
- **Impact:** No Pluto→Honcho signals pushed since May 29. Bridge skill (`pluto-honcho-signal-bridge`) cannot qualify beyond 2 cycles until fixed.

### 2. Voice Overview False Negatives — RESOLVED
- **First observed:** May 31, 2026
- **Resolution:** June 1 run at 22:15 UTC produced output successfully. Script now correctly finds `research_DATE.json` format.
- **Status:** ✅ No longer an active issue.

### 3. Honcho Push Timeout in Action Bridge
- **First observed:** May 31, 2026
- **Error:** "HonchoPush to external tracking failed (read timeout)" in action bridge output
- **Root cause:** The Honcho API (`api.honcho.dev`) may have intermittent connectivity from WSL.
- **Mitigation:** The action bridge has a retry loop (4 attempts with exponential backoff). Actions are saved locally and will be picked up on the next push cycle. Non-blocking.
- **Status:** Still occurs occasionally. Cosmetic — doesn't block the pipeline.

### 4. Pipeline Schedule Shift
- **Observed:** June 3, 2026
- **Finding:** Pipeline now fires at ~05:00 UTC (up from previous ~19:00 UTC). This means the 11:00 UTC skill extractor sees today's pipeline results, not yesterday's.
- **Impact:** Extraction reports should check actual log timestamps rather than assuming the pipeline hasn't run yet.

## Pending Skills (all qualified, none created)

| # | Skill Name | First Qualified | Cycles | Why Not Created |
|---|-----------|----------------|--------|-----------------|
| 1 | `pluto-intelligence-pipeline` | May 29 | 6 | Awaiting user action |
| 2 | `pluto-cross-chamber-synthesis` | May 29 | 6 | Awaiting user action |
| 3 | `pluto-gumby-feedback-loop` | May 29 | 6 | Awaiting user action |
| 4 | `pluto-pipeline-orchestration` | May 29 | 6 | Awaiting user action |
| 5 | `pluto-honcho-signal-bridge` | May 30 | 2 | Cron misconfigured — bridge hasn't actually run |
| 6 | `pluto-weekly-research-digest` | June 1 | 2 | Awaiting user action; next run Sunday June 7 |

## Watched Patterns (not yet qualifying)

| Pattern | First Seen | Occurrences | Status |
|---------|-----------|-------------|--------|
| Voice Note → MemPalace Pipeline | June 3 | 0 in production | Scripts created (`voice_poller.py`, `whisper_transcribe.py`). Not yet cron-installed. Watch for ≥2 production runs. |

## Extraction Run History

| Date | Patterns Found | Qualifying | New Skills Created | Notes |
|------|---------------|-----------|-------------------|-------|
| May 29 | 4 | 4 | 0 (first extraction) | All 4 pipeline patterns emerged |
| May 30 | 1 | 0 | 0 | Honcho bridge emerged (1 cycle) |
| May 31 | 0 | 0 | 0 | Quietest day — only watcher runs |
| June 1 | 1 | 1 | 0 | Weekly digest qualified (2 cycles) |
| June 2 | 0 | 0 | 1 | `pluto-skill-extraction` skill created |
| June 3 | 1 | 0 | 0 | Voice pipeline identified (not yet qualifying). Pipeline schedule shifted to 05:00 UTC. Local whisper model working. Agentic AI & Security topic researched.
