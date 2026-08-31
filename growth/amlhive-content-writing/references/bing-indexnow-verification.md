# Bing IndexNow Key Verification (AMLHive) — 2026-08-08

Verified live against the real endpoints. Use this when confirming the
IndexNow/Webmaster key setup or diagnosing "IndexNow not working" reports.

## The two keys in `.hermes/.env` (Windows side) — do NOT confuse them

| Env var | What it actually is | Length | Accepts |
|---|---|---|---|
| `INDEXNOW_KEY` | IndexNow submission key | 32 alphanumeric | IndexNow API (api.indexnow.org) ✅ |
| `BING_WEBMASTER_API_KEY_AMLHIVE` | **Also an IndexNow key** (name is misleading) | 32 alphanumeric | IndexNow API (api.indexnow.org) ✅ |

Both 32-char values are **IndexNow keys**, NOT Bing Webmaster API keys. The
Bing Webmaster **API** key is a different GUID-like string generated at
Bing Webmaster Tools → API Access. Do not assume `BING_WEBMASTER_API_KEY_*`
grants Webmaster API access — test it (below) before building anything on it.

## Test procedure (no browser needed)

```bash
# 1) IndexNow key check — GET with key + url params
#    HTTP 200/202 = key accepted for that host; 4xx = rejected
curl -s -o /dev/null -w "%{http_code}\n" \
  "https://api.indexnow.org/indexnow?url=https://amlhive.com.au/&key=<KEY>"

# 2) Bing Webmaster API check — GetUserSites with Basic auth (key: empty pw)
#    HTTP 200 = valid Webmaster API key; 400 ErrorCode 3 "InvalidApiKey" =
#    this key is NOT a Webmaster API key (it's an IndexNow key)
curl -s -u "<KEY>:" \
  "https://ssl.bing.com/webmaster/api.svc/json/GetUserSites"
```

Result (2026-08-08): both `.env` keys → IndexNow API 200/202 ✅, Webmaster API
400 InvalidApiKey (all four auth variants — key:colon, key-only, colon:key,
raw header — none work).

## Key-file pitfall (Cloudflare)

IndexNow validates ownership two ways: the API ping (works) AND optionally the
key file at `https://amlhive.com.au/{key}.txt`. The key file currently returns
**403 behind Cloudflare** — the API ping still succeeds, but Bing/Google may
re-validate the key file. Recommendation: serve `/{key}.txt` with the key as
content (static route or Cloudflare rule) for full IndexNow compliance.

## Pitfalls

- Reading `.env` keys must never print the value — report length only
  (`len=32`), and never echo the key.
- The value has no quotes/whitespace/comments in the raw line — if a key
  "looks wrong", the value itself is wrong, not the parsing.
- `indexnow.txt` at the site root 404s and is EXPECTED to — the key file lives
  at `/{key}.txt`, not `/indexnow.txt`.
- This is a fetch-side verification; it does not prove the site's sitemap was
  submitted to Bing Webmaster Tools (separate action, needs the Webmaster API
  key or manual UI submission).
