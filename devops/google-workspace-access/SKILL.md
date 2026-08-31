---
name: google-workspace-access
description: "Use when Google Sheets/Drive access blocked or needs setup."
version: 1.0.0
author: Pluto
tags: [google, oauth, sheets, drive, gmail, wsl]
---

# Google Workspace Access (Hermes on WSL)

Class-level skill for getting Hermes connected to Google resources
(Sheets, Drive, Docs, Gmail API) from this WSL machine, and for diagnosing why
a connection is blocked. Complements the bundled `google-workspace` skill
(which documents the generic OAuth flow) with this environment's actual
credential state and the pitfalls that bite here.

## Trigger
- "access this Google Sheet / Drive / Doc" and it fails or needs setup
- OAuth setup appears blocked (`invalid_client`, `invalid_scope`, `deleted_client`)
- A cron/script needs Google API access for a specific account
- Confusing "I have access, why can't you?" situations (browser access ≠ API access)

## Two credential systems — never confuse them

| System | What it covers | How it authenticates |
|--------|----------------|----------------------|
| **Gmail App Password** | IMAP/SMTP only (reading/sending email) | `GOOGLE_GMAIL_APP_PASSWORD_MACARTHUR` in `.hermes/.env`, used by `gmail_ingestor_imaplib.py` |
| **OAuth2 client + token** | Sheets, Drive, Docs, Gmail API (REST) | Desktop OAuth client JSON → consent flow → `~/.hermes/google_token.json` |

**A working Gmail ingestor does NOT mean Sheets/Drive work.** App passwords
never grant REST API scopes. Each system has its own failure surface.

## Triage checklist (fastest first)

1. **Identify the stored OAuth client's project** (read `client_id` prefix from
   `~/.hermes/google_client_secret.json`). If it starts with `477680308212`,
   it belongs to the **deleted project** — every client there returns
   `invalid_client: The OAuth client was not found.` on the token endpoint.
2. **Verify a client is alive before building a flow**: token endpoint 401
   `invalid_client` = deleted. (All 477680308212 clients confirmed dead 2026-08-07.)
3. **gcloud ADC is useless for sensitive scopes**: the ADC
   (`/mnt/c/Users/habib/AppData/Roaming/gcloud/application_default_credentials.json`)
   is the gcloud built-in client (`764086051850-...`) with only
   `cloud-platform`, `sqlservice.login`, `userinfo.email`, `openid` scopes.
   Requesting `spreadsheets.readonly` via refresh → `invalid_scope`. Skip it.
4. **Test if the resource is public before OAuth**:
   ```
   https://docs.google.com/spreadsheets/d/<ID>/export?format=csv&gid=0
   https://docs.google.com/spreadsheets/d/<ID>/gviz/tq?tqx=out:csv
   ```
   HTTP 401 = private (needs account auth). HTTP 200 = public, no OAuth needed.
5. **Search for a newer client secret** in `~/Downloads`, `~/Desktop`,
   `~/Documents`, `~/OneDrive` (Windows side) for `client_secret*` files or the
   target project number. The working project for macarthurgarments@gmail.com is
   **open-claw1-494112** (Sheets API enabled there 2026-08-03).
6. **Ignore stale pending OAuth state**: `~/.hermes/google_oauth_pending.json`
   may hold PKCE leftovers with no `client_id` — not a usable connection.

## The fix path (one-time user action)

A Desktop OAuth client must exist in a live GCP project with the target account
as a test user:

1. console.cloud.google.com → live project (e.g. `open-claw1-494112`)
2. APIs & Services → Library → enable **Google Sheets API** + **Google Drive API**
3. OAuth consent screen → External → Test users → add the target account
   (e.g. `macarthurgarments@gmail.com`)
4. Credentials → Create Credentials → OAuth 2.0 Client ID → **Desktop app** → Create
5. Download JSON → run the bundled `google-workspace` setup flow:
   ```bash
   python ~/.hermes/skills/productivity/google-workspace/scripts/setup.py \
     --client-secret /path/to/client_secret_<project>-....json
   python ~/.hermes/skills/productivity/google-workspace/scripts/setup.py \
     --auth-url --services sheets,drive --format json
   ```
   → user approves as the target account → exchange code → token saved to
   `~/.hermes/google_token.json` → API calls work.

## Environment reference (as of 2026-08-08)

- Target sheet: **Agent Task Queue & Kanban Board** —
  `1knJLcmr_erIXAa7fMCf55b5rqAYF9GjF0_GNMkMWzII` (confirmed real by Haris;
  macarthurgarments@gmail.com has access).
- OAuth status: **no valid OAuth client on this machine**; all old clients
  belong to deleted project 477680308212 (`invalid_client` confirmed live).
- **Working access path (since 2026-08-08): CDP-attach to the user-signed-in
  Chrome on port 9222 (dedicated profile, login persists).** Full recipe —
  Chrome launch command, WSL patchelf RPATH fix, name-box navigation,
  `.cell-input` reads, and the F2 + Selection API + insertText + **Tab** write
  sequence — lives in `references/cdp-sheets-access.md`. The Kanban Board was
  read (22 tasks) and written (TASK-023 instruction + TASK-003 status/response
  + TASK-024..039 rows) through this path. Unblocks on-demand sheet access
  now; the OAuth client remains the right end-state for durable
  cron/automation.
- **If the debug Chrome was closed and needs relaunching, read the "Relaunch &
  profile pitfalls" section in `references/cdp-sheets-access.md` FIRST.** The
  wrong `--user-data-dir` silently creates a fresh profile with no login; the
  user's normal Chrome (where they often open the target) has no debug port;
  and the gateway scanner may block direct chrome.exe launches (use
  `cmd.exe /c start` from `/mnt/c`).

## Pitfalls

- **Browser access by the user ≠ API access by the agent.**
- **Hermes' own browser tool can fail with `libnspr4.so: cannot open shared
  object file` on WSL even though the Playwright test runners work.** The
  long-lived Hermes process doesn't inherit the session `LD_LIBRARY_PATH`;
  exporting it in `.bashrc` won't help until Hermes restarts. Fix without
  restart: bake the library path into the Chrome binary and its transitive
  deps with `patchelf --set-rpath` (DT_RUNPATH is not transitive — patch the
  libs too). Full commands in `references/cdp-sheets-access.md` §2.
- Browser access by the user ≠ API access by the agent. "The sheet is opening"
  in the user's browser proves nothing about Hermes' ability to read it.
- Deleting/recreating a GCP project silently kills every OAuth client under it;
  stale `client_secret_*.json` files on disk keep looking valid but 401.
- Never hardcode Google credentials — the app-password pattern (read from `.env`
  at runtime) is the template; OAuth tokens auto-refresh from
  `google_token.json`.
- The `google-workspace` skill's `--check` prints `NOT_AUTHENTICATED` when
  `google_token.json` is missing — that is the expected state until the
  one-time consent flow completes, not a broken install.
