---
name: pluto-daily-maintenance
description: Pluto's lightweight daily maintenance engine — 4-task health check (skills, memory, cron, scripts) run at 2:00 PM AEST. Focus on keeping things running, not dreaming. Saturday deep reviews handle the heavy lifting. Use when running the daily maintenance cron, debugging why it found issues, adding new health checks, or classifying cron errors during any audit.
---

# Pluto Daily Maintenance

## When to Use
- Running the daily maintenance cron (`575918cbc242`, 2:00 PM AEST)
- Debugging why the daily maintenance found issues
- Adding new health checks to the daily routine
- Classifying cron errors during any audit

## The 4-Task Procedure

### Task 1: Skill Health Check
1. Load skills used/referenced in the last 24 hours
2. Check for stale references: old repo names (`ideas-*-au` → `ideas-*`), dead file paths, wrong cron times
3. Patch minor issues immediately; flag severe staleness for Saturday
4. Check for old pruned cron IDs referenced outside of `pipeline-orchestration` (historical documentation)
5. **Fleet-mirror drift — the biggest silent gap (added 2026-09-23).** `daily_skill_scan.py` does NOT
   compare skill CONTENT against the canonical repo, so a skill can be patched in WSL for weeks while
   the copy every other agent reads stays old. Scan by normalised hash, not mtime (normalise CRLF on
   BOTH sides or every `/mnt/c` file reads as changed), listing (a) skills absent from the repo and
   (b) skills whose content differs. Classify: an ABSENT skill is a pure ADD — safe to copy straight
   in (then run the frontmatter check and path-scoped `git add`/`git commit -m "..." -- <paths>`);
   a DIFFERING skill needs a MERGE, because the repo side often carries sections the WSL side never
   had (see the merge pitfall in `fleet-skill-governance`) — report those, never bulk-overwrite them
   from a daily tick. Seen 2026-09-23: repo held 341 SKILL.md vs 246 local, 112 WSL-only (several
   fleet-relevant, incl. `acma-dncr-live-washing`, `alexandria-vault-sync`, `git-working-tree-hygiene`,
   and — circularly — `fleet-skill-governance` itself) and 104 differing.

### Task 2: Memory Grooming
1. Check `~/.hermes/memories/MEMORY.md` for stale entries
2. Remove/update entries referencing old repo names, old cron schedules, outdated facts
3. Also check for naming drift — e.g., memory says "Tapease payout sweep" but cron script is `tapease_payout_email.py`; the daily transactions cron (`114039a7ff9b`) uses `tapease_daily_transactions.py` for CSV export, while the payout email cron (`77f0402cb1de`) uses `tapease_payout_email.py`. Another recurring drift: `gmail_health_check.py` (4:50 AM pre-flight) looks for `GMAIL_USER`/`GMAIL_APP_PASSWORD`, but the working ingestor uses `GOOGLE_GMAIL_APP_PASSWORD_MACARTHUR` + hardcoded `macarthurgarments@gmail.com` — when Gmail creds migrate, the health-check's env-var names must be updated in lockstep or it exits 2 ("CONFIG MISSING") forever.
4. If no MEMORY.md exists, note it — not an error

### Task 2b: Memory architecture hooks — VERIFIED REALITY (10 Sep 2026)
The 2PM cron prompt itself contains ONLY the 4 tasks above — it is NOT a memory-pipeline hook. Earlier revisions of this skill claimed (a) drain `~/.hermes/mempalace-inputs/`, (b) rebuild the FTS index, (c) run `memory_check.py`, (d) git commit+push the ops/facts repo. Corrected state:
- **(a)** Inbox draining is owned by the Mempalace Inbox Watcher cron `5678a363ce3b` (every 5m, `mempalace_watcher.py`) + MemPalace Nightly Cleanup `0fc5019948be` (11:55 PM, `mempalace_cleanup.py`). Do not expect `mempalace-inputs/` to be drained by this cron.
- **(b)** FTS/index rebuild is `mempalace_optimize.py` / `mempalace_cleanup.py` — not run from here.
- **(c)** `memory_check.py` DOES NOT EXIST anywhere under `~/.hermes` — audit memory inline instead: compare `wc -c` of `~/.hermes/memories/{MEMORY,USER}.md` against `memory_char_limit` / `user_char_limit` in `config.yaml` (currently 4400 / 2500) and flag lines that are not pointer-shaped.
- **(d)** `~/.hermes/ops/` is a PLAIN directory — NOT a git repo, and no `facts/` subdir exists. There is no commit/push step. Durable facts live in `~/.hermes/ops/environment.md` (pointer target for memory).
Routing rules: `memory-hygiene` skill; design history: `~/.hermes/ops/memory-architecture-decision-2026-09-03.md`. Never truncate memory without a snapshot.

### Task 3: Cron Health Pulse

**Run the hardened helpers first — they cover Task 1 and Task 3 steps 1-4 + 6 in one pass:**
`python3 ~/.hermes/scripts/daily_cron_audit.py` (script-path resolution against BOTH script roots,
delivery-target histogram, non-ok jobs grouped by delivery, enabled jobs with null/past
`next_run_at`, **plus `=== error clustering ===` and `=== staleness classification ===`** — step 2
below is now automated, read it instead of clustering by eye) and `python3 ~/.hermes/scripts/daily_skill_scan.py` (skill usage + SKILL.md touches in
the last 24h, legacy-key scans by FILE not path since agent.log is append-only, dead-cron-ID
detection that skips context already marked RETIRED/PRUNED/dead/historical/PAUSED).

1. Parse `~/.hermes/cron/jobs.json` for `last_status` counts
2. **Before debugging ANY individual failure, cluster errors by string + timestamp.** Many jobs red
   inside one window is ONE event, not N bugs. `daily_cron_audit.py` prints this as
   `[N job(s)] CLUSTER (one event)` with the id list and time window; treat every cluster as ONE
   finding. **A cluster keyed on `Script exited with code <n>` alone is a FALSE cluster** — that
   string carries no discriminating power, so the audit appends the first error-marked stdout line
   as a discriminator (`… | stdout: ❌ HTTP <n> …`). If you ever see unrelated scripts merged under a
   bare exit-code signature, fix the discriminator in `_sig()`, do not read it as a real cluster.
   Seen 2026-09-15: 8 agent crons (5:02-6:45) all
   `RuntimeError: [Errno 32] Broken pipe` = a single DeepSeek upstream outage (503
   `service_unavailable_error` + `RemoteProtocolError` incomplete-chunked-read) with NO fallback
   chain configured to absorb it. Commands that settle it: `grep -c "Service is too busy"
   ~/.hermes/logs/agent.log`; `grep -E "<date> .*attempt 3/3" ~/.hermes/logs/agent.log` (proves the
   retries were exhausted, not a first-call failure); `hermes fallback list` (a chain resolving to
   ZERO hops IS the finding). Then fix the absent RESILIENCE, not the past blip.
3. Classify each error using the error classification guide below
4. Verify script paths exist for all `no_agent` script-based crons (see Pitfalls: `script` field is basename-only — prepend `~/.hermes/scripts/`)
5. Check for "never ran" crons — distinguish genuine scheduler bugs from weekly crons awaiting their first window
6. **Audit DELIVERY TARGETS, not just statuses.** Group every job by `deliver` and count per target; each must point at a live target from the routing table (`telegram:-1004485329864` AMLHive-subject, `telegram:-1003834479227` general/daily) or `local`. A job can report `last_status: ok` every single run while delivering into a retired channel — `ok` only means it RAN. **When the owner says a report or sweep "isn't firing", check `deliver` before debugging the job itself**; a sweep that runs perfectly into a retired channel reads as "not firing" forever. Retarget with `cronjob(action="update", job_id=..., deliver="telegram:<id>")`, then re-verify. Re-run this audit after ANY channel change or owner routing instruction: jobs that were correct when the change was made silently rot afterwards.

### Task 3b: Shared-lane hygiene (added 2026-09-14 after a real cascade)

A dirty index on a shared agent lane blocks jobs that never touched it. Run:

```bash
cd ~/code/amlhive1 && git status --porcelain | wc -l && test -f .git/MERGE_HEAD && echo MERGE_IN_PROGRESS
git diff --name-only --diff-filter=U   # unmerged paths
```

A non-zero `MERGE_HEAD` means an in-progress merge was left behind — the next `git checkout` on that
lane dies with `error: you need to resolve your current index first`. Seen 2026-09-14: the 03:00
test runner's `git merge origin/dev` hit an add/add conflict in
`docs/agent_rules/agent-branch-standard.md`, printed ❌ and CONTINUED (no `merge --abort`), leaving
MERGE_HEAD set; the Mon 10:30 CRAP job (`153af82d274e`) then failed at step 1 and produced NO report.
Recovery is the repo's own rule (`docs/agent_rules/agent-branch-standard.md`): a merge conflict →
`git merge --abort`, STOP and report BLOCKED — do NOT resolve a conflict in a governance doc
autonomously, and never `git reset --hard` over an in-progress merge. Both lane runners now abort
themselves and print `⚠️ MERGE_NOT_APPLIED — origin/dev NOT merged (conflict, aborted; BLOCKED)`;
treat that marker as BLOCKED, never as a pass (the suite then ran on UNMERGED `pluto_pr`).

### Task 4: Script Validation
1. Check Python syntax of recently modified scripts: `python3 -m py_compile <script>`
2. **`py_compile` is NOT proof for a script you just patched.** A newly referenced constant, helper, or import alias that was never defined compiles clean and dies with `NameError` at its next scheduled fire — with no test run in between. Before the schedule fires, (a) run a name-resolution check (AST pass: names loaded at module scope that are neither module-level definitions nor builtins), (b) run ONE live invocation and read its stdout for the expected counts, and (c) for collectors/drains, run it twice and confirm the second run reports "no changes" (idempotency) — a pipeline that double-writes or re-prunes on every run corrupts its own output.
3. Verify all script paths referenced in cron jobs exist on disk (prepend `~/.hermes/scripts/` — the `script` field is basename-only)
4. Report broken scripts immediately
5. **Hardcoded-credential sweep — and the two-party handshake that follows.** Grep the fleet scripts
   for literal secret assignments by SHAPE (never print the value; report `file:line` only). When you
   find any, the fix splits in two: **the code stops carrying the value, the owner rotates it** —
   state that split explicitly, because he cannot rotate until your half is done and listed.
   (a) **Back up FIRST** — `cp -a ~/.hermes/scripts/*.py ~/.hermes/backups/scripts_$(date +%Y%m%d_%H%M%S)/`
   plus `jobs.json`: these scripts live outside git, so that copy is the only undo.
   (b) Move each literal to the **existing** loader convention (`/mnt/c/Users/habib/.hermes/.env` then
   `~/.hermes/.env` into `os.environ`, as `amlhive_daily_report.py` and `podcast_insight_extract.py`
   already do) rather than inventing a new secret store.
   (c) **Fail loudly, naming the missing key** — a default or empty-string fallback silently restores
   the old behaviour, which is the bug you are fixing.
   (d) Verify WITHOUT real values: set obvious dummies in the subprocess env and show the script reads
   them (or exits with the named-key error), then shape-grep to prove no literal remains.
   (e) Hand back the **rotation list: key name, file, line** — never a value.
   Cron **prompts inside `jobs.json` carry credentials too**: back that file up before touching it and
   change only the prompt string, never a job's enabled state.
   **(f) Sweep ARCHIVED OUTPUT, not just scripts/skills.** Agents echo the working command (with the
   secret inline) into their report files, so the durable leak lives in `reports/` archives and in the
   two alexandria repos — and a repo copy means the value is already PUBLISHED, including in git
   history. Scan by SHAPE with a hash-matched pattern file (`rg -l -f <pattern>` where the pattern file
   is written in-process and shredded after; report `file:line` and counts, never the value) across
   skills, `cron/jobs.json`, `~/.hermes/ops/`, both alexandria trees and the scripts roots. Seen
   2026-09-19: a LIVE Supabase operator password (still matching auth) sat in 3 files of the PUBLIC
   `haris-admin/skills-rules-repo` (HEAD + history) plus 329 archived reports across
   `haris-admin/alexandria-ops` and the vault. **Classify by whether the leak is ONGOING** — compare
   the newest affected artifact's date against the last prompt/skill sanitisation; a leak that stopped
   months ago still needs ROTATION, not more scrubbing. Sanitising the working tree is the cheap half
   and never the fix: say so plainly and name the rotation target (env key + file:line) in the alert.

## Error Classification Guide

When you see `last_status: error` on a cron, classify before escalating:

### 🚫 No Fake Pass Rule (Aug 2026 — Haris explicit: "put a rule to not to do the fake pass")

**A check that did not actually verify is NEVER a PASS.** This is a classification rule for ALL cron scripts, monitors, and test runners — not just errors:

- `DATASET_SOURCE_UNAVAILABLE` / source-not-configured → **ALERT**, never "skipped, pass". Seen 2026-08-15: `amlhive_asic_sync.py` collapsed every `skipped=true` reason into `⏭️ Skipped (no change)` → summary said ✅ PASS while `asic-registered-schemes` never synced (empty `ASIC_REGISTERED_SCHEMES_CSV_URL`). Fix: classify reasons explicitly — `DATASET_SOURCE_UNAVAILABLE → overall_alert=True`; only `NO_CHANGE` / `FILE_NOT_YET_PUBLISHED` pass. **One documented exception (verify before flagging):** `amlhive_asic_sync.py` quiet-skips `DATASET_SOURCE_UNAVAILABLE` for `asic-registered-schemes` ONLY (standing order "no ASIC trying for now" — no public CSV source exists), and still alerts for every other dataset with that reason. That single skip is intentional, not a fake pass — see `amlhive-asic-sync` skill. Also: an `enqueued=True` async response is NEVER a pass (rows are a stale fingerprint); the next run reporting `NO_CHANGE` with real remote row counts is the proof the enqueue landed.
- 0 tests collected / config-parse error → **ERROR**, never "0 passed" (test-runner false-green, Aug 2026; see `wsl-cron-test-runner` for the `guard_no_tests` pattern).
- A `skipped=true` / `ok` field in a script's own output is only a PASS when the underlying check genuinely completed.
- When auditing a cron that reports "ok" but skips work, read the script's reason classification before trusting the summary icon.

### By-Design (NOT errors — do NOT escalate)
- **`pluto_feedback_processor.py` exit code 3** (`59f18c4d557c`, Pluto Feedback Loop 06:10
  `deliver: local`): `sys.exit(3)` is the script's own DEGENERATE-SCORER signal. It means every
  tracked finding carries the same `used_count`, `skipped_count=0`, and no `USED:`/`SKIPPED:`
  markers exist in the Gumby brief — usage is *inferred, never measured*. All three artefacts are
  still written (`feedback_<date>.json/.md` + `pluto-feedback-to-gumby.md`). Classification:
  **REAL / standing config gap, UNCHANGED** — do not re-escalate, and do not "fix" it here. It
  clears only when Gumby emits the markers or the script exits 0 once its artefact is written.
- **`amlhive_prod_monitor.py` exit code 1**: The fleet monitor exits 1 when incidents are found (RLS bypass probes, API 500s, CloudWatch alarms). Email IS the alert mechanism. This is documented behavior. Verify by checking the output file for incident details — if present, the monitor worked correctly. The 11AM run often shows `ok` because incidents cleared by then.
- **Alert scripts that email internally**: Any script that sends its own email alerts should exit 0 even on findings. If it exits 1, it's a false-positive in cron health. See `pipeline-orchestration` skill's "Design rule for no_agent alert scripts."

### Transient (watch, auto-recovers)
- **`GIT_TIMEOUT`**: Script stdout contains `GIT_TIMEOUT`. Network/git-remote issue. Usually self-resolves next run. Escalate only if 3+ consecutive days.
- **Gateway shutdown**: `Gateway shutdown (final-cleanup) killed the job's tool subprocess`. Caused by gateway restarts. Auto-recovers next cycle.
- **`Interrupted by shutdown before terminal completion` with NO gateway restart**: the message is misleading — the real cause is a scheduler fire-claim loss. Confirm with `grep "fire claim ownership lost" ~/.hermes/logs/errors.log | grep <job-id>`; if the timestamp matches the job's `last_run_at` and `logs/gateway.log` shows no shutdown at that minute, it was a claim-ownership interruption, not a shutdown. The job's deliverable is often ALREADY WRITTEN — check `~/.hermes/cron/output/<id>/` and the artifact's own path (e.g. `research_outputs/`) before calling it a failure. Seen 4x between 09-09 and 09-12 (incl. the 09-12 Saturday Weekly Review, whose 16 KB report was produced at 06:03 before the 06:04 interrupt). Flag as a standing scheduler defect, do not re-escalate the individual jobs.
- **`Broken pipe` on agent-driven crons**: Stream stale/timeout. Built-in 3-attempt retry usually succeeds — **but check for a CLUSTER before calling it transient.** Several agent crons red in the same window with the same error is ONE provider event, and the retry only saves you if a fallback chain exists. Verified 2026-09-15: 8 jobs, `[Errno 32] Broken pipe` + `503 Service is too busy` from `provider=deepseek`, all dead at attempt 3/3 because the chain was empty — one outage, eight red jobs, no 6:00 AM briefing. See Task 3 step 2 for the cluster commands; resilience fix in `monitoring-alert-verification` + `llm-cost-routing`.
- **`Script timed out after 3600s` on `hermes_update_check.sh` (4eef20ef0e25)**: The `hermes update` step (git pull + npm rebuild + web UI build) is slow and can exceed the 3600s cron timeout even when the update SUCCEEDS. Check `~/.hermes/logs/hermes_update.log` first — if it ends with "✓ Code updated!" / "✓ Model catalog cache refreshed", the update applied and only the "Restart gateway" prompt was cut off (gateway is still running old code until its next natural restart). Escalate only if the log shows no "Code updated" line. Note: the 03:00 Mon+Fri run (`0 3 * * 1,5`) may also show `ok` vs `error` depending on whether the load-sleep (30 min) plus slow update fits in the window.

### Stale (error from previous run, job runs infrequently)
- **Weekly crons (Mon-only, Fri-only)**: An error from the last weekly run persists until the next schedule. Check the `last_run_at` date — if it's days old and the cron only runs once a week, it's stale.
- **Biweekly crons (Mon+Fri)**: Same pattern — error from Monday persists until Friday.

### Real-but-external (the monitor is fine, its UPSTREAM is down)
- **RE-CHECK EVERY STANDING FAULT RECORD AGAINST THE JOB'S OWN RECENT OUTPUT — do not copy it forward.**
  A "known persistent fault" note in this skill or in `environment.md` is a snapshot from the day it was
  written; the upstream can clear without anyone updating the note. Before reporting any standing fault,
  reconstruct its recent history from the job's own outputs:
  ```bash
  cd ~/.hermes/cron/output/<job-id>
  for f in $(ls -t | head -14); do echo "$f | $(grep 'OVERALL' "$f") | $(grep -A3 '<dataset> ━' "$f" | tail -2 | tr '\n' ' ')"; done
  ```
  That one loop shows the exact streak start/end and the recovery row. Seen 2026-09-26: `acnc-charities`
  had been recorded as UNRESOLVED for **two extra days** after it recovered on 2026-09-24 (9-day streak
  09-15→09-23, then a real `✅ Synced: 65,758 rows, Δ+59`). The record had been **copied forward** by
  successive maintenance runs instead of re-verified. Cost of the miss: two daily reports carried a
  false fault line and the skill actively told future agents not to look at it.
  **When you find a stale record: patch the skill, correct `environment.md`, and mirror the skill.** A
  fault record is only trustworthy on the run that re-derived it.
- **`acnc-charities` HTTP 500 — ✅ RESOLVED 2026-09-24, INCIDENT CLOSED (do NOT re-open; historical only).**
  Ran 2026-09-15 → 2026-09-23 (9 consecutive red runs), then recovered with a real sync. `937bb914c497`
  has been `OVERALL: ✅ PASS` on 09-24/09-25/09-26 (`NO_CHANGE · 65,758 rows`). The old signature was a
  bare 500 with no body detail, from an app-side fault (backend `/internal/sync/acnc-charities` handler
  or its Nector worker) — not the script, creds or source URL. **If a bare 500 reappears, treat it as a
  NEW occurrence of that fault class**, not as this incident continuing. Full triage: `amlhive-asic-sync`
  skill. Re-check the OTHER datasets each run — if they also go `NO_CHANGE` with a stale `last_synced_at`,
  that IS new and means the whole sync pipeline has stalled. CloudWatch triage: `amlhive-asic-sync` skill.
- **`🔴 dashboard /api/status unreachable on http://127.0.0.1:3009` (`4c28178fad0f`, CMDB Cost
  Monitor, 07:20 daily, `deliver: origin`)**: the monitor exits 1 because the Notion-CMDB dashboard
  plugin it reads is not running — `hermes dashboard --status` reports "No hermes dashboard or serve
  processes running" and `ss -tlnp` shows nothing on 3009 (nor on the 9119 default). **The blind
  output is the danger, not the exit code:** the run then prints `Assets: 0`, `Known spend: A$0.00`,
  `Δ vs last: ±A$0.00` — read as an all-clear that spend collapsed. Compare the day before in
  `~/.hermes/cron/output/4c28178fad0f/` — a healthy run shows `Assets: 38 (13 priced)` and
  `A$768.59/month`; a transition to 0/0.00 with `Connection refused` is the DOWN signature. Escalate
  as "start the :3009 dashboard" (owner: Haris), never as a monitor bug, and never report A$0 as
  real spend. Probing the LAN alias (192.168.50.210:3009) triggers the security scanner's
  private-network/plain-HTTP prompt and will hang waiting for approval in a cron — use the loopback
  check + `hermes dashboard --status` instead.

### Real (needs action)
- **`RuntimeError: Missing required environment variable: <KEY>` (cluster of same-day jobs, different
  scripts)**: a credential-hardening pass removed hardcoded values and pointed the scripts at env keys
  that **exist in neither `.env`**. The signature is a group of `no_agent` scripts failing on the import
  line within minutes of each other, each naming a DIFFERENT key (`SUPABASE_HOST`, `RDS_PW`, …) — one
  sweep, several dead jobs. Do not treat it as a config typo; check journal-style notes at
  `~/.hermes/ops/credential_exposure_fix_*.md` for the pass that did it, then:
  1. Confirm absence by NAME across both stores:
     `for f in /mnt/c/Users/habib/.hermes/.env ~/.hermes/.env; do grep -oE '^[A-Za-z_][A-Za-z0-9_]*' "$f"; done | sort -u`
  2. Prefer the **dynamic fetch a sibling already uses** (Secrets Manager / SSM) over adding an env key —
     e.g. `tapease_payout_email.py :: fetch_db_password()` resolves `tapease/rds/credentials-production`.
     Convert the module-level `_required_env("KEY")` into a lazy cached fetch so import no longer needs
     the secret.
  3. Verify by RUNNING the real path (fetch + one read-only query), not by `py_compile` — see the
     `credential-exposure-remediation` skill, whose dummy-value probe reported `KEY=loaded` for a key
     production did not have.
  Seen 2026-09-16: `tapease_daily_transactions.py` (`RDS_PW`), `pluto_chamber_refresh.py` +
  `podcast_ingestor.py` (`SUPABASE_HOST`) — the two Supabase scripts were repaired the same night by
  deriving creds from `SUPABASE_OPERATOR_SPOOLER_DATABASE_URL`; the Tapease one stayed broken until
  fixed here.
- **`state.db reported structural corruption` (cluster of agent crons, one morning)**: 8 agent-driven jobs
  died 06:27→11:01 with `RuntimeError: ⚠️ No reply: the turn was stopped because the state
  database reported structural corruption` (2026-09-17). The message is self-describing and
  prescriptive — classify it as **Real/systemic (one event, N red jobs)**, never as N separate bugs.
  The gateway refuses all writes and diverts transcripts to `~/.hermes/sessions/<id>.jsonl`
  (which is where you recover the lost turns). Triage order: (1) `hermes doctor --fix`; (2) snapshot
  the bundle — `cp -a state.db{,-wal,-shm}` into `~/.hermes/backups/` BEFORE anything touches it;
  (3) `hermes sessions recover --source ~/.hermes/state.db --inspect-only` — this is **safe on a live
  DB** (it copies the source + sidecars before SQLite opens anything) and prints
  `recoverable: true/false` plus per-table readability; (4) the actual repair needs the gateway
  STOPPED — `hermes sessions recover --source ... --output ~/.hermes/recovered-state.db`; the CLI
  never swaps the live DB (`installed: false`) so the restart is a manual step. **Never run
  `sqlite3 ".recover"` against the live file** (a vulnerable sqlite3 CLI corrupts it further).
  Confirming the outcome does NOT rely on the absence of log warnings — prove it with a read-only
  check on a COPY: `PRAGMA integrity_check` → `ok`, plus an `INSERT INTO messages_fts(messages_fts)
  VALUES('integrity-check')` on both FTS tables. The live DB had already been repaired by the time
  of the 23:38 restart (`integrity_check` = ok, 131,607 message rows, history continuous) while
  `jobs.json` still showed all 8 failures — **jobs.json is a lagging indicator; verify, don't assume
  the outage is still live.** Note `system sqlite3` is NOT installed on this host; use
  `~/.hermes/venv/bin/python -c "import sqlite3..."`.
- **`FATAL: password authentication failed`**: Credential is wrong or expired. For env-var-based scripts: check the env var. For SSM-based scripts (`amlhive_daily_report.py`): the AWS Secrets Manager secret (`amlhive/prod/rds`) is out of sync with the actual RDS password — needs AWS console fix (see RDS Credential Isolation pitfall below).
- **`Traceback` in script**: Genuine Python error. Read the traceback to diagnose.
- **`401 Unauthorized` on 3+ crons same day**: Systemic credential failure — check provider API keys, not individual crons.
- **`delivery_failed` with an EMPTY `last_error`**: the script ran and wrote its artifact — the failure is the outbound send, not the job. Confirm in `~/.hermes/logs/agent.log`: `Job '<id>': delivery error: Telegram send failed: Timed out (target telegram:<id>)`. Transient network / flood-control (seen 2026-09-13 07:00 on `8d3be30eb9f7`, whose output file was complete and healthy). Do not escalate unless it repeats on consecutive days — the next scheduled run resends.

## "Never Ran" — Genuine Bug vs Expected

A cron with `last_run_at: null` is NOT always a scheduler bug:

### Expected (do NOT escalate)
- **Weekly cron created mid-cycle**: E.g., a Friday-only cron created on Saturday. It won't fire for nearly a week. Check `next_run_at` — if it shows the correct upcoming day, it's fine. Example: `f7e6cb145925` (Weekly Evidence Summary, Fri 3PM) created Jul 18 (Sat) — next run Jul 24 (Fri). Expected.
- **Monthly cron**: Created mid-month, won't fire until the 1st of next month.

### Genuine Bug (escalate)
- **Daily cron** with `last_run_at: null` and `created_at` > 2 days ago. A daily cron should have fired by now.
- **Weekly cron** with `created_at` > 8 days ago and `next_run_at` in the past. The scheduler missed its window.
- Any cron where `enabled: true` but `next_run_at` is `null` or in the past.

**Verification:** Check `next_run_at` before escalating. Also check if the cron has an output directory in `~/.hermes/cron/output/<id>/` — presence of output files proves it ran even if jobs.json is ambiguous.

## RDS Credential Isolation (Pitfall)

The fleet monitors (`amlhive_prod_monitor.py`, `tapease_prod_monitor.py`) do **NOT** connect to RDS directly — they monitor via AWS API (EC2, CloudWatch, Docker, SSM). They never need database passwords.

**Only `amlhive_daily_report.py` connects to RDS** — and it fetches credentials dynamically from AWS Secrets Manager, not from env vars:

| Script | RDS Endpoint | Credential Source | Cron |
|--------|-------------|-------------------|------|
| `amlhive_daily_report.py` | `amlhive-prod.ch4ykiy82n3q` | AWS SSM `amlhive/prod/rds` via `fetch_pw()` | `3ebed4e59ee3` |
| `amlhive_prod_monitor.py` | N/A (no RDS connection) | N/A — uses AWS API only | `4f4dc2487b98` |

**Failure mode:** When the RDS password is rotated, the AWS Secrets Manager secret (`amlhive/prod/rds`) may not be updated in sync. The script fetches a stale/wrong password from SSM → `FATAL: password authentication failed`. The fleet monitors show `ok` because they don't touch RDS.

**Detection:** `grep 'fetch_pw\|secretsmanager\|amlhive/prod/rds' ~/.hermes/scripts/amlhive_daily_report.py` — confirms SSM-based credential fetching.

**Fix:** Update the secret in AWS Secrets Manager (`amlhive/prod/rds`) to match the current RDS master password. This requires AWS console access. Pluto cannot fix this autonomously.

See `pluto-fleet-monitor` skill for full AmLHive architecture.

## Retiring a service/monitor — the SECOND-ORDER sweep (verified Sep 2026)

First-order retirement (remove cron, archive script) is NOT enough — downstream
references keep the dead service "live" in docs, configs, and prompts for months.
Run the full sweep the same session you retire anything (Vercel example:
`vercel-monitoring` skill's "Second-order retirement sweep COMPLETED 2026-09-05"
record):

1. **Cron prompts** — grep jobs.json for the service name: every prompt/script
   reference must be replaced or the cron agent will cat stale report dirs.
2. **config.yaml keys** — Hermes REFUSES direct `patch` writes to config.yaml
   (security-protected). Use the CLI: `hermes config unset <dotted.path>` (e.g.
   `hermes config unset terminal.vercel_runtime`), then grep to verify gone.
3. **EVERY SKILL.md + references/** — grep -rln the name across ~/.hermes/skills/
   and update each live table/row/example (cron tables, delivery exceptions,
   pipeline diagrams, email example docstrings). Skip: RETIRED markers, dated
   historical incident logs, curator backups, unrelated design-system mentions.
4. **Scripts** — grep *.py docstrings/examples; a shared module's usage example
   that names the dead monitor propagates it into every future consumer.
5. **Stale data dirs** — archive old report JSONs to `~/.hermes/archive/...` and
   remove the empty dir so greps and `reviews/` scans stop hitting them.
6. **Leave a completion record** in the retired service's skill + note remaining
   string matches are INTENTIONAL — so no future agent re-audits or re-enables.

## Cron self-scheduling note
- A catch-up fire is not a config error: the 2026-09-17 run executed at **23:38** instead of its
  14:00 slot (the gateway was restarted at 23:38 after the state.db repair) and the 2026-09-18 run
  fired at 14:00:24 on time. Before flagging a wrong-time run, check whether a gateway
  restart/shutdown happened in that window — if the slot is held correctly the run after it is on
  time, and there is nothing to fix.

## Output

Save detailed results to `~/.hermes/reviews/daily/maintenance-{DATE}.json` with:
- Skills patched count
- Memory entries updated count
- Cron failures detected (breakdown by classification)
- Scripts broken count
- Any 🚨 alerts requiring immediate attention

Keep the user-facing report brief (under 5 min runtime target). Only surface what needs action.

## Pitfalls
- **Verify chat IDs from gateway logs BEFORE bulk-rerouting cron deliveries (Aug 2026).** When Haris says "use this group for X jobs", do NOT trust `channel_directory.json` — it stores stale internal names (it still said `daily_status_v2` for the AMLHive group after the retitle) and can miss newly-created groups. The session context shows the group's CURRENT title; the real chat ID is in the gateway log: `grep "inbound message" ~/.hermes/logs/gateway.log | tail -20` — the `chat=` on the line matching this session's first user message IS the group's ID. Then confirm with `cronjob action=list` that jobs show `deliver: telegram:<that-id>`. Mistake made 2026-08-13: assumed `-1003834479227` (daily_status_v2) was the AMLHive group, "confirmed" it, and told the user all jobs were already there when they landed in the wrong group. Correct split: AMLHive jobs → `-1004485329864`; general daily + TapEase jobs → `-1003834479227`; DM `5273126730`.
- **Do NOT `grep -i error` on cron output files.** Output files contain false-positive matches on the literal word "error" (JSON keys, section headers, normal output). Use `jobs.json` `last_status` field — it's authoritative.
- **Never-ran ≠ broken.** Always check `next_run_at` and the cron's schedule frequency before escalating.
- **Exit code 1 ≠ failure** for alert scripts that email internally. Check the script's design intent.
- **Memory.json may not exist.** Not all Hermes profiles use memory. Absence is not an error.
- **Cron `script` field is basename-only.** The `script` field in `jobs.json` contains just the filename (e.g., `mempalace_watcher.py`), not a full path. When verifying script paths on disk, prepend `~/.hermes/scripts/` before checking `os.path.exists()`. Without the prefix, every script-based cron will appear "missing" — a 100% false-positive rate. The scripts resolve correctly at runtime because Hermes's cron runner knows the scripts directory. **There are TWO scripts roots and they hold DIFFERENT files:** WSL `~/.hermes/scripts/` and Windows `/mnt/c/Users/habib/.hermes/scripts/` (e.g. `pluto_monthly_strategy_job.py` and `send_strategy_professional_email.py` exist ONLY on the Windows side). A cross-reference validator that checks just the WSL root reports ~100% false positives — check both before flagging a referenced script as missing.
- **Dead cron IDs in skills are usually intentional history.** A validator that flags every 12-hex token absent from `jobs.json` produces ~26 hits, almost all of them documented-retired jobs (`RETIRED` markers, `KNOWN_DEAD_*` sets, `pipeline-orchestration` history, raw-hex `vault/reports` folders like `0ccbb673faea` that alexandria-vault-sync documents as "leave those as historical"). Read the surrounding context before calling one stale; only a dead ID presented as a LIVE schedule is a real fix.
- **`ideas-*` grep is high-noise.** Several skills (fleet-intelligence, git-sync, weekly-review) legitimately contain `KNOWN_DEAD_REPOS = {'ideas-ndis', 'ideas-exitlens', ...}` lists or documentation referencing `ideas-*/` repo paths. A bare `grep -rl 'ideas-'` across skills will hit all of them. Before flagging a hit as stale, read 2-3 lines of surrounding context. Only escalate if it's an operational reference (e.g., a script hardcoding a dead repo path), not documentation or a KNOWN_DEAD_REPOS set.
- **Git token obfuscation → "Port number not decimal" error.** When a git sync cron fails with `GIT_FETCH_FAILED: URL rejected: Port number was not a decimal number`, do NOT assume it's only a display artifact. Check the repo's *actual* remote URL (`git remote -v` in the repo dir) — the real root cause seen 2026-08-13 was a **duplicated token in the remote URL**: `https://oauth2:TOKEN@oauth2:TOKEN@github.com/...` (two `@` + two `oauth2:` prefixes; git parses the second `oauth2:TOKEN` as host:port). **⚠️ Check the WINDOWS copy, not the WSL copy:** `daily_repo_sync.py` syncs `/mnt/c/Code/github/almhive-tech/amlhive1` (dir name misspelled `almhive-tech`, remote still `github.com/amlhive-tech`), while the test runner uses `~/code/amlhive1`. The WSL copy can be clean (`at_count:1`) while the Windows copy is corrupted (`at_count:2`) — recurred 2026-08-19 (2nd time after 2026-08-13). Verify the fix landed by re-checking `at_count==1` AND `git ls-remote` exit 0. Fix by deduplicating in-place and verifying auth before writing back:
  ```python
  # in repo dir, read .git/config, dedup, test, then write back
  fixed = re.sub(r'https://(oauth2:[^@]+)@\1@', r'https://\1@', raw)  # 2x@ -> 1x@
  subprocess.run(['git','ls-remote', fixed, 'HEAD'])  # exit 0 => token still valid, write back
  ```
  Note `daily_repo_sync.py` uses plain `git fetch origin` (token lives in the repo's remote URL, not the script), so the script itself is fine — inspect the remote URL, not the script. The `ghp_...` dots in `last_error` ARE the redaction layer, but the `@oauth2:` duplication is real.

  **ROOT CAUSE + FLEET-WIDE SCOPE (found 2026-08-26, 3rd recurrence):** The stacking comes from `remote.replace('https://', f'https://oauth2:{TOKEN}@')` in THREE scripts — `a2square_git_sync.py`, `a2square_test_runner.py`, `unified_weekly_report.py`. Because `str.replace` substitutes **every** occurrence of `https://`, and the existing remote already contains `oauth2:TOKEN@`, each run prepends another token (counts climbed 2x→3x→4x→11x→24x). The corruption was **not** isolated to `amlhive1` — a full scan of `/mnt/c/code/github` found **22 repos** affected (a2_square ×5, almhive-tech ×5, haris-admin ×12). Fix applied: (1) dedup all 22 configs by extracting the first token + rebuilding `https://oauth2:TOKEN@github.com/<path>`, verifying with `git ls-remote` before write-back; (2) patched all 3 scripts to strip-and-set (`_base = remote[remote.index('github.com'):]; auth_remote = f'https://oauth2:{TOKEN}@{_base}'`). If this recurs AGAIN, grep the scripts for `replace('https://', f'https://oauth2:` — any new script with that pattern is the culprit. `unified_git_sync.py` already has the correct strip-then-set pattern; `a2square_weekly_test_runner.py` already uses `x-access-token` basic-auth. `git_sync.py`'s `.replace` sites are clone-path only (clean API `clone_url`) — safe.
