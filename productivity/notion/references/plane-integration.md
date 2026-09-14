# Plane.so integration (feeds the Notion issue mirror)

Plane is the **system of record for issues**; the Notion databases `Plane Projects`
(`9070d92c-09ad-4309-a093-cb2c3d160ac3`) and `Plane Issues` (`ad2c3422-abd7-45ad-ba3f-1066226fafe9`)
mirror it. **Keep the flow one-way (Plane → Notion).** Writing back creates two masters.

## Keys (Windows `.env`, strip CRLF/BOM)

| Var | Workspace | Verified |
|---|---|---|
| `PLANE_API_KEY_TAPEASE` | `tapease` | ✅ 2026-09-13 |
| `PLANE_API_KEY_AI_IDEAS` | `ai_ideas` | ✅ 2026-09-13 |

Both authenticate as **`hhsiddiqui`** / `hhsiddiqui@gmail.com` (user id `52dd5125-ff63-427a-8305-316203b00767`).

## 🔴 Cloudflare gotcha — error 1010 (this WILL bite you)

`api.plane.so` sits behind Cloudflare. A request carrying **python-urllib's default User-Agent gets
HTTP 403 with Cloudflare error 1010** ("banned browser signature"). This is **not** an invalid key —
it is the client fingerprint. Same key, same URL:

- default urllib UA → **403 / error 1010**
- browser-like UA → **200**

```python
req.add_header("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
               "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36")
```

Always set a browser UA when calling Plane programmatically (curl's default UA works too).

## Endpoints

Base `https://api.plane.so/api/v1`, header `X-API-Key: <key>`.

| Path | Result |
|---|---|
| `GET /users/me/` | 200 — identity / key validity check |
| `GET /workspaces/{slug}/projects/` | 200 — projects in that workspace |
| `GET /workspaces/{slug}/projects/{project_id}/issues/` | issues |
| `GET /workspaces/` | **404 — no such endpoint.** Don't probe it; go straight to a slug. |

## Workspaces → projects (verified 2026-09-13)

**`tapease`** (key `PLANE_API_KEY_TAPEASE`)
- `TEWEB` Tapease-website — `9100b6fc-e339-4547-a5b5-65db2de487c4`
- `TAPEA` tapease — `bf288c51-c781-43bd-a5b7-99b06559e99c`

**`ai_ideas`** (key `PLANE_API_KEY_AI_IDEAS`) — note the **underscore**; `ai-ideas` 404s
- `AML` AML Solution — `006507dd-87f1-4624-83f0-2a25522adf33`
- `PERSONAL` Personal — `6f9cf4ff-9ec6-4723-b2d5-2bc6463a75b5`
- `PA` Personal_Assistant — `9c4727e4-7994-42b8-8766-00699b770ecb`
- `STARTUP` Startup moonshot — `facd3d98-13f2-464a-98a5-4368ce180402`

(6 projects total = the 6 rows in the Notion `Plane Projects` mirror.)
