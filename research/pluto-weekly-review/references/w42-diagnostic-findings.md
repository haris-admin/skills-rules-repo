# W42 Diagnostic Findings (week ending Fri 9 Oct 2026)

Window 2026-10-03 → 2026-10-09 (AEST; DST switched to AEDT on Oct 4). Review ran on schedule:
`fire_claim 2026-10-10T00:05:21+11:00` = Fri 23:05 AEST.

## 1. `cross_ref_verify.py` is blind to output-body failures — never let it clear a claim

Both `chromadb import fails in chamber refresh` (0959371eec17) and `podcast chain assertion red 3 days`
(7e4a2379157d) came back `DO NOT REPORT — healthy` because the tool reads only `jobs.json`
`last_status` + `last_run_at`. The chamber-refresh feed genuinely failed on Oct 3 and the chain
assertion genuinely exited 1 with a RED banner on Oct 3, 4 and 8 — the *last* run of each job was
green, which is exactly the lagging-indicator trap already documented for `jobs.json`.

**Rule:** use `cross_ref_verify.py` only to kill stale-state complaints ("job X is broken" when it is
fine now). For any claim about a specific run's content, open the `cron/output/<job>/<date>_*.md`
body and quote it. A verifier exit code of 2 is not evidence about a run's body.

## 2. Feedback loop has a SECOND degeneracy — topic level is inert

`signal_scores.json` → `topic_scores` carried `AUSTRAC: {used: 33, total_signals: 0, score: 0.0}` and
`total_signals: 0` for every other topic. Nothing can be boosted or demoted; the topic layer exists
only on paper. Simultaneously `feedback_*.json` reports `topics_used: ["AUSTRAC"]` for **7/7 days** —
topic attribution has collapsed to one label.

**Detection:**
```bash
python3 -c "import json;d=json.load(open('/home/habib/.hermes/research_outputs/feedback/signal_scores.json'));print(d['topic_scores']);print(sum(1 for v in d['findings'].values() if v.get('score')))"
```
Finding-level attribution can be healthy (29/89 findings with `used_count=1`) while the topic layer is
dead — check both. Report the topic layer as UNMEASURED-in-practice, not as "scorer fixed".

## 3. DST change re-ran completed evening jobs via `cron.timezone_migration.catch_up`

On 2026-10-04 (AEST→AEDT) ~30 `cron.timezone_migration.catch_up` warnings fired and four evening jobs
each produced two output files ~1h apart — `be81c61778a8`, `be5061d19a5a`, `28bf484caedd`,
`0fc5019948be` (Oct 4 23:0x **and** Oct 5 00:0x). Catch-up has no "already ran recently" guard, so
artifacts were rewritten after delivery (the W39 harm class, now clock-triggered).

**Detection (day-boundary duplicates, DST weeks):**
```bash
for j in <job_ids>; do echo -n "$j: "; ls ~/.hermes/cron/output/$j/2026-10-0[45]_* | xargs -n1 basename | tr '\n' ' '; echo; done
```
Do not call the many `*/2h` or `*/4x daily` jobs "duplicates" — count runs/day against the schedule
expression first (`e736e32679ab` = every 2h = 12/day by design).

## 4. `event loop stalled … (GIL pressure suspected)` is a countable signal, and it self-cleared

`hermes_cli.web_server` stalls: 27 / 124 / 235 / 145 warnings on Oct 3/4/5/6, then **0** from Oct 7 —
self-resolved by the Oct 6 16:00 gateway restart. Nothing was fixed; there is no tripwire.

**Detection:** `for d in 03 04 05 06 07; do grep -c "^2026-10-$d.*event loop stalled" ~/.hermes/logs/errors.log.1; done`
Report the cluster + the resolution date, and recommend a >100/day alert rather than a code fix.

## 5. `errors.log` rotates fast — state the retention window before any week-level claim

`errors.log` held only 6 lines (Oct 9 20:45 onward); the week lives in `errors.log.1`
(2026-09-25 → 2026-10-09 20:45). `executions.db` retained only from 2026-10-07T06:55. Always name the
window; a "zero provider stalls this week" claim is only valid for the covered range.

## 6. Paused lanes: probe the state file, then report STANDBY not failure

Pre-Dispute's 12h report (`92e8ab1f5102`) prints `🟡 STANDBY — worker crons are paused; endpoints
backend=DOWN acma=DOWN`; `e3cc72366dd7` + `ff18d93e2d10` are `enabled: false` since 2026-09-26. That is
a parked lane, not an outage — report it as STANDBY with the pause date, never as down service.

## 7. Verified-working (do NOT re-flag)

- **W41 HIGH #2 is IMPLEMENTED:** `agent/error_classifier.py` routes
  `RuntimeError … "consecutive stale attempts" … "aborting this call"` to `_v(_R.timeout, **_ABORT_FALLBACK)`
  where `_ABORT_FALLBACK = {"retryable": False, "should_fallback": True}` — the fallback ladder now
  engages on the abort that caused W41's missed briefing. Zero occurrences this week.
- **All 5 weekday briefings + Gemini-TTS voice MP3s** (Oct 5-9) present in `voice_outputs/`.
- **Daily maintenance engine** (`575918cbc242`) is the working implementer: 1-2 skills patched and
  mirrored daily, memory consolidated, cron failures classified, 0 broken scripts all week.
- **`research_outputs/inbox_*.json` growth is bounded, not runaway:** 7-day rotation, 5,947 files /
  8.73 GB steady state, +~120 MB/day, 877 GB disk free. Report it as a hygiene/target breach
  (<300 MB target, 29× over), NOT as a disk emergency.
- **amlhive 11PM `0 P0 / 2 P1 / 1 P2` all "observability drift"** = the delta-reporting feature working;
  exit 0 because the P1 count did not exceed 2.
