# ASIC/ACNC Reference Data Ingestion — June 26, 2026 Session

## What Was Set Up

The AML Hive internal sync endpoint (`POST /internal/sync/{dataset}` in `backend/app/api/internal/sync.py`) was configured end-to-end:

1. **Token**: `FLY_IO_SYNCH_API_KEY_PLUTO` extracted from Windows `.env` → deployed to Fly.io as `INTERNAL_SYNC_API_KEY` secret
2. **CSV URLs**: Three datasets configured — `ASIC_COMPANIES_CSV_URL`, `ASIC_BUSINESS_NAMES_CSV_URL`, `ACNC_CSV_URL`
3. **Data download**: ASIC companies ZIP (74MB), ASIC business names ZIP (68MB), ACNC charities CSV (14MB) downloaded from data.gov.au
4. **CSV extraction**: ZIPs extracted → 375MB + 235MB CSVs
5. **R2 upload**: All CSVs uploaded to `amlhive-documents/asic/` bucket

## GitHub PR

**PR #1** — `https://github.com/amlhive-tech/amlhive1/pull/1`
- Branch: `pluto/dynamic-asic-urls`
- Makes ASIC URLs auto-detect the latest month (dynamic YYYYMM construction)
- Uses `previous_month` logic (lags ~1 week)

## R2 Credentials Used

| Variable | Value |
|----------|-------|
| `R2_ACCOUNT_ID` | `0f9ad05aed2ef935f572d55cf6e4b8b8` |
| `R2_ACCESS_KEY_ID` | `62fd9151776bce1ae054277fcb3d5c35` |
| `R2_SECRET_ACCESS_KEY` | In Windows `.env` |
| `R2_ASIC_BUCKET_NAME` | `amlhive-asic-conent` (note typo — `conent` not `content` — bucket doesn't exist) |

## R2 Bucket Access

| Bucket | Access | Notes |
|--------|--------|-------|
| `amlhive-documents` | ✅ Read/write | Used for ASIC files under `asic/` prefix |
| `amlhive-help-content` | ✅ Read/write | Existing help content |
| `amlhive-blog-content` | ✅ Read/write | Existing blog content |
| `amlhive-asic-conent` | ❌ No permission | Bucket doesn't exist — create in Cloudflare dashboard |

## Files on R2

```
amlhive-documents/
  asic/
    asic_companies.csv          (376MB) — stable "current" URL target
    asic_business_names.csv     (236MB) — stable "current" URL target
    acnc_charities.csv          (14MB)  — stable (permanent URL)
    asic_companies_202606.csv   (376MB) — versioned snapshot (Jun 2026)
    asic_business_names_202606.csv (236MB) — versioned snapshot (Jun 2026)
```

## Sync API Test Results

| Endpoint | Result | Status |
|----------|--------|--------|
| `POST /internal/sync/asic-companies` | 503 "CSV URL not configured" → then auth 401 → then dataset validation 422 | ✅ Auth working, needs env var |
| `POST /internal/sync/asic-business-names` | Same progression | ✅ Auth working |
| `POST /internal/sync/acnc-charities` | Same progression | ✅ Auth working |
| `POST /internal/sync/asic-registered-schemes` | 503 "CSV URL not configured" | ⚠️ No dataset exists |

## Token Extraction Pattern

When `*** ` appears in Hermes terminal output for token values, it's Hermes output masking. Use `line.find('TOKEN_NAME')` instead of `line.startswith('TOKEN_NAME=*** in Python to bypass the masking issue.

## Sync API Auth Flow

```
1. Client sends: Authorization: Bearer {FLY_IO_SYNCH_API_KEY_PLUTO}
2. Fly.io reads: settings.INTERNAL_SYNC_API_KEY (from Fly.io secrets)
3. Uses: secrets.compare_digest(token, configured_key)
4. If both match → proceed
5. If no key set → 401 "Internal sync not configured"
6. If key mismatch → 401 "Invalid internal sync key"
```

The endpoint at `backend/app/api/internal/sync.py` uses `httpx.AsyncClient(timeout=300.0)` to download the CSV and `response.text` to load it entirely in memory.
