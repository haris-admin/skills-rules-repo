# Real fault records — the long tail of `### Real (needs action)`

Extracted from `SKILL.md` 2026-11-27 when the file hit the 100,000-char cap (97,927 chars, patch rejected). **Nothing here is optional reading when your symptom matches a heading.** Each entry is a fault class seen in production: the signature, the proof that settles it, and whether it is still live, resolved, or a standing owner decision. The one-line index lives in `SKILL.md` under `### Real (needs action)` — match the symptom there, then read the entry here.

- **✅ RESOLVED 2026-11-19 — GitHub's 100 MB per-file cap (GH001) blocked the VAULT push for ~1 day; do NOT re-escalate.** 2026-11-18: `fc726783497f` printed `push rc: 1` four times with `remote: error: GH001: Large files detected` / `pre-receive hook declined`, because the append-only monthly podcast lenses `vault/podcasts/lenses/general/2026-10.md` = 106,718,732 B and `2026-09.md` = 100,000,497 B (497 B over). Fix taken: per-lens DAILY views plus `vault/podcasts/lenses/` gitignored+untracked. Verified 11-19 12:56 AEDT — `push rc: 0`, `origin/main...HEAD` = `0 0`, 5,245 files, chain `7e4a2379157d` green. **Re-detect a recurrence with `git rev-list --objects origin/main..HEAD | git cat-file --batch-check='%(objecttype) %(objectsize) %(rest)' | awk '$1=="blob"&&$2>50000000'` — never `find . -size +100M` in a `/mnt/c` clone (the 9p walk alone blew a 180 s tool timeout).** Always a SIZE fault, never git/auth: report blob sizes and options, never force-push, never rewrite history, never delete lens files to unblock a push.
- **A skip `reason` the script does not recognise is a FAKE PASS — fixed 2026-10-22 in `amlhive_asic_sync.py`.**
  The dataset loop classified `NO_CHANGE` / `FILE_NOT_YET_PUBLISHED` (pass) and `DATASET_SOURCE_UNAVAILABLE`
  (alert, with the documented asic-registered-schemes exception), but every other reason fell through to
  `⏭️ Skipped: {reason}` with **no `overall_alert`** — so `asic-companies` + `asic-business-names` skipping
  as `DETECTION_UNAVAILABLE` looked like a pass. `DETECTION_UNAVAILABLE` is the BACKEND's own signal
  (`backend/app/api/internal/sync.py`: `detect_reference_dataset_change()` returned FAILED, i.e. the CKAN
  `resource_show` call to data.gov.au did not answer 200) — the dataset was never checked. Fix: an explicit
  `DETECTION_UNAVAILABLE` branch plus a catch-all that alerts on any unclassified reason, both printing
  `❌ NOT CHECKED`. Verified by running a STUBBED COPY of the script (a real run would POST real syncs): both
  branches print `❌ NOT CHECKED` and the run ends `OVERALL: ❌ ALERT`. Standing rule for every collector
  script: the reason classifier must be exhaustive, and the `else` branch ALERTS — never a neutral skip.
- **A `monitor`-mode watch whose UPSTREAM PAGE restructures fails with `Script exited with code 2` and
  SUPPRESSES the agent — fix the PARSER, and treat the missing report as the real damage.**
  `monitor_script` stdout is hashed and the agent only wakes on a CHANGE, so a parse break means the
  page's actual content change is never narrated to the owner (status reads `monitor source failed`,
  not `no_change`). Seen 2026-10-21 on `ce9caadf1d7b` (`austrac_enrol_overview_watch.py`, 07:15 daily):
  print was `HTTP: 200` + `AS_OF: UNPARSED` + `TABLE: UNPARSED` — AUSTRAC had replaced the
  "Enrolment progress by industry" table with one sentence, `As of 20 October 2026, we have 62,710
  businesses enrolled with us`, and `<table` count on the live page is now **0**. Two lessons that
  generalise to every page watch: (a) the visible `<h2>` text changed while its `id` still read
  `enrolment-progress-by-industry` — anchor section finding on VISIBLE TEXT, never on an id or on prose
  copied from the previous page shape; (b) re-verify the fault against the LIVE page before editing
  (`curl` it and read the real markup) instead of adjusting regexes against the error string. Fix shape:
  keep the legacy table parser AND add a sentence-form parser, emit `TOTAL_ENROLLED`, exit 0 when either
  form parses — then prove it with TWO live runs (exit 0, byte-identical stdout; determinism is a hard
  requirement because the engine hashes those bytes).
  **2026-10-22 — the fix HOLDS; the next red was a different class.** `RESULT: FETCH_FAILED` + `HTTP: 503`
  from austrac.gov.au itself (live `200` when curled at 14:00) — a transient upstream 503, not a parser
  regression. Before re-opening a just-fixed parser, curl the page: a 503 serves no HTML, so the parser is
  never reached. Recurred 2026-11-20 (07:16 `HTTP: 503` / `FETCH_FAILED`, live 200 at 14:00): a 503 red
  here is ALWAYS upstream until a curl proves otherwise.
- **`5b95adcb27d4` (Blog Posts via Codex, Tue/Thu 08:00) — STANDING BLOCK, owner decision pending; do NOT
  re-derive or re-escalate, and do NOT report it as a fresh red.** It fails its own `git merge origin/dev`
  pre-flight and BLOCKS by design (nothing written/committed/pushed; tree left clean). 8 consecutive dead
  runs as of 2026-10-06, last success 10 Sep, ~16 posts not produced; the job delivers its own BLOCKED
  report to `telegram:-1004485329864` each Tue/Thu, so Haris already sees it. Codex itself is healthy
  (`codex login status`, `codex --version`) — the blocker is the BRANCH, and only a human A/B/C choice
  clears it (park the 40 app-code commits + re-baseline `codex_pr`; or retarget at `pluto_pr`; or ship the
  drafts to the vault). **Re-measure the two numbers before quoting them:** on 2026-10-06 `codex_pr` was
  **376 behind / 40 ahead** of `origin/dev` (253 on 1 Oct ≈ +25/day, `ahead` frozen at 40 since 24 Sep) with
  17 unmerged files incl. application code, while `~/code/amlhive1-pluto-pr` carried **2173 dirty entries**
  — so Option B is NOT the one-line retarget the 1 Oct report called it; its BRANCH is still 0-behind dev,
  so the only clean path is a FRESH worktree off `pluto_pr`. Same cause blocks `31ac1948416f` (Fri Codex
  Review). **2026-10-30: that job's signature moved — `BLOCKED: origin/dev merge conflicted:
  CONFLICT (content): Merge conflict in .version`** (plus auto-merges of `CHANGELOG.md`,
  `backend/.env.example`, `backend/app/api/internal/sync.py`). Same standing block, different surface:
  the script still stops cleanly and produces no report, and the blocker is still the lane's drift, which
  only the owner's A/B/C choice clears. Classify as the standing owner-decision block — do NOT open it
  as a new fault — but note `.version` is exactly the file a long-diverged branch collides on first, so
  this is the expected shape of the same unresolved decision, not a worsening. **2026-11-20: yet another
  surface — `Status: 🔴 BLOCKED — codex_pr worktree unavailable` (same owner-decision block).** Any future content run must also use the current bundle path `assets/YYYY-MM-DD-<slug>/`, not `assets/blog-migration/<slug>/` (dev moved it 21 Sep). **Streak check 2026-11-28: SIX consecutive weekly runs BLOCKED (10-23, 10-30, 11-06, 11-13, 11-20, 11-27), zero Codex reviews produced since Oct.** A weekly job's `last_status: error` always reads as "stale, do not re-escalate", so this never surfaces as a live red — report the SIX-RUN STREAK and the owner's A/B/C lane choice, never "stale, ignore".
  `assets/blog-migration/<slug>/` (dev moved it 21 Sep). Detail: `environment.md` → "codex_pr IS NO LONGER
  A CONTENT LANE" + the 2026-10-06 status append.
- **A paused job's stale `last_status: error` is NOT a current failure — read `enabled` before classifying.**
  `daily_cron_audit.py` and this skill's own standing-fault records both key off `last_status`, so a job
  the owner PAUSED keeps appearing as a live red indefinitely. **`daily_cron_audit.py` now prints
  `DISABLED (paused by owner …)` instead of the old ambiguous `CHECK` verdict for `enabled: false` jobs
  (patched 2026-11-07, verified live) — a `DISABLED` verdict needs no action; a `CHECK` verdict does.** Seen 2026-09-30: `0e14d2e1095f`,
  `57e72391a773` and `a2ff28e23482` are `enabled: false` (retired INTO the chain orchestrator
  `7e4a2379157d`, 09:00 daily, silent when green) while still carrying `error` from their last run. Pull
  `enabled` + `next_run_at` for every non-ok job, and verify the REPLACEMENT job instead of the retired one.
- **Name a failing test the cron only counted.** When a test runner reports "N failed" with no names, the
  repo's own pytest cache has them: `backend/.pytest_cache/v/cache/lastfailed` (its mtime is that run).
  Seen 2026-09-30: `044c0bc41e31` reported 6 backend failures with no names; the cache gave the cluster
  (audit-entry `platform_user_id`, Veriff/provider-quality workflows, JWT email fallback). **But check the
  COUNT before trusting the cache: lastfailed accumulates every nodeid that has failed at ANY point in the
  cache's life (186 entries on 2026-10-04 for a run that reported 8 failed), so it names suspects, not
  the run's failures.** The authoritative names, in order of preference: the runner's own diagnosis writer
  `~/.hermes/reviews/test_diagnoses.log` (STALE since 2026-09-28 — two weeks of runs reported "N failed"
  with no names), then a `-q --tb=no -rf` re-run of the newly-failing subset, then the cache as a
  candidate list only. **Fixing the diagnosis writer is the real task**; until it is fixed, every
  "N failed" line in this report is a count with no actionable content.
- **`044c0bc41e31` (AMLHive Daily Test Suite) — baseline backlog is 6-8 backend failures/day
  (10-01: 8, 10-02: 7, 10-03: 2 + a 0-collected backend run, 10-04: 8, 10-05: 8). Do not report each day's
  number as a new incident. The 10-03 `❌ 0 passed, 0 failed (19.3s)` backend leg is the separate
  **collection-failure/pytest-cache signature** — 19 s and zero tests collected is never a pass (No Fake
  Pass Rule); it also invalidates that run's count. Escalate only on a change in the COUNT TREND or a
  change in component (frontend/E2E were green through this window).
  **2026-11-21→11-28 — NEW STEADY BASELINE (8 identical runs): `❌ 10015 passed, 52 failed, 3 errors`.**
  Backend `9683 passed, 45 failed` (35 = SQLite-vs-PostgreSQL suite gaps, issue-134; **10 genuine
  assertions**), frontend 288/1, E2E 44/6. The documented 6-8/day figure is SUPERSEDED — read the trend,
  not the number. Two standing degradations live inside it: (a) **all three legs print
  `Diagnosis: [Diagnosis skipped: timed out after 120s]` on every run**, so `reviews/test_diagnoses.log`
  gains nothing and the 10 genuine failures stay UNNAMED — a count with no actionable content; (b)
  `⚪ 'poetry' not found — fallback to venv pytest` is permanent on this host (expected, not a finding).
  Escalate only on a count-trend break, a leg reaching 0 collected, or the diagnosis timeout persisting
  after the runner's 120 s budget is raised.
  **TWO REAL ESCALATIONS on 2026-10-07 — these are NOT the standing backlog:**
  (a) **Count-trend break: `7641 passed, 31 failed`** (≈4× the baseline) on the first run after
  `git merge origin/dev` landed (`03e74c26`, 6 commits ahead of dev; backend deps reinstalled). A merge
  that raises BOTH the collected count (+232) and the failure count (+23) points at the merged slice, not
  at the pre-existing 6-8. Report the delta and the merge SHA.
  (b) **E2E leg produced ZERO tests — a No-Fake-Pass ERROR, not a skip:**
  `❌ playwright e2e did NOT actually run tests (exit_code=1)` / `❌ 0 passed, 0 failed (2.7s)`, because the
  Next dev server refuses to boot: `Error: \`experimental.cssChunking: "graph"\` is only supported with
  Turbopack. Please remove the option or run Next.js with Turbopack in next.config.ts.` The runner
  launches `next dev --webpack`, so `next.config.ts` and the runner's dev flag are out of sync. E2E was
  48/48 green on 10-04 and 10-05, so this is a fresh config regression — fix the config/flag mismatch,
  do not read `0 passed, 0 failed` as green. **The diagnosis writer explains WHY this is easy to miss:**
  `~/.hermes/reviews/test_diagnoses.log` is written only when a leg fails AND the OpenRouter diagnosis
  call returns (mtime 2026-10-05 — no entry for the 10-06 or 10-07 runs), so a failing run can leave NO
  diagnosis behind. Never infer "no failures" from an unchanged diagnosis log.
  **ROOT-CAUSED + FIXED 2026-10-08 — the writer was BROKEN, not merely quiet.** The runner runs on
  the cron PM env (`python 3.14.7`), whose default multiprocessing start method is **`forkserver`**
  (changed from `fork` in 3.14); forkserver/spawn must PICKLE the process target, and
  `codex_diagnose()` passes a local closure — so every failing leg returned
  `[Diagnosis failed: Can't pickle local object codex_diagnose.<locals>.worker ...]`. Fix applied to
  `~/.hermes/scripts/amlhive_daily_test_runner.py`: pin `multiprocessing.get_context("fork")` (no
  pickling; the runner is sequential at that point). Verified by exec'ing the patched function under
  the PM interpreter itself with a stubbed `chat_with_fallback` → non-error return + log write.
  **Standing rule for any `multiprocessing` timeout wrapper in a cron script: pin the start method
  explicitly (`get_context("fork")`) — never rely on the interpreter default, and never pass a
  closure to a spawn/forkserver context.** Detail: `wsl-cron-test-runner` skill.
  **2026-10-08 state of the two faults it hid:** (a) the 10-07 E2E `cssChunking`/Turbopack
  zero-test regression is **RESOLVED** (E2E 48 passed / 2 failed, both whitelisted `reduced-motion`
  flaky, run 1/3) — do not re-report it; (b) backend count trend still elevated: `7699 passed,
  38 failed` (10-07: 7641/31, baseline 6-8) on the merged tree — day 2 of the post-`origin/dev`-merge
  elevation, and vitest's 1 failure has now been escalated from known-flaky to real (3 consecutive
  runs).
  **Days 3-22 COMPRESSED (2026-10-09 → 2026-10-28) — read this, not a day-by-day log.** The backend
  band moved TWICE and both moves are explained; everything else is counter-drift on a stable band:
  - **Days 3-12 (10-09→10-18): flat `7770 passed, 34 failed`** (pre-10-07 baseline was 6-8; the
    elevation dates from the `03e74c26` `origin/dev` merge). vitest `240/1` climbed 5→13 consecutive
    runs, E2E oscillated `47-48/2-3`. Two REAL E2E excursions inside that window, both now superseded:
    the forgot-password recovery-copy/CTA regression (10-11/10-12) and the NFR load-timing benchmark
    (10-18); otherwise the diagnosis named the whitelisted `reduced-motion` pattern. The
    `get_context("fork")` diagnosis fix wrote real per-leg entries EVERY day — treat it as confirmed,
    and only re-open it if a leg prints a pickle error.
  - **Days 13-16 (10-19→10-22): `classify_pg_gated()` proven live** → output becomes
    `⚪ 30/34 are SQLite-vs-PostgreSQL suite gaps (issue-134)` + `🔴 4 genuine assertion failure(s)`.
    **Backend escalation trigger is the 🔴 GENUINE count, never the 34 total**, and the classifier
    suppresses the diagnosis route only when EVERY failure is PG-gated.
  - **Day 18 (10-24) 🚨 COUNT-TREND BREAK: `9157 passed, 49 failed`, 🔴 14 genuine** (collected +1,387,
    failures +15 in one run) after merging `origin/dev` at `e71bd5d5b` + `📦 Backend deps changed —
    reinstalling` — a dependency-version effect, not the PG-gated 34. Same run's E2E leg produced
    `❌ 0 passed, 0 failed (6.3s)` — **a boot failure, never green (No Fake Pass)**.
    **ROOT CAUSE, proven live: Next.js 16.4.0's agent-upgrade nudge** (`next/dist/lib/upgrade/nudge.js`)
    throws `SecurityFatalError` (exitCode 1) on the FIRST `next dev` after the advisory feed refreshes,
    writing a receipt under `<distDir>/cache/next-agentic-upgrade-retries/` that only authorises a retry
    inside `RETRY_TTL` = 5 min — so a single-shot harness loses the whole leg and the visible tail is
    the `next upgrade --agent=security --internal-nudge-id=…` advisory, NOT the real error.
    **Generalise: a zero-test leg whose tail is advisory/nudge text is a BOOT failure.** Day 19 (10-25)
    repeated it; day 20 (10-26) `"next": "^16.4.1"` landed and E2E returned to `48 passed, 2 failed`.
  - **Days 20-22 (10-26→10-28): backend `9274 passed / 51 failed` with `⚪ 35/51 gaps` + `🔴 16
    genuine` on all three days** — flat at the new level, the escalation rule is still the 🔴 count.
    vitest `266/1` → `267/1` (22+ consecutive, escalated long ago). OVERALL `9589 passed, 54 failed,
    3 errors` (10-28).
  **2026-10-28 (day 22) — the E2E flaky counter tripped again; that is the only change.** E2E `48
  passed, 2 failed` (200.7s) but the runner printed `⚠️ playwright e2e: 1 known-flaky pattern(s) for 3
  consecutive runs → ESCALATED as real failure`. So the whitelisted `reduced-motion` composition is no
  longer a benign 2/3 shape: **from 10-29 a further E2E red counts as a REAL leg**, and run 1 of a new
  counter is the only state that resets it.
  **2026-10-29 (day 23) — the escalated leg produced its first REAL E2E failure; this one is a code bug,
  not flaky noise.** `47 passed, 3 failed` (186.7s) and the diagnosis names it: test #18
  `"forgot password shows recovery copy and sign-in link CTA"` (`tests/e2e/amlhive.spec.ts:106`)
  timed out at 17.6s against 1-6s for its peers — the SAME regression seen 10-11/10-12 and then marked
  superseded. Third recurrence ⇒ treat as a real frontend regression to fix, and stop re-labelling the
  `reduced-motion` whitelist as the explanation for every E2E red. Band otherwise flat:
  backend 16 genuine, vitest 267p/1f (24 consecutive), OVERALL `9588 passed, 55 failed, 3 errors`.
  Read the diagnosis line before classifying any E2E red: a NAMED non-whitelisted test is a regression.
  **2026-10-30 (day 24) — band FLAT; the useless diagnosis got root-caused and FIXED.** backend
  `9274 passed / 51 failed`, ⚪35 gaps, 🔴16 genuine (identical to days 20-22); vitest `267p/1f`
  (25 consecutive); OVERALL `9589 passed, 54 failed, 3 errors`. E2E `48 passed, 2 failed` — the
  escalation counter is now 5 consecutive runs. The E2E diagnosis again read `output is truncated at
  test 41 … no failures visible`, and this time it was root-caused: `codex_diagnose()` was called
  WITHOUT `tail=True` on the playwright leg, and `window = test_output[-6000:] if tail else
  test_output[:6000]` fed the model the **FIRST** 6000 chars — 41 passing test lines — never the
  failure block at the end. Fixed 2026-10-30 (playwright call site now `tail=True`; vitest deliberately
  left on the head slice because its head slice DID name four real failures). Verified by exec'ing the
  extracted function with a stub `chat_with_fallback` in a forked child that writes what the model
  actually receives: `tail=True` → sees the named failure; default → head only. **Rule: a diagnosis that
  says "output truncated / no failures visible" on a leg that reported N failed means the SLICE is
  wrong — fix the slice; never conclude the failures are unreproducible, and never let a slice bug erase
  the test NAMES the escalation rule depends on.**
  **2026-10-31 (day 25) — NEW fault class at the install step, and the band move is explained.**
  `❌ Frontend dep install failed: … npm error code EUSAGE` (`npm ci` can only install when
  package.json and package-lock.json are in sync — `Missing: webpack@5.112.2 …`). Cause: commit
  `50fb44a55` (zod 3→4.6.7) rewrote `frontend/package-lock.json` deleting 580 lines without a full
  regeneration; it is on **`origin/dev`**, so `npm ci` fails for every clone and every CI job.
  `npm ci --dry-run` on the CLEAN tree reproduces it — verify reach with
  `git merge-base --is-ancestor <sha> origin/dev` before blaming a lane. **The dangerous half is the
  silent one: the runner printed this error and then ran vitest anyway against the stale
  `node_modules`, reporting `282 passed / 1 failed` from the WRONG tree.** When an install line fails,
  classify that leg as an ENVIRONMENT BLOCKER and do not diagnose its failures as code.
  Counts: backend `9518/53` (`⚪35` + `🔴18`), vitest `282p/1f` (26 consecutive), E2E `46 passed / 4 failed`
  (6 consecutive, diagnosis names a React hydration mismatch on inline `caret-color`), OVERALL
  `9846 passed / 58 failed / 3 errors`. The +244 collected vs day 24 is a **202-commit `origin/dev`
  merge**, not a trend break — size the merge (`git log --oneline <merge>^1..<merge>^2 | wc -l`) before
  escalating a count move.
  **`4689311b6ad0` STALE_BUILD — root cause is the ECR repo's IMMUTABLE tags** (`tag invalid: The image
  tag 'a202c80' already exists`), so a failed deploy retried on the same commit can never push and
  `Deploy to EC2 via SSM` is SKIPPED; worse, a deploy can report SUCCESS with a green post-deploy version
  gate while production still serves the old build. **✅ RESOLVED 2026-10-27 — do NOT re-open:** it ran
  `ok` silent and `curl https://api.amlhive.com.au/version` returned 0.50.185. **A stale build is an
  event with a lifespan; re-derive it with one curl before carrying it forward.**
  **2026-11-01→11-03 (days 26-29) — band FLAT, one blocker unchanged.** backend `9529 passed /
  51 failed`, ⚪35 gaps, 🔴16 genuine; vitest `282p/1f` (**29 consecutive**, escalated long ago); E2E
  `46 passed / 4 failed` with the SAME React hydration diagnosis (inline `caret-color`) — now **9
  consecutive** escalated runs. The `npm ci` EUSAGE lockfile blocker from day 25 is still present, so
  the vitest leg is STILL an ENVIRONMENT BLOCKER reading a stale tree. No action from a daily tick.
  **2026-11-04/05 (days 30-31) — band flat, same blocker.** backend `9529/51` (⚪35, 🔴16), vitest
  `282p/1f` (31 consecutive), E2E `47 passed / 3 failed` (11 consecutive, same hydration diagnosis),
  OVERALL `9858 passed / 55 failed / 3 errors` on BOTH days.
  **2026-11-06→09 (days 32-35) — band flat at 🔴 11-12, and the npm-ci blocker is GONE (fixed in code).**
  11-06: backend `9547/46` (⚪35, 🔴11) after a clean `origin/dev` merge into `pluto_pr` (`f8cfd2671`),
  vitest `283p/1f` (32 consecutive), E2E `46p/4f` (12), OVERALL `9876/51/3`. 11-07: backend identical,
  `283p/1f` (33), `47p/3f` (13), `9877/50/3`. 11-08: backend `9546/47` (⚪35, **🔴12**), vitest `287p/1f`
  (34), `46p/4f` (14), `9879/52/3`. 11-09: backend **identical `9546/47`** (⚪35, 🔴12), vitest `287p/1f`
  (35), E2E **`44p/6f`** (15 consecutive — failures up from 4, same hydration diagnosis; watch it, do not
  escalate on a single run), OVERALL `9877/54/3`.
  **The frontend install now SELF-HEALS — this SUPERSEDES the day-25 ENVIRONMENT BLOCKER.** The runner
  (patched 2026-11-08, `amlhive_daily_test_runner.py:195`) prints `⚠️ npm ci failed (lockfile drift) —
  falling back to npm install --package-lock=false` then `✅ Frontend deps installed via fallback
  (lockfile untouched)`, so vitest again runs on a FRESHLY installed tree. Stop classifying that leg as
  "stale tree": a `npm ci` fallback line is now the HEALTHY shape. `origin/dev`'s lockfile (`50fb44a55`,
  zod 3→4.6.7) is still out of sync — fix it if you want `npm ci` itself green, but the cron no longer
  depends on it. **A FALLING 🔴 count is never an escalation trigger** — read it as the band
  improving; a ±1 drift inside a flat band is counter noise; escalate only on a sustained RISE or a
  named non-whitelisted E2E regression.
  **The runner's header prints its START time labelled `AEST` while the host runs AEDT** (`★ AML Hive
  Daily Test Suite — 2026-11-08 02:40:11 AEST` for a `03:40` AEDT dispatch; the header clock is UTC+10),
  and the run takes ~51 min, so `last_run_at` and the output-file mtime are COMPLETION (04:36), not
  dispatch. Neither is a late fire — convert the header (+1 h to AEDT) and compare that to the expr;
  never re-derive a dispatch delay from the output file name.
  **2026-11-10→11-14 (days 36-40) — band FLAT and improving on the 🔴 count; nothing to escalate.**
  backend `9549/44` (⚪35, **🔴9**, down from 12 — a FALLING genuine count is the band improving, never an
  escalation trigger), vitest `286-287p/1f` (**40 consecutive**), E2E `43-46 passed / 4-7 failed`
  oscillating with the SAME hydration-mismatch diagnosis (inline CSS-in-JS `marginTop` camelCase vs
  `margin-top`; 20 consecutive escalated runs), OVERALL `9879-9880 passed / 51-52 failed / 3 errors`. The
  `⚪ 'poetry' not found — fallback to venv pytest` line is the PERMANENT path on this host, not a fault.
  `7 failed` on E2E is still inside the observed 4-7 band — escalate only on a NAMED non-whitelisted test
  or a sustained rise past 7.
  **2026-11-16 (day 41) — 🚨 REAL ESCALATION: the BACKEND leg hit its 5400 s timeout and reported
  ZERO results; the OVERALL line became a fake total.** Output shows only
  `❌ Error: … pytest … timed out after 5400 seconds` then `OVERALL: ❌ 328 passed, 8 failed` — 328 is
  vitest+E2E alone, so backend is UNKNOWN, NOT "backend passed nothing". The ramp that preceded it:
  11-12 3285 s → 11-13 3344 s → 11-14 3757 s → 11-15 5225 s (all ~9549 passed/44-45 failed) → timeout.
  **A RUNNING LEG TIME IS A TREND METRIC — read the per-leg seconds on every run, not just the pass
  count.** Escalate when the leg's duration reaches ~70 % of its ceiling, because the next 1-2 runs are
  then already lost. Trigger here is time-to-ceiling, not a failure count. Probe before patching:
  `cd ~/code/amlhive1/backend && .venv/bin/pytest tests/ --durations=25 -q --tb=no` on the clean tree to
  find the slowest/hanging test (the 11-16 run also merged `origin/dev` at `6a6aba99e`, so size that
  merge too) — Saturday scope, do not cut the timeout from a daily tick.
  Same day, `0959371eec17` (Pluto Chamber Refresh 05:10) failed for the first time in 8 runs:
  `pluto_mempalace_feeder.py --chamber startup-vc` exceeded the 60 s `run_python` budget while the
  MemPalace watcher was draining. **2026-11-17 (day 42) — the backend timeout repeated AND the feeder
  failed a second time on a DIFFERENT chamber** (`cloud-infra` after 10 transcripts, same 60 s
  `TimeoutExpired`, `run_python` at line 161). Two days / two chambers confirms it is systemic load from
  the draining watcher, not a bad chamber. **3-day rule tripped 2026-11-18 (3rd chamber `agent-architecture`) → FIXED: `run_python` now takes `timeout=180` and catches `TimeoutExpired`, so one slow call no longer aborts the remaining chambers** (backup `~/.hermes/backups/scripts_20261118_140846/`; verified by py_compile + a stubbed-exception test of the extracted function + a full `--dry-run` ending RC 0). A timeout line now means raise the budget, never a per-chamber exclusion. 11-17 backend again `timed out after 5400 seconds` and `OVERALL: ❌ 328 passed,
  10 failed` is again vitest+E2E only (backend UNKNOWN). **2026-11-18→20 (days 43-45) — backend timeout FIVE consecutive days; E2E drifting, band otherwise flat.**
  11-18 `327/8` (vitest 284p/1f, E2E 43p/7f), 11-19 `326/9` (42p/8f, 387 s), 11-20 `329/8` (286p/1f,
  43p/7f, 301.8 s) — no backend number in ANY of them, so every OVERALL total is vitest+E2E only. The
  `--durations` probe is mandatory Saturday work; no daily tick may cut the 5400 s ceiling. E2E sits at
  7-8 failures for 3 consecutive runs under the SAME inline-`marginTop` hydration diagnosis — one
  unresolved bug: watch for a NAMED non-whitelisted test rather than re-reporting the count.
  **2026-11-21 (day 46) — the timeout streak CLOSED with no intervention**: backend completed
  `9683 passed, 45 failed (3698.7 s)` with `⚪ 35/45` gaps + `🔴 10 genuine`, OVERALL `10016 passed /
  52 failed / 3 errors`. A leg that finishes under its ceiling after a timeout streak is the streak
  ENDING — re-derive from that run's own output and never carry the timeout forward as live. **11-22 identical
  (9683/45, ⚪35, 🔴10, 10016/52/3) — flat band, not an escalation.** The leg is
  still at ~68 % of the 5400 s ceiling, so the Saturday `--durations` probe stays open; a resumed
  timeout is a NEW occurrence.
- **`SSM: Error response from daemon: No such container: amlhive-app-1` on `3ebed4e59ee3` (AML Hive Daily
  Business Report, 21:15) — a CONTAINER RENAME, and production is uniformly HEALTHY. Class this as a
  script fault, NOT a prod outage.** Seen 2026-10-26 21:15, the first report after the 0.50.185 deploy:
  `amlhive_daily_report.py` fell back to `docker exec amlhive-app-1 python3` (no psql client on the host)
  and the container no longer existed. Verify in this order before touching anything:
  `curl -s https://api.amlhive.com.au/version` (answered 0.50.185), fleet monitor 05:02 file (API 200,
  frontend 200, both EC2s ok), then `ssm_shell(env, get_instance_id("amlhive-prod-backend", …),
  "docker ps -a --format '{{.Names}} :: {{.Status}}'")` → **`amlhive-api-1` + `amlhive-worker-1`**, i.e.
  the compose service was renamed `app` → `api` and a worker sibling appeared. The frontend is unchanged
  (`amlhive-frontend`). Fix shape: resolve the container from `docker ps` at runtime (env override still
  honoured), retry once on `No such container` because a deploy can rename it mid-run; proved with a real
  `SELECT 1` → `1|amlhive` through the patched transport. **Generalise: any `docker exec <name>` in a cron
  script is a stale-name time bomb — resolve it, never hardcode it, and never read the container error as
  an outage without curling the API.**
 `0320d41d6d71` unchanged standing shape (685/2: portal 649p/1f + the 9p 5400 s timeout on
 `tapease_portal_fastapi_a2square`; nextjs 36p/0f green). `5b95adcb27d4` reads `ok` while its report is
 still `🔴 BLOCKED` — it exits 0 after filing drafts to the vault, so `ok` never means "landed in repo".
 **2026-10-28 (day 22) — see the COMPRESSED block above; band flat, E2E counter tripped at 3.**
- **A skill at ≥99.9% of the 100,000-char SKILL.md cap is effectively UNPATCHABLE — `skill_manage`
  rejects the whole batch when the RESULT exceeds the cap, so even a correct fix fails.** Seen
  2026-10-10: `podcast-knowledge-base/SKILL.md` sat at 99,978 chars (22 chars headroom) and a
  stale-schedule fix was rejected with `content is 100,095 characters (limit: 100,000)`. Workaround for
  a daily tick: make the edit NET-NEGATIVE (shorter than the text it replaces) so the result fits. The
  real fix is Saturday scope — move a section into `references/`. Check the cap BEFORE patching:
  `len(Path(skill).read_text())` vs 100,000.
  **This skill itself was the worst offender and was COMPACTED 2026-10-28 (92,526 → 78,819 chars).**
  The expensive part was a per-day running log of `044c0bc41e31` (days 3-22, one paragraph per day,
  each repeating the same band). Rule: a per-day watch that emits a paragraph per run is a LOG, not a
  lesson — once a band is stable for 3+ days, replace the whole span with ONE `**Days N-M COMPRESSED**`
  block that keeps only (a) the band's start/end numbers, (b) every ROOT CAUSE with its proof, and
  (c) the escalation trigger. Keep day-by-day narration only for the current un-resolved incident.
  Compact with a line-range script (assert the anchor lines first, back the file up to
  `~/.hermes/backups/` before writing) rather than a 188-line `patch` match.
- **`daily_cron_audit.py`'s `=== legacy 'fallback_model' config key ===` scan is a DOCUMENTED FALSE
  POSITIVE — do not "fix" the two hits.** `monitoring-alert-verification` and `llm-cost-routing` name
  `fallback_model` only to explain it is the LEGACY key merged after the canonical
  `fallback_providers`. The real signal is `jobs referencing fallback_model: none`. Read the line's
  context before touching it; deleting it would remove the explanation of the key-shape whose absence
  broke fallover on 2026-09-15.
- **The `12:35 AM` ingestion time in `podcast-knowledge-base` was a stale doc, not a live job
  (fixed 2026-10-10).** No job at `35 0 * * *` exists in `jobs.json` or the WSL crontab; the live
  ingestion is the 4:00 AM `d4d77c41f6c0`. Same class as the `044c0bc41e31` stale-NAME trap — verify
  against the live expr, not the prose.
- **`e6b671746eaf` (Weekly Test Report — A2Square + AML Hive, Wed 02:00) has a STEADY standing
  pattern — do NOT report as a new incident.** Every run since at least 2026-09-23 has exited 1 with the
  SAME two legs: `a2square/portal: ❌ TEST FAILURE — 649 passed, 1 failed` and
  `amlhive1/backend: ⚠️ ENVIRONMENT BLOCKER — Could not install the locked dependency set for
  /mnt/c/Code/github/amlhive-tech/amlhive1/backend`. The second leg is a PATH artifact, not a code fault:
  the weekly report tests the **Windows** clone (`/mnt/c/...`), where the locked backend deps cannot
  install over 9p — the same suite is green via the WSL clone `~/code/amlhive1` (see `044c0bc41e31`).
  The 33 git-sync legs all report ✅ and the report file IS written
  (`~/.hermes/research_outputs/weekly-reports/weekly-report-<date>.md`). Escalate only if the ✅/❌ leg
  composition changes.
- **`0320d41d6d71` (A2Square Weekly Test Suite, Mon 02:30) has a STEADY standing pattern of 2-3 failures/errors per week — do NOT report as a new incident.** 2026-10-05: 684 passed / 3 failed-errors (`portal_backend_lambda_eventbridge` 649p/1f; `tapease_portal_fastapi_a2square` **0 passed 0 failed 1 error** = collection failure, No Fake Pass Rule; `tapease_frontend_nextjs_prod` `npm ci FAILED: ic, install-clean, isntall-clean` + 35p/1f). 2026-09-28: 685p/2 (portal 1f + the same `npm ci FAILED` line). The `npm ci FAILED: ic, install-clean, isntall-clean` string is npm's did-you-mean output and has recurred across weeks. Escalate only on a change in the COUNT TREND or a new repo component.
 **2026-10-12: composition moved, and the `0 passed, 0 failed, 1 error` leg is ROOT-CAUSED — it is an
 INTERPRETER-availability fault, not a code fault.** `685 passed, 2 failed/errors`:
 `portal_backend_lambda_eventbridge` 649p/1f (steady); `tapease_portal_fastapi_a2square` **0 passed,
 0 failed, 1 error** preceded by `⚪ not usable: <python> — <path>: No module named pytest`; and
 `tapease_frontend_nextjs_prod` is now **GREEN** (`✅ npm ci OK`, 36 passed / 0 failed) — the old
 `npm ci FAILED: ic, install-clean, isntall-clean` line is GONE, so stop describing it as standing.
 Cause: the runner resolves its pytest interpreter from `~/.hermes/cache/testenvs/<dir>`, where `<dir>` is
 `a2square-portal` for `portal_backend_*` but the REPO NAME for everything else — and
 `~/.hermes/cache/testenvs/tapease_portal_fastapi_a2square` **does not exist** (only `a2square-portal`,
 `a2square-portal-backend`, `amlhive-backend`, `amlhive1-backend` do). The repo has no `.venv` either, so
 the runner falls back to `sys.executable` = the cron PM env python, and **none of the four PM envs ships
 pytest** → the probe exits non-zero → the leg collects 0 tests and reports "1 error" (No-Fake-Pass: this
 is never a skip/pass). Remediation is OWNER-LEVEL managed state, so alert rather than apply from a daily
 tick: create that testenv (`python3 -m venv ~/.hermes/cache/testenvs/tapease_portal_fastapi_a2square` +
 install the repo's test deps incl. pytest), or make the runner report an ENVIRONMENT BLOCKER (as the
  `unified_weekly_report.py` amlhive leg does) instead of a test error.
 **2026-10-19: that remediation was applied and the leg's failure MODE CHANGED — the interpreter gap is
  gone, a 90-minute TIMEOUT replaced it.** `tapease_portal_fastapi_a2square` now resolves a real
  interpreter (`/mnt/c/Code/github/a2_square/tapease_portal_fastapi_a2square/.venv/bin/python`), so the
  old `0 passed, 0 failed, 1 error` / "No module named pytest" signature no longer appears; the leg now
  runs and dies with `Command [...'-m','pytest','tests/','-q','--no-header','--tb=line'] timed out after
  5400 seconds` (9p-mounted `.venv` on `/mnt/c`, not a code fault). Do not re-apply the testenv fix —
  alert that the Windows-clone venv is too slow over 9p and needs a WSL-side testenv instead. Overall
  composition stayed `685 passed, 2 failed/errors` (portal 649p/1f steady, nextjs 36p/0f green).
- **`ModuleNotFoundError: No module named 'chromadb'` in one or more same-morning `no_agent` scripts
  (seen 2026-09-28) — CRON SCRIPT INTERPRETER REGRESSION, not a MemPalace fault.** POSIX `no_agent`
  `.py` scripts no longer run on `~/.hermes/venv`: `cron/scheduler_script.py::_posix_cron_script_argv`
  runs them on the **PM dependency env** (`pm.environments.project_python(repo)` →
  `~/.hermes/installs/<install>/environments/<hash>/venv/bin/python`), which has **no chromadb** (and
  none of the ad-hoc packages the scripts historically imported by accident). It sets **no PYTHONPATH
  on purpose** (#123440) — do NOT add one as a workaround. Only scripts importing chromadb at MODULE
  TOP LEVEL break (`mempalace_health.py`, `sc_watch_to_mempalace.py`, `mempalace_reconcile.py`,
  `gumby_mempalace_query.py`, `mempalace_dedup_podcast.py`, `rebuild_drawers.py`, `seed_chambers.py`);
  scripts that shell out to `~/.hermes/venv/bin/python3` keep working — that is the standing fix
  pattern (`mempalace_watcher.py` → `pluto_mempalace_feeder.py`). Diagnose with
  `hermes pm env` + `ls <env>/venv/lib/python*/site-packages | grep -c chromadb`; cross-check the
  update's own chromadb health step in `~/.hermes/logs/hermes_update.log` (it only ever verifies
  `~/.hermes/venv` — which is why it reported "all 1 chromadb-bearing venv(s) healthy" while cron was
  broken). PM-native fix: `hermes pm install chromadb`; it is an owner-level managed-state change, so
  alert rather than apply it from this cron. **Status 2026-09-30 — SUPERSEDED; do NOT re-report these as daily reds, and do NOT re-open this as day-N.**
 All three jobs named here are now paused or healthy: `0e14d2e1095f` and `57e72391a773` are
 `enabled: false` (their checks moved INSIDE the chain orchestrator `7e4a2379157d`), `d941471b7fc8` ran
 `ok` on 09-30 ("nothing new to feed"), and `a2ff28e23482` is paused too. chromadb is STILL absent from all
 three PM envs (`~/ .hermes/installs/*/environments/*/venv` → 0 hits), so the standing rule is the
 CODE-side one: any cron script that imports chromadb — directly or via `pluto_mempalace_feeder` — must
 self-heal its interpreter AT IMPORT TIME (`os.execv` to `~/.hermes/venv/bin/python3`; recipe and the
 `grep -ln '^import chromadb'` sweep in the `podcast-knowledge-base` skill). A NEW import error dated
 after 2026-09-30 is a fresh fault with the same cause; report it as such.
- **A red job can hide a SECOND fault behind the one you already classified (2026-09-29).** The same
  morning's `57e72391a773` (reconcile) red was blamed first on the chromadb regression and on the
  verifier timeout — but its 8 unlanded files had a third, independent cause: the three-filter router
  emits no sidecar at all, so the artefacts can never land. When a job stays red after its cluster's
  cause is understood, re-read ITS OWN output and follow the artefact list to the producer before
  closing it with the cluster verdict.
- **`podcast_capture_verify_daily.sh` (`4ef6e889e8d6`) — ✅ RESOLVED 2026-09-30, historical (do NOT
  re-classify as a timeout).** It timed out on three consecutive mornings (09-27 → 09-29) at `--limit 60`,
  because the leg makes a live maker call per episode plus an independent checker call and retries at a
  larger token budget on `finish_reason=length` — 2-4 min/episode cannot fit a 7200 s cron timeout. The
  wrapper is now `--limit 12 --deadline 6300` under `timeout 6900` (a DEADLINE it can honour, not an outer
  kill), and the 09-30 run finished in 29 min with exit 0 (`locked=4 needs_human=8`, $0.113). If a timeout
  reappears, size the batch to the deadline — never conclude the verifier is broken.
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
- **`delivery_failed` with an EMPTY `last_error`**: the script ran and wrote its artifact — the failure is the outbound send, not the job. Confirm in `~/.hermes/logs/agent.log`: `Job '<id>': delivery error: Telegram send failed: Timed out (target telegram:<id>)`. Transient network / flood-control (seen 2026-09-13 07:00 on `8d3be30eb9f7`, whose output file was complete and healthy). Do not escalate unless it repeats on consecutive days — the next scheduled run resends. Seen 2026-11-04
  on `937bb914c497` (`last_status: delivery_failed`, `last_error` empty, though the job had printed
  `OVERALL: ✅ PASS` four runs running): `agent.log` read `live adapter delivery to
  telegram:-1004485329864 failed: Timed out, falling back to standalone` — the sync was green and the
  owner simply never received that day's report, so report the MISSING DELIVERY, not a sync failure.
