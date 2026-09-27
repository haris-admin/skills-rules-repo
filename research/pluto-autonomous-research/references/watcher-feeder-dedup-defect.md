# Watcher/feeder dedup defect — a whole briefing silently lost (28 Sep 2026)

## Symptom

`~/.hermes/mempalace-inputs/` held 2 files with **no `.processed/<stem>.done` marker**, and the
watcher kept re-processing them on every 5-minute run while the chamber gained nothing:

```
gmail-briefing-3788-20260928_045503.md | findings: 85 | fed: 0 | status: failed
   error: status='stored', stored=85, verified=0 (read-back must equal stored),
          stderr=dedup: 85 item(s) already present — skipped
```

A fresh Genspark Daily Intel (85 items) reported "stored=85" and "85 already present" at the same
time, while `col.get(where={'topic': 'Genspark Briefing: ... 2026-09-28'})` returned **0 documents**.

## Root cause (two defects stacked)

1. **Dedup identity was a substring test on a blob.** In `pluto_mempalace_feeder.py` `feed_findings()`,
   items without a `quote_hash` were deduped with
   `ident[:200] in "".join(collection.get(limit=2000).get("documents"))` where `ident` was the
   finding title. The Genspark ingestor writes every block as a bare `## Finding`, so all 85 items
   were titled `"Finding"` — one generic substring hit fast-forwarded the entire file.
   Same failure mode for any file with repeated or very short headings.
2. **Verification compared read-back to the INPUT count.** The watcher asserted
   `verified == findings_stored`, but `findings_stored` is `len(findings)` while `verified` counts
   only the ids actually added. Any legitimate dedup skip therefore looked like a failed feed, so no
   `.done` marker was written and the file was retried forever.

## Fix (both applied 28 Sep 2026)

* `pluto_mempalace_feeder.py`
  * builds `existing_docs = set(collection.get(limit=5000).get("documents") or [])` per chamber;
  * the non-`quote_hash` branch is now `dup = doc in existing_docs` (exact full-document identity);
  * every accepted doc is added to `existing_docs` so intra-batch duplicates are suppressed too;
  * the returned JSON now carries `findings_skipped_dedup` and `findings_added`.
* `mempalace_watcher.py`
  * compares read-back against `findings_added` (falling back to `findings_stored` for older
    feeder output), so a legitimate dedup skip reports `processed`, not `failed`.

## Verification recipe

```bash
# 1. run and read the per-file report (never pipe into head — SIGPIPE truncates the run)
cd /home/habib && python3 ~/.hermes/scripts/mempalace_watcher.py > /tmp/watcher_out.json 2>/tmp/watcher_err.txt
# 2. every entry should now read "status": "processed"
# 3. pending must be 0
pending=0; for f in ~/.hermes/mempalace-inputs/*.md; do stem="${f##*/}"; stem="${stem%.md}";
  [ -f ~/.hermes/mempalace-inputs/.processed/"${stem}".done ] || pending=$((pending+1)); done; echo $pending
```

Then confirm the chamber holds the content, not just that the watcher said ok:

```python
col.get(where={'topic': '...'})            # count must equal the feeder's findings_added
col.get(where_document={'$contains': '<a distinctive line from the file>'}, limit=1)
```

## Rules

* A "stored=N, verified=0, dedup: N already present" triple means nothing was written — treat it as
  data loss, not as an idempotent skip. Cross-check the chamber before believing either number.
* Never "clear" a stuck input by deleting the file or its `.done` marker: deleting the marker re-feeds
  (risking true duplicates), deleting the file destroys un-stored content.
* Any new ingestion route must carry a distinct per-item title, or the exact-document identity above
  is what keeps it honest.
