# Tap-Ease prod deploy boundary (all agents)

Applies to any deploy, container restart, migration, or DB mutation for the
Tap-Ease stack (`tapease_portal_fastapi_a2square` backend, the `tapease` frontend),
and to any `aws ssm send-command` against a Tap-Ease EC2 instance.

## Why this exists

Tap-Ease has no ALB and a documented history of full-site outages from a single
bad change (see the `nginx-change` skill / `context/RCA-2026-08-29-nginx-502-outage.md`).
Backend and frontend production each run on one instance. "Deploy the backend" or
"apply this fix" almost always means **dev / staging**, and acting on production
without the human saying so is the failure mode this rule blocks.

## The instances

| Role | Instance | Path | Public |
|---|---|---|---|
| **Dev / staging backend** (default target) | `i-0f9a6ec659e6aab83` | Docker: `tapease-backend`, `tapease-postgres` (db `tapease`); `scripts/deploy_dev_docker.sh` | `https://api-stg.tapease.com.au` (`"environment":"dev"`) |
| Production backend | `i-062b8ef5437ea6e2f` | `tapease-backend.service` (systemd, **not** Docker) | `https://api.tapease.com.au` |
| Production frontend + edge nginx | `i-0aca7e109d0f6e773` | PM2 `tapease-frontend`, `/etc/nginx/conf.d/` | `https://tapease.com.au` |

## Rules

1. **Deploys, migrations, DB writes, and container restarts default to
   `i-0f9a6ec659e6aab83` (dev / staging).** If the request doesn't name an
   environment, it is dev / staging. Say which box you are targeting before you act.
2. **Any production action needs an explicit, per-action "yes, production" (or
   "prod" / "go live" / the prod instance id) from the user in that same request.**
   Approval for a dev action, or a prior prod action, does not carry over. This
   covers: deploying to `i-062b8ef5437ea6e2f` / `i-0aca7e109d0f6e773`, `psql`
   writes against prod RDS, editing prod Secrets Manager entries, reloading prod
   nginx, and restarting `tapease-backend.service`.
3. **Production backend uses a different mechanism** (`systemd`, not Docker) — the
   `tapease-backend-deploy` skill's Docker/SSM procedure does not apply to it. If
   asked to ship the backend to prod, stop and confirm the procedure with the human.
4. **Never hand-edit prod nginx.** Use the `nginx-change` skill and
   `scripts/safe-nginx-reload.sh`.
5. **Reading Secrets Manager *values* over SSM is blocked and that is expected** —
   not a permissions bug to work around. `describe-secret` on
   `portal/clover-sync/prod` works from the dev instance role;
   `portal/clover-sync/dev` is denied. Diagnose token problems via the running
   app (`clover_shift_client.get_api_token()` returns a bool) or the per-device
   `trans_devices.clover_token`, never by dumping the secret.
6. **Always pass `--comment "<what>"` on `aws ssm send-command`** so the action is
   identifiable in `aws ssm list-commands`.

## Patterns to Follow

```bash
# Deploy request with no environment named -> dev/staging, and say so
aws ssm send-command --region ap-southeast-2 --instance-ids i-0f9a6ec659e6aab83 \
  --comment "deploy dev v4.2.x" --document-name AWS-RunShellScript \
  --parameters 'commands=["bash /opt/tapease/backend/scripts/deploy_dev_docker.sh dev"]'
```

## Patterns to Avoid

```bash
# NO: production instance id with only generic "deploy the backend" authorisation
aws ssm send-command --instance-ids i-062b8ef5437ea6e2f ...
# NO: dumping a secret to diagnose a token issue
aws secretsmanager get-secret-value --secret-id portal/clover-sync/dev
```

## Related

- Skills: `tapease-backend-deploy`, `tapease-pos-clover-shift-sync`, `deploy-frontend`, `nginx-change`, `api-endpoints`
- Rules: `terraform-prod-apply-safety.md`, `security-and-secrets.md`, `deployed-vs-local-code-parity.md`
