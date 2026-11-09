# An OAuth token needs the permission for every expanded field in a call (all agents)

Applies when a provider integration moves from a broad credential (API key, merchant token) to an OAuth token or a narrower scope, and when any call asks the provider to expand or include related objects.

## Why this exists

Tap-Ease, 9 Nov 2026. Two terminals moved to Clover OAuth. Their first payment after the switch failed in the Lambda's extended-payment fetch with
`403 {"message":"Invalid permissions for expandable fields."}` on every run (33 and 16 times). The call asked Clover to expand 26 related objects; with an OAuth
token Clover refuses the whole call if one expansion needs a permission the app does not hold. `customers` (v0.10.14) and `metadata` (v0.10.15) were the two
refused ones, and nothing read either. The old merchant token carried every permission, so the same call had always worked. A probe (one payment, one
expansion at a time, status codes only) found the culprits in one run.

## Rule

1. Before switching a merchant, tenant or account to a narrower credential, run the real production calls once with that credential on a canary (read-only).
2. Ask a provider only for the fields the pipeline reads. List each expansion against the code that uses it; drop the unused ones.
3. When such a call fails with 401 or 403 after a credential change, probe one field at a time and print only status codes. Never print the token.
4. Do not roll back as the first move when the cause can be found; a rollback hides the permission gap until the next cutover.
5. Adding a permission to a live provider app needs the provider's review and each customer to approve again, so prefer shrinking the request.

## How to apply

Keep the probe as a throwaway script run by the owner (`~/clover-probe.sh`). Record the refused fields in the integration's skill. Related:
`integration-config-change-verify-and-rollback.md`, skill `clover-oauth-v2-integration`.
