# Cloudflare Worker Click Tracker Pattern

Deploy when running ad campaigns (FB/IG/YT) and needing click attribution + conversion tracking without a third-party SaaS.

## Architecture

```
Ad → go.amlhive.com.au/click?c=CAMPAIGN&s=SOURCE&t=/path
     ↓
Cloudflare Worker logs click to KV
     ↓
Redirects to target URL with UTM params enriched
     ↓
Page loads → AdTracker component fires sendBeacon conversion event
```

## Files Created (Jul 2026 — amlhive-tech/amlhive1 on `dev`)

| File | Purpose |
|---|---|
| `workers/click-tracker/src/index.ts` | Worker: KV logging, rate limiting (100/IP/min), UTM enrichment, scheduled daily aggregation |
| `workers/click-tracker/wrangler.toml` | Config: dev/prod envs, KV namespace binding |
| `workers/click-tracker/package.json` | Deploy: `npm run deploy:dev` / `deploy:prod` |
| `frontend/lib/tracking.ts` | Tracking link builder + pre-built campaign presets (TRAN2, FREE, DEMO, SIGNUP, AUDIT, GUIDE) |
| `frontend/components/AdTracker.tsx` | Client-side conversion beacon — place on landing/signup/guide pages |

## Campaign Code Reference

| Code | Campaign | Source Examples |
|---|---|---|
| TRAN2 | Tranche 2 Compliance Guide | fb, ig, yt, go |
| FREE | Free Compliance Check | fb, ig |
| DEMO | Product Demo | yt, li |
| SIGNUP | Direct Signup | fb, go |
| AUDIT | Free Audit Offer | fb, li |
| GUIDE | Downloadable Guide | fb, ig |

## UTM Enrichment

The Worker appends these to every redirect URL:
- `utm_source` — from the `s` param
- `utm_medium` — from the `m` param (default: `paid`)
- `utm_campaign` — from the `c` param
- `utm_content` — from the `ct` param (creative variant)
- `utm_term` — from the `g` param (conversion goal)

## Why Cloudflare Workers (not a SaaS)

- **Cost:** $0 on existing Cloudflare plan (free tier includes 100K requests/day)
- **Data residency:** Runs on Cloudflare's global edge, not a third-party tracking company
- **No new vendor:** Uses Cloudflare DNS + Workers already provisioned for the domain
- **Full control:** Customize logging, rate limits, redirect logic without platform limits
