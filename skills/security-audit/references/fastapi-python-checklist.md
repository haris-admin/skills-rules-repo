# FastAPI / Python-stack security checklist

Concrete checks for a FastAPI + SQLAlchemy + Postgres service behind an nginx edge — the
common shape across this team's backends. Pair with the generic OWASP reference; this file
is the "where to actually look in this kind of codebase" layer.

## Entry point: app bootstrap

- Find the app factory (`app/main.py` or `app/asgi.py`) and read the middleware stack in
  the order it's registered — middleware order matters (e.g. auth must run before a
  handler that trusts `request.state.user`).
- `CORSMiddleware` — is `allow_origins` a wildcard (`["*"]`) at the same time as
  `allow_credentials=True`? That combination is the vulnerability by itself: it lets any
  origin make credentialed requests. A wildcard with `allow_credentials=False` is much
  lower risk on its own.
- Exception handlers — does a generic `Exception` handler leak `str(exc)` (which can
  include SQL text, file paths, internal hostnames) into the HTTP response body in
  production? Compare behavior with `DEBUG`/environment flag off.

## Auth & session

- Locate the JWT/session dependency (commonly a `Depends(get_current_user)`-style
  function). Confirm:
  - Signature algorithm is pinned (reject tokens with `alg: none` or an unexpected alg).
  - Expiry (`exp`) is checked, not just signature validity.
  - The dependency is actually applied to every router that needs it — grep for routers
    mounted without it, not just trust the ones that look protected.
- Role/permission checks — is "admin-only" enforced in the handler/dependency, or only in
  the frontend (hidden nav item, but the API endpoint itself accepts any authenticated
  caller)?
- Account lockout / retry-count logic — confirm a lockout can't be trivially reset by an
  unauthenticated caller, and that the unlock path itself is admin-only.

## Object-level authorization (IDOR) — usually the highest-value manual check

For every route that takes a resource ID (`/payouts/{id}`, `/transactions/{id}`,
`/users/{id}/...`):
- Does the handler filter the DB query by `owner_id == current_user.id` (or an equivalent
  ownership/tenant check), or does it fetch by ID alone and only check "is someone logged
  in"?
- For admin routes that legitimately need cross-user access, confirm the admin-role check
  is present and is the *only* path that skips ownership filtering.

## SQL / ORM

- Any `session.execute(text(...))` or raw `cursor.execute(...)` — is the SQL built with an
  f-string/`.format()`/`%`-interpolation from external input, or parameterized
  (`text("... WHERE id = :id"), {"id": id}`)?
- SQLAlchemy Core `.where()`/`.filter()` calls used correctly (values passed as bind
  params) vs. any place a filter condition is built as a raw string.
- Bulk/dynamic `ORDER BY` or column-name parameters taken from user input — these can't be
  parameterized the normal way and need an explicit allowlist of valid column names.

## Input validation

- Pydantic models on every external-input endpoint — are there any raw `dict`/`Any`-typed
  request bodies bypassing validation?
- File uploads — content-type and size limits enforced; filename never used directly as a
  filesystem path (path traversal via `../../`).
- Numeric/enum fields — does the handler trust a client-supplied `status`/`role`/`amount`
  field without server-side validation against the allowed set?

## Background jobs / webhooks

- Webhook receivers (payment processor, POS partner callbacks) — is the signature/HMAC
  verified before the payload is trusted, and is verification done on the raw body (not a
  re-serialized/re-parsed version, which can produce a different signature)?
- Are webhook endpoints idempotent (replay of the same event doesn't double-process a
  payout/transaction)?

## Rate limiting & abuse

- Login, password-reset, OTP/verification-code endpoints — any rate limit or backoff, or
  can they be hit unlimited times per second?
- Any endpoint that triggers an outbound email/SMS — can it be used to spam an arbitrary
  address/number without authentication?

## Logging & secrets

- Are request/response bodies containing card numbers, tokens, or passwords ever logged?
- Structured log lines — do they interpolate raw user input directly (log injection: a
  user-controlled newline/ANSI sequence forging fake log entries)?
- Are database/API credentials read from environment/secrets manager at runtime, or
  hardcoded/committed anywhere in the tree? (See secret-false-positives.md for what does
  and doesn't count as a real leak here.)

## Edge (nginx) & infra, when in scope

- `proxy_pass` targets match an actual known/intended backend — a stray or leftover vhost
  pointing at an unexpected upstream is itself a misconfiguration worth flagging.
- Security headers present on the public-facing 443 vhosts: `Strict-Transport-Security`,
  `X-Frame-Options` (or `frame-ancestors` CSP), `X-Content-Type-Options: nosniff`.
- TLS: no `SSLv3`/`TLSv1`/`TLSv1.1`, weak ciphers disabled.
- Any internal-only endpoint (metrics, admin, debug/`/docs` in production) reachable from
  the public internet that shouldn't be.
