# New behaviour behind a device or tenant flag must leave the flag-off path untouched

Applies to any change gated by a per-device, per-merchant or per-tenant flag (for example Tap-Ease `trans_devices.is_tapease_pos_enabled`).

## Why this exists

**1 Nov 2026, Tap-Ease Lambda 0.10.12:** the `is_tapease_pos_enabled` release shipped with only one flag-off test. Two flag-off
paths had changed anyway: the refund payout device and driver lookup was rewritten for every device, and a negative Clover
additional charge was passed through instead of becoming 0. Haris: "Make sure ... all the calculation is still done the old way"
and "If it is actually for the old devices, whatever we were doing earlier, keep on doing the same." Fixed in 0.10.13.

## Rules

1. Flag FALSE or NULL means the pre-release behaviour, byte for byte in outcome: amounts, lookups, filters, side effects.
2. Every gated branch has a flag-off test beside its flag-on test, including NULL, the edge inputs the old code handled
   (negative or missing values) and each downstream step (payout, lookup), not only the calculation.
3. A shared helper changed for the new path must be checked against every flag-off caller. Gate the change on the flag, or
   keep the old function and add a new one.
4. Each change traces to a spec clause. A change to a shared path with no clause is a gap to raise with Haris, not a refactor.
5. Prove the legacy path live: after deploy, confirm a flag-off transaction logs the legacy mode and unchanged numbers.

## How to apply

Write the flag-off tests first and run them against the new code (Red shows where the legacy path moved). Verify the flag
column in the live schema (read only) and count devices per value so you know how many are affected. Tap-Ease reference:
`tests/test_tapease_pos_legacy_path_unchanged.py` in `portal_backend_lambda_eventbridge`.
