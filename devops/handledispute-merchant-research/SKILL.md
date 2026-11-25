---
name: handledispute-merchant-research
description: Use when doing HandleDispute merchant enrichment jobs.
version: 7.0.0
author: Mercury
license: MIT
metadata:
  hermes:
    tags: [handledispute, enrichment, identity-research, abr, reports, acma, production]
    related_skills: [undispute-merchant-enrichment-agent, handledispute-edge-monitor]
---

# HandleDispute worker — instructions & skills (version 2)

## When to Use

Load before any HandleDispute agent work: claiming or completing an enrichment job, an
identity research job, submitting a research report, or producing an identity lookup report
for the owner.

## The instructions ARE the stored files

This skill stores the owner's documents **verbatim**. They are the whole contract; this page
adds only plumbing and things observed on the wire.

- `references/instructions.md` — `docs/runbooks/hermes-agent-instructions.md`
  (640 lines / 60,397 bytes; **Version 2.2**, 20 Nov 2026, OpenSpec 84f — poll BOTH lanes; 2.1
  (84e) added: report store provisioned 19 Nov, `204` also means only held/closed cases waiting,
  log `first report stored` once per run)
- `references/skills.md` — `docs/runbooks/hermes-agent-skills.md`
  (353 lines / 36,084 bytes; **skills 1–10** — 8 `identity-research-job` (84f: never skip the identity
  lane), 9 `research-report-submission` incl. 9.2b validator rules and 9.6 first-report proof,
  10 `research-completeness-check`)
- `references/profile-variables.md` — `docs/runbooks/hermes-profile-variables.md` (12 lines)

Read them before acting. If they and this page disagree, the files win. If the API rejects
something they allow, the API wins — report it to the owner.

⚠️ **Credential:** `HANDLEDISPUTE_AGENT_KEY` only (same value as AWS Secrets Manager
`handledispute/secrets/prod`). Both claims return **204**, a bogus-job heartbeat returns
**409**, the same claim without the key returns **401** — that pair is the connectivity proof.
`PLUTO_HERMES_HANDLEDISPUTE_AGENT_API_KEY` is deleted; do not reintroduce it.

## Version 2 in one glance (the files are authoritative)

1. **Load skills 1–10 first.** Never work from memory of an older version. Version 2.2 adds one
   rule to 2.1: **poll both lanes every cycle** — identity after enrichment — and a `204` on one
   lane never ends the cycle.
2. **Read the claim whole** — parse in memory, or save it to a file **with `lease_token` stripped**;
   the token stays in memory only, never in a file, log or note. Check every `hints` key including
   `postcode` and `receipt_clues.truncated`. A terminal capture can be cut off.
3. **Keep every candidate**, Australian or not, Active or Cancelled, with its exact status and
   the reason it is or is not the merchant. Never drop one for status.
4. **Completeness check before finishing** (skill 10): for each candidate set
   `WELL_SUPPORTED` / `PARTIAL` / `CONFLICTING` / `NO_EVIDENCE_FOUND` / `NOT_CHECKED` /
   `SOURCE_UNAVAILABLE` for identity & case link, registration, leadership, dispute contact and
   sign-up contact. An empty area is unfinished work, not a blank.
5. **Finish in order: report → attachments → `/complete`.** The report goes to
   `POST /api/v1/agent/{identity-research|merchant-enrichment}/{job_id}/reports` with
   `schema_version "1"`, `research_mode "claimed_job"`, a fresh `idempotency_key` (16–128 chars)
   and the lease token. `/complete` carries only the short summary; the narrative, all candidates,
   contacts and coverage live in the report. **The report has its own validator** (skill 9.2b):
   every required field, no unknown fields, a coverage row for all five areas of *every* candidate
   even when `NOT_CHECKED`, ids matching `^[A-Za-z0-9._:-]{1,64}$` with all references resolving,
   schema enums only, and `recommended_candidate` citing every successful source (policy minimum,
   default 1).
6. **`/fail` only while you still hold the lease**, and only for a source outage, a report-store
   outage or an exhausted time budget (`source_unavailable`, `storage_unavailable`, `time_budget`).
   Outcomes are `MATCHED`, `AMBIGUOUS`, `NOT_FOUND`, `OVERSEAS_ONLY` — and they go through
   `/complete`, not `/fail`. `409 LEASE_INVALID` means the lease is gone: stop and tell the owner,
   `/fail` and `/reports` are both refused. A first-attempt identity failure returns to the queue
   once; anything else ends FAILED for an administrator's Re-run research button (same job, attempt
   01/02/03). **Never call `/complete` after a failed report submission** — no job completes without
   a stored report. Identity leases are **120 minutes** by default; `lease_expires_at` is the truth.

Report shape and the validated example: `references/skills.md` §9.7. Payload limits: §9.2
(`legal_name` never null, `acn` 9 digits or null, ≤5 candidates in `/complete`, ≤10 evidence items,
`notes` ≤2000 chars). The full candidate list belongs in the report, not in `notes`.

## Observed on production (v0.280.04)

- **Report validator, accepted shape (verified on a stored report, 20 Nov 2026):** `outcome`
  `AUSTRALIAN_CANDIDATE` is accepted for a `MATCHED` job; `geography` `AUSTRALIA`; `case_identity_assessment`
  `SUPPORTED`/`UNDETERMINED`; `disposition` `INVESTIGATE`/`RULED_OUT`; `registrations[].kind` `ABN` with status
  `ACTIVE`/`CANCELLED`; `source_type` `registry`/`website` (`other` is unproven — prefer `website`); source `status`
  `SUCCESS`/`UNAVAILABLE`; contact `channel` `EMAIL`/`PHONE`/`WEB_FORM` and `purpose` `DISPUTE`/`SIGNUP`. 15 coverage rows
  (5 areas × 3 candidates) accepted. A stored report returns `report_id`, `version`, `attempt`, `storage_status
  STORED`, `readiness READY_FOR_REVIEW`, `job_state IN_PROGRESS`.
- **`attempt` in the report response is the job's attempt number, not yours.** A job can sit on `attempt: 3` while your
  first report stores fine — never infer that you retried, and never call `/fail` assuming a retry is still available.
- **File-driven lease holder is a compliant way to spread research across tool calls.** One background process claims,
  keeps the token in memory, and watches for `report_request.json` then `complete_request.json` written by the agent; it
  injects the token itself. The token never lands on disk, and the claim → `/reports` → `/complete` sequence still runs in
  one OS process. Reuse that pattern instead of holding the token in `execute_code` globals.
  **Ready-made:** `~/.hermes/scripts/hd_identity_lease_holder.py` (identity lane). It writes
  `~/.hermes/cache/scratch/hd_id_claim.json` (token stripped) plus `hd_id_holder_status.json`, then waits on
  `hd_id_report_request.json` (`{"report":..., "idempotency_key":...}`) → `hd_id_report_response.json` →
  `hd_id_complete_request.json` (`{"payload":...}`) → `hd_id_complete_response.json`; exits on its own, 55-minute life.
  Start it with `terminal(command="python3 ...", background=true)` (in this runtime a shell `nohup ... &` is rejected
  outright — "Foreground command uses shell-level background wrappers" — so use the tool's own background flag), then poll the status file — never re-implement it inline per run.
- **`/reports` is deployed** on both job families: a fake job id returns `404 JOB_NOT_FOUND`,
  not `405`. A **completed** job rejects a late report with `409 LEASE_INVALID` — a report can
  only be stored while the lease is held, so the report must be sent *before* `/complete`.
- **`MatchingNames.IsCurrent` is not ABN status** — it flags the name record. Read the ABN
  status from `AbnDetails` for every candidate. Franchise brands return many entities with the
  same trading name and mixed statuses.
- **Cloudflare** rejects the default python-urllib UA: send `HermesPreDisputeWorker/1.0`.
- **`/health` publishes** only `status`/`version`/`database`.
- **There is no GET for a claimed job.** Whatever is not captured at claim time is gone.

## Lease-token handling in this runtime (hard-won)

- **Never hold the lease token in an `execute_code` kernel variable across calls.** The session
  kernel restarts silently between calls (`execution_count` keeps rising, earlier globals are
  gone), and the token cannot be re-fetched: there is no GET for a claimed job and a re-claim
  returns `204` because the job is still held. The job then sits stranded until its 120-minute
  lease lapses — a lost run.
- **Do claim → research → `/reports` → `/complete` in ONE OS process.** Either one script run
  with `terminal`, or a single `execute_code` cell that fetches everything itself. Write the
  research to a report JSON file first (findings only, no secrets); that file may be reused, the
  token may not.
- **Recovery after a lost token:** the lease cannot be released, so wait for `lease_expires_at`
  and then claim. Claim only accepts a match on the same `job_id`; a mismatched claim must be
  left untouched and the waiter must exit, never `/fail` it. A waiter script that reads
  `HANDLEDISPUTE_AGENT_KEY` at runtime and keeps the token in memory is compliant. The identity
  lane cron (`0318817b1783`, every 10 min) also re-claims the job after the lease lapses and
  researches it from scratch, so a lost token delays a job rather than losing it.

## Local lane mechanics (not part of the owner contract)

- Base `https://api.handledispute.com.au`. Cadence comes from **`HERMES_POLL_INTERVAL_SECONDS`**
  in `~/.hermes/.env` (owner, 20 Nov 2026; currently **120 s**) — the lane-specific
  `PLUTO_HERMES_HANDLEDISPUTE_INTERVAL` / `..._PREDISPUTE_INTERVAL` names are fallbacks only, and the
  script defaults to 60 if none is readable. The cron schedule is static: it is `*/2 * * * *` to
  match 120 s, so changing the variable alone does not change the tick — update the schedule too.
- Claim tick `57805756dcc3` (`predispute_prod_claim_tick.sh` → `predispute_enrich_poll.py --prod`),
  gated worker `0128a604a0f5` (monitor `predispute_prod_queue_state.sh` → `idle` /
  `working:<job_id>` / `stuck:<job_id>`). Ops: `predispute_agent_ops.py --prod
  {state|heartbeat|fail <CODE>|complete --payload <file>}`.
- State `~/.hermes/cache/scratch/predispute_prod_worker_state.json`; log
  `~/.hermes/state/predispute_prod_worker_log.jsonl`; 12h report cron `92e8ab1f5102`
  (`55 9,21 * * *`).
- **Identity lane is polled by its own worker**, cron `0318817b1783` (`*/10 * * * *`, deliver
  origin): it claims in-process, so the lease token never reaches a file, then researches,
  submits `/reports` and calls `/complete`. The enrichment tick deliberately does **not** claim
  identity — claiming there would strand the job on a 120-minute lease with no process holding
  the token. Worst-case pickup for identity is 10 minutes; enrichment follows the configured
  120-second cadence (`*/2` on the claim tick and the gated enrichment worker).
- Legacy staging pair `e3cc72366dd7` / `ff18d93e2d10` is **paused**; its key is not valid against
  the public API (401) — never resume it as-is.
