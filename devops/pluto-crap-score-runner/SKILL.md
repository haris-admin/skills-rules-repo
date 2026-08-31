---
name: pluto-crap-score-runner
description: Use when running the AMLHive weekly CRAP score scan.
---

# Pluto CRAP Score Runner (Change-Risk Advisory)

## When to Use
- Running the weekly CRAP score cron (`153af82d274e`, Monday 10:30 AM AEST)
- Debugging why the CRAP scan produced a misleading ranking
- Understanding the `pluto_crap_score_runner.py` script flow

## What It Does
`pluto_crap_score_runner.py` runs `scripts/crap_score.py --root backend/app --top 25` as an
**advisory** scan (no `--fail-above`, no pytest coverage regeneration), then appends a dated
section to `docs/pluto_weekly_crap_score_log.md` and commits+pushed to `origin/pluto_pr`.

## Flow
1. **Mirror origin/pluto_pr + merge origin/dev** — `git fetch` → `checkout pluto_pr` → `reset --hard origin/pluto_pr` → `merge origin/dev --no-edit`. Runs on the merged state (user instruction Aug 23: pull ALL code onto pluto_pr, merge dev, run on merged).
2. **PREFLIGHT coverage.json** (mandatory since 23 Aug 2026 incident — 105 of 344 files were absent from the JSON, distorting the ranking):
   - (a) file-count check: `coverage.json['files']` count vs `find backend/app -name '*.py' | wc -l`
   - (b) verified date via `git log -1 --format=%ai -- backend/coverage.json` (NEVER memory/estimation)
   - `age_days > 14` → stale → treat coverage as 0% (pessimistic upper bound)
3. Run `python3 scripts/crap_score.py --root backend/app --top 25` (timeout 600s).
4. Append `## {TODAY}` section to `docs/pluto_weekly_crap_score_log.md` (skip if already logged today).
5. Commit + push to `origin/pluto_pr`. **Do NOT push to `dev` directly** — main agent reviews/merges.

## Preflight Verdict Logic
| Condition | Verdict |
|-----------|---------|
| `json_files != py_count` | INCOMPLETE — do NOT trust ranking, treat as unreliable |
| `age_days > 14` | STALE — score coverage as 0% (pessimistic upper bound) |
| else | VERIFIED — real coverage used |

## Pitfalls
- **coverage.json file-count mismatch ≠ missing file.** The Aug 23 incident was 105/344 files
  absent from the JSON (stale/incomplete coverage), not a missing `coverage.json`. The preflight
  exists to catch this. Never trust the ranking without the preflight verdict.
- **Branch is `pluto_pr`, never `dev`.** The scan is advisory and read-only wrt app code; the
  only write is the log file. Push the log to `pluto_pr` so the main agent merges.
- **Repo lives at `~/code/amlhive1` (WSL ext4), NOT `/mnt/c/`.** The cron sets Workdir to
  `/home/habib/code/amlhive1`. Running CRAP on the NTFS mount is 3-4x slower.
- **`coverage_date` must come from `git log`, not mtime** — `git reset --hard` touches mtimes
  every run, so `stat` mtime is always "today" even for a stale committed coverage file.
- **Read-only wrt application code** — never edits `backend/app`, never deploys. If a fix is
  needed, it goes to the main agent, not this runner.
