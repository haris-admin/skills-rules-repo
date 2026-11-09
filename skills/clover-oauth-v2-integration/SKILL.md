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
- **Legacy and OAuth run in parallel.** `clover_merchant_credentials.use_oauth` is the per-merchant switch. **Since backend 4.5.21 (9 Nov 2026) every
  successful approval stores `use_oauth = true`**, from a Tap-Ease link or a Clover install, for a known or a new merchant, first approval or re-approval
  (Haris: "Set the flag as true on the backend once we get the successful credentials"; spec `oauth-approval-sets-use-oauth`). Before 4.5.21 a merchant
  already in `trans_devices` stayed on legacy and needed a manual `UPDATE`; a merchant approved before that release still does.
- **An OAuth merchant with no terminal assigned to a driver gets no Lambda sync** (token answer `skipped`, `no_assigned_terminal`; decisions 67 to 71).
  Its cursor is held, so nothing is lost, but the sync alert ("skipped x1") repeats every run until a driver is assigned. A portal assignment
  (`POST /admin/assign_device_to_user`, status 1) also runs a safeguard: it makes sure the merchant is switched on, logs
  `Clover OAuth at terminal assignment | outcome=...` and sends a temporary email to `NOTIFICATION_EMAIL`.
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

- **An OAuth token is refused for the WHOLE call if any `expand` field needs a permission the app lacks** (9 Nov 2026): Clover answers
  `403 {"message":"Invalid permissions for expandable fields."}`. The old merchant API token carried every permission, so the same call worked.
  `customers` and `metadata` were refused; the Lambda's payment fetch (`bronze_payments_extended_fetcher.py`) asked for both, so the first payment of
  every merchant moved to OAuth failed with 403 on every run. Fixed in Lambda 0.10.14 (customers) and 0.10.15 (metadata). Request only the expansions the
  pipeline reads. Find the culprit by calling Clover for ONE payment once per expansion and printing only status codes (never the token): see
  `references/probe_expand.py` (run it as `ec2-user` on the production box through a short script Haris starts; the auto-mode classifier blocks an agent from running it).
- **The first thing a customer sees is usually our error page, not Clover's.** Clover first calls the callback with no `code` (only `merchant_id` and
  `client_id`; a launch request), we answer 400, then after consent a second call arrives with the `code` and works. Seen for three merchants on 9 Nov. A
  repeated code gives a 502 (Clover: "Failed to validate authentication code") even though the merchant is already connected. A friendly handling of both
  is proposed, not built: it changes the callback's frozen 400 and needs Haris's approval.
- **A Clover "installed" list entry proves nothing about our side.** Only a `clover_merchant_credentials` row does. Merchants showed "installed" in
  Clover with no callback at all, and 1086's first attempt was refused by Clover for redirect `https://api.tapease.co` before reaching us.
- **A log search proves absence only for the window the log covers.** The backend deploy moves and prunes `app/log/`, so after a release the day's file
  starts at the restart. Confirm "no approval" with the credential row (database), not a log (`rules/a-log-search-proves-absence-only-for-the-window-it-covers.md`).

## Verify

```bash
# read-only check of staging (no secrets printed): infra/staging-clover-oauth/verify.sh in the backend repo
./infra/staging-clover-oauth/verify.sh
```

After a switch, check three things (read-only): the Lambda's token answer for the merchant is `source: oauth` (backend log, within about 4 minutes), the
Lambda's `Clover token sources this run` line lists the merchant under `oauth_merchants` with `skipped=0`, and the Lambda log has no
`FETCH_FAILED` or `403 Forbidden` for it. Then watch the first payment through bronze, silver and gold.

## Related

- Skills: `tapease-pos-clover-shift-sync`, `tapease-backend-deploy`, `tapease-db-access`, `terraform-safety`, `external-api-integration`
- Rules: `secrets-in-query-strings-never-logged.md`, `one-secret-one-audience.md`, `locks-must-expire-by-their-own-ttl.md`,
  `tapease-prod-deploy-boundary.md`, `terraform-prod-apply-safety.md`
