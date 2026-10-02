# W41 Diagnostic Findings — week ending Fri 2 Oct 2026

## 🔴 The "Provider unresponsive" non-retryable abort converted into a USER-VISIBLE MISS

W41: `c527fed4a1da` (Morning Briefing 6:00) and `0fb6bf47f704` (Daily Learning 6:15) both died on
Oct 2 with `RuntimeError: Provider has been unresponsive (no response received) for 6 consecutive
stale attempts — aborting this call to avoid an indefinite stall`. The abort is **non-retryable**, so
the fallback ladder (Qwen3.8 → Gemini3.8 → DeepSeek V4.1) is never consulted — the run dies on
`deepseek-flash`.

**Report the delivery impact, not just the error.** A briefing cron that fails before its final
response delivers nothing. Two cheap proofs of non-delivery:
```bash
# 1. the run produced only the failure banner, no report body
wc -c ~/.hermes/cron/output/c527fed4a1da/2026-10-02_*.md      # ~2.8KB = failure trace only
# 2. the voice leg never ran — voice_outputs/ stops the previous day
ls -t ~/.hermes/voice_outputs/ | head -3
```
Distinguish this from the *stale-stream* family (W38 `Errno 32` / 600s stall): that one is a stream
that opened then stalled; this one is **no response at all** after 6 attempts. Both are invisible to
the fallback ladder, but only this one is explicitly self-labelled non-retryable.

Detection sweep:
```bash
grep -rn "Provider has been unresponsive" ~/.hermes/cron/output/*/2026-* | head
```
Count it as **1 root cause** however many crons it kills.

## 🔴 chromadb exposure is a per-script property — sweep it, never assume the fix is fleet-wide

The `_sanitized_env()` guard (strip foreign `site-packages` from the child `PYTHONPATH`) exists ONLY in
`mempalace_watcher.py`. W41 confirmed **9 of 10** chromadb-importing scripts are still exposed, and
they fail intermittently (Sep 20, Sep 25, Oct 2) depending on whether the gateway's poisoned
`PYTHONPATH` is inherited.

```bash
for f in $(grep -rln "import chromadb" ~/.hermes/scripts/*.py); do
  grep -q _sanitized_env "$f" && echo "GUARDED $(basename $f)" || echo "EXPOSED $(basename $f)"
done
```
W41 result: guarded = `mempalace_watcher.py`; exposed = `gumby_mempalace_query.py`,
`mempalace_dedup_podcast.py`, `mempalace_health.py`, `mempalace_optimize.py`,
`pluto_chamber_refresh.py`, `pluto_cross_chamber_synthesizer.py`, `pluto_mempalace_feeder.py`,
`rebuild_drawers.py`, `seed_chambers.py`.

**Rule:** when a Haris session ends with "the other N scripts share this exposure — say the word",
that N is an OPEN item until the sweep returns nothing. Record it as a HIGH improvement with the
sweep as its verification command. The failure signature is
`ModuleNotFoundError: No module named 'pydantic_core._pydantic_core'` inside a
`.../environments/<gen>/venv/lib/python3.14/site-packages/pydantic_core/__init__.py` traceback —
the foreign interpreter's path in the traceback IS the proof.

## 🔴 Sessions moved out of `sessions/*.jsonl` into `state.db` — query the DB or undercount to zero

An mtime scan of `~/.hermes/sessions/*.jsonl` for the review window returned **0 user sessions**,
which is wrong: `session_search` and `state.db` both showed **12 Telegram sessions**. Only 9 jsonl
files remain on disk (1 non-cron); live sessions are rows in `state.db`.

```bash
python3 - <<'PY'
import sqlite3, datetime
lo = datetime.datetime(2026,9,26,tzinfo=datetime.timezone(datetime.timedelta(hours=10))).timestamp()
hi = lo + 7*86400
c = sqlite3.connect('file:/home/habib/.hermes/state.db?mode=ro', uri=True)
for r in c.execute("""SELECT source,count(*),sum(message_count) FROM sessions
    WHERE started_at>=? AND started_at<? GROUP BY source""", (lo,hi)): print(r)
for r in c.execute("""SELECT id,datetime(started_at,'unixepoch','+10 hours'),source,chat_type,message_count
    FROM sessions WHERE started_at>=? AND started_at<? AND source NOT IN ('cron','subagent')
    ORDER BY started_at""", (lo,hi)): print(r)
PY
```
`started_at` is a **unix float** (not an ISO string) — a `LIKE '2026-10-%'` predicate silently returns
nothing. Sources: `cron` (dominant), `telegram`, `subagent`, `cli`, `webhook`. Also available from the
same table: `estimated_cost_usd` / `actual_cost_usd`, `api_call_count`, `input_tokens`,
`output_tokens` — use them for the spend line instead of guessing.

## 🟡 `research_outputs/inbox_*.json` is an unbounded disk sink

The every-5-min watcher writes an `inbox_<ts>.json` file per run regardless of whether anything
changed, and the files are large (up to 10 MB). W41: **1,797 files / 1.1 GB** inside an 8-day window,
with the per-day rate *accelerating* (199 → 448). `state.db` is separately ~770 MB.

```bash
du -sh ~/.hermes/research_outputs
ls ~/.hermes/research_outputs/inbox_*.json | wc -l
ls ~/.hermes/research_outputs/inbox_*.json | sed 's/.*inbox_//;s/_.*//' | sort | uniq -c | tail -10
```
Report as a retention gap (MEDIUM), not as a failing cron — nothing errors, the disk just fills.

## 🟡 Honcho rotation note is the only evidence rotation ran — check its date

`research_outputs/.honcho_bridge_state.json` carries `_rotation_note` (e.g. "Rotated 2026-09-05:
retain last 14 days of dated files"). W41: last rotation **27 days** before the review and
`pushed_files` back to 92 entries — the stated 14-day retention was not being enforced. Compare the
note's date against the review date; a stale date plus a large `pushed_files` = rotation stopped.

## 🟡 Gateway "another instance is already running" can persist WITHOUT the respawn storm

W41 had **23** refused-start events (18× the live PID 94301 across Sep 29–Oct 2, 5× the prior PID
55614 across Sep 25–27) and **zero** `restarted N times in 120s` / `Refusing --replace` lines. No
outage, no counter climb, gateway healthy and single-instance. Grade it MEDIUM (contention: something
keeps attempting a second start), not P0 — the P0 grading in this skill applies only when the
backoff/refusal triad is present and the restart counter is climbing.

## ✅ Verified-healthy in W41 — do not re-flag

- **Fleet monitors**: AMLHive + TapEase 4× daily all `ok` (5AM/11AM/5PM/11PM).
- **AMLHive Daily Business Report** (`3ebed4e59ee3`) 3/3 — the SSM-based RDS password fix holds.
- **Alexandria sync** (`fc726783497f`): `push rc: 0` on every run; library ~4,500 files updated.
- **Git repo sync**: 27 current / 11 skipped daily; the only merge failure is `skills-rules-repo`.
- **06:25 Podcast Capture Watchdog RED** is its DESIGNED signal — never count it as a defect.
- **Weekly cadence**: CRAP (Mon), Security Scan (Fri), Citation SoV (Fri), Metadata audit (Thu),
  Weekly Evidence Summary (Fri), Saturday review, Sunday Adversarial + Portfolio Pulse — all fired.
- **Podcast episode counting**: use the run **footer** (`Done. New episodes: N`). The per-show line is
  capped by "Max 3 new episodes per show" and undercounts badly.
