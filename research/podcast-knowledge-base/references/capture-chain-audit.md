# Capture-chain audit — where podcast knowledge gets dropped

## Why this exists

The pipeline has five links and each one fails silently:

```
episode → transcript → chunks → insights → curated knowledge
   P0         P1          P2        P3            P5
                          (P4 = independent verify of P3)
```

A break anywhere yields the **same** user-visible symptom: "Alexandria has nothing on the episode I
heard" plus a daily digest that teaches something unrelated. Because the symptom is identical, do not
guess which link broke — measure all of them, in order, and report which one is broken.

The dominant failure mode is not a bad summariser. It is a **reader whose selection criteria nothing
satisfies** (e.g. an episode-selection query requiring `>= 8` chunks while the chunk writer has been
dead for months). Every cron can report `ok` throughout.

## The audit

`python3 ~/.hermes/scripts/podcast_capture_audit.py`

Read-only. Exit `0` = chain intact, `1` = capture gap (so a `no_agent` cron surfaces it instead of
hiding behind a green status), `3` = cannot reach the KB.

| Flag | Output |
|---|---|
| *(none)* | totals + the gap counts |
| `--by-podcast` | per-show episode/chunked counts + transcript chars |
| `--ledger` | per-episode lines for the last 60 days (❌ no chunks, ⚠️ partial, ✅ selectable) |
| `--json` | machine-readable summary for chaining into other checks |

Fields worth reading first:

- `newest_chunk_at` — **the single fastest tell that a producer died.** Compare it against
  `episodes.created_at`; a chunk date months behind means the reader has been blind since that date.
- `selectable_by_daily_learning` vs `episodes` — the reachable fraction of the corpus.
- `false_green_ingests` — runs that logged success while creating nothing.
- `insights_episodes_in_window` vs `insights_episodes_read` / `unread` — taken from the extractor's own
  published accounting; the rolling window means anything unread in that window is dropped forever.

## Core coverage SQL

```sql
-- reachable fraction of the corpus
select count(*) total,
       count(*) filter (where exists (select 1 from podcast_kb.chunks c where c.episode_id=e.id)) chunked,
       count(*) filter (where (select count(*) from podcast_kb.chunks c where c.episode_id=e.id) >= 8) selectable
from podcast_kb.episodes e;

-- is the chunk writer alive?
select max(created_at), count(*) from podcast_kb.chunks;

-- did a producer claim success while producing nothing?
select count(*), max(created_at) from podcast_kb.ingest_log
where coalesce(chunks_created,0) = 0 and status = 'success';

-- per-episode chain state (drop the filter to sweep everything)
select e.id, left(e.title,50), length(coalesce(e.transcript_text,0)) tr_chars,
       (select count(*) from podcast_kb.chunks c where c.episode_id=e.id) chunks
from podcast_kb.episodes e
where e.published_date >= current_date - 30 order by e.published_date desc;
```

Run SQL through `python3 ~/.hermes/scripts/podcast_kb_query.py <file.sql>` — pass a **file**, never a
shell pipe into the interpreter (trips the pipe-to-interpreter scanner), and never inline the password.

## The gate set a repair must satisfy

| Gate | Assertion | Rationale |
|---|---|---|
| P0 ingest | episode has a real transcript (> threshold chars) | a 400–1,700 char "transcript" is a YouTube description/Short; it cannot produce chunks or key points |
| P1 raw leg | immutable per-episode record: episode id, show, date, transcript sha256, char count | gives "we did process it" evidence and lets a later pass detect a changed/re-fetched transcript. Lives on `alexandria-ops` (raw), not the curated repo |
| P2 chunks | `>= 8` chunks **and** chunk text >= ~60% of transcript chars | this is what makes the episode selectable at all; coverage catches a chunker that writes 8 tiny stubs |
| P3 extract | key points stored **per episode**, each with verbatim quotes | a rolling window file is not storage; a per-episode record is queryable weeks later |
| P4 verify | an **independent** pass re-reads the transcript, checks every quoted line verbatim, and lists what the extractor MISSED; loop, then lock | a maker cannot verify itself; the "what did you miss" question is the whole point of a second pass |
| P5 curate | only `locked` episodes are curated into the knowledge layer | a gap then reads as `unlocked: N` in the ledger instead of as silence |

Design rules that fall out of this:

- **Verify with a different model family than the maker**, or the check agrees by construction.
- **Quote verification is not capture verification.** Checking that quotes appear verbatim in the
  transcript proves the extractor did not hallucinate; it says nothing about what it never read.
- **Make the ledger the deliverable.** Coverage must be a number per episode (locked / unlocked /
  thin / missing), otherwise "have we missed others?" is unanswerable.
- **Fail the stage, not the report.** A producer that writes zero output must exit non-zero; a
  monitor may never print "success" over an empty result.

## Pitfalls

- **`status='success'` with `chunks_created = 0` is a false green** — the reason a dead producer can go
  unnoticed for months. Assert output counts at the stage that produces them.
- **Never prune a producer without grepping its consumers.** Before removing a stage, find everything
  that selects on its output (`hybrid_search()`, the daily-learning `>= 8` chunks filter, the insight
  extractor) and fix those in the same change.
- **Do not answer "the KB does not have it" from a single search.** Report which link broke: episode
  absent entirely (P0/ingest coverage), present but unchunked (P2), chunked but never read (P3/P4), or
  extracted but never curated (P5). Each has a different fix.
- **Bare substring `ILIKE` on short acronyms returns the wrong show.** `%AMA%` matches *Amazon*.
  Use word-boundary regex (`~* '\mAMA\M'`) or match against the title.
- **Check ingestion coverage per show, not only in total.** A corpus can look healthy while one
  tracked show silently stops receiving new episodes (its channel handle changed, or it fell outside
  the ingest window) — the user notices that specific show missing long before any total moves.
