# Clover OAuth v2: verified facts (14 Oct 2026)

Each line says where it came from. "Fiserv" is Joshua Nicolson, Saas Partners and Developer Relations, by email. "Docs" is docs.clover.com.
"Dashboard" was seen in the Australian developer dashboard (`www.ap.clover.com/developer-home/...`). Re-verify before relying on a UI label.

## Hosts (Australia / APAC)

| Purpose | Production | Sandbox |
|---|---|---|
| OAuth authorize page | `www.ap.clover.com` | `sandbox.dev.clover.com` |
| Token, refresh, migrate_v2 | `api.ap.clover.com` | `apisandbox.dev.clover.com` |
| REST API (`/v3/merchants/...`) | `api.ap.clover.com` (Fiserv: "for all api calls") | sandbox REST host not stated |
| `/oauth/v2/recovery` | answers on `api.ap.clover.com`; Fiserv has not tested it end to end | unknown |

Legacy dashboard API tokens were accepted on `api.ap.clover.com` by a full production sync run (no 401, 403 or 405).

## Tokens

- Access token about 30 minutes; refresh token single use (Fiserv). Refresh body `{client_id, refresh_token}`; exchange body
  `{client_id, client_secret, code}` (docs, high-trust flow). Recovery request shape is **unverified**.
- Auth is **1:1 per merchant**; "access tokens in Clover are merchant-specific" (docs). A reseller may install in a merchant's account but then
  accepts the terms on the merchant's behalf and "should seek legal advice" (Fiserv).
- A market or dashboard install redirects the merchant to the redirect URI with the authorization code (Fiserv). You cannot generate the initial
  code server side without a user interface (docs FAQ).

## Fiserv approval method

Fiserv installs the app on its own production merchant and uses it as a live merchant, checking that each requested permission is used in a
visible flow ("orders read is being used to show orders in your dashboard"). It will not approve an app that requires a provided API key, even
as a private app. Webhooks need an approved app. API key integrations are more strictly rate limited.

## Permissions (docs permissions page; dashboard editor names)

Dashboard permission names: Customers, Employees, Inventory, Merchant, Orders, Payments, Ecommerce, each with Read and Write.

| Need | Permission |
|---|---|
| `GET /employees`, `GET /employees/{id}/shifts` | Employees Read |
| `POST /employees/{id}/shifts` (create a shift) | **Employees Write** (shift hours are under Employees; there is no shift-only write) |
| Orders, Payments, Customers, Inventory/items | the same-named Read |
| Tenders | Merchant Read (a Clover tender doc) |
| Cash events, devices, `transactions` endpoint, payment `expand` fields | **not documented**: test in the sandbox (a 401 or 403 names the missing permission) |
| Confirming a merchant (`GET /v3/merchants/{id}`) | Merchant Read |

## Dashboard behaviour

- **REST Configuration** (with the Site URL) appears only after the app type includes **REST Clients: Web** (App Settings, App Type, edit).
- Fields: Site URL, Alternate Launch Path (optional), CORS Domain (optional), Default OAuth Response (Code, the right choice; Token is testing only).
- The Site URL is the single redirect target. `redirect_uri` is a request parameter that must sit under it (same scheme and host).
- **Alternate Launch Path is appended to the Site URL.** Setting it equal to the callback path produces a doubled URL; leave it empty when the
  Site URL is already the callback.
- **A Site URL change is reviewed by Clover** before it can be published. A permissions change shows as "1 change in review" with Cancel
  Submission and Revert all changes.
- The REST Configuration editor shows the App Secret in clear text. The App Settings page masks it (eye icon).
- An app marked PRIVATE with availability "all merchants" is still private; production and staging are separate apps with separate IDs.
- The Global Developer sandbox and the production dashboard are separate environments (toggle at the top).

## Staging vs production in Tap-Ease

- `api-stg.tapease.com.au` resolves to the production frontend host (an nginx proxy) but is served by the dev EC2 `i-0f9a6ec659e6aab83`.
- Production app ID is not the staging app ID. Each has its own secret in `portal/clover-oauth/<env>`.

## Sandbox observations, 19 Oct 2026 (TapEase POS and Portal staging; observed, not documented by Clover)

- The Portal's code exchange, `POST apisandbox.dev.clover.com/oauth/v2/token`, returned **401 "Failed to validate authentication code"** for the TapEase sandbox app with a fresh code, for BOTH the US Test Merchant and an AU merchant. The same 401 message came back for the real app secret and for a wrong UUID-shaped secret with a fake code, so that probe cannot prove the stored secret is right. Refreshing an already stored token kept working (refresh needs the refresh token, not the secret).
- A redirect with only `merchant_id`, `client_id` and `packageName` (no `code`, no `state`) is the Clover app-install or open-app redirect, not an authorisation. A callback must see `code`; without it the Portal correctly shows "We could not complete the connection".
- Production Fiserv hosts for Australia are the `ap` region (`api.ap.clover.com`). Whether an AU **sandbox** merchant is served by `sandbox.dev.clover.com` / `apisandbox.dev.clover.com` is not documented; it was asked of Clover.
- A Flex 4 moved from the US Test Merchant to an AU sandbox merchant reported `FATAL: SRED_KEY_MISSING` on every card payment (provisioned, but SRED DUKPT, SRED TA and PIN DUKPT keys all false). Moving it back restored card payments.

