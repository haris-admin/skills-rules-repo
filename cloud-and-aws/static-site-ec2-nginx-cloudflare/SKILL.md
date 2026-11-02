---
name: static-site-ec2-nginx-cloudflare
description: Deploy a static site (Next.js export or a single HTML file) to a shared EC2 nginx box behind Cloudflare, using SSM and a Cloudflare Origin certificate, and cut DNS over from a Cloudflare Worker without downtime. Use when asked to host a site or demo on an existing EC2 instance, add a hostname to the shared nginx, issue an origin certificate, or move a domain off Cloudflare Workers or Pages.
---

# Static site on a shared EC2 nginx box behind Cloudflare

Learned on ChargeRail (2026-11-01): `chargerail.com.au`, `www` and `demo` moved from a Cloudflare Worker to the `handledispute-frontend` box that also serves HandleDispute. Reference config: `ideas-ev-charging/infra/nginx/chargerail.conf`; hosting notes: `ideas-ev-charging/infra/README.md`.

## Before touching anything (read-only)
1. Find access: `aws configure list-profiles`, then `aws --profile <p> ssm describe-instance-information`. SSM Run Command works without SSH.
2. Inspect the box: `ss -ltnp`, `ls /etc/nginx/conf.d`, `nginx -T | grep -E "server_name|root|ssl_certificate"`. Note what else it serves. A shared box means a bad reload breaks the other site.
3. Inspect Cloudflare: list zones, DNS records, Worker custom domains (`accounts/<id>/workers/domains`), and the zone SSL mode. Mail, DKIM and verification records must not be touched.
4. Ask the owner which hostnames to move and whether the box may be shared. Moving the apex replaces a live site.

## Deploy steps
1. Build the static export locally (`npm run build`, output in `out/`).
2. Origin certificate: generate the key and CSR on the box (`openssl req -new -newkey rsa:2048 -nodes`), `umask 077`, key never leaves the box. Request the certificate from the Cloudflare API (`POST /certificates`, `request_type origin-rsa`, hostnames apex plus wildcard), then write only the signed public PEM to the box. Check the key and certificate modulus hashes match.
3. Transfer files: SSM cannot copy files. `tar czf`, base64, split into chunks of about 60,000 characters (the command parameter limit is about 97 KB), append each chunk to a file on the box, decode, then compare `sha256sum` with the local file. Extract into `/var/www/<site>/releases/<UTC timestamp>/` and symlink `current`. Keep the previous release for rollback.
4. nginx: add a separate file in `conf.d/`, never edit the other site's file. Back up `conf.d`, run `nginx -t`, reload only if it passes, otherwise remove the new file. Port 80 redirects to https, `www` redirects to the apex, `include /etc/nginx/cloudflare-ips.conf` with `real_ip_header CF-Connecting-IP` if the existing sites do.
5. Test on the box before DNS: `curl -sk --resolve host:443:127.0.0.1 https://host/`. The security group may allow 443 only from Cloudflare, so tests from a laptop fail. Also confirm the other site still returns 200.

## DNS cutover from a Worker (order matters)
- A record creation fails with "A DNS record managed by Workers already exists on that host" while a Worker custom domain holds the name.
- Removing the Worker custom domain removes its `AAAA 100::` records, so the name has no record until the new A record exists, and the site returns 530.
- Safest order: lower the gap by running both steps in one script, per hostname: delete the Worker custom domain, immediately create the proxied A record, then verify. Do apex last if reviewers are likely to visit. Have a rollback script ready (re-add the Worker custom domains, delete the A records).
- DELETE calls can return an empty body. Parsers must tolerate it (`json.loads` on empty text crashed the first cutover script and left the apex down).
- A 522 right after the change can be propagation. Re-check after 30 seconds and look for a leftover `AAAA 100::` record before changing anything.
- SSL mode `full` accepts a Cloudflare Origin certificate. Do not use `flexible`.

## Agent guardrails
- The auto mode classifier blocks DNS, certificate and domain changes. Do not work around it. Write a short executable script at a short path (for example `~/cf-cutover.sh`), run `bash -n` on it, set `chmod +x`, give the user `! ~/script.sh`, and tell them to delete it afterwards.
- Check that every script file has its execute bit and full content before handing it over (a script created by `>>` after a blocked command had no shebang and no `+x`).
- Cloudflare tokens come from AWS Secrets Manager into an environment variable inside the script. Never print a token or part of it. List only non-secret fields (zone names, ids, record names).
- In zsh, a variable holding `--profile x --region y` is not word split. Use a bash script file for AWS loops.
- Push, deploy and DNS changes need an explicit ask. State the downtime risk plainly before a cutover.

## Splitting products into containers and per-product edges
See `references/container-edge-split.md` (live-config capture, own port plus Cloudflare Origin Rule, proof-header gate, unique release ids).

## Verification checklist
- `curl -s -o /dev/null -w "%{http_code}"` for apex (200), `www` (301 to apex), demo (200), and the other site on the box (200).
- Page title, no console errors in Chrome, and no claims removed from the site reappear.
- Record the change in `context.md`, `docs/current_progress.md` and `infra/README.md` in the same session.
