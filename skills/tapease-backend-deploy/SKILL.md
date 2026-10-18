---
name: tapease-backend-deploy
description: >
  The sanctioned procedure for cutting a Tap-Ease backend release
  (tapease_portal_fastapi_a2square) and deploying it to the dev / staging
  environment on EC2. Use when asked to "release", "cut a version", "deploy the
  backend", "push to dev/staging", "ship 4.2.x", or to verify a backend deploy
  that just ran. Covers the 7-file version bump, the SSM Docker deploy to
  i-0f9a6ec659e6aab83, DB / SSM access, smoke tests, and the prod boundary.
  Also documents the production path (pushing `main` triggers the CI prod deploy) and the cautions around it. NOT for the frontend (see deploy-frontend).
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
| Production backend | `i-062b8ef5437ea6e2f`, `tapease-backend.service` (systemd, not Docker), `https://api.tapease.com.au`. Deployed ONLY by CI when `main` is pushed (see "The prod boundary"). Reads secrets from `portal/clover-sync/prod`. |

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

   **If the release changed an endpoint contract** (new query param, field, path,
   status code), also confirm it is live in the *served* schema — introspect
   `/openapi.json` with a base64'd Python script piped to `base64 -d | python3`
   (inline `char()` tricks to dodge SSM `--parameters` quoting are fragile):
   ```bash
   SCRIPT='import urllib.request, json
   d = json.load(urllib.request.urlopen("http://127.0.0.1:8000/openapi.json"))
   for p, ops in d["paths"].items():
       if "refunds" in p and "get" in ops:
           print(p, [q["name"] for q in ops["get"].get("parameters", [])])'
   B64=$(printf '%s' "$SCRIPT" | base64)
   PARAMS=$(python3 -c "import json,sys;print(json.dumps({'commands':['docker exec tapease-backend sh -c \"echo $B64 | base64 -d | python3\"']}))")
   aws ssm send-command --instance-ids i-0f9a6ec659e6aab83 --region ap-southeast-2 \
     --document-name AWS-RunShellScript --parameters "$PARAMS" --query Command.CommandId --output text
   ```

5. **If the release changed seed data / fixtures** (dev only): re-run the relevant
   seeder against the box — see `tapease-db-access`. The deploy script never seeds.

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
- **Build `--parameters` with `python3 -c 'import json; print(json.dumps({"commands": [...]}))'`**
  and pass the result as one quoted arg. Raw `'commands=[...]'` with embedded
  quotes/`$` mangles (same failure class as the 2026-08-29 nginx outage).
- Connecting a `psql` to the DB from your workstation (not via SSM) — the port map
  (`5433` docker vs `5433` tunnel vs `5434` prod) and the `.pgpass` classifier
  workaround are in `tapease-db-access`.

## Configuring the staging box (learned 14 Oct 2026, Clover OAuth release)

- **Env file:** `/opt/tapease/.env` (not in the backend checkout). The `backend` service reads it with Compose `env_file: - .env` plus a few
  explicit `environment:` keys. **`docker restart` does not re-read it**, and the deploy script only restarts. To apply a changed `.env`:
  `cd /opt/tapease && docker-compose up -d --no-deps --force-recreate backend` (staging is down about a minute; `--no-deps` leaves postgres and
  redis alone). The box has the standalone `docker-compose`, **not** the `docker compose` plugin.
- **The compose file defines three services** (`postgres`, `redis`, `backend`). There is no frontend service here; the `tapease-frontend`
  container in the Facts table is stale. `api-stg.tapease.com.au` resolves to the production frontend host's nginx (its certificate covers
  `api`, `api-stg` and `api-pos-stg`) and is served by this box.
- **Secrets Manager is off globally** (`USE_AWS_SECRETS_MANAGER` is not set). To read one secret, use a per-secret switch (for Clover OAuth:
  `CLOVER_OAUTH_USE_SECRETS_MANAGER=true`, which reads only `portal/clover-oauth/dev`). Turning the global flag on would change how every secret
  resolves, and the instance role is denied `portal/clover-sync/dev`.
- **Verify a specific migration:** run the deploy script with `TARGET_MIGRATION=<file.sql>` exported. It runs all pending SQL migrations and
  Alembic, then checks that migration is recorded.
- **Read-only checks without a secret:** `docker exec tapease-backend env | cut -d= -f1 | grep '^CLOVER'` lists names. To run a Python check inside
  the container, copy the script with `docker cp` and run `docker exec -e PYTHONPATH=/app -w /app tapease-backend python3 /tmp/x.py` (a script run by
  path has its own folder on `sys.path`, not the working directory). `docker exec` needs `-i` to read a script from stdin.
- **Building SSM `--parameters`:** write the remote script to a file and build the JSON with `python3 -c 'import json,sys; print(json.dumps({"commands":[open(sys.argv[1]).read()]}))'`.
  A `$(...)` inside a double-quoted local string runs on your machine, not the box.
- **Saved scripts:** the backend repo has `infra/staging-clover-oauth/` (`verify.sh` read only, `deploy.sh`, `configure_env.sh`, `selfcheck.sh`),
  guarded to the staging instance, the `dev` branch equal to `origin/dev`, and never a push.
- **Pushing `dev` cannot deploy production** (the CI deploy job needs `refs/heads/main`). Never put `[skip deploy]` in a `dev` commit.

## The prod boundary

- The SSM procedure above only ever targets `i-0f9a6ec659e6aab83` (staging).
- **Production = pushing `main`.** The CI job `deploy-to-ec2` in
  `.github/workflows/fast-feedback.yml` runs on every push to `main` once `lint` and
  `security-light` pass (skipped only by `[skip deploy]` in the commit message), builds
  an S3 bundle and deploys over SSM to `i-062b8ef5437ea6e2f`. There is no manual gate,
  so a push to `main` is irreversible-ish and outward-facing: only do it when the user
  has explicitly asked for production, and say plainly that the push deploys.
- Order that worked (2026-10-13, v4.3.24): commit on `dev` -> push `dev` -> SSM staging
  deploy -> check `https://api-stg.tapease.com.au/health` shows the new `version` ->
  `git checkout main && git pull --ff-only && git merge --ff-only dev && git push origin main`.
- Verify prod without AWS or `gh` (the Actions API returned 404 from the agent): poll
  `https://api.tapease.com.au/health` for the new `version`. Expect ~3 minutes of empty
  responses while the service restarts. `"status":"degraded"` is normal on both.
- Never "seed" production (see `tapease-db-access`), and a dev reseed wipes dev data;
  neither is part of a release, the deploy scripts never seed.
- Read the repo's `AGENTS.md` (§4, §7) before telling the user a deploy path is out of
  scope; it documents the prod path and the guardrails.
