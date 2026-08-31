# W29 Diagnostic Findings — July 24, 2026

## 🔴 Gateway Shutdown — Simultaneous Cron Kills

**Pattern discovered:** When the Hermes gateway shuts down for maintenance or restart, it sends `final-cleanup` signals that kill all running tool subprocesses. This produces identical-timestamp errors across multiple crons.

**This week:** `4eef20ef0e25` (Hermes Update Check) and `d4d77c41f6c0` (Podcast KB Ingestion) both killed at `2026-07-24T04:04:42`.

**Detection:** Look for crons with `last_error: "Gateway shutdown (final-cleanup) killed the job's tool subprocess"` sharing the same `last_run_at` timestamp. These are NOT real failures — the gateway restart caused them, not the cron scripts.

**Reporting:** Group gateway-shutdown crons together. Count them as "transient — gateway restart" not as separate failures. Do not escalate.

---

## 🔴 AML Hive DB Password Auth Failure

**Pattern:** `psql: FATAL: password authentication failed for user "amlhive"` — the RDS password fetched via SSM has changed or the SSM parameter was rotated.

**Script:** `amlhive_daily_report.py` line ~58 fetches password via `ssm()` → `psql()`.

**Detection:** `RuntimeError: SSM: psql: error: connection to server at "amlhive-prod.ch4ykiy82n3q.ap-southeast-2.rds.amazonaws.com" ... FATAL: password authentication failed`

**Impact:** Daily business report goes dark. Secondary: the same SSM path may be used by other scripts.

**Human action needed:** Verify RDS master password rotation status and SSM parameter path. Pluto cannot fix this autonomously.

---

## 🟡 Git Index Lock on /mnt/c/ Filesystem

**Pattern:** `fatal: Unable to create '/mnt/c/Code/github/almhive-tech/amlhive1/.git/index.lock': File exists.` — Another git process on the Windows side holds the lock.

**Root cause:** WSL accessing git repos on the Windows filesystem (`/mnt/c/`). Windows git processes (VS Code, GitHub Desktop, etc.) can leave stale locks that block WSL git operations.

**Detection:** `GIT_RESET_FAILED` in cron output for `0dbba3db3116` (Daily Repo Sync).

**Fix:** Add retry logic: `rm -f /mnt/c/Code/github/almhive-tech/amlhive1/.git/index.lock` before git operations, or add a 30s retry loop. The lock is almost always stale.

---

## 🟡 Test Suite Exit Code 1 With Many Passing Tests

**Pattern:** `044c0bc41e31` (AMLHive Daily Test Suite) exits code 1 despite 838+ tests passing. A few tests are failing but the cron output is truncated — the specific failures are invisible.

**Detection:** `Script exited with code 1` + `838 passed` visible in stdout. Need to view full cron output to identify failing tests.

**Fix:** Either increase the truncation limit or have the script write test failures to a separate file for diagnostics.

---

## 🟡 ASIC Intentionally Disabled — Should Exit 0

**Pattern:** User's standing order is "no asic trying for now" (from memory). The ASIC Ref-DB sync script exits code 1 when `CSV URL for asic-registered-schemes is not configured`. The `acnc-charities` portion works fine.

**Detection:** `HTTP 503 — "CSV URL for asic-registered-schemes is not configured (set the env var)"` in `937bb914c497` output.

**Fix:** Script should check if ASIC is intentionally disabled (missing env var = disabled) and exit 0, not 1. Only exit 1 on actual connection/auth failures.

---

## 🟡 Daily Learning — Fixed Location, Wrong Content Size

**Pattern (update to W28 finding):** The misrouting is fixed — 7/7 files now in `research_outputs/daily-learning-*.md`. BUT the files are 1.6-3.4KB while the full cron output in `cron/output/0fb6bf47f704/` is 68KB. The research_outputs versions are summaries, not the full learning synthesis.

**Detection:** Compare `wc -c research_outputs/daily-learning-*.md` (~2.7KB avg) vs `wc -c cron/output/0fb6bf47f704/*.md` (~68KB avg). If research_outputs files are <5% of cron/output size, they're summaries.

**Fix:** Update cron prompt for `0fb6bf47f704` to write the FULL output to research_outputs, not a summary.

---

## 🟡 Honcho Bridge State File — Unbounded Growth

**Pattern:** `.honcho_bridge_state.json` accumulates every pushed file since inception (now 85+ entries back to Jul 8). The `pushed_files` array grows without bound.

**Detection:** `wc -l ~/.hermes/research_outputs/.honcho_bridge_state.json` — if it's above 100 lines, the array is growing.

**Fix:** Either rotate the file weekly (keep last 14 days only) or use a hash set for deduplication instead of a growing array.
