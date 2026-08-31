# Skill Extraction — Key Data Sources

## Primary: cron/jobs.json
**Path:** `~/.hermes/cron/jobs.json`
**Format:** JSON object with `jobs` array and `updated_at` timestamp.

Each job has these fields useful for extraction:
- `id` — cron job ID (stable identifier)
- `name` — human-readable name
- `last_run_at` — ISO 8601 timestamp (null if never run)
- `last_status` — "ok", "error", or null (never run)
- `last_error` — error message if any
- `schedule.expr` — cron expression
- `repeat.completed` — total run count
- `next_run_at` — next scheduled run
- `enabled` — boolean
- `no_agent` — true if script-based (no LLM invocation)

**Key queries:**
- Jobs that NEVER fired: `last_run_at` is null AND `enabled` is true AND `repeat.completed` is 0
- Jobs that errored: `last_status` is "error"
- Jobs with schedule drift: `next_run_at` far in future or past

## Secondary: tasks/ Manifests
**Path:** `~/.hermes/tasks/PIPELINE_NAME/DATE-HHMM.json`
**Format:** JSON with task_id, pipeline, mode, timestamp, status, result_path.

Even if a cron never fired, the task manifest confirms it was queued. Useful for distinguishing "queued but scheduler dropped" from "never queued at all."

## Secondary: sessions/sessions.json
**Path:** `~/.hermes/sessions/sessions.json`
**Format:** JSON object keyed by session_key. Each has:
- `session_id` — unique session identifier
- `updated_at` — last activity timestamp
- `platform` — telegram, cron, etc.
- `last_prompt_tokens` — can indicate session depth

## Secondary: reviews/ Directory
**Path:** `~/.hermes/reviews/`
Key files:
- `weekly/weekly-review-*.md` — Friday weekly self-assessment
- `weekly/improvements-*.md` — Saturday DREAM MODE 5-phase report
- `weekly/dreams-*.md` — speculative improvement proposals
- `vercel/vercel-report-*.json` — deployment health checks

The improvements report is especially rich: it documents bugs found, skills created, crons fixed, and data cleaned. Always check it for patterns that emerged during maintenance sessions.

## Fallback: agent.log
**Path:** `~/.hermes/logs/agent.log`
Use only when filesystem sources are insufficient. The log format varies by session type (cron vs interactive). Prefer `grep` by session_id (from cron/jobs.json `id` field) rather than by date or job name.

**CRITICAL LIMITATION:** Morning pipeline agent sessions (`b0de180cec84`, `ddceef1f9e5b`, `38c1aa80a5b8`, `59f18c4d557c`, `67319a9b2606`, `ee4e48300826`) are `no_agent: false` agent sessions but produce ZERO entries in agent.log. Only watcher (`5678a363ce3b`) and extractor (`2d33c8f9a89c`) sessions reliably appear. `cron/jobs.json` is the sole authoritative source for pipeline session confirmation.

**Timezone trap:** Pipeline runs at 05:00 AEST = 19:00 UTC the previous day. Grep for the PREVIOUS day's UTC date when looking for pipeline sessions.

## State Files (in ~/.hermes/research_outputs/)
- `.honcho_bridge_state.json` — tracks files pushed to Honcho
- `.gmail_ingestor_state.json` — tracks processed email IDs
- `.podcast_monitor_state.json` — tracks ingestion runs, episodes
- `.cleanup_state.json` — tracks archived count
- `.briefing_feedback.json` — user responses to briefing improvement prompts (NEW Jun 2026)
- `.briefing_improvements.json` — briefing improvement tracking history (NEW Jun 2026)
- `.research_enriched_latest.json` — enriched research output
