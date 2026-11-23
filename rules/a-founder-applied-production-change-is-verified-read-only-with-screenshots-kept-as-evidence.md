# A founder-applied production change is verified read-only afterwards, and the evidence is kept

After the owner applies a change, the agent checks the result from a different path than the one that applied it, changes nothing, and files the evidence in the repository.

**Scope:** security settings, DNS, TLS and certificate changes made by the owner.

---

## Core Directives

1. **Second source.** If a script applied the setting, read it back in the provider dashboard (or the reverse). A re-read by the same script is not independent.
2. **Screenshot the pages.** Save the two or three pages that show the values and commit them under `docs/history/evidence/` with the date.
3. **Write down what stayed off.** Record settings deliberately left off (for example HSTS until the live checks pass) and why.
4. **Close your own tabs.** Leave no browser tab open that you created.

## Why this exists

**23 Nov 2026 (SonoVantage F8):** SSL mode, Always Use HTTPS and minimum TLS were set by the owner's script, then confirmed in the Cloudflare dashboard (Full (strict), on, TLS 1.2), with screenshots kept as evidence.
