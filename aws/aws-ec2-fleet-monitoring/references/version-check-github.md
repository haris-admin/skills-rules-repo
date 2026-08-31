# Hourly Production Version Check — GitHub Dev Branch API

## Purpose
Detect silent-stale-build regressions (issue-151 class — a fresh EC2 boot can silently serve a many-releases-old build with no error).

## Architecture

```
GitHub raw API (PAT auth) ── success → live .version
    │ fail ──→ alert on auth failure
    ▼
Local clone (/mnt/c/Code/github/almhive-tech/amlhive1/.version)
    │ refreshed daily at 02:30 via git fetch+reset origin/dev
    ▼
Compare with API version
    │
    ├─ MATCH → exit 0 (ok)
    ├─ STALE_BUILD (API < repo) → alert email, exit 1
    └─ REPO_LAG (API > repo) → exit 0 (repo .version needs update)
```

## Key Details

| Detail | Value |
|--------|-------|
| **Script** | `~/.hermes/scripts/hourly_version_check.py` |
| **Schedule** | Hourly at `:00` (`0 * * * *`) |
| **GitHub URL** | `https://raw.githubusercontent.com/amlhive-tech/amlhive1/dev/.version` |
| **Branch** | `dev` (lowercase — NOT `Dev`) |
| **PAT env var** | `GITHUB_PAT_CLASSIC_AMLHIVE_AGENT` in Windows `.hermes/.env` |
| **Local clone path** | `/mnt/c/Code/github/almhive-tech/amlhive1/.version` |
| **Daily refresh** | `daily_repo_sync.py` at `30 2 * * *` — `git fetch origin && git reset --hard origin/dev` |

## Critical Rules (Per Pluto Operating Contract v1.2+)

1. **Prefer GitHub API first** — always try `raw.githubusercontent.com` with PAT before falling back
2. **Alert on auth failure** — if the PAT is expired, send an URGENT RED email. Do NOT silently fall back
3. **Local clone is fallback only** — the daily 02:30 sync bounds staleness to 1 day
4. **Case-sensitive branch name** — `dev` is lowercase. `Dev` returns 404
5. **No hardcoded tokens** — PAT read from `.env` at runtime

## Email Alerts

| Condition | Subject | Recipients |
|-----------|---------|------------|
| API endpoint unreachable | 🚨 URGENT — API Version Endpoint Unreachable | hhsiddiqui@gmail.com, shoaib@amlhive.com.au, tech@amlhive.com.au |
| Version mismatch (stale build) | 🚨 URGENT — Stale Build Detected — API Behind Repo | Same |
| GitHub PAT auth failure | 🚨 URGENT — GitHub PAT Auth Failure — Version Check Degraded | Same |

## PAT Renewal

When the PAT expires:
```bash
# The env var is in Windows file:
#   C:\Users\habib\.hermes\.env
#   GITHUB_PAT_CLASSIC_AMLHIVE_AGENT=ghp_<new_token>
# 
# The PAT needs classic token scope with access to:
#   - amlhive-tech/amlhive1 (read)
#   - raw.githubusercontent.com
```
