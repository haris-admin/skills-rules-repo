# Answering "is the YouTube scanning still running, and what did it produce?"

Use when asked whether podcast/YouTube scanning is alive, whether results exist, or what the scans
yielded. Answer with the measured funnel — never with "yes, it's running".

## 1. Prove the sensor is alive (ingest leg, daily 04:00, job `d4d77c41f6c0`)

Read the newest RUN LOGS, not the cron status:

```bash
ls -t ~/.hermes/cron/output/d4d77c41f6c0/*.md | head -5
```

Each run prints a header `📡 N podcasts | Looking back D days (since YYYY-MM-DD)` followed by one
`New: N episodes` line per show. Sum the per-show counts for episodes FOUND that day; list a few
actual titles so the answer is inspectable.

Health tell: `API returned 0 videos — falling back to yt-dlp`. Count these lines. A double-digit
share of shows (10-15 of 39) falling back is the normal shape — discovery still worked, via the
slower path. The real failure is a run with no `New:` lines at all, or a header claiming fewer shows
than the registry holds.

## 2. Prove the corpus is growing

```bash
python3 ~/.hermes/scripts/podcast_capture_audit.py --json
```

Compare `episodes.total` against the last figure you or the skill quoted. Rising total + flat
newest-chunk timestamp = ingest is landing but the chunker is dead (see the capture-chain section).

## 3. Say what the scans PRODUCED (insight leg, 05:02, job `67319a9b2606`)

`~/.hermes/research_outputs/podcast_insights.md` (plus `.json`). Its summary line answers the question
directly: episodes in window · with a usable transcript · short-form skipped · episodes read ·
frameworks extracted · portfolio connections · quotes verified (`N/N verbatim`).

The four sections that downstream proposal/content work actually consumes:
`## Frameworks for the Library`, `## Portfolio Connections`, `## AU & Regulatory Notes`,
`## Notable Signals`. Quote the verified quotes verbatim — they are the only part of the report that
has been through a check.

## 4. State the coverage caveat with its number

"Scanned" is not "captured". Thin/short-form/no-transcript episodes are a permanent large share of
the corpus (~63% unreachable at last audit). Report `selectable` vs `unreachable` from the SAME audit
run, and never present the raw episode count as coverage.

## 5. Then answer, in this shape

(a) alive or not — run dates + episodes found per day; (b) corpus size and selectable share;
(c) what the last extraction delivered, with 2-4 verified findings; (d) the one gap that limits it,
and what adding a source would cost.

## Pitfalls

- **`🎙️ N` lines are SHOWS SCANNED, not episodes found.** A healthy run can scan 39 shows and find 0
  new episodes on a quiet day; report both numbers or the answer is misleading.
- **`needs_human` is a review queue, not a failed run** (see "A review FINDING is not a job FAILURE").
  Only `error>0` fails the verify leg.
- **Filenames carry the run date, but the guest clock can lag days.** Confirm today's date against a
  network source before calling any run "today's" (see `date-gated-crons`).
- **The insight window is rolling (~3 days).** A finding absent from today's md may just be outside
  the window — query `podcast_kb` for the episode before telling the user the KB lacks it.
- **Empty insight rows are a known class, not proof of no content.** A long multi-talk compilation can
  produce parseable-but-empty JSON; re-extract it block-wise with `podcast_insights_re_extract.py`.
