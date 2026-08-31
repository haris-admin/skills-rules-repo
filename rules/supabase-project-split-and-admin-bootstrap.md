# Supabase dev/prod project split and platform-admin bootstrap (all agents)

Applies whenever an agent is asked to create/modify a platform admin (`AMLHIVE_ADMIN`), run any
script under `backend/scripts/` that talks to Supabase Auth, or reason about which environment a
local backend command will actually hit.

## Why this exists

Two facts make "just run the script" unsafe, and both were re-derived from scratch on 26 Jul 2026
after roughly a dozen tool calls. Neither is discoverable from the script itself.

**1. There are two Supabase projects, and this machine's `backend/.env` points at the dev one.**

| | Project ref | Reached from |
|---|---|---|
| **Dev** | `mhqdympsyulawviycjmb` | local `backend/.env` (`SUPABASE_URL`, and `DATABASE_URL` → `aws-1-ap-southeast-2.pooler.supabase.com`) |
| **Production** | `lktkqoocfzbsounguotk` | deployed app only — prod `SUPABASE_URL` + prod RDS `DATABASE_URL` (`yourapp-prod…rds.amazonaws.com`) |

See `docs/context.md` ("Auth" row) for the authoritative statement of the split. A local
`poetry run python scripts/…` therefore hits **dev Supabase Auth + the dev Supabase Postgres** —
never production. That is usually the safe outcome, but it means a local run can silently do
nothing for production while looking like it succeeded.

**2. `bootstrap_admin.py` writes to two different systems, and they can be pointed at different
environments.** It (a) creates/updates the Supabase Auth identity with
`app_metadata.role = AMLHIVE_ADMIN`, then (b) inserts the `platform_users` row and writes an
`ADMIN_BOOTSTRAP` platform audit entry via `AsyncSessionLocal`. If `SUPABASE_URL` and
`DATABASE_URL` resolve to different environments, the result is a **half-provisioned admin** —
an identity that can authenticate but has no `platform_users` row, or a row whose identity does
not exist. Both are worse than not running it at all.

`AMLHIVE_ADMIN` is the highest privilege in the system: platform-wide, and it bypasses tenant
isolation via `set_platform_bypass`. Treat creating one as a privilege change subject to
[privilege-change-blast-radius-audit.md](privilege-change-blast-radius-audit.md).

## Rules

1. **Establish the target environment before running anything that writes.** Do it without
   printing secrets — hostnames and project refs are not secrets, keys are:

   ```bash
   cd backend && ./.venv/bin/python -c "
   from urllib.parse import urlparse
   from app.core.config import settings
   db = urlparse(str(settings.DATABASE_URL))
   print('SUPABASE_URL host:', urlparse(settings.SUPABASE_URL).hostname)
   print('DATABASE_URL host:', db.hostname, '| db:', (db.path or '').lstrip('/'))
   print('ENVIRONMENT      :', settings.ENVIRONMENT)
   "
   ```

   `mhqdympsyulawviycjmb` → dev. `lktkqoocfzbsounguotk` → **production, stop and get explicit
   authorisation.** A `DATABASE_URL` host of `*.pooler.supabase.com` is Supabase;
   `yourapp-prod*.rds.amazonaws.com` is the production RDS. If the two do not agree on
   environment, do not run the script — report the mismatch.

2. **`backend/scripts/bootstrap_admin.py` is the only path to create a platform admin.** There is
   no admin-portal endpoint for it — `backend/app/api/admin/v1/users_admin.py` manages *agency*
   users only (`list_pending_users`, `approve_user`, `reject_user`, `deactivate_user`) and never
   creates a `PlatformUser`. Do not hand-insert a `platform_users` row as a workaround; without
   the Supabase Auth identity the account cannot log in.

3. **Never let the generated temp password into agent context.** The script prints a 20-character
   plaintext password to stdout. Redirect the whole run to a file outside the repo and surface
   only the non-secret lines:

   ```bash
   ./.venv/bin/python scripts/bootstrap_admin.py --email <addr> > "$OUT" 2>&1
   grep -v -i "temp password" "$OUT"   # then tell the human where $OUT is
   ```

   This is a redirect, not masking — see [no-secret-masking.md](no-secret-masking.md), which
   forbids deriving a "safe" display string from the credential itself.

4. **A 401 from Supabase is a rotation event, not a puzzle.** `{"message":"Invalid API key"}` on
   `/auth/v1/admin/users` **and** `/rest/v1/` means `SUPABASE_SECRET_KEY` is revoked, rotated, or
   belongs to the other project — Supabase's own hint says so. Get a fresh `sb_secret_*` key from
   Supabase → Settings → API Keys for the correct project ref. Never reconstruct one, and never
   test a suspect key against the *production* project to find out which one it belongs to —
   ask the human. See [aws-profile-and-secret-recovery.md](aws-profile-and-secret-recovery.md).

5. **Auth is still Supabase.** `openspec/changes/00d-cognito-auth-postmark-login/` is
   `status: proposed` (verified 26 Jul 2026) — Cognito is **not** live. `verify_jwt_supabase` in
   `backend/app/core/auth_admin.py` is still the admin auth path, enforcing AMLHIVE_ADMIN/SUPPORT
   plus AAL2 outside dev. Re-check that status before asserting otherwise; when it flips, this
   rule needs revising, not working around.

## Known state — 26 Jul 2026

The dev `SUPABASE_SECRET_KEY` in `backend/.env` is a new-format `sb_secret_*` key that project
`mhqdympsyulawviycjmb` **rejects with 401 `Invalid API key`** on both `/auth/v1/admin/users` and
`/rest/v1/`. `bootstrap_admin.py` cannot run locally until it is rotated. The failure occurs in
`create_auth_user()`, which runs *before* any DB write, so a failed run leaves no partial state —
verified: `platform_users` still held exactly its two pre-existing rows afterwards.

Worth investigating rather than just rotating: a dev `.env` holding a key its own project rejects
usually means either dev was rotated without the local file being updated, or a **production**
secret was pasted into the dev file.

## Related

- [privilege-change-blast-radius-audit.md](privilege-change-blast-radius-audit.md) — the audit an
  `AMLHIVE_ADMIN` grant is subject to
- [no-secret-masking.md](no-secret-masking.md) — why the temp password gets redirected, not masked
- [aws-profile-and-secret-recovery.md](aws-profile-and-secret-recovery.md) — rotate, never
  reconstruct
- [cloudflare-r2-two-account-credential-trap.md](cloudflare-r2-two-account-credential-trap.md) —
  the same two-accounts-one-name failure shape, on Cloudflare
- `docs/context.md` — authoritative dev/prod project refs and the post-cutover auth posture
