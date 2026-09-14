---
name: plane-issues
description: "Use when reading Plane.so issues or projects."
platforms: [linux, macos, windows]
---

# Plane.so — issues and projects (fleet)

Plane is the fleet's **system of record for issues/tickets**. It mirrors **one-way into Notion**
(`Plane Projects` / `Plane Issues` databases). Never write issues back from Notion — that creates two
masters.

## Two keys, two spaces

Both in `/mnt/c/Users/habib/.hermes/.env` (strip CRLF/BOM). Never print the values.

| Var | Workspace slug | Scope |
|---|---|---|
| `PLANE_API_KEY_TAPEASE` | `tapease` | Tapease business |
| `PLANE_API_KEY_AI_IDEAS` | `ai_ideas` | AI ventures |

Both authenticate as `hhsiddiqui` / `hhsiddiqui@gmail.com` (user id `52dd5125-ff63-427a-8305-316203b00767`).

## 🔴 Cloudflare error 1010 — the gotcha that wastes an hour

`api.plane.so` sits behind Cloudflare. **python-urllib's default User-Agent gets HTTP 403 with
Cloudflare error 1010** ("banned browser signature"). It looks exactly like an invalid key. It is
not. Same key, same URL:

- default urllib UA → **403 / error 1010**
- browser-like UA → **200**

```python
req.add_header("User-Agent",
  "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
  "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36")
```

curl's default UA passes. **Always set a browser UA** when calling Plane programmatically, and
interpret a 1010 as a fingerprint problem, never as a bad credential.

## Endpoints

Base `https://api.plane.so/api/v1`, header `X-API-Key: <key>`.

| Path | Result |
|---|---|
| `GET /users/me/` | 200 — validate a key |
| `GET /workspaces/{slug}/projects/` | 200 — projects |
| `GET /workspaces/{slug}/projects/{project_id}/issues/` | issues |
| `GET /workspaces/` | **404 — no such endpoint.** Go straight to a slug. |

Note the slug is **`ai_ideas`** (underscore) — `ai-ideas` returns `Workspace not found`.

## Workspace → projects (verified 2026-09-13)

**`tapease`** — 2 projects
- `TEWEB` Tapease-website — `9100b6fc-e339-4547-a5b5-65db2de487c4`
- `TAPEA` tapease — `bf288c51-c781-43bd-a5b7-99b06559e99c`

**`ai_ideas`** — 4 projects (the AI ventures; more get added over time)
- `AML` AML Solution (AMLHive) — `006507dd-87f1-4624-83f0-2a25522adf33`
- `PERSONAL` Personal — `6f9cf4ff-9ec6-4723-b2d5-2bc6463a75b5`
- `PA` Personal_Assistant — `9c4727e4-7994-42b8-8766-00699b770ecb`
- `STARTUP` Startup moonshot — `facd3d98-13f2-464a-98a5-4368ce180402`

**Ventures tracked under `ai_ideas`:** AMLHive, Undispute, Simplifii — plus anything new Haris
stands up. When a new venture appears, add its project id here.

## Reading issues

```python
# projects
GET /workspaces/ai_ideas/projects/
# issues for one project (page through with ?cursor=)
GET /workspaces/ai_ideas/projects/{project_id}/issues/
```

Set a browser `User-Agent` on every call (see above). Report reads as counts by state/priority plus
the open items that matter — don't dump raw JSON at the user.

## Related

- `productivity/notion` — `references/plane-integration.md`
- `devops/notion-cmdb-operations` — the CMDB side
- Rule: `rules/fleet-records-system-of-record.md`
