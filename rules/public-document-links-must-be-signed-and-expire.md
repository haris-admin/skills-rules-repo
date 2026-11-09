# Public document links are signed and expire (all agents, all repos)

Applies to any route that serves a PDF, receipt, report or file to someone without a login.

## Why this exists
**8 Nov 2026, Tap-Ease C75 A1:** two blind reviews found `/receipts/{n}/pdf` and `/shifts/{id}/report/pdf` skipped authentication by path prefix, and the ids were sequential. Anyone could read pickup, drop-off, ABN, card last four, auth code and driver earnings by counting. The spec named the risk but left protection "optional", and an agent recommendation ("permanent, deterministic link") had been recorded as if decided. Haris chose: signed link with expiry, range 7 days to 2 years, default 90 days.

## Rules
1. Never expose a guessable id on an unauthenticated route. Use a signed token bound to the object and an expiry; unsigned, tampered, wrong-object or expired returns 404.
2. The signing key is a managed secret, never in logs, errors or the client. The server issues the link, the client never signs.
3. Bypass authentication by exact-route allowlist, never by path prefix.
4. Test the negative cases: guessed id, no signature, tampered signature, signature for another object, expired.
5. List the exposed fields and the expiry in the data inventory.
6. An agent recommendation about access control is a recommendation. Ask the human before recording it as decided.
7. The link carries a random token stored on the row (22 characters, URL safe, from a CSPRNG), never a primary key, a business number or anything derived from them. The signature covers kind, token and expiry. Every failure (bad token, bad signature, expired, unknown) returns one identical 404 so nothing can be probed.
8. Keep tokens and signatures out of logs: no access log of the query string, redact the token segment in app logs, skip error reporting for 404 and 429 on these paths. Add a per-IP rate limit on the public routes.
9. The client never builds the URL. The terminal asks the server for the signed link and shows "QR code unavailable" if it cannot get one; it never falls back to an id based address (Tap-Ease C65C: the first QR carried the trip number and returned receipt not found).
