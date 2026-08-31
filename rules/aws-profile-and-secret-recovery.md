# AWS profile discipline and lost-secret recovery (all agents)

Applies whenever an agent runs `aws`/`terraform`/any AWS SDK command against this repo's
infrastructure, or is asked to recover a secret that appears lost/unrecoverable.

## Why this exists

This machine's `default` AWS CLI profile is **not** YourApp — it resolves to a completely
different company's account (AnotherCompany, account `707843605914`, `IAM_GRAFANA` user). YourApp's
account is `560205084533` (`I_AM_CLI_ACCOUNT`), reachable only via `--profile yourapp` /
`AWS_PROFILE=yourapp`. A bare `aws`/`terraform` command with no profile set silently succeeds
against the wrong account instead of erroring — there is no loud failure to catch the mistake,
only wrong-account state that looks like YourApp state until someone notices the account ID.

Separately, during an active credential-recovery situation (1 Jul 2026, some Fly.io/Vercel
secrets were unrecoverable), the operative instruction was: treat a lost secret as a
**clean-rotation event**, not a puzzle to solve from fragments — attempting to reconstruct a
secret from logs, shell history, screenshots, or partial dumps risks producing a value that looks
plausible but is silently wrong, which is worse than an honest rotation.

## Rules

1. **Every AWS CLI / Terraform / boto3 command against this repo's infra must carry an explicit
   `--profile yourapp` / `AWS_PROFILE=yourapp`.** Never rely on the `default` profile resolving to
   the right account — verify with `aws sts get-caller-identity --profile yourapp` if there is any
   doubt, and confirm the account ID is `560205084533` before proceeding with anything
   state-changing.
2. **Never attempt to reconstruct a lost/unrecoverable secret** from logs, shell history,
   screenshots, partial dumps, or "does this look like the old value" comparisons. Regenerate at
   the source (AWS Secrets Manager, the provider's own dashboard) and treat it as a normal
   rotation — see [credential-rotation-safety.md](credential-rotation-safety.md) for the rotation
   workflow itself.
3. **`PII_ENCRYPTION_KEYS` is the one exception to "just rotate it".** It is a MultiFernet keyring;
   old keys must stay in the keyring (decrypt-only) until a tested re-encryption job has run.
   Never replace the keyring outright — that would strand any row encrypted under a retired key.
4. **If asked to test a connection or run a command that requires piping a real secret through a
   command you execute** (e.g. `aws secretsmanager get-secret-value | psql`), prefer handing the
   user the exact command to run themselves and asking for non-sensitive results back (row counts,
   whether data looks current) over running it yourself — this applies even when the request is
   phrased as an action ("test the connection") rather than a display request ("show me the
   password"). Confirmed as the right call by the user, not overcautious, when raised in-session.

## Related

- [credential-rotation-safety.md](credential-rotation-safety.md) — safe rotation mechanics once a
  rotation is actually happening
- [no-secret-masking.md](no-secret-masking.md) — never derive a "safe" display string from a
  credential-bearing field
- `.claude/skills/handling-sensitive-data/` — packages the rotation workflow end-to-end
