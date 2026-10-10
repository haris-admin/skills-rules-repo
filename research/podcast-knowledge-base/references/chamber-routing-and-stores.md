# Chamber routing, free-tier pacing, and the three stores

> Extracted from `SKILL.md` 2026-10-11 (SKILL.md was at the 100,000-char ceiling and patches were hard-failing).
> Read this before changing any routing, pacing, or store/reconcile behaviour.

---

### Chamber router — BUILT, measured, and in calibration

`scripts/podcast_three_filters.py` reads each **locked** episode and routes its material into three
chambers, verbatim and attributed; `scripts/podcast_filters_report.py` aggregates the run's JSONL into
one markdown file per lens under `~/.hermes/mempalace-inputs/` for the vault sync to carry to Alexandria.

It routes from the **stored** transcript, so a YouTube block does not block it (only ingest/repair are
blocked) — do not park routing work behind a transcript-access problem. Measured over 41 episodes:
**0 failures, $0.00069 per episode**, ~12 chamber-1 items each, i.e. the entire 1,364-episode corpus
routes for about a dollar. Cost is not a reason to ration routing; **relevance calibration is the real
problem** (see the calibration rules below).

1. **Chamber 1 — noteworthy, verbatim**: frameworks, numbers, predictions, contrarian claims, tactics,
   lessons. The quote is copied exactly and carries a short context label.
2. **Chamber 2 — Australian relevance**: geography, regulation, payments rails/schemes, local industry,
   sovereignty, workforce — each with a short `why_australia` line.
3. **Chamber 3 — project lenses**, one file per lens rather than one mixed bucket (retrieval and dedup
   stay clean):
   - `simplifii` — neurodivergent/accessible learning, EdTech, students, study support
   - `predispute` — pre-chargeback reconciliation and recovery, merchant/customer disputes, chargebacks
   - `tapease` — card-present POS, transport ticketing, taxi, forecourt, in-person payments
   - `amlhive` — AML/CTF compliance, AUSTRAC, RegTech, reporting obligations
   - `haris` — the operator's own public positioning: AI adoption and safe agent rollouts in regulated
     environments, agent architecture and governance, payments architecture, cloud/resilience,
     engineering operating models, regulated delivery (APRA CPS 230, AUSTRAC Tranche 2, Privacy Act,
     Essential Eight). Source of truth for this lens is harishabib.au — re-read it when the lens
     looks stale rather than inventing themes.

**Hard rules — each one earned by a failure earlier in this chain:**

- **Only `locked` episodes feed the router.** The P5 gate is the router's input filter, never its job.
  ⚠️ **This is the CONTRACT, not current code — check before repeating it.** As of 2026-09-30 the
  worker selects on transcript length alone (`tf.pick_ids`) and routes `locked`, `needs_human` and
  un-judged episodes alike (measured on the 06:00 tick's 30 routed records: 26 had no ledger row at
  all, 1 `locked`, 3 judged minutes later). Enforcing the gate is a one-line change in the worker's
  candidate/fetch predicate — it is an open decision, not an established behaviour.
- **A shared fetch helper must NEVER carry one leg's selection policy.** `podcast_capture_verify.
  fetch_episodes` embeds the VERIFY leg's "never re-verify what has already been judged" clause. The
  router reuses that helper, and its input is the *opposite* set, so every judged episode came back
  empty and printed as `ep=N: not found` — a cross-leg collision wearing the costume of a data problem
  (2026-09-30 06:00 tick: 10 of 40 slots lost; 209 of the 316 then-remaining candidates already
  judged, so the lane was starving toward `routed=0 failed=0 cooling=[]`, which reads as healthy).
  Fixed by making the clause opt-out (`fetch_episodes(..., ignore_ledger=True)` from the router; the
  default still excludes, so the verify leg is unchanged). When you add a WHERE clause to a helper
  that more than one leg imports, ask which legs it is a correct filter for.
- **Verify quotes in code** with the token-window check and drop (counting) anything that fails. A model
  claiming it quoted verbatim is not evidence; some cheap models paraphrase silently.
- **Provenance per item**: episode id, show, published date, transcript sha, router model, run timestamp.
- **Dedup across episodes** — the same idea from N episodes is one entry citing N sources, not N lines.
- **A lens with nothing says so** ("0 items from N locked episodes"). An empty chamber must never be
  indistinguishable from a chamber nothing was routed into.
- **Idempotent and resumable**, keyed by (episode id, lens, quote hash), so re-runs and corpus backfills
  cannot duplicate entries.
- **Choose the model by measurement, not reputation** — route that decision through `llm-cost-routing`
  ("Value bake-off: reference-scored, and per JOB SHAPE"): benchmark against a named reference on the
  router's OWN output shape (many items with quotes), and project corpus cost from measured tokens.
- **Benchmark over >=8 real episodes, never one** (2026-09-27, cheap Chinese models on OpenRouter): on a
  single episode `inclusionai/ling-3.0-flash` matched the Qwen 3.8 reference's lens counts at 1/28th the
  cost, which looked like an obvious switch. Over 8 real episodes it delivered **70% of the reference's
  recall** (8.4 vs 12.0 general items/ep, 1.2 vs 5.2 Australia, 2.1 vs 6.0 project) with 87% verbatim.
  `deepseek-v4-flash` held up at **90% recall, 96% verbatim, $0.00056/episode** and stayed the router.
  **At $0.25-$0.76 per THOUSAND-EPISODE corpus, routing cost is not the constraint — recall is.** Do not
  trade 30% recall for $0.51 across the whole corpus. Free-tier variants (`:free`) score well and are
  fine for probes, but rate-limit in production. Costs come from the live OpenRouter catalogue, and
  three of five models produced quotes that failed the verbatim matcher — verify in code, always.
- **A FREE first rung does NOT work — measured 2026-09-29, do not adopt it.** Smoke-tested three `:free`
  OpenRouter ids on a real 64k-char episode: `qwen/qwen3.8-27b:free` → **HTTP 429** (rate-limited),
  `nvidia/nemotron-3-super-120b-a12b:free` → **503** (upstream overloaded), `google/gemma-4-31b-it:free`
  → **429**. All three failed in under a second while the paid `deepseek/deepseek-v4-flash` completed the
  same episode in 29.5s (15 general items, 17/19 quotes verbatim, ~$0.001). Free ids share a throttled
  pool, so a free first rung adds a failed hop to every episode and falls through to the paid model
  anyway — slower, not cheaper. Keep free ids for backfills and one-off evaluation only. Corollary: at
  ~$0.0008/episode the router is not the cost problem; **recall and plumbing are.**
- **Router ladder as measured (2026-09-27)** — ordered by *completion reliability first*, then value:
  1. `deepseek/deepseek-v4-flash` — completes long structured output, quotes verify, ~$0.0007/episode
  2. `z-ai/glm-5.3-flash` — highest recall (82% vs the Qwen 3.8 reference) and 16/16 verbatim, **but only
     with `reasoning: {enabled: false}`**: left on, it spends the whole output budget on hidden reasoning
     and returns an empty `content` (same trap that killed both Nemotrons and starves DeepSeek at low
     `max_tokens`). Reasoning-heavy models must have reasoning turned OFF for extraction work.
  3. `deepseek/deepseek-v4.1-flash` — fallback, 73% recall
  4. `qwen/qwen3.8-flash` — last resort: proven checker, verbose router (truncated at 7k output tokens)
- **Do not park routing behind transcript access.** The router reads the STORED transcript, so a YouTube
  block stops ingest and repair but not routing — run the filters over what is already captured.

**Calibration — a lens LABEL is not evidence that an item belongs in that lens.** The first real run
produced three failure modes worth guarding against in any filter/router prompt:

- **A free-text relevance field invites post-hoc rationalisation.** Asked *why* an item matters to a
  lens, the model will invent a link: a sports/business episode yielded an item claiming it "touches
  fintech and RegTech". Require an **explicit anchor** — the item must name the regulation, rail,
  jurisdiction or entity it connects to — and drop items that only assert generic relevance. A single
  "relevance" field with no anchor requirement manufactures plausible noise at scale.
- **A broad lens becomes a catch-all.** The self-positioning lens absorbed generic AI-infrastructure
  minutiae while the specific project lenses returned zero — including an episode squarely about
  education scoring zero for the education lens. Define every lens by **explicit triggers** (see the
  trigger table in `references/chamber-router.md`) and **score each item's relevance in code** with a
  threshold, rather than trusting which bucket the model chose.
- **Chamber 1 runs ~12 items per episode**, so 40 episodes produced 500+ items. Dedup by normalised
  quote hash across episodes (the same idea from N episodes is ONE entry citing N sources), and expect
  chamber 1 to need theme-level curation on top of quote-level dedup.

**Run mechanics for any multi-episode model pass:** a tool call cannot hold a run of this length (the
`execute_code` cell caps out around five minutes), so launch it **detached** (`tmux new-session -d`),
shard the episode list across 2-3 workers, and have the script **append each episode's result to a
JSONL the moment it lands** — then poll the log with a bounded loop. Partial evidence must survive an
interrupt, and a run must never hold the only copy of its own results in memory.

Sequencing: repair fragments → re-chunk → verify to `locked` → route. Never route ahead of the gate.

### Free-tier routing — the pool IS usable, but only when PACED (built 2026-09-29)

Operator instruction: spend nothing on the routing stage — use the FREE OpenRouter pool. Measured truth:
free ids **do** work on the real router shape, but they are throttled per-upstream, so availability comes
from *patience and rotation*, never from a bigger timeout.

- **Burst vs paced, same episode, same day:** a burst of free ids returned **429/503 inside a second**
  and looked like a hard wall. Paced calls on the same ids succeeded: `openrouter/free` 39.7s
  (gen=10 au=6), `nvidia/nemotron-3-super-120b-a12b:free` 41.0s (gen=8 au=3, **0 dropped quotes**),
  `inclusionai/ling-3.0-flash-sante:free` 7.0s (gen=12 au=1). **Never conclude "free is impossible" from
  a burst failure** — conclude "free needs staggering".
- **`scripts/podcast_free_router.py`** is the staggered worker. Design rules, each load-bearing:
  * rotates the free pool; a model answering 429/503/5xx/timeout goes into **cooldown (default 900s)**
    instead of being retried in a hot loop;
  * when **every** model is cooling it **ends the run cleanly (exit 0)** and resumes next tick —
    "resume later" is success, so a cron tick that routes 2 episodes and stops is not a failure;
  * `--throttle` seconds of our-side pacing between calls (never burst upstream);
  * `--timeout` generous (420s) because free models are slow;
  * **no paid fallback by default** (`--allow-paid` opts in).
- **Wrapper + schedule — the CURRENT lane is the PAID DeepSeek DIRECT lane, not free (switched 2026-09-29
  per the measured verdict below; the script NAME is historical):** `podcast_free_router_stagger.sh`,
  2-hourly cron `e736e32679ab` (`0 */2 * * *`, named "… — DeepSeek DIRECT lane (measured best value)"),
  runs `podcast_free_router.py --since-days 3650 --limit 40 --throttle 3 --cooldown 300 --deadline 2100
  --timeout 420 --models "deepseek-flash@maker,deepseek/deepseek-v4-flash@checker"`. The wrapper then
  runs the report (`podcast_filters_report.py`) and the sidecar conversion (`mempalace_sidecar_from_md.py`)
  in the SAME tick (otherwise the work is dropped — see the emitter rule above), and greps ONE status line
  (`free-routed=N failed=N skipped=N cooling=[...]`) for the channel; the full run stays in
  `cache/scratch/router_value.log`. **That grep must be run-scoped** (`RUN_START=$(wc -l < $LOG)` before
  the run, then `tail -n +$((RUN_START+1)) $LOG | grep ...`): over the whole cumulative log, `tail -2`
  returned the PREVIOUS tick's summary alongside this tick's, so the channel line showed two different
  counts and the stale one read as this tick's result (fixed 2026-09-30). The paid daily router
  `a2ff28e23482` is **disabled**, not deleted —
  re-enable it to revert; the old free-lane settings (`--limit 10 --throttle 20 --deadline 1500` with the
  free ids) remain runnable through `--models`. **The cron PROMPT still calls this a free-tier tick and
  claims "free capacity exhausted = exit 0": the job NAME, the script args and this bullet are the truth —
  never re-route to free on the strength of the prompt.**
- **Backlog accounting (do this before claiming a stall or an ETA):** candidates are
  `podcast_kb.episodes` rows with `length(transcript_text) >= 2000`, counted **ALL-TIME** rather than
  inside a window (the windowed count is exactly what hid the 15 older episodes — see the correction
  below). (708 on 2026-09-30 06:30, windowed; the worker's `done` set is `cache/scratch/free_router_done.json` (393 then).
  Remaining = candidates − done ⇒ **315, all fetchable after the fix below ⇒ ~8 ticks / ~16h at 40 per
  tick**. Count the JUDGED remainder too — before the fix 209 of 316 were counted but unroutable, which
  is how a "backlog" and an idle lane can look identical in the summary line.
  **DRAINED 2026-09-30 20:17** — done caught up to the whole window (708/708, remaining 0; cumulative
  routed 718). **So a tick now reporting `free-routed=0 failed=0 skipped=0 cooling=[]` is CAUGHT UP, not
  starved** — the starved-lane shape and the drained-lane shape are identical, so resolve the two by
  comparing `done` against the candidate count (both are one query each; see the coverage queries
  above) before escalating. From here a tick routes only episodes ingested since the last tick, so the
  steady-state count is small and 0 is normal.
  **CORRECTION 2026-10-03 — "caught up" is only true WITHIN the window you counted, and the window was
  too narrow.** The 400-day window hid **15 transcript-bearing episodes** (13 × The Logan Bartlett Show
  Apr–Jun 2025, 2 × Masters of Scale Aug 2024) that NEITHER lane could ever reach — the daily router runs
  `--since-days 2` and this lane ran `--since-days 400` — so 12 ticks a day printed a clean
  `0 episode(s) queued` while real work sat unqueued. Count candidates with
  `tf.pick_ids(100000, None, None)`, never `pick_ids(400, ...)`. The all-time candidate count is NOT a
  fixed number — it GROWS every time the daily ingestion adds an episode (766 at the 2026-10-03
  verification, 810 at 2026-10-07 08:00), so re-count it each time instead of comparing against a
  remembered figure; what decides CAUGHT UP is `REMAINING: 0`, never the absolute number. A window
  narrower than the corpus turns a DRAINED queue into a STARVED one with
  the same summary line — when a lane reports 0 for hours, re-count with the widest window before
 believing it. **That check is one command:** `python3
 ~/.hermes/skills/research/podcast-knowledge-base/scripts/router_coverage_probe.py` prints all-time
 candidates vs the `done` set and the verdict (`CAUGHT UP` / `STARVED`) — it loads the router's own
 `pick_ids`/`fetch_episodes`, so its candidate count cannot drift from the lane's, and it carries the
 cron env guard, so it runs unchanged from a cron tick.
- **A single `failed=N` is usually TRANSIENT — retry the id once before investigating.** The episode is
  NOT written to `done` on failure, so it re-queues on the next tick by design. 2026-10-03 ep=152 (Logan
  Bartlett, 2273 chars): the maker returned `JSONDecodeError: Extra data: line 1 column 4009` (the model
  emitted a valid object then appended text — the router's greedy `re.search(r"\{.*\}")` swallows the
  extra), the OpenRouter fallback then returned `no verifiable items`; a manual
  `podcast_free_router.py --episode-id 152` minutes later routed it clean (gen=14). So a lone failed
  count is not a dead episode, and it is NOT grounds to widen the model pool or the timeout — re-run the
  id and read the actual error first.
- **The router and the verify leg walk the SAME newest-first frontier — expect them to collide.** The
  05:35 verify run writes its verdict batch while the 06:00 router tick is reading the same head, so a
  judgment landing mid-run turns that episode into `not found` for the router (2026-09-30: its 12-row
  batch landed at 06:04 between the router's 2nd and 5th episode). Combined with the policy leak above,
  judged episodes stayed in the candidate list forever, burning slots on every tick. A `not found`
  count in the summary is therefore a plumbing signal, never "the episode has no transcript" — check
  the ledger status of those ids first.
- **Cost on the direct lane is NOT recorded anywhere.** The worker hardcodes `cost=0.0` on every
  direct-lane record (the DeepSeek API returns tokens, not dollars), so the JSONL's small `$0.05` total
  covers OpenRouter rows only. Never quote our own logs as the spend for this job — verify at the
  provider console. The only per-episode figure we hold is the bake-off's ~$0.0026/episode on
  `deepseek-flash` DIRECT.
- **Free and paid SHARE the dedup state** (`three_filters_state.json`) and the same JSONL, so switching
  lanes can never double-route. Corollary: the free worker must ALSO seed its `done` set from the JSONL,
  or it re-routes what the paid run already did and the quotes come back deduped to zero items
  ("no verifiable items" = a false failure).
- **Pitfall — `LIMIT` before the `done` filter reports "0 episodes queued" forever.** `pick_ids(since,
  limit)` applies the limit first, so the newest N are returned — and the newest are exactly what the
  daily run already routed. Fetch the whole candidate list, then drop `done`, then slice. Symptom: a
  worker that looks idle while the backlog is untouched.
- **MEASURED VERDICT (2026-09-29, 8 episodes x 6 candidates, reference-scored, quotes code-verified):**
  the free tier is **not** the right lane for this job, and neither is OpenRouter's paid route. Per run:

  | candidate | ok | kept | dropped | general | AU | latency | $/ep |
  |---|---|---|---|---|---|---|---|
  | **deepseek-flash DIRECT** | **8/8** | **29.6** | **0.0** | 16.5 | 6.0 | 39s | $0.0026 |
  | OpenRouter deepseek-v4-flash | 6/8 | 20.7 | 3.3 | 15.0 | 3.3 | 70s | $0.0006 |
  | free ling-3.0 | 8/8 | 17.4 | 2.2 | 11.5 | 3.5 | 11s | $0 |
  | free openrouter/free | 7/8 | 14.1 | 1.3 | 12.0 | 1.3 | 38s | $0 |
  | free nemotron-super | 5/8 | 12.0 | 0.6 | 9.6 | 1.2 | 32s | $0 |

  Free reproduces only **~23% of the direct lane's material** (22.4-25.7%) and **fails on 12-37% of
  episodes** (Nvidia 503s, malformed JSON). OpenRouter's paid route **timed out 2/8 at 240s** on long
  episodes. DeepSeek **direct** wins on recall, fidelity (zero dropped quotes), reliability AND latency.
  **The whole ~643-episode backlog costs ~$1.70 on the direct lane**, so preferring free to save that
  throws away ~3/4 of the knowledge for pocket change. **Decision: route on DeepSeek direct**, with the
  OpenRouter id behind it as a different-route fallback. `scripts/probe_free_vs_paid_quality.py` is the
  harness; `--models "deepseek-flash@maker,deepseek/deepseek-v4-flash@checker"` selects the lane.
- **A 400 from the `reasoning` parameter is a WIRING failure, not a bad model — and it silently voids a
  bake-off.** Z.AI's GLM endpoint answers HTTP 400 `Reasoning is mandatory for this endpoint and cannot
  be disabled`, so sending `reasoning:{enabled:false}` scored GLM 0/8 in a run where it was never
  actually tested. Any harness that benchmarks models must retry once with the parameter OMITTED on a
  400 before recording a failure — otherwise it reports a working model as broken.
- **Key state:** `OPENROUTER_API_KEY` is the canonical name (`podcast_capture_verify.llm` already prefers
  it and prints WHICH name resolved); the `_OPENCLAW` suffix is retired. The key carries its own
  **per-key spend limit** — check `GET /api/v1/key` for `limit` vs `usage` before assuming headroom.

**Scheduled — ⚠️ PAUSED 2026-09-29; do not read it as the live router.** `scripts/podcast_three_filters_daily.sh`
ran 06:45 daily (cron `a2ff28e23482`, `no_agent`
script, `deliver: local`, failures routed to the origin chat); that job is now `enabled: false` and the
ACTIVE router is the 2-hourly DeepSeek-DIRECT lane `e736e32679ab` (`podcast_free_router_stagger.sh`), with
the whole chain judged by the 09:00 assert job `7e4a2379157d`. Re-enable `a2ff28e23482` to revert. A **2-day window** catches late-ingested
episodes; the router's quote-hash dedup makes re-runs a no-op. It sits at the end of the chain
(04:00 ingest → 04:30 chunk → 05:35 verify → 06:10 curate → 06:25 watchdog → 06:45 route) so it can only
ever route what is already captured and verified.

**The 06:25 watchdog going RED is the DESIGNED signal while one upstream fault stands — do not read it
as a second, independent failure.** It exits 1 whenever episodes cannot reach the reader, so a red
`cc76c11d35d2` next to a 04:00 ingest reporting "success" with 0 new episodes is ONE fault (transcript
fetches returning 0 chars / `IpBlocked`), reported twice. Before escalating, check the pair: if the ingest
log shows `consecutive transcript failures` or a 0-episode run, the remedy is source access (cookies), and
neither job is broken.

**🔴 Writing markdown into `mempalace-inputs/` is NOT the same as getting knowledge into the palace.**
The watcher parses one shape only — `# Topic`, a `Tags:` line, then `## Finding` headings carrying `Type:`
and `Confidence:` lines (detail in `pluto-mempalace-bridge`). Bullet-style output (`- **point**` plus a
`> "quote"` line) parses to **zero findings**, and the file is then reported processed anyway: the queue
looks clean while nothing is stored. Measured once as 24 of 163 queued files — including the whole output
of a 244 KB run — against a companion file in the expected shape that parsed and stored normally.
**Gate every producer:** `python3 ~/.hermes/scripts/mempalace_watcher.py --dry-run --file <name>` must
print `findings > 0` before the drop is trusted, or the producer emits a JSON sidecar in the feeder's own
shape. Audit the queue with `scripts/audit_inbox_parse.py` in `pluto-mempalace-bridge`.

Full detail, decisions and the gate rationale: `references/capture-chain-audit.md`.
Router prompt contract, lens trigger table and the calibration fixes: `references/chamber-router.md`.

### The three stores and the palace CONTRACT (2026-09-27)

Podcast knowledge lands in three places, and each used to be checkable only by eye. A store can look
healthy while the knowledge is missing from the others, so the links are now explicit:

1. **Supabase `podcast_kb`** — system of record (episodes, chunks, capture ledger). Everything else is
   derived from it.
2. **Alexandria (files) — the subject tree**, not dated blobs: `vault/podcasts/<show>/<year>/ep-<id>.md`
   (one canonical note per episode, with front-matter provenance), plus `index/by-show.md`,
   `index/by-lens.md`, `index/coverage.md` and `lenses/<lens>/<YYYY-MM>.md`. Generated by
   `podcast_alexandria_export.py`, invoked from inside `alexandria_sync.py` so the sync stays the single
   writer; idempotent, so `PODCAST_TREE_FILES=0` means nothing to commit.
3. **MemPalace (vector)** — collections `podcast-knowledge`, `podcast-australia`, `podcast-projects`
   (one collection per lens family, alongside the topic chambers). **Every document carries provenance**
   — `source_type, show, episode_id, published, lens, project, quote_hash, verified, producer` — because
   a hit that cannot be traced to an episode is not knowledge. Embeddings are the local ChromaDB default
   (all-MiniLM), so feeding the palace costs nothing.

**Producers emit markdown + a machine sidecar.** `<name>.md.findings.json` (see
`scripts/mempalace_contract.py`) is the ONLY thing the bridge consumes; human markdown is never scraped
for structure. For artefacts that predate the contract, `mempalace_sidecar_from_md.py` converts with a
shape cascade — bullets → bold section headings → whole document — and attaches episode provenance.

**Five rules the bridge now enforces (each one earned by a silent loss):**

- **Zero findings from a substantial file is a FAILURE.** Only files <400 bytes or carrying an explicit
  gap statement may be skipped: a 244 KB run (502 items) once parsed to zero findings and was marked
  `processed` with `skipped_reason: No findings parsed` — knowledge discarded while the queue looked
  clean.
- **Read back after writing.** A successful `add()` is not proof of storage: the feeder reports
  `findings_stored` AND `verified` (re-read from ChromaDB), and the bridge only marks a file done when
  they match.
- **Reconcile the three stores.** `scripts/mempalace_reconcile.py` (cron `57e72391a773`, 07:15) checks
  queue → palace → Alexandria, prints nothing when healthy and exits 1 with the specific unlanded list.
  Silent health is only trustworthy because the failure mode is loud.
- **A fail-closed consumer obliges you to audit every producer in the same change.** The moment the
  bridge drops markdown-only files, any producer not yet emitting a sidecar becomes a **daily** silent
  drop — the reconciler then lists that day's files as unlanded, which names the symptom and not the
  emitter. Treat a recurring unlanded list as a wiring defect: connect the producer to the contract, then
  run `mempalace_sidecar_from_md.py` once to backfill what was already written. Producers that write
  into `mempalace-inputs/` on a cron (the router's per-lens reports included) must be checked against
  this, not assumed covered. **FIXED 2026-09-29 — the emitter is now wired.** `podcast_three_filters_daily.sh` runs
  `mempalace_sidecar_from_md.py` immediately after `podcast_filters_report.py`, so the router's output is
  converted to contract sidecars inside the same run. Receipt: the 21-file backlog converted (general
  530/617/804, australia 24/31/38, harisabib 25/26/38 items) and drained on the next watcher tick —
  podcast-knowledge 527→792, podcast-australia 24→38, podcast-projects 29→49 — and
  `mempalace_reconcile.py` went from exit 1 to silent-healthy. Historically `podcast_three_filters.py`
  (cron `a2ff28e23482`) wrote markdown only, so every run added 4-8
  substantial files with no `.findings.json` (`podcast-filter1-general-*`, `-filter2-australia-*`,
  `-filter3-{harisabib,amlhive,simplifii,predispute,tapease}-*`) and `mempalace_reconcile.py` exits 1
  every morning. Only the 2026-09-27 batch has sidecars (a one-off backfill) — that proves the converter
  works and the EMITTER is the missing link. Fix: emit from the router, or run
  `mempalace_sidecar_from_md.py` over new artefacts inside `podcast_three_filters_daily.sh`.
- **Cascade the sidecar converter on the BUILT findings, not on the parser's return value.**
  `mempalace_sidecar_from_md.py` tries bullets → bold headings → whole document; switching shape because
  "the parser returned items" still yields zero when every parsed item is then dropped for having no
  title/body — the same silent loss wearing a different hat. Score the cascade after the build+verify
  stage and advance only when findings actually materialise.
- **A `.done` marker keyed on EXISTENCE alone silently drops every LATER addition to a growing file.**
  The per-day artefacts are rewritten as the router appends items — measured 2026-09-29: `general`
  804→1167 findings within one day, `australia` 38→127 — but `mempalace_watcher.get_pending_files()`
  only asked whether `<stem>.done` existed, so the day's file was processed **once on first sighting**
  and every subsequent addition was ignored. The marker already recorded `file_hash`; it was simply
  never compared. **Any producer that appends to a stable filename obliges its consumer to re-process
  on CONTENT CHANGE, not on first sighting.** After the fix (compare `file_hash`), a single watcher run
  recovered **540 findings** (knowledge 792→1155, australia 38→127, projects 49→137). Symptom to watch
  for: the queue reports clean, reconcile is green, and the palace count simply never moves again.
- **Non-knowledge files get a NAMED exception, never a silent one.** Telegram relay fragments and similar
  short-form files cannot become findings and would fail the reconciler forever; move them to
  `mempalace-inputs/_relays/` with a README stating why, so the queue stays honest instead of permanently
  red. An exception must be visible and enumerable — a file that vanishes without a trace is the exact
  failure this contract exists to prevent.
