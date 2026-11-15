# After pointing Cloudflare at a new origin: expect a short 522, prove the certificate, and test for a real 404 (all agents, all repos)

Applies when a site moves to a new origin host behind Cloudflare.

## Why this exists
**15 Nov 2026 (ChargeRail):** right after the DNS switch the owner saw a Cloudflare "Host Error" (522) while the origin answered 200 locally; five minutes later every request passed. The same cutover found an edge config that served `/404.html` with status 200 for any missing page, which only a live test with a missing path showed.

## Rules
1. Build and test the origin first, with a placeholder certificate and `curl --resolve host:443:127.0.0.1` on the box (Cloudflare-only firewalls block tests from a laptop). Then install the Origin CA certificate with a script whose private key is generated on the box and never leaves it, verify the issuer and SAN, and refuse the DNS switch while the placeholder is in place (Full strict).
2. The DNS switch is a dry run by default that lists every change and any CNAME or AAAA conflict; the owner applies it. Proxied records change quickly, but a brief 522 while Cloudflare drops the old origin is normal: retest several times before debugging, and read the edge log to see Cloudflare addresses arrive.
3. Test one missing path on the live host and expect 404 (use `try_files ... =404` and `error_page 404 /404.html`), unknown Hosts dropped, http redirected, `www` redirected, and security headers on the site root only.
4. Generate the edge config from a template in the repo with a pure render function and tests (including the Cloudflare ranges read from the same Terraform file as the firewall), not by patching a live file in place.
