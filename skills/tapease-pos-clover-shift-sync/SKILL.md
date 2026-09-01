---
name: tapease-pos-clover-shift-sync
description: >
  How the Tap-Ease POS terminal integration (PAUSE / Clover partner) syncs driver
  shifts to the Clover Platform REST API, and how to debug it. Use when a partner
  reports that POST /v1/pos/shifts/start or /v1/pos/shifts/close returns
  clover_shift_id: null, is_clover_synced is wrong, clover_sync_status is
  "pending"/"skipped", a Clover shift isn't opening/closing, or when changing the
  shift-close payout / Clover mirror logic in app/services/pos_service.py or
  app/services/clover_shift_client.py.
---

# Tap-Ease POS ↔ Clover shift sync

`POST /v1/pos/shifts/start` and `/v1/pos/shifts/close` (in
`app/routers/pos_integrations.py` → `app/services/pos_service.py`) mirror the
driver shift into Clover via `app/services/clover_shift_client.py`, and return a
`clover_shift_id` plus a `clover_sync_status`.

## What must be true for `clover_shift_id` to come back

Three inputs, all resolved from the DB row for the terminal:

| Input | Column | Notes |
|---|---|---|
| Clover **merchant id** | `trans_devices.merchant_id_clover` (falls back to `terminal_merchant_id`, then `"DEV_MERCHANT"`) | e.g. `GRW1F281F36K1` |
| Clover **API token** | `trans_devices.clover_token` | **production model: the token lives on the device row.** `pos_service` passes it as `api_token=` to every `clover_shift_client` call. Falls back to global `CLOVER_API_TOKEN` env / `portal/clover-sync/*` secret only if the device has none. |
| Clover **employee id** | `auth_users.employee_id_clover` (or `user_id_clover`) for the driver assigned to the device (`trans_device_users.status = 1`) | the real value shows up as `payment.employee.id` in Clover payment payloads |

If `employee_id_clover` is missing → `start_driver_shift` sets
`clover_sync_status = "skipped"` + a `clover_sync_error`, and never calls Clover.
If the token can't be resolved → `create_shift()` logs *"Clover API token not
configured; skipping"* and returns `None`, so `clover_shift_id` stays null with
`clover_sync_status = "pending"`.

## `clover_sync_status` contract (as of v4.2.22)

| Value | Meaning |
|---|---|
| `synced` | a Clover `create_shift` / `close_shift` call **confirmed** it. `is_clover_synced: true`. |
| `pending` | Clover was called but did not confirm (HTTP error, no id back). Retry-able. |
| `skipped` | no identity/token to sync with — Clover was **not** called. |
| `failed` | `create_shift` raised. |

Before v4.2.22 `close` hard-coded `clover_sync_status = "synced"` and
`is_clover_synced: true` **regardless of whether any Clover call happened** — a
null `clover_shift_id` with `is_clover_synced: true` was the classic symptom.
`clover_sync_error` is now persisted to `trans_driver_shifts`.

## Close-time resolution order (`process_shift_close_payout`)

1. `clover_shift_id` stored on the open `trans_driver_shifts` row (set at start).
2. else `get_open_shift_for_employee(merchant, employee, api_token)` if we have an employee id.
3. else `get_open_shift_for_merchant(merchant, api_token)` — lists
   `GET /v3/merchants/{mId}/shifts?filter=outTime is null&expand=employee`
   (added v4.2.22, for drivers with no `employee_id_clover`).
4. then `close_shift(...)` mirrors the punch-out; `outTime` **must be after** the
   Clover shift's `inTime` or Clover returns `400 {"message":"In time cannot be
   after out time"}` and status becomes `pending` (partner sent a bad `shift_end`).

## Debugging "clover_shift_id is null"

On `i-0f9a6ec659e6aab83` (`tapease-postgres`, db `tapease`):

```sql
-- driver identity for the terminal
SELECT u.user_id, u.email, u.employee_id_clover,
       d.serial_number, d.merchant_id_clover, LEFT(d.clover_token,13) AS token
FROM trans_devices d
JOIN trans_device_users tdu ON tdu.device_id = d.device_id AND tdu.status = 1
JOIN auth_users u ON u.user_id = tdu.user_id
WHERE d.serial_number = '<SERIAL>';

-- what actually happened on the shift
SELECT local_shift_id, status, clover_shift_id, clover_sync_status,
       LEFT(clover_sync_error,180)
FROM trans_driver_shifts WHERE local_shift_id = '<LOCAL_SHIFT_ID>';
```

Backend reasoning (do NOT `docker logs` — see below):
```
docker exec tapease-backend sh -c \
  "tail -n 4000 /app/app/log/*DEV*BACKEND.log | grep -i 'clover'"
```
Key lines: `app.services.clover_shift_client - INFO - Clover API token not
configured; skipping ...` (no token), `... WARNING - Clover close shift returned
HTTP 400 ...` (bad time window / bad merchant/employee).

Smoke test (M2M key = Shoaib POS staging key, `X-API-Key` or `Authorization: Bearer`):
```bash
K=tp_test_m2m_7b6b8b0e_<secret>
docker exec tapease-backend curl -s -X POST http://127.0.0.1:8000/v1/pos/shifts/start \
  -H "X-API-Key: $K" -H "Content-Type: application/json" \
  -d '{"serial_number":"C046AG61420023","local_shift_id":"SMOKE-1","start_time":"<90 min ago, ISO8601>"}'
# then /v1/pos/shifts/close with shift_end = now (after start_time)
```
Delete `SMOKE-*` / `E2E-*` rows from `trans_driver_shifts` + `trans_payouts`
afterwards; a stray `open` shift on the terminal makes the next real start
idempotent-return.

## Environment gotchas

- `portal/clover-sync/dev` secret: the **dev instance role cannot read it**
  (`secretsmanager:DescribeSecret`/`GetSecretValue` denied). `portal/clover-sync/prod`
  is readable (it holds `DATABASE_URL`, via `AWS_SECRET_NAME`). This is why the
  global-token path is dead on dev and the **per-device `clover_token` is the
  working path**.
- `CLOVER_BASE_URL` is **not** set as a container env var on dev → the client
  defaults to `sandbox.dev.clover.com` for non-production. Merchant `GRW1F281F36K1`
  takes real payments, so its shift API is on `api.clover.com`. If a real token is
  in `trans_devices.clover_token`, also set `CLOVER_BASE_URL=https://api.clover.com`
  in the container env, or the client will hit sandbox and 401.
- `app/integrations/clover.py` is a **stub** (placeholder URL) — the real Clover
  payment data is *pushed to us by the device*, not fetched. There is no shared
  token there to borrow.

## Seed / fixtures

`scripts/pos_partner_fixtures.py` holds the canonical values:
`CLOVER_MERCHANT_ID`, `HH_SIDDIQUI_CLOVER_EMPLOYEE_ID` (`C6F2AWPMAPMM8`),
`CLOVER_DEVICE_TOKEN`. `scripts/seed_dev_data.py` writes `clover_token` on every
`GRW1F281F36K1` device and backfills `DEV-EMP-<user_id>` for any driver on a
merchant device with no `employee_id_clover`. `scripts/_apply_pos_partner_fixtures.sql`
is the idempotent staging apply (not run by the deploy script — apply it manually).
