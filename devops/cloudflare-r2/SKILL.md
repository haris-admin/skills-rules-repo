---
name: cloudflare-r2
description: "General-purpose Cloudflare R2 (S3-compatible object storage) operations — credential management, boto3/AWS CLI setup, public access, custom domain caching behavior, upload/read patterns for static content, and troubleshooting common issues like SignatureDoesNotMatch."
version: 1.0.0
author: Pluto
license: MIT
category: devops
platforms: [linux, macos, wsl]
metadata:
  hermes:
    tags: [cloudflare, r2, s3, object-storage, boto3, caching, devops]
    related_skills: [reference-data-ingestion, aws-cloudwatch-agent, pluto-fleet-monitor]
---

# Cloudflare R2

## When to Use

- Uploading or reading files from Cloudflare R2 buckets via AWS CLI or boto3
- Debugging R2 credential issues (AccessDenied, SignatureDoesNotMatch)
- Working with R2 public buckets (`pub-*.r2.dev`) vs custom domains (`cdn.example.com`)
- Troubleshooting stale content on R2 custom domains despite successful uploads
- Setting up cron jobs that sync content to R2

## Architecture

Cloudflare R2 is S3-compatible. The key difference from AWS S3:

| Aspect | AWS S3 | Cloudflare R2 |
|--------|--------|---------------|
| Endpoint | `s3.<region>.amazonaws.com` | `https://<account_id>.r2.cloudflarestorage.com` |
| Region | Required | Always `auto` |
| Auth | IAM roles/keys | R2 API tokens |
| Direct public URL | Bucket website hosting | `https://pub-<hash>.r2.dev/<key>` |
| Custom domain | CloudFront + Route53 | Built-in R2 custom domains (via Cloudflare proxy) |

## Credentials

### Finding Credentials

R2 credentials are stored in the Windows `.env` (`/mnt/c/Users/habib/.hermes/.env`) and WSL `.env` (`~/.hermes/.env`). They can and do drift — check **both** locations when debugging.

### Multi-Credential Pattern

Different R2 buckets or accounts use different credential sets:

| Credential Name | Scope | Used For |
|----------------|-------|----------|
| `R2_ACCESS_KEY_ID` / `R2_SECRET_ACCESS_KEY` | AML Hive backend | `amlhive-blog-content`, `amlhive-documents` |
| `R2_PRIMARY_ACCESS_KEY_ID_HHSIDDIQUI` / `R2_PRIMARY_SECRET_ACCESS_KEY_HHSIDDIQUI` | hhsiddiqui Cloudflare account | Primary account operations (may not have bucket-level access) |
| `R2_ASIC_BUCKET_NAME=amlhive-asic-conent` | ASIC data | Note the typo "conent" (not "content") |

**Important:** The `R2_PRIMARY_*_HHSIDDIQUI` credentials often get AccessDenied on buckets created under the AML Hive account. Always test which credential set works for the target bucket before relying on it.

## AWS CLI Usage

```bash
# Configure per-command (no permanent profile needed)
AWS_ACCESS_KEY_ID=<key> AWS_SECRET_ACCESS_KEY=<secret> \
  aws s3 <command> s3://<bucket>/<key> \
  --endpoint-url https://<account_id>.r2.cloudflarestorage.com \
  --region auto
```

### Common Commands

```bash
# Upload a file
aws s3 cp /path/to/file s3://bucket/path/to/key --endpoint-url https://<id>.r2.cloudflarestorage.com --region auto

# List objects (may fail if credentials are write-only)
aws s3 ls s3://bucket/prefix/ --endpoint-url https://<id>.r2.cloudflarestorage.com --region auto

# Check object metadata
aws s3api head-object --bucket <bucket> --key <key> --endpoint-url https://<id>.r2.cloudflarestorage.com --region auto

# Delete an object
aws s3 rm s3://bucket/path/to/key --endpoint-url https://<id>.r2.cloudflarestorage.com --region auto
```

## boto3 (Python) Usage

```python
import boto3
from botocore.config import Config

client = boto3.client(
    "s3",
    endpoint_url=f"https://{R2_ACCOUNT_ID}.r2.cloudflarestorage.com",
    aws_access_key_id=R2_ACCESS_KEY_ID,
    aws_secret_access_key=R2_SECRET_ACCESS_KEY,
    region_name="auto",
    config=Config(signature_version="s3v4"),
)

# Upload
with open("file.xml", "rb") as f:
    client.put_object(Bucket="bucket-name", Key="path/to/key", Body=f.read(), ContentType="application/xml")

# Read
obj = client.get_object(Bucket="bucket-name", Key="path/to/key")
content = obj["Body"].read()

# List
resp = client.list_objects_v2(Bucket="bucket-name", Prefix="prefix/")
for obj in resp.get("Contents", []):
    print(obj["Key"], obj["Size"])
```

## Public URL Patterns

R2 objects are accessible via two URL patterns:

### 1. Direct R2 Public URL (`pub-*.r2.dev`)
```
https://pub-<hash>.r2.dev/<key>
```
- Always reflects the **current** bucket content immediately after upload
- Can be 403 Forbidden if the bucket doesn't have public access enabled
- Use this for verification that an upload actually succeeded

### 2. Custom Domain (`content.example.com`)
```
https://content.example.com/<key>
```
- Goes through **Cloudflare edge proxy**
- Server header shows `cloudflare`
- **May serve stale content** even after a successful bucket upload, because:
  - Cloudflare edge caches the response
  - `cf-cache-status: DYNAMIC` does NOT mean uncached — it means the origin (R2) serves dynamic content but CF still caches at the edge
  - The ETag and Last-Modified headers reflect the OLD object
- A direct cache-busting URL query param (`?v=<timestamp>`) does NOT bypass the edge cache for R2 custom domains

### Verifying Updates

```bash
# Always verify BOTH URLs:
curl -s https://pub-<hash>.r2.dev/path/to/file | wc -c   # source of truth
curl -s https://content.example.com/path/to/file | wc -c  # may be stale
```

If the direct URL shows updated content but the custom domain doesn't, the upload succeeded but Cloudflare edge is caching the old response.

## Troubleshooting

### SignatureDoesNotMatch

This error can be **intermittent** with R2. Causes:

- **Clock skew** between the WSL machine and Cloudflare servers (check with `date -u`)
- **Key-value corruption** in the credential string (truncated characters from environment variable interpolation)
- **Specific key paths** may work while others don't (e.g., `prod/sitemap.xml` succeeds but root `sitemap.xml` fails — possible bucket policy or versioning issue)

**Workarounds:**
1. Retry — often succeeds on the second attempt
2. Use boto3/Python instead of AWS CLI (more consistent signing)
3. Use explicit `ContentType` and region
4. If intermittent, the credentials are correct but the R2 edge may be having transient issues

### AccessDenied

- **Write-only keys**: Some R2 tokens have PutObject permission but not GetObject, ListObjects, or HeadObject. This is by design for security. The upload may succeed while ListBuckets, HeadObject, and ListObjectsV2 all fail.
- **Wrong credential set**: Different buckets/accounts use different keys. Test with a different set.
- **Wrong endpoint**: Make sure the account ID in the endpoint URL matches the correct Cloudflare account.

### Custom Domain — Stale or Wrong Content

If the direct `pub-*.r2.dev` URL shows updated content but the custom domain shows **different** content, the custom domain may be bound to a **different bucket** — not just a caching issue.

#### Diagnosis: compare ETag + Content-Length

```bash
curl -sI https://pub-<hash>.r2.dev/sitemap.xml | grep -i -E 'content-length|etag'
curl -sI https://content.example.com/sitemap.xml | grep -i -E 'content-length|etag'
```

| Scenario | Direct R2 URL | Custom Domain | Root Cause |
|----------|---------------|---------------|------------|
| Cache delay | New ETag (your upload) | Same ETag, older Last-Modified | Cloudflare edge caching; purge the URL |
| Different bucket | New ETag (your upload) | **Different ETag**, different content | Custom domain is bound to another bucket |
| No public access | 404/403 | Works with old content | You wrote to the wrong bucket |

`cf-cache-status: DYNAMIC` does NOT mean content is live. It only means Cloudflare didn't cache at its outermost layer — the R2 origin itself returns the old object. **Different ETags = different bucket, not a cache delay**.

#### Fix: Different Bucket

1. Check the CNAME target for the custom domain (grey-cloud the record to see it, or check Cloudflare Dashboard)
2. The R2 bucket connected to the custom domain needs different credentials
3. Upload a probe file to verify which bucket the domain actually maps to

## Related References

- `references/indexnow-sitemap-submission.md` — IndexNow protocol for notifying search engines of sitemap updates
- `references/bing-webmaster-api.md` — Bing Webmaster API auth (`apikey=` query param, NOT Basic), dual-use key with IndexNow, dashboard data (verified 2026-08-08)
- `references/sitemap-sync-to-content-domain.md` — sitemap sync pattern to R2 custom domain

## Cron Sync Pattern

For daily sitemap/content sync to R2 with a custom domain:

```python
# Pseudo-code for a sync cron job:
import requests
import boto3

# 1. Fetch source content
resp = requests.get("https://source.example.com/sitemap.xml")
source_content = resp.content

# 2. Upload to R2
client.put_object(
    Bucket="bucket-name",
    Key="prod/sitemap.xml",
    Body=source_content,
    ContentType="application/xml",
)

# 3. Upload to root path as well (for direct R2 URL)
client.put_object(
    Bucket="bucket-name",
    Key="sitemap.xml",
    Body=source_content,
    ContentType="application/xml",
)

# 4. Verify via direct R2 URL (pub-*.r2.dev)
verify_resp = requests.get("https://pub-<hash>.r2.dev/sitemap.xml")
assert len(verify_resp.content) == len(source_content)  # confirm upload worked

# 5. Note: custom domain may still be stale — requires Cloudflare cache purge
```

**Important - the custom domain may NOT reflect the update immediately** even after a successful R2 upload. Always verify via the direct `pub-*.r2.dev` URL first. If that shows updated content, the R2 bucket is correct and any remaining staleness is a Cloudflare edge caching issue, not a bucket issue.

## Pitfalls

- **`cf-cache-status: DYNAMIC` does NOT mean the response is uncached**. It means Cloudflare treats the origin as dynamic but still caches the response on edge servers. The only reliable indicators are the `content-length` and `etag` headers.
- **Different ETag between R2 public URL and custom domain = different bucket**. If you upload to a bucket and the direct `pub-*.r2.dev` URL shows your new content but the custom domain shows different content with a different ETag, the custom domain is bound to a different bucket. This is NOT a cache issue — verify by comparing ETags and Last-Modified headers.
- **Intermittent SignatureDoesNotMatch**: R2 can throw this error on some key paths but not others in the same bucket. Always retry. Use boto3 (Python) instead of AWS CLI when AWS CLI is unreliable.
- **No ListBuckets**: The R2 credentials are typically scoped to specific buckets and cannot list all buckets. Don't rely on `aws s3 ls` or `list_buckets()`.
- **Dual-location credentials**: R2 keys in Windows `.env` vs WSL `.env` can drift. Sync them with `cat /mnt/c/Users/habib/.hermes/.env | grep "^R2_" >> ~/.hermes/.env`.
- **Content-Type matters**: Always set `ContentType` when uploading (e.g., `application/xml` for sitemaps, `text/csv` for CSVs, `text/markdown` for markdown). Without it, R2 serves files with the wrong MIME type.
- **Sitemaps must be at the bucket root for the custom domain root URL**: If `content.example.com/sitemap.xml` is the target, upload to `sitemap.xml` (root), not `prod/sitemap.xml`.
