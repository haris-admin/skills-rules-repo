---
name: sentry-setup
description: "Set up Sentry error monitoring for Python (FastAPI) and Next.js projects — DSN configuration, SDK installation, config files, test events, and build integration. Use when adding Sentry error tracking to a new or existing project."
version: 1.0.0
author: Pluto
license: MIT
category: devops
platforms: [linux, macos, wsl]
metadata:
  hermes:
    tags: [Sentry, Error-Monitoring, Observability, Python, Next.js, FastAPI]
    related_skills: [vercel-monitoring, fastapi-field-propagation]
---

# Sentry Setup

Configure Sentry error tracking for Python (FastAPI) and Next.js (JS/TS) projects.

## Prerequisites

- Sentry account and organization (e.g. `amlhive-pty-ltd` on sentry.io)
- A Sentry project created for each app type (e.g. `python-fastapi`, `javascript-nextjs`)
- **SENTRY_DSN** — the project's DSN (found in Sentry Dashboard → Settings → Client Keys)
- **SENTRY_AUTH_TOKEN** — for source map uploads (Settings → Auth Tokens → Create New Token)

### DSN Structure

```
https://{key}@o{org_id}.ingest.us.sentry.io/{project_id}
```

The `ingest.us.sentry.io` indicates US region (check your project region). The project ID in the DSN is the **Sentry project ID**, not the org ID.

### Auth Token Scopes

| Scope | Required for |
|-------|-------------|
| `project:read` | Read project info, verify setup, **read events via `/events/` endpoint** |
| `project:releases` | Upload source maps, create releases |
| `org:read` | List organizations, projects |
| `event:read` | Read issues via `/issues/` endpoint, get issue details with aggregate counts |

**Minimal token**: `project:read` + `project:releases` is enough for the build plugin to upload source maps.

**🟡 Important scope trap:** The `/issues/` endpoint requires `event:read` scope, but the `/events/` endpoint works with just `project:read`. If your token returns HTTP 403 on issue listing, use the events endpoint instead (see "Reading Events with Limited Scope" below).

---

## Python (FastAPI)

### Installation

```bash
pip install sentry-sdk
```

### Configuration

```python
import sentry_sdk

sentry_sdk.init(
    dsn="https://{key}@o{org_id}.ingest.us.sentry.io/{project_id}",
    environment="production",  # or "staging", "test", "development"
    traces_sample_rate=1.0,    # 0.1 for production (sample 10%)
)
```

For FastAPI middleware integration:

```python
from fastapi import FastAPI
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.starlette import StarletteIntegration

sentry_sdk.init(
    dsn=DSN,
    environment="production",
    integrations=[
        StarletteIntegration(transaction_style="endpoint"),
        FastApiIntegration(transaction_style="endpoint"),
    ],
    traces_sample_rate=0.1,
)
```

### Testing

```python
# Send a test message
sentry_sdk.capture_message("Test message from {app_name}")

# Capture an exception
try:
    1 / 0
except ZeroDivisionError as e:
    sentry_sdk.capture_exception(e)

# Sentry flushes pending events within 2 seconds
```

### Verify via API

```python
import urllib.request, json

url = f"https://sentry.io/api/0/projects/{org_slug}/{project_slug}/"
req = urllib.request.Request(url, headers={
    "Authorization": f"Bearer {SENTRY_AUTH_TOKEN}",
})
with urllib.request.urlopen(req) as resp:
    data = json.loads(resp.read())
    print(f"Project: {data['slug']}, Status: {data['status']}")
```

### Reading Events with Limited Scope (🔑 Critical Workaround)

If your `SENTRY_AUTH_TOKEN` only has `project:read` scope (no `event:read`), the `/issues/` endpoint returns HTTP 403. This means you get **zero issue details** — only event counts via `/stats/`.

**Workaround:** Use the `/events/` endpoint instead. It returns individual event objects with full details using just `project:read` scope:

```python
import urllib.request, json

auth = "Bearer " + SENTRY_AUTH_TOKEN
org = "your-org-slug"
project = "your-project-slug"

url = f"https://sentry.io/api/0/projects/{org}/{project}/events/?full=true&limit=20"
req = urllib.request.Request(url, headers={"Authorization": auth})
with urllib.request.urlopen(req) as resp:
    events = json.loads(resp.read())

# Group by groupID to get unique issues
seen = {}
for evt in events:
    gid = evt.get("groupID")
    if gid not in seen:
        seen[gid] = {
            "title": evt.get("title", "?"),
            "level": evt.get("level", "error"),
            "count": 0,
            "sample": evt.get("message", "")[:120],
        }
    seen[gid]["count"] += 1

for gid, info in seen.items():
    print(f"[{info['level'].upper()}] {info['title']} ({info['count']}×)")
    print(f"  {info['sample']}")
```

**⚠️ The Count Discrepancy Trap:** The `/stats/` endpoint (used for event counts) can report misleadingly low numbers (e.g. "1 event in 24h") while `/events/` returns 100+ events. This happens because `/stats/` uses its own aggregation window that may not align with the 24-hour lookback. **Always cross-check event counts against the `/events/` endpoint for accurate volume data.** For monitoring scripts, fetch actual events rather than relying on stats alone.

---

## Next.js (JavaScript/TypeScript)

### Installation

```bash
npm install @sentry/nextjs
# or
yarn add @sentry/nextjs
```

### Configuration Files

Create **three** config files in the project root:

#### `sentry.client.config.ts`
```typescript
import * as Sentry from "@sentry/nextjs";

Sentry.init({
  dsn: "https://{key}@o{org_id}.ingest.us.sentry.io/{project_id}",
  environment: "production",
  tracesSampleRate: 1.0,
  debug: false,  // set true during initial setup
});
```

#### `sentry.server.config.ts`
```typescript
import * as Sentry from "@sentry/nextjs";

Sentry.init({
  dsn: "https://{key}@o{org_id}.ingest.us.sentry.io/{project_id}",
  environment: "production",
  tracesSampleRate: 1.0,
  debug: false,
});
```

#### `sentry.edge.config.ts`
```typescript
import * as Sentry from "@sentry/nextjs";

Sentry.init({
  dsn: "https://{key}@o{org_id}.ingest.us.sentry.io/{project_id}",
  environment: "production",
  tracesSampleRate: 1.0,
  debug: false,
});
```

### `next.config.ts` Wrapper

```typescript
import { withSentryConfig } from "@sentry/nextjs";

const nextConfig = {
  // ... your existing config
};

export default withSentryConfig(nextConfig, {
  org: "your-org-slug",
  project: "your-project-slug",
  authToken: process.env.SENTRY_AUTH_TOKEN,
  silent: false,
  telemetry: false,
});
```

### Client-Side Test Page

Create a test page at `src/app/test/page.tsx`:

```tsx
"use client";

import { useEffect, useState } from "react";
import * as Sentry from "@sentry/nextjs";

export default function TestPage() {
  const [status, setStatus] = useState("checking...");

  useEffect(() => {
    const client = Sentry.getClient();
    setStatus(client ? "✅ Sentry initialized" : "❌ Not initialized");
  }, []);

  const sendMessage = () => {
    const id = Sentry.captureMessage("🧪 Test message", {
      level: "info",
      tags: { test_type: "manual" },
    });
    setStatus(`✅ Sent! Event ID: ${id}`);
  };

  const sendError = () => {
    try {
      throw new Error("🧪 Test error");
    } catch (e) {
      const id = Sentry.captureException(e);
      setStatus(`✅ Sent! Event ID: ${id}`);
    }
  };

  return (
    <div>
      <p>Status: {status}</p>
      <button onClick={sendMessage}>Send Test Message</button>
      <button onClick={sendError}>Send Test Error</button>
    </div>
  );
}
```

### Build Verification

```bash
# With auth token for source map upload
SENTRY_AUTH_TOKEN="sntryu_..." npx next build

# Expected output includes:
#   ✓ Compiled successfully
#   [@sentry/nextjs] ✓ Completed runAfterProductionCompile
#   ✓ Generating static pages
```

**Note on static exports** (`output: "export"`): Sentry client SDK is still bundled and works in the browser. Source map upload will skip with a "No auth token" warning if the build can't reach the Sentry API, but the SDK itself still functions perfectly.

---

## 📎 Reference Files

- `references/homelab-config.md` — This environment's Sentry org, projects, DSNs, and token scope details. Consult for session-specific values.

## Pitfalls

- **`gh auth login --with-token` fails**: The token may lack `read:org` scope. This is fine — the token still works for git operations and API calls. Use git credential store + `GITHUB_TOKEN` env var instead.
- **"Project not found" during build**: The org and project slugs in `next.config.ts` must match the Sentry project exactly. Check the Sentry URL: `sentry.io/organizations/{org}/projects/{project}/`
- **Static export kills server-side Sentry**: With `output: "export"`, `sentry.server.config.ts` and `sentry.edge.config.ts` are dead code — no server runtime exists to trigger them. Only client-side Sentry (`sentry.client.config.ts`) works. A Sentry project monitoring a statically-exported Next.js app will show **zero events from the server/edge layers**. This is not a bug — it's expected. Don't flag it as telemetry silence; just drop server-side Sentry projects from monitoring checks.
- **DSN vs Auth Token**: The DSN is for SDK initialization (sends events). The Auth Token is for API access (source maps, project management). They are not interchangeable.
- **Permission denied on API calls**: Sentry auth tokens can be project-scoped. If a token lists projects but can't read issues, it lacks `event:read`. Use the `/events/` endpoint instead — it works with just `project:read` (see "Reading Events with Limited Scope" above).
- **Stats endpoint underestimates event volume**: `/stats/?stat=received&resolution=1d` uses its own aggregation window that can misalign with a 24-hour lookback. It may report "1 event" when 100+ exist. Always validate against `/events/` for accurate counts in monitoring scripts.
- **`/issues/` vs `/events/` endpoint semantics**: `/issues/` returns unique issues with aggregate event counts (requires `event:read`). `/events/` returns individual event objects (works with `project:read`). To get unique issue counts from `/events/`, group by `groupID` in application code.
