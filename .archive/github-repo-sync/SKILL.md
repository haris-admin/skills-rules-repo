---
name: github-repo-sync
description: Automated GitHub repo sync and testing across multiple orgs — PAT auth, WSL cross-mount workarounds, cron-based pull schedules, weekly test reports with Docker/pytest. Use when setting up automated git sync, test runners, or weekly report generation for GitHub repositories.
allowed-tools: [terminal, file, read_file, write_file, execute_code, cronjob]
---

# GitHub Repo Sync & Test Pipeline

## When to Use
- Setting up automated git pulls for multiple GitHub orgs
- Creating weekly test + report cron jobs for repos
- Working with GitHub repos on Windows filesystem from WSL
- Debugging git clone failures in Hermes sandbox
- Adding new GitHub tokens and repo directories

## Architecture

```
┌─────────────────────────────────────────┐
│  .hermes/.env (Windows)                  │
│  GITHUB_PAT_CLASSIC_<ORG>_AGENT=<token> │
│  CODE_REPO_LOCATION_<ORG>=<path>        │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│  /mnt/c/code/github/<org>/              │
│  ├── repo1/  (.git + code)              │
│  ├── repo2/  (.git + code)              │
│  └── ...                                │
└──────────────┬──────────────────────────┘
               │
      ┌────────┴────────┐
      ▼                 ▼
┌───────────┐   ┌──────────────┐
│ Git Sync   │   │ Weekly Report │
│ Thu+Mon   │   │ Wed 2AM       │
│ 2AM AEST  │   │ AEST          │
│ no_agent  │   │ no_agent      │
└───────────┘   └──────────────┘
                      │
                      ▼
               ┌──────────────┐
               │ Report at:    │
               │ weekly-reports│
               │ /YYYY-MM-DD.md│
               └──────────────┘
```

## Setup Pattern

### 1. Environment Variables

In `/mnt/c/Users/habib/.hermes/.env`:
```
GITHUB_PAT_CLASSIC_<ORG>_AGENT=ghp_...
CODE_REPO_LOCATION_<ORG>=C:\code\github\<directory>\
# WSL equivalent: /mnt/c/code/github/<directory>
```

### 2. Repo Discovery

```python
# Use GitHub API to list repos accessible by token
curl -s -H "Authorization: Bearer $TOKEN" \
  -H "Accept: application/vnd.github+json" \
  "https://api.github.com/user/repos?per_page=100&type=all&sort=updated"
```

### 3. Repo Cloning

**Preferred:** Clone manually from Windows terminal (Hermes sandbox cannot spawn `git-remote-https` for WSL cross-mount):
```powershell
cd C:\code\github\<org>
git clone https://github.com/<org>/<repo>.git
```

**Fallback:** GitHub archive API (downloads code without git history):
```bash
curl -sL -H "Authorization: Bearer $TOKEN" \
  "https://api.github.com/repos/<org>/<repo>/zipball/main" \
  -o /tmp/repo.zip
unzip -q /tmp/repo.zip -d /mnt/c/code/github/<org>/<repo>/
```

### 4. Git Pull (for already-cloned repos)

Use `-c credential.helper=` to bypass sandbox child-process restrictions:
```bash
git -c credential.helper= -C /mnt/c/code/github/<org>/<repo> fetch origin
git -c credential.helper= -C /mnt/c/code/github/<org>/<repo> merge origin/main
```

## Scripts

### `unified_git_sync.py`
Pulls all repos across all configured orgs. Used by cron jobs.
```bash
python3 -u ~/.hermes/scripts/unified_git_sync.py [--dry-run]
```
- Reads tokens and repo paths from `.env`
- Pulls each repo with credential helper bypass
- Reports: changed, up to date, failed
- Handles archive-only repos (no `.git`) gracefully

### `unified_weekly_report.py`
Full test suite + report generation. Used by Wednesday cron.
```bash
python3 -u ~/.hermes/scripts/unified_weekly_report.py [--dry-run]
```
- Phase 1: Git sync all repos
- Phase 2: Run tests:
  - `portal_backend_lambda_eventbridge`: Docker PostgreSQL + pytest + Alembic
  - `amlhive1`: Backend pytest, frontend Next.js check
- Phase 3: Generate report at `~/research_outputs/weekly-reports/weekly-report-YYYY-MM-DD.md`

### Report Format
```markdown
# Weekly GitHub Report — YYYY-MM-DD
## Git Sync Summary — X changed, Y current, Z issues
## Test Results — portal_backend_lambda_eventbridge
## Test Results — amlhive1
## Issues & Recommendations
## Vercel Deployment Status
```

## Cron Jobs

| Job ID | Name | Schedule | Script |
|--------|------|----------|--------|
| `6c1e5ffb89d9` | Git Sync (Thu 2AM) | `0 2 * * 4` | `unified_git_sync.py` |
| `e12213405122` | Git Sync (Mon 2AM) | `0 2 * * 1` | `unified_git_sync.py` |
| `e6b671746eaf` | Weekly Report (Wed 2AM) | `0 2 * * 3` | `unified_weekly_report.py` |

All use `no_agent: true` and `deliver: local`.

## Current Orgs

### a2square
- **Token:** `GITHUB_PAT_CLASSIC_A2SQUARE_AGENT`
- **Path:** `C:\code\github\a2_square` (`/mnt/c/code/github/a2_square`)
- **5 repos:** `portal_backend_lambda_eventbridge` (Docker+pytest), `tapease_a2square_dev_infra`, `tapease_a2square_prod_infra`, `tapease_frontend_nextjs_prod`, `tapease_portal_fastapi_a2square` (Poetry, 100+ tests)

### amlhive
- **Token:** `GITHUB_PAT_CLASSIC_AMLHIVE_AGENT`
- **Path:** `C:\code\github\almhive-tech` (`/mnt/c/code/github/almhive-tech`)
- **5 repos:** `amlhive1` (Next.js+Vercel+FastAPI), `ideas-verifylink`, `ideas-agentgate`, `ideas-cloudwise`, `zerolang`
- **Vercel:** `amlhive1` frontend deployed at `amlhive.com.au`, monitored by `745ec76c6bf9`
- **4 repos missing `.git`** — downloaded via archive API, need Windows-side clone for full sync

### operator (haris-admin)
- **Token:** `GITHUB_PAT_CLASSIC_OPERATOR_AGENT`
- **Path:** `C:\code\github\haris-admin` (`/mnt/c/code/github/haris-admin`)
- **13 repos:** 12 syncing via GitHub (haris-admin user), 1 (`guardrail-scan`) points to GitLab — excluded from GitHub sync
- **Already cloned:** all repos have `.git` and correct remotes, no archive downloads needed

## Pitfalls

### WSL Cross-Mount Git Operations
- `git clone` over HTTPS to `/mnt/c/` paths fails with `waitpid: No child processes` — the Hermes sandbox cannot spawn `git-remote-https` for cross-mount operations
- `git fetch/pull` with `-c credential.helper=` works for already-cloned repos (fetches are quicker and don't spawn the same processes), but timeout at 120s for large repos
- Archive downloads via GitHub API work as a fallback but lack `.git` history
- Cloning from Windows terminal (PowerShell/CMD) always works — do initial setup there
- **Jun 2026:** `openclaw` repo fetch timed out at 30s; script timeout now bumped to 120s for all git operations

### Remote URL Management
- Always set auth URL before operations: `git remote set-url origin "https://oauth2:$TOKEN@github.com/org/repo.git"`
- Some repos have stale or duplicate remotes — verify with `git remote -v` and clean up before syncing
- `tapease_portal_fastapi_a2square` had two remotes pointing to different orgs (haris-a2squre vs A2-Square-aus) — use the org-level one
- **URL doubling bug (Jun 2026):** The `replace('https://', 'https://oauth2:TOKEN@')` pattern accumulates tokens across runs. Fix: strip stale tokens first with regex `re.sub(r'(?:oauth2:[^@]+@|https://[^@]+@)', 'https://', remote)` before adding fresh auth. Some repos use `username:TOKEN@` format instead of `oauth2:TOKEN@` — the regex handles both.
- **Stale ref lock (Jun 2026):** After broken fetches, `refs/remotes/origin/main` can get locked at wrong commit. Fix: `rm .git/refs/remotes/origin/main` then re-fetch.
- **Local changes blocking merge:** Repos with active local work (e.g. `openclaw` = Gumby's own codebase with session data) can't be auto-merged without stomping local state. These need manual intervention — stash/pop or force-reset per repo.

### Token Scope
- Tokens need `repo` scope for private repos
- Test token access with: `curl -sH "Authorization: Bearer $TOKEN" https://api.github.com/user/repos`
- Different orgs need different tokens — each PAT appears in the org's contributor list

## Adding a New Org

1. Create PAT on GitHub with `repo` scope
2. Add to `.env`: `GITHUB_PAT_CLASSIC_<ORG>_AGENT=<token>`
3. Add repo location: `CODE_REPO_LOCATION_<ORG>=C:\code\github\<dir>\`
4. Discover repos via API
5. Clone repos from Windows terminal
6. Add org to `unified_git_sync.py` REPOS list
7. Add org's test runner to `unified_weekly_report.py`
8. Existing crons pick up new orgs automatically (they iterate the REPOS list)
