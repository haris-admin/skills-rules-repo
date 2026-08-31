# WAF False 403 — Python urllib User-Agent Blocking

**Reproduction date:** Thursday 9 July 2026
**Affected script:** `amlhive_prod_monitor.py`
**Root cause:** Cloudflare WAF blocks `Python-urllib/3.x` User-Agent → `http_get()` returns HTTP 403 for every endpoint.

## Symptom

The fleet monitor's public health section consistently reported both API and frontend as HTTP 403:

```
🔴 API: https://api.amlhive.com.au/health → HTTP 403
🔴 Frontend: https://amlhive.com.au → HTTP 403
```

The state file had `pub_health_fails: 15` — 15 consecutive failed cycles over ~3.75 days.

## Initial Misdiagnosis

The first assumption was a real AWS/CloudFront/Security Group issue. The Sentry section compounded the confusion — its diagnostic `http_get(API_HEALTH_URL)` also returned 403, so it fell through to:

> (API also unreachable — app may be down)

Instead of the correct diagnostic:

> (API responds 200 — Sentry DSN/config may need review)

This masked a potential real Sentry DSN issue.

## Debugging Path

### 1. Verify endpoints independently (outside the monitor)

A simple curl from the same WSL environment showed the truth:

```bash
curl -s -o /dev/null -w "%{http_code}" https://api.amlhive.com.au/health
# → 200

curl -s -o /dev/null -w "%{http_code}" https://amlhive.com.au
# → 200
```

### 2. Check User-Agent sensitivity

The key insight: compare curl's default UA vs Python urllib's default UA:

```bash
# curl with Python's User-Agent → 403
curl -s -o /dev/null -w "%{http_code}" \
  -A "Python-urllib/3.11" \
  https://api.amlhive.com.au/health
# → 403
```

### 3. Confirm the exact monitor code path

The `http_get()` function in `amlhive_prod_monitor.py`:

```python
def http_get(url, timeout=10):
    """Simple HTTP GET. Returns (status_code, body_or_error)."""
    try:
        req = urllib.request.Request(url, method="GET")
        # ^^^ no User-Agent header → Cloudflare gets default Python-urllib/3.x
```

The fix was adding a browser-like User-Agent:

```python
req = urllib.request.Request(url, method="GET",
    headers={"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) ..."})
```

Verification after fix:

```python
# Both endpoints return 200 with proper UA
curl -A "Mozilla/5.0 (X11; Linux x86_64) ..." https://api.amlhive.com.au/health
# → 200
```

## Secondary Impact: Sentry Diagnostic

The Sentry check also calls `http_get(API_HEALTH_URL)` to determine whether zero events means "app is down" vs "DSN may be misconfigured":

```python
# Sentry check (simplified)
if total_events == 0:
    code, _ = http_get(API_HEALTH_URL, timeout=5)
    if code == 200:
        # "(API responds 200 — Sentry DSN/config may need review)"
    else:
        # "(API also unreachable — app may be down)"
```

With the UA bug, `code` was always 403, so it took the wrong branch every time. Fixing the UA fixed both symptoms.

## State File Cleanup

The accumulated `pub_health_fails: 15` in `amlhive_state.json` needed manual reset. Without this, the first post-fix cycle would still show `[CONSECUTIVE]` because the counter only resets on *this* cycle's success, but the last cycle had failed. Reset to 0.

## Broader Lesson

**Any Python monitoring script that does HTTP health checks must set a browser-like User-Agent header.** Cloudflare, AWS WAF, CloudFront, and many CDN/WAF services block `Python-urllib/` by default. This applies to:

- `urllib.request.Request(url, headers={...})`
- All `http_get()` and `http_get_sentry()` style helpers
- Any webhook or API health check in monitoring scripts

The standard fix pattern:

```python
req = urllib.request.Request(url, 
    headers={"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"})
```

## How to Detect This Class of Bug

When a monitor reports HTTP 4xx for ALL endpoints simultaneously:

1. Check the endpoints with a **different tool** (curl, browser, Postman) from the same network
2. If they work in curl but not in Python, compare User-Agent
3. Run curl with `-A "Python-urllib/3.11"` to reproduce
4. Check Sentry/telemetry fallback diagnostics — they may use the same broken HTTP helper
5. Check state file for cumulative failure counters that need resetting after fix
