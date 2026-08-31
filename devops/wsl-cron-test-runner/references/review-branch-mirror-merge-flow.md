# Review-Branch Mirror + Merge Flow (pluto_pr + dev) — Aug 2026

## Haris's instruction (23 Aug 2026, restated out-of-band)

> "Every night before running the check code check for the AMLHive:
> 1. Pull all the code back to the Pluto PR branch.
> 2. Merge it with our Pluto PR branch from the dev branch.
> 3. Run on that."
> "Your main job is to first fetch everything from the dev branch to your
> Pluto PR branch and then run that."

Meaning: **never run the nightly suite (or the weekly CRAP scan) on bare
`dev`.** Mirror `origin/pluto_pr`, merge `origin/dev` into it, then run on the
merged tree — the exact state the main agent reviews. If the merge conflicts,
surface it; do not run on a conflict-marked tree.

## The flow (baked into both runners)

```bash
git fetch origin
git checkout pluto_pr            # or: git checkout -B pluto_pr origin/pluto_pr
git reset --hard origin/pluto_pr # mirror the review branch exactly (no stash/pop)
git merge origin/dev --no-edit   # overlay latest dev
# ... run tests / scan on the merged tree ...
```

## Why this matters (what the merge protects)

Fixes that main agent has NOT yet merged to `dev` live only on `pluto_pr`
(e.g. the Postmark token-guard fixture and the frontend signOut race fix).
A runner that resets to bare `dev` wipes them from the working tree every
03:00 — the suite then fails daily until the branch is merged. Mirroring
`pluto_pr` first keeps those fixes in the test tree.

## Where implemented

| Runner | Cron | Script |
|--------|------|--------|
| AML Hive daily test suite | `044c0bc41e31` 03:00 daily | `~/.hermes/scripts/amlhive_daily_test_runner.py` |
| Weekly CRAP scan | `153af82d274e` Mon 10:30 | `~/.hermes/scripts/pluto_crap_score_runner.py` |

## CRAP runner specifics (weekly change-risk scan)

The CRAP runner also:
1. Merges `origin/dev` into `pluto_pr` BEFORE scanning (same flow as above).
2. PREFLIGHTS `backend/coverage.json` before trusting it:
   - **File-count check:** `python3 -c "import json; print(len(json.load(open('backend/coverage.json'))['files']))"` vs `find backend/app -name '*.py' | wc -l`. Mismatch = the JSON is missing whole files → the CRAP ranking is DISTORTED (105/344 files absent on 23 Aug 2026 hid the true #1 `matter_screening_detail`; `validate_ownership_extraction_v2` showed 16,256 instead of its real 130).
   - **Verified date from a command:** `git log -1 --format=%ai -- backend/coverage.json` (or `stat -c %y` if uncommitted). NEVER from memory — the first run reported 2026-07-23 when the real date was 2026-06-24.
   - Stale (>14d) or missing → score as 0% pessimistic; say so in the log; do NOT regenerate via pytest.
3. Appends a dated entry to `docs/pluto_weekly_crap_score_log.md`.
4. Commits + pushes THAT ONE FILE to `origin/pluto_pr` for main-agent review
   (Haris override of the old "only write, never commit/push" rule).

Canonical docs (updated 23 Aug 2026 to match this flow):
`docs/pluto_agent_instructions.md` § Weekly CRAP Score,
`docs/pluto_crap_score_instructions.md`, `docs/agent_rules/crap-score.md`.

## Pitfall observed live

The CRAP runner originally mirrored ONLY `origin/pluto_pr` (no dev merge) —
on 23 Aug 2026 that showed the stale `coverage.json` (239/344 files, dated
2026-06-24) and old docs, because the user's fixes were on `origin/dev`, not
yet merged into `pluto_pr`. The preflight caught it; the fix was adding
`git merge origin/dev --no-edit` to the runner. Lesson: **a runner that
mirrors only its own branch will see stale state whenever the user's latest
changes live on another branch — always merge the tracked dev branch in.**
