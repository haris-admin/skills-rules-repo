# W38 Diagnostic Findings — Week Ending Fri 18 Sep 2026

## Headline events

1. **DeepSeek provider outage + stream stall — 12 runs dead on 15 Sep.**
   `api.deepseek.com` returned `HTTP 503 — Service is too busy. We advise users to temporarily
   switch to alternative LLM API service providers`, then `Stream stale for 600s ... Killing
   connection` → `[Errno 32] Broken pipe`. 77 broken-pipe lines in `logs/errors.log`, **all on
   that date**. The fallback ladder did not engage because a mid-stream stall is not a retryable
   transport error. One root cause, 12 symptoms. Sep 15 produced 5 research artefacts vs 13–19
   on normal days, and the 6:00 AM briefing never reached Haris.
2. **`state.db` structural corruption on 17 Sep — 8 agent crons dead 06:27→11:01.** Repaired
   13:52; gateway restarted 23:40 with a second snapshot. Verified: `PRAGMA integrity_check` ok,
   both FTS tables pass, **131,607 message rows (more than pre-recovery), no history lost**.
   Snapshots: `backups/corrupt-state-20260917/` and `backups/corrupt-state-20260917-live-2340/`.
   `jobs.json` still showed 2 of the 8 as failing a day later — lagging indicator.
3. **The Sat 12AM auto-improvement executor was disabled on 15 Sep.** `159702fe072c`
   (dream-mode: deletes Supabase rows, rebuilds Chroma, patches cron config) and `0dbba3db3116`
   (daily repo sync hard-reset) were disabled by the cron audit. The Friday review now has no
   automated implementer for its action list.

## Metric-integrity findings

- **`jobs.json` `last_status` is a lagging indicator in BOTH directions.** All 12 Sep 15 failures
  had recovered to `ok` by Friday; 2 state.db casualties still read `error` after repair.
  Output-header scanning is the only honest weekly tally: **47 of 512 runs (9.2%) failed across
  26 jobs** in W38, versus the 10-error snapshot.
- **Podcast counts: use `Done. New episodes: N`.** The per-show `New: N episodes` line is capped
  by `Max 3 new episodes per show` (summed to 7 when the truth was 95).
- **W37's 203-episode claim did not reconcile** with its own per-day footers (109). Check the
  previous review's figure against its logs before trending.
- **Feedback loop static for a 4th week**: `1/6 findings used, topics_used: ["AUSTRAC"]` for 8
  consecutive days; every finding at `used_count == total runs, skipped_count: 0`. The W37 exit-3
  guard fires honestly (`failure_streak: 7`) but the scorer itself is unrepairable without
  `USED:`/`SKIPPED:` markers from the brief generator.

## Verified-working fixes (do not re-flag)

| Fix | Evidence |
|---|---|
| Alexandria `--autostash` push self-heal | Sep 18 18:30: `push rc: 1` → `rebase+retry attempt 1` → `push rc: 0` |
| `cron_verify.py` schedule-aware | `with_false_flags: 25` — suppressing, not failing |
| TTS (Gemini provider) | `voice_outputs/pluto_briefing_2026-09-1{6,7,8}.mp3` (1.4–1.6 MB) |
| Monitor delta reporting (NEW vs STANDING) | Sep 18 23:00 report: `NEW (4)` + `STANDING: none` |
| Zero-test guard (daily runner only) | `amlhive_daily_test_runner.py` lines 222–240 |
| Chamber-refresh dedupe guard | hash + watcher-marker, fail-closed |
| `amlhive1` clean working tree | `git status --porcelain` empty (~1,240 dirty files gone) |

## Open items carried into W39

| Item | Job | Class |
|---|---|---|
| AMLHive test suite — 28-run failure streak (vitest Blob, Playwright selector) | `044c0bc41e31` | real, longest-running |
| A2Square weekly — 2/3 repos collect 0 tests, pytest 120 s timeout | `0320d41d6d71` | real |
| Unified weekly report prints `0 passed, 0 failed` (no zero-test guard) | `e6b671746eaf` | real |
| CRAP Score — `git checkout pluto_pr` → "resolve your current index first" | `153af82d274e` | real, local git state |
| CMDB dashboard :3009 — nothing listening; report shows fake `A$0.00` | `4c28178fad0f` | real, 2 days |
| `acnc-charities` HTTP 500 | `937bb914c497` | external upstream |
| Feedback scorer degenerate | `59f18c4d557c` | 4th week |
| Competitor Intel 0 hits, 7/7 days | `1a13a2d49682` | 3rd+ week |
| `skills-rules-repo` merge fails daily | `c23dc3f73e2d` | undiagnosed |
| `90115d0e06ce` (S&C five partners) never executed; first run due Sat 19 Sep 09:00 | `90115d0e06ce` | unverified |
| Shutdown-interrupt terminal state (streak 2); 06:10 shift never applied | `7d24b37a03f2` | recurring |
| Honcho state file unbounded (87 entries) | `pluto_honcho_bridge_daily` | W29 carry-over |

## Useful commands

```bash
# the week's real failure tally (NOT jobs.json)
python3 - <<'PY'
import glob,os,re,collections
d=collections.Counter(); r=collections.Counter()
for p in glob.glob('/home/habib/.hermes/cron/output/*/*'):
    b=os.path.basename(p)
    if os.path.isdir(p) or not re.match(r'2026-09-(1[2-8])',b): continue
    j=os.path.basename(os.path.dirname(p)); r[j]+=1
    t=open(p,errors='ignore').read(4000)
    if '(FAILED)' in t or 'script failed' in t.lower(): d[j]+=1
print('failed',sum(d.values()),'of',sum(r.values()),'runs')
PY

# provider-stall detection
grep -c "Errno 32" ~/.hermes/logs/errors.log

# bridge-state / dashboard liveness
curl -s -o /dev/null -w '%{http_code}\n' http://127.0.0.1:3009/api/status
ss -ltnp | grep 3009
```
