# AMLHive Website Monitor (Created Jul 27, 2026)

Cron job at 07:00 AEST (job_id: 8d3be30eb9f7), script: `amlhive_website_monitor.py`

## Pages Monitored

| Page | Path | Expected |
|------|------|----------|
| Homepage | `/` | 200 |
| LLMS | `/llms.txt` | 200 |
| LLMS Full | `/llms-full.txt` | 200 |
| Agent Card | `/.well-known/agent-card.json` | 200 |
| Sitemap | `/sitemap.xml` | 200 |
| Pricing | `/pricing` | 404 (known — anchor section, not separate route) |
| Compliance Blog | `/compliance-blog` | 404 (known — anchor section) |

## SSL

- Expires: 2026-09-25 (59 days as of Jul 27)
- Uses Cloudflare

## Site Info

- Served via Cloudflare (HTTP/2, HSTS)
- Next.js App Router (RSC, Turbopack)
- Structured data: Organization, WebSite, SoftwareApplication (JSON-LD)
- Pricing: Starter $149/mo, Professional $299/mo
- Social: LinkedIn, Facebook, X, Reddit, f6s
- ABN: 49 696 485 015
