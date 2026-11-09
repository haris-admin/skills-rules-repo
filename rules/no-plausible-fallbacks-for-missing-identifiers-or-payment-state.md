# Never turn a missing value into a plausible one (all agents, all repos)

Complements the `honest-failure` skill. Applies to receipts, reports, invoices and any record a customer keeps.

## Why this exists
**8 Nov 2026, Tap-Ease C75 A2, A3:** receipts printed the dev-kit terminal id `TERM-C046AG` and the literal `MERCHANT-ID` when the real id was unknown, and an unpaid trip rendered APPROVED, TOTAL PAID, paid by CASH because a missing payment method defaulted to CASH. Tests passed the fallback value in as input, so they never saw it.

## Rules
1. In production a missing identifier, amount or payment outcome stops the document with a coded error. The staging value is a staging-environment setting, never a code constant.
2. No default payment method, status or total. A pending record gets a "not ready" response, not a document.
3. Historical documents read the values stored when they were created, never the current state of a mutable row (a re-pair must not rewrite old receipts). Old rows without a stored value are flagged unknown, not guessed.
4. A test for the failure path must not supply the fallback itself.
