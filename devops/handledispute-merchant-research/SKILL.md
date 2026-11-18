---
name: handledispute-merchant-research
description: Use when doing HandleDispute merchant enrichment jobs.
version: 4.0.0
author: Mercury
license: MIT
metadata:
  hermes:
    tags: [handledispute, enrichment, identity-research, abr, acma, production]
    related_skills: [undispute-merchant-enrichment-agent, handledispute-edge-monitor]
---

# HandleDispute worker — instructions & skills

## When to Use

Load before any HandleDispute agent work: claiming or completing an enrichment job, an
identity research job, or producing an identity lookup report for the owner.

## The instructions ARE the stored files

This skill stores the owner's two documents **verbatim**. They are the whole contract; this
page does not restate, summarise or extend them.

- `references/instructions.md` — `docs/runbooks/hermes-agent-instructions.md` (580 lines)
- `references/skills.md` — `docs/runbooks/hermes-agent-skills.md` (201 lines, skills 1–8)
- `references/profile-variables.md` — `docs/runbooks/hermes-profile-variables.md` (12 lines)

⚠️ **Credential (owner decision, 2026-11-16):** the single worker credential is
**`HANDLEDISPUTE_AGENT_KEY`** — the same name and value as AWS Secrets Manager
`handledispute/secrets/prod`. `references/profile-variables.md` now documents it too. Both
`/agent/merchant-enrichment/claim` and `/agent/identity-research/claim` return **204**, a
bogus-job heartbeat returns **409** (auth accepted), and the same claim with no key returns
**401** — that pair is the connectivity proof. The short-lived
`PLUTO_HERMES_HANDLEDISPUTE_AGENT_API_KEY` was deleted from the env: do not reintroduce it.

Read both before acting. If they and this page ever disagree, the files win. If the API
rejects something they allow, the API wins — report it to the owner. When the owner says the
documents changed, re-copy them; never run on a superseded copy.

## API quirks observed on production (v0.280.04)

- **`MatchingNames.IsCurrent` is not ABN status.** It flags the *name record* as current; the
  ABN behind it is often `Cancelled`. Always confirm every candidate with `AbnDetails.AbnStatus`
  before listing it — otherwise live franchisees and dead entities get reported as active.
- **`/identity-research/{job_id}/complete` validation:** `legal_name` must be a string (null → 422);
  `acn` must be exactly nine digits **or null** (empty string → 422); a bad ABN checksum → 422.
  Success returns `200` with `state=COMPLETED`, `outcome`, `link_status=RECORDED_FOR_REVIEW`.
- **Franchise brands** (e.g. The Athlete's Foot): a name search returns the franchisor plus many
  franchisees sharing the trading name. The supplied `hints.abn` corroborated against the brand's
  own terms/promotions page settles which entity is meant; list the franchisees at low confidence
  and say so in `notes` rather than dropping them.
- **Read the whole claim body.** It carries `hints` (including `postcode` and `receipt_clues`);
  truncating the response loses evidence you cannot re-fetch — there is no GET for a claimed job.

## Local lane mechanics (not part of the owner contract)

Only the plumbing that runs the contract:

- Base `https://api.handledispute.com.au`, key `HANDLEDISPUTE_AGENT_KEY`, 60s cadence.
  Cloudflare rejects the default python-urllib UA — send `HermesPreDisputeWorker/1.0`.
- Claim tick `57805756dcc3` (`predispute_prod_claim_tick.sh` → `predispute_enrich_poll.py --prod`),
  gated worker `0128a604a0f5` (monitor `predispute_prod_queue_state.sh`, gate prints
  `idle` / `working:<job_id>` / `stuck:<job_id>`). Ops calls: `predispute_agent_ops.py --prod
  {state|heartbeat|fail <CODE>|complete --payload <file>}`.
- State `~/.hermes/cache/scratch/predispute_prod_worker_state.json`; log
  `~/.hermes/state/predispute_prod_worker_log.jsonl`; 12h report `92e8ab1f5102`
  (`55 9,21 * * *`, production lane).
- The legacy staging pair `e3cc72366dd7` / `ff18d93e2d10` is **paused**; its key is not
  valid against the public API (401), so never resume it as-is.
- Prod `/health` publishes only `status`/`version`/`database`.
