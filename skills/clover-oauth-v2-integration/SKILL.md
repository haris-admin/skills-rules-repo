---
name: clover-oauth-v2-integration
description: >-
  How the Tap-Ease backend authenticates to Clover with OAuth v2 expiring tokens instead of merchant API tokens, and how the Clover
  developer dashboard, Fiserv approval and the token broker fit together. Use when working on the Clover OAuth callback, the token broker
  or its secrets, a Clover app's Site URL, REST Configuration, permissions or Android/REST app type, migrating merchants from API tokens
  to OAuth, answering Fiserv approval questions, or debugging a Clover 401, 405 or "not configured" response.
---

# Clover OAuth v2 integration (Tap-Ease)

Fiserv will not approve a Clover app that needs a provided API key, so the Tap-Ease **Portal backend** holds one encrypted OAuth v2 token
pair per merchant. Verified facts, dashboard behaviour and Fiserv's answers are in `references/verified-facts.md`; the build and test
lessons are in `references/build-lessons.md`. Source of truth in the repo: `openspec/changes/clover-oauth-v2-token-broker/`
(`design.md` section 9 holds every decision, recorded verbatim).

## Shape of the system

```
Clover terminal app --local intent--> Clover device                 (no REST token; unchanged)
        | HTTPS
mapp/backend (hop 2) --Tapease M2M key--> Portal backend (hop 3) --Bearer--> Clover cloud (api.ap.clover.com)
                                          + Lambda reads Clover (separate change)
```

- **Only the Portal backend** exchanges or refreshes tokens (the broker, `app/services/clover_oauth_service.py`). Refresh tokens are single use,
  so two refreshers destroy each other. The Lambda must never refresh; it asks the backend (shared-secret internal endpoint, not built yet).
- **One token pair per merchant**, never one for the company. Clover has no client-credentials grant and no umbrella token; each merchant
  approves once (a market install, or a staff-run in-person session).
- **Legacy and OAuth run in parallel.** `clover_merchant_credentials.use_oauth` (default false) is the per-merchant switch. A merchant already in
  `trans_devices` stays on the legacy token; an unknown merchant (Fiserv's own test install) is accepted OAuth only.
- **The single redirect URI** `GET /integrations/clover/oauth/callback` serves two modes: with `state` a staff connect (single use, expiring,
  merchant-bound, hash stored), without it a Clover install (the code exchange is the proof, and the merchant is confirmed with Clover).
- **Secrets** live only in `portal/clover-oauth/<env>` (app secret, Fernet encryption key, internal API secret), created by
  `infra/clover-oauth-iam`. The placeholder `REPLACE_WITH_CLOVER_APP_SECRET` means not configured and fails closed.

## Do

1. Read `design.md` section 9 before changing behaviour; a changed requirement voids earlier reviews (`requirement-change-voids-reviews`).
2. Use the dashboard's **Site URL** (under App Settings, REST Configuration) set to the callback URL; `redirect_uri` is a request parameter,
   not a dashboard field, and must sit under the Site URL. One Site URL per app, so one Clover app per environment.
3. Request the permissions the code uses, read-only except **Employees Write** (shift create and close; there is no shift-only write).
4. Never log the OAuth `code` or `state` (`rules/secrets-in-query-strings-never-logged.md`).
5. Keep the production app separate from the staging app: different App ID, secret, Site URL. Check which the dashboard is showing.

## Pitfalls

- `www.ap.clover.com` is only the OAuth authorize page; token, refresh and REST calls use `api.ap.clover.com`. Legacy dashboard API tokens
  work on both hosts.
- A URL setting with a trailing space produced HTTP 405 on every call and silently stopped a production sync
  (`rules/integration-config-change-verify-and-rollback.md`).
- Adding the REST Clients: Web type, or changing permissions, on a **live private app** is a change to something merchants already have;
  a permissions change goes to Clover review. The REST Configuration editor shows the App Secret in clear text: do not screenshot it.
- Changing a Site URL is reviewed by Clover before it can be published.
- `use_oauth = true` with `needs_reauth` has no fallback to the legacy token by design: it skips and reports.
- **Dashboard install is not the same as the v2 link (27 Oct 2026).** A merchant installing from the Clover dashboard follows a link with no `redirect_uri`, so Clover builds the redirect from the app settings (Site URL, Alternate Launch Path). The v2 link supplies `redirect_uri` itself. The v2 link and the callback work; the dashboard path failed before reaching us. Clover's v2 App Market flow (per Codex, not yet verified by us) is launch URL first, then the app starts `/oauth/v2/authorize`. Our callback refuses a request with no `code` (400) and nothing starts the authorize step. Confirm with Clover before changing any production setting.
- Our app settings are `Site URL = https://api.tapease.com.au/integrations/clover/oauth/callback` and `Alternate Launch Path = /integrations/clover/oauth/callback`. Joined, that is 96 characters with the path twice; unproven whether Clover joins them.
- **The install alone gives only `merchant_id`, `employee_id` and `code`.** Device ID and serial come later from the REST sync (needs the stored credential). The callback confirms the merchant id only; no name or email is read.
- The Lambda Gold devices sync (`devices_gold_service.py`) already creates `trans_devices` rows (`ACTIVE`) from Silver devices that have a `terminal_id`, matching existing rows by `terminal_id`. A placeholder row with no `terminal_id` would be missed and duplicated unless a merge rule is added.
- Onboarding direction (Haris, 27 Oct 2026, verbatim in the backend repo's `docs/clover_dashboard_install_assessment_2026-10-27.md`): install creates an unlinked device row at the callback (reverses the callback's documented no-write property; spec R20 is the no-API-key rule), `link_status` column, pending user activated by invite, staff link. Merge rule (fill the placeholder) and email (Clover if returned, else staff) decided; plan in the backend repo's `openspec/changes/clover-install-unlinked-onboarding/`. Terms gate (O7), O9a and the launch endpoint still open.

## Verify

```bash
# read-only check of staging (no secrets printed): infra/staging-clover-oauth/verify.sh in the backend repo
./infra/staging-clover-oauth/verify.sh
```

## Related

- Skills: `tapease-pos-clover-shift-sync`, `tapease-backend-deploy`, `tapease-db-access`, `terraform-safety`, `external-api-integration`
- Rules: `secrets-in-query-strings-never-logged.md`, `one-secret-one-audience.md`, `locks-must-expire-by-their-own-ttl.md`,
  `tapease-prod-deploy-boundary.md`, `terraform-prod-apply-safety.md`
