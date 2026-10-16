# Podcast Insight Extractor — Production Workflow

> **Status: PROVEN** — running daily since June 2026. Cron `67319a9b2606`, **05:02 AM AEST** (`2 5 * * *`), deliver `origin`.
> **Last verified run:** 2026-10-16 (18/18 quotes verbatim, md 182 lines / json 77.9 KB, 38 frameworks, 46 connections; 5 of the ranked 15 new + 3 fresh extras; QOTD curated off the repeat onto 🆕 No Priors; compute-market speaker attributed to Evan/San Francisco Compute from the transcript; all 7 portfolio labels normalised to canonical).
> Prior: 2026-10-15 (17/17 quotes, 35 frameworks, 35 connections — the auto-picker had repeated the previous day's lead-episode quote on a 3-day-window overlap; the SAME repeat recurred on 2026-10-16, so curating QOTD from a 🆕 episode is now the standing step, not an occasional repair).
> Owner: Pluto. Supersedes the June 2026 Claude-extraction draft of this doc.

## Pipeline Position (verified against the live cron store, 2026-09-20)

```
04:00  Podcast KB Ingestion      (d4d77c41f6c0, no_agent script)
05:02  Podcast Insight Extractor (67319a9b2606)  → podcast_insights.md + .json
05:05  Morning Research          (b0de180cec84)  reads podcast_insights.json
05:10  Cross-Chamber Synthesis   (ddceef1f9e5b)  reads podcast_insights.json
05:20  Briefing Improver         (7cc81d64613a)  🎧 Podcast Insights section in briefing
05:25  Chamber Refresh           (0959371eec17)
05:45  AMLHive Content Ideas     (b76909ed2d52)
06:00  Morning Briefing          (c527fed4a1da, Mon-Fri)  ★
06:45  LinkedIn Ideas            (ee4e48300826)
```

Dual-consumer pattern (research enrichment + content generation) still holds — one extraction, many readers. Never edit the `.md`/`.json` by hand; regenerate from the raw snapshot so the quote verifier runs.

## Implementation (current)

| Piece | Path |
|-------|------|
| Runner (query → extract → verify → publish) | `~/.hermes/scripts/podcast_insights_daily.py` |
| Credential loader / SQL helper | `~/.hermes/scripts/podcast_kb_query.py` (`run_sql`, `load_pass`) |
| Password for `psql` CLI use | `python3 ~/.hermes/scripts/supabase_pass.py` (stdout only, never logged) |
| Extraction cache (per run) | `/tmp/podcast_insights_raw.json` |
| Curation layer (optional) | `/tmp/podcast_insights_overrides.json` |
| Outputs | `~/.hermes/research_outputs/podcast_insights.md` + `.json` |

```bash
cd ~/.hermes/scripts
python3 podcast_insights_daily.py            # full run (query + extract + publish)
python3 podcast_insights_daily.py --publish  # re-publish from raw cache (+ overrides); re-verifies quotes
```

Run properties: 15 primary episodes, 3 fresh extras max, `ThreadPoolExecutor(5)`, DeepSeek `deepseek-flash`
(`DS_MODEL` env to override), 30k sampled chars/episode, retries at 8k/14k/20k `max_tokens`.
Typical wall time 3–6 min, ~125k tokens.

### Steps

1. **Query** — window = `created_at >= NOW() - 3 days OR published_date >= CURRENT_DATE - 3 days`,
   transcripts `length >= 2000`, ordered by `au_relevance_score DESC, published_date DESC`, limit 40.
2. **Select** — top 15 + up to 3 extras (newly ingested **and** AU ≥ 0.30) so fresh-but-lower-ranked
   episodes are not silently dropped.
3. **Sample** — 1500-char chunks scored by portfolio-keyword density (compliance/licence/AU/cloud/
   payment/crypto/tax/agent governance...), always keeping the first 3 chunks; gaps marked
   `[...transcript omitted...]`. Sampling is what makes the quote verifier meaningful — it proves a
   quote came from the real transcript, not a summary.
4. **Extract** — one DeepSeek call per episode, JSON out: `key_theme`, `frameworks[]`, `quote{text,speaker}`,
   `portfolio_relevance[]`, `notable_signal`, `au_relevance_note`.
5. **Verify** — `quote_verified()` normalises both sides and requires either a full verbatim substring or a
   12/10/8-word verbatim prefix. `publish()` **re-fetches transcripts from Supabase** and re-checks every
   final quote (overrides included) — the published header must show `N/N quotes verified`.
6. **Publish** — md sections: Top AU-Relevant Episodes table → Key Frameworks Today → Quote of the Day
   (+ runners-up) → Portfolio Connections → AU & Regulatory Notes → Notable Signals → Source Episodes.
   json carries the same content plus per-episode structured fields for programmatic consumers.

## Curation layer (`/tmp/podcast_insights_overrides.json`)

`publish()` auto-applies the file if present. `archive_stale_artifacts()` moves yesterday's raw + overrides
into `/tmp/podcast_insights_run_<yyyymmdd>/` when the raw snapshot is from another day, so curation can
never bleed across days (overrides are keyed by `youtube_id`). Do **not** leave a curated file behind after
a run unless it is today's.

Supported keys — any key present **fully replaces** that auto-built section:

| Key | Effect |
|-----|--------|
| `quote_of_the_day` | `{text, speaker, show, youtube_id, why}` — `why` gives Haris the reason to care |
| `other_quotes` | list of `{text, speaker, show}` runners-up (3 reads well) |
| `quote_overrides` | `{youtube_id: {text, speaker}}` — per-episode quote repair, re-verified at publish |
| `notable_signals` | list of `{signal, show}` — replaces the first-10-in-episode-order default |
| `portfolio_connections` | list of `{episode, title, project, why, youtube_id, extra_fresh}` |
| `frameworks`, `au_notes`, `pipeline_health` | full replacement of those sections |

Curation rules that have earned their place:

- **Only curate what the extractor got wrong** — quote selection, labels, missing rationales. Themes,
  frameworks and AU notes stay as extracted (they are the actual research output).
- **Every curated quote must be a verbatim substring of stored `transcript_text`** and must survive
  `publish()`'s re-verification. The pipeline prints `[reverify] N/N final quotes verbatim` — treat any
  `NOT FOUND in transcript` as a blocker, not a warning.
- **Normalise project labels** onto the canonical set (below); the extractor emits variants such as
  `FinAI / AI-gov`.
- **Drop, never publish, a portfolio mapping with an empty rationale** — an empty bullet is a visible defect
  in the briefing. Either write the rationale from the episode's own content or omit the mapping.
- Transcript text is stored with upstream escaping (`can''t`, `\$`) — the pipeline unescapes on publish
  (`unesc()`), so curated text uses normal punctuation.

Canonical portfolio set: `ExitLens/CGT`, `PayLicence/PSP`, `TokenPilot/DLT`, `FinAI/AI-gov`,
`AML Hive/compliance`, `CloudProof/cloud`, `Tapease/market`.

## Known extractor defects + standing fixes

| Defect | Symptom | Fix |
|--------|---------|-----|
| Truncated quote | quote stops mid-clause (`...productively spend`) | `quote_overrides` with the completed sentence |
| Weak/mumbled quote chosen | lowest-signal line wins the slot | `quote_overrides`; mine candidates by grepping the transcript for portfolio keywords |
| Empty `why` in a connection | blank bullet in md | fill from episode content, else drop the mapping |
| Label variants | `FinAI / AI-gov` vs `FinAI/AI-gov` | normalise in the curation step |
| Escaped titles | `\$40 Trillion`, `startups''` | `fix_title()` / `unesc()` already handle this on publish |
| Reverify false `NOT FOUND` on multi-line transcripts | quote is verbatim in the DB but `reverify_quotes_from_db` reports `NOT FOUND in transcript` | **Fixed 2026-09-21** in `podcast_insights_daily.py`: the reverify SQL now wraps the transcript in `replace(..., chr(10), ' ')`. Transcripts contain raw newlines, and `run_sql` output was split per line, so only the transcript's first fragment reached `quote_verified()` (only bit long, newline-bearing transcripts — e.g. We Study Billionaires 2026-09-20, 1236 lines). Any repeat means the `chr(10)` replace was lost |
| Model-paraphrased quote | extract-time `quote_verified: False`, or a reverify `NOT FOUND` that survives the `chr(10)` fix | `quote_overrides` with a verbatim line mined from the transcript. 2026-09-21: Lenny's `97LRJUUPy_w` and CoreWeave `cQQbJqvZkpo` |
| Reverify false `NOT FOUND` on inline speaker markers | quote is verbatim in the DB but `reverify_quotes_from_db` reports `NOT FOUND in transcript`; the stored text carries `>>` turn markers **inside** a sentence | **Fixed 2026-10-14** in `podcast_insights_daily.py`: `norm()` now strips `>+` runs on both sides before comparing (a16z `3Q1mdn5ZGvM`: `...bleederboard >> where we keep track...`). Any repeat means the `re.sub(r">+", " ", s)` line was lost |
| ASR-garbled quote wins a slot | quote is verbatim in the DB but is broken English from the source captions (`"...like we are bad capital allocators..."`) or carries `uh`/`you know um` filler mid-clause | `quote_overrides` (per-episode) and/or `other_quotes` (runner-up slots) with a clean verbatim line mined from the same transcript. 2026-09-22: All-In `VTF6p0U98ek`, This Week in Startups `6748oCo7Z_M` |
| Guessed speaker name | host labelled `Jay (host)`, guest name spelled two ways in one transcript (`Audi` vs `Addy`) | Attribute to the confirmed name or the role label. Confirm hosts from on-air address forms in the transcript (a preceding segment asking "what do you think, Jason?" fixes the monologue as Jason Calacanis). Never pick one of two competing spellings — use `Agent Mail co-founder` instead |
| Low-signal auto runner-ups | the auto-built `other_quotes` fallback takes per-episode quotes in episode order, so soft or filler-laden lines reach the published section | Curate `other_quotes` — they are not run through `quote_verified()` by `publish()`, so verify them yourself before writing the override (see the pre-publish check below) |
| Repeated Quote of the Day | the same quote (or a worse-truncated copy of it) headlines the digest on consecutive days | **Expected, not random:** the 3-day window keeps yesterday's lead episode in the ranked set, and `qotd()` takes the FIRST verified quote in episode order, so it re-wins every day until it ages out. Curate `quote_of_the_day` from a `🆕` episode — the QOTD slot is the one Haris reads in the briefing, so a repeat reads as a stale feed. Seen 2026-10-15 (`znstX7x9zZo`, Fintech Insider, second day running, and truncated mid-clause vs the previous day's copy) |
| Truncated quote chosen for QOTD | quote ends mid-clause (`...waiting to be invented`, `...saving trillions of dollars`) | `quote_overrides` with the completed sentence — but the stored transcript often carries the speaker's stutter (`for the for the world`), so prefer a different, cleanly-bounded line from the same episode rather than publishing the stutter verbatim |
| Freshness flags all false | header reads `0 of the ranked` and no 🆕 markers, even though the 4 AM ingest wrote rows | **Fixed 2026-09-25** in `podcast_insights_daily.py`: a publish timestamp from *today* is ignored, the cutoff then falls back to the raw snapshot's `prev_run_cutoff` (same-day re-run) or a rolling 24h. Any repeat means the same-day check or the raw reuse was bypassed — check the `[prev]` log lines |
| Parseable-but-EMPTY extraction on a long multi-talk compilation | the episode publishes with a **blank Key Theme cell**, no frameworks, no connections and `quote_check: too short` — while its own log line says `ok` and `error` is `null` | **Re-extract block-covering**, not densest-window: `python3 ~/.hermes/scripts/podcast_insights_re_extract.py <youtube_id> [--empty] [--publish]`. 2026-10-17: AI Engineer NYC `jiUC6IUMdvc` (421,281 chars) — the daily 30k densest-text sample has no single dense window in a conference compilation, so DeepSeek returned valid JSON with every field empty; 10 contiguous blocks × one keyword-scored window each (46k chars) produced a theme, 2 frameworks, 3 connections and a verbatim quote. **`error: null` + `N/N ok` does NOT prove every row is populated — read the published md for blank Key Theme cells before calling the run clean.** |

Candidate-quote mining recipe (read-only, one pass):

```python
# sentences containing portfolio keywords, straight from stored transcripts
import sys; sys.path.insert(0, "/home/habib/.hermes/scripts")
import podcast_kb_query as kb, re
tx = kb.run_sql("SELECT transcript_text FROM podcast_kb.episodes WHERE youtube_id='<id>';")
i = tx.lower().find("token market fit")
print(repr(tx[max(0, i-500):i+700]))   # copy verbatim, unescape '' -> '\
```

Pre-publish verification of curated quotes (run this *before* `--publish`; `publish()` only re-verifies the
per-episode `quote` fields, so `quote_of_the_day` and `other_quotes` must be checked here):

```python
import json, sys; sys.path.insert(0, "/home/habib/.hermes/scripts")
import podcast_kb_query as kb
from podcast_insights_daily import quote_verified
ov = json.load(open("/tmp/podcast_insights_overrides.json"))
for y, q in ov["quote_overrides"].items():
    tx = kb.run_sql("SELECT coalesce(replace(transcript_text, chr(10), ' '),'') "
                    "FROM podcast_kb.episodes WHERE youtube_id='%s';" % y)
    print(y, quote_verified(q["text"], tx))
```

## Pitfalls

- **A quiet ingestion day still produces a report.** The 3-day window re-reads older episodes, so themes
  can repeat; check `new_since_last_run` / the 🆕 markers before treating anything as new.
- **Zero-episode windows are not an error** — report the ingestion timestamp (`max(created_at)`) instead.
- **Short-form items** (<2000 chars, Shorts/clips) are excluded by design; the md attributes the gap as
  `skipped_short_form`.
- **AU scores are upstream-assigned and coarse** (0.00/0.15/0.30/0.45/0.60 in practice) — they are used for
  ordering only. Never present the score as a verdict.
- **Never print the Supabase credential.** Use `supabase_pass.py` / `load_pass()` inside command
  substitution, or `run_sql()`; both keep the value out of logs and out of skills.
- `--publish` alone is safe and cheap (no LLM calls) — it is the right way to re-apply curation and confirm
  quote verification.
- **Freshness baseline now self-heals (fixed 2026-09-25).** The baseline is the previous
  `podcast_insights.json` `generated_at`, but a same-day run or manual publish writes *today's* timestamp
  into that file, which used to make every episode read "not new" (2026-09-21: a manual pre-dawn artifact
  set `prev_generated_at` to `05:05 today` instead of `05:03 yesterday` → 15/15 unflagged, 0 extras). The
  runner now resolves the cutoff defensively, in this order, logging each choice (`[prev] ...`):
  1. `generated_at` from the previous digest **only if it is from an earlier day** — a timestamp from today
     is this job's own earlier run, not a baseline, and is ignored;
  2. `prev_run_cutoff` recorded in `/tmp/podcast_insights_raw.json` **when that snapshot is from today** —
     a same-day re-run reuses the day's original cutoff, so the flags stay stable across re-runs;
  3. otherwise a rolling **24h** cutoff, matching the header's `New since last run: <created_24h> ingested`.
  The raw snapshot keeps both `prev_generated_at` and `prev_run_cutoff` for audit. Practical effect: a
  hand-edit or a pre-run publish no longer silently understates what is new. Still sanity-check the flag
  against the DB before writing prose about freshness — confirm which rows in the top 15 were created after
  the cutoff (`created_at > timestamptz '<prev_run_cutoff>'`, converted to AEST).

## Verification checklist (post-run)

```bash
wc -l ~/.hermes/research_outputs/podcast_insights.md          # target < 500 lines
python3 - <<'EOF'
import json; d = json.load(open("/home/habib/.hermes/research_outputs/podcast_insights.json"))
print(d["date"], d["quote_verification"], len(d["frameworks"]), len(d["portfolio_connections"]))
print("blank rationales:", sum(1 for c in d["portfolio_connections"] if not c["why"].strip()))
print("unverified:", [e["show"] for e in d["episodes"] if not e["quote_verified"]])
EOF
grep -c -F -e '\$' -e "''" ~/.hermes/research_outputs/podcast_insights.md   # 0 escaping artifacts
```

Pass criteria: date = today, `N/N quotes verified`, no blank rationales, no unverified quotes,
no `\$`/`''` leaking into the published md.

## Production track record (recent)

| Date | DB total | Window | Usable tx | Ranked | Frameworks | Connections | Quotes |
|------|----------|--------|-----------|--------|------------|-------------|--------|
| 2026-09-19 | 1267 | 82 | 41 | 15 + 1 extra | 33 | — | 16/16 |
| 2026-09-20 | 1286 | 73 | 36 | 15 | 31 | 30 | 15/15 |
| 2026-09-21 | 1301 | 66 | 31 | 15 | 31 | 27 | 15/15 (2 quote_overrides; reverify `chr(10)` fix) |
| 2026-09-22 | 1317 | 67 | 30 | 15 + 0 extras | 30 | 20 | 15/15 (3 quote_overrides; curated QOTD + 3 runners-up) |
| 2026-09-25 | 1364 | 58 | 24 | 15 + 0 extras | 30 | 22 | 15/15 (1 of the ranked new; freshness cutoff self-healed) |
| 2026-10-14 | 1842 | 102 | 37 | 15 + 0 extras | 30 | 28 | 15/15 (3 of the ranked new; inline-`>>` reverify false negative fixed) |
| 2026-10-15 | 1877 | 107 | 43 | 15 + 2 extras | 35 | 35 | 17/17 (8 of the ranked new; curated QOTD + 3 runners-up, all re-verified verbatim) |
| 2026-10-16 | 1905 | 116 | 49 | 15 + 3 extras | 38 | 46 | 18/18 (5 of the ranked new; curated QOTD off the repeat → 🆕 No Priors; compute-market quote attributed from the transcript; label normalisation applied) |
| 2026-10-17 | 1939 | 119 | 52 | 15 + 3 extras | 37 | 43 | 18/18 (5 of the ranked new; AI Engineer NYC `jiUC6IUMdvc` — 421k-char compilation — came back parseable-but-empty and was re-extracted block-wise via `podcast_insights_re_extract.py`, lifting the digest from 35/40 to 37 frameworks/43 connections) |

(Pipeline switched from Claude to DeepSeek Flash during 2026; the June table in git history is historical only.)
