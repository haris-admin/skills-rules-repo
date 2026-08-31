# IndexNow Sitemap Submission

When search engines need to be notified of sitemap updates, use the **IndexNow protocol** — the modern standard supported by Google, Bing, Yandex, Seznam, and Naver. The old `google.com/ping` and `bing.com/ping` endpoints were deprecated in 2024 (return 404/410).

## Prerequisites

- An **IndexNow API key** (stored in `.env` as `INDEXNOW_KEY`)
- A **key verification file** deployed at `https://<your-domain>/<key>.txt` (search engines check this to verify ownership)
- The target URLs must be accessible (HTTP 200)

## Finding the Key

```bash
grep INDEXNOW_KEY /mnt/c/Users/habib/.hermes/.env ~/.hermes/.env 2>/dev/null
```

## Single-Endpoint Submission (Covers All Partners)

Submit to `api.indexnow.org` — it automatically notifies Google, Bing, Yandex, Seznam, and Naver:

```bash
curl -s -X POST 'https://api.indexnow.org/indexnow' \
  -H 'Content-Type: application/json' \
  -d '{
    "host": "example.com.au",
    "key": "YOUR_INDEXNOW_KEY",
    "keyLocation": "https://example.com.au/YOUR_INDEXNOW_KEY.txt",
    "urlList": ["https://example.com.au/sitemap.xml"]
  }'
```

HTTP 200 with empty body = success. No error body means accepted.

## Direct Bing Submission (Redundant but Confirms)

```bash
curl -s -X POST 'https://www.bing.com/indexnow' \
  -H 'Content-Type: application/json' \
  -d '{
    "host": "example.com.au",
    "key": "YOUR_INDEXNOW_KEY",
    "keyLocation": "https://example.com.au/YOUR_INDEXNOW_KEY.txt",
    "urlList": ["https://example.com.au/sitemap.xml"]
  }'
```

## Batch Submission (Multiple URLs)

Submit up to 10,000 URLs in a single request:

```bash
curl -s -X POST 'https://api.indexnow.org/indexnow' \
  -H 'Content-Type: application/json' \
  -d '{
    "host": "example.com.au",
    "key": "YOUR_INDEXNOW_KEY",
    "keyLocation": "https://example.com.au/YOUR_INDEXNOW_KEY.txt",
    "urlList": [
      "https://example.com.au/sitemap.xml",
      "https://example.com.au/",
      "https://example.com.au/about"
    ]
  }'
```

## Yandex-Specific

```bash
curl -s -X POST 'https://yandex.com/indexnow' \
  -H 'Content-Type: application/json' \
  -d '{"host":"example.com.au","key":"KEY","keyLocation":"https://example.com.au/KEY.txt","urlList":["https://example.com.au/sitemap.xml"]}'
```

Yandex returns HTTP 202 (Accepted) instead of 200.

## Key File Deployment

The key verification file MUST be accessible at `https://<domain>/<key>.txt` returning HTTP 200 with the key as the content.

**If the domain is behind a SPA/router** (Next.js, React, etc.), the `.txt` route may be caught by the frontend router and return the app shell or redirect to login. Fix this by:

1. **Upload to R2 bucket root** — if the domain serves from R2:
   ```bash
   echo -n "YOUR_INDEXNOW_KEY" > /tmp/key.txt
   aws s3 cp /tmp/key.txt s3://bucket/KEY.txt \
     --endpoint-url https://<account>.r2.cloudflarestorage.com \
     --region auto
   ```

2. **Add a rewrite rule** in Cloudflare → Rules → Transform Rules to serve the `.txt` file directly from R2 without hitting the SPA router.

3. **Verify** the key file is accessible:
   ```bash
   curl -s -o /dev/null -w 'HTTP %{http_code}' "https://example.com.au/KEY.txt"
   # Should return 200, not 302/404
   ```

## Search Engine IndexNow Endpoints

| Engine | Endpoint | Notes |
|--------|----------|-------|
| All partners (recommended) | `https://api.indexnow.org/indexnow` | Single submission covers all |
| Google | `https://google-api.indexnow.org/indexnow` | May not exist — use api.indexnow.org |
| Bing | `https://www.bing.com/indexnow` | Confirmed working |
| Yandex | `https://yandex.com/indexnow` | Returns 202, not 200 |

## Verification

```bash
# Check sitemap is accessible
curl -s "https://example.com.au/sitemap.xml" | head -5

# Check key file is accessible
curl -s -o /dev/null -w '%{http_code}' "https://example.com.au/KEY.txt"

# Submit
curl -s -X POST 'https://api.indexnow.org/indexnow' \
  -H 'Content-Type: application/json' \
  -d '{"host":"example.com.au","key":"KEY","keyLocation":"https://example.com.au/KEY.txt","urlList":["https://example.com.au/sitemap.xml"]}'
# HTTP 200 empty body = accepted
```

## Pitfalls

- **Old ping endpoints are dead** — `google.com/ping` returns 404, `bing.com/ping` returns 410
- **HTTP 000 from curl** = DNS resolution or connection failure, not an IndexNow rejection
- **Key file MUST return HTTP 200** — a redirect (302 to login page) will cause verification failure
- **IndexNow doesn't return error messages** — HTTP 200 with empty body is the success signal. If you get HTTP 429 (rate limited), wait and retry
- **Key verification is asynchronous** — search engines check the key file after submission, not during
