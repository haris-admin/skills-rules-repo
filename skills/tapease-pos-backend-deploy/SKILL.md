---
name: tapease-pos-backend-deploy
description: >-
  Deploy and verify the Tap-Ease POS terminal backend (repo tapease-termianl-pos-app, FastAPI under backend/) on staging (api-pos-stg) and production (api-pos) over SSM. Use when asked to deploy the POS backend, push a receipt or shift report PDF change to staging or production, verify a POS backend release, or read production health read-only. Not for the Portal backend (see tapease-backend-deploy).
---

# Deploy the Tap-Ease POS terminal backend (staging and production)

The POS backend is a separate service from the Portal backend. App and backend are released as a pair at the same version number (for example both 1.1.12), so a layout or config fix that does not change the API stays at the same version and is proven by the commit on the box.

## Facts

| | Staging | Production |
|---|---|---|
| URL | `https://api-pos-stg.tapease.com.au` | `https://api-pos.tapease.com.au` |
| Instance (ap-southeast-2) | `i-0f9a6ec659e6aab83` (host port 8001 behind nginx) | `i-0bed5e09655e73872` (RDS Postgres, Multi-AZ) |
| Branch it pulls | `dev` | `main` |
| Deploy script on the box | `backend/scripts/deploy_docker.sh dev` | `backend/scripts/deploy_rds_docker.sh main` |
| Checkout on the box | `/opt/tapease/terminal-backend` (origin is GitHub) | same path |
| Container | `tapease-terminal-backend` | `tapease-terminal-backend` |

The scripts read their own secrets from Secrets Manager and print none. A deploy with no migration is a container restart of about a minute.

## Procedure

1. **Land the code.** Tests green (`pytest tests/unit -m "not integration"` with a dummy `DATABASE_URL`, `PDF_SIGNING_SECRET`; set no `PUBLIC_BASE_URL`), commit, fast-forward `dev` (and `main` for production) and `git push origin <branch>`. Check `git merge-base --is-ancestor origin/<branch> HEAD` first and list `git log origin/<branch>..HEAD`.
2. **Staging first.** Write a small remote script (git fetch, checkout dev, `pull --ff-only`, echo `BOX_HEAD`, run the deploy script, echo `BOX_HEAD_AFTER`). Build the SSM parameters with `python3 -c 'import json,sys; print(json.dumps({"commands":[open(sys.argv[1]).read()]}))' script.sh > p.json` and send `aws ssm send-command --region ap-southeast-2 --instance-ids <id> --document-name AWS-RunShellScript --timeout-seconds 900 --comment "<what>" --parameters file://p.json`. Poll `get-command-invocation` until the status leaves InProgress.
3. **Verify staging:** `/health` shows status ok, database reachable, the version, `environment: staging`, `sentry.enabled`; `BOX_HEAD` equals the pushed commit; for a code change, prove it inside the container (below).
4. **Production only when the owner asks for it**, and say plainly that it restarts the live service. Take a read-only look first (remote, branch, HEAD, container status, health). Then run the same script with `main` and `deploy_rds_docker.sh`.
5. **Verify production read-only, counts only:** `/health` (version, environment production, `sentry.enabled`, portal credentials configured), the container uptime, and COUNTS of `Traceback` and ` 500 ` in `docker logs --since 6m`. Never print production log lines; they hold customer data.

## Proving a change inside the container (no secrets printed)

Write a Python script, base64 it, and run it with `echo <b64> | base64 -d > /tmp/x.py && docker cp /tmp/x.py tapease-terminal-backend:/tmp/x.py && docker exec -e PYTHONPATH=/app -w /app tapease-terminal-backend python3 /tmp/x.py`. To render real receipts, import the app, build the signed link with `build_signed_receipt_url` and fetch it in-process with `httpx.AsyncClient(transport=ASGITransport(app=app))`, so no link is printed. Select trips with a read-only query.

## Gotchas

- **SSM output is capped at about 24 KB**: move one PDF (base64) per command; two truncate and the second will not open.
- Running the app code in the container makes Sentry report a pending event on exit; mention it.
- A per-terminal setting can hide a feature on a test device: `terminal_configs` holds `(serial_number, key)` overrides over the fleet default (`""`). The staging Dev Kit has `show_outcome_before_receipt = false`.
- No `.github` workflows in this repo: a push does not deploy; the deploy is the SSM script.
- Never force-push; tags are additive (see the release-tags rule). The auto-mode classifier blocks destructive git steps and may block mutating production commands: do not work around it, hand the owner a short script.
- Keep the 1.1.x pairing: do not bump only the backend version unless the app is released with it.
