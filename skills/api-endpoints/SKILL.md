---
name: api-endpoints
description: >
  Canonical reference for every Tap-Ease API base URL — which host serves what,
  which one to hand to the iOS/Android/M2M teams, which one the frontend itself
  uses, and how to verify each is healthy. Use when someone asks "what's the API
  URL", "what do I give the app devs", "is the API up", "should we use
  tapease.com.au/api", or is changing NEXT_PUBLIC_API_URL / the API routing.
---

# Tap-Ease API endpoints

## The map

| Base URL | Serves | TLS | Who uses it |
|---|---|---|---|
| `https://api.tapease.com.au` | **production** backend (`10.0.2.161:80` via nginx on the frontend box) | LE SAN cert | **iOS app, Android app, M2M partners** — this is the one to hand out |
| `https://api-stg.tapease.com.au` | **staging** backend (`3.26.61.230:8000`) | same SAN cert | app/partner staging + QA |
| `http://10.0.2.161:80/` | production backend, internal VPC, no TLS | — | **only** the frontend's server-side proxy (`NEXT_PUBLIC_API_URL`) |
| `https://tapease.com.au/api/` | production backend (legacy passthrough) | site cert | retained for backward-compat; **do not hand out** — couples callers to the website's nginx |
| `http://localhost:8000` | local dev backend | — | local development |

Swagger UI at `/docs`, schema at `/openapi.json`, liveness at `/health` on every
backend host.

## Rules

- **Give external teams `https://api.tapease.com.au` / `https://api-stg.tapease.com.au`.**
  Not `tapease.com.au/api`. Tell them to keep the base URL a single config value.
- **Never set `NEXT_PUBLIC_API_URL` to a public `https://` URL.** The frontend proxy
  runs *on* the frontend box; the internal `http://10.0.2.161:80/` is same-VPC, no
  TLS, lowest latency. A public URL would hairpin every call out through the edge
  nginx + a TLS handshake.
- There is **no load balancer**. Both `api.*` subdomains are A-records to the
  frontend box `13.210.208.34`; nginx there proxies to the backends. A bad nginx
  reload on that box takes down the site *and* the API — always use
  `scripts/safe-nginx-reload.sh` (see the `nginx-change` skill).
- The production backend is a **single EC2 instance** (`i-062b8ef5437ea6e2f`,
  `tapease-backend.service`) with a history of crash-loops and no reliable
  auto-restart. Treat backend availability as the weak link, not the frontend.

## Verify

```bash
# production — expect 200, "environment":"production", "database":"ok"
curl -sS https://api.tapease.com.au/health
# staging — expect 200, "environment":"dev"
curl -sS https://api-stg.tapease.com.au/health
# correct behaviour (not just liveness): empty login must be 422, not 502/500
curl -sS -o /dev/null -w '%{http_code}\n' -X POST https://api.tapease.com.au/auth/login \
  -H 'content-type: application/json' -d '{}'
# HTTP -> HTTPS
curl -sS -I http://api.tapease.com.au/ | grep -i '^location'
```

A `502` from `api.tapease.com.au` with `content-length: 157` (bare nginx page) means
the **backend** is down/redeploying — check `tapease-backend.service` on
`i-062b8ef5437ea6e2f`, not the frontend. If the whole `tapease.com.au` site is also
502, it's the frontend nginx — see the `nginx-change` skill and the RCA.

## Config locations

- nginx vhosts: `infra/nginx/tapease-api-subdomains.conf` (mirror of
  `/etc/nginx/conf.d/tapease-api-subdomains.conf` on `i-0aca7e109d0f6e773`)
- `NEXT_PUBLIC_API_URL`: `.env_example` (base), `.env.local` on the box (built by
  `deploy.yml` from `.env_example` + AWS secrets)
- frontend consumer: `src/app/next-api/proxy/route.js`, `src/proxy.js`
