# AML Hive Sync API Pipeline Stage (Configuring — env vars set Jun 26)

The AML Hive internal sync API (`POST /internal/sync/{dataset}`) is designed to be called **weekly by Hermes cron** according to its OpenAPI specification. Once CSV URLs are deployed on Fly.io and the underlying data is uploaded to a publicly accessible URL (R2 or data.gov.au), a weekly cron can trigger dataset refreshes.

*Note on drift:* this section was documented twice in the original skill with two slightly different env-var tables (one calling the ACNC var `ACNC_CSV_URL`, the other `ACNC_CHARITIES_CSV_URL`) and two different confidence levels (one says 3 CSV URLs are already set, the other says the API isn't configured and returns 503). Both versions are kept below rather than silently resolved — verify the actual Fly.io secret name and live API status before relying on either.

## Datasets Ready for Sync

| Dataset | Env Var | Status |
|---------|---------|--------|
| `asic-companies` | `ASIC_COMPANIES_CSV_URL` | ✅ Set (data.gov.au Jun 2026) |
| `asic-business-names` | `ASIC_BUSINESS_NAMES_CSV_URL` | ✅ Set (data.gov.au Jun 2026) |
| `acnc-charities` | `ACNC_CSV_URL` (also documented elsewhere as `ACNC_CHARITIES_CSV_URL` — confirm actual secret name) | ✅ Set (permanent URL) |
| `asic-registered-schemes` | `ASIC_REGISTERED_SCHEMES_CSV_URL` | ⚠️ No bulk dataset exists |

All four datasets sync weekly once configured.

## Auth

Bearer token from `FLY_IO_SYNCH_API_KEY_PLUTO` in `.env` → `INTERNAL_SYNC_API_KEY` deployed on Fly.io (documented elsewhere as "already deployed").

## Suggested Schedule

Sunday 4:00 AM AEST (before the Sunday Adversarial Pulse) — gives a 2h buffer for sync completion.

## Data Pipeline (manual monthly refresh)

Files are downloaded from data.gov.au → extracted from ZIP → uploaded to `amlhive-documents/asic/` on R2. See `reference-data-ingestion` skill for the full procedure.

## Pitfalls

- Sync loads the entire CSV into memory (375MB → ~512MB+ RAM on a 1024MB Fly.io machine)
- CSV URLs currently point to data.gov.au — if data.gov.au breaks access, switch to R2 presigned URLs or make the bucket public
- The `amlhive-asic-conent` bucket doesn't exist (typo in name) — use `amlhive-documents/asic/` prefix instead
- The sync API may not yet be configured (no `CSV_URL` secrets set) — calling it in that state returns 503
- Each sync may take several minutes (large CSVs: ASIC companies = ~2.8M rows)
- See `pluto-fleet-monitor/references/sync-api-setup.md` for full setup instructions
