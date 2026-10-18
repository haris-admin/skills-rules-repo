# One secret, one audience (all agents, all repos)

Applies to any secret store where access is granted per secret, not per key (AWS Secrets Manager, Vault paths, SSM parameters,
a `.env` shared between hosts), whenever a new key is added to a secret or a new reader is granted access.

## Why this exists

14 Oct 2026, Tap-Ease Clover OAuth. Two findings from one design:

- The design said a Lambda must never hold the token encryption key, but its shared secret for calling the backend was a key in the
  **same** secret as the encryption key. IAM grants a whole secret, so any role allowed to read one key could read both.
- The mapp POS host already read the shared `portal/clover-sync/*` secret. Putting the new OAuth app secret there would have exposed it
  to a host with no need for it, so a separate secret `portal/clover-oauth/<env>` and its own IAM scope were created.

## Rules

1. **Before adding a key, list who can read the secret.** If any reader should not see the new key, it belongs in a different secret.
2. **Group secrets by audience, not by project.** A secret read by two different audiences is two secrets.
3. **Name secrets `<system>-<purpose>/<env>`** and give each environment its own, so a dev role can never read production.
4. **Grant by secret ARN with the random suffix wildcard** (`.../name-*`), to named roles only, through code, with a validation that
   refuses roles that must never have it.
5. **Verify with the IAM policy simulator** that the intended roles are allowed and the excluded roles are implicitly denied, and
   that a dev role is denied the production secret. Do it against the real secret ARN once it exists.
6. **Say where generated values live.** If Terraform generates a secret value it is in the state file: document it, restrict the state
   bucket, add `prevent_destroy`, and prefer a placeholder with `ignore_changes` for any value a person owns (a third-party app secret).
7. **Do not read the value to check it.** Check names, shapes and lengths, and print booleans.

## Related

- Rules: `terraform-prod-apply-safety.md`, `credential-rotation-safety.md`, `no-root-or-unbounded-credentials-for-agents.md`
