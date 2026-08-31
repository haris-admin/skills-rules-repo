---
name: deploy-frontend
description: >
  The sanctioned procedure for deploying the Tap-Ease frontend to production and
  verifying it is actually serving. Use when asked to "deploy", "ship", "release",
  "push to prod", or "cut a build" for this repo, or to verify a deploy that just
  ran. Covers the GitHub Actions path, the manual SSM path, post-deploy smoke
  checks, and rollback.
---

# Deploy the Tap-Ease frontend

Production is a single EC2 instance with no ALB — a bad deploy or a bad nginx reload
takes the whole site down. The 2026-08-29 outage
(`context/RCA-2026-08-29-nginx-502-outage.md`) is why this procedure exists.

## Facts

| | |
|---|---|
| Live branch | `master` |
| Prod EC2 | `i-0aca7e109d0f6e773` (`tapease-frontend-production`), `ap-southeast-2` |
| App runtime | Next.js standalone, PM2 process `tapease-frontend`, `127.0.0.1:3000` |
| Public URL | `https://tapease.com.au` |
| Pipeline | `.github/workflows/deploy.yml` → `s3://tapease-objects/frontend_package/<YYYYMMDD>/` → SSM → `scripts/deploy_from_s3.sh` on the box |
| Scope | pipeline deploys the **app only** — nginx is separate, see the `nginx-change` skill |

## Pre-deploy

1. `git fetch && git log --oneline origin/master -5` — confirm the commit you intend
   to ship is on top of `master`. The pipeline triggers on push to `master`/`main`.
2. `git status` clean. You are not shipping unrelated local work.
3. `npm run test:ci` locally — **note**: `deploy.yml` runs `npm run test || echo
   "Tests failed but continuing deployment"`, so CI will NOT stop a red suite. You
   are the gate.
4. `npm run build` locally if the change is non-trivial — catch build breaks before
   the runner does.
5. Know the current live version and the previous S3 package (rollback target):
   `aws s3 ls s3://tapease-objects/frontend_package/`.

## Deploy — GitHub Actions (normal path)

1. Merge to `master` (or `workflow_dispatch` with a `version` of `YYYYMMDD`).
2. Watch the run. Do not trust the green tick alone — open the **"Verify
   deployment"** step log and confirm its curl to `https://tapease.com.au/` actually
   returned success (the step is non-fatal).

## Deploy — manual SSM (pipeline broken / hotfix)

```bash
# build + package locally per README, upload to S3, then on the box via SSM:
aws ssm send-command --region ap-southeast-2 --instance-ids i-0aca7e109d0f6e773 \
  --document-name AWS-RunShellScript \
  --parameters commands='sudo -u ec2-user bash /home/ec2-user/scripts/deploy_from_s3.sh <YYYYMMDD>'
```

Prefer base64-encoding any multi-line script and piping to `base64 -d | bash` — raw
heredoc/quoted commands through SSM mangle `$` (this is how the nginx outage
happened).

## Post-deploy — REQUIRED, do every one

1. `scripts/postdeploy-smoke.sh` exits 0:
   - `https://tapease.com.au/` → 200
   - `https://tapease.com.au/next-api/health` → 200
   - `http://tapease.com.au/` → 301, `Location: https://tapease.com.au/` exact (no `\`)
   - on box: `http://localhost:3000/next-api/health` → 200
   - redirect-followed → 200
2. Via SSM on `i-0aca7e109d0f6e773`:
   - `sudo -u ec2-user pm2 list` → `tapease-frontend` `online`, restart count (↺) flat
   - `sudo -u ec2-user pm2 logs tapease-frontend --lines 40 --nostream` → clean start
   - `sudo tail -n 40 /var/log/nginx/tapease-error.log` → no `upstream prematurely
     closed connection`
   - `sudo cat /home/ec2-user/app/package.json | grep version` → matches intended commit
3. Load `https://tapease.com.au/` in a browser: logged out (landing renders) and
   logged in (dashboard + one successful API call).
4. Watch the error log for 2 minutes.

"Deployed" = steps 1–4 pass. Not "pipeline green".

## Rollback (app)

```bash
# previous packages: s3://tapease-objects/frontend_package/<YYYYMMDD>/
aws ssm send-command --region ap-southeast-2 --instance-ids i-0aca7e109d0f6e773 \
  --document-name AWS-RunShellScript \
  --parameters commands='sudo -u ec2-user bash /home/ec2-user/scripts/deploy_from_s3.sh <PREVIOUS-YYYYMMDD>'
```
then re-run `scripts/postdeploy-smoke.sh`.

## If nginx is involved

Stop. Use the `nginx-change` skill / `scripts/safe-nginx-reload.sh`. Never hand-edit
`/etc/nginx/conf.d/tapease.conf`.
