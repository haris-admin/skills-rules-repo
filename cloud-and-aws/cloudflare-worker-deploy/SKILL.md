---
name: cloudflare-worker-deploy
description: Deploy, route, and manage Cloudflare Workers, KV bindings, and R2 storage buckets.
---

# Cloudflare Workers & Edge Infrastructure

## Guidelines
- Manage Worker configurations via `wrangler.toml`.
- Configure custom domains, edge routing, and caching rules.
- Maintain separate development and production KV namespaces and R2 buckets.
- Purge Cloudflare edge caches immediately following public asset or CMS deployments.

