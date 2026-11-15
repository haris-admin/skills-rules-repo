# After pointing Cloudflare at a new origin: expect a short 522, prove the certificate, and test for a real 404 (all agents, all repos)

Applies when a site moves to a new origin host behind Cloudflare.

## Why this exists
**15 Nov 2026 (ChargeRail):** right after the DNS switch the owner saw a Cloudflare "Host Error" (522) while the origin answered 200 locally; five minutes later every request passed. The same cutover found an edge config that served `/404.html` with status 200 for any missing page, which only a live test with a missing path showed.

## Rules
1. Build and test the origin first, with a placeholder certificate and `curl --resolve host:443:127.0.0.1` on the box (Cloudflare-only firewalls block tests from a laptop). Then install the Origin CA certificate with a script whose private key is generated on the box and never leaves it, verify the issuer and SAN, and refuse the DNS switch while the placeholder is in place (Full strict).
2. The DNS switch is a dry run by default that lists every change and any CNAME or AAAA conflict; the owner applies it. Proxied records change quickly, but a brief 522 while Cloudflare drops the old origin is normal: retest several times before debugging, and read the edge log to see Cloudflare addresses arrive.
3. Test one missing path on the live host and expect 404 (use `try_files ... =404` and `error_page 404 /404.html`), unknown Hosts dropped, http redirected, `www` redirected, and security headers on the site root only.
4. Generate the edge config from a template in the repo with a pure render function and tests (including the Cloudflare ranges read from the same Terraform file as the firewall), not by patching a live file in place.
5. **Check the zone settings, not only the origin.** After the ChargeRail cutover the zone had Always Use HTTPS off and a minimum TLS of 1.0. In Full or Full (strict) mode Cloudflare sends an http visitor to the origin on port 80, so with a Cloudflare-only firewall that closes 80, `http://site` hangs for ever. Turn Always Use HTTPS on and raise the minimum TLS to 1.2 with a script that reads before and after, tests https, http and the API, retries while the change propagates, and restores the old values on a failed check.
6. **Post-change checks written in Python must set their own User-Agent.** Cloudflare blocks `Python-urllib`, so a health check of a healthy site reported failure and the script (correctly) reverted. Test the constant, not only the logic.
7. **A restore drill restores into a scratch database inside the same Postgres container** (never the live one): newest off-box backup, `gzip -t`, `createdb`, restore with `ON_ERROR_STOP`, count tables, always `dropdb` in a trap, print the seconds. Run it for real once the nightly timer exists, and repeat it once there is data: an empty database proves the pipeline, not fidelity.
8. **Secrets that lack `POSTGRES_USER` and `POSTGRES_DB` make the Postgres image run as `postgres`**, and a dump script using `$POSTGRES_USER` then runs `pg_dump -U ""` as root and fails. Default both in every backup and restore script, and test with the variables unset. A readiness check that only opens the port never proves a login.
