# Bing Webmaster API — Authentication & Verification (2026-08-08)

## Key Finding: auth is `apikey=` query param, NOT Basic auth

The Bing Webmaster API (`ssl.bing.com/webmaster/api.svc/json/*`) authenticates
with the API key as an **`apikey=` query parameter** — NOT Basic auth. Trying
Basic auth (`Authorization: Basic base64(key:)`) returns `InvalidApiKey` even
with a correct key.

```python
import json, urllib.request, urllib.parse

key = "<BING_WEBMASTER_API_KEY>"
url = "https://ssl.bing.com/webmaster/api.svc/json/GetUserSites?" + urllib.parse.urlencode({"apikey": key})
req = urllib.request.Request(url)
with urllib.request.urlopen(req, timeout=20) as resp:
    data = json.loads(resp.read())
# [{"d": {"D": [{"D": "https://site1.au/"}, ...], "Errors": [], "Success": true}}]
```

## Dual-use of the 32-char key (verified 2026-08-08)

`BING_WEBMASTER_API_KEY_AMLHIVE` in the Windows `.env` (~/.hermes/.env) is a
32-char alphanumeric key that validates against BOTH:

| API | Endpoint | Result |
|-----|----------|--------|
| Bing Webmaster REST | `ssl.bing.com/webmaster/api.svc/json/GetUserSites?apikey=...` | ✅ IsVerified: true |
| IndexNow | `api.indexnow.org/indexnow` (POST with key) | ✅ HTTP 200/202 accepted |

So the same key serves two purposes: Webmaster API data access AND IndexNow
pinging. Don't generate a second key if IndexNow already works.

## Verified sites (AML Hive, 2026-08-08)

- `https://amlhive.com.au/` → IsVerified: true
- `https://harishabib.au/` → IsVerified: true

## Where to find the key in the UI

Bing Webmaster Tools → Settings (gear) → **API access (Manage credentials)**
→ API Key. The panel states: *"Use this API Key by simply passing it with the
`apikey=YOUR-API-KEY` parameter while making an API request."* The panel also
warns: don't give the key to untrusted third parties.

## Dashboard data visible when logged in (reference)

For amlhive.com.au (Jun 23 – Aug 6, 2026): **25 clicks / 248 impressions**;
Top Recommendations: (1) not enough high-quality inbound links, (2) some URLs
not indexed due to robots **NOINDEX** meta tags.

## Pitfalls

- **Legacy SOAP/POX retire Aug 31, 2026** — use the REST endpoints
  (`api.svc/json/*`), not the SOAP ones. The new Responses-style/JSON REST API
  is the forward path.
- **The API key value is NOT the `tid` query param** in the Bing Webmaster
  dashboard URL (`?tid=8835097c-...` is the site/tenant ID, not the API key).
- **Basic auth returns InvalidApiKey** — this is a trap. The correct transport
  is the query param. If you get `InvalidApiKey` from Basic auth, that's an
  auth-method error, not necessarily a wrong key.
- **IndexNow key-file check may 403 behind Cloudflare** even when the key
  validates via API. The API pings are accepted, but for full IndexNow
  compliance serve `https://<domain>/<key>.txt` returning 200 with the key as
  content (see indexnow-sitemap-submission.md). A 403 key-file does NOT break
  the API-side validation.
