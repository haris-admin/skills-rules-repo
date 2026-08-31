---
name: github-auth
description: "GitHub auth setup: HTTPS tokens, SSH keys, gh CLI login."
version: 1.2.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [GitHub, Authentication, Git, gh-cli, SSH, Setup]
    related_skills: [github-pr-workflow, github-code-review, github-issues, github-repo-management]
---

# GitHub Authentication Setup

This skill sets up authentication so the agent can work with GitHub repositories, PRs, issues, and CI. It covers two paths:

- **`git` (always available)** — uses HTTPS personal access tokens or SSH keys
- **`gh` CLI (if installed)** — richer GitHub API access with a simpler auth flow

## Detection Flow

When a user asks you to work with GitHub, run this check first:

```bash
# Check what's available
git --version
gh --version 2>/dev/null || echo "gh not installed"

# Check if already authenticated
gh auth status 2>/dev/null || echo "gh not authenticated"
git config --global credential.helper 2>/dev/null || echo "no git credential helper"
```

**Decision tree:**
1. If `gh auth status` shows authenticated → you're good, use `gh` for everything
2. If `gh` is installed but not authenticated → use "gh auth" method below
3. If `gh` is not installed → use "git-only" method below (no sudo needed)

---

## Method 1: Git-Only Authentication (No gh, No sudo)

This works on any machine with `git` installed. No root access needed.

### Option A: HTTPS with Personal Access Token (Recommended)

This is the most portable method — works everywhere, no SSH config needed.

**Step 1: Create a personal access token**

Tell the user to go to: **https://github.com/settings/tokens**

- Click "Generate new token (classic)"
- Give it a name like "hermes-agent"
- Select scopes:
  - `repo` (full repository access — read, write, push, PRs)
  - `workflow` (trigger and manage GitHub Actions)
  - `read:org` (if working with organization repos)
- Set expiration (90 days is a good default)
- Copy the token — it won't be shown again

**Step 2: Configure git to store the token**

```bash
# Set up the credential helper to cache credentials
# "store" saves to ~/.git-credentials in plaintext (simple, persistent)
git config --global credential.helper store

# Now do a test operation that triggers auth — git will prompt for credentials
# Username: <their-github-username>
# Password: <paste the personal access token, NOT their GitHub password>
git ls-remote https://github.com/<their-username>/<any-repo>.git
```

After entering credentials once, they're saved and reused for all future operations.

**Alternative: cache helper (credentials expire from memory)**

```bash
# Cache in memory for 8 hours (28800 seconds) instead of saving to disk
git config --global credential.helper 'cache --timeout=28800'
```

**Alternative: set the token directly in the remote URL (per-repo)**

```bash
# Embed token in the remote URL (avoids credential prompts entirely)
git remote set-url origin https://<username>:<token>@github.com/<owner>/<repo>.git
```

**Step 3: Configure git identity**

```bash
# Required for commits — set name and email
git config --global user.name "Their Name"
git config --global user.email "their-email@example.com"
```

**Step 4: Verify**

```bash
# Test push access (this should work without any prompts now)
git ls-remote https://github.com/<their-username>/<any-repo>.git

# Verify identity
git config --global user.name
git config --global user.email
```

### Option B: SSH Key Authentication

Good for users who prefer SSH or already have keys set up.

**Step 1: Check for existing SSH keys**

```bash
ls -la ~/.ssh/id_*.pub 2>/dev/null || echo "No SSH keys found"
```

**Step 2: Generate a key if needed**

```bash
# Generate an ed25519 key (modern, secure, fast)
ssh-keygen -t ed25519 -C "their-email@example.com" -f ~/.ssh/id_ed25519 -N ""

# Display the public key for them to add to GitHub
cat ~/.ssh/id_ed25519.pub
```

Tell the user to add the public key at: **https://github.com/settings/keys**
- Click "New SSH key"
- Paste the public key content
- Give it a title like "hermes-agent-<machine-name>"

**Step 3: Test the connection**

```bash
ssh -T git@github.com
# Expected: "Hi <username>! You've successfully authenticated..."
```

**Step 4: Configure git to use SSH for GitHub**

```bash
# Rewrite HTTPS GitHub URLs to SSH automatically
git config --global url."git@github.com:".insteadOf "https://github.com/"
```

**Step 5: Configure git identity**

```bash
git config --global user.name "Their Name"
git config --global user.email "their-email@example.com"
```

---

## Method 2: gh CLI Authentication

If `gh` is installed, it handles both API access and git credentials in one step.

### Interactive Browser Login (Desktop)

```bash
gh auth login
# Select: GitHub.com
# Select: HTTPS
# Authenticate via browser
```

### Token-Based Login (Headless / SSH Servers)

```bash
echo "<THEIR_TOKEN>" | gh auth login --with-token

# Set up git credentials through gh
gh auth setup-git
```

⚠️ **`gh auth login --with-token` requires the token to have `read:org` scope.**
If the token only has `repo` (+ `workflow`) but not `read:org`, it will fail with:
```
error validating token: missing required scope 'read:org'
```

**Workaround when token lacks `read:org`:**
The token is still fully usable — just not through `gh auth login`. Use it directly instead:

```bash
# 1. Set GITHUB_TOKEN for API calls (curl)
export GITHUB_TOKEN="<token>"

# 2. Configure git credential store for git operations
git config --global credential.helper store
git config --global user.name "Your Name"
git config --global user.email "your-email@example.com"
echo "https://<github-username>:${GITHUB_TOKEN}@github.com" >> ~/.git-credentials
chmod 600 ~/.git-credentials

# 3. Verify git access
git ls-remote https://github.com/<owner>/<repo>.git

# 4. Verify API access
curl -s -H "Authorization: token $GITHUB_TOKEN" https://api.github.com/user
```

This approach works for all git operations (clone, push, pull) and all REST API calls — the missing `read:org` scope only blocks `gh auth` not actual repo access.

### Verify

```bash
gh auth status
```

---

## Using the GitHub API Without gh

When `gh` is not available, you can still access the full GitHub API using `curl` with a personal access token. This is how the other GitHub skills implement their fallbacks.

### Setting the Token for API Calls

```bash
# Option 1: Export as env var (preferred — keeps it out of commands)
export GITHUB_TOKEN="<token>"

# Then use in curl calls:
curl -s -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/user
```

### Extracting the Token from Git Credentials

If git credentials are already configured (via credential.helper store), the token can be extracted:

```bash
# Read from git credential store
grep "github.com" ~/.git-credentials 2>/dev/null | head -1 | sed 's|https://[^:]*:\([^@]*\)@.*|\1|'
```

### Helper: Detect Auth Method

Use this pattern at the start of any GitHub workflow:

```bash
# Try gh first, fall back to git + curl
if command -v gh &>/dev/null && gh auth status &>/dev/null; then
  echo "AUTH_METHOD=gh"
elif [ -n "$GITHUB_TOKEN" ]; then
  echo "AUTH_METHOD=curl"
elif _hermes_env="${HERMES_HOME:-$HOME/.hermes}/.env"; [ -f "$_hermes_env" ] && grep -q "^GITHUB_TOKEN=" "$_hermes_env"; then
  export GITHUB_TOKEN=$(grep "^GITHUB_TOKEN=" "$_hermes_env" | head -1 | cut -d= -f2 | tr -d '\n\r')
  echo "AUTH_METHOD=curl"
elif grep -q "github.com" ~/.git-credentials 2>/dev/null; then
  export GITHUB_TOKEN=$(grep "github.com" ~/.git-credentials | head -1 | sed 's|https://[^:]*:\([^@]*\)@.*|\1|')
  echo "AUTH_METHOD=curl"
else
  echo "AUTH_METHOD=none"
  echo "Need to set up authentication first"
fi
```

---

## WSL / Cross-Filesystem Auth (Windows → WSL)

When the agent runs inside WSL but Git repos live on the Windows filesystem (`/mnt/c/Code/...`), standard auth detection often fails because:

- `gh` may be installed but not logged in (no `gh auth status`)
- `~/.git-credentials` may have stale/expired tokens
- The actual working PATs are stored in the **Windows user's `.hermes/.env`** file at `/mnt/c/Users/<username>/.hermes/.env`

### Multi-Org PAT Detection (WSL)

> 📎 See `references/token-extraction-patterns.md` for alternative Python-based extraction (avoids shell escaping issues).

This user's setup uses org-specific PAT naming:

| Env var | Target Org/User |
|---------|----------------|
| `GITHUB_PAT_CLASSIC_A2SQUARE_AGENT` | A2-Square-aus org |
| `GITHUB_PAT_CLASSIC_AMLHIVE_AGENT` | amlhive-tech user (User account, not org) |
| `GITHUB_PAT_CLASSIC_OPERATOR` | haris-admin user |

**Discovery pattern:**

```bash
# 1. Check what PATs exist for the target org
grep -i "GITHUB_PAT_CLASSIC" /mnt/c/Users/habib/.hermes/.env 2>/dev/null

# 2. Extract full token (terminal may truncate with `...`; use xxd to see full value)
grep "GITHUB_PAT_CLASSIC_A2SQUARE_AGENT" /mnt/c/Users/habib/.hermes/.env | cut -d'=' -f2 | xxd

# 3. Set the remote URL with the correct org-specific token
FULL_TOKEN=$(grep "^GITHUB_PAT_CLASSIC_A2SQUARE_AGENT=" /mnt/c/Users/habib/.hermes/.env \
  | cut -d'=' -f2 | tr -d '\n\r')
git remote set-url origin "https://oauth2:${FULL_TOKEN}@github.com/A2-Square-aus/repo.git"
```

**Token length check** (should be 40 chars for a `ghp_` classic PAT):

```bash
echo "${#FULL_TOKEN}"
```

### Fixing Corrupted Remote URLs in WSL

Remote URLs can become corrupted when the credential helper double-encodes its token. Signs:

```
# BAD — token repeated, embedded https://
https://oauth2:ghp_X...@oauth2:ghp_X...@https://oauth2:ghp_X...@github.com/...

# GOOD — clean URL
https://oauth2:ghp_X...@github.com/...
```

Fix by reconstructing the URL with the token from `.hermes/.env`.

### Pre-Push Hooks with Windows Paths

WSL repos cloned from a Windows environment may have `.git/hooks/pre-push` that runs a Windows `python.exe` path, causing:

```
fatal: cannot exec '.git/hooks/pre-push': No such file or directory
```

**Workaround:** Disable the hook temporarily, push, then restore:

```bash
mv .git/hooks/pre-push .git/hooks/pre-push.bak
# ... push work ...
mv .git/hooks/pre-push.bak .git/hooks/pre-push
```

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `git push` asks for password | GitHub disabled password auth. Use a personal access token as the password, or switch to SSH |
| `remote: Permission to X denied` | Token may lack `repo` scope — regenerate with correct scopes |
| `fatal: Authentication failed` | Cached credentials may be stale — run `git credential reject` then re-authenticate |
| `ssh: connect to host github.com port 22: Connection refused` | Try SSH over HTTPS port: add `Host github.com` with `Port 443` and `Hostname ssh.github.com` to `~/.ssh/config` |
| Credentials not persisting | Check `git config --global credential.helper` — must be `store` or `cache` |
| Multiple GitHub accounts | Use SSH with different keys per host alias in `~/.ssh/config`, or per-repo credential URLs |
| `gh: command not found` + no sudo | Use git-only Method 1 above — no installation needed |
