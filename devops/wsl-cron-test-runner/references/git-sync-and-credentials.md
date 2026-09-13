# Git Stash/Pull Patterns and PAT Credential Safety

Covers the stash-pull-pop pattern for a working copy that legitimately carries local edits (as opposed to a pure test mirror — see [mirror-sync-and-false-green-guards.md](mirror-sync-and-false-green-guards.md) for that case), the failure modes that pattern can still hit, and the correct (non-corrupting) way to authenticate git operations with a PAT.

## Contents

- [Git Stash + Pull Pattern](#git-stash--pull-pattern)
- [Stash-Pull-Pop Fails on a Pre-Existing Conflict](#stash-pull-pop-fails-on-a-pre-existing-conflict)
- [Stale .git/index.lock on the NTFS Copy](#stale-gitindexlock-on-the-ntfs-copy)
- [\"Provider Timeout\" Alert ≠ Provider Failure](#provider-timeout-alert--provider-failure)
- [Git Clone/Pull with PAT — Never Embed the Token in the URL](#git-clonepull-with-pat--never-embed-the-token-in-the-url)

## Git Stash + Pull Pattern

**⚠️ Do NOT use a blind `git stash` without popping it back** — that silently discards legitimate local edits (e.g. the Postmark test fixes of Aug 2026 would have been lost). The cron-safe pattern is: check dirty → stash with message → pull → **pop back**:

```python
import subprocess

def update_repo(repo_path):
    """Stash local changes, pull latest, restore. Handles CI leftovers without data loss."""
    dirty = subprocess.run(["git", "status", "--porcelain"], cwd=str(repo_path),
        capture_output=True, text=True, timeout=10).stdout.strip()
    stashed = False
    if dirty:
        subprocess.run(["git", "stash", "push", "-m", "auto-stash before pull (test runner)"],
            cwd=str(repo_path), capture_output=True, text=True, timeout=15)
        stashed = True
    r = subprocess.run(["git", "pull", "--ff-only", "origin", "dev"], cwd=str(repo_path),
        capture_output=True, text=True, timeout=90)  # 90s since Aug 2026 (NTFS + large repos)
    if stashed:
        pop = subprocess.run(["git", "stash", "pop"], cwd=str(repo_path),
            capture_output=True, text=True, timeout=15)
        if pop.returncode != 0:
            # Conflict on pop — changes are preserved in stash list, NOT lost
            print(f"⚠️  Stash pop failed (kept in stash): {(pop.stderr or pop.stdout)[:150]}")
    return r.returncode == 0
```

Key points:
- Only stash when `git status --porcelain` is non-empty (fast, cheap check).
- Always `--ff-only` — a diverged branch should fail loudly, not merge.
- On pop conflict the changes stay in `git stash list`; never `git stash clear` in a runner.
- The 03:00 AM cron failure on 2026-08-02 (`cannot pull with rebase: You have unstaged changes`) was exactly this — the runner's plain pull refused because of the two Postmark test-file edits. The stash-pull-pop pattern above fixes it permanently.

## Stash-Pull-Pop Fails on a Pre-Existing Conflict

If a previous job (e.g. the 02:30 `daily_repo_sync.py` reset) or an earlier interrupted pull left a tracked file in **UU (unmerged) state**, the stash-pull-pop chain collapses:

```
⚠️ Pull failed: error: Pulling is not possible because you have unmerged files.
⚠️ Stash pop failed (kept in stash): docs/pluto_agent_instructions.md: needs merge
```

The stash **does** protect the edits (they survive in `git stash list`), but the runner exits 1 and the suite never runs. Diagnosis + fix:

```bash
# 1) Identify the conflicted file(s) — status shows UU:
git status --short                      # → "UU docs/pluto_agent_instructions.md"
git ls-files -u docs/<file>             # shows 3 stages (base/ours/theirs)

# 2) Decide which side is canonical. For the Pluto contract, the LOCAL
#    (stashed) version is the source of truth — resolve keeping it:
git checkout --theirs docs/<file>       # 'theirs' = the stashed side here
git add docs/<file>                     # marks resolved; conflict markers gone
grep -c '^<<<<<<<' docs/<file>          # → 0

# 3) Drop the now-duplicate stash entry (files are back in the worktree):
git stash drop stash@{0}

# 4) Verify the pull path works again (simulate the runner: stash → pull --ff-only → pop).
```

Never resolve the contract file "blind" — check both stages first (`git show :2:<file>` vs `git show :3:<file>`) and keep whichever side is the canonical source of truth (memory: `docs/pluto_agent_instructions.md` = sole source of truth, skill = synced mirror). This overall review-branch/mirror/merge workflow is also documented end to end in [review-branch-mirror-merge-flow.md](review-branch-mirror-merge-flow.md).

## Stale .git/index.lock on the NTFS Copy

A failed 02:30 reset left a **zero-byte `.git/index.lock`** that made every later git command on the Windows copy fail (`Unable to create ... index.lock: File exists`). No git process was running — it was a leftover. Fix:

```bash
ps aux | grep -i "[g]it fetch\|[g]it reset"   # confirm no live git
rm -f /mnt/c/<repo>/.git/index.lock
```

Also: `daily_repo_sync.py` hits the Windows/NTFS copy and needs **>60s timeouts** (memory: `--timeout=60000`; 30s → `GIT_TIMEOUT` for 4+ days). Bump fetch + reset to 90s.

## "Provider Timeout" Alert ≠ Provider Failure

When a `no_agent` script job fails, the Telegram alert may say `provider timeout. Fallback chain was exhausted` even when the real cause is a script exit-1 (git conflict, test failure). The provider-timeout text usually comes from the **diagnosis** step (OpenRouter call hitting its 30s/120s kill), not the job itself. **Always read `~/.hermes/cron/output/<job_id>/<latest>.md` before diagnosing** — it shows the real `Status: script failed` + stdout. The 2026-08-09 AMLHive suite alert was exactly this: alert said provider timeout, actual failure was a UU conflict plus 1 flaky NFR color-contrast E2E test.

## Git Clone/Pull with PAT — Never Embed the Token in the URL

**🔴 Critical (Aug 2026): the old `x-access-token:{PAT}@` URL pattern corrupts remotes** if it's ever written into `.git/config` (as opposed to passed as a one-off command argument, see below).

Embedding the PAT in the clone URL and then calling `git remote set-url` writes it into the repo's `.git/config` remote URL. Every later `git pull` that re-tokenizes (or a clone command run against an existing repo) stacks ANOTHER `oauth2:ghp_...@` prefix. A2Square remotes were found with the PAT embedded **3× and even 16×** (`tapease_a2square_dev_infra`), producing `fatal: unable to access 'https://oauth2:ghp_...@oauth2:ghp_...@...github.com/...'` and `remote: invalid credentials` / `Repository not found` on pull.

**Correct pattern — ephemeral auth, never touches the remote URL:**

```python
# clone (new repo) — pass auth URL as ARGUMENT, never git remote set-url
auth_url = repo_info["url"].replace("https://github.com/",
                                    f"https://x-access-token:{PAT}@github.com/")
r = subprocess.run(["git", "clone", auth_url, str(path)], ...)
# pull (existing repo) — pass auth URL as ARGUMENT
r = subprocess.run(["git", "pull", "--ff-only", auth_url], cwd=str(path), ...)
```

**⚠️ CRITICAL (tested Aug 2026): classic GitHub PATs REJECT `Authorization: Bearer` header auth** — returns `remote: invalid credentials`. They MUST use the `x-access-token:<PAT>@` basic-auth form. The `http.extraheader=Authorization: Bearer` pattern FAILS for classic PATs (it only works for OAuth/fine-grained tokens). The runner was switched to `http.extraheader` and every pull failed until reverted to `x-access-token` basic auth.

Passing the auth URL as a `git pull <url>`/`git clone <url>` ARGUMENT keeps `remote.origin.url` clean — the PAT never lands in `.git/config`. The `--ff-only` flag avoids the "divergent branches" interactive prompt; on divergence the runner notes it and runs tests on local code.

**Sanitize an already-corrupted remote:**
```bash
cd /path/to/repo
git remote set-url origin "$(git remote get-url origin | sed -E 's|https://[^@]+@github.com/|https://github.com/|; s|oauth2:[^@]+@||g')"
# fix doubled https://https:// if the sed left it
git remote set-url origin "https://github.com/<org>/<repo>.git"
```
Audit all repos of a multi-repo runner at once: `git remote get-url origin | grep -c 'oauth2:'` → >0 means corruption.

PAT read from `.env` (values never printed):
```python
ENV_PATH = Path("/mnt/c/Users/habib/.hermes/.env")
PAT = None
if ENV_PATH.exists():
    for line in ENV_PATH.read_text().splitlines():
        if "GITHUB_PAT_CLASSIC_AMLHIVE_AGENT" in line and "=" in line:
            PAT = line.split("=", 1)[1].strip()
```
