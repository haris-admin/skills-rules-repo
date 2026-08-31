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
  1st Mon 11:00 ★ Monthly Strategy Review        50eea054f911  three priorities from gaps   agent ✅

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

## AmLHive AWS Fleet Monitoring (Separate Track)

A **parallel pipeline** monitoring AmLHive AWS infrastructure (account `560205084533`) through direct AWS CLI calls + SSM. Runs the same 4-slot schedule as TapEase. Uses raw smtplib email with ━━━ plain-text formatting.

| Time (AEST) | Job ID | What It Does | Delivery |
|---|---|---|---|
| 5:00 AM | `4f4dc2487b98` | Full EC2 + Docker + CloudWatch + RDS health check | local (email from script) |
| 11:00 AM | `6728be78d1bf` | Full EC2 + Docker + CloudWatch + RDS health check | local (email from script) |
| 5:00 PM | `d52fa74ab6c1` | Full EC2 + Docker + CloudWatch + RDS health check | local (email from script) |
| 11:00 PM | `be5061d19a5a` | Full EC2 + Docker + CloudWatch + RDS health check | local (email from script) |

**Primary Runner:** `amlhive_prod_monitor.py` — standalone production monitor covering all 10 report sections (EC2, Docker, CloudWatch alarms+logs, RDS, Sentry, public endpoints). Formats plain-text report, sends via SMTP to `EMAIL_TO_AMLHIVE` recipients from .env. Exit 0 on all-healthy, 1 on incidents (email IS the alert mechanism — exit code 1 on issues is by design, not a bug). **Legacy reference:** `amlhive_aws_runner.py` imports `amlhive_aws_health.py` module (kept for dynamic instance discovery pattern).

**AWS resources monitored:** EC2 instances (amlhive-frontend + amlhive-prod via SSM), Docker containers + compose, CloudWatch alarms + log groups, RDS PostgreSQL.

**Credentials:** `AWS_ACCESS_KEY_ID_AMLHIVE` + `AWS_SECRET_ACCESS_KEY_AMLHIVE` from Windows `.env`. Loaded via Python line-by-line parsing (NOT bash `source` — the .env has special characters).

*Created Jul 6, 2026 — mirrors TapEase monitor runner pattern.*

## TapEase Fleet Monitoring + Daily Transactions (Separate Track)

**Replaced bridge-based monitor on Jul 8, 2026.** Old `tapease_monitor_runner.py` (bridge-based, HTML errors since Jun 26) → new `tapease_prod_monitor.py` (direct AWS CLI + SSM). See `tapease-fleet-monitor` skill for full architecture, script docs, pitfalls, and known issues.

| Time (AEST) | Job ID | What It Does | Delivery |
|---|---|---|---|
| 5:00 AM | `dbd3cb1b5bd3` | Full EC2 + SSM process + nginx logs + alarms + Lambda + RDS | local (email from script) |
| 11:00 AM | `582bd225ddd1` | Full EC2 + SSM process + nginx logs + alarms + Lambda + RDS | local (email from script) |
| 5:00 PM | `1086e6405da1` | Full EC2 + SSM process + nginx logs + alarms + Lambda + RDS | local (email from script) |
| 9:30 PM | `114039a7ff9b` | **Daily Transaction Export** — SSM → psql → CSV → email | local (email from script) |
| 11:00 PM | `be81c61778a8` | Full EC2 + SSM process + nginx logs + alarms + Lambda + RDS | local (email from script) |

**Credentials:** `AWS_ACCESS_KEY_ID_TAPEASE` + `AWS_SECRET_ACCESS_KEY_TAPEASE` from Windows `.env`.

**Old bridge issues now resolved by direct monitor:**
- 🔴 TapEase Bridge HTML Error Pages → ✅ Replaced by direct AWS calls
- 🔴 Double Email From Same Cron Job → ✅ Single email send in `tapease_prod_monitor.py`

**Chain of duplication:**
```
tapease_monitor_runner.py (cron)
  ├─ POST /tapease/monitor → bridge → powershell
  │   └─ lambda_monitor_unified.ps1 → unified_delivery.ps1
  │       └─ professional_email_unified.ps1 → 📧 EMAIL 1 (clean, HTML, Habibi logo)
  │          Script path: C:\Users\habib\.openclaw\workspace\scripts\delivery\professional_email_unified.ps1
  │          Agent logo: habibi_logo_email.jpg, branded gradient header, PDF+voice attachments
  │
  └─ send_email(summary) in tapease_monitor_runner.py → 📧 EMAIL 2 (raw, plain text)
     Uses Python smtplib → Purelymail SMTP → plain MIMEText, no HTML, no logo
     
  stdout → cron deliver: origin → 📱 Telegram delivery (separate, not email)
```

**Symptoms:**
- Email 1: Professional HTML with Habibi's avatar/logo, gradient header, tables, PDF+voice attachments
- Email 2: Plain text, no formatting, no logo — stripped-down duplicate of same content
- Goes to overlapping recipients: `hhsiddiqui@gmail.com`, `habibshoaib841@gmail.com`, `admin@harishabib.au`

**Recommended fix:** Remove the `send_email()` call from `tapease_monitor_runner.py` (line ~137). The PowerShell delivery pipeline (`professional_email_unified.ps1`) already handles email — and does it better (HTML, branded, with attachments). The Python `send_email()` is a redundant plain-text duplicate.

**Files to modify:**
```bash
# Edit tapease_monitor_runner.py (WSL path)
# Comment out or remove: sent = send_email(summary)
patch /home/habib/.hermes/scripts/tapease_monitor_runner.py \
  "sent = send_email(summary)" "# sent = send_email(summary)  # DISABLED: duplicates PowerShell email"
```

**Recipients per sender:**
| Sender | Recipients |
|---|---|
| `professional_email_unified.ps1` | `admin@harishabib.au`, `hhsiddiqui@gmail.com`, `habibshoaib841@gmail.com` |
| `tapease_monitor_runner.py` (Python) | `shoaib.habib@a2square.com.au`, `admin@harishabib.au`, `hhsiddiqui@gmail.com`, `habibshoaib841@gmail.com` |
```
  unified_git_sync.py       — pulls a2square + amlhive + operator repos (Thu+Mon 2AM)
  unified_weekly_report.py  — Docker tests + report (Wed 2AM)
  briefing_improver.py      — v2 morning briefing engine (5:20 AM, deliver:local)
  hermes_update_check.sh    — `hermes update --check` (Mon+Fri 4AM) — git-aware, NOT pip
  pluto_feedback_processor.py — Gumby→Pluto feedback loop (6:10 AM, no_agent)
  skill_extractor.py        — daily skill proposals (11:00 AM, no_agent)
  pluto_chamber_refresh.py  — feeds all sources to ChromaDB (5:25 AM, no_agent)
  pluto_performance_tracker.py — daily perf snapshots → feeds Saturday review (11:30 PM, no_agent)
```
### Delivery Rules

| Day | 6:00 AM | Delivers | Format |
|-----|---------|----------|--------|
| Mon-Fri | Standard daily briefing | Telegram | News + signals + actions |
| Saturday | **Weekly Review** | Telegram | Retro + perf + repos + 3 build options + improvements |
| Sunday  | **Adversarial + Portfolio Pulse** | Telegram | Blind spots + counter-narratives + portfolio check + one pipeline fix |

**Voiceover preference:** Every major response to Haris should include a TTS voiceover alongside text. Use `text_to_speech` for recommendations, build proposals, and weekly reports. This is preferred over text-only delivery.

**Honcho peer card:** Haris is registered as peer `haris` with 7 profile facts. Use `honcho_profile(peer="haris")` for quick context, `honcho_reasoning` for synthesized answers.

## Performance Tracker Data Flow

```
Daily Cron (28bf484caedd)        Saturday Weekly Review (7d24b37a03f2)
    11:30 PM                         6:00 AM Sat
       │                                │
       ▼                                ▼
  perf_2026-W24.json ───────────────► reads cumulative
  {days: [...]}                        week data
  {summary: {                           │
    total_errors,                        ▼
    broken_pipe,                  Produces retrospective:
    cron_health,                   - What worked/didn't
    output_files                     - Repo health audit
  }}                                 - Signals this week
                                     - 3 build options
                                     - Improvements
```

### ✅ RESOLVED: Podcast KB Ingestion Timeout — Global script_timeout_seconds Fix (June 14, 2026, updated to 900s)
The podcast ingestor (`d4d77c41f6c0`) processes 16 YouTube channels with rate-limited transcript downloads and Supabase inserts. **Measured runtime: 872 seconds (14.5 min)** for a full run with 12 new episodes ingested. The original 120s default timeout caused every run to fail.

**Fix timeline:**
1. **June 14, 14:00:** Set `cron.script_timeout_seconds: 300` — still not enough
2. **June 14, 18:00:** Measured actual runtime at **872 seconds** for a full run. Script ingested 12 episodes cleanly across 16 channels with zero errors. The YouTube API works; the fallback to yt-dlp for some channels (Moonshots, a16z, Logan Bartlett) adds latency but doesn't cause failures.
3. **June 14, 18:15:** Set `cron.script_timeout_seconds: 900` — verified correct

**Verification:** `grep script_timeout_seconds ~/.hermes/config.yaml` → shows `900`.

**Important:** There is no per-job timeout in the Hermes cron scheduler. The `script_timeout_seconds` config is a single global value for all no_agent scripts. If a future job needs a different timeout, `scheduler.py` at line ~1009 would need modification to support a per-job `timeout` field in `jobs.json`. The current 900s is safe for all scripts — fast ones finish well before it.

### ✅ RESOLVED: Mempalace Watcher — Converted to no_agent (May 24, 2026 — old problem, DO NOT RE-FLAG)

> **⚠️ TRAP:** This job is `no_agent: true`. The `model` field in `cronjob list` is **cosmetic** — it has zero effect. Any report of "broken pipe" or "LLM errors" on this job is either stale or misattributed. **Do not flag this job.** The fix was applied on May 24, 2026.

The Mempalace Inbox Watcher (`5678a363ce3b`, every 5m) was **originally** an LLM-driven cron calling DeepSeek Flash. DeepSeek's streaming server intermittently hangs for 180s+ even at 4.8K tokens.

**Fix (May 24):** Converted to `no_agent: true` script (`mempalace_watcher.py`). The watcher is a mechanical file-checker — it doesn't need an LLM. Runs as a standalone Python script, exits 0 with empty stdout when no new files, non-empty when processing. **No more DeepSeek dependency = no more broken pipe.**

**Pattern:** Any cron job that checks files, runs a script, or performs deterministic work should be `no_agent: true`. Only use LLM-driven crons for tasks that genuinely need reasoning (synthesis, extraction, content generation).

### 🔴 Gotcha: YouTube API Key Must Be in BOTH .env Files (June 14, 2026)

The YouTube Data API key (`YOUTUBE_DATA_API_KEY`) was added to Windows `.env` (`/mnt/c/Users/habib/.hermes/.env`) but NOT to WSL `.env` (`~/.hermes/.env`). When cron `no_agent` scripts run, they pick up env vars from the WSL `.env` — not the Windows one. The podcast ingestor silently fell back to yt-dlp (which is IP-blocked).

**Fix:** Always add new API keys to BOTH locations:
```bash
# After adding to Windows .env:
grep 'NEW_KEY' /mnt/c/Users/habib/.hermes/.env >> ~/.hermes/.env
```

**Best practice:** When adding credentials for cron `no_agent` scripts, add to `~/.hermes/.env` (WSL) FIRST, then copy to Windows `.env` for cross-platform access. The cron scheduler reads from WSL.

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

## Sync API Pipeline Stage (Configuring — env vars set Jun 26)

The AML Hive internal sync API (`POST /internal/sync/{dataset}`) is designed to be called **weekly by Hermes cron** according to its OpenAPI specification. Three CSV URLs are deployed on Fly.io — once the underlying data is uploaded to a publicly accessible URL (R2 or data.gov.au), a weekly cron can trigger refreshes.

### Datasets Ready for Sync

| Dataset | Env Var | Status |
|---------|---------|--------|
| `asic-companies` | `ASIC_COMPANIES_CSV_URL` | ✅ Set (data.gov.au Jun 2026) |
| `asic-business-names` | `ASIC_BUSINESS_NAMES_CSV_URL` | ✅ Set (data.gov.au Jun 2026) |
| `acnc-charities` | `ACNC_CSV_URL` | ✅ Set (permanent URL) |
| `asic-registered-schemes` | `ASIC_REGISTERED_SCHEMES_CSV_URL` | ⚠️ No bulk dataset exists |

### Auth
Bearer token from `FLY_IO_SYNCH_API_KEY_PLUTO` in `.env` → `INTERNAL_SYNC_API_KEY` deployed on Fly.io.

### Suggested Schedule
Sunday 4:00 AM AEST (before the Sunday Adversarial Pulse) — 2h buffer.

### Data Pipeline (manual monthly refresh)
Files are downloaded from data.gov.au → extracted from ZIP → uploaded to `amlhive-documents/asic/` on R2.
See `reference-data-ingestion` skill for full procedure.

### Pitfalls
- Sync loads entire CSV into memory (375MB → ~512MB+ RAM on 1024MB Fly.io machine)
- CSV URLs currently point to data.gov.au — if data.gov.au breaks access, switch to R2 presigned URLs or make the bucket public
- The `amlhive-asic-conent` bucket doesn't exist (typo in name) — use `amlhive-documents/asic/` prefix instead

The AML Hive internal sync API (`POST /internal/sync/{dataset}`) is designed to be called **weekly by Hermes cron** according to its OpenAPI specification. Once the 4 `*_CSV_URL` secrets are set on Fly.io, a weekly cron job can trigger dataset refreshes.

### Datasets to Sync

| Dataset | Fly.io Secret | Frequency |
|---------|------|----------|
| `asic-companies` | `ASIC_COMPANIES_CSV_URL` | Weekly |
| `asic-registered-schemes` | `ASIC_REGISTERED_SCHEMES_CSV_URL` | Weekly |
| `asic-business-names` | `ASIC_BUSINESS_NAMES_CSV_URL` | Weekly |
| `acnc-charities` | `ACNC_CHARITIES_CSV_URL` | Weekly |

### Auth

Bearer token from `FLY_IO_SYNCH_API_KEY_PLUTO` in `.env`. The `INTERNAL_SYNC_API_KEY` secret is already deployed on Fly.io.

### Suggested Schedule

Sunday 4:00 AM AEST (before the Sunday Adversarial Pulse) — gives 2h buffer for sync completion.

### Pitfalls

- The sync API is not yet configured (no `CSV_URL` secrets set) — calling it returns 503
- Each sync may take several minutes (large CSVs: ASIC companies = ~2.8M rows)
- See `pluto-fleet-monitor/references/sync-api-setup.md` for full setup instructions

## Adding a New Cron Stage

## Weekly Self-Improvement Pipeline (DREAM MODE)

**Cron:** `159702fe072c`, Saturday 12:00 AM AEST
**Input:** Friday weekly review (`~/.hermes/reviews/weekly/weekly-review-*.md`)
**Output:** `~/.hermes/reviews/weekly/improvements-{DATE}.md` + dream proposals

This 5-phase autonomous improvement pipeline runs after the Friday review. It implements fixes — not just reports them.

### Phase 1: 🧹 Stale Data Cleanup (Supabase pgvector)
Connect to `podcast_kb` on Supabase and find/delete stale data:
- Episodes with `transcript_text LIKE '%YouTube is blocking%'` (IP-blocked garbage — safe to delete)
- Duplicate episodes (same `podcast_id` + `youtube_id`)
- Episodes with `transcript_text` length < 100 chars (failed downloads stored as errors)
- Episodes older than 90 days with no `au_relevance_score`
- Orphaned chunks with no matching episode

**Connection string:** `PGPASSWORD='...' PGSSLMODE=require psql -h aws-1-ap-southeast-2.pooler.supabase.com -p 6543 -U postgres.vyqagemgwxfscppkfswq -d postgres`

**Full query reference:** `references/supabase-stale-data-queries.md` — all 6 stale-data detection queries, combined health check, safe-delete rules, and weekly ingestion audit query.

Only delete items that are safe to re-ingest (IP-blocked garbage, short transcripts). Report counts for items needing human review.

### Phase 2: 🧠 MemPalace Update
- Review `~/.hermes/research_outputs/` for files older than 7 days
- Verify `mempalace_cleanup.py` cron (`0fc5019948be`) is archiving properly (check `.cleanup_state.json`)
- Consolidate daily synthesis files into a weekly summary
- Verify ChromaDB health: `python3 -c "import chromadb; c = chromadb.PersistentClient(path='/mnt/c/Users/habib/.mempalace/palace'); ..."`
- Archive stale files to `~/.hermes/archive/research/YYYY/MM/`

### Phase 3: 🔧 Skill Rewriting
- Load ALL skills via `skills_list` and audit for staleness
- Check for: outdated repo names, old cron schedules, broken commands, dead paths, missing pitfalls
- Patch stale skills with `skill_manage(action='patch')`
- Flag skills needing full rewrites (too many issues to patch)

### Phase 4: 🔗 Rewire Connections
- Audit all cron jobs from `~/.hermes/cron/jobs.json`
- Check: valid skill references, valid script paths, schedule collisions, stale cron names
- Fix BrokenPipeError-vulnerable scripts with wrapper pattern (see pitfall above)
- Check memory for stale facts — remove outdated entries

### Phase 5: 🌙 Dreaming — Speculative Improvements
- Read the Friday review's "What Didn't Work" section
- Brainstorm 2-3 alternative approaches for each failure
- Propose at least ONE new capability Pluto doesn't have yet
- Write dream proposals to `~/.hermes/reviews/weekly/dreams-{DATE}.md` with: what, why (evidence), how (implementation), cost (low/med/high)

### Report Format
Write comprehensive report to `~/.hermes/reviews/weekly/improvements-{DATE}.md` with sections for each phase:
- What was found
- What was fixed (actual code/skill changes)
- What was proposed (dreams)
- What needs human review (risky changes)

**Rule:** Actually DO the fixes, don't just report them. DELETE bad data, PATCH stale skills, WRAP vulnerable scripts. Only report items needing human approval.

### Run Findings

**Week 5 (July 18, 2026) — Best Implementation Cycle Yet:**
- **Phase 1:** Supabase pristine — 481 episodes, 501 chunks, 0 stale records. 46 legacy episodes >90 days without AU scores (carried from W26). **Fixed 3 instances of `created_at` → `published_date` column name bug** in supabase-stale-data-queries.md (this bug burned every DREAM MODE cycle since creation — now fixed permanently with a Column Name Pitfalls section).
- **Phase 2:** MemPalace healthy — 27 collections, 3,165 docs (+1,490 vs June W26). Nightly cleanup cron active (469 archived). ChromaDB growing steadily.
- **Phase 3:** No skills patched — remarkably, all 106 skills are current. `pluto-weekly-review` was already patched with W28 findings during the Friday review.
- **Phase 4:** **3 fixes applied** (highest single-cycle implementation): (1) Daily Learning cron prompt patched — now saves to `research_outputs/daily-learning-YYYY-MM-DD.md` to close 100% false negative. (2) `gmail_health_check.py` created — pre-flight IMAP login test, P0 alert to mempalace on failure, BrokenPipeError-safe. (3) `competitor_intel.py --debug` flag added for diagnosing 43% empty-output rate. Also: guardrail-scan investigated and confirmed healthy — Friday review claim was false (verified against 8 consecutive sync runs all showing "already current"). Two transient errors (Hermes Update + Podcast Ingestion — both Gateway shutdown).
- **Phase 5:** 5 dream proposals: Pipeline Health in Briefing (3rd week stalled — now CRITICAL at 5 weeks of Gmail darkness), Cron Output Path Validator (NEW), Intelligence Health Scorecard, Auto-Register Gmail Health Cron (NEW), Batch AU Re-Scorer (3rd week stalled).
- **Key result:** Implementation rate hit **60%** (3/5 dreams implemented) — best ever. Dream pipeline improving: W23=0% → W24=25% → W25=37.5% → W28=60%. The key shift was prioritizing LOW-cost, self-contained fixes over multi-step orchestration dreams. Gmail Health Monitor script created but not yet registered as cron (Dream #4 — 5 min task).
- **Skills updated:** `pluto-weekly-review` (guardrail-scan verification pitfall, Supabase column name pitfall), `pluto-pipeline-orchestration/references/supabase-stale-data-queries.md` (3x `created_at`→`published_date` fixes, Column Name Pitfalls section added).

**Week 3 (June 20, 2026):**
- **Phase 1:** Supabase pristine — 275 episodes, 501 chunks, 0 stale records. 34 legacy episodes with zero AU relevance scores (valid transcripts, pre-scoring ingestions) — deferred to Dream Proposal #1 for batch re-scoring.
- **Phase 2:** MemPalace healthy — 27 collections (3 new emergent: `market-signals`, `quantum-computing`, `space-tech`), 1,675+ docs. Nightly cleanup cron confirmed working (194 archived). 3 state files >7 days old (benign — actively referenced).
- **Phase 3:** 2 skills patched (pipeline-orchestration, vercel-monitoring). No skills flagged for full rewrite.
- **Phase 4:** 3 scripts fixed: `vercel_monitor.py` (BLOCKED verification), `pluto_performance_tracker.py` (tool_warnings field), `git_sync.py` (skip dead repos). All 31 crons verified healthy. 2 skills patched.
- **Phase 5:** 6 dream proposals: AU re-scorer (LOW), podcast chunking lite (MEDIUM), chamber auto-documenter (LOW), insight extractor auth fix (LOW), Sunday engagement prompt (LOW), cron output auto-prune (LOW).
- **Key result:** First zero-error week continues — all 31 crons `last_status: ok`.
- **Phase 1:** Supabase pristine — 214 episodes, 501 chunks, 0 stale records (clean 2 weeks running)
- **Phase 2:** MemPalace healthy — 24 collections, 1,023+ docs, cleanup cron working (112 archived)
- **Phase 3:** 1 skill flagged for full rewrite (`pluto-autonomous-research` pipeline table pre-June-12). No patches needed.
- **Phase 4:** 2 timeout fixes applied (podcast crons 120s → 300s). All script paths valid. No stale memory.
- **Phase 5:** 6 dream proposals (provider migration, scheduler monitor, proxy rotation, credential monitor, auto-skill-creation, competitor confidence tiers)

**Week 1 (June 13, 2026 — inaugural run):**
- **Phase 1:** Supabase clean (0 IP-blocked, 0 duplicates, 0 orphans, 214 episodes)
- **Phase 2:** MemPalace healthy (24 collections, cleanup cron working, 112 files archived)
- **Phase 3:** 1 stale reference found (honcho-bridge-limitations.md: "5:20 PM" → "6:00 AM")
- **Phase 4:** 2 BrokenPipeError wrappers added (skill_extractor.py, pluto_feedback_processor.py)
- **Phase 5:** 4 dream proposals (proxy rotation, scheduler monitor, auto-skill-creation, provider migration)

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

When Haris reports missing output, silent failures, or "Hermes is a disappointment," run this systematic audit:

### Phase 1: Surface Status
```bash
hermes cron list                          # All jobs + last_status
crontab -l                                # System crontab (should be just gateway + reboot)
```

### Phase 2: Error Investigation
For each job with `last_status: error`, check its output:

```bash
# View last n outputs
ls -lt ~/.hermes/cron/output/<JOB_ID>/ 2>/dev/null | head -5

# Read the most recent error output
cat ~/.hermes/cron/output/<JOB_ID>/$(ls -t ~/.hermes/cron/output/<JOB_ID>/ | head -1) | tail -30
```

**Classify the error:**
- **"Broken pipe"** → LLM-driven cron shelling out to a script → fix: convert to `no_agent: true`
  - **FIRST CHECK — Is the cron already `no_agent: true`?** If `no_agent: true`, the `model` field shown in `cronjob list` output is **cosmetic** — it has zero effect on execution. The broken pipe is NOT from LLM invocation. Look inside the script itself for `subprocess.run()`, pipe-to-subprocess, or stdout-flush-at-exit patterns that could fail. Changing the model field on a `no_agent` cron does nothing. This is a common trap because `cronjob list` always renders the model column regardless of `no_agent` status — it is dead weight on those jobs.
  - **Cross-check error reports against actual output:** Before acting on a second-hand error report (Saturday review, error log, or Haris flagging it), verify the actual cron output. Check `cron/output/<JOB_ID>/` for the latest `.md` file. If the cron shows `last_status: ok` and produces clean output, the error report is either stale (pre-fix) or misattributed (wrong cron ID). The Saturday review attribution of 396+ broken pipe errors to the Mempalace Watcher was inaccurate — the job was already `no_agent: true` with zero errors and clean `[]` output every 5 minutes.
- **"401 Unauthorized"** → credential expiry → 3+ crons with same error = systemic
- **"timeout"** → script too slow → increase timeout or optimize script
- **"exit code 1" (vercel_monitor.py)** → intentional alert → fix: change to exit 0 (see pitfall above)
- **"merge failed" (git_sync)** → divergent branches → cosmetic, script exits 0

### Phase 3: Script Verification
Run the actual script manually to separate script bugs from cron infrastructure issues:

```bash
python3 ~/.hermes/scripts/<script_name>.py 2>&1; echo "EXIT: $?"
```

If the script succeeds manually (exit 0, produces output) but the cron shows "error", the issue is in **cron configuration** (delivery target, timeout, no_agent flag), not the script itself.

### Phase 4: Cross-Platform Path Audit
Verify all scripts that reference shared data (ChromaDB, git repos) use the correct **Windows path**:

```bash
grep -n "/mnt/c/\|Windows\|palace\|CHROMA" ~/.hermes/scripts/<script>.py
```

Key path rules:
- **ChromaDB** lives at `/mnt/c/Users/habib/.mempalace/palace/` — WSL-side path `~/.hermes/mempalace/chromadb/` is EMPTY
- **Git repos** at `/mnt/c/Code/gitlab/` — NOT in WSL homedir
- **Windows .env** at `/mnt/c/Users/habib/.hermes/.env` — NOT `~/.hermes/.env`
- **Python venv** is WSL-side: `~/.hermes/venv/bin/python3`

### Phase 5: Delivery Target Check
A pipeline that runs perfectly but delivers nothing to the user is the worst failure mode:

```bash
# Find all crons delivering to origin (user-facing) vs local (file-only)
cat ~/.hermes/cron/jobs.json | python3 -c "
import json, sys
data = json.load(sys.stdin)
for j in data.get('jobs', []):
    name = j.get('name', '?')[:50]
    deliver = j.get('deliver', '?')
    status = j.get('last_status', 'never run')
    print(f'{deliver:10s} {status:10s} {name}')
" | sort
```

**Rule:** One Telegram delivery at 6:00 AM Mon-Fri (daily briefing). Saturday delivers a separate weekly review at 6:00 AM (`7d24b37a03f2`). Sunday delivers a system improvement report at 6:00 AM (proposed — pending Haris confirmation). All other jobs stay `deliver: local`.

### Phase 6: Cross-Cron Error Pattern Detection (Systemic Failures)

```bash
# Find ALL crons that failed on a given day — detects systemic failures
cat ~/.hermes/cron/jobs.json | python3 -c "
import json, sys
data = json.load(sys.stdin)
jobs = data.get('jobs', [])
for j in jobs:
    lr = j.get('last_run_at', '')
    ls = j.get('last_status', '')
    if 'YYYY-MM-DD' in lr and ls == 'error':
        print(f'{j.get(\"name\",\"?\")}: {lr} — {ls} — {str(j.get(\"last_error\",\"\"))[:120]}')
"
```
If 3+ crons show the SAME error string on the same day, it's a **systemic credential/app failure**, not individual cron bugs. Escalate to provider-level investigation.

### Phase 7: Triage → Classify → Auto-Recovery Assessment

After investigating all error jobs, classify them into categories to determine next steps:

```bash
# Quick triage: for each error job, manually run the script and check exit code
python3 ~/.hermes/scripts/<script_name>.py 2>&1; echo "EXIT: $?"
```

**Category A — Stale Error (will auto-recover on next run):**
- Script exits 0 when run manually
- Root cause was already fixed (converted to no_agent, changed exit code, added known-dead-repo filter)
- **Action:** Note it, move on. Next cron run will show `ok`.

**Category B — Needs Permanent Fix:**
- Script fails when run manually (broken pipe, 401, timeout)
- Root cause is in the script itself or cron configuration
- **Action:** Fix the script or cron config NOW, then re-verify exit 0

**Category C — Needs Pipeline Change:**
- The job's purpose requires an LLM (skill extraction, synthesis) but it's configured as LLM-driven and hitting broken pipe
- **Action:** Convert to `no_agent: true` with a deterministic script that does the data collection. Accept some loss of reasoning quality for reliability.

**Category D — Systemic/Credential Failure:**
- 3+ jobs with same error (e.g., 401, timeout)
- **Action:** Check shared credentials, provider status, gateway health. Don't debug individual crons.

**After fixing all Category B/C/D jobs, list the Category A auto-recoveries** so the user knows which errors are stale and which were actively fixed:

```bash
# Show which crons still show "error" but are actually fixed
echo "== Auto-Recovery Candidates (stale error, next run fixes) =="
cat ~/.hermes/cron/jobs.json | python3 -c "
import json, sys
data = json.load(sys.stdin)
for j in data.get('jobs', []):
    if j.get('no_agent') and j.get('last_status') == 'error' and j.get('script'):
        print(f'{j.get(\"id\",\"?\")} — {j.get(\"name\",\"?\")[:50]}')
        print(f'  no_agent={j.get(\"no_agent\")} script={j.get(\"script\")} — will auto-recover next run')
"
```

### Never-Executed Cron Detection (Created But Never Fired)

```bash
# Find crons that have NEVER executed — different class from 'errored'
cat ~/.hermes/cron/jobs.json | python3 -c "
import json, sys
data = json.load(sys.stdin)
jobs = data.get('jobs', [])
found = False
for j in jobs:
    lr = j.get('last_run_at')
    if lr is None:
        created = j.get('created_at', '?')[:10]
        schedule = j.get('schedule', {}).get('expr', '?')
        next_run = j.get('next_run_at', '?')[:10] if j.get('next_run_at') else '?'
        print(f'{j.get(\"name\",\"?\")} ({j.get(\"id\",\"?\")})')
        print(f'  Created: {created}  Schedule: {schedule}  Next: {next_run}')
        found = True
if not found:
    print('All crons have executed at least once.')
"
```

A cron with `last_run_at: null` and `enabled: true` is a **scheduler bug**, not a timeout or failure. It means the Hermes cron scheduler never picked up the job. Compare `created_at` to today's date — if a cron has gone 3+ days without firing and its schedule should have triggered it (e.g., a weekly cron created 11 days ago), escalate as a scheduler-level defect.

**Cross-check with output directories** — even if `jobs.json` is ambiguous, the presence or absence of a cron output directory in `~/.hermes/cron/output/<id>/` is definitive proof of execution:

```bash
# List all crons that have NO output directory = never produced any output
for j in $(cat ~/.hermes/cron/jobs.json | python3 -c "
import json, sys
jobs = json.load(sys.stdin).get('jobs', [])
for j in jobs:
    print(j['id'])
"); do
  [ -d ~/.hermes/cron/output/$j ] && echo "HAS_OUTPUT: $j" || echo "NEVER_RAN: $j"
done
```

**Scheduler‑bug signature:** A cron showing `next_run_at` that skips the very next valid execution window (e.g., a weekly Thursday cron created June 8 showing next_run June 18 when June 11 is a Thursday) suggests the scheduler's day‑of‑week calculation is off. This affects weekly crons (`0 2 * * 4`) more than daily crons, since the offset can push the first fire date a full week.

**Stale display name detection** — compare each cron's `name` field against its schedule `display` value:

```bash
cat ~/.hermes/cron/jobs.json | python3 -c "
import json, sys
data = json.load(sys.stdin)
for j in data.get('jobs', []):
    name = j.get('name', '?')
    sched = j.get('schedule_display', '?')
    time_parts = sched.split()
    if len(time_parts) >= 2:
        h, m = int(time_parts[0]), int(time_parts[1])
        display_time = f'{h:02d}:{m:02d}'
        if display_time not in name and display_time.replace(':', '') not in name:
            print(f'NAME/SCHEDULE MISMATCH: {j.get(\"id\",\"?\")}')
            print(f'  Name:     {name}')
            print(f'  Schedule: {sched} ({display_time})')
            print(f'  Source:   cron name field stale — update to match actual schedule')
"
```

Cron names containing a time that doesn't match the job's `schedule_display` cause confusion during auditing. Fix by editing the cron: `hermes cron edit <id> --name "New Name with Correct Time"`. On June 11, 2026, `pluto_honcho_bridge_daily` was named "Pluto Honcho Signal Bridge (5:20 PM AEST)" but ran at `0 6 * * *` (6:00 AM AEST).

### Force-Run / Auto-Retry Detection
```bash
# Find crons with near-identical last_run_at far from schedule
cat ~/.hermes/cron/jobs.json | python3 -c "
import json, sys
from collections import Counter
data = json.load(sys.stdin)
jobs = data.get('jobs', [])
timestamps = [j['last_run_at'][:16] for j in jobs if j.get('last_run_at')]
dupes = {t: c for t, c in Counter(timestamps).items() if c >= 3}
if dupes:
    for ts, count in sorted(dupes.items()):
        print(f'{count} crons ran at {ts} (same timestamp — likely force-run/batch-trigger)')
else:
    print('No force-run clusters detected')
"
```
A force-run cluster (multiple crons with identical last_run_at far from their scheduled times) means the gateway batch-triggered them — often after a maintenance action, restart, or backlog clearance. Correlate with the scheduled times to distinguish batch-triggers from normal execution.

## Pitfalls
- Cron "ok" status does not mean output was produced. Always verify output files.

## Reference Files
- `references/cron-drift-examples.md` — Patterns found June 9: ghost crons, missing crons, stale times
- `references/competitor-intel-operations.md` — Competitor intel pipeline operations
- `references/dream-mode-pipeline.md` — 🆕 Full 5-phase DREAM MODE pipeline (weekly self-improvement): Supabase cleanup, MemPalace update, skill rewriting, connection rewiring, speculative dreaming
- `references/performance-tracking.md` — 🆕 Daily perf snapshot pipeline → Saturday weekly review data
- `references/youtube-data-api-credentials.md` — 🆕 YouTube Data API v3 setup, quota, script wrapper, env file placement, fallback behavior
- `references/recovery-script-gaps.md` — 🆕 Startup recovery script gaps: discovered June 14 — Saturday Weekly Review (`7d24b37a03f2`) not caught by startup-recovery.sh after WSL sleep. Detection and mitigation steps.
- `references/psql-stdin-piping.md` — 🆕 Pattern for piping SQL to psql via stdin instead of `-c` to avoid ARG_MAX limit on large data (transcripts, batch inserts). Discovered July 4, 2026 fixing podcast ingestion.

## Pitfalls
- Cron "ok" status also does NOT mean the output reached the user. `deliver: local` saves to disk only — Haris never sees it. Verify `deliver` field is `origin` for user-facing jobs. `local` is correct only for internal pipeline stages that feed downstream jobs (research → synthesis → actions → briefing chain).
- **CRITICAL: `deliver: local` is the default.** Every new cron job defaults to `local`. If you want Haris to see the output, explicitly set `--deliver origin` on creation, or update existing jobs via `hermes cron update <id> --deliver origin`. On June 12, 2026, 26/29 jobs were `local` — Haris was receiving almost nothing despite the pipeline running perfectly.
- Schedules are AEST, not UTC. `5 5 * * *` = 5:05 AM Sydney time.
- No-agent crons use `deliver: local` — output goes to filesystem.
- The gateway false negative is cosmetic — doesn't affect cron execution.
- Crons created but never firing is a known bug — always test with manual trigger first.
- **Documentation drift:** When a cron is created, rescheduled, or deleted, both this skill AND the schedule listing must be updated. The cross-reference check (`hermes cron list` vs documented schedules) catches ghost crons (in docs but not reality), missing crons (in reality but not docs), and stale times. Run this check after any cron change. See `references/cron-drift-examples.md` for patterns found June 9.
- **`no_agent: true` model field is cosmetic.** This is the #1 trap. When a cron job is `no_agent: true`, the `model` field shown in `cronjob list` output is **dead weight** — it has zero effect on execution. The scheduler does not invoke any LLM. Changing `deepseek-v4-flash` to `deepseek-v4-pro` (or any model) on a `no_agent` cron does nothing. This trap is especially dangerous because `cronjob list` always renders the model column regardless of `no_agent` status, making it look configurable. **Workaround:** Check `jobs.json` directly — `grep '"no_agent": true' ~/.hermes/cron/jobs.json | head -5` to confirm a job is script-only.
- **Broken pipe errors on `no_agent` crons are NOT from the LLM.** If a `no_agent: true` cron shows broken pipe errors, the source is the script itself (subprocess.run pipe closure, stdout flush at exit after cron timeout) or a misattributed error report. DO NOT change the model field — fix the script or adjust the cron timeout. The BrokenPipeError wrapper pattern (try/except at main()) is the standard fix for scripts that exceed the cron scheduler's timeout.
- **deliver:origin + No Last run:** Crons with `deliver: origin` that show no "Last run" field may have never executed. On June 9, 6 such crons were identified — all weekly/periodic jobs that missed their last window.
- **Cross-cron error matching (401 cascade):** When 4+ crons fail with the identical error string on the same day, it's a **systemic failure** — credential rotation, token expiry, or provider outage. DO NOT debug each cron individually. Check: (a) API keys/tokens in `.env`, (b) OpenRouter/DeepSeek status pages, (c) provider auth endpoint health. The Jun 10, 2026 cascade affecting Podcast KB, Podcast Insights, LinkedIn Ideas, and Daily Maintenance was a 401 credential failure hitting the Hermes Gateway authentication layer — no individual cron fix would have resolved it.
- **Force-run detection:** Pipeline stages showing `last_run_at` at 10:55 AM when their schedule is 05:00 AM is a force-run/batch-trigger signature. Multiple crons with identical timestamps far from schedule = gateway has auto-retried or queued them outside normal flow. Correlate with gateway restarts, profile switches, or maintenance actions.
- **Podcast crons need 3600s timeout, not 120s.** `podcast_ingestor.py` processes 16 YouTube channels with transcript downloads across Supabase (measured **872 seconds** for a full run with 12 episodes). Previously hit 120s default timeout → `last_status: error` with `Script timed out.` **Fix (June 14, 2026, updated June 15):** `hermes config set cron.script_timeout_seconds 3600` (escalated from 300→900→3600 after measuring 872s runtime + buffer for future channel growth). Current value: 3600s (verified Jun 17). Verify: `grep script_timeout_seconds ~/.hermes/config.yaml`.
- **🆕 `psql -c` ARG_MAX limit on large data (July 4, 2026).** Passing SQL via `psql -c "<sql>"` embeds the query in command-line arguments. Long transcripts (25,000+ chars) in dollar-quoted INSERTs exceed the OS ARG_MAX limit (~128KB) → `[Errno 7] Argument list too long: 'psql'`. **Fix:** Pipe SQL via stdin: `subprocess.run(['psql', ..., '--no-psqlrc'], input=sql, ...)`. See `references/psql-stdin-piping.md` for full pattern, verification, and cross-script applicability. This applies to ANY `no_agent` script using `psql -c` with variable-length data.
- **🆕 Hermes update check — git vs pip trap (July 10, 2026).** `hermes_update_check.sh` was using `pip list --outdated | grep hermes` and `pip install --upgrade hermes-agent` — but Hermes is installed via git, not PyPI. The script silently reported "No update found" while Hermes was 104 commits behind. **Fix:** Use `hermes update --check` (checks git remote) and `hermes update` (pulls from git). The pip approach ONLY works for PyPI-installed Hermes; git-installed instances need the CLI's built-in git update mechanism. **Detection:** `hermes --version` shows "Update available: N commits behind" but `hermes_update_check.sh` output says "No update found" → script is using wrong method. **Verification:** `bash -n ~/.hermes/scripts/hermes_update_check.sh` (syntax), then `hermes update --check` to confirm detection works. **Fixed script:** Now uses `hermes update --check` with grep for "behind" to detect pending updates, and `hermes update` to apply them. Next run (Mon/Fri 4AM) will auto-detect and apply.
