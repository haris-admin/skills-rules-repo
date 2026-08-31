---
name: fleet-intelligence
description: Cross-agent fleet intelligence gathering — how Pluto rapidly acquires context about the Gumby+Pluto dual-agent infrastructure, queries foreign agent memory stores, and triangulates fleet state from multiple data sources. Use when Pluto needs to understand what the fleet is doing, what's changed since last session, or what projects are active.
---

# Fleet Intelligence — Dual-Agent Context Acquisition

## When to Use
- Pluto is waking up after any gap (hours or days) and needs to understand fleet state
- User asks "what's going on" / "get up to speed" / "review everything"
- User references Gumby's work and Pluto needs context
- Before proposing new projects or research directions — understand the landscape first

## Architecture

```
Pluto (Hermes, WSL)          Gumby (OpenClaw, Windows)      Gumby GC (Genspark)
/home/habib/.hermes/         /mnt/c/Users/habib/.openclaw/   macarthurgarments@genspark.email
       |                              |                              |
  [state.db]                    [memory/main.sqlite]           [10K credits]
  [skills/]                     [reports/]                     [lightweight research]
  [sessions/]                   [logs/]
                                [workspace/]
                                [AGENTS.md]
                                [MEMORY.md]
                                [USER.md]

  n8n Bridge (port 18796) — dispatches tasks to Gumby GC via POST /research
     ↓
  Email backchannel — Gumby GC sends results → macarthurgarments@gmail.com
     ↓
  Gmail Ingestor → mempalace-inputs → ChromaDB chambers

  MemPalace (shared):
  /mnt/c/Users/habib/.mempalace/palace/chroma.sqlite3 ← ChromaDB
  /mnt/c/Users/habib/.openclaw/mempalace_experiments/ ← test scripts
```

## Rapid Context Acquisition Sequence

### Phase 0: Honcho Peer Check (30s health check)
Before diving into Gumby's data, verify Honcho is alive and peers are reachable:
```python
# Quick health check via honcho_context for all 3 peers
honcho_context(peer="haris")   # human
honcho_context(peer="habibi")  # Gumby/OpenClaw
honcho_context(peer="pluto")   # self
```
All three should return recent messages. Peer cards (`honcho_profile`) return empty for self-hosted Honcho < 3.x — this is expected, not an error. See `references/honcho-setup.md` for full peer map and configuration.

**Honcho Signal Bridge (push channel):** Pluto also pushes structured `[pluto]` signals to Honcho via `pluto_honcho_bridge.py` and a patched `pluto_action_bridge.py`. Gumby's message pull pipeline picks these up alongside the file-based Gumby brief. This dual-channel approach (file pull + Honcho push) gives Gumby both long-form briefs and scannable signal cards. First operational cycle (May 29): 8/11 signals delivered via Honcho, 100% utilization. See `references/honcho-signal-bridge.md` for the full bridge architecture, scripts, and operational flow.

### Phase 1: Gumby's Memory DB (fastest, richest)

Gumby stores all session memory in SQLite at `/mnt/c/Users/habib/.openclaw/memory/main.sqlite`. The `sqlite3` CLI may not be installed in WSL — use `execute_code` with Python's built-in `sqlite3` module instead. See `references/gumby-memory-db.md` for the full schema, critical queries, and edge cases.

**New: Honcho memory provider** — See `references/honcho-setup.md` for setup and configuration of the dialectic memory backend that layers on top of built-in memory.

### Phase 2: Maintenance Reports (fleet health)

Recent maintenance reports at `/mnt/c/Users/habib/.openclaw/logs/maintenance-report-*.txt`. These contain:
- Git maintenance status (pull/push results)
- System health (RAM, CPU, disk)
- Today's fleet activity (which cron jobs ran)
- AnchorSync review (skills promoted, open items)
- Current fleet status (NOMINAL/DEGRADED/DOWN)

### Phase 3: AGENTS.md (infrastructure reference)

`/mnt/c/Users/habib/.openclaw/AGENTS.md` is the authoritative reference for:
- Cron job schedule and purpose
- Channel configuration (Telegram groups, email recipients)
- Plane.so workspace layout
- Model configuration
- Known pain points and gotchas
- Skill architecture

### Phase 4: Delivery Logs (recent activity)

`/mnt/c/Users/habib/.openclaw/logs/` contains delivery results showing which cron jobs fired and whether they succeeded. Pattern: `delivery-results-<job-name>-<date>.json`.

### Phase 5: Reports (deep content)

`/mnt/c/Users/habib/.openclaw/reports/` organized by date (YYYYMMDD format). Contains:
- Morning briefings
- Afternoon briefings
- Evening reviews
- CloudWatch monitor reports
- Daily context archives
- Weekly plans and retrospectives

### Phase 6: MemPalace (16-chamber ChromaDB)

ChromaDB at `/mnt/c/Users/habib/.mempalace/palace/chroma.sqlite3`. Now a **16-chamber knowledge architecture** (upgraded May 2026). Each chamber is a dedicated ChromaDB collection with auto-routing via `route_to_chamber()`. 87 chamber docs + 219 legacy docs across 16 domains.

**Quick status:**
```bash
python3 ~/.hermes/scripts/pluto_mempalace_feeder.py --status
```

**Chamber-specific search:**
```bash
python3 ~/.hermes/scripts/pluto_mempalace_feeder.py --query "AUSTRAC" --chamber fintech-aml
```

Full architecture docs in `pluto-mempalace-bridge` skill, `references/16-chamber-architecture.md`.

### Phase 7: Obsidian Vault (knowledge management)

`/mnt/c/Users/habib/Documents/Obsidian Vault/` — contains Daily Reviews and OpenClaw Reports. Use the Obsidian skill for programmatic access.

### Phase 8: Project Repo Discovery (locate working code)

Main project repos may not be cloned on the WSL side. When projects listed in memory aren't found at expected paths, sweep the Windows filesystem:

```bash
# Discover ALL git repos under Windows user directory
find /mnt/c/Users/habib -maxdepth 4 -name ".git" -type d 2>/dev/null
```

Key findings as of June 2026: ideation repos live under `/mnt/c/Code/gitlab/ideas-*/`, fintech-sample and n8n-integration are cloned, but **tapease, plane, ndis-billbot, and mempalace repos may not be locally cloned** — they may be on GitHub/GitLab only or under different names. Don't assume "not found" means "doesn't exist" — ask Haris if a critical repo is missing.

## AWS Infrastructure Health Check

When reports show CloudWatch logs are empty or EC2 metrics are missing, the CloudWatch Agent config was likely wiped by an RPM upgrade. See the **`aws-cloudwatch-agent` skill** for the full diagnostic and recovery pipeline (SSM commands, merged config deployment, verification).

Quick check:
```bash
# Are EC2 instances reporting metrics?
aws cloudwatch list-metrics --region ap-southeast-2 --namespace CWAgent --query 'Metrics[*].[MetricName]'

# Are log groups receiving data?
aws logs describe-log-groups --region ap-southeast-2 --query 'logGroups[?storedBytes==`0`].[logGroupName]'
```

For the Tapease fleet specifically, the deployed config reference is in `aws-cloudwatch-agent` → `references/tapease-config.md`.

## Hermes Gateway Health Check

Quick verification that the Hermes gateway is running:
```bash
cat ~/.hermes/gateway.pid && ps aux | grep "[h]ermes gateway"
```
A missing PID file or no matching process means the gateway is down — restart with `hermes gateway`.

## n8n Research Bridge (Port 18796) - TapEase Fleet Monitor

Full lifecycle management, endpoint reference, editing guide, and troubleshooting in windows-bridge-management skill. This section covers fleet-level context only.

A Node.js Express server running on Windows at C:\Code\gitlab\n8n-habibi-integration\bridge\research_bridge.js. This is a separate fleet from the Hermes cron pipeline - it monitors TapEase AWS infrastructure (Lambda, EC2, RDS, S3) and provides cross-agent message relay.

Health check: curl -s http://localhost:18796/health

TapEase monitoring schedule (4x daily via Hermes cron):
- 5:00 AM (dbd3cb1b5bd3) - Morning cycle
- 11:00 AM (582bd225ddd1) - Midday cycle
- 5:00 PM (1086e6405da1) - Evening cycle
- 11:00 PM (be81c61778a8) - Night cycle

Runner: /home/habib/.hermes/scripts/tapease_prod_monitor.py — direct AWS CLI + SSM monitor (replaced bridge-based tapease_monitor_runner.py Jul 8, 2026).

PowerShell encoding trap: The monitoring scripts at scripts/system/ contain Unicode chars. Fix: Save .ps1 files with UTF-8 BOM.

## Cron Job Health Investigation

When any cron job shows `error` status or delivers empty/incomplete results, run this diagnostic pipeline before touching any config.

### Phase 1: Get the landscape
```bash
# cronjob list shows all jobs with last_status and last_run_at
```
Look for: `last_status: error`, long gaps between `last_run_at` and `next_run_at`, or jobs that show `ok` but with warnings in logs.

### Phase 2: Check errors.log for the failing job ID
```bash
grep "<job_id>" ~/.hermes/logs/errors.log | tail -20
```
The error log captures the exact exception and stack trace. Key patterns:
- `HTTP 401: Authentication Fails, Your api key: ****XXXX is invalid` → credential expired/rotated server-side. Fix: update the key in `.env` — no cross-location sync needed.
- `Path not found: /home/habib/.hermes/<path>` → the cron agent is searching wrong directories. Fix: update the cron job prompt with the explicit correct path.
- `No module named '<package>'` → venv missing a dependency. Fix: pip install in `~/.hermes/venv/`.
- `credential pool: no available entries` → all credentials for that provider exhausted. Often follows repeated 401s — check the real root cause above.

### Phase 3: Cross-reference agent.log for credential exhaustion
```bash
grep "<job_id>" ~/.hermes/logs/agent.log | grep -E "credential pool|exhausted|rotating|401"
```
When a credential fails, the agent's credential pool marks it "exhausted" and tries to rotate. If there's only one entry and it's bad, every subsequent run fails identically. The tell: hundreds of identical failures at regular intervals (e.g., every 5 minutes for the Mempalace Inbox Watcher).

### Phase 4: Fix and verify
1. Fix the root cause (update key, correct path, install package)
2. Run the job manually: `cronjob run <job_id>` 
3. Check `cronjob list` confirms `last_status: ok`
4. Check `errors.log` tail for clean runs

### Phase 5: Jobs that self-heal
Jobs that failed due to a transient credential outage (now fixed) will self-heal on their next scheduled run. They still show `error` from the failed run but will flip to `ok` after the next successful execution. Don't manually mark them fixed — just note the schedule.

### Common failure modes by job type
| Job pattern | Typical root cause | Fix |
|-------------|-------------------|-----|
| All jobs failing simultaneously | Provider API key expired | Update key in `.env` |
| One job searching wrong paths | Vague cron prompt, agent wandering | Update prompt with explicit path |
| Watcher job (every 5min) racking errors | Credential or path issue on first run, then repeats | Fix root cause — the 5min interval amplifies it |
| Weekly/monthly job shows `error` | Failed on last run during outage window | Wait for next scheduled run — self-heals |

## Pluto as Main Agent (June 2026)

As of June 1, 2026, Pluto is the primary fleet agent. Gumby (OpenClaw/Windows) is being stood down for scheduled activities.

**Pluto's Cron Fleet (25 healthy jobs — June 13, 2026 prune):**

| Job | Schedule (AEST) | Purpose |
|-----|----------------|---------|
| Gmail Briefing Ingestor | 4:55 AM | Pull Perplexity/Genspark briefings + **competitor signal scan** (79 companies) |
| Podcast Insight Extractor | 5:02 AM | Active — produces podcast_insights.json daily |
| Morning Research | 5:05 AM | Daily deep research on tracked topics |
| Competitor Intel | 5:07 AM | Daily competitor signal extraction |
| Cross-Chamber Synthesis | 5:10 AM | Cross-domain pattern detection |
| Action Bridge | 5:15 AM | Convert synthesis → actions |
| Briefing Improver | 5:20 AM | Enhance briefing with podcast + competitor intel |
| Chamber Refresh | 5:25 AM | Feed research→ChromaDB chambers |
| Honcho Signal Bridge | 5:30 AM | Push [pluto] signals to Honcho |
| ★ Main Briefing | 6:00 AM Mon-Fri | Deliver text + voice to Telegram |
| Feedback Loop | 6:10 AM | Close feedback cycle |
| Moonshots Learning | 6:15 AM | Teach+quiz from podcast KB |
| ★ Pluto Saturday Weekly Review | Sat 6:00 AM | Weekly retrospective: perf, repos, signals, 3 build options | `7d24b37a03f2` |
| ★ Pluto Adversarial Sunday | Sun 6:00 AM | Blind spots + counter-narratives + portfolio pulse | `f8756a2b8403` |
| Pluto Skill Extractor | 11:00 AM | Scan sessions for new skill patterns |
| Daily Maintenance | 2:00 PM | Skill & memory updates |
| Git Repo Sync | 1:00 AM | Pull all repos (skips 5 stale) |
| Weekly Test Report | Wed 2:00 AM | A2Square + AML Hive report |
| Hermes Update Check | Mon+Fri 4:00 AM | Check Hermes version |
| ★ Sat Weekly Review | Sat 6:00 AM | Deep retrospective + 3 build options |
| ★ Sun Adversarial+Portfolio | Sun 6:00 AM | Blind spots, counter-narratives, portfolio pulse |
| Sat Auto-Improvements | Sat 12:00 AM | Implement weekly review improvements |
| Fri Weekly Review | Fri 11:05 PM | Internal self-review (feeds Sat) |
| Performance Tracker | 11:30 PM | Daily cron/perf data → feeds Sat review |
| MemPalace Cleanup | 11:55 PM | Archive old files, compact DBs |
| MemPalace Watcher | Every 5 min | Auto-process mempalace-inputs/ |
| Vercel Monitor | 5:05 AM/PM | AML Hive deployment health |

**Honcho peers (June 13):**
- `haris` — human collaborator. Peer card populated via `honcho_profile` with 7 facts (role, location, portfolio, preferences). Queries now work.
- `habibi` — Gumby/OpenClaw agent. May be empty (self-hosted Honcho < 3.x).
- `pluto` — self. Expected empty.

### Gumby GC (Genspark OpenClaw) — June 16, 2026

A Genspark-based agent ("Gumbi GC") now has credentials and 10,000 credits for lightweight research on Pluto's behalf. Integration points:

- **Control:** Pluto dispatches research tasks via n8n Bridge: `POST /research` on port 18796, or sends mission briefs via `POST /pluto/deliver`.
- **Output channel:** Gumby GC sends results via email to `macarthurgarments@gmail.com` (subject: Genspark-sourced). Gmail ingestor matches `genspark` as sender.
- **Ingestion path:** Gmail Ingestor → `mempalace-inputs/` → ChromaDB chambers (auto-routed by topic).
- **Budget:** 10,000 credits. Use selectively — high-impact targets only: competitor deep-dives, regulatory deadline verification, cross-validation of Pluto's findings.
- **Mission pattern:** (1) Dispatch via bridge, (2) watch for email delivery, (3) ingest findings to chambers, (4) tag as `[Validated by Gumby GC]` in briefing when used.

### Periodic Pruning Pattern

Fleet health degrades — duplicate crons, stale pipelines, credential drift. Prune every 2-4 weeks. Look for: never-executed crons (null last_run_at), error-status crons for 3+ days, paused jobs with no plan, stale repos in git sync, superseded jobs.

**Jun 13 prune removed:** Podcast KB Ingestion (IP-blocked), Voice & Task Processor (paused), Podcast Chunking (dead downstream), A2Square Git Syncs (never executed), Weekly Research Digest (superseded), Old Saturday "About Haris" Briefing (replaced).

### Vercel Monitor — Fixed (Jun 13)

Previously false-alerted "no deployments in 12h" on stable live apps. Now only alerts on real deployment errors (ERROR/BLOCKED state). Current: 10 deployments, all READY, 0 errors. Healthy.

### Git Sync — Stale Repos Skipped (Jun 13)

```python
KNOWN_DEAD_REPOS = {'ideas-ndis', 'ideas-exitlens', 'ideas-gridpass', 'ideas-pitguard', 'ideas-verifylink'}
```

**Saturday "About Haris" Briefing — Session Discovery:** See `references/about-haris-briefing-discovery.md` for the proven pattern to find Haris's interactive sessions among cron noise. First run June 13, 2026: 2 interactive sessions found, 8 observations extracted.

**New infrastructure (June 4, 2026):**
- **Supabase podcast_kb:** PostgreSQL + pgvector on `vyqagemgwxfscppkfswq` (ap-southeast-2). Schema: podcasts, episodes, chunks (vector embeddings), cross_references, au_keywords, hybrid_search(). Pooler: `aws-1-ap-southeast-2.pooler.supabase.com:6543`. See `pluto-podcast-kb` skill for full architecture.
- Credentials in `/mnt/c/Users/habib/.hermes/.env` under `SUPABASE_OPERATOR_SPOOLER_DATABASE_URL`.

**What still needs migration from Gumby:**
- ~~TapEase 5 AM AWS monitor~~ ✅ **MIGRATED** (Jun 14) — 4x daily via bridge port 18796. See "n8n Research Bridge" section below.
- ASX market analysis
- n8n workflow triggers
- NDIS BillBot monitors

**Already migrated (complete):**
- ✅ Gumby Morning Brief (6:00 AM) — Pluto now delivers full briefing directly as of June 4, 2026 (research → LinkedIn → voice → email → Telegram, no Gumby intermediary)

**Cron migration process:** Gumby runs on a different platform (OpenClaw/Windows). Jobs cannot be auto-imported. Process: (1) Ask Gumby to list his cron jobs, (2) recreate each one here via `cronjob action=create`, (3) verify with `cronjob action=run`, (4) disable on Gumby side.

**Build queue:** Active project registry at `~/.hermes/mempalace-inputs/.build-queue/BUILD_QUEUE.md` — tracks active/staged/queued/frozen projects across the portfolio.

**Hermes config repo:** Pluto's scripts, skills, build queue, and cron config are backed up to `C:\Code\gitlab\hermes-pluto-config\` (`git init` June 1, 2026). Push to GitLab pending fresh PAT. Live scripts run from `~/.hermes/scripts/`, custom skills from `~/.hermes/skills/research/`.

## Key Fleet Facts (cross-reference with memory)

- **Timezone:** Australia/Sydney (AEST/AEDT)
- **Human:** Habib ("habibi"), +61450902040
- **GitHub:** `haris-admin` account (11 repos: 10 private + 1 public). PAT in `~/.hermes/.env`.
- **GitLab repo:** gitlab.com/hhsiddiqui/openclaw
- **Plane.so workspaces:** AML, STARTUP, PERSONAL, PA
- **Email recipients:** admin@harishabib.au, hhsiddiqui@gmail.com, habibshoaib841@gmail.com
- **Telegram bot:** @Hari_personal_bot
- **9 active cron jobs on Pluto** (plus ~8 on Gumby pending migration)
- **WSL to Windows bridge:** `/mnt/c/Users/habib/`
- **Credential verification:** When API calls fail, sweep ALL credential locations (6+) — different locations can hold completely different key sets. See `references/credential-verification.md`.
- **gstack methodology:** Garry Tan's AI product development workflow (23+ skills: plan/build/ship/secure layers). 4 OpenClaw-native skills already packaged for Gumby. Full review and fleet project mapping in `references/gstack-product-development.md`.

## Cron Bridge Verification (Honcho Signal Bridge)

When a `no_agent` script-based cron shows `last_status: ok`, **do not trust it.** The script may exit 0 even when no data was pushed. This happened June 3, 2026: the Honcho Signal Bridge (`pluto_honcho_bridge_daily`) reported `ok` for 2 consecutive days but had 7 files sitting unpushed.

**Verification procedure for bridge-like crons:**

1. **Run the script in `--list` mode** to see what would be pushed:
   ```bash
   cd ~/.hermes && /home/habib/.hermes/venv/bin/python3 scripts/pluto_honcho_bridge.py --list
   ```
2. **Check the state file** to see what was previously pushed:
   ```bash
   cat ~/.hermes/research_outputs/.honcho_bridge_state.json | python3 -c "import sys,json; d=json.load(sys.stdin); print('Last run:', d.get('last_run'), '; Pushed:', len(d.get('pushed_files',[])))"
   ```
3. **If pending files exist, run the bridge manually:**
   ```bash
   cd ~/.hermes && /home/habib/.hermes/venv/bin/python3 scripts/pluto_honcho_bridge.py
   ```
4. **Verify the state file updated** — re-run step 2 to confirm files moved from pending to pushed.

The root cause pattern: `no_agent` scripts exit 0 on success but `deliver: local` means cron delivery status isn't correlated with script payload success. The script could hit an API timeout, state-file write failure, or empty run without the cron scheduler knowing.

## Competitor Signal Verification (NEW June 11, 2026 — Updated July 3, 2026)

The competitor intel pipeline (`competitor_intel.py`, cron `1a13a2d49682`) generates daily competitor signals from research findings. The competitor database was **expanded from 21 to 79 companies** (July 3, 2026) — now covering the full AML/CTF compliance landscape including KYC/identity providers, transaction monitoring platforms, compliance automation tools, and digital identity schemes.

**Database location:** `~/.hermes/data/competitors.json`
**Categories tracked:**
- `aml_austrac` (62 companies) — AML platforms, KYC/identity, transaction monitoring, compliance automation, digital ID
- `esop_cgt` (3) — ExitLens competitors (Cake Equity, Orchestra, Pulley)
- `psp_licensing` (3) — PayLicence competitors
- `ai_governance` (3) — FinAI File competitors
- `cloud_infra` (3) — CloudProof competitors
- `payments_saas` (3) — Tapease competitors
- `digital_assets` (2) — TokenPilot competitors

**CRM integration opportunity (NEW July 3, 2026):** Top 10 AU real estate CRMs identified as integration targets for AML Hive. Key findings:
- **Reapit** launched AML/CTF compliance built into their CRM (direct competitive threat — they're baking compliance into the agent workflow)
- **PropertyMe** acquired Phoenix Software to expand into real estate CRM (consolidation trend)
- **REA Group** integrating with **MRI Software** CRM for data-enriched leads
- **Rex Software** launched AI features (Rex AI — database unlocking, lead nurturing)
- Top CRM targets for AML Hive API integration: Rex (PropertyTree), MRI (Console Cloud), Reapit, PropertyMe, Aspire, Agency Plus, Rocket Agent, CoreLogic RP Data, rest (Rockend), Salesforce Real Estate Cloud

**Always verify before reporting.** See `references/competitor-signal-verification.md` for:
- Full description of the false-positive mechanism
- Step-by-step signal verification procedure
- Signal confidence tiers (🔴 Confirmed / 🟡 Probable / 🟢 Pipeline-only)
- The Change Financial × Paymentology case study (real vs pipeline noise)
- Recommended fix for the script

**Quick check:** If a competitor shows all three signals (💰🏢🚀) simultaneously, it's almost certainly a false positive from generic word matching. Run the verification steps in the reference before treating it as real.

## Pitfalls

### 🔴 MANDATORY: Cross-Validation Workflow (June 16, 2026)

For **high-impact findings** before surfacing in a briefing: run them past another agent for verification.

1. **Credentials & System Health** — Delegate to Gumby (OpenClaw) to check `.env` token validity, Vercel deployment states, AWS health from his Windows vantage.
2. **Competitor/Regulatory Signals** — Dispatch to Gumby GC (Genspark, 10K credits) for a lightweight verification: "Confirm this competitor move / regulatory deadline" — watch for email reply at macarthurgarments@gmail.com.
3. **Briefing Content Coverage** — Before the 6:00 AM delivery, verify all 3 sources contributed: Gmail (Perplexity/Genspark), YouTube/podcast, and Pluto's own web research. Note gaps explicitly.
4. **Tag validated findings** in the briefing with `[Cross-validated by Gumby GC]` or `[Verified by Gumby/OpenClaw]` so Haris knows what level of assurance each item carries.

### 🔴 MANDATORY: Cross-Reference Before Any Error Report

Before reporting ANY cron job issue, the review MUST run this verification:

```python
# Run the cross-reference verifier on the claimed issue
import subprocess, json
result = subprocess.run(
    ['python3', f'{HERMES_HOME}/scripts/cross_ref_verify.py', job_id, claimed_issue],
    capture_output=True, text=True
)
verdict = json.loads(result.stdout)
if verdict['verdict'] == 'FALSE-POSITIVE':
    # SILENT — do not report. The fix was already applied or the claim is wrong.
    # Write to review notes but do NOT surface to Haris as an action item.
```

**Key rules:**
1. **If a cron is `no_agent: true`, NEVER report LLM-related issues** (broken pipe, model, retries, streaming). The model field is cosmetic.
2. **If `last_status: ok` and output files are clean**, do not report errors.
3. **If the pipeline-orchestration skill says "RESOLVED"**, do not re-report. The fix was already applied.
4. **Stale cron IDs**: If the skill references `fabab82f804a` (old podcast cron), that cron was deleted. Use the current ID `d4d77c41f6c0`. Check `cronjob list` for current IDs.

**Known false-positive patterns to always skip:**
- "Mempalace Watcher broken pipe" → no_agent since May 24. Cosmetic model field.
- "Podcast KB Ingestion broken pipe" → replaced with no_agent script on June 12. Timeout now fixed.
- Any `no_agent` cron showing a model name → the model field is ignored.

- **`no_agent` script crons: `last_status: ok` is NOT sufficient verification.** See "Cron Bridge Verification" above. The Honcho Signal Bridge (`pluto_honcho_bridge_daily`) is the canonical example — always verify by running `--list` and checking actual pending files, not the cron status.
- **sqlite3 CLI not installed:** The `sqlite3` binary may not be available in WSL. ALWAYS fall back to Python's `sqlite3` via `execute_code`. Never fail with "command not found."
- **Windows paths from WSL:** ALL Windows paths must use `/mnt/c/` prefix, not `C:\`. PowerShell syntax does NOT work in WSL terminal.
- **Memory DB is Gumby's, not Pluto's:** Pluto's memory is in `~/.hermes/state.db`. Gumby's is at the Windows path. They are separate.
- **AGENTS.md may be truncated:** When reading with `read_file`, always check if it got truncated and request continuation with `offset`.
- **Reports are date-organized:** Look for `reports/YYYYMMDD/` directories, not flat files.
- **Gumby's memory DB is volatile:** The SQLite DB at `/mnt/c/Users/habib/.openclaw/memory/main.sqlite` may be empty or freshly reinitialized. Always `SELECT name FROM sqlite_master` to check table existence before assuming data is present. A 0MB file with no tables means the DB was reset — don't treat the skill's size estimates as current.
- **Honcho writes need gateway restart:** `honcho_conclude` silently fails with "Failed to save conclusion" if the Hermes gateway hasn't been restarted after adding Honcho env vars to `.env`. Reads work while writes fail — they use different API paths. Fix: restart the gateway.
- **Cross-platform credential drift:** `.env` files exist in 6+ locations (WSL `~/.hermes/`, Windows `.hermes/`, Windows `.openclaw/`, `.openclaw/workspace/`, `.openclaw/workspace/config/`, `~/.aws/credentials`). Tokens can be completely different values across locations — not just truncated copies. When API calls fail, sweep ALL locations, identify unique key suffixes, test each. Full diagnostic in `references/credential-verification.md`.
- **macarthurgarments@gmail.com Gmail access:** Himalaya v1.2.0 IMAP/SMTP configured June 3, 2026. Credentials in Windows `.env` (`GOOGLE_GMAIL_APP_PASSWORD_MACARTHUR`). Config at `~/.config/himalaya/config.toml`. Daily Perplexity briefings land here. See `references/macarthurgarments-gmail.md` for full setup and operations.
- **Time-aware communication (CRITICAL):** Server is UTC, user is Sydney AEST (UTC+10). NEVER use time-based greetings ("good morning", "good evening") without checking current Sydney time first. Haris flagged this June 3 when greeted with "good morning" at 10:16 PM Sydney. When in doubt, skip the greeting or use time-neutral openers.
