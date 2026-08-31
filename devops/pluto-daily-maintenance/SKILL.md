---
name: pluto-daily-maintenance
description: Pluto's lightweight daily maintenance engine — 4-task health check (skills, memory, cron, scripts) run at 2:00 PM AEST. Focus on keeping things running, not dreaming. Saturday deep reviews handle the heavy lifting.
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

### Task 2: Memory Grooming
1. Check `~/.hermes/memories/MEMORY.md` for stale entries
2. Remove/update entries referencing old repo names, old cron schedules, outdated facts
3. Also check for naming drift — e.g., memory says "Tapease payout sweep" but cron script is `tapease_payout_email.py`; the daily transactions cron (`114039a7ff9b`) uses `tapease_daily_transactions.py` for CSV export, while the payout email cron (`77f0402cb1de`) uses `tapease_payout_email.py`. Another recurring drift: `gmail_health_check.py` (4:50 AM pre-flight) looks for `GMAIL_USER`/`GMAIL_APP_PASSWORD`, but the working ingestor uses `GOOGLE_GMAIL_APP_PASSWORD_MACARTHUR` + hardcoded `macarthurgarments@gmail.com` — when Gmail creds migrate, the health-check's env-var names must be updated in lockstep or it exits 2 ("CONFIG MISSING") forever.
4. If no MEMORY.md exists, note it — not an error

### Task 3: Cron Health Pulse
1. Parse `~/.hermes/cron/jobs.json` for `last_status` counts
2. Classify each error using the error classification guide below
3. Verify script paths exist for all `no_agent` script-based crons (see Pitfalls: `script` field is basename-only — prepend `~/.hermes/scripts/`)
4. Check for "never ran" crons — distinguish genuine scheduler bugs from weekly crons awaiting their first window

### Task 4: Script Validation
1. Check Python syntax of recently modified scripts: `python3 -m py_compile <script>`
2. Verify all script paths referenced in cron jobs exist on disk
3. Report broken scripts immediately

## Error Classification Guide

When you see `last_status: error` on a cron, classify before escalating:

### 🚫 No Fake Pass Rule (Aug 2026 — Haris explicit: "put a rule to not to do the fake pass")

**A check that did not actually verify is NEVER a PASS.** This is a classification rule for ALL cron scripts, monitors, and test runners — not just errors:

- `DATASET_SOURCE_UNAVAILABLE` / source-not-configured → **ALERT**, never "skipped, pass". Seen 2026-08-15: `amlhive_asic_sync.py` collapsed every `skipped=true` reason into `⏭️ Skipped (no change)` → summary said ✅ PASS while `asic-registered-schemes` never synced (empty `ASIC_REGISTERED_SCHEMES_CSV_URL`). Fix: classify reasons explicitly — `DATASET_SOURCE_UNAVAILABLE → overall_alert=True`; only `NO_CHANGE` / `FILE_NOT_YET_PUBLISHED` pass.
- 0 tests collected / config-parse error → **ERROR**, never "0 passed" (test-runner false-green, Aug 2026; see `wsl-cron-test-runner` for the `guard_no_tests` pattern).
- A `skipped=true` / `ok` field in a script's own output is only a PASS when the underlying check genuinely completed.
- When auditing a cron that reports "ok" but skips work, read the script's reason classification before trusting the summary icon.

### By-Design (NOT errors — do NOT escalate)
- **`amlhive_prod_monitor.py` exit code 1**: The fleet monitor exits 1 when incidents are found (RLS bypass probes, API 500s, CloudWatch alarms). Email IS the alert mechanism. This is documented behavior. Verify by checking the output file for incident details — if present, the monitor worked correctly. The 11AM run often shows `ok` because incidents cleared by then.
- **Alert scripts that email internally**: Any script that sends its own email alerts should exit 0 even on findings. If it exits 1, it's a false-positive in cron health. See `pipeline-orchestration` skill's "Design rule for no_agent alert scripts."

### Transient (watch, auto-recovers)
- **`GIT_TIMEOUT`**: Script stdout contains `GIT_TIMEOUT`. Network/git-remote issue. Usually self-resolves next run. Escalate only if 3+ consecutive days.
- **Gateway shutdown**: `Gateway shutdown (final-cleanup) killed the job's tool subprocess`. Caused by gateway restarts. Auto-recovers next cycle.
- **`Broken pipe` on agent-driven crons**: Stream stale/timeout. Built-in 3-attempt retry usually succeeds.
- **`Script timed out after 3600s` on `hermes_update_check.sh` (4eef20ef0e25)**: The `hermes update` step (git pull + npm rebuild + web UI build) is slow and can exceed the 3600s cron timeout even when the update SUCCEEDS. Check `~/.hermes/logs/hermes_update.log` first — if it ends with "✓ Code updated!" / "✓ Model catalog cache refreshed", the update applied and only the "Restart gateway" prompt was cut off (gateway is still running old code until its next natural restart). Escalate only if the log shows no "Code updated" line. Note: the 04:00 run may also show `ok` vs `error` depending on whether the load-sleep (30 min) plus slow update fits in the window.

### Stale (error from previous run, job runs infrequently)
- **Weekly crons (Mon-only, Fri-only)**: An error from the last weekly run persists until the next schedule. Check the `last_run_at` date — if it's days old and the cron only runs once a week, it's stale.
- **Biweekly crons (Mon+Fri)**: Same pattern — error from Monday persists until Friday.

### Real (needs action)
- **`FATAL: password authentication failed`**: Credential is wrong or expired. For env-var-based scripts: check the env var. For SSM-based scripts (`amlhive_daily_report.py`): the AWS Secrets Manager secret (`amlhive/prod/rds`) is out of sync with the actual RDS password — needs AWS console fix (see RDS Credential Isolation pitfall below).
- **`Traceback` in script**: Genuine Python error. Read the traceback to diagnose.
- **`401 Unauthorized` on 3+ crons same day**: Systemic credential failure — check provider API keys, not individual crons.

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
- **Cron `script` field is basename-only.** The `script` field in `jobs.json` contains just the filename (e.g., `mempalace_watcher.py`), not a full path. When verifying script paths on disk, prepend `~/.hermes/scripts/` before checking `os.path.exists()`. Without the prefix, every script-based cron will appear "missing" — a 100% false-positive rate. The scripts resolve correctly at runtime because Hermes's cron runner knows the scripts directory.
- **`ideas-*` grep is high-noise.** Several skills (fleet-intelligence, git-sync, weekly-review) legitimately contain `KNOWN_DEAD_REPOS = {'ideas-ndis', 'ideas-exitlens', ...}` lists or documentation referencing `ideas-*/` repo paths. A bare `grep -rl 'ideas-'` across skills will hit all of them. Before flagging a hit as stale, read 2-3 lines of surrounding context. Only escalate if it's an operational reference (e.g., a script hardcoding a dead repo path), not documentation or a KNOWN_DEAD_REPOS set.
- **Git token obfuscation → "Port number not decimal" error.** When a git sync cron fails with `GIT_FETCH_FAILED: URL rejected: Port number was not a decimal number`, do NOT assume it's only a display artifact. Check the repo's *actual* remote URL (`git remote -v` in the repo dir) — the real root cause seen 2026-08-13 was a **duplicated token in the remote URL**: `https://oauth2:TOKEN@oauth2:TOKEN@github.com/...` (two `@` + two `oauth2:` prefixes; git parses the second `oauth2:TOKEN` as host:port). **⚠️ Check the WINDOWS copy, not the WSL copy:** `daily_repo_sync.py` syncs `/mnt/c/Code/github/almhive-tech/amlhive1` (dir name misspelled `almhive-tech`, remote still `github.com/amlhive-tech`), while the test runner uses `~/code/amlhive1`. The WSL copy can be clean (`at_count:1`) while the Windows copy is corrupted (`at_count:2`) — recurred 2026-08-19 (2nd time after 2026-08-13). Verify the fix landed by re-checking `at_count==1` AND `git ls-remote` exit 0. Fix by deduplicating in-place and verifying auth before writing back:
  ```python
  # in repo dir, read .git/config, dedup, test, then write back
  fixed = re.sub(r'https://(oauth2:[^@]+)@\1@', r'https://\1@', raw)  # 2x@ -> 1x@
  subprocess.run(['git','ls-remote', fixed, 'HEAD'])  # exit 0 => token still valid, write back
  ```
  Note `daily_repo_sync.py` uses plain `git fetch origin` (token lives in the repo's remote URL, not the script), so the script itself is fine — inspect the remote URL, not the script. The `ghp_...` dots in `last_error` ARE the redaction layer, but the `@oauth2:` duplication is real.

  **ROOT CAUSE + FLEET-WIDE SCOPE (found 2026-08-26, 3rd recurrence):** The stacking comes from `remote.replace('https://', f'https://oauth2:{TOKEN}@')` in THREE scripts — `a2square_git_sync.py`, `a2square_test_runner.py`, `unified_weekly_report.py`. Because `str.replace` substitutes **every** occurrence of `https://`, and the existing remote already contains `oauth2:TOKEN@`, each run prepends another token (counts climbed 2x→3x→4x→11x→24x). The corruption was **not** isolated to `amlhive1` — a full scan of `/mnt/c/code/github` found **22 repos** affected (a2_square ×5, almhive-tech ×5, haris-admin ×12). Fix applied: (1) dedup all 22 configs by extracting the first token + rebuilding `https://oauth2:TOKEN@github.com/<path>`, verifying with `git ls-remote` before write-back; (2) patched all 3 scripts to strip-and-set (`_base = remote[remote.index('github.com'):]; auth_remote = f'https://oauth2:{TOKEN}@{_base}'`). If this recurs AGAIN, grep the scripts for `replace('https://', f'https://oauth2:` — any new script with that pattern is the culprit. `unified_git_sync.py` already has the correct strip-then-set pattern; `a2square_weekly_test_runner.py` already uses `x-access-token` basic-auth. `git_sync.py`'s `.replace` sites are clone-path only (clean API `clone_url`) — safe.
