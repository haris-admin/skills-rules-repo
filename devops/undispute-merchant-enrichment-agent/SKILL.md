---
name: undispute-merchant-enrichment-agent
description: Use when running the Undispute/Pre-Dispute merchant-enrichment worker.
---

# Pre-Dispute merchant-enrichment agent (Hermes scoped worker)

> The platform was rebranded **Undispute -> Pre-Dispute** (v0.130.08): Next.js UI, email
templates, TouchSMS sender ID (`PreDispute`) and the evidence packs all say "Pre-Dispute".
The repo name is unchanged: `haris-admin/undispute-scheme-neutral-resolution`, and the
"undispute" identifiers left in this skill are real - do not rename them.

Spec = `docs/hermes-agent-instructions.md` in that repo. Design = `openspec/changes/15-merchant-contact-discovery-agent` + `16-acma-compliance-and-outreach-gating`. Agent boundary = `backend/app/api/v1/hermes_enrichment.py`; the contract/validation = `backend/app/services/hermes_enrichment_service.py`.

## The scheduled worker (Hermes crons)

One job in flight at a time; the LLM only runs when there is something to do.

| Cron | ID | Shape |
|------|----|-------|
| ☿ Pre-Dispute Claim Tick | `e3cc72366dd7` | `* * * * *`, **no_agent**, script `predispute_claim_tick.sh` -> `predispute_enrich_poll.py --quiet` |
| ★ Pre-Dispute Enrichment Worker | `ff18d93e2d10` | `* * * * *`, agent, **monitor-gated** on `predispute_queue_state.py`, skills=[this skill], toolsets terminal/file/web/skills |
| ☿ Pre-Dispute 12-Hour Report | `92e8ab1f5102` | `55 9,21 * * *`, **no_agent**, script `predispute_12h_report.py` -> rolls the window and delivers to the group |

Scripts (all under `~/.hermes/scripts/`):

- `predispute_enrich_poll.py` - claim only, behind the contract gate above. Resolves key + base, refuses to claim while a live claim is held (one in flight), writes `~/.hermes/cache/scratch/predispute_worker_state.json`. `--quiet` = watchdog output for a no_agent cron (empty stdout means nothing is delivered; a refusal is logged, never printed, so a 60s cron cannot alert-storm). Exit 10 = claimed, 3 = refused. On `204` the non-quiet mode prints the runbook's exact line: `Pluto Hermes: job queue is empty; sleeping until next configured interval`.
- `predispute_queue_state.py` - the deterministic gate: prints `idle` / `working:<job_id>` / `stuck:<job_id>`. Never prints a timestamp (non-deterministic output would wake the agent every tick).
- `predispute_agent_ops.py` - `state | heartbeat | fail <CODE> | complete --payload <file>`; refreshes the lease in the state file on heartbeat and closes it (`closed`) on success/failure.
- `predispute_12h_report.py` - the 09:55/21:55 report: tick counts from `~/.hermes/cron/executions.db`, jobs claimed/completed/failed, open-claim leak check, endpoint health, 🟢/🔴 verdict. Always exits 0 (a non-zero exit would replace the report with a scheduler error alert).
- `~/.hermes/state/predispute_worker_log.jsonl` - append-only event log written by the poll/ops scripts (`claimed`, `heartbeat`, `completed`, `failed`, `claim_failed`, `complete_rejected`, `fail_rejected`). It lives in `state/`, not `cache/scratch/` (scratch is pruned after 72h), and is the only history the report has — so log new terminal paths when adding them.

Why two crons: the claim endpoint has **no GET**, so queue depth cannot be read. The no_agent tick makes the cheap claim, the monitor reads the state file, and the agent wakes only on a state change (or when a claim goes stale - `stuck:` fires once, 12 min after the last heartbeat).

## Endpoints (scoped agent boundary only)

Base `http://localhost:8008/api/v1/agent/merchant-enrichment`, header `X-Hermes-Agent-Key`:

- `POST /claim` `{"worker_run_id": "<8-64 chars>"}` -> `204` (no work, stop) or `200` with `job_id`, `lease_token`, `merchant_name`, `abn`, candidate email/phone, `origin_case_id`, `lease_expires_at`.
- `POST /{job_id}/heartbeat?lease_token=...` -> extends the lease (10 min). Heartbeat every ~4 min.
- `POST /{job_id}/complete` (JSON body) -> `{"state":"SUCCEEDED","policy_version":N,"policy_version_id":...}`.
- `POST /{job_id}/fail?lease_token=...&error_code=...` -> `{"state":"FAILED"}`. Works on an expired lease too (only `complete`/`heartbeat` check the clock), which is how a stale claim is cleared.

Credential and base URL (Hermes side):

- `PLUTO_HERMES_PREDISPUTE_AGENT_API_KEY` in `/mnt/c/Users/habib/.hermes/.env` - **the same secret the backend holds as `HERMES_AGENT_API_KEY`** (`backend/.env`). The old *Hermes-side* name `HERMES_AGENT_API_KEY` was removed 2026-09-22; the scripts still accept `PREDISPUTE_AGENT_API_KEY` as a fallback name. Empty key fails closed (401 for everyone).
- **Configuration is a hard gate, not a convenience (runbook 2026-09-22).** `predispute_enrich_poll.py` validates all three `PLUTO_HERMES_PREDISPUTE_*` and **refuses to start (exit 3)** if any is missing, the base URL is not `https://`, has a trailing slash, or carries `/api/v1`, or the interval is not a positive whole number. Process env is authoritative; the `.env` file only fills in what the runtime did not export. **There is NO silent http:// fallback and NO localhost substitution** - the old `http://localhost:8008` probe-and-fallback was removed because it bypassed the rule without operator intent. Plaintext is reachable ONLY through the explicit, named non-production opt-in below, and only for a **private** origin. The shell wrapper maps exit 3 to 0 so a refusal cannot alert-storm, the refusal is written to the worker log as a `refused` event, and the 12h report surfaces it RED.
- ⚠️ **`http://192.168.50.210:8008` is private (RFC1918), so with the opt-in it is now CONTRACT-LEGAL under the amended rule — the blocker is REACHABILITY, not the contract.** WSL cannot reach a Windows-bound listener on the LAN IP, so the worker would validate and then claim nothing. Loopback mirroring only works for `127.0.0.1`. Keep the origin set to `http://127.0.0.1:8008`; a private LAN or staging origin is permitted only when the worker can actually reach it (e.g. worker and backend co-located on the dev/staging box).
- ⚠️ **`PLUTO_HERMES_PREDISPUTE_BASE_URL` is the one value that must be right.** As of 2026-09-22 it is `http://127.0.0.1:8008` (the loopback mirror WSL can actually reach) plus the explicit non-prod opt-in. If it is ever set back to the Windows LAN IP (`http://192.168.50.210:8008`), the config now VALIDATES (private origin + opt-in) but the worker still claims nothing: **WSL cannot reach a Windows-bound listener on that IP**, and only mirrored loopback works.
- **Non-production exception (owner-directed 2026-09-22; widened to the amended contract 2026-09-28).** Plaintext is allowed ONLY for a **private** origin — loopback (`127.0.0.1` / `localhost` / `::1`), RFC1918 (`10/8`, `172.16/12`, `192.168/16`), link-local/ULA, or a private-only TLD (`.local` / `.internal` / `.lan`) — AND only when the operator sets `PLUTO_HERMES_PREDISPUTE_ALLOW_INSECURE_LOCAL=1` in `/mnt/c/Users/habib/.hermes/.env`. Any PUBLIC host on http:// is still refused, so the exception can never silently authorize plaintext over a public network. The rule has exactly one implementation — `is_private_host()` in `predispute_enrich_poll.py`; the contract test matrix lives beside it and covers prod-HTTPS, private-RFC1918, private name, and public-host refusal. Each use is logged as an `insecure_override` event and the 12h report shows it as a 🟡 FYI (never a RED, never silent). **Unset it for production** - that is the production checklist item.
- **Nothing from the wire is logged or reported.** The response body of a failed call is drained and discarded; the log and the delivered Telegram banner carry only `http <status> · category <category>` plus an opaque run id, per the runbook's `claim failed; category=<c>; run_id=<r>` shape. Categories: `auth` (401), `conflict` (409), `validation` (422), `service_unavailable` (503), `server_error` (other 5xx), `transport_error`, `http_<code>`.

## Hard rules

- Merchant-only data. Never cardholder PII, dispute narrative, transaction amounts/dates, PAN/CVV, receipts, tokens, or free-text notes. Never email/SMS/phone the merchant, never touch user/admin APIs or the DB as the agent.
- `source_url`, `return_policy_url`, `chargeback_resolution_url` must be `https` on the verified official domain (subdomains allowed). The ABR/ASIC reference does NOT satisfy that check - carry it inside `llm_assessment` instead.
- ACMA outcomes: `ALLOWED|BLOCKED|DEFERRED|UNKNOWN` only; map the ACMA service's `BLOCKED_*` to `BLOCKED`; never `ALLOWED` on uncertainty or outage.
- `enrichment_action_ready` is set by the backend as `bool(contact_email and acma_decision == "ALLOWED")`. Submitting a null `contact_email` is the reliable way to leave outreach not-ready.
- The backend runs its OWN policy analysis: `hermes_enrichment_service.complete()` calls `deepseek_policy_analysis_service.assess(source_url, observed_at, raw_policy_text)` and **overwrites** `llm_assessment`, `llm_commentary` and `llm_rule_analysis` (adding `confidence`). Submit them as `{}`; what the backend actually needs from the agent is `raw_policy_text` + `policy_fields`.

## Where the ACMA credential lives (two sides, never the same file)

`ACMA_API_KEY` is a **caller** credential and belongs to the **consumer**, not to the ACMA service:

- **undispute** `backend/.env` -> `ACMA_API_KEY` (+ `ACMA_SERVICE_URL`). `acma_client._headers()` sends it as `X-API-Key` on every call. Empty value makes the gate silently BYPASS with a warning (`ACMA_API_KEY not set - bypassing compliance check`).
- **acma-python** `.env` -> `MASTER_API_KEY` (bootstrap, mints ad-hoc keys via `/admin/keys`) + `UNSUBSCRIBE_SECRET`, and, when the service self-provisions a caller, that caller's raw key too (see below). The `api_keys` registry in `acma.db` keeps only the SHA-256 `key_hash` and an 8-char `key_prefix`.

**Two provisioning paths, do not confuse them:**

1. **Declared (preferred).** `init_db()` (`app/db/database.py`) upserts a `pluto-hermes` row at startup from `settings.PLUTO_HERMES_ACMA_API_KEY`, and treats a *changed* env value as an intentional rotation (new hash, `notes = "Rotated from PLUTO_HERMES_ACMA_API_KEY."`). Here the raw key legitimately sits in acma-python's `.env` as the declaration of record. Because this runs only on startup, a `.env` edit alone does nothing - reload the service.
2. **Minted (fallback).** `POST /api/v1/admin/keys` with `X-API-Key: <MASTER_API_KEY>`; raw value returned once and never stored raw. Use for consumers without a declared slot (e.g. `undispute-backend`).

Flow: mint at ACMA (`POST /api/v1/admin/keys`, `X-API-Key: <MASTER_API_KEY>`) -> raw value shown once -> copy into the consumer's `.env`. One project key per caller so revocation is per-caller (observed: `pluto-hermes` for the worker, `undispute-backend` for the backend).

## ACMA leg (independent source)

acma-python service on `:8009`. Real endpoint is `POST /api/v1/check/contact` (not `/check/outreach` - that path is a stale reference and 404s). Authenticate with the **provisioned** pair from `/mnt/c/Users/habib/.hermes/.env`: `PLUTO_HERMES_ACMA_BASE_URL` + `PLUTO_HERMES_ACMA_API_KEY` (send as `X-API-Key`). Do not mint ad-hoc keys when a provisioned one exists.

**Route pitfall:** the configured base is `http://192.168.50.210:8009`. That is the Windows host's LAN IP and WSL mirrors it, but a Windows-bound listener is NOT reachable from the WSL namespace on that IP - only on mirrored loopback. Verified: `192.168.50.210:8009` -> connection refused from WSL, `127.0.0.1:8009` -> 200, same URL -> 200 from Windows. There is also no Windows Firewall inbound allow rule for TCP 8008/8009 or for python/uvicorn, so LAN callers cannot reach it either. From WSL use `http://localhost:8009`; resolve with a `/health` probe and fall back. Same for the backend on `:8008`.

Creating a key is only a fallback: `POST /api/v1/admin/keys {"project_name": ...}` with header `X-API-Key: <MASTER_API_KEY>`; the raw key is shown once. OpenAPI is at `/openapi.json`.

Read the decision + `audit_id` from the response and submit `acma_evidence_reference = f"acma-audit:{audit_id}"`.

## Secret hygiene (binding)

No credential value ever appears in tool output, a log, or a report — only its name, presence or length. Read env files with `python3 ~/.hermes/scripts/envpeek.py <file>` instead of ad-hoc `grep`/`cat`: a debug filter written to "show me the config" is the most common leak path, and it is what puts a key into session history. Binding card: `~/.hermes/rules/secret-handling.md` (mirrored in `~/.hermes/skills/rules/`). Local-network-only keys are covered too — the label describes the blast radius, not permission to print.

## Configuration — single source, verified 2026-09-23

Every pre-dispute worker component reads its config from **`/mnt/c/Users/habib/.hermes/.env`** (the Windows-side Hermes env). Nothing sources the WSL `~/.hermes/.env` (it holds no `PLUTO_HERMES_*`) and the gateway does not export these names to cron children, so there is **no shadowing** — process env wins only when a caller sets a value explicitly (that is how the config tests override the base URL).

| Variable | Purpose / current value |
|---|---|
| `PLUTO_HERMES_PREDISPUTE_BASE_URL` | API origin the worker polls. Must be HTTPS *or* a **private** `http://` with the opt-in below. Currently `http://127.0.0.1:8008` — the LAN IP `192.168.50.210` is a Windows-bound listener **WSL cannot reach**. |
| `PLUTO_HERMES_PREDISPUTE_AGENT_API_KEY` | Scoped credential; the backend holds the same secret as `HERMES_AGENT_API_KEY` (73 chars at present). |
| `PLUTO_HERMES_PREDISPUTE_INTERVAL` | Positive whole-number seconds (60). The crons express the same cadence as `* * * * *`. |
| `PLUTO_HERMES_PREDISPUTE_ALLOW_INSECURE_LOCAL` | Non-prod opt-in (`1`/`true`, private-host-only — loopback/RFC1918/link-local/ULA/private TLD; a public host is always refused). Logged once per UTC day — see the log-hygiene rule below. Unset for production. |
| `PLUTO_HERMES_ACMA_BASE_URL` | The ACMA service. **Must be the loopback form `http://127.0.0.1:8009`** — the LAN form is unreachable from WSL. |
| `PLUTO_HERMES_ACMA_API_KEY` | Declared ACMA project key (`pluto-hermes`). Verified: `/api/v1/check/phone` → 200 `ALLOWED`, `/api/v1/check/email` → 200 `BLOCKED_NO_CONSENT`, **no key → 401** (fails closed). |

**ACMA routes** (from `/openapi.json`): `POST /api/v1/check/phone` · `/api/v1/check/email` · `/api/v1/check/contact` · `POST /api/v1/unsubscribe` · `GET|POST /api/v1/admin/keys` · `DELETE /api/v1/admin/keys/{project_name}` · `GET /api/v1/admin/cache/dncr` · `DELETE /api/v1/admin/cache/dncr/expired` · `GET /health`. There is **no bare `/api/v1/check`** — the three sub-routes are the entry points (a POST to the bare path returns 404).

**Backend safety flag:** `HERMES_ENRICHMENT_ENABLED=false` in `backend/.env` keeps the 5-minute outreach scheduler from emailing merchants — leave it false unless merchant contact is deliberately being turned on.

## Pitfalls (all hit in practice)

- **`complete` no longer breaks on a datetime expiry.** `canonical_enrichment_seal()` now stringifies `acma_expires_at` when it is set, so the old `TypeError: Object of type datetime is not JSON serializable` is fixed. `acma_expires_at: null` is still safe and remains the default; if the ACMA response carries an expiry it can now be relayed.
- **Running dev servers do not see `.env` edits.** Both services run `uvicorn --reload`, which watches `.py` files only. A `touch app/main.py` (mtime only, no content change) forces a reload that re-reads `.env`. Do not kill the process if a reload will do.
- **`DATABASE_URL` points at Supabase, not the local container.** `backend/.env` is the Supabase pooler (`...pooler.supabase.com:6543/postgres?sslmode=require`) with `ENVIRONMENT=staging`, so every claim/complete writes to **cloud staging**, not the local `undispute-postgres-local` (5440) container (which is usually behind head or absent). Resolve `DATABASE_URL` before claiming anything you would not want in staging. There is no psycopg in the Hermes python, so DB reads come from the backend venv (copy a script into `backend/`, `./.venv/Scripts/python.exe`, delete it) - or not at all.
- **ACMA cannot normalise 13/1800 service numbers** (`132284`, `1800 954 491`): DNCR is `SKIPPED` and the service still returns `ALLOWED` on an email-only path. Relay the decision; do not silently upgrade a `SKIPPED` to confidence.
- **Candidate contact fields are unvalidated at intake** (real case: `wght@200..700` - a scraped CSS artefact). Verify before submitting; send `null` rather than repeat junk.
- **An unverifiable merchant cannot be completed, only failed.** `complete` demands an `official_domain` and HTTPS URLs on it, so when the ABN fails the ABR checksum and the candidate domain is NXDOMAIN there is no valid completion. Fail with a bounded code (e.g. `UNVERIFIABLE_MERCHANT_IDENTITY`) and leave the merchant untouched - do not invent a domain to satisfy the validator.
- **The `fail` endpoint appends no audit entry** (only QUEUED and CLAIMED appear). Treat terminal-failure auditing as a known gap rather than assuming the chain is complete.
- **Synthetic test fixtures reach the live database.** `backend/tests/test_dispute_service.py` literals ("Tech Electronics", ABN `11223344556`, `support@techelectronics.com.au`) have appeared as real queued jobs, because the suite runs against the configured `DATABASE_URL`. A job whose values match a test fixture is test data: fail it with `TEST_FIXTURE_DATA`, do not enrich it. Run this check BEFORE any research - the 2026-09-21 claim of exactly that fixture is now unreachable (heartbeat 409: the row is gone or terminal after the staging rebuild).
- **An abandoned claim is invisible.** There is no queue listing and `claim` only returns `PENDING` rows, so a claim left `IN_PROGRESS` is never offered again. The state file plus the `stuck:` monitor signature exist to make that leak visible: if a job cannot be completed, FAIL it - never walk away from a held lease.
- **A cron script that exits non-zero raises an error alert.** The claim script exits 10 to mean "a job was claimed", which the scheduler reads as a failure, so the shell wrapper maps 10 -> 0. Any new wrapper around a worker script must do the same.
- **Never let a per-tick worker log a standing state** (a flag, an opt-in, an endpoint mode). One row per tick is ~1,440 rows/day and buries the events that matter — the `insecure_override` notice alone did exactly that before 23 Sep 2026. Log it once per UTC day against a marker file under `state/`; the 12h report reads the opt-in from the env file, so the state still surfaces.
- **Do not assume a Windows-host origin is reachable from WSL.** `127.0.0.1` is mirrored into WSL; the host's LAN IP is not. Every `*_BASE_URL` a WSL-run worker uses must be the loopback form.
- **The contract gate must stay testable.** Config comes from the process env first, then the env file, so a test can override the origin without editing the file — keep that precedence if the loader is ever refactored.

## Verification (read-back is mandatory)

The agent boundary has no GET. Verify as the operator: the `complete` response, a follow-up `claim` not returning the same job, the app log, and the audit chain in `audit_ledger_entries` (columns: `sequence`, `action_code`, `outcome`, `actor_type`, `actor_id`, `source`, `occurred_at`; note the table is `audit_ledger_entries`, not `audit_ledger`, and the timestamp is `occurred_at`). The state file (`predispute_worker_state.json`) must read `closed` with an `outcome` - an open state IS the leak signal.

A clean run leaves exactly six entries: `MERCHANT_ENRICHMENT_QUEUED` -> `MERCHANT_ENRICHMENT_CLAIMED` (actor `hermes:<worker_run_id>`) -> `MERCHANT_ENRICHMENT_SUCCEEDED` -> `CASE_POLICY_VERSION_PINNED` -> `CASE_ACMA_DECISION_RECORDED` -> `MERCHANT_ACTION_READINESS_UPDATED` (expect `DENIED` when no verified contact email).

Run operator queries with the backend venv python (it carries psycopg2 + settings): copy the script into `backend/`, run `./.venv/Scripts/python.exe <script>`, then delete it. Use `isolation_level="AUTOCOMMIT"` and one connection per query, or a failed query aborts the transaction for the rest.
