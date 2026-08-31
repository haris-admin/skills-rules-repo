# Sitemap Sync: amlhive.com.au → content.amlhive.com.au

## Objective

Daily sync of the main website sitemap (`https://amlhive.com.au/sitemap.xml` — Next.js auto-generated, 26 URLs) to the R2 bucket serving `content.amlhive.com.au/sitemap.xml` so crawlers hitting either endpoint get the same data.

## R2 Bucket Details

| Property | Value |
|----------|-------|
| Bucket Name | `amlhive-blog-content` |
| R2 Account ID | `0f9ad05aed2ef935f572d55cf6e4b8b8` |
| R2 Endpoint | `https://0f9ad05aed2ef935f572d55cf6e4b8b8.r2.cloudflarestorage.com` |
| Working Credentials | `R2_ACCESS_KEY_ID=62fd9151776bce1ae054277fcb3d5c35` + `R2_SECRET_ACCESS_KEY=a50581bddfba30ba9f4ced74d05d7427bed121c9ab68c315be6c5b4705ff9e69` |
| Non-Working Credentials | `R2_PRIMARY_ACCESS_KEY_ID_HHSIDDIQUI=6b47c53d1b1731d98e889e8627cc4e51` (AccessDenied on this bucket) |
| Direct Public URL | `https://pub-88cf461ffc804bf68f23f15df3540660.r2.dev` |
| Custom Domain | `https://content.amlhive.com.au` |

## Key Paths

| Key in Bucket | Public URL |
|---------------|------------|
| `sitemap.xml` | `https://pub-88cf46...r2.dev/sitemap.xml` |
| `sitemap.xml` | `https://content.amlhive.com.au/sitemap.xml` |
| `prod/sitemap.xml` | `https://pub-88cf46...r2.dev/prod/sitemap.xml` |
| `prod/sitemap.xml` | `https://content.amlhive.com.au/prod/sitemap.xml` |

## Critical Discovery (Jul 12, 2026) — Custom Domain Bound to Different Bucket

**The custom domain `content.amlhive.com.au` is NOT bound to bucket `amlhive-blog-content`.**

Evidence:
1. Uploaded updated sitemap to `amlhive-blog-content` at both `sitemap.xml` and `prod/sitemap.xml`
2. Direct R2 URL `pub-88cf46...r2.dev/sitemap.xml` confirmed 4,666 bytes (UPDATED)
3. Custom domain `content.amlhive.com.au/sitemap.xml` still shows 1,305 bytes (OLD)
4. ETags differ: `8881eb12` (R2 direct) vs `455a8438` (custom domain)
5. Blog post files `prod/posts/*/post-v1.md` return **NoSuchKey** from the bucket but serve **HTTP 200** at the custom domain
6. Probe file uploaded to bucket is **not accessible** at the custom domain
7. `cf-cache-status: DYNAMIC` means Cloudflare passes through to origin — origin returns different content

**Conclusion:** The bucket `amlhive-blog-content` is NOT the origin for `content.amlhive.com.au`. The custom domain is bound to a different bucket (different Cloudflare account or bucket name). The working credentials (`R2_ACCESS_KEY_ID=62fd9...`) only give access to `amlhive-blog-content`, not the bucket that `content.amlhive.com.au` actually serves from.

## Current Status (Jul 12, 2026)

| Endpoint | Size | Status |
|----------|------|--------|
| `https://amlhive.com.au/sitemap.xml` | 4,666 bytes | ✅ Source of truth (Next.js auto-generated) |
| `pub-88cf46...r2.dev/sitemap.xml` | 4,666 bytes | ✅ Updated (mirrors source) |
| `content.amlhive.com.au/sitemap.xml` | 1,305 bytes | ❌ Stale — different bucket, needs Haris to check Cloudflare Dashboard |

## Next Steps

1. Haris checks which R2 bucket `content.amlhive.com.au` is actually bound to in Cloudflare Dashboard
2. Provide credentials for that bucket
3. Re-run the sync with correct bucket/credentials
4. Set up daily 4:30 AM cron once confirmed working

## Cron Job Design (Planned)

- **Schedule**: Daily at 4:30 AM AEST
- **Source**: Fetch `https://amlhive.com.au/sitemap.xml`
- **Destination**: Upload to `s3://amlhive-blog-content/prod/sitemap.xml` AND `s3://amlhive-blog-content/sitemap.xml`
- **Verification**: Check `pub-88cf46...r2.dev/sitemap.xml` matches source
- **Cache Purge Required**: After upload, Cloudflare cache for `https://content.amlhive.com.au/sitemap.xml` needs purging for the change to propagate to the custom domain
- **Credentials**: Need `R2_ACCESS_KEY_ID` + `R2_SECRET_ACCESS_KEY` for the blog-content bucket (NOT the hhsiddiqui PRIMARY keys)
- **Cron format**: `30 4 * * *` (4:30 AM)

## Verification Commands

```bash
# Check source
curl -s https://amlhive.com.au/sitemap.xml | wc -c

# Check R2 direct (source of truth for bucket content)
curl -s https://pub-88cf461ffc804bf68f23f15df3540660.r2.dev/sitemap.xml | wc -c

# Check custom domain (may be cached)
curl -s https://content.amlhive.com.au/sitemap.xml | wc -c

# Full diff
diff <(curl -s https://amlhive.com.au/sitemap.xml) <(curl -s https://content.amlhive.com.au/sitemap.xml) && echo "IDENTICAL"
```
