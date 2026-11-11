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

## Bulk updates and rate limits (HandleDispute, 8 Nov 2026)

- Plane answered HTTP 429 after about 30 calls in a minute. Read the ticket list once into a file, sleep 3 seconds between writes, and on a 429 wait 40 seconds and retry that one call. Do not re-run a whole batch: it repeats comments.
- Move a ticket to Done only with evidence that it is released and checked live, and write that evidence in a comment on the ticket. A ticked task is not evidence.
- A script that creates tickets from specs can duplicate one you created by hand: dry run it first and search titles for the spec id.



## Learned in Claude Code on macOS (11 Nov 2026, Tap-Ease TAPEA board)

- **Where the key is:** the TAPEA key is `PLANE_API_KEY_TAPEASE` in the POS repo's gitignored `backend/.env` (and the Lambda repo's `.env`). Read it inside a script; never print it or put it on a command line. The workspace is `tapease`, project TAPEA `bf288c51-c781-43bd-a5b7-99b06559e99c`.
- **Rate limit:** bursts of reads return HTTP 429. Sleep about 1.5 s between calls and retry with a growing wait (20 s times the attempt number).
- **Pagination:** list issues with `?cursor=<next_cursor>` while `next_page_results` is true; `sequence_id` is the number in `TAPEA-<n>`.
- **Labels:** `GET /labels/` lists them (POS, BACKEND, FRONTEND, LAMBDA, POS_APP exist); create one with `POST /labels/` and `{name, color}`. When setting labels on an issue with `PATCH`, send the full list (existing ids plus the new one); the patch replaces the list.
- **State and text:** `PATCH {"state": <uuid>}` with the uuid from `GET /states/` (Backlog, Todo, In Progress, Done, Cancelled); `description_html` is HTML and replaces the whole description, so read it first and append a dated status block.
- **Create:** `POST /issues/` with `name`, `description_html`, `state`, `priority`, `labels`. **Delete:** `DELETE /issues/<uuid>/` is permanent; verify the state and title before deleting and only when asked.
- **Practice:** search the board before building a screen (a ticket for the same screen may already exist); move tickets to Done only when the owner says so or the work is submitted and verified; add a status note to each touched ticket.
