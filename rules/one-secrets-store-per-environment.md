# One secrets store per environment, one readable map, no value ever printed

Applies to every product with production credentials, on every machine.

## Why this exists

**3 Nov 2026, handledispute.** Production secrets were split between SSM SecureStrings and a local `.env` that also pointed at a live email provider and a remote database. The founder asked for a single production secret ("handledispute/prod/secrets") and said staging gets the same shape later.

## Core Directives

1. **Name by environment:** `<product>/<env>/secrets` in Secrets Manager (JSON), or `/<product>/<env>/<name>` for individual SSM SecureStrings. Production exists now; staging is created with the same shape when a staging environment exists.
2. **Say which store and why.** Secrets Manager costs about 0.40 USD a month per secret and needs an IAM grant per runtime consumer. SSM is free and already wired into deploy scripts. Record the founder's choice verbatim.
3. **Reading order in tooling:** real environment variables, then the secret store, then the git-ignored env file as a fallback. Select the environment with one variable (`HD_ENV`, default `prod`).
4. **Create once, never overwrite:** a founder-run short script reads the local file and calls `create-secret` (which fails if the secret exists). The agent never reads or prints the values.
5. **Values never reach argv, logs or error messages.** Pass them in the environment or on stdin. A helper that fails must throw a sanitised message (an e2e helper once echoed a database password in its error).
6. **Keep a runbook table** of every secret: store, name, consumer. Names and locations only.
7. **A local `.env` can point at live systems.** Before running a local server, seed or test, override the database URL, email provider and SMS credentials at launch (a `local-env.sh` that is sourced, not committed with values), and refuse a non-loopback database.
8. **Do not move a production password into a second store** unless asked. A second copy is a second place to leak.

## Verification

The runbook table matches `aws ssm get-parameters-by-path` and `aws secretsmanager describe-secret` (names only). No secret value appears in any transcript.
