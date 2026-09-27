# Chamber router — three filters, from locked episodes to chambers

## Components

| Piece | Path | Job |
|---|---|---|
| Router | `~/.hermes/scripts/podcast_three_filters.py` | one episode → three filters, verbatim quotes |
| Aggregator | `~/.hermes/scripts/podcast_filters_report.py` | run JSONL → one markdown file per lens |
| Raw per-episode log | `~/.hermes/cache/scratch/three_filters.jsonl` | append-as-you-go evidence |
| Chamber output | `~/.hermes/mempalace-inputs/podcast-filter<N>-<lens>-<date>.md` | carried to alexandria by the vault sync |

```bash
python3 scripts/podcast_three_filters.py --since-days 7 --limit 40   # or --episode-id N
python3 scripts/podcast_filters_report.py                            # renders the lenses
```

**Input is `locked` episodes only** (the P5 curation gate is the router's input filter, never its job).
It routes from the STORED transcript, so a YouTube block does not stop it.

## Prompt contract

```json
{"general":  [{"point": "…", "quote": "exact transcript words", "why": "…"}],
 "australia":[{"point": "…", "quote": "…", "why": "…"}],
 "projects": {"<lens>": [{"point": "…", "quote": "…", "why": "…"}]}}
```

- Build the prompt with `.replace("{transcript}", …)`, never `.format()` — the JSON braces in the
  schema raise `KeyError`.
- Validate the JSON in code; a non-parsing answer is a retry, not a result.
- **Verify every quote in code** with the token-window check after folding typography to ASCII, and
  count the drops. A router that paraphrases silently is worse than a slightly dearer one that quotes
  faithfully — model self-reports about quoting are not evidence.

## Lens triggers — define lenses by what FIRES them

| Lens | Fires on (explicit triggers) |
|---|---|
| `general` | frameworks, numbers, predictions, contrarian claims, tactics, lessons — anything worth keeping verbatim |
| `australia` | a named AU regulator/scheme/place (AUSTRAC, ASIC, APRA, ATO, RBA, OAIC, Privacy Act, CPS 230, Essential Eight, NDIS, AFSL/PSP), payments rails and schemes, data sovereignty, local industry, workforce |
| `amlhive` | AML/CTF obligations, AUSTRAC, transaction monitoring, RegTech, reporting thresholds, fraud controls |
| `tapease` | card-present / terminal acceptance, transport ticketing, taxi and forecourt, in-person payments |
| `simplifii` | education AND learning AND accessibility: neurodivergence, students, study support, EdTech |
| `predispute` | chargebacks, dispute recovery, pre-chargeback reconciliation, merchant/customer disputes |
| `haris` | the operator's own public positioning: AI adoption and safe agent rollouts in regulated environments, agent architecture and governance, payments architecture, cloud/resilience, engineering operating models, regulated delivery |

A lens is fired by a trigger being **named or directly in play**, not by the model's sense of fit. The
source of truth for the self-positioning lens is the operator's own site — re-read it when the lens
looks stale instead of inventing themes from memory.

## Calibration failures and their fixes

1. **Rationalisation.** A `why`/relevance field with no anchor requirement makes the model invent links
   (a sports/business episode produced "touches fintech and RegTech"). Fix: require an anchor — a named
   regulation, rail, jurisdiction or entity — and drop unanchored items.
2. **Catch-all lens.** A broad self-positioning lens absorbs generic AI-infrastructure minutiae while
   narrow project lenses return zero (an education episode scored zero for the education lens). Fix:
   explicit triggers + per-item relevance scored 0-3 **in code** with a threshold, instead of trusting
   the model's bucket choice.
3. **Volume.** ~12 chamber-1 items per episode → 500+ items from 40 episodes. Dedup by normalised quote
   hash across episodes; chamber 1 still needs theme-level curation above that.
4. **Silence is not an answer.** Every run must state its counts per lens AND the number of episodes it
   considered, so "0 items" is distinguishable from "never routed".

## Model ladder for this output shape

The router's shape is LONG structured JSON: many items, each carrying a verbatim quote.

- Models that spend the completion budget on hidden reasoning return **empty content with
  `finish_reason=length`** — send `"reasoning": {"enabled": false}` in the request where the API
  supports it, and keep the 8k → 16k → 32k retry ladder as the fallback.
- A model that keeps starving on this shape is not a router: reorder the ladder to one that completes,
  rather than retrying the same model again.
- A model already proven as a **verifier** (short per-item verdicts) is not thereby a router — the job
  shapes differ, so re-benchmark per shape (`llm-cost-routing`).
- Measured on this shape: the cheap flash tier routed 41/41 episodes with 0 failures at ~$0.0007 per
  episode, which sets the bar any replacement must beat.

## Running it

```bash
# shard the window across workers and detach — a tool call cannot hold the run
tmux new-session -d -s f3 'bash cache/scratch/f3_run.sh > cache/scratch/f3.log 2>&1'
# bounded poll, never an open-ended wait
for i in $(seq 1 20); do grep -q F3_ALL_DONE cache/scratch/f3.log && break; sleep 15; done
```

- Append per-episode results to JSONL as they complete; log per episode: id, counts per filter, model
  used, cost. Surviving an interrupt beats a clean summary you never get.
- Keep exceptions per episode in the log instead of aborting the whole run.
- Provenance per item: episode id, show, published date, transcript hash, router model, run timestamp.
