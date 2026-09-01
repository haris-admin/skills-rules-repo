---
name: backend-doctor
description: >-
  Diagnose a Python backend (FastAPI, Django, Flask, or similar) that won't start,
  fails auth/JWT verification, can't reach its database, or fails a startup
  "preflight"/settings-validation check — without ever reading .env/.env.local file
  contents directly (works even when those files are permission-denied). Framework-
  and project-agnostic: detects the settings mechanism instead of assuming one. Run
  when the user pastes a backend startup traceback, reports "backend won't start",
  "401/403 that doesn't make sense", "DB connection refused", "preflight failed",
  "JWKS/DNS error", or asks to check backend/env/DB config. Also covers cross-
  checking a paired frontend's env vars (Next.js/Vite) against the backend's, e.g.
  when auth works client-side but every authenticated API call fails server-side.
---

# /backend-doctor — Python backend startup & config diagnosis

Core constraint this skill is built around: **`.env`/`.env.local` files are commonly
permission-denied to you by design** (secret protection), across many projects and
tool configs, not just one. Never try to bypass that — read the *resolved* config
through the app's own code instead. Every check below is presence-only: booleans,
lengths, prefixes, fingerprints. **Never print a raw secret value, even partially.**

## Step 1 — Get the actual error

If the user hasn't pasted a traceback, ask for one before guessing. A "won't start"
report with no traceback wastes a round-trip — the traceback tells you which phase
failed (import time / settings validation / DB connect / migration / route mount).

## Step 2 — Identify the settings mechanism (don't assume)

```bash
grep -rl "BaseSettings\|pydantic_settings" --include="*.py" . 2>/dev/null | head -5   # pydantic-settings (FastAPI-common)
grep -rl "class Config\|django.conf" --include="*.py" . 2>/dev/null | head -5         # Django settings.py
grep -rl "app.config\[" --include="*.py" . 2>/dev/null | head -5                      # Flask
grep -rln "os.environ\|os.getenv" --include="*.py" . 2>/dev/null | head -10           # raw os.environ, no framework wrapper
```

Find the module that owns config resolution (e.g. `app/core/config.py`, `settings.py`,
`config.py`). This is the single import point for every check below — never grep the
`.env` file itself, always import the resolved settings object.

## Step 3 — Look for a startup validation ("preflight") pattern

Many production backends fail loudly on boot if critical config is still a placeholder.
Find it before assuming one doesn't exist:

```bash
grep -rln "preflight\|validate_settings\|check_env\|startup.*valid" --include="*.py" . 2>/dev/null
grep -rn "lifespan\|on_startup\|ready_check\|AppConfig.ready" --include="*.py" . 2>/dev/null | head -10
```

If found, read it — it usually names the exact placeholder strings/prefixes it
rejects (e.g. `example.com`, `test-`, `changeme`, `localhost` in a prod DB URL,
default framework secret keys). Reuse those exact literals in Step 4 rather than
guessing your own placeholder heuristics.

**Also check for an escape hatch that bypasses this check** — `SKIP_*`, `DISABLE_*`,
`BYPASS_*` env-backed booleans are common local-dev conveniences that can mask the
real problem by turning a loud boot-time crash into a confusing runtime failure
later (DNS/JWKS errors, silent 401s). If one is set, say so explicitly — it changes
the whole diagnosis.

```bash
grep -n "SKIP_\|DISABLE_\|BYPASS_" <settings_module>
```

## Step 4 — Presence-only diagnostic (the core technique)

Run the app's own settings resolution in a subprocess and print only shape, never
content. Adapt the import line to whatever Step 2 found; the pattern is universal:

```bash
python -c "
from <settings_module_path> import settings   # or however the project exposes it
import inspect

# List every field the project's own preflight/config calls out as
# placeholder-guarded, or every *_URL / *_KEY / *_SECRET / *_TOKEN field if no
# preflight exists. Never hardcode a project-specific field name across projects.
fields = [f for f in vars(settings) if any(s in f.upper() for s in ('URL','KEY','SECRET','TOKEN','DSN'))]
for f in fields:
    v = str(getattr(settings, f, ''))
    print(f, '| len=', len(v), '| looks_placeholder=', any(p in v.lower() for p in ('example', 'test-', 'changeme', 'placeholder', 'localhost')) if v else 'EMPTY')
"
```

For Django: `python manage.py shell -c "from django.conf import settings; ..."` with
the same presence-only body. For Flask: `flask shell` or a one-off script importing
`create_app().config`.

**If this diagnostic contradicts what the user believes they set** (e.g. they say
they edited the file but the resolved value is unchanged), the likely causes, in
order of frequency:
1. A duplicate key later in the same `.env` file overriding the one they edited (env
   file loaders generally apply last-occurrence-wins).
2. Wrong file edited (multiple `.env*` files in the repo — `find . -maxdepth 2
   -iname ".env*"` to enumerate, without reading contents).
3. Process wasn't actually restarted (env is read once at process start in most
   frameworks, not per-request).
4. CWD mismatch — relative `.env` paths resolve from the process's working directory,
   not the settings file's location.

Report which of these it is by asking the user to check narrowly (e.g. "search for
a second line starting with `KEY_NAME=`"), never by reading the file yourself.

## Step 5 — Cross-check a paired frontend, if relevant

If the symptom is "frontend auth succeeds but every backend API call fails," the
mismatch is usually between the frontend's public env vars and the backend's server
env vars pointing at different projects/environments. Same presence-only rule
applies, adapted per frontend framework:

```bash
# Next.js — public env vars are inlined at build time via @next/env, not
# plain process.env in a one-off node script:
node -e "
const { loadEnvConfig } = require('@next/env');
loadEnvConfig(process.cwd());
for (const k of Object.keys(process.env).filter(k => k.startsWith('NEXT_PUBLIC_'))) {
  const v = process.env[k] || '';
  console.log(k, '| present:', !!v, '| len:', v.length);
}
"
# Vite — VITE_-prefixed vars, similar idea via `import.meta.env` in a small script
# or by checking .env* presence with the same node/dotenv approach.
```

Compare a **shared identifier** between the two sides (a project ref embedded in
both a frontend public URL and a backend server URL) for equality without ever
printing the full value — e.g. `url.includes('<the-substring-from-the-other-side>')`.

## Step 6 — DB / migration connectivity

Detect the migration tool before running anything:

```bash
[ -f alembic.ini ] && echo "Alembic" 
[ -f manage.py ] && grep -q django . -r 2>/dev/null && echo "Django migrations"
find . -iname "flyway.conf" -o -iname "schema.prisma" 2>/dev/null
```

Then run the tool's own "current vs head" check (`alembic current` / `alembic
heads`, `python manage.py showmigrations`, etc.) — a mismatch here is a distinct
failure mode from a bad connection string and should be reported separately, not
conflated.

## Step 7 — Report

One short table: check | result | verdict. End with a root-cause hypothesis and the
**specific narrow next step** for the user (a line to check, a var to fix) — not a
generic "check your .env" restatement.

## Do not

- Never `cat`, `Read`, or otherwise print `.env*` file contents, even if a
  permission prompt would technically allow it — the presence-only technique exists
  precisely so this is never necessary.
- Never print a full secret value, even to confirm it "looks right" — length,
  prefix, and equality-to-a-known-placeholder are always sufficient.
- Don't assume the settings module, framework, or field-naming convention from a
  previous project — re-derive via Step 2 every time.
- Don't silently fix the `.env` yourself even if you could construct the right
  value — env file edits are the user's action; you diagnose and point at the line.
