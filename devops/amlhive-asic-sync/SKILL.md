---
name: amlhive-asic-sync
description: Use when running/debugging the AML Hive ASIC/ref-DB sync.
allowed-tools: [terminal, read_file]
---

# AML Hive ASIC / Ref-DB Sync

Pluto's named agent ("Nector") that keeps AML Hive's `ref_db` in sync with
Australian government reference data via the internal sync API.

## When to Use
- Running or debugging the daily ASIC/Ref-DB sync cron (`937bb914c497`, 03:15 Australia/Sydney)
- Diagnosing `HTTP 524` / `503` / `401` / `422` sync failures
- Understanding why `asic-registered-schemes` is skipped
- Adding a new dataset to the sync roster

## What It Does

`~/.hermes/scripts/amlhive_asic_sync.py` POSTs to
`https://api.amlhive.com.au/internal/sync/{dataset}` for 4 datasets:

| Dataset | Timeout | Notes |
|---------|---------|-------|
| `asic-companies` | 900s | long (multi-million rows) |
| `asic-business-names` | 900s | long |
| `asic-registered-schemes` | 120s | **intentionally unavailable** (see standing order) |
| `acnc-charities` | 120s | permanent URL |

Auth: `Bearer INTERNAL_SYNC_API_KEY`, read from `.env` (checks
`/mnt/c/Users/habib/.hermes/.env` first, then `~/.hermes/.env`).

## Standing Order — "no ASIC trying for now"

`asic-registered-schemes` has no bulk CSV source (no public dataset exists). Per
Haris's standing order, this dataset is **intentionally skipped**. The script
treats `DATASET_SOURCE_UNAVAILABLE` on `asic-registered-schemes` as a **quiet
skip with exit 0** — NOT an alert. Any *other* dataset returning
`DATASET_SOURCE_UNAVAILABLE` sets `overall_alert = True` (exit 1).

Do NOT "fix" this by adding a source — there isn't one, and Haris explicitly
paused ASIC work. See `reference-data-ingestion` skill for the CSV source path.

## Cloudflare 524 Handling (the tricky bit)

Cloudflare caps request duration at ~100s, but the backend allows up to 900s for
the long datasets. A `HTTP 524` does NOT mean the sync failed — the origin may
still be syncing. `_verify_after_cf_timeout()` handles this:

1. On 524, wait 90s, then re-POST with `force=false`
2. `NO_CHANGE` response (fingerprint already updated) = the earlier sync landed → ✅
3. **Long datasets (asic-companies, asic-business-names): 8 verify attempts
   (~12 min)** — the full asic-companies sync takes 10-15 min (3.9M rows into
   ref.db), so a fixed 3x90s window gives up BEFORE the sync can finish (Aug
   2026 OOM-era failures). Short datasets keep 3x90s.
4. Alert if still inconclusive after max attempts

## OOM Root Cause (Aug 2026 — asic-companies nightly 502/524 failures)

**Symptom:** `asic-companies` failed 3 nights in a row: `HTTP 502` (attempt 1) or
`524` + verify attempts failing 502/524.

**Root cause:** the full asic-companies sync (remote CSV changed → download 399MB
CSV → backup 1.4GB ref.db → stream 3.9M rows into SQLite with 700MB+ WAL, holding
`BEGIN IMMEDIATE` for 10-15 min) exceeds the t3.medium's **3.8GB RAM (no swap, no
container memory limit — `Memory=0`)**. The kernel OOM-kills the python worker
(dmesg: 2.8-3.0GB RSS kills at 03:19-03:27 AEST). Cloudflare sees the dead origin
→ 502/524. The interrupted sync leaves `ref.db` LOCKED and the fingerprint
UNCHANGED → every subsequent probe re-triggers the full sync → infinite loop.

**Detection:**
- `dmesg -T | grep -i oom` on the backend instance (IAM_MONITOR creds)
- `docker events` — `oom` event on the app container
- CloudWatch `/amlhive/backend` — `500 database is locked` + slow POST times
- Container RSS: `docker top <cid> -o pid,rss,comm` — one worker at 2.4GB+
- `ref.db-wal` growing to 600MB+ while `ref.db` is locked

**Script-side mitigations applied (Aug 28):** `502` now retries like `503`
(transient origin restart); 524-verify window extended to 8x90s for long datasets.

**Real fix (backend/infra, main-agent scope):** sync is too memory-hungry for
t3.medium — chunk the upsert, add swap/memory limit, or resize the instance.

## ACNC NO_CHANGE skip — VERDICT (Codex investigation, 31 Aug 2026)

**Symptom:** acnc-charities shows `Skipped (no change): NO_CHANGE · 65,589 rows · last
update 2026-08-24` for a week (24→31 Aug). User asked "why is ACNC skipped?"

**Verdict: skip was CORRECT; no fingerprint bug for this case.**
- Remote file changed 2026-08-30 19:02:40 UTC = 31 Aug 05:02:40 AEST — **1h46m AFTER**
  the 03:15 AEST cron probe. At probe time the old etag was still live → NO_CHANGE expected.
- `synced_at` staying at 24 Aug is BY DESIGN: NO_CHANGE returns the stored timestamp
  (sync.py:484); the fingerprint is saved only after a real sync (sync.py:516).
- Job history proves ACNC synced 65,540 → 65,589 on 25 Aug, then NO_CHANGE daily = the
  upstream file genuinely did not change for 6 days (ACNC publishes ~weekly).
- Next run (01 Sep 03:15) detects new etag → syncs ~65.6K rows.

**Latent robustness gaps found (not this incident):**
- HEAD probe sends no `Cache-Control: no-cache` (sync.py:176-177) — a stale CDN response
  could hide a change (no evidence it happened).
- Missing validator headers → empty strings in fingerprint (sync.py:159) — a 200 without
  etag/last-modified/content-length could miss a body change.
- ACNC's buffered GET does NOT follow redirects while the HEAD probe does (sync.py:176 vs
  sync.py:244) — real asymmetry bug that would affect a DETECTED sync, not the skip.
- Timezone: none — persistence is UTC, comparison is string-based.

**Recommendations:** keep force=false; alert only if 01 Sep still NO_CHANGE. Backend
hardenings optional: Cache-Control:no-cache on HEAD, reject validator-less probes,
follow redirects on buffered GET.

## Exit Code Semantics

- `0` = PASS (all datasets synced or legitimately skipped)
- `1` = ALERT (a real sync failure — dataset didn't update, auth error, etc.)

This is the standard no_agent "exit 0 unless real alert" pattern. Email/alert is
driven by the exit code + stdout, not by in-script SMTP.

## Retry / Backoff

- `503` → retry up to 3 attempts, wait `10 * (attempt+1)`s
- `401` / `422` → permanent error, no retry, alert
- `524` → verify path (above)
- Other HTTP errors → alert

## Pitfalls

- **`asic-registered-schemes` skip is CORRECT — do not flag it.** It shows
  `⏭️ Skipped (intentionally unavailable)` on every run. This is by design.
- **Token read is line-split based.** The `.env` must have
  `INTERNAL_SYNC_API_KEY=...` on a single line. If the token has whitespace,
  `split()[0]` truncates it — check the value isn't quoted/space-padded.
- **Health check is a hard gate.** If `/health` on api.amlhive.com.au is down,
  the script aborts before syncing (exit 1). A backend deploy during the 03:15
  window will surface as a health-check failure, not a sync failure.
- **Cloudflare 524 verify adds latency.** A full run can take 10+ minutes when
  multiple long datasets hit 524. The cron timeout must accommodate this.

## Related

- `reference-data-ingestion` — the CSV source path (data.gov.au → R2 → Supabase)
- `pluto-pipeline-orchestration` — where the sync cron sits in the pipeline
