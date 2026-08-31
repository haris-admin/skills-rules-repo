---
name: github-repo-pipeline
description: Multi-org GitHub repo sync, test, and reporting pipeline. PAT-based auth, unified git sync, Docker-based test execution, weekly reporting. Use when setting up GitHub repo management for new orgs, debugging cross-mount git failures, or adding repos to the sync pipeline.
allowed-tools: [terminal, file, read_file, write_file, execute_code]
---

# GitHub Repo Pipeline — Multi-Org Sync + Test

## When to Use
- Setting up GitHub sync for a new org/account
- Adding repos to the existing sync pipeline
- Debugging git clone/pull failures in WSL/Hermes sandbox
- Running weekly test reports
- Generating consolidated repo health reports

## Architecture

```
┌─────────────────────────────────────────────┐
│  GitHub Orgs (a2square, amlhive, operator)  │
│  ~18 repos across 3 orgs                     │
└──────────────┬──────────────────────────────┘
               │ PAT tokens in .env
               ▼
┌──────────────────────────────────────────────┐
│  git + GitHub API                             │
│  ├── unified_git_sync.py (Thu+Mon 2AM)        │
│  ├── unified_weekly_report.py (Wed 2AM)       │
│  └── a2square_test_runner.py (legacy)         │
└──────────────┬───────────────────────────────┘
               │
               ▼
┌──────────────────────────────────────────────┐
│  Docker + pytest                              │
│  ├── portal_backend_lambda_eventbridge       │
│  │   PostgreSQL 17, pytest, alembic           │
│  ├── amlhive1 (backend tests)                 │
│  └── future: additional repos                 │
└──────────────┬───────────────────────────────┘
               │
               ▼
┌──────────────────────────────────────────────┐
│  Weekly Report                                │
│  ~/research_outputs/weekly-reports/           │
│  Git status + test results + Vercel health    │
└──────────────────────────────────────────────┘
```

## Env Var Pattern

Each org needs two env vars in `/mnt/c/Users/habib/.hermes/.env`:

```
GITHUB_PAT_CLASSIC_{ORG}_AGENT=ghp_...
CODE_REPO_LOCATION_{ORG}=C:\code\github\{dir}\
```

Existing orgs (June 8, 2026):
- `GITHUB_PAT_CLASSIC_A2SQUARE_AGENT` + `CODE_REPO_LOCATION_A2SQUARE` → `C:\code\github\a2_square`
- `GITHUB_PAT_CLASSIC_AMLHIVE_AGENT` + `CODE_REPO_LOCATION_AMLHIVE` → `C:\code\github\almhive-tech`
- `GITHUB_PAT_CLASSIC_OPERATOR_AGENT` + `CODE_REPO_LOCATION_OPERATOR` → `C:\code\github\haris-admin`

## Adding a New Org

1. Add PAT token and location to `.env`
2. Discover repos via GitHub API:
   ```bash
   curl -s -H "Authorization: Bearer $TOKEN" \
     "https://api.github.com/user/repos?per_page=50&type=all&sort=updated"
   ```
3. Clone repos to target directory
4. Add repos to `unified_git_sync.py` REPOS list: `("repo-name", "/mnt/c/code/github/dir", "token_key")`
5. Add repos to `unified_weekly_report.py` git_sync() function
6. If repos have tests (Docker/pytest/package.json), add test section
7. Update this skill's org list

## Scripts

> **Coverage note (Aug 2026):** the skill-extractor (`skill_extractor.py`) periodically proposes
> `a2square-git-sync`, `unified-weekly-report`, and `a2square-test-runner` as "no matching skill"
> because it matches exact script-filename → skill-name, not content coverage. These ARE covered
> here (and in `git-sync` / `wsl-cron-test-runner`). Do NOT create duplicate skills for them.

### unified_git_sync.py
Pulls all repos across all configured orgs. Used Thu+Mon 2AM AEST.

```bash
python3 ~/.hermes/scripts/unified_git_sync.py [--dry-run]
```

Repo format: `("name", "base_dir", "token_key")` where token_key maps to `TOKENS` dict.

### unified_weekly_report.py
Full pipeline: git sync → Docker PostgreSQL → pytest → coverage → report.
Used Wed 2AM AEST.

```bash
python3 ~/.hermes/scripts/unified_weekly_report.py [--dry-run]
```

Test sections:
- `test_a2square_portal()` — Docker PostgreSQL 17, alembic migrations, pytest
- `test_amlhive()` — Backend pytest + frontend package.json detection

### a2square_test_runner.py
Legacy single-org runner for a2square. Being replaced by unified script.

## Cron Jobs

| Job ID | Name | Schedule | Script |
|--------|------|----------|--------|
| `c23dc3f73e2d` | Git Repo Sync (Daily 1AM) | Daily 1AM AEST | git_sync.py |
| `0dbba3db3116` | Daily Repo Sync — Pull Latest Dev Branch | Daily 2:30AM AEST | daily_repo_sync.py |
| `e6b671746eaf` | Weekly Test Report — A2Square + AML Hive | Wed 2AM AEST | unified_weekly_report.py |

All use `no_agent: true` + `deliver: local`. Reports saved to `~/research_outputs/weekly-reports/`.

Note: `unified_git_sync.py` (`c23dc3f73e2d`) replaced the old Thu+Mon sync crons (`6c1e5ffb89d9`, `e12213405122`) on 2026-06-05 with a consolidated daily schedule.

## Token Auth Pattern

### ⚠️ Classic PATs REJECT `Authorization: Bearer` header auth (tested Aug 2026)

**Classic GitHub PATs (`ghp_...`) return `remote: invalid credentials` when used with `-c http.extraheader=Authorization: Bearer <PAT>`** — the Bearer header only works for OAuth/fine-grained tokens. The A2Square runner was switched to Bearer headers and every pull failed until reverted to basic auth.

**Working patterns (in order of preference):**

1. **Pass the auth URL as an ARGUMENT (never persist to remote config)** — safest, remote stays clean:
```python
auth_url = repo_url.replace("https://github.com/", f"https://x-access-token:{PAT}@github.com/")
# clone / pull — auth_url as argument, NOT git remote set-url:
subprocess.run(["git", "pull", "--ff-only", auth_url], cwd=str(path), ...)
```
2. **`-c credential.helper=` with the token in a temp URL** for environments that can't spawn helpers.

**NEVER `git remote set-url origin` with a tokenized URL** — the token lands in `.git/config` and every later re-tokenized run stacks `oauth2:ghp_...@oauth2:ghp_...@` prefixes. One repo had the PAT embedded **16×**. Sanitize corrupted remotes:
```bash
git remote set-url origin "$(git remote get-url origin | sed -E 's|https://[^@]+@github.com/|https://github.com/|; s|oauth2:[^@]+@||g')"
# fix doubled https://https:// if sed leaves it
git remote set-url origin "https://github.com/<org>/<repo>.git"
```

### Git operations (legacy pattern — see warning above)
```python
auth_remote = remote.replace('https://', f'https://oauth2:{token}@')
run(f'git -C "{rp}" remote set-url origin "{auth_remote}"')
run(f'git -c credential.helper= -C "{rp}" fetch origin {branch}')
```

### API operations
Use Bearer token header:
```bash
curl -s -H "Authorization: Bearer $TOKEN" \
  "https://api.github.com/repos/$ORG/$REPO/zipball/main"
```

## WSL Sandbox Workaround for git clone

**Problem:** `git clone` over HTTPS to WSL cross-mount paths (`/mnt/c/...`) fails in Hermes sandbox with `error: waitpid for git-remote-https failed: No child processes`. The sandbox cannot spawn credential helper or remote-https child processes.

**git pull still works** with `-c credential.helper=` but the initial clone must be done differently.

**Workaround — GitHub archive API:**
```python
# Download zipball
url = f"https://api.github.com/repos/{org}/{repo}/zipball/main"
r = terminal(f'curl -sL -H "Authorization: Bearer {token}" -o "{zip_path}" "{url}"')
# Extract
r = terminal(f"unzip -q -o {zip_path} -d {repo_path}")
```

**Limitation:** Archive downloads have NO `.git` directory — they're code snapshots. The `unified_git_sync.py` correctly detects and skips them. For proper git tracking, clone from Windows terminal directly:
```
cd C:\code\github\{org-dir}
git clone https://github.com/{org}/{repo}.git
```

## Weekly Report Format

Reports saved to `~/research_outputs/weekly-reports/weekly-report-YYYY-MM-DD.md`:

```markdown
# 📊 Weekly GitHub Report — YYYY-MM-DD

## 📥 Git Sync Summary
**N changed** | **N current** | **N issues**
- ✅ repo-name: up to date

## 🧪 Test Results — portal_backend_lambda_eventbridge
**Migrations:** ✅ Passed
**Tests:** ✅ All N passed

## 🧪 Test Results — amlhive1
**Backend:** ✅ All N passed
**Frontend:** 📦 Next.js deployed on Vercel

## 🔍 Issues & Recommendations
✅ No issues detected. (or list issues)

## 🚀 Vercel Deployment Status
- amlhive-frontend: monitoring active
```

## Pitfalls

### Auth & Credential Management
- **Auth URL placeholder bug:** The `auth_remote` URL must use the actual token, not a literal `***` placeholder. Fixed June 8, 2026.
- **URL doubling bug:** The `replace('https://', 'https://oauth2:TOKEN@')` pattern accumulates tokens across runs. Fix: strip stale tokens first with regex `re.sub(r'(?:oauth2:[^@]+@|https://[^@]+@)', 'https://', remote)` before adding fresh auth. Some repos use `username:TOKEN@` format instead of `oauth2:TOKEN@` — the regex handles both.
- **Git credential store corruption:** The Windows `.git-credentials` file (at `~/.git-credentials` on WSL) can accumulate overlapping entries that cause the remote URL to double up (e.g. `https://oauth2:TOKEN@oauth2:TOKEN@github.com/...`). This produces `fatal: URL rejected: Port number was not a decimal number between 0 and 65535` on fetch. Fix: inspect `cat ~/.git-credentials | grep github` and remove duplicate entries, then run `git remote set-url origin https://github.com/{org}/{repo}.git` to reset to a clean URL. The credential helper re-adds the token on the next authenticated operation.
- **Token scope:** Tokens need `repo` scope for private repos. Test with `curl -sH "Authorization: Bearer $TOKEN" https://api.github.com/user/repos`
- **Different orgs need different tokens** — each PAT appears in the org's contributor list

### Git Operations
- **`git remote` may have wrong name:** Some repos have remotes with non-standard names (not `origin`). Always check with `git -C "{rp}" remote -v` and fix with `git remote remove/add` if needed.
- **Stale ref lock:** After broken fetches, `refs/remotes/origin/main` can get locked at wrong commit. Fix: `rm .git/refs/remotes/origin/main` then re-fetch.
- **Local changes blocking merge:** Repos with active local work (e.g. `openclaw` = user's own codebase with session data) can't be auto-merged without stomping local state. These need manual intervention — stash/pop or force-reset per repo.
- **`openclaw` repo fetch timed out at 30s** — script timeout now bumped to 120s for all git operations
- **`tapease_portal_fastapi_a2square` had two remotes** pointing to different orgs (haris-a2squre vs A2-Square-aus) — use the org-level one.

### WSL Sandbox
- **`git clone` fails in WSL cross-mount:** `git clone` over HTTPS to `/mnt/c/` paths fails with `waitpid: No child processes` — Hermes sandbox cannot spawn `git-remote-https` for cross-mount. Use GitHub archive API as fallback (code snapshot, no `.git` history).
- **`git fetch/pull` with `-c credential.helper=` works** for already-cloned repos, but timeout at 120s for large repos.
- **Cloning from Windows terminal (PowerShell/CMD) always works** — do initial setup there.
- **Cross-mount `find` timeouts:** Avoid recursive `find` on `/mnt/c/` mounts. Use targeted checks per repo instead of broad searches.
- **archive-only repos are detected correctly:** The sync script checks for `.git` directory and reports `no_git` status for archive downloads. They appear as `⚠️` in the report.

### Docker & Testing
- **Docker PostgreSQL port collision:** Use port 5433 for test PostgreSQL (docker-compose.test.yml) to avoid conflicts with local PostgreSQL on 5432 and portfolio projects on 5436+.
- **`/tmp` venvs evaporate on reboot:** Test venvs (`/tmp/a2square_test_venv`, `/tmp/amlhive_test_venv`) are auto-created if missing.
