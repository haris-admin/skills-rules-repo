---
name: bing-webmaster-tools
description: "Use when working with Bing Webmaster API or IndexNow pings."
version: 1.0.0
author: Pluto
license: MIT
category: devops
platforms: [linux, macos, wsl]
metadata:
  hermes:
    tags: [bing, webmaster, indexnow, api, seo, amlhive]
    related_skills: [pluto-amlhive-operating-contract, website-uptime-monitor, google-workspace-access]
---

# Bing Webmaster Tools & IndexNow

Class-level skill for Bing Webmaster API access, IndexNow URL submission, and
reading Bing search-console evidence from Hermes on WSL. Complements the
operating contract's "Bing and DuckDuckGo workflow" (which says what to check)
with the concrete API mechanics (how to check).

## Trigger

- Submit/verify IndexNow pings for an approved URL
- Read Bing Webmaster evidence (clicks, impressions, recommendations, sitemap status)
- Troubleshoot `InvalidApiKey` / "No pages found" / stale-key issues
- Retrieve or verify the Bing Webmaster API key
- Any task referencing `BING_WEBMASTER_API_KEY_AMLHIVE` or `INDEXNOW_KEY`

## Key facts

| Env var (Windows `.env` only — `/mnt/c/Users/habib/.hermes/.env`) | Type | Valid for |
|---|---|---|
| `BING_WEBMASTER_API_KEY_AMLHIVE` | 32-char alphanumeric | Bing Webmaster REST API (as `apikey=`) AND IndexNow API |
| `INDEXNOW_KEY` | 32-char alphanumeric | IndexNow API |

Both 32-char values validate against IndexNow. The `BING_WEBMASTER_API_KEY_AMLHIVE`
value is ALSO the real Webmaster API key — one key, two surfaces. The key does
NOT live in the WSL `.env` (only the Windows one).

## Auth: `apikey=` query param — never Basic auth

The Webmaster API rejects Basic auth with
`{"ErrorCode":3,"Message":"ERROR!!! InvalidApiKey"}` (all variants fail).
Correct method:

```python
import json, urllib.request, urllib.parse
url = "https://ssl.bing.com/webmaster/api.svc/json/GetUserSites?" + urllib.parse.urlencode({"apikey": key})
req = urllib.request.Request(url, headers={"Content-Type": "application/json"}, method="GET")
with urllib.request.urlopen(req, timeout=20) as r:
    sites = json.loads(r.read().decode())["d"]   # [{Url, IsVerified, ...}]
```

Both hosts work:
- `https://ssl.bing.com/webmaster/api.svc/json/GetUserSites?apikey=...`
- `https://www.bing.com/webmaster/api.svc/json/GetUserSites?apikey=...`

`IsVerified: true` confirms key ↔ site mapping. Legacy SOAP/POX APIs retire
**2026-08-31** — use REST.

## IndexNow dual-use

```python
url = "https://api.indexnow.org/indexnow?" + urllib.parse.urlencode({
    "url": "https://amlhive.com.au/", "key": key})
```
HTTP 202 = accepted; HTTP 200 = key validated. A Webmaster-API rejection does
NOT mean the key is wrong — it means the auth method was wrong.

## Key-file compliance caveat

`https://{site}/{key}.txt` should return the key as content for full IndexNow
compliance. On AMLHive it returned **403 behind Cloudflare** (2026-08-08) —
API pings still work, but Bing/Google may re-validate the key file. Check the
site's `/indexnow-key/[key]` route before assuming a 403 is a failure.

## Reading the key from the Bing Webmaster UI (CDP)

Path: **Settings gear (top-right) → "API access" → "API Key" row → key value**.

UI quirks (learned 2026-08-08):
- The Settings drawer and API-access sub-panel are **portal-rendered**: their
  text does NOT appear in `document.body.innerText`. Use `Page.captureScreenshot`
  + vision to read them.
- Click via text-match where `textContent` **starts with** the label (`API
  access`, `API Key`) — exact `^label$` matches fail because rows carry subtext
  ("Manage credentials", "View API Key").
- The API-access page accepts `?siteUrl=` but returned "No pages found" for
  `https://amlhive.com.au` without trailing slash; with `https://amlhive.com.au/`
  it still showed the empty state — the working route was the Settings drawer,
  not a direct URL. Don't burn time on direct-url navigation.

## CDP prerequisites

Driving the Bing UI requires the user-signed-in debug Chrome on port 9222 —
see the `google-workspace-access` skill → `references/cdp-sheets-access.md`
for the launch/relaunch/profile pitfalls (same CDP machinery, different site).
The Bing login lives in the same profile the user signed into; the user's
normal Chrome (where they often open Bing) has NO debug port.

## Dashboard evidence to record (weekly review cadence)

From the Webmaster home (logged-in): total clicks / impressions for the period,
and "Top Recommendations" — e.g. observed 2026-08-08: (1) not enough inbound
links from high-quality domains, (2) some URLs not indexed due to robots
NOINDEX meta tags. Both are delivery-risk signals for the operating contract's
weekly review; record them alongside GSC evidence, never equate sitemap
inclusion with indexing.
