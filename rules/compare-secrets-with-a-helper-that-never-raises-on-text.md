# Compare secrets, tokens and signatures with one helper that never raises on text (Python, all repos)

`hmac.compare_digest` and `secrets.compare_digest` raise `TypeError` when given a `str` with a non-ASCII character, so a caller who controls a header, query string or body can turn a normal refusal into a 500.

**Scope:** any Python service that compares a caller supplied value with a secret, token, signature or code.

## Why this exists

**23 Nov 2026 (HandleDispute, spec 38n):** a blind review found that `GET /disputes/{case}/track` with a token containing `é` returned 500 for an existing case and 404 for a missing one (a case existence oracle), and `POST /operations/auth/login` with a non-ASCII `admin_secret` returned 500 for a real operations email and 401 otherwise. Reproduced with `hmac.compare_digest("abc", "aéc")`. Only one call site had been fixed earlier.

## Rules

1. Put one helper in the codebase (`safe_equal(a, b)`): `None` on either side is False, `str` is encoded to UTF-8 with `errors="surrogatepass"`, then `hmac.compare_digest` on bytes.
2. Replace every direct call. Add a guard test that parses the source with `ast` and fails on any `compare_digest` call whose arguments are not both `.encode(...)` calls. No roster of allowed sites.
3. Status codes and bodies stay the same: a 500 becomes the route's existing refusal.
4. Test with a non-ASCII value at every route that takes a secret, and assert the same answer for an existing and a missing resource.
5. If a spec's own static test expects the literal word `compare_digest` in a module that already encodes to bytes, leave that module alone; do not edit the other spec's test.
