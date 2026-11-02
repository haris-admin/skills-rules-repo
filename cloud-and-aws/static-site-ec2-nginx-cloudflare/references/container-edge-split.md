# Moving a shared nginx host to per-product containers and edges (handledispute, 2 Nov 2026)

Use when one EC2 nginx serves several products behind Cloudflare and you want each product self-contained and liftable.

## Read the live host first
- Capture the LIVE nginx config from the host (`cat /etc/nginx/conf.d/*.conf` over SSM). The repo copy had drifted: the live ChargeRail config also served `demo.chargerail.com.au`, which the repo version did not. Reproduce live behaviour, not the repo.
- Note every product on the box and who deploys it. Swapping the host nginx for a container takes ALL of them down for seconds.

## Shape
- One edge container per product, each with its own configs, certs (mount only that product's pair), network, container names and deploy folder (`infra/frontend/<product>/`).
- HandleDispute took its own public port 8443 (Cloudflare supports 8443); ChargeRail kept 80 and 443. A Cloudflare Origin Rule (phase `http_request_origin`, action `route`, `origin.port`) sends only that product's hostnames to the new port. A PUT replaces the whole phase, so read and MERGE existing rules; identify your rule by a description marker.
- Security group: add ingress for the new port from the Cloudflare IPv4 and IPv6 lists only (same `for_each` as 443). Never 0.0.0.0/0.
- Do NOT change instance `user_data` when `user_data_replace_on_change = true`; it replaces the instance and loses certs. Install Docker over SSM at deploy time.
- Images: `linux/amd64`, `docker save | gzip`, sha256, upload to the private releases bucket, `docker load` over SSM. Use a NEW release id for any change: a script that compares the running image tag skips the recreate when the tag is unchanged.

## Order (no outage)
1. Terraform plan read-only, founder applies (the auto-mode classifier blocks agent applies).
2. Start the new edge on its own port, stage a test copy on a loopback port, check every hostname with `curl --resolve`, unknown host dropped, headers present.
3. Create the Origin Rule (dry run first, apply separately), verify through Cloudflare.
4. The old shared edge is removed last, and only after a proof gate: the new edge stamps a header (`X-HD-Edge: 8443`) and the cutover script refuses to continue until the public site returns it.
5. Roll back by removing the new edge or the rule; the old edge keeps serving until step 4. Keep host nginx stopped (not deleted) as the last-resort fallback.

## After
- The Cloudflare IP refresh script must reload every running edge container, never start host nginx, and write the shared file in place (a replaced single-file bind mount goes stale).
- Run a read-only status script across both instances and verify from outside (public URLs, not `--resolve`).
- Another session may deploy to the same boxes: re-read container state before assuming it is as you left it.
