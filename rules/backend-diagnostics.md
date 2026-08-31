# Backend startup / config diagnostics (all agents)

Applies when the backend won't start, a preflight/settings check fails, auth
works client-side but every backend call 401s, or a DB/migration error appears.

Full procedure (Claude Code): global skill `~/.claude/skills/backend-doctor/`.

## Core rule

`.env` is permission-denied by design for secret protection — never try to read
it directly. Diagnose through the app's own resolved settings object instead,
printing **only** booleans/lengths/prefixes, never a raw value:

```bash
python -c "
from app.core.config import settings
for f in ('SUPABASE_URL','SUPABASE_JWT_SECRET','SUPABASE_SECRET_KEY','DATABASE_URL'):
    v = str(getattr(settings, f, ''))
    print(f, '| len=', len(v), '| is_placeholder=', v.startswith('https://example.supabase') if 'URL' in f else None)
"
```

## Check `SKIP_PREFLIGHT` before trusting a clean boot

`backend/app/core/preflight.py` hard-fails on placeholder Supabase/DB/Stripe
config **unless** `SKIP_PREFLIGHT=true` is set in `.env` (local-dev escape
hatch). A clean boot with `SKIP_PREFLIGHT=true` does not mean config is correct —
it means the check was skipped. Always check this var first when a backend boots
cleanly but authenticated requests still fail (JWKS DNS errors, 401s).

## Cross-check frontend vs backend Supabase project

If frontend Supabase calls (`/auth/v1/*`) succeed but backend API calls 401, the
two sides may point at different Supabase projects/keys. Check frontend env the
same presence-only way (Next.js `@next/env`'s `loadEnvConfig`, not raw
`process.env`), and compare the project ref substring between the two URLs
without printing either full value.

## After finding the root cause

Point the user at the specific line to check/edit — never read or edit `.env`
yourself.
