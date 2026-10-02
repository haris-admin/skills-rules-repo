# W37 Diagnostic Findings — week ending Fri 12 Sep 2026

Written by the Saturday dream-mode self-improvement cron (`159702fe072c`).
Each item = a failure class worth recognising again.

## 1. `cron_verify.py` stall heuristic — now schedule-aware (FIXED)

**Was:** flat rules (`*/` in expr → "high-frequency", else `hours_since > 48` → "stalled") produced
5+ deterministic false positives every week: P3 Competitor Sweep, Weekly CRAP Score, PSP Reform
watch, Month-End, Start-of-Month, plus `last_run_at: null` on a cron whose first Monday had not
yet arrived.

**Now:** `schedule_window_hours(expr)` derives the widest legitimate gap from the expression
itself — weekly single-day = 174h, day-list = widest circular gap × 24 + 12, day-of-month = 756h,
daily = 26h — and the checks are skipped entirely for paused/disabled jobs and for one-shots
(`once at <datetime>`) that are not due yet.

**Rules for the reviewer:**
- Never report "stalled" from hours-since-last-run alone; compare against the job's own schedule.
- `state: paused` + `enabled: false` = intentionally stopped (e.g. `a0b1f0f642af` fleet monitor,
  superseded; `1dc6606ac8c5` Alexandria archive). Not an issue.
- A cron with `last_run_at: null` created less than one schedule window ago is **not**
  never-executed.
- Superseded flags are emitted as `false_flags` ("suppressed stall flag …") so the suppression
  itself is auditable.

**Verification:** `python3 ~/.hermes/scripts/cron_verify.py --issues-only` returns **0** stall
flags while still listing genuinely failed jobs (W37 result: 4 real issues, all of them the
"status=error but complete output" transient class).

## 2. A test suite that executes ZERO tests can still look green (FIXED)

`guard_no_tests()` in `amlhive_daily_test_runner.py` only caught runs where **no** test-count
marker appeared. A bootstrap crash that still prints `0 passed` parsed as `ran=True,
passed=0, failed=0` → no failures, no errors → potentially a green OVERALL line.

**Fix:** `ran=True` with `passed == 0 and failed == 0` is now forced to `errors=1`
(`zero_tests: True`), so it can never be summarised as a pass. Verified against three cases
(zero-test, healthy 48-pass, not-run) with an AST-extracted copy of the function.

**Rule:** for any suite with a known non-zero test count, "0 executed" is an ERROR, not a pass.

## 3. `pluto_pr` ↔ `origin/dev` add/add conflicts block the test lane (OPEN — High)

`git merge origin/dev` into `pluto_pr` fails with `CONFLICT (add/add)` in
`backend/prod_issues/issue-287-c464-refdb-async-sync-false-pass.md` and
`openspec/changes/468-refdb-async-worker-init-and-monitoring/tasks.md`.
It has failed on **every** daily test-suite run from at least Sep 9–11.

The runner continues and tests the **unmerged** tree, so the daily "AML Hive test suite" result is
*not* a dev-integration signal — it is "pluto_pr as of the last successful merge".
Detection: `grep -m2 'CONFLICT' ~/.hermes/cron/output/044c0bc41e31/<latest>.md`.
Fix requires resolving the two add/add conflicts in the repo lane (human/Codex), not a Hermes change.

## 4. Playwright E2E is fully dark — `EventEmitter.defaultMaxListeners` (OPEN — Med)

`frontend/instrumentation.ts` (dev-only branch of `register()`) does:
```ts
const { EventEmitter } = await import("node:events");
if (EventEmitter.defaultMaxListeners < 20) { EventEmitter.defaultMaxListeners = 20; }
```
In Next 16's dev server bundle `EventEmitter` is not the class there → `Cannot read properties of
undefined (reading 'defaultMaxListeners')` → `next dev` dies during the Playwright `webServer`
bootstrap, so E2E runs 0 tests (Sep 11: first occurrence; 48 passed Sep 10).

**Safe pattern:** resolve the class defensively and never let diagnostics kill the server:
```ts
const events: any = await import("node:events");
const EE: any = events.EventEmitter ?? events.default?.EventEmitter ?? events.default;
if (EE && EE.defaultMaxListeners < 20) EE.defaultMaxListeners = 20;
```
wrap it in `try { … } catch { /* diagnostics must not break startup */ }`.

This is a **repo** fix (code lane with node_modules + a real `npm run dev`), not a Hermes fix.
The Hermes-side false-green guard (§2) is done so the regression can never hide again.

## 5. Never exec a Pluto runner script to test its functions

`amlhive_daily_test_runner.py` has its repo sync (`reset --hard origin/pluto_pr`, merge
`origin/dev`, remove untracked blockers) at **module level**. Importing/exec'ing its source to unit
test a helper runs that sync against the real checkout — W37 did exactly this and produced a
conflicted merge state, repaired with `git merge --abort` (HEAD restored to `origin/pluto_pr`, clean).

**Rule:** extract the function with `ast` (`ast.Module(body=[func_node])`) and exec only that node.
Same applies to any script with module-level side effects.

## 6. Feedback scorer degeneracy — now detected, not reported as a metric

`feedback_*.json` reported a byte-identical `1/6 findings, topics_used: [AUSTRAC]` for 8+ days and
`signal_scores.json` had **every** finding at `used_count == runs, skipped_count == 0, score == 1.0`
with `AUSTRAC: used 115 / total_signals 0`. Root cause: with no `USED:`/`SKIPPED:` markers in the
brief, usage is *inferred*, so it only ever accumulates.

**Fix in `pluto_feedback_processor.py`:** `compute_diagnostics()` records findings tracked, distinct
used counts, recorded skips, markers found, matched topics and brief length; a degenerate state
prints `⚠️ DEGENERATE SCORER — usage never recorded` and **exits 3** (never a green cron), the
pre-fabrication counts were zeroed once and stamped with `fabricated_history_reset_at`, and
the utilisation line now reads `UNMEASURED (degenerate scorer)` instead of `17%`.

**Rule:** if a metric is identical across many consecutive days, treat it as a broken measurement
until the raw inputs are shown. Exit non-zero on a degenerate scorer so it cannot hide.

## 7. Source-blindness vs a quiet market (competitor intel)

`competitor_intel.py` scanned only `research_*.json` + `synthesis_*.json` + `arxiv/actions`
(14 items / 16,243 chars) → 0 hits for 79 tracked competitors, 7/7 days. Now it also ingests the
`gumby-action-brief-*.md`, `gumby-brief-input.md`, `morning-briefing-*.md` and the day's podcast
transcripts (Sep 11: 45 items / 34,981 chars — 2.2× more text), tracks a zero-hit streak in
`.competitor_intel_state.json`, writes `"status": "degraded"` after 3 consecutive zero-hit days, and
`briefing_improver.generate_competitor_section()` skips the section when degraded.

**Residual (needs Haris):** still 0 hits over the larger corpus. Either the market is genuinely
quiet for these competitors, or the matcher (name/≥5-char brand token **plus** a signal keyword
within a ±500-char window) is too strict. Decide which before spending more effort on sources.
