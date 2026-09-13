---
name: pluto-pipeline-orchestration
description: Pluto's 35-stage cron pipeline orchestration — the full morning-to-night chain from Podcast Ingestion through Git Sync, Gmail, Research, Synthesis, Action Bridge, Feedback, LinkedIn, Voice, to Cleanup, plus fleet monitors, daily business reports, and weekly reviews. Use when managing, debugging, or modifying the cron pipeline schedule.
allowed-tools: [terminal, read_file, write_file, skill_manage]
---

# Pluto Pipeline Orchestration

## When to Use
- Debugging why a specific cron job didn't fire
- Adding a new stage to the pipeline
- Verifying the full chain completed
- Adjusting cron schedules to avoid collisions

## The 45-Stage Pipeline (July 18, 2026 — Pluto Operating Contract + Hourly Jobs Added)

All times AEST (UTC+10). This now includes the Pluto Operating Contract schedules (Daily Discovery, Weekly Search/Content/AI/Blog/Evidence reviews, Monthly Strategy) and two new hourly probes.

All times AEST (UTC+10). **Weekend deliveries:** Saturday 6AM = deep weekly review → Telegram. Sunday 6AM = adversarial/system health (proposed). Mon-Fri 6AM = standard daily briefing. See "Delivery Rules" below.

```
CONTINUOUS (every 5 min only):
  every 5m Mempalace Watcher       5678a363ce3b  mempalace-inputs    deliver: local

DAILY CHAIN:
 1:00 AM Git Repo Sync             c23dc3f73e2d  local (skips stale)    no_agent ✅
 4:00 AM Podcast Ingestion         d4d77c41f6c0  YouTube API + transcript  no_agent ✅ LIVE
 4:55 AM Gmail Ingestor            e5675447ed37  mempalace-inputs    no_agent ✅
 5:02 AM Podcast Insights          67319a9b2606  research_outputs    deliver: local ✅ resumed
 5:05 AM Morning Research          b0de180cec84  pipeline            v2 briefing skill  deliver: local
 5:05 AM Vercel Monitor AM         745ec76c6bf9  AML Hive            no_agent ✅ real health
 5:12 AM Competitor Intel          1a13a2d49682  competitor data     no_agent    deliver: local
 5:10 AM Cross-Chamber Synth       ddceef1f9e5b  synthesizer         deliver: local
 5:15 AM Action Bridge             38c1aa80a5b8  actions             deliver: local
 5:20 AM Briefing Improver         7cc81d64613a  briefing engine     no_agent    deliver: local
 5:25 AM Chamber Refresh           0959371eec17  mempalace feed      no_agent    deliver: local
 5:30 AM Honcho Signal Bridge      pluto_honcho_bridge_daily  Honcho  no_agent ✅ (moved from 6AM)
 6:00 AM ★ Pluto Morning Briefing   c527fed4a1da  ALL IN ONE          deliver: origin 📱 (Mon-Fri ONLY)
 6:10 AM Feedback Loop             59f18c4d557c  feedback            no_agent    deliver: local
 6:15 AM Moonshots Learning         0fb6bf47f704  teach concept       deliver: local
 6:45 AM LinkedIn Ideas             ee4e48300826  content             deliver: local
11:00 AM Skill Extractor            2d33c8f9a89c  proposals           no_agent    deliver: local ✅
 2:00 PM Daily Maintenance          575918cbc242  skill+memory  pro ✅  deliver: local
 5:05 PM Vercel Monitor PM          745ec76c6bf9  AML Hive            no_agent ✅ real health
 9:30 PM Tapease Daily Transactions  114039a7ff9b  CSV export + email   no_agent ✅ NEW Jul 14
11:30 PM Performance Tracker        28bf484caedd  perf data cache     no_agent    deliver: local 🆕
11:55 PM MemPalace Cleanup          0fc5019948be  archive             no_agent    deliver: local
 2:00 AM Weekly Test Report (Wed)   e6b671746eaf  weekly-reports     no_agent    deliver: local

WEEKEND:
Sat 6AM  ★ Saturday Weekly Review   7d24b37a03f2  deep retro + 3 build options  deliver: origin 🆕
Sun 6AM  ★ Adversarial + Portfolio     f8756a2b8403  blind spots + portfolio pulse  deliver: origin 🆕 LIVE June 14

HOURLY PROBES (every hour, 24/7):
  :00   ★ Hourly Version Check               4689311b6ad0  api.amlhive.com.au/version    no_agent ✅ LIVE
  :30   ★ Hourly Attribution Probe            b705c3ee3882  C152 T5.4 journey            no_agent ✅ LIVE

Both scripts use `~/scripts/alert_email.py` shared module for URGENT red HTML email alerts on threshold breach.
See `references/alert-email-pattern.md` for details.

PLUTO OPERATING SCHEDULE (per pluto-amlhive-operating-contract):
  09:00 ★ Daily Discovery Health             756e4e66c320  delivery+sitemap+robots+AI    agent ✅ Mon-Fri
  Tue 10:30 ★ Weekly Search/Content Review     291c2320c81b  one priority packet          agent ✅
  Wed 10:30 ★ Weekly AI-Answer Review           f1b73c7cd48d  controlled prompt set        agent ✅ (fortnightly)
  Thu 11:00 ★ Weekly Metadata/Blog/Social Audit 7059cc6796d6  page audit + blog inventory  agent ✅
  Fri 15:00 ★ Weekly Evidence Summary           f7e6cb145925  operating record              agent ✅
  1st Mon 11:00 ★ Monthly Strategy Review        50eea054f911  three priorities from gaps  agent ✅ (expr 0 11 * * 1 — OR-semantics fix applied 01 Sep; gate filters day ≤ 7)
   1st 00:01 ☿ Month-End Review                   09d6d950544f  month in numbers + RULES TO REFRESH  agent ✅ (bookend chain; runs 00:01 on 1st reviewing just-ended month)
   1st 00:15-03:59 ☿ Start-of-Month Rule Refresh   2f4e89762abb  completion-gated on month-end; refreshes skills/docs on pluto_pr (local only, no push)  agent ✅

FLEET MONITORS (4x daily at 5/11/17/23):
🔵 TapEase (direct AWS)             dbd3cb1b5bd3  EC2+SSM+CW+RDS       no_agent 4x jobs ✅ NEW Jul 8
☁️ AmLHive AWS (direct)            4f4dc2487b98  EC2+Docker+CW+RDS   no_agent 4x jobs ✅ NEW Jul 6

WEEKLY:
Fri 11PM Weekly Review              cc5ca5690d05  reviews             deliver: local
Sat 12AM Weekly Improvements        159702fe072c  auto-fix            deliver: local
Mon+Fri 4AM Hermes Update           4eef20ef0e25  update check        no_agent

=== REMOVED IN PRUNE (June 13, 2026) ===
 fabab82f804a  Podcast KB Ingestion      — YouTube IP-blocked, 12 errors
 79c8ad5b9465  Podcast Chunking           — dead downstream of ingestion
 bcbe9b21e0ab  Voice & Task Processor     — paused, fighting gateway
 6c1e5ffb89d9  A2Square Git Sync Thu      — never executed (0 runs)
 e12213405122  A2Square Git Sync Mon      — never executed (0 runs)
 3cde85223e18  Weekly Research Digest     — superseded by Saturday review
```

## Fleet Monitoring Tracks (AmLHive AWS & TapEase)

Two parallel 4x-daily fleet monitors (5/11/17/23) run outside the main briefing chain and alert via raw SMTP instead of Telegram: **AmLHive AWS** (`amlhive_prod_monitor.py`, account `560205084533`, EC2+Docker+CloudWatch+RDS) and **TapEase** (`tapease_prod_monitor.py`, direct AWS CLI+SSM, replaced a bridge-based monitor on Jul 8, 2026, and also runs the 9:30 PM Daily Transaction Export). See [Fleet Monitoring Tracks](references/fleet-monitoring-tracks.md) for per-job schedules, credentials, the historical TapEase bridge double-email chain, and the related script list.

### Delivery Rules

| Day | 6:00 AM | Delivers | Format |
|-----|---------|----------|--------|
| Mon-Fri | Standard daily briefing | Telegram | News + signals + actions |
| Saturday | **Weekly Review** | Telegram | Retro + perf + repos + 3 build options + improvements |
| Sunday  | **Adversarial + Portfolio Pulse** | Telegram | Blind spots + counter-narratives + portfolio check + one pipeline fix |

**Voiceover preference:** Every major response to Haris should include a TTS voiceover alongside text. Use `text_to_speech` for recommendations, build proposals, and weekly reports. This is preferred over text-only delivery.

**Honcho peer card:** Haris is registered as peer `haris` with 7 profile facts. Use `honcho_profile(peer="haris")` for quick context, `honcho_reasoning` for synthesized answers.

## Performance Tracker Data Flow

`pluto_performance_tracker.py` (11:30 PM daily, no_agent) writes a daily cron-health/error-rate/output-volume snapshot to `~/.hermes/research_outputs/.performance_tracker/{week_id}.json`, which the Saturday Weekly Review (`7d24b37a03f2`) reads to produce trend analysis. See [Performance Tracking](references/performance-tracking.md) for the full architecture, the JSON schema per day/week, and pitfalls (e.g. the tracker doesn't see the 11:55 PM MemPalace Cleanup since it runs after the 11:30 PM snapshot).

## Cross-Check Infrastructure (June 14, 2026)

Two scripts were created to prevent false-positive error reports:

**`~/.hermes/scripts/cross_ref_verify.py`** — Validates a claimed issue against actual cron output before reporting. Usage:
```bash
python3 ~/.hermes/scripts/cross_ref_verify.py <job_id> "<claimed issue>"
```
Exit codes: 0=inconclusive, 1=CONFIRMED (report it), 2=FALSE POSITIVE (suppress).

**`~/.hermes/scripts/cron_verify.py`** — Fleet-wide health scan with false-flag detection. Usage:
```bash
python3 ~/.hermes/scripts/cron_verify.py --issues-only
```
Outputs only crons with real problems + any crons with cosmetic model field confusion.

Both are used by the Saturday Review, Sunday Adversarial Pulse, and Daily Maintenance to validate claims before surfacing them to Haris.

## User Preferences on Problem-Solving

Haris has expressed strong frustration with recurring problems that get band-aids instead of root-cause fixes. When fixing pipeline issues:
1. **Find the root cause** — don't stop at the symptom. A "broken pipe" on an LLM cron might actually be a model timeout, and changing the model fixes the root, not just the symptom.
2. **Verify the fix** — don't just change a config and walk away. Run the job, check the output, confirm it works.
3. **Document what was wrong** — update skills, memory, and reference files so the same issue doesn't get re-flagged next week.
4. **Fix permanently** — if a 300s timeout isn't enough, set it to 3600s. Don't iterate through 3 insufficient values. "Fix it once and for all."

## Known Issues

The pipeline has accumulated a long incident history (broken-pipe recoveries, 401 cascades, false-positive alert fixes, scheduler anomalies, and the standing design rules that came out of them — e.g. `no_agent: true` crons must always exit 0, and their `model` field is cosmetic). Rather than a live to-do list, treat it as a pattern-matching reference: check it whenever a "new" error looks like something that's happened before. See [Pipeline Known Issues — Incident History](references/known-issues-history.md) for the full chronological log.

## Sync API Pipeline Stage (Configuring — env vars set Jun 26)

The AML Hive internal sync API (`POST /internal/sync/{dataset}`) is designed to be called weekly by Hermes cron to refresh `asic-companies`, `asic-business-names`, `acnc-charities`, and `asic-registered-schemes` from data.gov.au/R2 CSV URLs, authenticated via `FLY_IO_SYNCH_API_KEY_PLUTO`. Suggested schedule: Sunday 4:00 AM AEST (2h buffer before the Sunday Adversarial Pulse). See [ASIC Sync API Pipeline](references/asic-sync-api-pipeline.md) for the dataset/env-var table, auth details, and pitfalls (memory footprint, bucket-name typo, 503 if unconfigured).

## Weekly Self-Improvement Pipeline (DREAM MODE)

**Cron:** `159702fe072c`, Saturday 12:00 AM AEST, runs after the Friday weekly review. A 5-phase autonomous pipeline that *implements* fixes rather than just reporting them: (1) Supabase stale-data cleanup, (2) MemPalace health check, (3) skill rewriting/patching, (4) cron/connection rewiring (including the BrokenPipeError wrapper pattern), (5) speculative "dream" proposals for new capabilities. **Rule:** actually DO the fixes — delete bad data, patch stale skills, wrap vulnerable scripts — and only report items that need human review. See [DREAM MODE Pipeline](references/dream-mode-pipeline.md) for the full per-phase procedure, connection queries, and the Week 1/2/3/5 run-history findings (implementation rate improved from 0% to 60%).

## Adding a New Cron Stage

1. Pick a time slot that doesn't overlap (check pipeline schedule)
2. Allow at least 5 minutes buffer after previous stage
3. Create: `hermes cron create --name "Name" --schedule "MM HH * * *" --prompt "..." --deliver origin`
4. Verify: `hermes cron list` (check Next run timezone shows +10:00)
5. Update this skill with the new stage

## Verification Commands
```bash
hermes cron list                              # All cron statuses
hermes cron run JOB_ID                        # Manual trigger test
ls -lt ~/.hermes/research_outputs/ | head -20 # Pipeline output chain
```

## Quick Daily Status (When Haris Asks "What Ran Today?")

When Haris asks what happened with the cron pipeline today, produce a concise answer using this procedure — NOT a full Phase 1-7 audit:

```bash
# 1. Which jobs ran today? (recent output files)
for dir in ~/.hermes/cron/output/*/; do
  name=$(basename "$dir")
  today_files=$(ls "$dir" 2>/dev/null | grep "$(date +%Y-%m-%d)_" | wc -l)
  if [ "$today_files" -gt 0 ]; then
    echo "$name: $today_files files"
  fi
done | sort
```

```bash
# 2. Which jobs errored? (cron job list status)
cat ~/.hermes/cron/jobs.json | python3 -c "
import json, sys
data = json.load(sys.stdin)
for j in data.get('jobs', []):
    lr = j.get('last_run_at', '') or ''
    ls = j.get('last_status', '')
    if lr.startswith('$(date +%Y-%m-%d)') and ls == 'error':
        print(f'FAILED: {j.get(\"name\",\"?\")} ({j.get(\"id\",\"?\")}) — {lr}')
"
```

```bash
# 3. Which crons have NEVER run? (created but never fired)
cat ~/.hermes/cron/jobs.json | python3 -c "
import json, sys
data = json.load(sys.stdin)
for j in data.get('jobs', []):
    if j.get('last_run_at') is None and j.get('enabled', False):
        print(f'NEVER RAN: {j.get(\"name\",\"?\")} ({j.get(\"id\",\"?\")}) — schedule: {j.get(\"schedule\",{}).get(\"expr\",\"?\")}')
"
```

**Keep the answer concise:** List today's runs grouped by status (✅ ran, ❌ failed, ⏳ pending). Flag any "never ran" crons. Only investigate individual error outputs if the user asks for details. Do NOT dump the full cron list or all output files — the user wants a summary.

**⚠️ Pitfall: Do NOT grep cron output files for the word "error."** Cron output files are full of false-positive matches on the literal word "error":
- JSON keys like `"error": "No findings parsed"` (Mempalace Watcher — 17 per file, 50+ files/day)
- Section headers like "Sentry Error Tracking" (Fleet Monitor)
- Normal output like "error handling" or "zero errors" (Moonshots, Research)

Use `hermes cron list` to check `last_status` — it's authoritative and instant. If you must grep output files, use specific patterns: `Traceback`, `FATAL`, `Script timed out`, `401 Unauthorized`. Never `grep -i error` or `grep -i failed` on the full output corpus.

## Pipeline Audit Checklist

When Haris reports missing output, silent failures, or "Hermes is a disappointment," run the full systematic audit: Phase 1 surface status (`hermes cron list`, `crontab -l`), Phase 2 error investigation + classification (broken pipe / 401 / timeout / exit-code-1 / merge-failed), Phase 3 manual script verification, Phase 4 cross-platform path audit (WSL vs Windows paths for ChromaDB, git repos, `.env`), Phase 5 delivery-target check (`deliver: origin` vs `local`), Phase 6 cross-cron error pattern detection (3+ crons with the same error = systemic), and Phase 7 triage into auto-recovering / needs-fix / needs-pipeline-change / systemic categories. Also covers never-executed-cron detection, stale display-name detection, and force-run/batch-trigger detection. See [Pipeline Audit Checklist](references/pipeline-audit-checklist.md) for every phase's exact commands.

## Pitfalls
- Cron "ok" status does not mean output was produced. Always verify output files.
- Cron "ok" status also does NOT mean the output reached the user. `deliver: local` saves to disk only — Haris never sees it. Verify `deliver` field is `origin` for user-facing jobs. `local` is correct only for internal pipeline stages that feed downstream jobs (research → synthesis → actions → briefing chain).
- **CRITICAL: `deliver: local` is the default.** Every new cron job defaults to `local`. If you want Haris to see the output, explicitly set `--deliver origin` on creation, or update existing jobs via `hermes cron update <id> --deliver origin`. On June 12, 2026, 26/29 jobs were `local` — Haris was receiving almost nothing despite the pipeline running perfectly.
- Schedules are AEST, not UTC. `5 5 * * *` = 5:05 AM Sydney time.
- No-agent crons use `deliver: local` — output goes to filesystem.
- The gateway false negative is cosmetic — doesn't affect cron execution.
- Crons created but never firing is a known bug — always test with manual trigger first.
- **Documentation drift:** When a cron is created, rescheduled, or deleted, both this skill AND the schedule listing must be updated. The cross-reference check (`hermes cron list` vs documented schedules) catches ghost crons (in docs but not reality), missing crons (in reality but not docs), and stale times. Run this check after any cron change. See `references/cron-drift-examples.md` for patterns found June 9.
- **`no_agent: true` model field is cosmetic.** This is the #1 trap. When a cron job is `no_agent: true`, the `model` field shown in `cronjob list` output is **dead weight** — it has zero effect on execution. The scheduler does not invoke any LLM. Changing `deepseek-v4-flash` to `deepseek-v4-pro` (or any model) on a `no_agent` cron does nothing. This trap is especially dangerous because `cronjob list` always renders the model column regardless of `no_agent` status, making it look configurable. **Workaround:** Check `jobs.json` directly — `grep '"no_agent": true' ~/.hermes/cron/jobs.json | head -5` to confirm a job is script-only.
- **Broken pipe errors on `no_agent` crons are NOT from the LLM.** If a `no_agent: true` cron shows broken pipe errors, the source is the script itself (subprocess.run pipe closure, stdout flush at exit after cron timeout) or a misattributed error report. DO NOT change the model field — fix the script or adjust the cron timeout. The BrokenPipeError wrapper pattern (try/except at main()) is the standard fix for scripts that exceed the cron scheduler's timeout — see [Known Issues](references/known-issues-history.md) for the full try/except pattern.
- **`cronjob(action='update', script=...)` does NOT auto-set `no_agent: true`.** After updating a job's `script` field via the `cronjob` tool, `jobs.json` still shows `"no_agent": false` — the job keeps running in agent mode with an empty prompt. Manually set `no_agent: true` (and clear `prompt`) in `jobs.json` after any script update, then verify with `grep '"no_agent"' ~/.hermes/cron/jobs.json`. Full fix script in [Known Issues](references/known-issues-history.md).
- **`/tmp`-based Python venvs disappear on WSL reboot.** Any `no_agent` script depending on a `/tmp/*_venv/` silently breaks after a WSL restart (e.g. `podcast_ingestor.py` failing on a missing `/tmp/podcast_venv/bin/yt-dlp`). Detect with `ls /tmp/<venv>/bin/<tool>`; recreate with `python3 -m venv` + reinstall; long-term fix is moving the venv to `~/.hermes/venvs/` which survives reboots. See [Known Issues](references/known-issues-history.md).
- **deliver:origin + No Last run:** Crons with `deliver: origin` that show no "Last run" field may have never executed. On June 9, 6 such crons were identified — all weekly/periodic jobs that missed their last window.
- **Cross-cron error matching (401 cascade):** When 4+ crons fail with the identical error string on the same day, it's a **systemic failure** — credential rotation, token expiry, or provider outage. DO NOT debug each cron individually. Check: (a) API keys/tokens in `.env`, (b) OpenRouter/DeepSeek status pages, (c) provider auth endpoint health. The Jun 10, 2026 cascade affecting Podcast KB, Podcast Insights, LinkedIn Ideas, and Daily Maintenance was a 401 credential failure hitting the Hermes Gateway authentication layer — no individual cron fix would have resolved it.
- **Force-run detection:** Pipeline stages showing `last_run_at` at 10:55 AM when their schedule is 05:00 AM is a force-run/batch-trigger signature. Multiple crons with identical timestamps far from schedule = gateway has auto-retried or queued them outside normal flow. Correlate with gateway restarts, profile switches, or maintenance actions.
- **Podcast crons need 3600s timeout, not 120s.** `podcast_ingestor.py` processes 16 YouTube channels with transcript downloads across Supabase (measured **872 seconds** for a full run with 12 episodes). Previously hit 120s default timeout → `last_status: error` with `Script timed out.` **Fix (June 14, 2026, updated June 15):** `hermes config set cron.script_timeout_seconds 3600` (escalated from 300→900→3600 after measuring 872s runtime + buffer for future channel growth). Current value: 3600s (verified Jun 17). Verify: `grep script_timeout_seconds ~/.hermes/config.yaml`.
- **🆕 `psql -c` ARG_MAX limit on large data (July 4, 2026).** Passing SQL via `psql -c "<sql>"` embeds the query in command-line arguments. Long transcripts (25,000+ chars) in dollar-quoted INSERTs exceed the OS ARG_MAX limit (~128KB) → `[Errno 7] Argument list too long: 'psql'`. **Fix:** Pipe SQL via stdin: `subprocess.run(['psql', ..., '--no-psqlrc'], input=sql, ...)`. See `references/psql-stdin-piping.md` for full pattern, verification, and cross-script applicability. This applies to ANY `no_agent` script using `psql -c` with variable-length data.
- **🆕 Hermes update check — git vs pip trap (July 10, 2026).** `hermes_update_check.sh` was using `pip list --outdated | grep hermes` and `pip install --upgrade hermes-agent` — but Hermes is installed via git, not PyPI. The script silently reported "No update found" while Hermes was 104 commits behind. **Fix:** Use `hermes update --check` (checks git remote) and `hermes update` (pulls from git). The pip approach ONLY works for PyPI-installed Hermes; git-installed instances need the CLI's built-in git update mechanism. **Detection:** `hermes --version` shows "Update available: N commits behind" but `hermes_update_check.sh` output says "No update found" → script is using wrong method. **Verification:** `bash -n ~/.hermes/scripts/hermes_update_check.sh` (syntax), then `hermes update --check` to confirm detection works. **Fixed script:** Now uses `hermes update --check` with grep for "behind" to detect pending updates, and `hermes update` to apply them. Next run (Mon/Fri 4AM) will auto-detect and apply.

## Reference Files
- `references/alert-email-pattern.md` — Shared `alert_email.py` module for URGENT red HTML email alerts, used by the two hourly probes
- `references/fleet-monitoring-tracks.md` — Full AmLHive AWS + TapEase fleet monitor schedules, credentials, and the historical TapEase bridge double-email chain
- `references/known-issues-history.md` — Full chronological incident log: broken-pipe recoveries, 401 cascades, false-positive fixes, scheduler anomalies, and the design rules/pitfalls each one produced
- `references/asic-sync-api-pipeline.md` — AML Hive internal sync API dataset/env-var table, auth, and pitfalls
- `references/pipeline-audit-checklist.md` — Full 7-phase audit procedure with exact commands for each phase
- `references/cron-drift-examples.md` — Patterns found June 9: ghost crons, missing crons, stale times
- `references/competitor-intel-operations.md` — Competitor intel pipeline operations
- `references/dream-mode-pipeline.md` — Full 5-phase DREAM MODE pipeline (weekly self-improvement): Supabase cleanup, MemPalace update, skill rewriting, connection rewiring, speculative dreaming, plus Week 1-5 run history
- `references/supabase-stale-data-queries.md` — All 6 stale-data detection queries used by DREAM MODE Phase 1 (Supabase pgvector cleanup), combined health check, safe-delete rules, weekly ingestion audit query, and the `created_at`→`published_date` column-name pitfall
- `references/performance-tracking.md` — Daily perf snapshot pipeline → Saturday weekly review data
- `references/youtube-data-api-credentials.md` — YouTube Data API v3 setup, quota, script wrapper, env file placement (both WSL and Windows `.env`), and fallback behavior
- `references/recovery-script-gaps.md` — Startup recovery script gaps: discovered June 14 — Saturday Weekly Review (`7d24b37a03f2`) not caught by startup-recovery.sh after WSL sleep. Detection and mitigation steps.
- `references/psql-stdin-piping.md` — Pattern for piping SQL to psql via stdin instead of `-c` to avoid ARG_MAX limit on large data (transcripts, batch inserts). Discovered July 4, 2026 fixing podcast ingestion.
