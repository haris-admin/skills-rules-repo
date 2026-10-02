# W36 Diagnostic Findings — week ending Fri 11 Sep 2026

Scope: 2026-09-05 → 2026-09-11. Snapshot numbers: 75 crons (73 enabled), 61 `ok` / 14 `error`,
6 real failures behind 4 root causes, 7/7 pipeline days, 203 podcast episodes, ~20 user requests
(187 user messages over 3 Telegram sessions).

## 1. Stale hardcoded instance-ID fallback (CRITICAL — two crons, one cause)

- `i-0b111b75d3c70fcb7` (AML Hive backend, t3.medium) was terminated; `i-04f81ec595a004caf`
  (t3.medium, launched 2026-09-10T15:54Z = Sep 11 01:54 AEST) carries the `amlhive-prod-backend` tag.
- `amlhive_prod_monitor.py:33-54` `get_instance_id()` runs `aws ec2 describe-instances` with **no**
  `env=load_aws_creds()` → tag discovery has always queried the ambient account (`707843605914`,
  `IAM_GRAFANA`) instead of the product account (`560205084533`) and silently used the hardcoded
  fallback on lines 56-57. The frontend fallback happened to stay valid, which hid the bug.
- Symptoms: 4×/day monitor emits `[P0] Backend instance … not found in EC2` and stops monitoring
  backend Docker/uptime/disk/mem; `amlhive_daily_report.py:32` (same helper) failed Sep 11 21:15 with
  `JSONDecodeError` because SSM send-command against a dead instance returns no JSON. It had passed
  Sep 1-10.
- It is **not** a live outage: `https://api.amlhive.com.au/health` = 200, frontend healthy.
- Fix = creds env in the helper + refresh both fallbacks + update SSM/C464 runbooks to the new ID.

## 2. Chamber Refresh vs Hermes update days (Mon/Fri)

`0949371eec17`-style evidence (job `0959371eec17`): Sep 7 and Sep 11 = `chromadb import failed`;
Sep 8/9/10 = `✅ Fed 16-17 new item(s)`; Sep 2-4 = `Fed 0 items` (separate silent window).
Sep 7 = Monday, Sep 11 = Friday → both are 3AM Hermes Update Check (`4eef20ef0e25`, Mon+Fri) days,
where `uv pip install -e .` reintroduces opentelemetry drift. Feeds go dark at 05:25 until the
14:08 repair. Fix direction: repair pins immediately after the update, or self-heal inside
`pluto_chamber_refresh.py` when the smoke test fails.

## 3. Feedback loop degenerate scorer

`feedback_2026-09-04..11.json` all report `findings_estimated_used: 1`,
`total_findings_available: 6`, `topics_used: ["AUSTRAC"]`; `signal_scores.json` records **every**
finding with `used_count: 86, skipped_count: 0, score: 1.0`. A scorer that never records a skip
cannot reweight anything, so the daily "boost general/market-signals/startup-ecosystem" advice and
the "17% stuck" narrative are artefacts of a broken metric, not of signal quality.

## 4. Test suite state (job `044c0bc41e31`)

Backend improved to `7038 passed, 0 failed`. Frontend `196 passed, 1 failed` for 16 consecutive runs
(jsdom `navigation` / `instanceof Blob`). Playwright: `48 passed` on Sep 10 but **0 tests executed**
on Sep 11 (`EventEmitter.defaultMaxListeners` in the web-server bootstrap) — guard against a green
overall line when zero E2E tests ran.

## 5. Competitor intel 0-hit root cause (job `1a13a2d49682`)

7/7 days at 773 bytes with `hits: 0`, `competitors_tracked: 79`, and `_diag.texts_loaded: 14`
(16,243 chars) from `research_*.json`, `synthesis_*.json`, `gumby-brief-input.md`. The W31 `--debug`
fix is present and working — the source set is simply too narrow. Either widen sources (podcast
transcripts, feed items) or mark the section degraded/skip it.

## 6. TTS 401 (low user impact)

`tts.provider: openai` is handed an OpenRouter key (`sk-or-v1-…6728`) → 401 on Sep 10 05:09 and
Sep 11 05:07. The 6:00 briefing MP3s are still produced daily (`voice_outputs/pluto_briefing_2026-09-1*.mp3`,
2.1-2.35 MB), so the user-facing voice briefing survives; the failure is noise plus a wasted tool call.
Credential belongs to Haris.

## 7. Verifier false positives to suppress

- 5 `cron_verify.py` stall flags = weekly/monthly crons waiting correctly (111h, 108h, 86h, 263h, 259h).
- `3a818ea08059` `last_run_at: null` = created 2026-09-08, first fire Mon 14 Sep.
- 4 `Interrupted by shutdown before terminal completion` crons all have complete outputs and
  `last_delivery_error: None`; the cuts land 3-5 min into 6:00 LLM runs with no matching gateway
  restart in `gateway.log`, i.e. worker/executor teardown, not a user restart.
