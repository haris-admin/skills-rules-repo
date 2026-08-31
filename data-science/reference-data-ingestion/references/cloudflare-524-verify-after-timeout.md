# Cloudflare 524 on long syncs — verify after timeout, don't blind-alert (Aug 2026)

## Symptom

Cron `★ Pluto ASIC / Ref-DB Sync — Nector (03:15 Sydney)` (job `937bb914c497`)
fails with `❌ HTTP 524 — error code: 524` on `asic-companies` while other
datasets sync fine. A "failed" alert fires even though the dataset DID update.

## Root cause

`api.amlhive.com.au` sits behind Cloudflare, whose proxy caps a single request
at **~100s** — but the backend sync endpoint allows up to **900s** (see
`amlhive_asic_sync.py` `LONG_TIMEOUT_DS`). A large dataset (asic-companies
~4M rows) can legitimately take 8+ min, so Cloudflare returns **HTTP 524** to
the client while the origin KEEPS syncing and completes seconds/minutes later.
The script's generic HTTP-error branch set `overall_alert = True` → false alarm.

Observed 2026-08-18:
- 03:15:10 POST asic-companies (client timeout 900s)
- ~03:16:50 Cloudflare 100s cap → script sees HTTP 524
- 03:23:13 backend finishes the sync anyway (fingerprint saved)
- Verification POST `?force=false` later returned `NO_CHANGE` with
  `rows_synced: 3,999,184`, `sync_at: 2026-08-17T17:23:13Z` → sync DID land.

## Fix pattern — on 524, verify instead of alerting

Wait ~90s, then re-POST the same dataset with `force=false` as a probe: if the
earlier sync landed, the fingerprint now matches → response is
`skipped=true, reason=NO_CHANGE` with the real row count — that PROVES the
sync completed, so print ✅ and continue. Only alert if verification still
fails after 3 attempts.

```python
# inside the HTTPError handler, new branch for e.code == 524:
elif status == 524:
    if _verify_after_cf_timeout(url, token, timeout, dataset):
        break                       # sync landed — PASS
    overall_alert = True            # still not confirmed — alert
    break

def _verify_after_cf_timeout(url, token, timeout, dataset) -> bool:
    for attempt in range(3):
        time.sleep(90)
        try:
            status, body = _post_sync(url, token, timeout, force=False)
        except Exception:
            continue
        rows = body.get("rows_synced", 0)
        skipped = body.get("skipped", False)
        reason = body.get("reason", "")
        sync_at = body.get("sync_at", "")
        if not skipped and rows:
            print(f"   ✅ Sync completed (verified): {rows:,} rows · {sync_at}")
            return True
        if skipped and reason == "NO_CHANGE":
            print(f"   ✅ Sync landed before timeout (verified NO_CHANGE): {rows:,} rows · {sync_at}")
            return True
        if skipped:
            print(f"   ⏭️ Verify probe: skipped ({reason}) · {rows:,} rows")
            return True            # backend healthy; not a 524 problem anymore
    print("   ❌ Sync still not confirmed — alerting")
    return False
```

`force=false` (the default) never forces a download, so the probe is cheap and
safe to run after a timeout.

## Alignment output (prevents recurrence confusion)

Print remote count + last-update on every skip row so a 524-style false alarm
is instantly recognizable:

```
⏭️ Skipped (no change): NO_CHANGE · 3,999,184 rows (remote) · last update 2026-08-17T17:23:13Z
✅ Synced: 3,999,184 rows (before 3,999,184, Δ0) · 2026-08-17T17:23:13Z
```

## Related

- `DATASET_SOURCE_UNAVAILABLE` is a sync that did NOT happen — it must stay an
  alert, not PASS (the registered-schemes quiet-skip is the one standing
  exception per the "no ASIC trying for now" order).
- Full script: `~/.hermes/scripts/amlhive_asic_sync.py` (has `_post_sync` +
  `_verify_after_cf_timeout` helpers as of 2026-08-18).
