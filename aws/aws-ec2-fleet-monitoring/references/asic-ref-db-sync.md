# ASIC / Reference DB Sync — Pluto as Hivey

## Overview
Daily sync of reference datasets (ASIC companies, business names, registered schemes, ACNC charities) into the backend SQLite `/data/ref.db` on EBS. Pluto acts as a **Hivey named agent** — it only makes HTTP POST calls; it never downloads CSVs, SSHs to EC2, or writes storage directly.

## Schedule
- **Time:** 03:30 Australia/Sydney daily
- **Cron:** `30 3 * * *` with `CRON_TZ=Australia/Sydney`
- **Script:** `amlhive_asic_sync.py`
- **Job ID:** (to be created)

## API Contract
**Endpoint:** `POST https://api.amlhive.com.au/internal/sync/{dataset}`  
**Auth:** Bearer token — `INTERNAL_SYNC_API_KEY` from `.env`  
**Health check first:** `GET /health` — abort + alert if down  
**Call order** (sequential, not parallel):
1. `asic-companies` — 900s timeout
2. `asic-business-names` — 900s timeout
3. `asic-registered-schemes` — 120s timeout
4. `acnc-charities` — 120s timeout

## Success Responses
```json
{"dataset":"asic-companies","rows_synced":3412847,"sync_at":"...","skipped":false,"reason":null}
{"dataset":"asic-companies","rows_synced":0,"sync_at":"...","skipped":true,"reason":"NO_CHANGE"}
```
Treat HTTP 200 with `skipped: true` as SUCCESS — no alert.

## Error Handling
| HTTP Status | Action |
|-------------|--------|
| 200 (skipped=false) | ✅ Success — log row count |
| 200 (skipped=true) | ✅ Success — no change |
| 304 | ✅ No change — skip |
| 503 | Retry up to 2× with exponential backoff |
| 401, 422 | ❌ Never retry — permanent error |
| Other non-200 | ❌ Alert |
| Timeout | ❌ Alert |

## Critical Rules
- Never print or commit the API key
- Never download CSVs or write EBS/RDS/S3/R2 directly
- Every outcome is audited as Hivey by the API
- The backend performs change detection (HEADs data.gov.au, skips when fingerprint unchanged)
