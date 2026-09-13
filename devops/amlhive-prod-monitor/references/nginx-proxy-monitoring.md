# Nginx / Cloudflare Proxy-Layer Monitoring

## Why this exists
When a request dies at nginx (e.g. oversized cookies, malformed headers), the app never runs — Sentry sees nothing. Only nginx and Cloudflare logs record the failure.

## Three-layer monitoring strategy

### Layer 1: SSM nginx log tail (live, last 1000 lines)
- Function: `check_cloudflare_origin()` in `amlhive_prod_monitor.py`
- Runs on frontend EC2 via SSM: `sudo tail -1000 /var/log/nginx/access.log | grep -E 'HTTP/[0-9.]+ [45]'`
- Catches current/recent 4xx/5xx with request path and method
- Also tails error log: `sudo tail -100 /var/log/nginx/error.log | grep -iv 'letsencrypt' | grep -iv 'acme'`
- Shows upstream failures (`connect() refused`), SSL handshake errors, buffering warnings

### Layer 2: CloudWatch log search (6h window, persistent)
- Searches `/amlhive/frontend-system` for nginx HTTP status patterns
- Uses `filter-pattern '"HTTP/1.1" 400'` to match nginx access log format
- Alerts:
  - 400 count > 10 in 6h → P1 (live — likely oversized cookie/header rejection)
  - 400 count > 3 in 6h → P2 (drift — review nginx logs)
  - 502/503/504 > 3 in 6h → P0/P1 (live — upstream unreachable)

### Layer 3: Cloudflare Analytics API (optional, token-dependent)
- Requires zone analytics scope on the CF API token
- Current `CLOUDFLARE_API_TOKEN` is R2-scoped only (returns 403)
- Falls back gracefully — nginx logs are more direct/reliable

## Where it runs
- **4x daily**: `amlhive_prod_monitor.py` (5/11/17/23 AEST) — full check including alerts
- **1x daily 9:15 PM**: `amlhive_daily_report.py` — imports `check_cloudflare_origin()` and displays summary in report

## Key notes
- CF token from `.openclaw/.env` — `load_env()` must scan that file (was a bug: it only scanned `.hermes/.env` initially)
- Nginx access logs go to `/amlhive/frontend-system` CloudWatch log group, NOT `/amlhive/frontend`
