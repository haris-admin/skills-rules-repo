# Build-time browser keys: prove them on the live bundle

Any single-page app that bakes `REACT_APP_*` (Create React App) or `VITE_*` values into its JavaScript at build time. A hosting-platform variable set after the build changes the server only, never the browser.

**Scope:** frontend and release work on Create React App, Vite or similar builds deployed from a Docker image or a pre-built bundle (Simplifii-OS, 5 Oct 2026).

---

## Why this exists

On 5 Oct 2026 Sentry and PostHog keys were added as Railway variables and the service was redeployed, twice. `/api/health` said `sentryConfigured: true`, which was true for the Node server only. The browser bundle still carried the old Sentry address and no PostHog key, because the browser values are written into the JavaScript by the build. Nothing in the health check could see that. Three image rebuilds followed before the live bundle matched.

## Core Directives

1. **Browser keys are build inputs.** To change a `REACT_APP_*` or `VITE_*` value, rebuild and publish a new image tag. A runtime variable does not reach the browser. Server-only values (`SENTRY_DSN`, service keys) are runtime and need only a redeploy.
2. **Health flags are not proof for the browser.** `sentryConfigured`, `posthogConfigured` and similar fields describe the server process. Prove the browser by reading the served JavaScript.
3. **Prove it on the live bundle, without printing the secret.** Fetch the page, find the `static/js/*.js` files, and compare in code: the DSN or key in the bundle equals the value in the env file you built from. Print only `True` or `False`.
4. **Also prove what must be absent.** Check the live database or API host is not in the bundle when it must not be (a workshop build must not contain the production Supabase address).
5. **Use a new tag per rebuild.** Do not overwrite the tag you may need to roll back to. Record the tag, digest and bundle filename in the shared notes.
6. **These browser keys are public by design.** Docker will warn that `ARG`s hold secrets; for the Supabase anon key, the PostHog project key and a Sentry browser DSN that is expected. Never pass a service-role key or private API key as a `REACT_APP_*` value.

---

## Patterns to Follow

```bash
# Fetch every script the page loads, then compare without echoing the key
for f in $(curl -sS https://host/ | grep -o 'static/js/[a-z0-9.]*\.js'); do curl -sS https://host/$f; done > b.txt
python3 - <<'EOF'
import re
t = open('/tmp/b.txt', encoding='utf8', errors='ignore').read()
print('PostHog key in bundle:', bool(re.search(r'phc_[A-Za-z0-9]{20,}', t)))
print('Sentry browser DSN in bundle:', bool(re.search(r'ingest(\.[a-z]+)?\.sentry\.io', t)))
print('production db host in bundle (must be False):', 'PROD_REF' in t)
EOF
```

## Patterns to Avoid

- Setting `REACT_APP_*` in the hosting dashboard and calling it done.
- Reading `sentryConfigured: true` as "browser errors are captured".
- Printing a DSN or key into chat or a log to compare it.
