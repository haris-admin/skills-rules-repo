---
name: cloud-provider-account-research
description: "Cloud signup research: types, verification, free tiers."
---

# Cloud Provider Account Research

Research account types, identity/real-name verification, free-tier offers, and startup (Activate-style) programs for cloud providers — Alibaba Cloud, AWS, GCP, Azure — with an Australian-entity lens (sole trader / Proprietary ABN vs Pty Ltd).

## When to use
- User asks about signing up for a cloud provider: account types (individual vs enterprise), verification/real-name requirements, free tier / token credits, or startup programs.
- Comparing provider perks (e.g. AWS Activate vs Alibaba Cloud AI Catalyst) for one of the user's entities (e.g. harishabib.au vs AMLHive).

## Workflow
1. Go to the provider's OFFICIAL help center / docs first. Exact doc URLs are part of the deliverable — attach one to every claim.
2. Docs sites are often JS-rendered. Test with curl: a page returning a small HTML shell (~3KB) is a JS app → use the browser. A page that server-renders real content (tens of KB) → curl + strip tags/scripts works fine. **Before switching to the browser, grep the shell for an inline state blob** — `window._ROUTER_DATA = {...}`, `__NEXT_DATA__`, etc. Some SPAs (e.g. Volcengine docs) embed the FULL article server-side in that JSON: `curl` + `python3 -c "import json..."` extracts it without a browser. Volcengine recipe: body lives at `loaderData["docs/(libid)/(docid$)/page"]["curDoc"]["Content"]` (a JSON string containing a Quill delta `{"version":"0.4.16","data":{"0":{"ops":[...]}}}` — double `json.loads`, join `op["insert"]`); the nav tree at `loaderData["docs/(libid)/layout"]["docListMap"]` gives every docID→Title for sibling-page discovery.
3. When a docs URL 404s, do NOT guess new URLs: fetch a live sibling page and grep its internal `href`s to discover the current URL structure (providers restructure docs constantly; old URLs keep returning HTTP 200 with a 404 shell, so check for `notfound:"true"` in the HTML).
4. For marketing pages (free-tier, startup programs), extract text with browser_console `document.body.innerText` — the a11y snapshot is noisy on these.
5. Verify free-tier / startup T&C on the official page itself — headline numbers (e.g. "70+ million tokens") differ from actual eligibility rules (e.g. enterprise-only tiers, one account per user).
6. Flag explicitly anything official docs do NOT confirm (e.g. sole-trader ABN acceptance as an enterprise document) as unverified, and recommend a support ticket before final signup decisions.

## Pitfalls
- Search engines (Google, Bing, DuckDuckGo) frequently block automated curl with CAPTCHAs — use the provider's own docs index / site links instead of burning time on them.
- **Don't trust that a vendor's international site exists** — some CN vendors (Volcengine) shut down their intl brand: `volces.com`/`volcanoengine.com` are NXDOMAIN **globally**. When local DNS fails, confirm via public DoH (`curl -s "https://dns.google/resolve?name=<domain>&type=A" -H "accept: application/dns-json"`); NXDOMAIN from 2+ resolvers = domain dead, not a geo-block. Then probe the API host directly: dummy POST → 401 JSON = live service; timeout/000 = dead.
- **CN-gated signup is visible on the live form** — check the country-code field on the registration page (Volcengine hard-codes +86 on every tab; no email-only path). A live docs page is not proof an international user can sign up; the form is.
- Old Alibaba Cloud doc URLs 404 after restructuring; the current canonical set is in `references/alibaba-cloud-international.md`.
- Headline free-tier numbers ≠ what an individual (unverified) account actually gets; "enterprise exclusive" offers usually require company verification.
- Signup forms often collect just email+password for BOTH account types — entity details come later at profile completion / verification, so the signup form alone doesn't answer "can a sole trader sign up".

## Provider references
- `references/alibaba-cloud-international.md` — Alibaba Cloud (intl): canonical doc URLs, individual vs enterprise verification, free tier T&C, Model Studio free quota mechanics, AI Catalyst startup program, Australia payment/contracting-party facts, dual-account rules, gotchas.

## Verification checklist before reporting
- [ ] Every claim carries an exact URL
- [ ] Findings dated (docs show "Last Updated"; note it where visible)
- [ ] Unverified / discretionary items flagged as such
