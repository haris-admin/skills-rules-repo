---
name: website-uptime-monitor
description: "HTTP health checks: status, SSL, response times."
version: 1.0.0
author: Pluto
license: MIT
category: devops
---

# ★ Website Uptime Monitor

## When to Use

- Setting up daily/new HTTP health monitoring for a public website
- Adding SSL expiry checks to an existing monitoring pipeline
- Creating a cron-based website watchdog (no_agent script pattern)
- Monitoring key pages beyond just the homepage (pricing, blog, API docs, etc.)

## Architecture

```
no_agent cron → script → curl checks → stdout delivery to chat
```

Each website gets:
- **Script:** `~/.hermes/scripts/<project>_website_monitor.py` — no_agent: true, self-contained
- **Cron:** Daily at 07:00 AEST (after tests, before briefing)
- **Delivery:** Inline stdout to origin chat (works with `deliver=origin` on cron)

## Script Pattern

```python
PAGES = {
    "Homepage": "/",
    "Pricing": "/pricing",
    "Blog": "/compliance-blog",
    "LLMS": "/llms.txt",
    "Agent Card": "/.well-known/agent-card.json",
    "Sitemap": "/sitemap.xml",
}

def check_page(name, path):
    url = f"{BASE}{path}"
    # curl -sI -o /dev/null -w "%{http_code}|%{time_total}|%{ssl_verify_result}"
```

## SSL Check Gotcha — Use curl, NOT openssl

Do NOT use `openssl s_client` — OpenSSL may not have libnspr4 or CA paths configured. Use curl verbose output:

```python
r = subprocess.run(
    ["curl", "-vI", "https://www.example.com", "--connect-timeout", "10", "--stderr", "-"],
    capture_output=True, text=True, timeout=15)
m = re.search(r'expire date: ([^\n]+)', r.stderr)
```

## Delivery Format

```
★ AMLHive Website Monitor — date
   ✅ Homepage      200    43ms
   ✅ LLMS          200    45ms
   ❌ Pricing       404    56ms
   ✅ SSL: expires 2026-09-25 (59 days)
━━━ 5/7 pages OK — 1 issue(s) ━━━
```

Always show every page — the user needs the full picture.

## Known 404 Patterns

Some Next.js sites serve `/pricing` and `/compliance-blog` as anchor sections on the homepage, not separate routes. Log them as issues — they may be intentional.

### CRITICAL: Site Rebuilds Move Paths — Check the Live Sitemap First

When a monitor that used to pass suddenly 404s on a known page, the site was likely **rebuilt with a new URL structure** — do NOT assume an outage. Pull the live sitemap and diff the monitor's `PAGES` against reality:

```bash
curl -s https://www.<domain>/sitemap.xml | grep -oP '(?<=<loc>)[^<]+'
```

Real case (AMLHive, Aug 2026): `/compliance-blog` moved to `/Compliance/compliance-blog` (capital C), plus new pages (`/austrac-compliance`, `/Compliance/austrac-tranche-2-guide`). The monitor's stale paths 404'd → cron exit 1 → false "site down" every morning. Fix: update `PAGES` to the live sitemap structure, add the new pages, re-run, verify exit 0. 3xx (e.g. `/pricing` → 308 redirect) counts as OK (`200 <= code < 400`).

## Cron Setup

```
no_agent: true | script: <project>_website_monitor.py | schedule: 0 7 * * * | deliver: origin
```

## Related Reference Files

- `references/visibility-campaign-brief.md` — Media outreach brief for AMLHive (guest posts to Elite Agent, realestatebusiness.com.au, etc.)
- `references/amlhive-website-monitor.md` — AMLHive website monitor specifics (endpoints, SSL expiry, cron)
- `references/daily-probe-consolidation.md` — 🆕 21:45 consolidated daily probe table (hourly version check + attribution probe). Use when adding a new hourly HTTP probe or extending the daily summary: every hourly probe gets a JSONL history file + a column in `daily_probe_summary.py`. **Also holds the output contract: hourly probes are SILENT on success, raise immediately on any failure/mismatch, and only the 21:45 table delivers the all-clear.**
