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

## Fast path (run these first, then read only what a finding points at)
1. `python3 ~/.hermes/scripts/daily_cron_audit.py` — script paths, delivery targets, non-ok jobs, clustering, staleness.
2. `python3 ~/.hermes/scripts/daily_skill_scan.py` — usage from `state.db`, SKILL.md touches in 24h, legacy refs, dead cron IDs.
3. Fleet-mirror hash scan (Task 1 step 5) **plus** a per-skill `diff | grep -c '^[<>]'` before picking a direction (step 6).
4. Both alexandria clones: `git log -1` + `git rev-list --left-right --count origin/main...HEAD` (must read `0\t0`).
5. `python3 -m py_compile` every script modified in 24h (`find scripts -maxdepth 1 -name '*.py' -newermt '-24 hours'`).
6. Memory: record-then-groom in ONE batched call; confirm the reported current/limit.
Then write `~/.hermes/reviews/daily/maintenance-{DATE}.json` and report the status block. Classification rules: "Error Classification Guide" for any non-ok job, "Task 2b" for memory architecture, "Task 3" for Alexandria.

## The 4-Task Procedure

### Task 1: Skill Health Check
1. Load skills used/referenced in the last 24 hours
2. Check for stale references: old repo names (`ideas-*-au` → `ideas-*`), dead file paths, wrong cron times
2b. **Audit the schedule EXPR, never the job NAME — a stale NAME survives every expr change.** Cron job
   names are free text and are not rewritten when the schedule moves. Seen 2026-10-01: `044c0bc41e31` is
   named `★ AMLHive Daily Test Suite (03:00 AM)` while its live expr is `40 3 * * *` (fires 03:40) — the
   name had been stale since a contention-driven move, and three skills plus `environment.md` had copied
   the NAME's time forward as fact. When reconciling a documented time against `cron list`/`jobs.json`,
   trust `schedule.expr` (and the run's own stdout timestamp) and fix the DOCS, not the expr; flag the
   stale name to the owner rather than renaming the job from this tick.
3. Patch minor issues immediately; flag severe staleness for Saturday
4. Check for old pruned cron IDs referenced outside of `pipeline-orchestration` (historical documentation)
5. **Fleet-mirror drift — the biggest silent gap (added 2026-09-23).** `daily_skill_scan.py` does NOT
   compare skill CONTENT against the canonical repo, so a skill can be patched in WSL for weeks while
   the copy every other agent reads stays old. Scan by normalised hash, not mtime:

   ```bash
   python3 - <<'EOF'
   import hashlib
   from pathlib import Path
   L=Path.home()/'.hermes/skills'; R=Path('/mnt/c/Code/github/haris-admin/skills-rules-repo')
   def sk(root):
       d={}
       for p in root.rglob('SKILL.md'):
           c=p.read_text(encoding='utf-8',errors='replace').replace('\r\n','\n').strip()
           d[str(p.relative_to(root))]=hashlib.md5(c.encode()).hexdigest()
       return d
   l,r=sk(L),sk(R)
   print('MISSING IN REPO:', [k for k in l if k not in r])
   print('DIFFERS:', [k for k in l if k in r and l[k]!=r[k]])
   EOF
   ```

   Normalise CRLF on BOTH sides or every `/mnt/c` file reads as changed. Two classes of result:
   (a) **repairable now** — a skill absent from the repo entirely is a pure ADD: copy it in, run the
   frontmatter check, then path-scoped `git add -- <paths>` + `git commit -m "..." -- <paths>` + push.
   **A 1/1 diff is NOT a merge — it is one stale line in the repo replaced by the WSL line.** When
   `repo-only` lines are just SUPERSEDED VARIANTS of WSL lines (`Action Bridge (5:15)` vs `(5:17)`,
   `OpenAI Nova` vs `Gemini Kore`), the WSL copy is still the superset and the fix is a straight
   `cp` WSL→repo, then require `0` diff-lines. Only treat repo-only lines as a merge when they carry
   content the WSL side has NO equivalent of (a section, not a correction). Seen 2026-11-24: four
   skills flagged `DIFFERS` were all pure corrections (5:17 timing, Gemini TTS, reach-metric wording)
   and mirrored in one scoped commit.
   (b) **Saturday scope** — a copy that DIFFERS needs a MERGE, because the repo side often carries
   sections the WSL side never had (see the fleet-skill-governance merge pitfall); a blind overwrite
   deletes them. Report the differing list, do not bulk-overwrite it from a daily tick.
   **Reconciling a divergent copy — insert at a CONTENT anchor and prove it with the repo-only count.**
   The hash scan keys by parent-dir NAME, so it flags real divergences (not just path differences) as
   `DIFFERS` even when the repo copy simply lacks a section the WSL copy gained. Test before touching:
   `diff <(sed 's/\r$//' $REPO) <(sed 's/\r$//' $WSL) | grep -c '^<'` — **0 repo-only lines means the repo
   copy is a strict subset and the change is a pure ADD**: insert the block at a UNIQUE SENTENCE anchor
   (never at `## Related` or any heading that may appear more than once — anchoring on a heading the first
   time put the block at the file END and the divergence survived), then re-run the diff and require BOTH
   counts to read 0 before `git add -- <path>`. Seen 2026-10-11 on `fleet-skill-governance`: WSL ahead by
   23 lines (`## Adopting a new STANDARD (not just a skill) — it lands on four surfaces`), repo-only 0 →
   additive mirror, commit `ff21de9`, repo/WSL 0/0 afterwards. If repo-only > 0, it is a MERGE — Saturday scope.
   **Re-measured 2026-11-25 (`.archive` excluded both sides): repo 416 SKILL.md vs WSL 178; 59 absent
   by name, 81 content-differing.** The count drifts with corpus growth — judge the CLASS, never the
   number. Compare by skill NAME, not path (`devops/fleet-skill-governance` reads as repo-absent only
   because the repo files it under `agent-governance-and-git/`, byte-identical), and never trust a
   DIFFERS hit without the line count: the hash keys by parent-dir name, the repo carries duplicate
   names (`apple-notes`, `apple-reminders`, `monitoring-alert-verification`, `vulnerability-watcher`),
   and a TRAILING-NEWLINE-only difference hashes as a full divergence while `diff … | grep -c '^[<>]'`
   reads **0/0** (2026-11-12, `tapease-upstream-watch`). A 24h-touched skill with `repo_only=0` is a
   pure ADD → `cp` WSL→repo, require `0` diff-lines, path-scoped commit+push (2026-11-25: mirrored
   `monitoring-alert-verification`, `web-data-acquisition`, `handledispute-merchant-research` + 3
   repo-absent Mercury skills, commit `af538c4`). `repo_only>0` is MERGE scope —
   `pluto-autonomous-research` (31 repo-only lines) is the standing Saturday item.

6. **Mirror drift runs BOTH ways — the repo copy can be the superset.** Every note above frames the WSL
   copy as the newer one, so a STALE WSL copy reads as `DIFFERS` and gets "merged" in the wrong
   direction. Count both sides first (`diff <(sed 's/\r$//' $R) <(sed 's/\r$//' $W) | grep -c '^[<>]'`)
   and read the repo-only lines before picking a direction. Seen 2026-11-27: `fleet-skill-governance`
   had 10 repo-only lines carrying the path-scoped `git add -- <cat>/<skill>` + `validate.py` /
   `generate_catalog.py` procedure while the WSL copy still said `git add -A` (forbidden) — the repo was
   canonical and the fix was repo→WSL, i.e. NO repo commit; `pluto-content-firewall` had lost its
   `## Additional references` section in WSL while the repo still carried it (also repo→WSL); and
   `au-vc-funding-radar` was the ordinary WSL→repo case. Rule: a repo-only line that CORRECTS or EXTENDS
   an existing WSL line → adopt repo→WSL and re-verify 0/0; only a repo-only SECTION on a different
   subject is a merge.

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

**Alexandria writer check (step 5).** Both alexandria writers are `no_agent` scripts that push to
`haris-admin/alexandria` (`fc726783497f`) and `haris-admin/alexandria-ops` (`1dc6606ac8c5`). Verify by
date, not by status: `cd /mnt/c/Code/github/haris-admin/alexandria && git log -1 --format='%h %ad %s'
--date=iso && git rev-list --left-right --count origin/main...HEAD` (the count must read `0\t0` —
anything else means an unpushed commit). A non-zero `git status --porcelain` on `alexandria-ops` is
usually an untracked cron-output subdir (e.g. `?? podcast-capture/`) and is NOT a push failure.
**But "untracked" is not automatically benign — check whether it was EVER tracked before writing it off.**
`git ls-files <dir> | wc -l` = 0 AND `git check-ignore -v <dir>` fails means nothing in that tree has ever
reached the remote: every report that calls it "known untracked, not a failure" is describing an unbacked
data leg. Verified 2026-11-26: `alexandria-ops/podcast-capture/` held 881 files / 15 MB (12 new in 24 h,
not ignored, zero tracked) and had been excused this way in daily reports since 27 Sep, while
`environment.md` describes it as the immutable per-episode raw record. Report the age, file count and
size, say plainly that the record exists only on this box, and put the commit-vs-gitignore choice to the
owner — do not mass-commit raw JSON unasked and do not keep repeating the benign phrasing.
**`FileNotFoundError` raised inside `drain_reports()` is a TOCTOU against a SELF-PRUNING source dir,
not a missing path and not a repo problem.** Seen 2026-10-25 11:08: `alexandria_ops_sync.py:132` died on
`os.path.getsize('/home/habib/.hermes/cron/output/5678a363ce3b/2026-10-25_01-45-15.md')` — `5678a363ce3b`
is the every-5-minute MemPalace Inbox Watcher whose output dir holds only ~50 files, so a path captured
by `listdir()` can be rotated away before the `stat()`. Tell-tale second symptom: the run had already
pruned earlier folders, so the tree carried **uncommitted `D` deletions + untracked new reports** while
`rev-list` still read `0 0` — the writer is NOT atomic, and a crash leaves the prune half-applied until
the next successful run commits it. Fix = wrap the size comparison in `try/except OSError: continue`
(patched 2026-10-25); prove it with `--dry-run` then a real run, and require the SECOND run to print
`0 copied, 0 pruned` + `no changes` (idempotency) before calling it fixed. Never "fix" this by widening
retention on the watcher.

**Run the hardened helpers first — they cover Task 1 and Task 3 steps 1-4 + 6 in one pass:**
`python3 ~/.hermes/scripts/daily_cron_audit.py` (script-path resolution against BOTH script roots,
delivery-target histogram, non-ok jobs grouped by delivery, enabled jobs with null/past
`next_run_at`, **plus `=== error clustering ===` and `=== staleness classification ===`** — step 2
below is now automated, read it instead of clustering by eye) and `python3 ~/.hermes/scripts/daily_skill_scan.py` (skill usage **from `state.db` tool_calls** + SKILL.md touches in
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
6. **Audit DELIVERY TARGETS, not just statuses.** Group every job by `deliver` and count per target; each must point at a live target from the routing table (`telegram:-1004485329864` AMLHive-subject, `telegram:-1003834479227` general/daily, `telegram:-5552363922` TAPEase-upstream-watch only — `e68234a738eb`, does NOT belong to the fleet-monitor group) or `local`. A job can report `last_status: ok` every single run while delivering into a retired channel — `ok` only means it RAN. **When the owner says a report or sweep "isn't firing", check `deliver` before debugging the job itself**; a sweep that runs perfectly into a retired channel reads as "not firing" forever. Retarget with `cronjob(action="update", job_id=..., deliver="telegram:<id>")`, then re-verify. Re-run this audit after ANY channel change or owner routing instruction: jobs that were correct when the change was made silently rot afterwards.

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
3. Verify all script paths referenced in cron jobs exist on disk (prepend `~/.hermes/scripts/` — the `script` field is basename-only). **A basename miss on an `enabled: false` job is usually a RETIREMENT, not a break: retired scripts are moved to `~/.hermes/scripts/retired/` while the job record keeps the old basename** (seen 2026-11-22, `a0b1f0f642af` → `retired/pluto_fleet_monitor.py`, superseded by `4f4dc2487b98` 05:00 + `6728be78d1bf` 11:00).`daily_cron_audit.py` already prints these as `retired/disabled, informational` — do not report them as missing scripts.
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
- **`5678a363ce3b` (MemPalace Inbox Watcher, `*/5`) reading `Script timed out after 7200s` on every pass is a THROUGHPUT signal, not a hang — verify progress before classifying.** The cron fires every 5 min but one pass drains the entire pending set and is killed at the job's 7200 s ceiling, so the status is red ~every 2 h while it is actively feeding. Health check (30 s, no writes): `find ~/.hermes/mempalace-inputs/.processed -name '*.done' -newermt '-2 hours' | wc -l` (healthy ≈ 25-30) plus `pgrep -af mempalace_watcher.py` for a live child feeder. Measured 2026-11-11: 330 pending (~330 files/day inflow), ~15 files/h drain, ~248 s/file — i.e. roughly break-even, so the red will persist until either the inflow drops or the job is re-sized. **Do NOT "fix" it by deleting markers or widening retention** (that re-feeds stored content); the real lever is Saturday scope. Same day: `pluto-mempalace-bridge`'s "≤5 minutes" latency claim was false and was retracted — never quote that figure.
- **The podcast leg is RED by design: `cc76c11d35d2` (Capture Watchdog 06:25) and the chain's `verify`
  row.** ~63% of the corpus has no readable transcript (YouTube IP block; 63.2% / 1,657 episodes on
  2026-11-09 and rising as the corpus grows faster than transcripts resolve), so the watchdog tripping is
  the designed signal, not a regression. **`63.5% unreachable by learning` is a REACH metric, not a loss rate** — the loss number comes from the integrity sweep, which no cron runs; the audit now prints `UNKNOWN` or a swept-denominator instead of a fake `0 (0.0%)` (fixed 2026-11-23 — see `podcast-knowledge-base` → "Capture-chain integrity"). **The chain is
  judged by the ONE 09:00 assertion job `7e4a2379157d`**, whose other rows (`ingest/chunk/export/
  alexandria/contract/palace/feed`) carry the real status. A `verify` leg reporting `locked=N error=1`
  (2026-10-04: 4 locked / 7 needs_human / 1 error) is a **single-episode** maker/checker failure — either
  unparseable JSON from the maker or a 240 s `curl rc=28` timeout — and is written to the ledger for the
  next run; do not re-escalate it. **Re-verified 2026-10-12 + 2026-10-13 (2 consecutive days): both times
  the chain flagged ONLY `verify` while the other 7 legs (`ingest/chunk/export/alexandria/contract/
  palace/feed`) were ✅, and both times the failure was an unparseable-JSON maker response
  (`locked=3 | needs_human=8 | thin=0 | error=1`, $0.10895 on 10-13). Still single-episode maker-quality,
  not a code fault — watch only if it reaches 3+ consecutive days or a leg reports ZERO locked episodes.**
  **2026-10-14: CLEARED — the chain returned to SILENT GREEN** (201-byte output, the same size as the
  10-09/10-10/10-11 green runs; 10-12 and 10-13 were the only red days: 865/867 bytes). The 2-day verify
  watch is reset to zero — do NOT carry the "verify red" line forward again without a fresh red run. Escalate only if a leg produces NO locked episodes, or the 09:00
  assertion flags a stage other than `verify`. Detail: `podcast-knowledge-base` skill.
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
- **`Restart-safe cron worker failed after handoff: … exited before durable recovery could terminalize its execution state (exit 1)` plus `Cron external worker … did not acknowledge within 30s` on a `no_agent` script = a SCHEDULER HANDOFF crash, not a script fault.** Seen 2026-11-18 04:50 on `4161036f7818` (Gmail Health): both lines in `errors.log`, NO output file for that date, `last_status: error` the only trace, and the same script run by hand returned `Gmail Health: IMAP login successful` RC 0. Run the script directly to prove it innocent, report it as a missed run (not a credential/IMAP failure), and escalate only if it recurs on consecutive days.
- **`tapease_prod_monitor.py` SSM `subprocess.TimeoutExpired` on `list-command-invocations` (seen 2026-10-05, first red in 10 runs)**: the monitor's `ssm_shell()` hardcodes `timeout=15` on the inner `list-command-invocations` call (the function's own default is `timeout_sec=20`; its `send-command` step uses 30 s), so a slow AWS SSM API kills the whole run inside `check_processes` → exit 1 with a `TimeoutExpired` traceback. Classify TRANSIENT single-occurrence (AWS latency; 9 green runs preceded it). Watch only: escalate (or raise the inner timeout to match the outer budget) if it recurs on 3+ days — do NOT patch prod-monitor code from a daily tick for a one-off. The same `timeout=15` shape sits in `amlhive_prod_monitor.py:503`, which has stayed green.
- **`GIT_TIMEOUT`**: Script stdout contains `GIT_TIMEOUT`. Network/git-remote issue. Usually self-resolves next run. Escalate only if 3+ consecutive days.
- **`<3>WSL (<pid> - ) ERROR: UtilAcceptVsock:271: accept4 failed 110` on a `.sh` cron (exit 1, empty stdout)**: WSL interop talking to a Windows process (WSLg/`wslpath`/Win exe); `110` is ETIMEDOUT. The script never reached its logic. Classify TRANSIENT unless it repeats on consecutive days, and do NOT patch the script — seen 2026-11-14 on `a593b164f4c1` (`tapease_old_pos_daily.sh`), green on the three days either side. A `.sh` cron whose only output is a `WSL (...)` stderr line has NO verdict at all: never read it as a data result.
- **Mirroring a strict-superset skill: OVERWRITE the repo copy, do not append the missing block at the END.** When `diff | grep -c '^<'` reads 0 the repo copy lacks nothing, but the missing block may live mid-file — appending it at the end leaves `0` repo-only and `1` WSL-only on the next diff (position, not content). Copy the WSL file over the repo file and require BOTH counts `0` (seen 2026-11-15 on `chief-of-staff-os/daily-task-prep`).
- **Gateway shutdown**: `Gateway shutdown (final-cleanup) killed the job's tool subprocess`. Caused by gateway restarts. Auto-recovers next cycle.
- **`Interrupted by shutdown before terminal completion` with NO gateway restart**: the message is misleading — the real cause is a scheduler fire-claim loss. Confirm with `grep "fire claim ownership lost" ~/.hermes/logs/errors.log | grep <job-id>`; if the timestamp matches the job's `last_run_at` and `logs/gateway.log` shows no shutdown at that minute, it was a claim-ownership interruption, not a shutdown. The job's deliverable is often ALREADY WRITTEN — check `~/.hermes/cron/output/<id>/` and the artifact's own path (e.g. `research_outputs/`) before calling it a failure. Seen 4x between 09-09 and 09-12 (incl. the 09-12 Saturday Weekly Review, whose 16 KB report was produced at 06:03 before the 06:04 interrupt). Flag as a standing scheduler defect, do not re-escalate the individual jobs.
- **`Broken pipe` on agent-driven crons**: Stream stale/timeout. Built-in 3-attempt retry usually succeeds — **but check for a CLUSTER before calling it transient.** Several agent crons red in the same window with the same error is ONE provider event, and the retry only saves you if a fallback chain exists. Verified 2026-09-15: 8 jobs, `[Errno 32] Broken pipe` + `503 Service is too busy` from `provider=deepseek`, all dead at attempt 3/3 because the chain was empty — one outage, eight red jobs, no 6:00 AM briefing. See Task 3 step 2 for the cluster commands; resilience fix in `monitoring-alert-verification` + `llm-cost-routing`.
 - **`Provider has been unresponsive (no response received) for N consecutive stale attempts` (cluster,
 one morning)**: a STREAMING STALL, distinct from `Broken pipe`/503 — and it is classified
 **non-retryable**, so the fallback chain NEVER engages even when `hermes fallback list` shows healthy
 hops. Verified 2026-10-02: 3 hops configured, jobs still died. Seen 05:35→07:15 the same day:
 `c527fed4a1da` (Morning Briefing), `0fb6bf47f704` (Moonshots Daily Learning), `4ef6e889e8d6` (podcast
 verify — `curl rc=28` 240 s timeout, "3 bytes received" against `api.deepseek.com`). Treat as ONE
 provider event, not three bugs. **Also check delivery**: the briefing was red AND still delivered
 (`agent.log`: `Job 'c527fed4a1da': delivered to telegram:-1003834479227`), meaning the USER received
 the error text as their briefing — report that, it is user-visible. Confirm with
 `grep "<job-id>" ~/.hermes/logs/agent.log | grep delivered`.
 - **A chromadb red whose signature is `No module named 'pydantic_core._pydantic_core'` (not the plain
 `No module named 'chromadb'`) is an ABI MIX, and it may already be stale.** The traceback shows
 chromadb from `~/.hermes/venv/lib/python3.13/site-packages` and pydantic from a PM env's
 `lib/python3.14/site-packages` — two interpreters' trees on one `sys.path`. **PM generation hashes
 rotate**, so RE-PROVE it before reporting: `~/.hermes/venv/bin/python3 -c "import chromadb"` (healthy
 → expect OK), then re-run the script through the real cron bootstrap. Seen 2026-10-02: `0959371eec17`,
 `d941471b7fc8`, `7e4a2379157d` were all red at 05:25–07:50 with this signature, but the same bootstrap
 invocation of `sc_watch_to_mempalace.py` at 14:00 printed `nothing new to feed` exit 0 — the PM env
 had regenerated (traceback hash `87ff6705…` vs live `47f2039c…`). Do not carry it forward as a live
 fault, and never "fix" it by exporting `PYTHONPATH` (leakage is what creates it). Recipe + the
 self-heal checklist: `podcast-knowledge-base` skill.
 **CONFIRMED ROOT CAUSE + PROVEN FIX (2026-10-03) — this IS a live cause, and it is not a
 chromadb-only problem.** The gateway exports a `PYTHONPATH` entry pointing at a FOREIGN
 interpreter's `site-packages`; PYTHONPATH is prepended to `sys.path`, so it shadows the running
 venv's `pydantic_core` while `chromadb` still resolves from the venv (mixed ABI). It is NOT
 self-clearing and NOT a stale record: reproduced deterministically by adding one env var —
 `PYTHONPATH=<pm-env site-packages> <cmd>` fails every time, without it the same command passes.
 Because `subprocess.run(...)` children INHERIT `os.environ`, that one entry also reached every test
 process in `amlhive_daily_test_runner.py`: the backend suite died with **243 errors during
 collection** while the same venv collected **7833 tests clean** by hand. Fix = an in-process env
 guard at the TOP of the script (before any chromadb/feeder import): strip every `site-packages`
 entry from `os.environ["PYTHONPATH"]`, drop foreign-version `site-packages` from `sys.path`, then
 re-exec onto `~/.hermes/venv/bin/python3` when not already there. Applied + verified 2026-10-03 to
 `mempalace_watcher.py`, `mempalace_health.py`, `sc_watch_to_mempalace.py`, `podcast_pipeline_daily.py`,
 `pluto_chamber_refresh.py`, `amlhive_daily_test_runner.py`; full recipe, per-line rationale and the
 sweep live in `~/.hermes/ops/environment.md` -> "Cron env guard". A `find_spec('chromadb')`
 self-heal CANNOT detect this (chromadb is found; its dependency fails), which is why the older
 guards in `mempalace_health.py`/`sc_watch_to_mempalace.py` never fired — when you meet a
 `find_spec`-shaped guard on a pydantic_core error, replace it, do not add a PYTHONPATH export.
 **`poetry` is NOT installed on this host** — the test runner's `backend/.venv/bin/pytest` fallback
 is now the permanent path, so a stale `.venv` surfaces as 243 collection errors, not as a
 "missing poetry" warning.
- **`Script timed out after 3600s` on `hermes_update_check.sh` (4eef20ef0e25)**: The `hermes update` step (git pull + npm rebuild + web UI build) is slow and can exceed the 3600s cron timeout even when the update SUCCEEDS. Check `~/.hermes/logs/hermes_update.log` first — if it ends with "✓ Code updated!" / "✓ Model catalog cache refreshed", the update applied and only the "Restart gateway" prompt was cut off (gateway is still running old code until its next natural restart). Escalate only if the log shows no "Code updated" line. Note: the 03:00 Mon+Fri run (`0 3 * * 1,5`) may also show `ok` vs `error` depending on whether the load-sleep (30 min) plus slow update fits in the window.
- **`⚠ A previous hermes update pulled new code but did not restart running gateways` printed by
  EVERY `hermes` CLI call — a FALSE POSITIVE; verify, do not restart blindly (root-caused 2026-09-20).**
  `_warn_pending_fleet_restart()` (`hermes_cli/update_cmd_fleet.py`) prints it whenever the latest
  update RECEIPT failed — even when the restart completed. The 2026-09-19 14:14 AEST update applied
  `5dea46d1` → `03fee43c` and DID restart the gateway (`gateway_restart.restarted_services:
  ["hermes-gateway"]`, `incomplete: false`; systemd shows the gateway active since 14:15:54, inside the
  receipt's own window). The receipt is marked failed only by a mid-update
  `TypeError: _find_stale_dashboard_pids() got an unexpected keyword argument 'scope_home'`: the process
  loaded the NEW `dashboard_procs.py` (passes `scope_home=`, HEAD line 584) while the OLD
  `main_dashboard.py` sat in `sys.modules` (pre-update `5dea46d1` signature: `(*, exclude_pids=None)`)
  — self-inflicted mixed-modules, NOT a bug at HEAD. Confirm in two commands: dump the receipt
  (`python3 -c "import sys;sys.path.insert(0,'/home/habib/.hermes/repo');from hermes_cli.update_receipt
  import read_latest_receipt;import json;print(json.dumps(read_latest_receipt(),indent=2))"`) and read
  `stop_reason` + `gateway_restart`; then
  `git show <pre_sha>:hermes_cli/main_dashboard.py | grep -A2 "def _find_stale_dashboard_pids"`.
  It clears by itself on the next clean `hermes update` (Mon/Fri 03:00 window). Cosmetic — never
  restart the gateway from this cron to silence a warning.

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
  **2026-10-22: a DIFFERENT acnc signature appeared — `HTTP 503 … Could not fetch acnc-charities CSV from
  data.gov.au: 503`.** That is the UPSTREAM CKAN source, not the app handler: the same run's
  `asic-companies` / `asic-business-names` came back `DETECTION_UNAVAILABLE` because the backend's CKAN
  `resource_show` failed too. ONE upstream event — verify with
  `curl -sI https://data.gov.au/data/dataset/acnc-register` (302→200 at 14:00, recovered) before touching
  the script or opening a new incident.
- **RESOLVED 2026-09-20 — this failure mode no longer exists; do NOT re-chase it.**
  `cmdb_cost_monitor.py` was rewritten to read the Notion CMDB **DIRECTLY** (data_source
  `40638825-121a-48f6-8f95-d2bf11fffb15`, `NOTION_TOKEN_WS`) — no local `:3009` plugin, no LAN probe,
  no auth-approval hang. Verified 2026-09-20: `last_status: ok`, `Assets: 38 (13 priced)`,
  `A$768.59 / month`. Only the Hermes dashboard on `:9119` runs now, and the monitor does not depend on
  it. The entry below is kept **historical** for recognising the old blind-zero signature in archived
  output — if you see a `:3009 unreachable` failure dated after 2026-09-20, treat it as a NEW fault.
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

The long tail (22 entries, ~43 KB) moved to **`references/real-fault-records.md`** on 2026-11-27 when SKILL.md hit the 100,000-char cap. Match your symptom in the index, then read the entry there. Keep NEW entries in the reference file — and compress a stable band into one `**Days N-M COMPRESSED**` block instead of adding a paragraph per run.

1. ✅ RESOLVED 2026-11-19 — GitHub's 100 MB per-file cap (GH001) blocked the VAULT push for ~1 day; do NOT re-escalate. 2026
2. A skip `reason` the script does not recognise is a FAKE PASS — fixed 2026-10-22 in `amlhive_asic_sync.py`.
3. A `monitor`-mode watch whose UPSTREAM PAGE restructures fails with `Script exited with code 2` and
4. `5b95adcb27d4` (Blog Posts via Codex, Tue/Thu 08:00) — STANDING BLOCK, owner decision pending; do NOT
5. A paused job's stale `last_status: error` is NOT a current failure — read `enabled` before classifying.
6. Name a failing test the cron only counted. When a test runner reports "N failed" with no names, the
7. `044c0bc41e31` (AMLHive Daily Test Suite) — baseline backlog is 6-8 backend failures/day
8. `SSM: Error response from daemon: No such container: amlhive-app-1` on `3ebed4e59ee3` (AML Hive Daily
9. A skill at ≥99.9% of the 100,000-char SKILL.md cap is effectively UNPATCHABLE — `skill_manage`
10. `daily_cron_audit.py`'s `=== legacy 'fallback_model' config key ===` scan is a DOCUMENTED FALSE
11. The `12:35 AM` ingestion time in `podcast-knowledge-base` was a stale doc, not a live job
12. `e6b671746eaf` (Weekly Test Report — A2Square + AML Hive, Wed 02:00) has a STEADY standing
13. `0320d41d6d71` (A2Square Weekly Test Suite, Mon 02:30) has a STEADY standing pattern of 2-3 failures/errors per week — d
14. `ModuleNotFoundError: No module named 'chromadb'` in one or more same-morning `no_agent` scripts
15. A red job can hide a SECOND fault behind the one you already classified (2026-09-29). The same
16. `podcast_capture_verify_daily.sh` (`4ef6e889e8d6`) — ✅ RESOLVED 2026-09-30, historical (do NOT
17. `RuntimeError: Missing required environment variable: <KEY>` (cluster of same-day jobs, different
18. `state.db reported structural corruption` (cluster of agent crons, one morning): 8 agent-driven jobs
19. `FATAL: password authentication failed`: Credential is wrong or expired. For env-var-based scripts: check the env var. F
20. `Traceback` in script: Genuine Python error. Read the traceback to diagnose.
21. `401 Unauthorized` on 3+ crons same day: Systemic credential failure — check provider API keys, not individual crons.
22. `delivery_failed` with an EMPTY `last_error`: the script ran and wrote its artifact — the failure is the outbound send, 


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
- **A provider stall kills THIS job, and its only durable signature is a MISSING
  `~/.hermes/reviews/daily/maintenance-<date>.json`.** Seen 2026-10-15: the run started 14:00:51, stalled
  600 s on `[Errno 104] Connection reset by peer` (`bytes=0 chunks=0`, `attempt 3/3, not retryable`), and
  aborted at 15:01 with `Provider has been unresponsive … 6 consecutive stale attempts`. `last_status:
  error` at an odd time (15:01, not 14:00) plus no dated JSON file is the whole trace — so when asked
  "did the daily maintenance run?", check for the dated file before blaming the scheduler, and do NOT
  backfill the missed day: the next on-time run covers the same checks.
- A catch-up fire is not a config error: the 2026-09-17 run executed at **23:38** instead of its
  14:00 slot (the gateway was restarted at 23:38 after the state.db repair) and the 2026-09-18 run
  fired at 14:00:24 on time. Before flagging a wrong-time run, check whether a gateway
  restart/shutdown happened in that window — if the slot is held correctly the run after it is on
  time, and there is nothing to fix.
- **A catch-up fire can DUPLICATE already-delivered output — count the output files, don't trust `last_run_at`.**
  Seen 2026-09-21: WSL/Windows reboot stopped the gateway at 11:57:14 and it restarted 12:02:44; the
  scheduler then re-fired five completed morning agent jobs, INCLUDING the 6:00 AM briefing
  (`c527fed4a1da` wrote output at 06:02:44 AND 12:27:28 and delivered a second copy to
  `telegram:-1003834479227` — confirmed in agent.log: `Job 'c527fed4a1da': delivered to
  telegram:-1003834479227`). Detection: `ls -t ~/.hermes/cron/output/<id>/ | head -4` — two files with
  the same date and hours apart is a double-run; `last_run_at` shows only the newer one and `cron list`
  still labels it `Dispatch: on time`, so neither field reveals the duplicate. Report the duplicate to
  the owner (the delivered copy is user-visible) rather than dismissing the run as an ordinary catch-up.
- **A `pgrep`-based liveness check must match EVERY launch form of its target.** `gateway-watchdog.sh`
  (crontab `*/2 * * * *`) hardcoded `pgrep -f "hermes_cli.main gateway run"` while the live gateway's
  cmdline was `/home/habib/.hermes/repo/venv/bin/python3 /home/habib/.hermes/venv/bin/hermes gateway`
  → permanent false DOWN → it fired `hermes gateway run --replace` every 2 minutes; the ownership
  guard refused (no `gateway.pid`) and spammed 104 error lines in one afternoon (~720/day). Verify the
  pattern against the REAL cmdline (`tr '\0' '\n' < /proc/<pid>/cmdline`), never against the string a
  docstring claims, and prefer matching both the module form and the console-script form.
- **Never read skill usage out of `agent.log`.** Log lines are only
  `tool skill_view completed (0.9s, 43242 chars)` — the skill NAME is never on the line, so a
  log-regex scan prints an empty list every day and reads as "no skills used in 24h". Query
  `state.db` instead (`select tool_calls from messages where tool_calls like '%skill_view%' and
  timestamp >= <epoch>`; `timestamp` is a UNIX float, not ISO). Any scanner that can return empty for
  two different reasons (nothing used vs. cannot see) must print an explicit UNKNOWN warning.

## Output

Durable standing faults belong in `~/.hermes/ops/environment.md` (a plain dir, not a repo) as well as
in this skill — the skill is re-read only when a maintenance run loads it, while environment.md is the
pointer target every agent can reach.

Save detailed results to `~/.hermes/reviews/daily/maintenance-{DATE}.json` with:
- Skills patched count
- Memory entries updated count
- Cron failures detected (breakdown by classification)
- Scripts broken count
- Any 🚨 alerts requiring immediate attention

Keep the user-facing report brief (under 5 min runtime target). Only surface what needs action.

## Pitfalls
- **Verify chat IDs from gateway logs BEFORE bulk-rerouting cron deliveries (Aug 2026).** When Haris says "use this group for X jobs", do NOT trust `channel_directory.json` — it stores stale internal names (it still said `daily_status_v2` for the AMLHive group after the retitle) and can miss newly-created groups. The session context shows the group's CURRENT title; the real chat ID is in the gateway log: `grep "inbound message" ~/.hermes/logs/gateway.log | tail -20` — the `chat=` on the line matching this session's first user message IS the group's ID. Then confirm with `cronjob action=list` that jobs show `deliver: telegram:<that-id>`. Mistake made 2026-08-13: assumed `-1003834479227` (daily_status_v2) was the AMLHive group, "confirmed" it, and told the user all jobs were already there when they landed in the wrong group. Correct split: AMLHive jobs → `-1004485329864`; general daily + TapEase jobs → `-1003834479227`; DM `5273126730`.
- **Credential-shape sweep: ONE expected hit, not a finding.** `a2square_test_runner.py:30`
  `POSTGRES_PASSWORD = "test_password"` is the throwaway credential for the LOCAL test Postgres the
  runner boots on `:5433` (`test_user`/`test_db`) — matched by the shape regex, but there is nothing to
  rotate. Report `0 real secrets` when it is the only hit; do NOT raise a rotation alert for it.
  Sanity-check any other hit by reading the LHS: a `*_PASSWORD`/`*_TOKEN` feeding a 127.0.0.1 test
  service is a fixture, one feeding a real endpoint is a leak.
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
