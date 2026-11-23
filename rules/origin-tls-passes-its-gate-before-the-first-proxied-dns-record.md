# Origin TLS passes its gate before the first proxied DNS record exists

A proxied record sends real visitors to the origin. Create it last, after the certificate, the strict mode and the TLS checks have passed.

**Scope:** putting a site behind a proxy such as Cloudflare in Full (strict) mode.

---

## Core Directives

1. **Order.** Origin certificate installed, then zone settings (strict, always HTTPS, minimum TLS 1.2), then the container and edge deploy, then the origin TLS gate with its expected count, then the DNS records.
2. **Do not make DNS the first public step.** An unproxied or early record exposes a half-built origin and invites 525 and 526 errors.
3. **Create records one at a time.** Check the form's summary line (name, address, proxied) before each save, and check the record count rose by exactly the number added.
4. **Leave mail and verification records alone.** Count them before and after.
5. **Verify through the proxy.** Request each name over HTTPS and HTTP and read the redirect target.

## Why this exists

**23 Nov 2026 (SonoVantage):** the 54-check TLS gate passed before any A record existed; six proxied records then went in through the dashboard (13 records became 18) and the 40-check public run and the 61-check full run both passed.
