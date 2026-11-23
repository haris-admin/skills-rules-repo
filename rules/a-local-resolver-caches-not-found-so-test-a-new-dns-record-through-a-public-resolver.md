# A local resolver caches not found, so test a new DNS record through a public resolver

Right after a record is created, the machine you test from may still hold the earlier not-found answer.

**Scope:** checking that a newly created DNS record resolves.

---

## Core Directives

1. **Ask a public resolver** (`dig +short A name @1.1.1.1` and `@8.8.8.8`) and, if it answers, test the site with `curl --resolve name:443:IP`.
2. **Do not call it broken** until a public resolver says so. The local cache clears on its own (often within the hour); the macOS flush is `sudo dscacheutil -flushcache; sudo killall -HUP mDNSResponder`.
3. **Tell the owner** that their browser may show the same error for a while and that another network or a phone on mobile data is a quick check.

## Why this exists

**23 Nov 2026 (SonoVantage):** five names answered at once but the apex returned could not resolve on the Mac, while 1.1.1.1 and 8.8.8.8 returned Cloudflare addresses and a `--resolve` test returned 200 with a valid certificate.
