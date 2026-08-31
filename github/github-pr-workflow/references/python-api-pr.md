# Programmatic PR Creation via Python + GitHub REST API

Use this when `gh` CLI isn't available and you need to create a PR programmatically — e.g. modifying a file in a remote repo and opening a PR from an automated script.

## Prerequisites

- A GitHub PAT with repo access (see `github-auth` skill)
- The repo must exist and be accessible with the token

## Workflow

### 1. Read the current file content (get SHA)

```python
import urllib.request, ssl, json, base64

headers = {
    "Accept": "application/vnd.github.v3+json",
    "User-Agent": "YourAgent/1.0",
    "Authorization": f"Bearer {TOKEN}",
}

def api(method, url, data=None):
    body = json.dumps(data).encode() if data else None
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    with urllib.request.urlopen(req, timeout=15) as resp:
        return resp.status, json.loads(resp.read().decode())

status, data = api("GET", f"https://api.github.com/repos/{owner}/{repo}/contents/{file_path}?ref=main")
sha = data.get("sha", "")
current_content = base64.b64decode(data["content"]).decode("utf-8", errors="replace")
```

### 2. Create a branch from main

```python
# Get the SHA of main branch
status, ref_data = api("GET", f"https://api.github.com/repos/{owner}/{repo}/git/ref/heads/main")
main_sha = ref_data["object"]["sha"]

# Create the branch
branch_name = "feat/my-change"
status, result = api("POST", f"https://api.github.com/repos/{owner}/{repo}/git/refs", {
    "ref": f"refs/heads/{branch_name}",
    "sha": main_sha,
})
# status should be 201
```

### 3. Modify the file content and commit

```python
new_content = current_content.replace(
    "old string to replace",
    "new string"
)

encoded = base64.b64encode(new_content.encode()).decode()
status, result = api("PUT", f"https://api.github.com/repos/{owner}/{repo}/contents/{file_path}", {
    "message": "descriptive commit message",
    "content": encoded,
    "sha": sha,           # the current file SHA from step 1
    "branch": branch_name,
})
# status should be 200 or 201
```

### 4. Create the Pull Request

```python
status, result = api("POST", f"https://api.github.com/repos/{owner}/{repo}/pulls", {
    "title": "PR title",
    "head": branch_name,
    "base": "main",
    "body": "PR description with markdown\n\n## Changes\n- List of changes",
})
# status should be 201
# result["html_url"] contains the PR URL
```

## Complete Example (from PLuto's ASIC URL PR)

This creates a PR that modifies `backend/app/api/internal/sync.py` to dynamically construct ASIC CSV URLs:

```python
import urllib.request, ssl, json, base64

TOKEN = "..."
headers = {"Accept": "application/vnd.github.v3+json", "User-Agent": "PlutoBot/1.0", "Authorization": f"Bearer {TOKEN}"}

def api(method, url, data=None):
    body = json.dumps(data).encode() if data else None
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    with urllib.request.urlopen(req, timeout=15, context=ctx) as resp:
        return resp.status, json.loads(resp.read().decode())

OWNER = "amlhive-tech"
REPO = "amlhive1"
FILE = "backend/app/api/internal/sync.py"
BRANCH = "feat/dynamic-asic-urls"

# Step 1: Read current file
_, data = api("GET", f"https://api.github.com/repos/{OWNER}/{REPO}/contents/{FILE}?ref=main")
sha = data["sha"]
content = base64.b64decode(data["content"]).decode("utf-8", errors="replace")

# Step 2: Create branch
_, ref_data = api("GET", f"https://api.github.com/repos/{OWNER}/{REPO}/git/ref/heads/main")
api("POST", f"https://api.github.com/repos/{OWNER}/{REPO}/git/refs", {
    "ref": f"refs/heads/{BRANCH}",
    "sha": ref_data["object"]["sha"],
})

# Step 3: Modify and commit (add import + new function)
new_content = content.replace(
    "from datetime import datetime, timezone",
    "from datetime import datetime, timezone, timedelta"
)
new_content = new_content.replace(
    '    "asic-business-names",\n]\n\n\n#',
    '    "asic-business-names",\n]\n\n# URL builder code here...\n#'
)
# Add the URL builder function...

encoded = base64.b64encode(new_content.encode()).decode()
api("PUT", f"https://api.github.com/repos/{OWNER}/{REPO}/contents/{FILE}", {
    "message": "C68: make ASIC CSV URLs dynamic",
    "content": encoded,
    "sha": sha,
    "branch": BRANCH,
})

# Step 4: Create PR
_, pr = api("POST", f"https://api.github.com/repos/{OWNER}/{REPO}/pulls", {
    "title": "C68: Dynamic ASIC CSV URLs",
    "head": BRANCH,
    "base": "main",
    "body": "## Changes\n\nMake ASIC bulk CSV URLs auto-detect the latest month from data.gov.au.",
})
print(f"PR: {pr['html_url']}")  # https://github.com/amlhive-tech/amlhive1/pull/1
```

## Pitfalls

- **The `!=*** in Python source code** — Hermes' terminal output masking substitutes `***` for token-like strings. When writing a Python script via `write_file` that contains `line.startswith('KEY=')`, avoid having `***` in adjacent parts of the source. Use `line.find('KEY=*** ` — actually this applies to any tool that handles `.env` references. The safest approach: extract the token value separately and pass it at runtime.
- **The `sha` parameter in PUT is critical** — GitHub uses it for optimistic locking. If you don't pass the current file SHA, the commit will fail. Always read the file first to get its SHA.
- **Private repos require authentication** — unauthenticated requests to private repos return 404 (not 401). This can be confused with "repo doesn't exist".
- **Different PATs may be needed for different orgs** — a PAT for `haris-a2squre` (user account) may not access `amlhive-tech` repos, even if the user is a member of the org. Use the org-specific PAT.
- **Token scopes matter** — to create branches and commit via API, the token needs at least `repo` scope. For org repos, may also need `read:org`.
