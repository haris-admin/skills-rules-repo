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
| API TLS | one SAN cert `/etc/letsencrypt/live/api.tapease.com.au/` covers both `api.` + `api-stg.` |

The root `location /` in the **`tapease.com.au`** `443` server **must** proxy to
`localhost:3000`. The `api.*` vhosts legitimately proxy their root to a backend —
`preflight-nginx.sh` check 4 skips them by server_name.

## Procedure

1. **Read** `infra/nginx/README.md`, `infra/nginx/HARDENING.md`, and the file you
   will change (`tapease.conf` for the site / redirects / app routes;
   `tapease-api-subdomains.conf` for `api.tapease.com.au` / `api-stg.tapease.com.au`).
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
7. Push the file and apply (`safe-nginx-reload.sh` copies your file to the right
   live path based on its name):
   ```bash
   # base64 upload (NOT heredoc — heredoc re-escapes $)
   B64=$(base64 -i "infra/nginx/$FILE" | tr -d '\n')
   CID=$(aws ssm send-command --region ap-southeast-2 --instance-ids i-0aca7e109d0f6e773 \
     --document-name AWS-RunShellScript \
     --parameters commands="echo $B64 | base64 -d | sudo tee /tmp/$FILE.new >/dev/null && sudo bash /home/ec2-user/scripts/safe-nginx-reload.sh /tmp/$FILE.new" \
     --query Command.CommandId --output text)
   # then get-command-invocation and read the full output
   ```
8. Read `safe-nginx-reload.sh` output: preflight PASS, smoke PASS. If it auto-rolled
   back, the change is rejected — read the failing check and fix the repo file.
9. Independently verify (site + both API subdomains, whichever you touched):
   ```bash
   curl -sS -I https://tapease.com.au/                          # 200
   curl -sS -I http://tapease.com.au/ | grep -i location        # https://tapease.com.au/  (no backslash)
   curl -sS -o /dev/null -w '%{http_code}\n' https://tapease.com.au/next-api/health   # 200
   curl -sS https://api.tapease.com.au/health                   # 200, "environment":"production"
   curl -sS https://api-stg.tapease.com.au/health               # 200, "environment":"dev"
   ```
10. Watch `sudo tail -f /var/log/nginx/{tapease-error,api-error,api-stg-error}.log`
    ~2 min — no `upstream prematurely closed connection` / `connect() failed`.
11. **Commit `infra/nginx/$FILE`** once the box is verified healthy.

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
