# Third-Party Client-Side Tag Guarding

Every third-party browser tag (analytics, ads, social pixels, session replay, bot management, tag managers) must carry five guards, and turning off a channel must remove its tag.

## When this applies

Whenever a client-side third-party `<script>` is added, changed, audited, or its vendor channel is
switched off.

## The five guards

| # | Guard | Why |
|---|---|---|
| 1 | **CSP allowlist entry, with a test** | Without it the browser silently blocks the script or its beacons. CSP violations do not reach error tracking, so the gap stays invisible until a Lighthouse run or a manual console check. |
| 2 | **Environment and production-host guard** | `NODE_ENV === 'production'` alone still loads the tag on preview or staging hosts; also check `window.location.hostname` against an allowlist. Otherwise dev and preview traffic pollutes the production analytics or ads account. |
| 3 | **Route-prefix privacy gate** | Block tags on authenticated routes (e.g. `/dashboard/**`, `/admin/**`) so no customer data or PII reaches a third party. |
| 4 | **Consent gating** | Any tag that sets non-essential cookies (ads, remarketing, pixels, most analytics) must wait for consent where privacy law or the site's own cookie policy requires it. |
| 5 | **Teardown on becoming blocked** | Client-side navigation does not remove an already-injected script, and many tags hook `history.pushState`. When the route gate trips, remove the script node and delete the tag's globals. |

Load tags lazily (`lazyOnload` or equivalent, after idle) so they stay out of the LCP window.

## The outlier is the bug

When several tags render together and one lacks a guard its siblings have, treat that one as the
defect, not a deliberate exception.

## Decommissioning a channel removes its tag

Switching a paid or analytics channel off in the vendor console does not stop the site loading the
tag. A leftover tag keeps dropping cookies, keeps failing CSP (console errors cost Lighthouse Best
Practices), and keeps its page weight. Real case (2026-09): two ad channels cut in August were
still loading on every public page a month later, adding ~360 KB and 10 third-party cookies to the
homepage with no consent gating. When a channel is cut:

1. Remove the tag component (or put it behind an explicit off flag) in the same change that records
   the cut.
2. Remove its CSP origins and its `preconnect` / `dns-prefetch` hints.
3. Update the tag inventory and the cookie/privacy policy disclosure.
4. Confirm on the live site: no request to the vendor origin, no vendor cookie.

## Keep an inventory, and never trust it as proof

Maintain a table of tags and their five guards, but re-verify each guard against the component
source (and ideally a live page load) before citing it. In the same 2026-09 case the inventory
showed every guard green while consent gating did not exist in code.
