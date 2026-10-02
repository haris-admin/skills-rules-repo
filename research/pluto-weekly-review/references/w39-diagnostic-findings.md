# W39 Diagnostic Findings — week ending 2026-09-21

Context: normal Friday run happened on schedule (2026-09-18 23:10). A **second, off-schedule run** of
`cc5ca5690d05` was claimed Monday 2026-09-21 12:14:11. Do not treat that as user intent — see #2.

## 🔴 Cold-start catch-up re-runs jobs that already completed (NEW CLASS)

**Symptom:** After a gateway cold start, a burst of LLM jobs run at a time unrelated to their schedule
(W39: 11 jobs from the 05:02–06:45 morning chain re-ran at 12:02–12:13, plus the Friday-only weekly review).

**Fingerprint (do this, don't infer):**
```bash
python3 - <<'PY'
import sqlite3
c=sqlite3.connect('/home/habib/.hermes/cron/executions.db');cur=c.cursor()
cur.execute("SELECT source,count(*) FROM executions WHERE started_at LIKE '<DATE>%' GROUP BY source")
print(cur.fetchall())                      # builtin vs direct
cur.execute("SELECT job_id,started_at,status FROM executions WHERE source='direct' AND started_at LIKE '<DATE>%' ORDER BY started_at")
print(cur.fetchall())
PY
cat ~/.hermes/cron/catch_up_occurrences      # count of catch-up occurrences in the last event
```
`source='direct'` + `scheduled_instant IS NULL` = an unscheduled, dispatcher-injected run. A job showing
**both** a `builtin` row and a later `direct` row on the same day ran twice.

**Real harm to report (not just cost):** pipeline artifacts are overwritten *after* the delivered briefing
consumed them (W39: `actions_<date>.json` and `competitor_intel_<date>.json` rewritten at 12:06/12:13, hours
after the 06:02 briefing) — the on-disk record no longer matches what was delivered.

**Always verify schedule integrity before reporting drift:**
```bash
python3 -c "import json;j=json.load(open('/home/habib/.hermes/cron/jobs.json'));jobs=j if isinstance(j,list) else j.get('jobs',j);jobs=jobs if isinstance(jobs,list) else list(jobs.values());[print(x['id'],x['schedule']['expr'],x.get('last_run_at'),x.get('next_run_at')) for x in jobs if x['id'] in (...)]"
```
`next_run_at` staying anchored to the schedule (W39: all 11 correct, weekly job still Fri 2026-09-25 23:05) means
**no permanent drift** — say so explicitly instead of implying the schedule is damaged.

## 🔴 Gateway dual-instance respawn storm (NEW CLASS)

**Symptom:** `errors.log` fills with a repeating pair:
```
ERROR gateway.run: Another gateway instance is already running (PID N, HERMES_HOME=/home/habib/.hermes)
WARNING hermes_cli.gateway: Gateway (re)started 8 times in 120s — backing off 40s to break a respawn storm
ERROR gateway.run: Refusing --replace: PID N cannot be proven to belong to this profile's gateway
```

**Detection:**
```bash
timeout 20 ~/.hermes/venv/bin/hermes gateway status | grep -E 'Active|Main PID|restart counter'
grep -c 'already running' ~/.hermes/logs/errors.log
ps -o pid,ppid,lstart,cmd -p <PID>      # ppid=1 + tty pts/N = started OUTSIDE systemd
cat ~/.hermes/gateway_state.json        # recorded pid + argv
```
W39: systemd restart counter climbed 31 → 36 within 2 minutes; the live gateway was PID 574 (ppid=1, `pts/1`,
started 12:03:09 after a WSL reboot) while `hermes-gateway.service` (`Restart=always`, `StartLimitIntervalSec=0`)
kept spawning instances that could not take over because `gateway_state.json` recorded
`argv ['/home/habib/.hermes/venv/bin/hermes','gateway']` while the live process ran under
`/home/habib/.hermes/repo/venv/bin/python3 …` — argv/start-time mismatch ⇒ ownership unprovable ⇒ exit non-zero ⇒ respawn.
Also check for the banner **"Installed gateway service definition is outdated"**.

**Rule — never fix this from inside a cron.** `hermes gateway restart` kills in-flight tool subprocesses, and the
live gateway is the parent of the current run: restarting it kills this review mid-flight and no report is written
(the `GATEWAY_SHUTDOWN` "final-cleanup" class). Report it as a P0 with the exact remedy
(`hermes gateway restart`, run when no cron is mid-flight) and state explicitly that you did not execute it and why.

## 🟠 ACNC 500 ↔ product-repo issue ID (correlate before blaming the script)

`937bb914c497` failed 7/7 with `acnc-charities → ❌ HTTP 500 — {"detail":"Internal Server Error"}` while the ASIC
datasets degraded correctly (`NO_CHANGE`, and `Skipped (intentionally unavailable): DATASET_SOURCE_UNAVAILABLE`).
The matching issue was already logged in the AMLHive repo and surfaced in the *test-suite* log the same week:
`docs(prod-issues): log issue-375 (ACNC sync audit write RLS violation)`. **Read the AMLHive test-suite commit line
before reporting an internal-API 500 as a Pluto script bug** — a 500 that is an app-side RLS violation is not fixable
in `~/.hermes/scripts/`.

## 🟡 `skills-rules-repo` merge failure emits an EMPTY reason

`git_sync` reports `⚠️ skills-rules-repo: merge failed (4.2s) — ` with nothing after the em-dash, on 19 runs in one
week, and the repo is **not** in `KNOWN_DEAD_REPOS`. Empty failure text is why a daily failure survives unnoticed:
when a script failure line has no detail, report the logging gap as its own item, not just the failure.

## ⚠️ Off-schedule runs of this review are real and must be labelled

Check `fire_claim` in `jobs.json` for `cc5ca5690d05` and the `source` of the matching `executions.db` row. If the
claim timestamp is not a Friday ~23:05, label the report `off-schedule catch-up run`, name the prior on-schedule
review file as the canonical one for its week, and scope the failure tally to the window you actually measured
(rolling 7 days) versus the incremental window since the last review. Never silently present an off-schedule run
as the Friday review.

## ✅ Verified-working (do not re-flag this week)

- **Alexandria self-heal closed.** The Sep 16–17 `rebase failed: cannot pull with rebase: You have unstaged changes`
runs stopped on their own; Sep 18–21 are clean (21 of 25 runs in the window). Re-open only if that exact message returns.
- **`state.db` corruption genuinely repaired** — `PRAGMA integrity_check` on the live 633 MB file returns `ok`;
the Sep 17 state-corruption failures (Blog Posts via Codex, Metadata/Blog/Social Audit) do not reproduce.
- **CMDB Cost Monitor's direct-Notion path works** (`✅ Notion CMDB live`) — the Sep 17–20 zeros were a dead local
dashboard on `127.0.0.1:3009`, not the monitor.
- **Feedback degeneracy detector works** (exit 3 + machine-readable diagnostics). The detector is fine; the *feed*
is the blocker.

## 🔢 Numbers to reuse

- Week tallies: 521 output runs / 78 jobs; 51 failed runs / 24 jobs (output-derived) vs 7 errors (snapshot).
- Podcast: **106 episodes over 6 days** (14,-,20,16,22,19,15); Sep 16 failed on `Missing required environment
  variable: SUPABASE_HOST` — the cold-worker env class, not the ingestor.
- Haris inbound Telegram: 65 in 7 days, 26 since Friday (count from `logs/gateway.log`
  `inbound message: platform=telegram user=Haris`). Ignore the Sep 17 12:00–13:00 skew (1416/1073 lines) as an anomaly.
- Default `deepseek-flash` provider context detected at 1,000,000 tokens on this host.
