# Slow third-party reads are served from our own tables, filled by an independent sync (all agents, all repos)

**Origin (Tap-Ease, 15 Nov 2026).** The client said the app was "very, very slow". Production logs showed the card provider (Oxygen) was the cause: `transactionsByCardProxyNo` ran at p50 28 s and timed out at the 30 s production override, and the backend called the provider live on every request and stored nothing. Database indexes were not the problem.

## Rules

1. **Measure before blaming indexes.** Read the outbound latency (p50, p95, timeouts) from the application log first. A slow screen is usually a slow upstream call.
2. **Own the data you show.** Provider data that a customer screen reads (balances, transactions, details, preferences, an operations log) is stored in our tables with the raw payload, a fetch time and a source. The screen reads our tables and shows an "as of" time. Live provider calls remain for writes and for explicit refresh.
3. **Fetching is independent of the web backend.** A scheduled function (EventBridge-triggered Lambda, as for Clover) calls the provider and upserts, with its own lock, cursor and sync-state table. The web backend does not run the batch.
4. **A failed fetch is not an empty fetch.** On an error or timeout write nothing, increase a failure counter and keep the last good row. A missing provider value is stored as NULL, never as 0 or an invented value. An unparseable amount skips that row and is logged.
5. **Idempotent keys.** Use the provider's id when it exists, else a deterministic hash, unique per card. Re-running the sync must not duplicate rows.
6. **One owner of the schema.** The repo that owns the migrations creates the tables; the sync reads the same contract, and shared test vectors keep duplicated rules (key, amount parsing) identical across repos.
7. **Prove the egress path before asking a provider for an allowlist.** Check which NAT address the existing function already uses; a new function in the same subnet shares it.
8. **Alerts are technical only.** Alert immediately for assigned cards, and send the rest as a daily digest.
9. **Check that log shipping is alive** when you rely on CloudWatch for evidence. A silent stream (no events for days) is its own incident.

Related: `external-calls-logged-request-and-response-mask-secrets`, `locks-must-expire-by-their-own-ttl`, `lambda-image-architecture-and-invocation-proof`, `no-plausible-fallbacks-for-missing-identifiers-or-payment-state`.
