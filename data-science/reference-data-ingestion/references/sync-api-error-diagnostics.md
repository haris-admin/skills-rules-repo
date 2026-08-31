# Sync API Error Diagnostics

Response patterns observed when calling `POST /internal/sync/{dataset}` on the Fly.io app `amlhive-api`.

## HTTP Status → Diagnosis

| Status | Response Body | Diagnosis | Next Step |
|--------|-------------|-----------|-----------|
| **200** | `{"dataset":"...","rows_synced":N,"sync_at":"..."}` | ✅ Success | Verify row count is reasonable. |
| **401** | `"Missing or invalid Authorization header"` | Wrong auth scheme — must use **Bearer** not x-api-key | Check: `Authorization: Bearer <TOKEN>` |
| **401** | `"Invalid internal sync key"` | Token value mismatch | Check `INTERNAL_SYNC_API_KEY` secret matches the `FLY_IO_SYNCH_API_KEY_PLUTO` token |
| **401** | `"Internal sync not configured"` | `INTERNAL_SYNC_API_KEY` env var not set on Fly.io | `flyctl secrets set INTERNAL_SYNC_API_KEY=... -a amlhive-api` |
| **404** | `{"detail":"Not Found"}` | Wrong URL path | Check: path must be `/internal/sync/{dataset}`, not `/api/v1/internal/sync/...` |
| **502** | **Empty body** or proxy error | 🚨 OOM kill — uvicorn process was terminated | See OOM diagnostic below |
| **503** | `"CSV URL for {dataset} is not configured"` | `*_CSV_URL` env var is empty or unset | Set the URL via `flyctl secrets set` |
| **503** | `"Could not fetch {dataset} CSV from data.gov.au: ..."` | data.gov.au unreachable or URL is wrong | Check the URL manually via curl, verify YYYYMM in filename |
| **503** | `"asic-business-names requires REF_DB_PATH to be configured"` | SQLite volume not set up | Configure `REF_DB_PATH` env var pointing to a Fly.io volume |

## OOM Kill Diagnostic (502 with empty body)

**Log signature:**
```
Out of memory: Killed process <PID> (uvicorn) total-vm:1.2-1.4GB, anon-rss:~681MB, ...
error.message="could not complete HTTP request to instance: legacy hyper error: client error
  (SendRequest), caused by: connection closed before message completed"
```

**Check command:**
```bash
flyctl logs -a amlhive-api -n | grep -i "out of memory\|Killed process"
```

**Machine spec:** `shared-cpu-2x:1024MB` (1GB RAM)

**Why 502 and not something clearer:** The Fly.io proxy sees the connection close mid-request (because the kernel's OOM killer terminated the process without HTTP cleanup). The proxy has no error body to forward, so it returns a generic 502. The app then auto-restarts within ~1 second.

**Fix:** Scale the machine to 2048MB:
```bash
flyctl machine update e820901c374338 --memory 2048 -a amlhive-api
```

Also documented in the `reference-data-ingestion` skill under **Pitfalls → OOM-kill on sync**.

## Test Results (Jun 26, 2026)

| Dataset | File Size | Auth | Response | Result |
|---------|-----------|------|----------|--------|
| `asic-companies` | 375 MB | Bearer token ✅ | 502 (OOM) | ❌ Process killed |
| `acnc-charities` | 14 MB | Bearer token ✅ | 502 (OOM) | ❌ Process killed |
| `asic-business-names` | 236 MB | Not tested | Expected 502 | ❌ Would also OOM |
| `asic-registered-schemes` | N/A | Not tested | Expected 503 | ❌ No dataset exists |

Auth is confirmed working — the endpoint correctly authenticated the `FLY_IO_SYNCH_API_KEY_PLUTO` token. The 502 is purely a memory issue, not an auth failure.
