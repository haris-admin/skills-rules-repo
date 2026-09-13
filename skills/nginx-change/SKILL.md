---
name: nginx-change
description: >
  How to safely change the production edge nginx config for tapease.com.au — add a
  location/route, change an upstream, adjust headers/SSL/redirects. Use for any
  request that touches the reverse proxy in front of the Tap-Ease frontend. Enforces:
  edit the repo mirror, never the box; grep for over-escaped variables; apply only
  via scripts/safe-nginx-reload.sh with auto-rollback.
---

# Change the edge nginx config

On 2026-08-29 a hand edit to the live config double-escaped every nginx variable
(`$host` → `\$host`). `nginx -t` passed. nginx then sent literal `$http_upgrade` /
`Connection: upgrade` to the app, Node closed the socket, and `tapease.com.au`
returned 502 site-wide for 47 minutes. This skill exists so that cannot recur. Full
write-up: `context/RCA-2026-08-29-nginx-502-outage.md`. Process rules:
`context/deployment-safety-rules.md`.

## Facts

| | |
|---|---|
| Repo mirrors (edit THESE) | `infra/nginx/tapease.conf` (site), `infra/nginx/tapease-api-subdomains.conf` (API subdomains) |
| Live files (never hand-edit) | `/etc/nginx/conf.d/tapease.conf` + `/etc/nginx/conf.d/tapease-api-subdomains.conf` on EC2 `i-0aca7e109d0f6e773` (`ap-southeast-2`) |
| Apply tool | `scripts/safe-nginx-reload.sh` (backup → preflight → reload → smoke → auto-rollback) — pass it the file you changed |
| Validators | `scripts/preflight-nginx.sh <file>`, `scripts/postdeploy-smoke.sh [base-url]` |
| App upstream | `http://localhost:3000` (Next.js standalone, PM2 `tapease-frontend`) |
| `tapease.com.au/api/` upstream | `http://10.0.2.161:80/` (prod backend) — legacy path |
| `tapease.com.au/stg-api/`, `/stage-api/` | `http://3.26.61.230:8000/` (dev backend) |
| `api.tapease.com.au/` | `http://10.0.2.161:80/` (prod backend) — canonical public API |
| `api-stg.tapease.com.au/` | `http://3.26.61.230:8000/` (staging backend) |
| `api-pos-stg.tapease.com.au/` | `http://3.26.61.230:8001/` (POS staging backend — same box as api-stg, different dev port) |
| API TLS | one SAN cert `/etc/letsencrypt/live/api.tapease.com.au/` covers `api.` + `api-stg.` + `api-pos-stg.` |
| DNS | Route53 zone `tapease.com.au.` (`Z03467402O9680BIPVEOP`). Every `api*` name is an A-record to `13.210.208.34` — same frontend box, never the backend's own IP. |
| Deploy scripts on the box | **NOT pre-staged.** `/home/ec2-user/scripts/safe-nginx-reload.sh` does not exist — the app deploy only ships the Next.js build, not `infra/`. Upload `safe-nginx-reload.sh` + `preflight-nginx.sh` + `postdeploy-smoke.sh` together to a scratch dir (e.g. `/tmp/nginx-safe-reload/`) before every use; they must sit in the same directory (the script finds its deps via its own dirname). See step 7. |

The root `location /` in the **`tapease.com.au`** `443` server **must** proxy to
`localhost:3000`. The `api.*` vhosts legitimately proxy their root to a backend —
`preflight-nginx.sh` check 4 skips them by server_name.

## Procedure

1. **Read** `infra/nginx/README.md`, `infra/nginx/HARDENING.md`, and the file you
   will change (`tapease.conf` for the site / redirects / app routes;
   `tapease-api-subdomains.conf` for `api.tapease.com.au` / `api-stg.tapease.com.au` /
   `api-pos-stg.tapease.com.au`).
2. **Sync check** — confirm the mirror still matches the box (`FILE` = the one you're
   changing):
   ```bash
   FILE=tapease.conf   # or tapease-api-subdomains.conf
   CID=$(aws ssm send-command --region ap-southeast-2 --instance-ids i-0aca7e109d0f6e773 \
     --document-name AWS-RunShellScript \
     --parameters commands="sudo cat /etc/nginx/conf.d/$FILE" \
     --query Command.CommandId --output text)
   sleep 6
   aws ssm get-command-invocation --command-id "$CID" --instance-id i-0aca7e109d0f6e773 \
     --region ap-southeast-2 --query StandardOutputContent --output text > /tmp/live.conf
   diff -u "infra/nginx/$FILE" /tmp/live.conf
   ```
   If they differ, reconcile first (update the mirror from the box, commit) before
   making your change.
3. **Edit `infra/nginx/$FILE`** — smallest change possible.
4. `git diff infra/nginx/` — review every line with the user.
5. **`grep -n '\\$' infra/nginx/$FILE` → must be empty.** Any `\$` is an
   over-escaped variable = the outage bug. Also run
   `scripts/preflight-nginx.sh infra/nginx/$FILE` (skip the `nginx -t` line — it
   only runs on the box).
6. Check every `proxy_pass` against the upstream table above.
7. Push the file **and the three deploy scripts** (they are not pre-staged on the
   box — see Facts) and apply (`safe-nginx-reload.sh` copies your file to the right
   live path based on its name):
   ```bash
   # base64 upload (NOT heredoc — heredoc re-escapes $). Build ONE outer script
   # locally that embeds all four base64 blobs (three scripts + your conf), so
   # the whole thing goes over SSM as a single command:
   #   mkdir -p /tmp/nginx-safe-reload
   #   echo '<safe-nginx-reload.sh b64>'  | base64 -d > /tmp/nginx-safe-reload/safe-nginx-reload.sh
   #   echo '<preflight-nginx.sh b64>'    | base64 -d > /tmp/nginx-safe-reload/preflight-nginx.sh
   #   echo '<postdeploy-smoke.sh b64>'   | base64 -d > /tmp/nginx-safe-reload/postdeploy-smoke.sh
   #   echo '<infra/nginx/$FILE b64>'     | base64 -d > /tmp/nginx-safe-reload/$FILE.new
   #   chmod +x /tmp/nginx-safe-reload/*.sh
   #   cd /tmp/nginx-safe-reload && sudo bash safe-nginx-reload.sh /tmp/nginx-safe-reload/$FILE.new
   # base64-encode that outer script itself and send ONE SSM command:
   #   echo '<outer b64>' | base64 -d > /tmp/remote-apply.sh && bash /tmp/remote-apply.sh
   # (all comfortably under SSM's ~100KB command-size limit for these files)
   CID=$(aws ssm send-command --region ap-southeast-2 --instance-ids i-0aca7e109d0f6e773 \
     --document-name AWS-RunShellScript \
     --parameters file://params.json \
     --query Command.CommandId --output text)
   # then get-command-invocation and read the full output
   ```
   If the SSM command instead reports `bash: .../safe-nginx-reload.sh: No such
   file or directory`, that confirms the scripts aren't on the box yet — stage
   them per the above, don't assume a stale path from a previous session.
8. Read `safe-nginx-reload.sh` output: preflight PASS, smoke PASS. If it auto-rolled
   back, the change is rejected — read the failing check and fix the repo file.
9. Independently verify (site + all API subdomains, whichever you touched):
   ```bash
   curl -sS -I https://tapease.com.au/                          # 200
   curl -sS -I http://tapease.com.au/ | grep -i location        # https://tapease.com.au/  (no backslash)
   curl -sS -o /dev/null -w '%{http_code}\n' https://tapease.com.au/next-api/health   # 200
   curl -sS https://api.tapease.com.au/health                   # 200, "environment":"production"
   curl -sS https://api-stg.tapease.com.au/health               # 200, "environment":"dev"
   curl -sS https://api-pos-stg.tapease.com.au/health           # 200, matches http://3.26.61.230:8001/health
   ```
10. Watch `sudo tail -f /var/log/nginx/{tapease-error,api-error,api-stg-error}.log`
    ~2 min — no `upstream prematurely closed connection` / `connect() failed`.
11. **Commit `infra/nginx/$FILE`** once the box is verified healthy.

## Adding a new API subdomain (e.g. `api-pos-stg.tapease.com.au`)

Same box, no load balancer — DNS always points at the frontend box; only nginx's
`proxy_pass` decides which backend a name actually reaches. Order matters:

1. **DNS first** — create the A-record (Route53 zone `Z03467402O9680BIPVEOP`,
   `tapease.com.au.`), value `13.210.208.34`, TTL 300, same as the existing
   `api*` records. Confirm `INSYNC` and that it resolves publicly
   (`dig +short <name> @8.8.8.8`) before touching the cert — certbot's HTTP-01
   challenge needs the name to resolve.
2. **Expand the SAN cert** (needs the plugin flag; `--non-interactive` alone
   fails with "Missing command line flags"):
   ```bash
   sudo certbot certonly --webroot -w /var/www/certbot \
     --cert-name api.tapease.com.au --expand \
     -d api.tapease.com.au -d api-stg.tapease.com.au -d <new-name> \
     --non-interactive
   ```
   `--expand` on the existing `--cert-name` is required — omitting it creates a
   second, separate cert lineage instead of adding a SAN to the one both
   existing vhosts reference.
3. **nginx** — add a new `listen 80` (redirect + ACME challenge) / `listen 443`
   pair to `infra/nginx/tapease-api-subdomains.conf`, copying the `api-stg`
   block and changing only `server_name`, `proxy_pass`, and the log filenames.
   Apply via the normal Procedure above (step 7 onward).
4. Expect a `preflight-nginx.sh` check-5 `WARN` ("unrecognised upstream") the
   first time — its known-upstream list doesn't have the new host:port yet.
   That's a warning, not a FAIL; add the upstream to the validator's allowlist
   as a follow-up so future reloads of this file go fully green.
5. Verify the new name matches the backend directly
   (`curl https://<new-name>/health` vs `curl http://<backend-ip>:<port>/health`
   — bodies should match) before calling it done. Until nginx is reloaded with
   the new server block, the name will silently fall through to whichever vhost
   nginx treats as default (in practice `api.tapease.com.au`, i.e. production) —
   don't mistake that for a DNS problem.

Note: if working inside an auto-mode agent session, read-only SSM commands
against this box (even `certbot certificates`) can be blocked by the harness's
own permission classifier ("Production Reads"). That's a session-level
restriction, not an AWS/IAM permission problem — it needs an explicit
human-in-the-loop approval, not a workaround.

## Manual rollback (if needed)

```bash
aws ssm send-command --region ap-southeast-2 --instance-ids i-0aca7e109d0f6e773 \
  --document-name AWS-RunShellScript --parameters commands='
    LATEST=$(ls -1t /etc/nginx/conf.d/tapease.conf.bak-* | head -1)
    sudo cp -a "$LATEST" /etc/nginx/conf.d/tapease.conf
    sudo nginx -t && sudo systemctl reload nginx'
```

## Never

- `vi` / `nano` / `sed -i` / `cat >` on `/etc/nginx/conf.d/tapease.conf`.
- `systemctl reload nginx` directly.
- Trust `nginx -t` as sufficient. The smoke test is the gate.
- Build the config on the box with an interpolating heredoc.
