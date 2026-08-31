# Bing Webmaster API — auth & verification recipe

Verified 2026-08-08 against the live Bing Webmaster account (macarthurgarments /
amlhive.com.au + harishabib.au).

## Auth: `apikey=` query param, NOT Basic auth

The 32-char keys in `/mnt/c/Users/habib/.hermes/.env` are the real Bing Webmaster
API keys:

- `BING_WEBMASTER_API_KEY_AMLHIVE` — same value as the API Key shown in Bing
  Webmaster Tools → Settings (gear) → API access → API Key
- `INDEXNOW_KEY` — also valid for the IndexNow API

Both keys authenticate the Bing Webmaster REST API ONLY via the `apikey=` query
parameter:

```python
import json, urllib.request, urllib.parse
key = "aa6fb4f08a654ac99483f1eb2bd0646e"  # read from .env, never hardcode
url = "https://ssl.bing.com/webmaster/api.svc/json/GetUserSites?" + urllib.parse.urlencode({"apikey": key})
req = urllib.request.Request(url, headers={"Content-Type": "application/json"}, method="GET")
with urllib.request.urlopen(req, timeout=20) as r:
    sites = json.loads(r.read().decode())["d"]
```

**All Basic-auth variants fail** with `{"ErrorCode":3,"Message":"ERROR!!! InvalidApiKey"}`
— key+colon, key-only, colon+key, raw header. That failure was once misread as
"key rejected"; it is an auth-format error, not a bad key.

## Known endpoints (ssl.bing.com/webmaster/api.svc/json/)

- `GetUserSites` — list verified sites (returns `Url`, `IsVerified`,
  `AuthenticationCode`, `DnsVerificationCode`). Verified 2026-08-08:
  `https://amlhive.com.au/` and `https://harishabib.au/` both `IsVerified: true`.
- Legacy SOAP/POX variants retire **2026-08-31** — use the JSON/REST forms.

## IndexNow side

Same keys work on `https://api.indexnow.org/indexnow?url=<url>&key=<key>`:
- `INDEXNOW_KEY` → HTTP 200
- `BING_WEBMASTER_API_KEY_AMLHIVE` → HTTP 202 (accepted)
- Key-file check: `https://amlhive.com.au/{key}.txt` returns **403 behind
  Cloudflare**. API pings succeed regardless, but Bing/Google re-validate the key
  file — serve it (allow `.txt` through the CDN) for full IndexNow compliance.

## Where to find the key in the UI (CDP-assisted)

1. Open `https://www.bing.com/webmasters` in the signed-in debug Chrome.
2. Click Settings gear (top-right) → Settings flyout → **API access**.
3. Panel shows two rows: **OAuth Client** and **API Key** → click API Key.
4. Key is displayed unmasked in a read-only field, with a Copy button and
   Regenerate/Delete icons. Note the on-page guidance: "Use this API Key by
   simply passing it with the apikey=YOUR-API-KEY parameter".
5. The dashboard (Home) shows Top Recommendations + Search Performance
   (clicks/impressions) — e.g. Aug 2026: 25 clicks / 248 impressions over
   Jun 23–Aug 6, with recommendations about inbound links and NOINDEX meta tags.

## Pitfalls

- The debug Chrome profile only holds the Google session; Bing/Microsoft login is
  a separate session in the same browser — the user must sign into Bing in the
  debug window too (their normal Chrome has no debug port).
- `apiaccess?siteUrl=<url>` without the trailing slash shows "No pages found";
  the site is registered with a trailing slash (`https://amlhive.com.au/`).
- Don't print the key value in outputs — read from `.env` at runtime.
