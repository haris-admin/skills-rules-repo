---
name: acma-dncr-live-washing
description: Use when running live ACMA DNCR washing for pre-dispute.
---

# ACMA DNCR live washing (Real-Time Access)

The pre-dispute stack must never let a stub, an error or a stale result justify contacting a phone number. This skill is the contract for making DNCR washing **live and current**, and the runbook for dispatching it as a subagent/task.

## Hard rules (non-negotiable)

- **Never scrape or "fully load" the national register.** It is not downloadable. Wash only the numbers we hold, against the official service.
- **Fail closed.** Stub mode, an invalid number, an expired result, missing credentials, a SOAP fault or a timeout must **never** produce a DNCR-based `ALLOWED`. Only a **live** `N` (not on the register) inside its 30-day window may permit contact.
- **Stub results are not evidence.** Never reuse a `stub` cache row after switching to live; never present a stub `CLEAN` as a wash.
- **Secrets never leave the secret store.** Account ID / passphrase / API keys must not appear in code, logs, audit rows, reports or chat. Mask phone numbers (last 4) in every log line and report.
- Report a missing subscription or credentials as **the blocker** — do not work around it.

## The real contract (verified 23 Sep 2026)

Source: ACMA/Donotcall "Real-time access via SOAP" fact sheet + the published WSDL. Re-read both before changing code.

| Item | Value |
|---|---|
| Channel | Real-Time Access (RTA) over SOAP — synchronous, one-by-one; best under a few hundred numbers |
| Prerequisite | Industry account + paid subscription **type D or above** |
| Credentials | **Account/Telemarketer ID + passphrase** (plus optional wash-only sub-account ID), passed **in the SOAP body** |
| WSDL | `https://www.donotcall.gov.au/dncrtelem/rtw/washing.cfc?wsdl` (ColdFusion service) |
| Operations | **`GetAccountBalance`**, **`WashNumbers`**, **`GetWashResult`** — there is no `CheckNumbers` |
| Transport | TLS 1.2 or above is mandatory |
| Batch | ~200 numbers per call recommended; **hard ceiling 500 per payload**; under ~5M numbers/month |
| Invalid entries | Do **not** abort the run and **are still charged** — validate before sending |
| Results (per number) | **`Y` = on the register** (block) · **`N` = not on the register** (eligible) · **`I` = invalid phone number** (fail closed) |

Batch alternative (not used here): AWS/SFTP at `sftp.donotcall.gov.au`, SSH-key auth.

## Current state of `acma-python` (verified 23 Sep 2026)

- **As of 23 Sep 2026 the mode is `soap`** in `acma-python/.env` (and `DNCR_API_ENDPOINT` is corrected to the published WSDL host), yet `/health` reports **`dncr_live_configured: false`** — live mode is selected but not configured, so every check must fail closed (it does: `/api/v1/check/phone` → `dncr_status: UNKNOWN`, `permitted: false`, `decision: DEFERRED`).
- **`DNCR_API_USERNAME` and `DNCR_API_PASSWORD` are EMPTY → there is no washing subscription credential. This is the standing BLOCKER** (and without it `GetAccountBalance` cannot be called, so credits are unknown).
- `DNCR_API_ENDPOINT` points at `https://rta.donotcall.gov.au/RTA/RTAService.svc?wsdl` — **wrong host and path**; the published WSDL is `https://www.donotcall.gov.au/dncrtelem/rtw/washing.cfc?wsdl`.
- `app/services/dncr_adapter.py` **has been rewritten** (acma-python v0.10.1+): the stub and every failure path return `UNKNOWN` (`dncr:unavailable`), and the live path **hand-builds a SOAP envelope for `{RTW}WashNumbers`** and posts it; `_parse_wash_response()` maps `Y→REGISTERED`, `N→CLEAN`, `I→UNKNOWN`, and anything ambiguous or not exactly one result → `UNKNOWN`. The endpoint must be HTTPS **and** on the published host, else `dncr:invalid-endpoint`. No `CheckNumbers` reference remains.
- `zeep` is no longer needed: the live adapter posts the SOAP body itself. (It is still absent from `/home/habib/.venvs/acma`; that only matters if someone reintroduces a zeep client.)
- `DncrCachedAdapter` caches successes for `DNCR_CACHE_TTL_DAYS` (30) and **reads the cache filtered by source** (`adapter_used == cache_source`), so a stub row can no longer be served in live mode; `UNKNOWN` is not cached. `adapter_used` is the lowercased class name minus `adapter`, so the live values are **`dncrstub`** / **`dncrsoap`** (not `stub`/`soap`).
- **Observed in `acma.db` on 23 Sep 2026: 1 row, `adapter_used='dncrstub'`, `status='CLEAN'`, unexpired.** With the source filter in place this is no longer a live-reuse hazard — it is stale stub evidence and should still be purged so nothing misleading lingers.
- **Two different credentials, never conflate them:** `PLUTO_HERMES_ACMA_API_KEY` in `/mnt/c/Users/habib/.hermes/.env` (and `ACMA_API_KEY` in `backend/.env`) is **our acma-python service key** — it authenticates the worker/backend *to our own ACMA service*. It is **not** a DNCR washing credential. DNCR needs its own Account/Telemarketer ID + passphrase from the register industry account (subscription type D or above), stored as `DNCR_API_USERNAME` / `DNCR_API_PASSWORD`, both currently empty.
- `app/api/v1/check.py` sets `dncr_status = "SKIPPED"` when a phone cannot be normalised to E.164, and the decision falls through to `ALLOWED`. That is a fail-**open** path independent of the stub.

## Required code changes (the fix this skill dispatches)

1. **Endpoint + method + fields:** WSDL → the published URL; call **`WashNumbers`** with the account ID, passphrase and the number list; read the per-number result and map **`Y`→REGISTERED** (block), **`N`→CLEAN** (eligible), **`I`→INVALID** (fail closed). Optionally confirm credits with **`GetAccountBalance`** before/after a run.
2. **Normalise and validate first:** E.164 for Australian numbers; reject anything un-normalisable as `INVALID` — never send an invalid number (it is charged).
3. **Fail closed in the decision layer:** `stub` / `INVALID` / `UNKNOWN` / missing credentials / SOAP fault / timeout → never `ALLOWED`; they block (`DEFERRED`/`BLOCKED_*`) or surface as a validation failure. An un-normalisable phone must not silently pass.
4. **Cache provenance:** only reuse a row whose `adapter_used` matches the **live** adapter, and only while `expires_at > now`; never write `UNKNOWN`/errors to the cache; never reuse a stub row in live mode (purge or ignore `adapter_used='stub'`).
5. **Record per wash:** wash time, expiry (wash + 30 days), source (`soap`), transaction/wash reference from the service, status. Add the reference column if the model lacks one (`app/models/dncr.py` currently has no transaction-reference field).
6. **Freshness job (optional):** a weekly sweep of numbers likely to be contacted may refresh results, but it **never replaces** the check for a new number or an expired one. Wash before an applicable call/fax, always.

## Secret hygiene (binding)

Never print a credential value — the DNCR Account/Telemarketer ID, passphrase, the `PLUTO_HERMES_ACMA_API_KEY` service key, or any other secret — in tool output, a log, or the report. Report **presence, absence or length only**, and mask every phone number apart from a few trailing digits. Read env files with `python3 ~/.hermes/scripts/envpeek.py <file>` rather than `grep`/`cat`. The binding card is `~/.hermes/rules/secret-handling.md`.

## Procedure

1. **Preflight (callable any time):** `python3 ~/.hermes/scripts/dncr_live_preflight.py` — reports mode, credential presence (never values), endpoint correctness against the published WSDL, SOAP client availability, unexpired stub rows in the cache, the backend's `ACMA_API_KEY` preflight status, the ACMA service's health, and (only when credentials exist) the credit balance via `GetAccountBalance`. **Exit 0 = ready for a live wash; exit 3 = blocked (fail closed).** `--json` for machine-readable output.
2. **Confirm the subscription/credits** (account opened, type D or above, balance > 0). If absent, **stop and report the blocker**.
3. **Apply the required code changes** (above) in `acma-python`, behind `DNCR_MODE=soap`; leave `stub` as the default so nothing is enabled by accident.
4. **Mock verification (no credentials needed):** registered (`Y` → blocked), clear (`N` → eligible), invalid (`I` → fail closed), unavailable (fault/timeout → fail closed), plus stub-mode (`→ never ALLOWED`) and an expired-cache re-wash. Assert the decision layer, not just the adapter.
5. **One authorised live wash** with a real, non-sensitive test number; confirm the audit row records time/expiry/source/reference, then report the **result and remaining credit balance** — masked, no numbers, no secrets.
6. **Record the outcome** in the repo's release notes/ADR and feed the fleet knowledge legs if the contract changed.

## Dispatch brief (use verbatim as the subagent task)

> Goal: make ACMA DNCR washing live and fail-closed in the pre-dispute ACMA service (`haris-admin/acma-python`). Follow the skill `acma-dncr-live-washing`.
> Constraints: never scrape the register; never put credentials, phone numbers or secrets in code, logs or the report; never enable live mode without confirming a type-D-or-above subscription; unmocked live calls only as the single authorised wash; do not touch the backend's case decisions.
> Deliver: (a) whether a DNCR washing account + credits exist (account ID/passphrase presence only) or the exact blocker; (b) the corrected integration (endpoint, `WashNumbers`, request fields, Y/N/I mapping) with the fact-sheet citation; (c) the fail-closed matrix and the cache-provenance fix; (d) mock-test evidence for Y/N/I/unavailable/stub/expired; (e) one live wash result with masked number + remaining credit balance; (f) what still blocks go-live.

## Pitfalls

- Drawing an `ALLOWED` conclusion from a stub `CLEAN`, or from a value the service never returned (`SKIPPED`, missing E.164).
- Calling `CheckNumbers`/reading a `registered` boolean: not the published contract; it fails silently into `UNKNOWN`.
- Caching `UNKNOWN` or stub rows for 30 days — an outage then looks like a fresh wash for a month.
- Treating an invalid number as cosmetic: the service charges for it and continues.
- Sending >500 numbers in one payload, or assuming no per-month ceiling.
- Reporting credits or results without masking the numbers.
