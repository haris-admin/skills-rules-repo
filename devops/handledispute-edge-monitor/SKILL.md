---
name: handledispute-edge-monitor
description: Use when checking HandleDispute TLS, HTTPS, API health.
version: 1.0.0
author: Mercury
license: MIT
metadata:
  hermes:
    tags: [monitoring, tls, https, cloudflare, pre-dispute, production]
    related_skills: [monitoring-alert-verification, undispute-merchant-enrichment-agent]
---

# HandleDispute edge monitor (TLS + HTTPS + API health)

## When to Use

Use when asked whether `handledispute.com.au`, `www.handledispute.com.au` or
`api.handledispute.com.au` are up, whether their certificate is valid or expiring, whether
plain HTTP is redirected, or what the production API reports about itself. Also use when the
6-hourly watchdog or weekly digest fires and the finding needs interpreting.

Public-edge watchdog for the Pre-Dispute production hostnames. Both names sit behind
**Cloudflare**, so the certificate a browser sees is Cloudflare's edge certificate, not
something certbot on an origin renews. Do not go looking for origin certs here.

## Monitored

| Host | Role | Expected |
|---|---|---|
| `handledispute.com.au` | web app | 200 `text/html` |
| `www.handledispute.com.au` | web app alias | 200 `text/html` |
| `api.handledispute.com.au` | production API | 200 `application/json` |

Per run (all read-only, no credentials, public path only):

1. **DNS** — A/AAAA resolution for each host.
2. **TLS** — chain verify (default CA store), protocol + cipher, notBefore/notAfter, days
   left, issuer, and **SAN actually covers the requested hostname**.
3. **HTTP** — status, latency, content-type, HSTS, `x-content-type-options`.
4. **HTTPS enforcement** — `http://handledispute.com.au/` must 301/308 to `https://`;
   returning 200 is a 🔴 (plaintext served), any refusal (4xx at the edge) is a digest note.
5. **API depth** — `GET /` must report `status=online` + `version`; `GET /health` must report
   `status=healthy`, `database=ok`, `environment=production`, `debug=false`, and root/health
   versions must match. Dependency block (`clamav`, `email_provider`, `sms_provider`) is
   surfaced as a standing note, never as an outage.
6. **Hygiene notes** (digest only): missing HSTS, public `/docs` in production, plain-HTTP
   non-redirect, mock email provider, unconfigured SMS, ClamAV not approved.

## Commands

```bash
python3 ~/.hermes/scripts/handledispute_edge_monitor.py            # watchdog: prints ONLY on problems
python3 ~/.hermes/scripts/handledispute_edge_monitor.py --report   # full picture (weekly digest)
python3 ~/.hermes/scripts/handledispute_edge_monitor.py --json     # machine dump
```

State (version tracking + repeat suppression): `~/.hermes/state/handledispute_edge_state.json`.
Delete it to re-alert immediately on an unchanged problem.

## Crons

| ID | Schedule | Script | Behaviour |
|---|---|---|---|
| `50c078daf27f` | `10 */6 * * *` (00:10/06:10/12:10/18:10) | `handledispute_edge_monitor.py` | silent when healthy; alert block otherwise |
| `0cc614455b97` | `15 7 * * 1` (Mon 07:15) | `handledispute_edge_digest.sh` → `--report` | always delivers the full picture |

Both deliver to the Handle-dispute Telegram group (origin).

## Thresholds and noise rules

- Certificate: 🟡 under 21 days, 🔴 under 10 days / expired / verify failure / SAN mismatch.
- API latency: 🟡 over 3000 ms. Response time is measured `urlopen` wall time from WSL.
- **Repeat suppression**: an identical alert set is not re-sent inside 12 h
  (`SUPPRESS_HOURS`). Persistent config items (HSTS, mock providers) live in notes so the
  watchdog stays silent instead of paging every 6 hours about the same non-outage.
- Exit code is always 0 — stdout is the signal; a non-zero exit would replace the real
  findings with a scheduler error alert.

## Cloudflare notes

- Edge certificate observed 2026-11-03: Let's Encrypt **YE1** wildcard,
  SAN `*.handledispute.com.au` + apex, valid 2026-10-31 → **2027-01-29**, TLS 1.3
  `TLS_AES_256_GCM_SHA384`. Renewal is Cloudflare-managed — do not "fix" it with certbot.
- No zone-scoped Cloudflare token in this fleet: the R2 token answers **403 on `/zones`**, so
  zone-level checks (cert packs, WAF, Always Use HTTPS toggle) cannot be automated from here.
  Measure from the public edge instead, and ask Haris to flip dashboard settings.
- HSTS and Always Use HTTPS are **Cloudflare dashboard** settings (SSL/TLS → Edge Certificates),
  not origin config: proxied responses are stamped at the edge, so changing nginx does nothing.

## Standing findings at first run (2026-11-03)

- ✅ TLS 1.3, valid chain, 87 days left on all three hostnames (shared wildcard).
- ✅ API v0.240.21, `environment=production`, `debug=false`, `database=ok`, `/docs` not public.
- 🟡 No `Strict-Transport-Security` on any hostname → enable HSTS in Cloudflare (with
  `includeSubDomains`; start with a short max-age, e.g. 300 s, before 1 year).
- 🟡 `http://handledispute.com.au` answers **400** instead of redirecting → enable
  **Always Use HTTPS**.
- 🟡 `email_provider=mock` and `sms_provider=not_configured` in production; `clamav=pending_approval`.
  Real cardholder notifications are therefore not being sent — config, not an outage.

## Adding a host

Append `{"host": ..., "role": ..., "expect": (200,), "kind": "html"|"json"}` to `HOSTS`
in the script. Keep `kind="json"` for the API only — the API-depth block assumes it.
