# AML Hive Internal Sync API

## Overview

The amlhive-api Fly.io app exposes sync endpoints discovered via `/openapi.json`:

| Endpoint | Method | Purpose |
|----------|--------|---------|
| /internal/sync/{dataset} | POST | Trigger a reference dataset sync (Hermes bridge) |
| /api/v1/kyc/asic/sync | POST | Sync ASIC data (KYC pipeline) |

The OpenAPI description says: *Download the specified dataset CSV from data.gov.au and upsert / full-refresh the corresponding Supabase table.* Called weekly by Hermes cron.

## Authentication

- **Client token** (`FLY_IO_SYNCH_API_KEY_PLUTO` in .env): 64-char hex bearer token
- **Server secret**: Set as `INTERNAL_SYNC_API_KEY` in Fly.io secrets
- **Status (Jun 26 2026)**: Both client token AND server secret are deployed.

## Data.gov.au CSV URLs — Discovered Jun 26 2026

All URLs verified HTTP 200. UUIDs are **permanent** — they do NOT change between data refreshes.

### ASIC Companies Register
- **Dataset page:** https://www.data.gov.au/data/dataset/asic-companies
- **Update freq:** Weekly (Tuesday), since Aug 2018  
- **File:** CSV (~394 MB) or ZIP (~78 MB)
- **Permanent UUIDs:**
  - Dataset: `7b8656f9-606d-4337-af29-66b89b2eeefb`
  - Resource (CSV): `5c3914e6-413e-4a2c-b890-bf8efe3eabf2`
  - Resource (ZIP): `d6d03876-71a4-4e82-8c77-2e4df5da4236`
- **URL template:** `https://data.gov.au/data/dataset/{UUID}/resource/{UUID}/download/company_{YYYYMM}.csv`
- **Filename changes monthly** — `company_202606.csv` -> `company_202607.csv`

### ASIC Business Names Register
- **Dataset page:** https://www.data.gov.au/data/dataset/asic-business-names
- **Update freq:** Weekly (Wednesday), since Oct 2018
- **File:** CSV (~247 MB) or ZIP (~71 MB)
- **Permanent UUIDs:**
  - Dataset: `bc515135-4bb6-4d50-957a-3713709a76d3`
  - Resource (CSV): `55ad4b1c-5eeb-44ea-8b29-d410da431be3`
  - Resource (ZIP): `45eddcf9-07c1-4c5c-a1aa-ff109a033977`
- **URL template:** `https://data.gov.au/data/dataset/{UUID}/resource/{UUID}/download/business_names_{YYYYMM}.csv`
- **Filename changes monthly**

### ASIC Registered Schemes — NO BULK DATASET EXISTS
No publicly available bulk data exists. The endpoint option exists but no data.gov.au source. Keep the env var but it will never have a valid URL.

### ACNC Charity Register — PERMANENT STATIC URL
- **Dataset page:** https://www.data.gov.au/data/dataset/acnc-register
- **Update freq:** Weekly
- **File:** CSV (~15 MB) or XLSX (~8.9 MB)
- **Permanent UUIDs:**
  - Dataset: `b050b242-4487-4306-abf5-07ca073e5594`
  - Resource (CSV): `8fb32972-24e9-4c95-885e-7140be51be8a`
- **URL:** `https://data.gov.au/data/dataset/b050b242-4487-4306-abf5-07ca073e5594/resource/8fb32972-24e9-4c95-885e-7140be51be8a/download/datadotgov_main.csv`
- **Filename NEVER changes** — `datadotgov_main.csv` is overwritten weekly

## Monthly URL Rotation — The Critical Gotcha

ASIC filenames include `{YYYYMM}` — they change each month. ACNC URL is permanent.

### Solution: Dynamic URL Construction (PR #1)

**PR:** https://github.com/amlhive-tech/amlhive1/pull/1
**Branch:** `pluto/dynamic-asic-urls`
**Status:** Open, awaiting review/deploy (Jun 26 2026)

The PR hardcodes the permanent UUIDs in `sync.py` and computes `YYYYMM` from the **previous month** (data lags ~1 week):

```python
_ASIC_DATA_URLS = {
    "asic-companies": {
        "dataset_uuid": "7b8656f9-...",
        "resource_uuid": "5c3914e6-...",
        "file_prefix": "company_",
    },
    "asic-business-names": {
        "dataset_uuid": "bc515135-...",
        "resource_uuid": "55ad4b1c-...",
        "file_prefix": "business_names_",
    },
}

def _build_asic_csv_url(dataset):
    tmpl = _ASIC_DATA_URLS.get(dataset)
    if not tmpl:
        return ""
    now = datetime.now(timezone.utc)
    prev = now.replace(day=1) - timedelta(days=1)  # previous month
    yyyymm = prev.strftime("%Y%m")
    return (f"https://data.gov.au/data/dataset/{tmpl['dataset_uuid']}"
            f"/resource/{tmpl['resource_uuid']}"
            f"/download/{tmpl['file_prefix']}{yyyymm}.csv")
```

After this PR is deployed, `ASIC_COMPANIES_CSV_URL` and `ASIC_BUSINESS_NAMES_CSV_URL` become **optional**.

## How to Enable

```bash
# ACNC URL (static, always needed):
flyctl secrets set ACNC_CHARITIES_CSV_URL="https://data.gov.au/data/dataset/b050b242-4487-4306-abf5-07ca073e5594/resource/8fb32972-24e9-4c95-885e-7140be51be8a/download/datadotgov_main.csv" -a amlhive-api

# Trigger a sync:
curl -X POST https://amlhive-api.fly.dev/internal/sync/asic-companies \
  -H "Authorization: Bearer $(grep FLY_IO_SYNCH_API_KEY_PLUTO ~/.hermes/.env | cut -d= -f2-)" \
  -H "Content-Type: application/json"
```

Expected: `{"dataset": "asic-companies", "rows_synced": ..., "sync_at": "..."}`

## GitHub Repo Access

Use the **`GITHUB_PAT_CLASSIC_AMLHIVE_AGENT`** token (NOT `GITHUB_PAT`) — the `haris-a2squre` PAT cannot access `amlhive-tech` repos. The agent PAT IS stored in Windows .env.

Key source files:
- `backend/app/api/internal/sync.py` — sync endpoint handler
- `backend/app/core/config.py` — Settings class with env var definitions
- `backend/scripts/sync_asic_api.py` — legacy hardcoded-URL script

## Pitfalls

- **Token name has SYNCH not SYNC** — grep for `FLY_IO_SYNCH_API_KEY_PLUTO`
- Token is 64 hex chars (SHA-256 digest) — no `fm2_` or `sntryu_` prefix
- Internal sync returns HTTP **503** for not configured (not 401). 503 = auth passed, dataset valid, but CSV URL secret not set
- Setting secrets triggers automatic deploy — shows as Staged until complete
- data.gov.au CKAN JSON API returns 404 (migrated to Drupal). Use dataset pages or pre-discovered UUIDs
- Config setting `ACNC_CSV_URL` (no CHARITIES_ infix) in config.py — matches the settings field name
- `asic-registered-schemes` does NOT exist on data.gov.au — always returns 503
- data.gov.au API search is broken from WSL — don't rely on it for URL discovery