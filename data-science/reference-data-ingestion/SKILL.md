---
name: reference-data-ingestion
description: "Australian government reference data ingestion — ASIC (companies, business names), ACNC (charities), ABN Lookup. Weekly/monthly CSV sync from data.gov.au to R2 storage, then via Hermes sync bridge into Supabase/ref_db. Covers URL management, R2 uploads, verification, and versioning."
version: 1.1.0
author: Pluto
license: MIT
category: data-science
platforms: [linux, macos, wsl]
metadata:
  hermes:
    tags: [ASIC, ACNC, data.gov.au, R2, reference-data, sync, Australian-government]
    related_skills: [pluto-fleet-monitor, pluto-pipeline-orchestration, sentry-setup]
---

# Reference Data Ingestion

## When to Use

- Setting up or troubleshooting the ASIC/ACNC reference data sync pipeline
- Uploading new monthly CSV dumps to R2 storage
- Debugging sync API failures (`POST /internal/sync/{dataset}`)
- Onboarding a new government dataset (ABN, ASIC registered schemes, etc.)
- Checking or updating R2 bucket contents for reference data files

## Datasets

| Dataset | Source | URL Pattern | Update Frequency | Size |
|---------|--------|------------|-----------------|------|
| **ASIC Companies** | data.gov.au | `company_{YYYYMM}.csv` — **monthly filename** | Weekly (Tuesdays) | ~375MB CSV / ~74MB ZIP |
| **ASIC Business Names** | data.gov.au | `business_names_{YYYYMM}.csv` — **monthly filename** | Weekly (Wednesdays) | ~235MB CSV / ~68MB ZIP |
| **ACNC Charities** | data.gov.au | `datadotgov_main.csv` — **permanent filename** | Weekly | ~14MB CSV |
| **ASIC Registered Schemes** | N/A | **No public bulk dataset exists** on data.gov.au | N/A | N/A |

## URL Architecture

### Permanent UUIDs (never change)

The data.gov.au resource and dataset UUIDs are **permanent identifiers** — only the filename date stamp changes each month:

| Dataset | Dataset UUID | Resource UUID (CSV) | Resource UUID (ZIP) |
|---------|-------------|---------------------|---------------------|
| ASIC Companies | `7b8656f9-606d-4337-af29-66b89b2eeefb` | `5c3914e6-413e-4a2c-b890-bf8efe3eabf2` | `d6d03876-71a4-4e82-8c77-2e4df5da4236` |
| ASIC Business Names | `bc515135-4bb6-4d50-957a-3713709a76d3` | `55ad4b1c-5eeb-44ea-8b29-d410da431be3` | `45eddcf9-07c1-4c5c-a1aa-ff109a033977` |
| ACNC Charities | `b050b242-4487-4306-abf5-07ca073e5594` | `8fb32972-24e9-4c95-885e-7140be51be8a` | N/A |

### CSV Download URL Format

```
https://data.gov.au/data/dataset/{DATASET_UUID}/resource/{RESOURCE_UUID}/download/{FILENAME}
```

### Dynamic URL Generation

For ASIC datasets, URLs must be constructed dynamically because the filename changes monthly. The current month's data lags by ~1 week, so use **previous month**:

```python
from datetime import datetime, timezone, timedelta

now = datetime.now(timezone.utc)
first_of_month = now.replace(day=1)
prev = first_of_month - timedelta(days=1)
yyyymm = prev.strftime("%Y%m")  # e.g. "202606"

url = (f"https://data.gov.au/data/dataset/{DATASET_UUID}"
       f"/resource/{RESOURCE_UUID}"
       f"/download/{PREFIX}{yyyymm}.csv")
```

ACNC uses a permanent filename (`datadotgov_main.csv`) — no date logic needed.

## Sync API — `POST /internal/sync/{dataset}`

### Endpoint
```
POST https://amlhive-api.fly.dev/internal/sync/{dataset}
Authorization: Bearer {INTERNAL_SYNC_API_KEY}
Content-Type: application/json
```

### Valid Datasets
| Dataset | Backend Path | Default Data Source |
|---------|-------------|-------------------|
| `asic-companies` | → `ref_db.sync_companies_from_csv()` or `asic_service.sync_bulk_companies()` | Data.gov.au or R2 URL in `ASIC_COMPANIES_CSV_URL` env var |
| `asic-business-names` | → `ref_db.sync_business_names_from_csv()` | Data.gov.au or R2 URL in `ASIC_BUSINESS_NAMES_CSV_URL` env var |
| `acnc-charities` | → `acnc_service.sync_from_csv_content()` | Data.gov.au or R2 URL in `ACNC_CSV_URL` env var |
| `asic-registered-schemes` | → `asic_service.sync_bulk_registered_schemes()` | No bulk dataset exists — will 503 |

### Env Vars Required
| Env Var | Status (Jun 27, 2026 — RESOLVED) |
|---------|----------------------|
| `INTERNAL_SYNC_API_KEY` | ✅ Deployed |
| `ASIC_COMPANIES_CSV_URL` | ✅ Deployed (points to data.gov.au Jun 2026 CSV) |
| `ASIC_BUSINESS_NAMES_CSV_URL` | ✅ Deployed (points to data.gov.au Jun 2026 CSV) |
| `ACNC_CSV_URL` | ✅ Deployed (points to permanent data.gov.au CSV) |
| `ASIC_REGISTERED_SCHEMES_CSV_URL` | Will 503 — no dataset exists |

### Auth Flow
```
Client sends: Authorization: Bearer {PLUTO_SYNC_TOKEN}
Fly.io app compares against: INTERNAL_SYNC_API_KEY secret
Uses: secrets.compare_digest() — timing-safe comparison
Returns: 401 "Internal sync not configured" if key not set
         401 "Invalid internal sync key" if mismatch
         503 "CSV URL not configured" if env var empty
         200 {dataset, rows_synced, sync_at} on success
```

> 💡 See `references/sync-api-error-diagnostics.md` for a complete HTTP status → diagnosis table with observed test results from Jun 26, 2026, including the OOM kill diagnostic path.

## Data Pipeline: data.gov.au → R2 → Sync API

### Step 1 — Download from data.gov.au
```bash
mkdir -p ~/data/asic_sync && cd ~/data/asic_sync

# ASIC Companies ZIP (contains CSV inside)
curl -L -o asic_companies.zip \
  "https://data.gov.au/data/dataset/7b8656f9-606d-4337-af29-66b89b2eeefb/resource/d6d03876-71a4-4e82-8c77-2e4df5da4236/download/company_202606.zip"

# ASIC Business Names ZIP
curl -L -o asic_business_names.zip \
  "https://data.gov.au/data/dataset/bc515135-4bb6-4d50-957a-3713709a76d3/resource/45eddcf9-07c1-4c5c-a1aa-ff109a033977/download/business_names_202606.zip"

# ACNC Charities CSV (permanent URL — no date stamp)
curl -L -o acnc_charities.csv \
  "https://data.gov.au/data/dataset/b050b242-4487-4306-abf5-07ca073e5594/resource/8fb32972-24e9-4c95-885e-7140be51be8a/download/datadotgov_main.csv"
```

### Step 2 — Extract CSVs from ZIPs
```python
import zipfile
with zipfile.ZipFile('asic_companies.zip') as z:
    csv_file = [f for f in z.namelist() if f.endswith('.csv')][0]
    z.extract(csv_file, '.')
    os.rename(csv_file, 'asic_companies.csv')

with zipfile.ZipFile('asic_business_names.zip') as z:
    csv_file = [f for f in z.namelist() if f.endswith('.csv')][0]
    z.extract(csv_file, '.')
    os.rename(csv_file, 'asic_business_names.csv')
```

CSVs inside ZIPs are named `COMPANY_202606.csv` and `BUSINESS_NAMES_202606.csv` (uppercase).

### Step 3 — Upload to R2
```python
import boto3
from botocore.config import Config

s3 = boto3.client(
    's3',
    endpoint_url=f"https://{R2_ACCOUNT_ID}.r2.cloudflarestorage.com",
    aws_access_key_id=R2_ACCESS_KEY_ID,
    aws_secret_access_key=R2_SECRET_ACCESS_KEY,
    config=Config(signature_version='s3v4'),
    region_name='auto',
)

# Upload with BOTH stable and versioned names (Jun 26, 2026 schema)
files = {
    "asic/asic_companies.csv": "asic_companies.csv",           # stable "current"
    "asic/asic_business_names.csv": "asic_business_names.csv",  # stable "current"
    "asic/acnc_charities.csv": "acnc_charities.csv",            # stable (already permanent)
    "asic/asic_companies_202606.csv": "asic_companies.csv",     # versioned snapshot
    "asic/asic_business_names_202606.csv": "asic_business_names.csv",  # versioned snapshot
}

for key, local in files.items():
    s3.upload_file(local_path, "amlhive-documents", key, ExtraArgs={'ContentType': 'text/csv'})
```

### Step 4 — Set Fly.io Env Vars
```bash
# R2 public URLs (if bucket is publicly accessible)
flyctl secrets set \
  ASIC_COMPANIES_CSV_URL="https://pub-{hash}.r2.dev/asic/asic_companies.csv" \
  ASIC_BUSINESS_NAMES_CSV_URL="https://pub-{hash}.r2.dev/asic/asic_business_names.csv" \
  ACNC_CSV_URL="https://pub-{hash}.r2.dev/asic/acnc_charities.csv" \
  -a amlhive-api
```

If the R2 bucket is NOT publicly accessible, use data.gov.au URLs instead (they're stable and the sync endpoint can download from them directly).

### Step 5 — Trigger Sync
```bash
TOKEN=<FLY_IO_SYNCH_API_KEY_PLUTO>
for ds in asic-companies asic-business-names acnc-charities; do
  curl -X POST "https://amlhive-api.fly.dev/internal/sync/$ds" \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d '{}'
done
```

## Versioning Strategy

Keep **two versions** only:
| Label | Filename | Purpose |
|-------|----------|---------|
| **Current** | `asic/asic_companies.csv` | What the sync endpoint fetches by default |
| **Previous** | `asic/asic_companies_202606.csv` | Rollback reference if current data has issues |

When new monthly data arrives:
1. Download latest ZIP from data.gov.au
2. Upload as `asic/asic_companies_{YYYYMM}.csv` (new previous)
3. Re-upload as `asic/asic_companies.csv` (overwrites — new current)
4. Delete the oldest versioned file

## GitHub Code Changes

The internal sync endpoint code lives at `backend/app/api/internal/sync.py` in the `amlhive-tech/amlhive1` repo.

### Key Files
| File | Purpose |
|------|---------|
| `backend/app/api/internal/sync.py` | The `POST /internal/sync/{dataset}` handler + auth + CSV fetching |
| `backend/app/core/config.py` | Env var definitions (`INTERNAL_SYNC_API_KEY`, `*_CSV_URL`) |
| `backend/scripts/sync_asic_api.py` | Legacy script (hardcoded URL — superseded by the internal API) |
| `backend/app/services/reference_data/` | Reference data sync logic directory |

### PR Pattern for URL Changes
When making URL-related changes (dynamic construction, new dataset, etc.):
1. Create branch: `pluto/<feature-name>`
2. Update `sync.py` with the template/builder function
3. Create PR to `main`
4. Reference: PR #1 ("Dynamic ASIC CSV URLs — auto-detect latest month")

## AUSTRAC is NOT part of this pipeline (checked 2026-08-08)

The Ref-DB sync covers **ASIC + ACNC only** — there is NO AUSTRAC ingestion:
no AUSTRAC register, no AUSTRAC reporting-entity list, no postal-address
reference data anywhere in `amlhive_asic_sync.py` or the pipeline. Do not
assume AUSTRAC data exists because the product does AML/CTF — KYB/UBO checks
use ASIC/ABR data. If the user asks "are we ingesting the AUSTRAC list?",
answer NO and explain the ASIC-only scope; options are (a) AUSTRAC public
register scraping, (b) an AUSTRAC API/data agreement, or (c) keep ASIC as the
de-facto KYB source.

### Daily "NO_CHANGE" is normal — but verify freshness

The cron (`937bb914c497`, daily 03:15 Sydney) posts to `/internal/sync/*` and
typically returns `⏭️ Skipped (no change): NO_CHANGE` for every dataset. That
is the backend's CSV-fingerprint short-circuit, NOT a failure. Before
reporting "the data is stale", confirm the env vars actually point at the
latest month's file: data.gov.au publishes monthly (`company_202607.csv` etc.,
~398MB each, ~1 week lag). Check deployed `ASIC_COMPANIES_CSV_URL` /
`ASIC_BUSINESS_NAMES_CSV_URL` (`flyctl secrets list -a amlhive-api`, needs
auth) — if pinned to an old month, the daily NO_CHANGE is hiding a stale
snapshot. CSV HEAD checks on data.gov.au return the same Content-Length across
months (all ~398MB), so size alone does not prove freshness — check the
configured URL month instead.

### 🔴 NO_CHANGE staleness trap — root cause + forced-sync fix (2026-08-08)

**Verified root cause:** the backend's change-detection fingerprint is
`url | etag | last_modified | content_length` (`_compose_fingerprint` in
`backend/app/api/internal/sync.py`). data.gov.au's `/download/{filename}.csv`
endpoint serves the **latest file regardless of the month in the URL** and
returns the **same etag / last-modified / content-length for ALL month
filenames** (verified: `company_202605/202606/202607.csv` all → 397,999,627
bytes, `Last-Modified: Mon, 03 Aug 2026`). So even though
`_build_asic_csv_url()` rolls the month correctly (prev-month logic →
`company_202607.csv` from Aug 1), the fingerprint never changes → NO_CHANGE
forever → **new monthly snapshots are silently never ingested**. Observed: the
last real ASIC-companies ingest was the initial Jul 24 load (3,308,701 rows);
Jul 25–Aug 8 all NO_CHANGE; July/August data never loaded.

**Diagnosis:** scan the cron output dir for repeated NO_CHANGE:
`ls ~/.hermes/cron/output/937bb914c497/` and grep each day's `.md` for
`Synced|Skipped`. The last `✅ Synced: N rows` line = last real ingest.

**Fix (one-time per rollover, or whenever staleness suspected):** trigger a
**forced sync** to bypass the fingerprint check:
```bash
curl -X POST "https://api.amlhive.com.au/internal/sync/asic-companies?force=true" \
  -H "Authorization: Bearer $INTERNAL_SYNC_API_KEY" \
  -H "Content-Type: application/json" -d '{}'
```
Repeat for `asic-business-names` and `acnc-charities`. Companies is a ~400MB
download — allow minutes (backend machine is 4GB, see OOM pitfall). Consider
scheduling a **monthly forced sync** on the ~5th (after ASIC publishes the
previous month's data) so this fingerprint alias can't silently stall the
pipeline again.

## Pluto Cron Sync (C332 ref_db → KYB ABR pre-check)

Since **25 July 2026**, the ASIC/Ref-DB sync runs as a Hermes cron job (the
sync agent is **Nector** — NOT "Hivey"; the Hivey branding was corrected
2026-08-08 in both the cron name and `amlhive_asic_sync.py` User-Agent):

| Detail | Value |
|--------|-------|
| Cron job ID | `937bb914c497` |
| Name | `★ Pluto ASIC / Ref-DB Sync — Nector (03:15 Sydney)` |
| Schedule | `15 3 * * *` AEST (daily 03:15) |
| Script | `amlhive_asic_sync.py` at `~/.hermes/scripts/` |
| Mode | `no_agent: true` |

Datasets: `asic-companies`, `asic-business-names`, `asic-registered-schemes`, `acnc-charities`.

**Status (25 Jul 2026):** `asic-companies` ✅, `asic-business-names` ✅, `acnc-charities` ✅, `asic-registered-schemes` ❌ 503 (no env var — pre-existing).

## Pitfalls

- **ZIP vs CSV**: The internal sync endpoint expects CSV text, not ZIP. Always download and extract the ZIP, then upload the CSV to R2. Do NOT point the env var to the ZIP URL.
- **✅ OOM-kill on sync — RESOLVED (machine at 4GB, Jun 27)**: The sync endpoint loads the entire CSV into memory via `response.text`. The machine was originally `shared-cpu-2x:1024MB` causing OOM on 375MB CSVs. **Confirmed scaled to `shared-cpu-2x:4096MB` (4GB)** — no longer a blocker.

  **Symptoms if it recurs (machine rebuild scenario):**
  1. Trigger sync → `HTTP 502` with empty body
  2. Fly.io logs: `flyctl logs -a amlhive-api -n | grep -i "out of memory\|Killed process"`
  3. App auto-restarts within ~1s

  **Re-fix:**
  ```bash
  flyctl machine list -a amlhive-api  # get machine ID
  flyctl machine update <MACHINE_ID> --memory 4096 -a amlhive-api
  ```
- **Month lag**: ASIC data publishes with ~1 week delay after month-end. July data arrives mid-July. Use `previous_month` logic, not current month.
- **ASIC Registered Schemes**: **No bulk dataset exists** on data.gov.au. The OpenAPI spec includes it (`asic-registered-schemes`) but it will always return 503. Don't attempt to configure it.
- **R2 public access**: The `amlhive-documents` bucket is NOT publicly accessible. Files uploaded there are only accessible via presigned URLs (expire 7 days) or via the Fly.io app using its embedded R2 credentials.
- **R2 credentials scope limitation (critical):** The `R2_ACCESS_KEY_ID` / `R2_SECRET_ACCESS_KEY` from the Windows `.env` are scoped to a specific R2 user and return **AccessDenied on ALL S3 API operations** (ListBuckets, CreateBucket, HeadBucket). They cannot create buckets, list buckets, or check if a bucket exists. To create or manage R2 buckets, use the Cloudflare Dashboard directly or generate a new R2 API token with S3 permissions in Cloudflare Dashboard → R2 → Manage R2 API Tokens.
- `R2_ASIC_BUCKET_NAME=amlhive-asic-conent` — note the typo "conent" (not "content"). This bucket doesn't exist yet and the current API token can't create new buckets. Either create it in Cloudflare dashboard → R2 → Create Bucket, or use `amlhive-documents/asic/` prefix instead (the existing `amlhive-documents` bucket supports upload operations).
- **Dual-location credentials:** R2 credentials live in TWO locations: `C:\Users\habib\.hermes\.env` (Windows) and `~/.hermes/.env` (WSL). They can and do drift — always check BOTH when debugging R2 upload failures. Copy with `cat /mnt/c/Users/habib/.hermes/.env | grep "^R2_" >> ~/.hermes/.env`.
- `*** ` prefix in token extraction

## Setting up a new dataset (checklist)

When onboarding a new government dataset to the sync pipeline:

1. Confirm bulk CSV/ZIP export exists from the source agency
2. Record the data.gov.au Dataset UUID + Resource UUID(s)
3. Add a row to the Datasets table in this skill
4. Add the env var name to fly.io secrets
5. Add an entry to the Sync API docs (Valid Datasets table + backend path)
6. Add sync logic to `backend/app/api/internal/sync.py` (or the appropriate service)
7. Add the dataset name to the Trigger Sync bash loop
8. Deploy to Fly.io
