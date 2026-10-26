---
name: hourly-version-check
description: Use when diagnosing the hourly AML Hive version check.
---

# Hourly Production Version Check

Cron `4689311b6ad0` (hourly, `0 * * * *`, no_agent) → `~/.hermes/scripts/hourly_version_check.py`.

**Purpose:** Detect silent-stale-build regressions (issue-151 class). Fetches
`https://api.amlhive.com.au/version` and compares against the repo `.version`
file. Alerts ONLY when the API is behind the repo (a build that looks deployed
but isn't the latest).

**Exit codes:** 0 = pass (version current), 1 = stale build (sends alert via
`alert_email.send_alert`).

**State:** history appended to
`~/.hermes/research_outputs/.version_check/history.jsonl` — consumed by the
21:45 Daily Probe Summary cron (`eca044f22146`, `daily_probe_summary.py`).

## Pitfalls
- **A run of red hours is ONE stale build, not N failures — and the first stop is GitHub Actions, not the
  script.** `history.jsonl` pairs a PASS and a FAIL per hour; read only the FAIL rows and the
  `source: deploy-run <sha> (<ts>)` field — it names the commit whose `backend/pyproject.toml` the check
  treats as expected. Verify the live side directly (`curl -s https://api.amlhive.com.au/version`) before
  touching anything.
- **ECR tags are IMMUTABLE — a retried deploy on the SAME commit hard-fails at `Build + Push to ECR`.**
  Signature: `tag invalid: The image tag '<sha7>' already exists in the 'amlhive-backend' repository and
  cannot be overwritten because the tag is immutable.`, with `Backend Tests` + `Resolve deploy tag` green
  and `Deploy to EC2 via SSM` SKIPPED. The release lane's own workaround is an *empty tip bump* commit
  (message: `chore(release): empty tip bump for <ticket> … ECR immutable tag`), which is why an identical
  version can sit on two different SHAs. **The fix is a NEW tag (new commit) or mutable tags — never a
  re-run**, and never from a daily maintenance tick.
- **A green deploy is not proof the build is live: compare the run's post-deploy version gate against
  `GET /version`.** Seen 2026-10-25: run `40192848005` deployed `bc9bb52e5c0a` with every step green
  including `Post-deploy gate (version + readiness)`, yet production still served the previous build. When
  the gate passes and the endpoint disagrees, that is a FALSE PASS in the gate — report both halves
  (pipeline blocked AND gate untrustworthy) instead of just the version drift.
- Inspect run/job/step outcomes with the GitHub API (`/actions/runs?per_page=12`, then `jobs_url`), not
  `gh` — `gh` is unauthenticated on this host unless `GH_TOKEN` is exported. Job logs: the
  `/actions/jobs/<id>/logs` endpoint redirects to a block-storage URL that rejects the forwarded
  `Authorization` header, and the payload may be **plain text, not a zip** — download the redirect target
  without auth and read it as text.
- This cron and `hourly_attribution_probe.py` (`b705c3ee3882`) are the two
  half-hour-offset hourly probes (version at :00, attribution at :30). Keep
  them from colliding with the 5/11/17/23 fleet monitors.
- The alert fires on a genuine stale build, not on API-down (that's the fleet
  monitor's job). Don't mute it without checking the actual version drift.
