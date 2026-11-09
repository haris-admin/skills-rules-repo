# Clover terminal rollout order: driver, pair, flag, then OAuth (Tap-Ease)

Applies when a terminal and its merchant move to the new Tap-Ease app on Clover OAuth.

## Why this exists

Tap-Ease, 8 and 9 Nov 2026, terminals 1015, 1032, 1086, 1045 and 1020. A merchant approved for OAuth before its terminal was ready was answered `skipped (no_assigned_terminal)` by the token backend. The Lambda then skipped it on every endpoint with the cursors held and no legacy fallback, so nothing was fetched until the terminal was ready. Terminal 1086 stayed skipped until its driver was assigned. Terminal 1045 already had a driver and stayed skipped until the device was paired. My reading from two cases: the backend needs both a paired device and an ACTIVE driver.

## Rule

1. In order: an ACTIVE `trans_device_users` row for the device, the terminal paired (`last_paired_at` set), `is_tapease_pos_enabled` TRUE, then approve OAuth for the merchant.
2. After approval read the next `Clover token sources` log line: `oauth` up by one, the merchant in `oauth_merchants`, `skipped` unchanged. If `skipped` rose, read the reason from the `Skipping merchant` line (a log filter, never a token).
3. Take a test payment and check Silver, Gold (net is gross / 1.05 rounded half up, surcharge the rest) and the driver's pending payout (the sum of the nets).
4. Switching a merchant back to legacy does not remove the 5% split; the split follows the device flag.
5. Do batches of a few terminals, a payment check each, before the next batch.

## How to apply

Use the per-terminal checklist in the Lambda repo's `AGENTS.md` (rule 19). Related: skill `clover-oauth-v2-integration`, `oauth-token-expanded-fields-need-every-permission.md`.
