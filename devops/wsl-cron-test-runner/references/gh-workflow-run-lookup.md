# GitHub Actions Workflow Run Lookup — gh CLI vs REST API (Aug 2026)

## The trap
`GET /repos/{owner}/{repo}/actions/runs?workflow_id=<id>` does NOT reliably
filter by workflow. Verified 7 Aug 2026: querying with the backend-deploy
workflow's ID (`308033175`, display name "Deploy Backend to EC2 (AWS)")
returned runs from OTHER workflows — including the "Scheduled — Deep Audit
(Full Test Suite)" run. Its commit's `backend/pyproject.toml` version (0.5.82)
was ahead of the actual last backend deploy (0.5.80), producing a **false
STALE_BUILD alert** in `hourly_version_check.py`.

Why it matters: a stale-build monitor that false-alarms is worse than none —
the whole point of the corrected check (contract 7 Aug 2026) was to STOP
comparing live `/version` against the repo `.version` file (bumped on
frontend-only releases too). Substituting one wrong source (REST API runs
filter) for another (`.version` file) just moves the false-positive class.

## The fix: use `gh` CLI with the display name
```bash
gh run list --repo amlhive-tech/amlhive1 \
  --workflow="Deploy Backend to EC2 (AWS)" \
  --status success --limit 1 --json headSha,updatedAt,displayTitle
```
`gh` resolves the workflow by display name reliably. The output JSON has
`headSha` / `updatedAt` keys (not `head_sha` / `updated_at`).

From Python (hourly cron script):
```python
env = dict(os.environ)
env["GH_TOKEN"] = github_token or ""   # PAT from .env, never printed
r = subprocess.run(["gh", "run", "list", "--repo", "amlhive-tech/amlhive1",
                    "--workflow=Deploy Backend to EC2 (AWS)",
                    "--status", "success", "--limit", "1",
                    "--json", "headSha,updatedAt,displayTitle"],
                   capture_output=True, text=True, timeout=30, env=env)
runs = json.loads(r.stdout)
head_sha = runs[0]["headSha"]
```

## Then: read the version at THAT commit, not current HEAD
```python
# GitHub Contents API at the deploy commit's ref:
#   /repos/{owner}/{repo}/contents/backend/pyproject.toml?ref={head_sha}
# base64-decode `content`, regex `^version\s*=\s*["']([^"']+)["']` (MULTILINE)
```

## General rule
- Workflow DISPLAY NAMES with parentheses/spaces: REST `workflow`/`workflow_id`
  query params are unreliable → use `gh run list --workflow="<name>"`.
- Compare deployed-version monitors against the commit that ACTUALLY deployed
  the component (last successful deploy-workflow run), never against a
  repo-wide version marker that frontend-only releases also bump.
- On GitHub API/PAT failure: alert on the auth failure itself; do NOT fall
  back to a local `.version` clone (reintroduces the false-positive class).

## Related
- `hourly_version_check.py` (fixed 7 Aug 2026) — now uses the gh-CLI pattern above.
- Operating contract (`pluto-amlhive-operating-contract`, user-owned) documents
  the corrected version-check rules; this file captures the implementation pitfall.
