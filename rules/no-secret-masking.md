# No secret masking — treat credential-shaped fields as opaque (all agents)

Applies whenever an agent needs to display, log, or reason about a value that might contain a
secret (a connection string, API key, token, password) without printing the secret itself.

## Why this exists

**5 Jul 2026:** Asked to check which Supabase/R2 environment a local `.env` pointed at without
printing secrets. An agent wrote a Python one-liner with a `mask_host()` regex that only matched
`https?://...` URLs. `DATABASE_URL` uses the `postgresql+asyncpg://user:password@host` scheme,
didn't match the regex, fell through to the "return url unchanged" branch, and printed the
**plaintext database password** directly into the tool output.

Writing masking/redaction logic and trusting it is inherently fragile: any format the regex
doesn't anticipate silently falls through to the raw value, and by the time the mistake is visible
(in the printed output) it has already leaked into the transcript. "Be more careful with the
regex" is not a fix — the entire approach of transform-then-inspect is the bug. See
[credential-rotation-safety.md](credential-rotation-safety.md) for the related pattern of secrets
leaking through *error* output rather than deliberate printing.

## Rules

1. **Never derive a "safe" display string from a field that can carry embedded credentials** (any
   `*_URL`, `*_DSN`, `*_CONNECTION`, `*_TOKEN`, `*_KEY`, `*_SECRET`, `*_PASSWORD`,
   `*_CREDENTIAL`). Treat the whole field as opaque by name-pattern match, not by inspecting its
   apparent format.
2. **Only print fields that are non-secret by definition** — bucket names, environment name/enum,
   feature flags, booleans. Never a substring or regex-extracted piece of a credential-bearing
   field.
3. **If presence/identity of a credential-bearing field is genuinely needed, print
   `"<set>" if value else "<unset>"`, or a one-way fingerprint (`sha256(value)[:8]`)** — never any
   of the actual characters, masked or not.
4. **Decide the output allow-list *before* running the command**, by checking each field name
   against the keyword list above — not by writing transformation code and reviewing the result
   afterward.
5. **If a leak happens anyway, say so immediately and recommend rotation** — don't let "it was
   only visible in this session" become a reason to leave it as is.

## Related

- [credential-rotation-safety.md](credential-rotation-safety.md) — the related pattern where a
  secret leaks through a library's *error* message rather than deliberate printing/masking
- `.claude/skills/handling-sensitive-data/` — packages both patterns into one workflow
