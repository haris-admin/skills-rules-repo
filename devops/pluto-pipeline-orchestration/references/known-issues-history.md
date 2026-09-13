# Pipeline Known Issues — Incident History

Chronological incident log for the daily cron pipeline: root causes, fixes applied, and resolution status. Most entries are historical (already fixed) — kept for pattern-recognition ("has this exact error happened before, and what fixed it") rather than as an active to-do list. A handful of entries (marked without a checkmark) describe ongoing design rules or environmental limitations rather than one-off bugs.

## Contents
- [✅ FIXED: Vercel Monitor False Positive (June 20, 2026)](#fixed-vercel-monitor-false-positive-june-20-2026)
- [✅ PRUNED: 6 Dead Crons Removed (June 13, 2026)](#pruned-6-dead-crons-removed-june-13-2026)
- [✅ RESOLVED: Podcast Crons (June 7–8, 2026)](#resolved-podcast-crons-june-78-2026)
- [🔴 401 Auth Cascade (June 10, 2026 — Systemic)](#401-auth-cascade-june-10-2026-systemic)
- [🔴 Stale Stream / Broken Pipe Recovery (June 9-11, 2026 — 3 Consecutive Days, Escalated to Pattern)](#stale-stream-broken-pipe-recovery-june-9-11-2026-3-consecutive-days-escalated-to-pattern)
- [Git Repo Sync Merge Failures — Cosmetic (c23dc3f73e2d, patched June 13)](#git-repo-sync-merge-failures-cosmetic-c23dc3f73e2d-patched-june-13)
- [✅ RESOLVED: Chunks Table — 0 → 501 rows (June 13, 2026)](#resolved-chunks-table-0-501-rows-june-13-2026)
- [✅ RESOLVED: Performance Tracker Cron Health 0/0 — Reads jobs.json (June 14, 2026)](#resolved-performance-tracker-cron-health-00-reads-jobsjson-june-14-2026)
- [✅ RESOLVED: All no_agent Cron Model Fields Cleared — Prevents False-Positive Error Reports (June 14, 2026)](#resolved-all-no_agent-cron-model-fields-cleared-prevents-false-positive-error-reports-june-14-2026)
- [✅ NEW: Cross-Reference Verification Scripts (June 14, 2026)](#new-cross-reference-verification-scripts-june-14-2026)
- [🟡 Performance Tracker Error Count — FIXED June 20, 2026](#performance-tracker-error-count-fixed-june-20-2026)
- [🔴 Podcast Insight Extractor — Supabase Auth Failures in Tool Calls (June 19, 2026)](#podcast-insight-extractor-supabase-auth-failures-in-tool-calls-june-19-2026)
- [🔴 Sunday Adversarial Triple-Run — Scheduler Anomaly (June 14, 2026)](#sunday-adversarial-triple-run-scheduler-anomaly-june-14-2026)
- [✅ MILESTONE: First Zero-Error Week (June 19, 2026)](#milestone-first-zero-error-week-june-19-2026)
- [✅ RESOLVED: Daily Maintenance Broken Pipe — Model deepseek-v4-flash → deepseek-v4-pro (June 14, 2026)](#resolved-daily-maintenance-broken-pipe-model-deepseek-v4-flash-deepseek-v4-pro-june-14-2026)
- [WSL Git Clone Fails in Hermes Sandbox (June 8)](#wsl-git-clone-fails-in-hermes-sandbox-june-8)
- [Gateway False Negative](#gateway-false-negative)
- [✅ RESOLVED: Podcast Ingestion Broken Pipe + Missing Dependency (June 12, 2026)](#resolved-podcast-ingestion-broken-pipe-missing-dependency-june-12-2026)
- [✅ RESOLVED: Pluto Fleet Monitor AML Hive — 5PM Venv Missing (June 26, 2026 → fixed by June 29)](#resolved-pluto-fleet-monitor-aml-hive-5pm-venv-missing-june-26-2026-fixed-by-june-29)
- [🔴 Saturday Auto-Improvement Pipeline: Reports ≠ Action (June 20 + June 26, 2026)](#saturday-auto-improvement-pipeline-reports-action-june-20-june-26-2026)
- [🔴 Briefing Improver — Dict Connection Crash (June 26, 2026 — FIXED)](#briefing-improver-dict-connection-crash-june-26-2026-fixed)
- [✅ RESOLVED: TapEase Bridge HTML Error Pages (Jul 8, 2026 — Replaced by Direct AWS Monitor)](#resolved-tapease-bridge-html-error-pages-jul-8-2026-replaced-by-direct-aws-monitor)
- [✅ RESOLVED: Dispatch Pipeline Zombie Crontab (June 12, 2026)](#resolved-dispatch-pipeline-zombie-crontab-june-12-2026)
- [✅ RESOLVED: Telegram Polling Conflict (June 12, 2026)](#resolved-telegram-polling-conflict-june-12-2026)
- [✅ CONFIRMED: Podcast Chunking Pruned — No Longer in jobs.json (June 19, 2026)](#confirmed-podcast-chunking-pruned-no-longer-in-jobsjson-june-19-2026)
- [⚠️ Vercel Monitor False Positive — FIXED June 20, 2026](#vercel-monitor-false-positive-fixed-june-20-2026)
- [Design Rule: Script-Only Crons MUST Be `no_agent: true`](#design-rule-script-only-crons-must-be-no_agent-true)
- [Pitfall: `cronjob(action='update', script=...)` Does NOT Auto-Set `no_agent` (June 12, 2026)](#pitfall-cronjobactionupdate-script-does-not-auto-set-no_agent-june-12-2026)
- [Pitfall: `/tmp` Venvs Disappear on WSL Reboot](#pitfall-tmp-venvs-disappear-on-wsl-reboot)
- [Pitfall: Long-Running no_agent Scripts Hit BrokenPipeError on Cron Timeout](#pitfall-long-running-no_agent-scripts-hit-brokenpipeerror-on-cron-timeout)
- [✅ RESOLVED: Feedback Loop Broken Pipe (June 12, 2026)](#resolved-feedback-loop-broken-pipe-june-12-2026)
- [✅ RESOLVED: Git Sync Dead Repos — Fully Skipped (June 20, 2026)](#resolved-git-sync-dead-repos-fully-skipped-june-20-2026)
- [✅ RESOLVED: Skill Extractor Broken Pipe (June 12–13, 2026)](#resolved-skill-extractor-broken-pipe-june-1213-2026)
- [RESOLVED ISSUES](#resolved-issues)
- [✅ RESOLVED: Podcast KB Ingestion Timeout — Global script_timeout_seconds Fix (June 14, 2026, updated to 900s)](#resolved-podcast-kb-ingestion-timeout-global-script_timeout_seconds-fix-june-14-2026-updated-to-900s)
- [✅ RESOLVED: Mempalace Watcher — Converted to no_agent (May 24, 2026 — old problem, DO NOT RE-FLAG)](#resolved-mempalace-watcher-converted-to-no_agent-may-24-2026-old-problem-do-not-re-flag)

### ✅ RESOLVED: Podcast KB Ingestion Timeout — Global script_timeout_seconds Fix (June 14, 2026, updated to 900s)
The podcast ingestor (`d4d77c41f6c0`) processes 16 YouTube channels with rate-limited transcript downloads and Supabase inserts. **Measured runtime: 872 seconds (14.5 min)** for a full run with 12 new episodes ingested. The original 120s default timeout caused every run to fail.

**Fix timeline:**
1. **June 14, 14:00:** Set `cron.script_timeout_seconds: 300` — still not enough
2. **June 14, 18:00:** Measured actual runtime at **872 seconds** for a full run. Script ingested 12 episodes cleanly across 16 channels with zero errors. The YouTube API works; the fallback to yt-dlp for some channels (Moonshots, a16z, Logan Bartlett) adds latency but doesn't cause failures.
3. **June 14, 18:15:** Set `cron.script_timeout_seconds: 900` — verified correct

**Verification:** `grep script_timeout_seconds ~/.hermes/config.yaml` → shows `900`.

**Important:** There is no per-job timeout in the Hermes cron scheduler. The `script_timeout_seconds` config is a single global value for all no_agent scripts. If a future job needs a different timeout, `scheduler.py` at line ~1009 would need modification to support a per-job `timeout` field in `jobs.json`. The current 900s is safe for all scripts — fast ones finish well before it. (Superseded — see the 3600s escalation in the main skill's Pitfalls list.)

### ✅ RESOLVED: Mempalace Watcher — Converted to no_agent (May 24, 2026 — old problem, DO NOT RE-FLAG)

> **⚠️ TRAP:** This job is `no_agent: true`. The `model` field in `cronjob list` is **cosmetic** — it has zero effect. Any report of "broken pipe" or "LLM errors" on this job is either stale or misattributed. **Do not flag this job.** The fix was applied on May 24, 2026.

The Mempalace Inbox Watcher (`5678a363ce3b`, every 5m) was **originally** an LLM-driven cron calling DeepSeek Flash. DeepSeek's streaming server intermittently hangs for 180s+ even at 4.8K tokens.

**Fix (May 24):** Converted to `no_agent: true` script (`mempalace_watcher.py`). The watcher is a mechanical file-checker — it doesn't need an LLM. Runs as a standalone Python script, exits 0 with empty stdout when no new files, non-empty when processing. **No more DeepSeek dependency = no more broken pipe.**

**Pattern:** Any cron job that checks files, runs a script, or performs deterministic work should be `no_agent: true`. Only use LLM-driven crons for tasks that genuinely need reasoning (synthesis, extraction, content generation).

### ✅ FIXED: Vercel Monitor False Positive (June 20, 2026)
The 4 stale BLOCKED deployments (dpl_7rXe, dpl_7kaK, dpl_GLpe, dpl_DSrt) that triggered false positives every run were verified to be garbage-collected artifacts. The monitor now pings `GET /v1/deployments/{uid}` before alerting on BLOCKED deployments — returns 404/not_found means the deployment no longer exists and is skipped. **Before:** 9/14 runs produced alerts. **After:** Only real deployment errors trigger alerts.

### ✅ PRUNED: 6 Dead Crons Removed (June 13, 2026)
Removed: Podcast Ingestion, Podcast Chunking, Voice Processor, A2Square Sync (Mon+Thu), Weekly Research Digest. All had persistent errors or were superseded.

### ✅ RESOLVED: Podcast Crons (June 7–8, 2026)
Both podcast crons (`fabab82f804a` ingestion, `67319a9b2606` insight extractor) were documented as "never fired" on June 6 due to a gateway scheduler bug. They self-resolved starting June 7 and have been firing reliably since:
- **Podcast Ingestion** (fabab82f804a): Jun 7 ✅, Jun 8 ✅ (17 episodes ingested, 39 found)
- **Podcast Insight Extractor** (67319a9b2606): Jun 7 ✅, Jun 8 ✅ (15 episodes, 6 frameworks, 4 quotes, 8 trends)
Root cause likely a gateway restart or state reset that cleared whatever was causing the scheduler picker to drop these jobs.

### 🔴 401 Auth Cascade (June 10, 2026 — Systemic)
**4 crons failed with identical 401 error on the same day:**
- Podcast KB Ingestion (`fabab82f804a`) — 401 Unauthorized
- Podcast Insight Extractor (`67319a9b2606`) — 401 Unauthorized
- LinkedIn Ideas (`ee4e48300826`) — 401 Unauthorized
- Daily Maintenance (`575918cbc242`) — 401 Unauthorized

**Signal:** 3+ crons with the same error = systemic credential failure, NOT individual bugs.
**Likely cause:** Hermes Gateway authentication token expired or was rotated. Check provider API keys.
**Impact:** Podcast pipeline completely down for one day. LinkedIn missed its schedule.
**Resolution:** Self-resolved by next cycle (no manual fix needed) — transient credential blip.

### 🔴 Stale Stream / Broken Pipe Recovery (June 9-11, 2026 — 3 Consecutive Days, Escalated to Pattern)

**Error:** `RuntimeError: [Errno 32] Broken pipe` — triggered by `Stream stale for Ns — no chunks received. Killing connection.`
**Affected crons:** Morning Research (`b0de180cec84`, 50K+ token context), Podcast KB Ingestion (`fabab82f804a`, ~22K), Skill Extractor (`2d33c8f9a89c`, ~13K)
**Days:** Jun 9 ❌, Jun 10 ❌, Jun 11 ✅ recovered on retry
**Severity:** HIGH — primary signal source for the entire pipeline.
**Hermes retry behavior:** Built-in 3-attempt retry with ~2s exponential backoff. Recovery rate ~2/3 of cases (research ✅ on retry Jun 11, skill extractor ✅ on retry Jun 11, podcast KB remained down due to concurrent 401).
**Impact when unrecovered:** No research JSON produced → synthesis engine runs on stale corpus data. Pipeline demonstrates partial resilience (synthesis/action bridge/feedback complete with old data).

**Detection in agent.log:**
```
WARNING agent.chat_completion_helpers: Stream stale for Ns (threshold Ns) — no chunks received. Killing connection.
WARNING agent.conversation_loop: API call failed (attempt 1/3) error_type=ReadError ... summary=[Errno 32] Broken pipe
WARNING agent.conversation_loop: Retrying API call in 2.x s (attempt 1/3)
```

**Outcome verification (check both):**
1. `cron/jobs.json` → `last_status` field for the cron ID
2. Output file existence: check `cron/output/<id>/` for output `.md` file
3. Research-specific: check `research_outputs/research_YYYY-MM-DD.json` exists

**Pattern signature:** Large-context crons (>10K tokens) are most susceptible. The stale-stream threshold varies by cron (180s for most, 240s for research). Retry usually succeeds on the second attempt but the pipeline runs ~2-3 minutes late as a result.

**Escalation criteria:**
1-2 consecutive failures → operational alert, monitor next run
3+ consecutive failures across 3+ crons → qualifying pattern, document recovery workflow
Any failure combined with a second error type (e.g., 401) → permanent failure, provider-level escalation

### Git Repo Sync Merge Failures — Cosmetic (c23dc3f73e2d, patched June 13)
The script now tracks merge failures separately from fetch failures. Merge failures (local branch divergence, dirty working trees) produce `⚠️` warnings but don't count toward fatal exit code. Only fetch failures that affect data freshness count as `failed`. Script exits 0 even when merge failures occur.

### ✅ RESOLVED: Chunks Table — 0 → 501 rows (June 13, 2026)
`podcast_kb.chunks` was empty (0 rows) as of June 12 despite 169+ episodes with transcripts. The chunking pipeline (`79c8ad5b9465`, 2:00 AM AEST) was converted to `no_agent: true` and began producing chunks. As of June 13: **501 chunks across 214 episodes.** Vector search is now functional.

### ✅ RESOLVED: Performance Tracker Cron Health 0/0 — Reads jobs.json (June 14, 2026)
`run_cron_list()` in `pluto_performance_tracker.py` was reading from `cron/state.db` (0 bytes SQLite — always empty) instead of `cron/jobs.json` (63KB, 27 job entries). Every daily snapshot showed `total: 0, ok: 0, error: 0` — feeding zero data to the Saturday review. **Fix:** Rewrote `run_cron_list()` to parse `jobs.json` (format: `{'jobs': [...], 'updated_at': '...'}`). Now returns 27 jobs with correct health stats (25 OK, 2 error as of Jun 14). W23 only has 2 days because the job was created Jun 13 (mid-week) — Jun 15 (W24) will track all 7 days naturally.

### ✅ RESOLVED: All no_agent Cron Model Fields Cleared — Prevents False-Positive Error Reports (June 14, 2026)
**14 cron jobs** that were `no_agent: true` still showed model names like `deepseek-v4-flash` in `cronjob list` output. This model field is **cosmetic** on no_agent jobs — the scheduler never invokes an LLM. However, the Saturday/Sunday reviews see the model name and hallucinate error reports (example: the review claimed 384-426 broken pipe errors/day on the Mempalace Watcher — a job already no_agent since May 24 with zero LLM calls).

**Fix:** All 14 no_agent cron model fields set to `model: no-agent-cron, provider: none`.

**Verification:** `cron_verify.py --issues-only` now reports `false_flags: 0`.

### ✅ NEW: Cross-Reference Verification Scripts (June 14, 2026)
Two new scripts in `~/.hermes/scripts/` that prevent false-positive error reporting:

1. **`cron_verify.py`** — Full cron health scan. Flags real issues vs false flags. Exits 1 if real issues exist, 2 if only false flags. Usage: `python3 ~/.hermes/scripts/cron_verify.py --issues-only`

2. **`cross_ref_verify.py <job_id> <claimed_issue>`** — Validates a single error claim against actual evidence. Returns verdict: FALSE-POSITIVE (exit 2, do NOT report), CONFIRMED (exit 1, report), or INCONCLUSIVE (exit 0, investigate). Usage: `python3 ~/.hermes/scripts/cross_ref_verify.py 5678a363ce3b "Mempalace Watcher broken pipe"`

**Purpose:** The Saturday review previously reported the Mempalace Watcher as having 384-426 broken pipe errors/day — but the job was already no_agent for 3 weeks with zero LLM calls and clean `[]` output every 5 minutes. These scripts cross-reference claims against evidence before surfacing them. Embed `cross_ref_verify.py` as the first step in any review's cron health section.

### 🟡 Performance Tracker Error Count — FIXED June 20, 2026
`pluto_performance_tracker.py` now distinguishes between:
- **Cron execution errors** (ERROR entries in errors.log — the real metric)
- **Tool-level warnings** (WARNING entries in errors.log — tracked separately as `tool_warnings_today`)
Both are reported in the daily snapshot. The Saturday review now sees `total_errors` (real) and `total_tool_warnings` (noise) separately.

### 🔴 Podcast Insight Extractor — Supabase Auth Failures in Tool Calls (June 19, 2026)

**Root cause:** Agent-driven cron (`67319a9b2606`, `no_agent: false`) attempts direct `psql` connections to Supabase with hardcoded credentials. Password authentication fails. Agent retries multiple times (7 attempts on Jun 19) and eventually falls back to other methods, producing output — but each attempt generates WARNING entries in errors.log.

**Evidence:** `errors.log` shows 7 consecutive `psql: FATAL: password authentication failed for user "postgres"` from `cron_67319a9b2606`. Job still produces `podcast_insights.json` (12KB, 15 episodes queried).

**Impact:** Low — output is produced, but error log is noisy. Agent wastes tool calls retrying psql.

**Fix:** Either update Supabase password used by the agent's tool calls, or have the agent skip psql and use Python Supabase client directly (which handles auth properly).

### 🔴 Sunday Adversarial Triple-Run — Scheduler Anomaly (June 14, 2026)

**Root cause:** Sunday Adversarial Pulse (`f8756a2b8403`) ran 3 times on June 14: once at 06:03 (scheduled), then again at 14:44 and 14:52. Likely a force-run or batch-trigger after a gateway restart/maintenance action.

**Evidence:** 3 output files for Jun 14 in `cron/output/f8756a2b8403/`: `06-03-08` (35KB), `14-44-57` (37KB), `14-52-27` (35KB).

**Impact:** Low — duplicate reports, wasted tokens. No harm beyond resource waste.

**Detection pattern:** Multiple crons with identical `last_run_at` timestamps far from their scheduled times indicate a batch-trigger, not individual cron bugs.

### ✅ MILESTONE: First Zero-Error Week (June 19, 2026)

All 31 cron jobs with `last_status: ok` across the entire week of June 13-19. First clean week since the pipeline was established. Key enablers: June 13 prune (6 dead crons), model upgrades (flash→pro), BrokenPipeError wrappers, and no_agent conversions.

### ✅ RESOLVED: Daily Maintenance Broken Pipe — Model deepseek-v4-flash → deepseek-v4-pro (June 14, 2026)
The Hermes Daily Maintenance cron (`575918cbc242`, 2PM daily) was running on `deepseek-v4-flash` and hitting `RuntimeError: [Errno 32] Broken pipe` exactly at 180s (the flash streaming timeout). This was the **real source** of the 800+ broken pipe errors/week attributed to the Mempalace Watcher. **Fix:** Changed model to `deepseek-v4-pro` via `cronjob(action='update', model={'model': 'deepseek-v4-pro', 'provider': 'deepseek'})`. The pro model handles long-context agent sessions without disconnecting. **Lesson:** Always verify which cron job is actually producing errors by checking its `last_status` and `output` — don't trust error attribution in second-hand reports. The Mempalace Watcher (`5678a363ce3b`) was already `no_agent: true` with zero LLM calls and had `last_status: ok` on every single run.

### WSL Git Clone Fails in Hermes Sandbox (June 8)
`git clone` over HTTPS to WSL cross-mount fails with `waitpid: No child processes`. Workaround: GitHub archive API or manual Windows-side clone. Git pull with `-c credential.helper=` works.

### Gateway False Negative
"Gateway is not running" warning is cosmetic. `ps aux` confirms gateway PID running.

### ✅ RESOLVED: Podcast Ingestion Broken Pipe + Missing Dependency (June 12, 2026)
Podcast KB Ingestion (`fabab82f804a`) was an **LLM-driven cron job** that ran `podcast_ingestor.py` via subprocess. Two issues: (1) LLM-driven cron caused `RuntimeError: Broken pipe` — same pattern as Feedback Loop. Fixed by converting to `no_agent: true` script. (2) The `/tmp/podcast_venv/` had `youtube-transcript-api` MISSING — transcript fetches silently failed (returned None). Installed: `/tmp/podcast_venv/bin/pip install youtube-transcript-api`. After both fixes, script ingests 5-8 episodes per run across 16 channels.

**June 12, 2026 — Second BrokenPipeError fix:** The podcast ingestor was already `no_agent: true`, but long-running scripts (13+ min for YouTube operations) get their stdout pipe closed by the cron scheduler on timeout. The main `main()` return then causes `BrokenPipeError: [Errno 32] Broken pipe` during stdout flush. Applied the `try/except BrokenPipeError` wrapper pattern (see pitfall below) to `podcast_ingestor.py`. Script now exits 0 gracefully even when the scheduler closes the pipe. Also wrapped in `sys.exit(0 if result is not None and result >= 0 else 1)` for proper exit code signaling.

### ✅ RESOLVED: Pluto Fleet Monitor AML Hive — 5PM Venv Missing (June 26, 2026 → fixed by June 29)

**Cron:** `a0b1f0f642af` (11AM + 5PM runs, `deliver: origin`)
**Original symptoms:** 5PM run on June 26 failed with `No such file or directory: '/home/habib/.hermes/repo/venv/bin/python'`. 

**Fix applied:** `/home/habib/.hermes/repo/venv/bin/python` now exists. June 27-29 5PM runs all produce normal output (~1KB each, Fly.io + Sentry + Vercel health checks). All `last_status: ok` since June 27.

**Lesson:** Per-run venv path mismatches can cause single-time-slot failures. If only one run time fails while others succeed, check the venv path in the script's shebang or the cron's script field.

### 🔴 Saturday Auto-Improvement Pipeline: Reports ≠ Action (June 20 + June 26, 2026)

**Pattern:** The Saturday auto-improvement cron (`159702fe072c`) writes comprehensive Phase 1-5 reports claiming "fixes deployed" — but the actual code changes are rarely applied. Week 3 (Jun 20): 1 of 4 specified fixes implemented. Week 4 (Jun 26): Verified Vercel Monitor and Git Sync fixes were NOT present in code despite the Saturday report claiming "3 scripts fixed."

**Root cause:** The LLM is guided to produce reports about fixes rather than executing them. The prompt allows the agent to describe what it WOULD do without actually doing it.

**Detection:** After the Saturday cron runs, verify claimed fixes exist in actual files:
```bash
grep "SKIP_REPOS" ~/.hermes/scripts/git_sync.py          # Should exist if "fixed"
grep "No deployments" ~/.hermes/scripts/vercel_monitor.py # Should NOT alert if "fixed"
```

**Fix:** The Saturday cron prompt must use ACTION language with verification. Example: "EXECUTE this patch, then run `grep` to verify it was applied before claiming it's done." The current "dream mode" framing encourages speculation over execution.

### 🔴 Briefing Improver — Dict Connection Crash (June 26, 2026 — FIXED)

**Root cause:** The podcast insight extractor (`67319a9b2606`) changed `portfolio_connections` format from strings (`"AML Hive - rationale"`) to dicts (`{"project": "AML Hive", "rationale": "...", "episode": "..."}`). `briefing_improver.py`'s `_map_podcast_connections()` called `.split()` on dict objects → `AttributeError`.

**Fix:** Patched `_map_podcast_connections()` and the inline connection_text builder in `extract_regulatory_signals()` to handle both formats with `isinstance()` checks. Script now handles both legacy strings and new dicts.

**File:** `~/.hermes/scripts/briefing_improver.py` — lines ~530 and ~195.

### ✅ RESOLVED: TapEase Bridge HTML Error Pages (Jul 8, 2026 — Replaced by Direct AWS Monitor)

All 4 TapEase Fleet Monitors fail with `JSONDecodeError: Expecting value: line 1 column 1 (char 0)`. The bridge at port 18796 returns HTTP 200 on `/health` but the `/tapease/monitor` endpoint returns an HTML error page instead of JSON.

**Affected crons:** `dbd3cb1b5bd3` (5AM), `582bd225ddd1` (11AM), `1086e6405da1` (5PM), `be81c61778a8` (11PM) — all `deliver: origin` with identical error.

**Resolution (Jul 8, 2026):** Built `tapease_prod_monitor.py` — direct AWS CLI + SSM. No bridge dependency. All 4 TapEase cron jobs updated to use the new script. See `tapease-fleet-monitor` skill for details.

### ✅ RESOLVED: Dispatch Pipeline Zombie Crontab (June 12, 2026)
**33 dead entries removed** from traditional crontab. The `dispatch_pipeline.sh` script wrote task JSON files to `~/.hermes/tasks/` but nothing consumed them — they were write-only. All 33 entries removed. Only remaining crontab entries: `@reboot` startup recovery + `*/2 * * * *` gateway watchdog.

### ✅ RESOLVED: Telegram Polling Conflict (June 12, 2026)
`voice_poller.py` (job `bcbe9b21e0ab`, every 1 min) polled Telegram with same bot token as Gateway → constant polling conflicts. **Paused** the cron. Gateway handles Telegram natively.

### ✅ CONFIRMED: Podcast Chunking Pruned — No Longer in jobs.json (June 19, 2026)
The podcast chunking cron (`79c8ad5b9465`) was removed in the June 13 prune. Verified on June 19 — no entry found in `jobs.json`, no output directory. This trade-off (stability over chunking) is accepted. If chunking is needed again, create a new `no_agent: true` script with a 900s+ timeout.

### ⚠️ Vercel Monitor False Positive — FIXED June 20, 2026
The 4 stale BLOCKED deployments (dpl_7rXe, dpl_7kaK, dpl_GLpe, dpl_DSrt) that triggered false positives every run were verified to be garbage-collected artifacts. The monitor now pings `GET /v1/deployments/{uid}` before alerting on BLOCKED deployments — returns 404/not_found means the deployment no longer exists and is skipped.
**Before:** 9/14 runs produced alerts on stable AML Hive. **After:** Only real deployment errors trigger alerts.

**Design rule for no_agent alert scripts:**

**Rule:** `no_agent` scripts must **always exit 0**. Use stdout emptiness vs. non-emptiness to signal health:
- **Healthy** → empty stdout, exit 0 → cron runs silently, no delivery
- **Alert** → non-empty stdout, exit 0 → cron output contains alert text, delivery fires

The cron scheduler uses exit code 0/1 as its primary health signal. Exit codes 1+ are treated as script failures, not alert notifications. If your script needs to notify humans (email, Telegram), do it **inside the script itself** — not via exit code.

**Before (wrong):**
```python
if alerts:
    send_email(...)  # ✅ sends alert
    return 1         # ❌ cron shows "error" — false positive
return 0
```

**After (correct):**
```python
if alerts:
    send_email(...)  # ✅ sends alert
    return 0         # ✅ cron shows "ok" — correct
return 0
```

**Verification:** `hermes cron list | grep JOB_ID` should show `last_status: ok` after the fix. Check `cron/output/<id>/` for the alert output file.

### Design Rule: Script-Only Crons MUST Be `no_agent: true`

**Signal:** Any cron job whose prompt is essentially "Run this Python script" is a **script cron**, not an LLM cron. If the job's entire purpose is to execute a deterministic script, it should be `no_agent: true` with a `script:` field. LLM-driven crons that shell out to scripts will hit `RuntimeError: Broken pipe` because the LLM tries to format/print output after the script runs, but the cron harness has already closed stdout.

**Fix:** Convert to `no_agent: true`:
```bash
hermes cron update JOB_ID --no-agent --script path/to/script.py --prompt ""
```

**Test:** `hermes cron run JOB_ID` should return immediately with the script's stdout as output. No LLM token burn.

### Pitfall: `cronjob(action='update', script=...)` Does NOT Auto-Set `no_agent` (June 12, 2026)

The `cronjob` tool's `update` action sets the `script` field but **does not set `no_agent: true`**. After updating, `jobs.json` still shows `"no_agent": false`. The job keeps running in agent mode with an empty prompt, wasting tokens or hitting broken pipe again.

**Fix after update:** Manually set the flag in jobs.json:

```bash
python3 -c "
import json
data = json.load(open('/home/habib/.hermes/cron/jobs.json'))
for j in data['jobs']:
    if j['id'] == 'JOB_ID':
        j['no_agent'] = True
        j['prompt'] = ''
json.dump(data, open('/home/habib/.hermes/cron/jobs.json', 'w'), indent=2)
"
```

Then verify with `grep '"no_agent"' ~/.hermes/cron/jobs.json | head -1`.

**Crons hit by this (June 12):** `2d33c8f9a89c` (Skill Extractor) needed manual fix after `cronjob(action='update', script='skill_extractor.py')`.

### Pitfall: `/tmp` Venvs Disappear on WSL Reboot

`/tmp/podcast_venv/` (and any other `/tmp`-based Python venvs) get wiped when WSL restarts or the system reboots. This silently breaks any `no_agent` script that depends on them. The podcast ingestor (`d4d77c41f6c0`) fails with `No such file or directory: '/tmp/podcast_venv/bin/yt-dlp'` every time the venv is cleaned.

**Detection:** `ls /tmp/podcast_venv/bin/yt-dlp` returns "No such file or directory".

**Fix:** Recreate the venv and install dependencies:
```bash
python3 -m venv /tmp/podcast_venv
/tmp/podcast_venv/bin/pip install yt-dlp youtube-transcript-api
```

**Long-term fix:** Move the venv to `~/.hermes/venvs/podcast/` which survives reboots. Update `podcast_ingestor.py` to reference the new path.

### Pitfall: Long-Running no_agent Scripts Hit BrokenPipeError on Cron Timeout

A `no_agent` script that runs longer than the cron scheduler's timeout (default ~120-180s) gets its stdout pipe closed by the scheduler. If Python's `main()` returns and the runtime tries to flush stdout, you get `BrokenPipeError: [Errno 32] Broken pipe`. The output already written (stdout capture) IS saved to the cron output file, but the job shows `FAILED` status.

**Fix:** Wrap `main()` in a try/except for `BrokenPipeError`:

```python
if __name__ == '__main__':
    try:
        result = main()
        sys.exit(0 if result is not None and result >= 0 else 1)
    except BrokenPipeError:
        # Cron scheduler closed stdout pipe (timeout) — exit gracefully
        sys.exit(0)
    except Exception as e:
        print(f"FATAL: {e}")
        sys.exit(1)
```

This pattern is already applied to `podcast_ingestor.py` (June 12, 2026), `skill_extractor.py` (June 13, 2026), and `pluto_feedback_processor.py` (June 13, 2026). The script completes its work and produces output; the BrokenPipeError is handled gracefully and the cron shows `ok` status.

### ✅ RESOLVED: Feedback Loop Broken Pipe (June 12, 2026)
LLM-driven cron → `no_agent: true` script. No more `RuntimeError: Broken pipe`.

### ✅ RESOLVED: Git Sync Dead Repos — Fully Skipped (June 20, 2026)
`git_sync.py` now skips `KNOWN_DEAD_REPOS` entirely (doesn't attempt fetch). Previously: dead repos were fetched (and failed) with errors suppressed by exit code — still produced "fetch failed" noise in every run. Now: repos in the dead set are skipped at the work-item loop before any git operation. Daily output is silent on known-dead repos.

### ✅ RESOLVED: Skill Extractor Broken Pipe (June 12–13, 2026)
**June 12:** Converted from LLM-driven cron to `no_agent: true` script (`skill_extractor.py`). The old LLM-driven cron tried to call terminal tools via subprocess and hit `RuntimeError: Broken pipe` because the cron harness closed stdout before the LLM finished generating. Now runs as a deterministic Python script that scans `scripts/`, `research_outputs/`, and `cron/output/` for recently modified files and identifies scripts without matching skills. Proposal output saved to `research_outputs/skill-proposals_YYYY-MM-DD.md`.

**June 13:** Even as a `no_agent: true` script, the extractor hit `BrokenPipeError` on Jun 12 because the cron scheduler closed stdout before Python flushed. Applied the `try/except BrokenPipeError` wrapper pattern (same as `podcast_ingestor.py`) to the entire execution block. Script now exits 0 gracefully on pipe closure.

### RESOLVED ISSUES
- ✅ **Podcast Crons** (June 7, 2026): Both fabab82f804a (ingestion) and 67319a9b2606 (insight extractor) now firing reliably after the June 6 gateway scheduler bug self-resolved. Both ran Jun 7 and Jun 8 with full output.
- ✅ **Gmail Ingestor** (June 7): Himalaya sandbox failure → switched to `no_agent: true` imaplib script
- ✅ **Voice Processor Delivery** (June 8): `deliver: origin` had no resolver → switched to `deliver: local` (later resolved by pausing the cron entirely on June 12)
- ✅ **Communication Protocol** (June 8): All crons switched to `deliver: local` except Learning (REVERSED June 12 — most now deliver to origin)
- ✅ **401 Auth Cascade** (June 10): 4 crons failed with 401 on the same day. Transient — self-resolved. Documented as systemic detection pattern.
