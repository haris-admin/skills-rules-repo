---
name: git-sync
description: Multi-org Git sync pipeline — parallel pulls across GitLab (hhsiddiqui + hhsiddiqui-group) and GitHub (haris-admin) to /mnt/c/Code/gitlab/. Use when debugging git sync failures, adding repos to sync, or understanding the sync pipeline.
---

# Git Repo Sync Pipeline

## When to Use
- Debugging why git_sync.py failed
- Adding new repos or orgs to the sync
- Understanding the sync architecture
- Diagnosing persistent fetch failures on specific repos

## Architecture

**Script:** `~/.hermes/scripts/git_sync.py`
**Cron:** `c23dc3f73e2d` — Daily 1:00 AM AEST (`0 1 * * *`), `no_agent: true`, `deliver: local`
**Target dir:** `/mnt/c/Code/gitlab/`
**Auth:** `GITLAB_PAT_OPENCLAW` + `GITHUB_PAT_CLASSIC_OPERATOR_AGENT` from Windows `.env`

## How It Works

### Sync Strategy
- **Shallow fetch:** `git fetch origin {branch} --depth 1 --no-tags` — minimizes bandwidth
- **Fast-forward merge only:** `git merge FETCH_HEAD --ff-only` — safe, no conflict resolution
- **Parallel workers:** 5 concurrent workers via `ThreadPoolExecutor`
- **Global timeout:** 90s — stops submitting new work after this, existing workers finish
- **Clone-only-once:** Full clone (`--depth 1 --single-branch`) only for new repos

### Repo Discovery
1. **GitLab user repos** (hhsiddiqui): `GET /api/v4/users/hhsiddiqui/projects?per_page=50`
2. **GitLab group repos** (hhsiddiqui-group): `GET /api/v4/groups/hhsiddiqui-group/projects?per_page=50`
3. **GitHub repos** (haris-admin): `GET /users/haris-admin/repos?per_page=50`
4. Deduplicate by repo name (user + group may overlap)

### Dead Repo Handling
```python
KNOWN_DEAD_REPOS = {'ideas-ndis', 'ideas-exitlens', 'ideas-gridpass', 'ideas-pitguard', 'ideas-verifylink'}
```
These repos are skipped entirely — no fetch attempt is made. They produce zero output.

### Exit Code Semantics
- **Exit 0:** All repos synced, OR only known-dead repos had fetch failures, OR only merge failures
- **Exit 1:** Unexpected fetch failures beyond known-dead repos

Merge failures (local branch divergence, dirty working trees) produce `⚠️` warnings but never cause exit 1.

## Cron Integration

**Schedule:** Daily 1:00 AM AEST (`0 1 * * *`)
**Type:** `no_agent: true` — runs as standalone Python script
**Timeout:** 300s (script completes in ~45-90s typically)
**Output:** stdout captured in cron output directory + embedded in `last_error` field (even on success)

## Verification Commands

```bash
# Run manually
python3 ~/.hermes/scripts/git_sync.py

# Check latest cron output
ls -lt ~/.hermes/cron/output/c23dc3f73e2d/ | head -3

# Check cron status
python3 -c "import json; data=json.load(open('/home/habib/.hermes/cron/jobs.json')); [print(json.dumps({k:j.get(k) for k in ['last_run_at','last_status','last_error']}, indent=2)) for j in data['jobs'] if j['id']=='c23dc3f73e2d']"
```

## Pitfalls

- **`/tmp` venvs disappear:** The script uses system Python, not `/tmp/` venvs — immune to WSL reboot cleanup
- **GitLab PAT expiry:** If `GITLAB_PAT_OPENCLAW` expires, GitLab repos silently fail. Check `~/.hermes/scripts/git_sync.py` output for `No GITLAB_PAT_OPENCLAW token`
- **KNOWN_DEAD_REPOS must be updated when repos are renamed/deleted:** If a repo starts failing every day, add it to `KNOWN_DEAD_REPOS` in `~/.hermes/scripts/git_sync.py`
- **Merge failures ≠ fetch failures:** A merge failure means the local branch has diverged — the data IS fresh, just can't fast-forward. Not a real error.
- **GitHub PAT auth differs from GitLab:** GitHub uses `https://{pat}@github.com/...` in clone URL. GitLab uses `oauth2:{pat}@` prefix.
