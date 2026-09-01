---
name: tapease-backend-deploy
description: >
  The sanctioned procedure for cutting a Tap-Ease backend release
  (tapease_portal_fastapi_a2square) and deploying it to the dev / staging
  environment on EC2. Use when asked to "release", "cut a version", "deploy the
  backend", "push to dev/staging", "ship 4.2.x", or to verify a backend deploy
  that just ran. Covers the 7-file version bump, the SSM Docker deploy to
  i-0f9a6ec659e6aab83, DB / SSM access, smoke tests, and the prod boundary.
  NOT for the frontend (see deploy-frontend) and NOT for production backend.
---

# Deploy the Tap-Ease backend (dev / staging)

`tapease_portal_fastapi_a2square` runs as Docker containers on a single EC2 box.
There is no ALB — a bad deploy takes staging down. Production backend is a
**separate** instance and is out of scope here: never deploy backend to prod from
this skill.

## Facts

| | |
|---|---|
| Repo | `A2-Square-aus/tapease_portal_fastapi_a2square`, working branch `dev` |
| Dev / staging EC2 | `i-0f9a6ec659e6aab83`, `ap-southeast-2` (a.k.a. `3.26.61.230`) |
| Containers | `tapease-backend`, `tapease-postgres`, `tapease-frontend`, `tapease-redis` |
| Backend checkout on box | `/opt/tapease/backend` (git working tree, volume-mounted into `tapease-backend:/app`) |
| Postgres | container `tapease-postgres`, db `tapease`, user `tapease` (no password inside the container network) |
| Public URL | `https://api-stg.tapease.com.au` → `/health` shows `"environment":"dev"` |
| Deploy script (runs ON the box) | `scripts/deploy_dev_docker.sh [branch]` — git pull, restart `tapease-backend`, `scripts/run_all_migrations.py` (numbered SQL then `alembic upgrade head`), verify migrations 051–054 + the target migration, `/health` |
| Production backend (DO NOT TOUCH) | `i-062b8ef5437ea6e2f`, `tapease-backend.service`, `https://api.tapease.com.au` |

## Release checklist — bump ALL 7 files (from the repo's AGENTS.md §5)

`x.y.zz` is the new version. Same value everywhere.

1. `app/config.py` — `VERSION: str = "x.y.zz"`
2. `pyproject.toml` — `version = "x.y.zz"`
3. `app/asgi.py` — docstring `API Version: x.y.zz` **and** prepend a
   `## Version x.y.zz Release Notes` block at the top of `api_description`
4. `CHANGELOG.md` — new `## [x.y.zz] - YYYY-MM-DD` with `Added` / `Changed` / `Fixed`
5. `RELEASE_NOTES.md` — new `## Version x.y.zz` section at the top
6. `docs/api_version_tracking.md` — new `## Version x.y.zz (...)` section
7. `docs/pos-integration-api-guide.md` — bump `**Version:** x.y.zz` (+ any endpoint spec changes)

The 4.2.x line is **not git-tagged** (tags stop at v4.1.42) — a release is the
commit + the 7-file bump, no tag.

## Procedure

1. **Land the code on `dev`.**
   - `poetry run pytest tests/<touched>` green; `poetry run ruff check` +
     `ruff format --check` clean.
   - Bump the 7 files, commit (`release(vx.y.zz): ...`), `git push origin dev`.
   - Commit message trailer: `Co-Authored-By: Claude ...` + `Claude-Session: ...`.

2. **Deploy via SSM** (mirrors `scripts/invoke_ssm_dev_deploy.ps1`, which is
   Windows-only — run this from macOS/Linux):
   ```bash
   CMD_ID=$(aws ssm send-command --region ap-southeast-2 \
     --instance-ids i-0f9a6ec659e6aab83 \
     --document-name AWS-RunShellScript --timeout-seconds 600 \
     --comment "deploy dev vX.Y.ZZ" \
     --parameters 'commands=[
       "set -e","export HOME=/root","cd /opt/tapease/backend",
       "git config --global --add safe.directory /opt/tapease/backend || true",
       "git fetch origin","git checkout dev","git pull --ff-only origin dev",
       "bash /opt/tapease/backend/scripts/deploy_dev_docker.sh dev"]' \
     --query Command.CommandId --output text)
   until [ "$(aws ssm get-command-invocation --region ap-southeast-2 \
     --command-id "$CMD_ID" --instance-id i-0f9a6ec659e6aab83 \
     --query Status --output text)" != "InProgress" ]; do sleep 10; done
   aws ssm get-command-invocation --region ap-southeast-2 --command-id "$CMD_ID" \
     --instance-id i-0f9a6ec659e6aab83 \
     --query '{Status:Status,Out:StandardOutputContent,Err:StandardErrorContent}' --output text
   ```
   Success ends with `=== Dev deploy complete (vX.Y.ZZ) ===`.

3. **Apply any one-off SQL fixtures the deploy script does NOT run** (e.g.
   `scripts/_apply_pos_partner_fixtures.sql`) with a separate
   `docker exec tapease-postgres psql -U tapease -d tapease -c "..."` SSM command.

4. **Verify**:
   ```bash
   docker exec tapease-backend curl -s http://127.0.0.1:8000/health
   # expect "version":"x.y.zz", "environment":"dev", "database":"ok"
   ```
   `"status":"degraded"` on its own is fine on dev — it only means the OTEL
   collector / Grafana Cloud isn't wired up.

## SSM gotchas (learned the hard way)

- **`docker logs tapease-backend` over SSM times out** — the container log is huge
  even with `--since`. Read the on-box files instead:
  `docker exec tapease-backend sh -c "tail -n 4000 /app/app/log/*DEV*BACKEND.log | grep -i <pat>"`.
- **Reading Secrets Manager *values* over SSM is blocked** by the sandbox
  classifier. `describe-secret` on `portal/clover-sync/prod` works from the dev
  instance role; `portal/clover-sync/dev` is **denied** (`secretsmanager:DescribeSecret`
  not in the role policy) — relevant to the `tapease-pos-clover-shift-sync` skill.
- Mutating `psql` / deploy commands over SSM may prompt or be denied — if so, hand
  the user the exact `aws ssm send-command` to run themselves.
- Always pass `--comment` so the command is identifiable in `aws ssm list-commands`.

## The prod boundary

- This skill only ever targets `i-0f9a6ec659e6aab83`.
- If asked to "release to production" / "prod" / "go live": stop and confirm
  explicitly. Production backend is `i-062b8ef5437ea6e2f` and uses a different
  path (`tapease-backend.service`, not Docker) — out of scope here.
