# Log every external call and every API request, mask secrets by name (Tap-Ease, 6 Nov 2026)

Applies to any service that calls a third party (card provider, POS, SMS, email, payments) or exposes an API.

## Why this exists

**6 Nov 2026, Tap-Ease RCA0054:** Oxygen asked for the exact performKYC request body and none existed in any log, because payload
logging had been removed on 10 Oct 2026. The body had to be reconstructed from stored rows. Haris: "the raw request that went out and
the raw request response that we received, we need to capture that. We cannot afford to leave it out." and "Everything means everything."

## Rules

1. One shared helper writes a request line, a response line and an error line (type and duration only) for EVERY outbound call. A new
   integration uses it. Enforce with a test that walks the code (AST) and fails when an HTTP call lives in a function without the three calls.
2. Inbound requests and their responses are logged by one middleware that wraps receive and send, never consumes the body, skips
   non-text bodies (record type and size) and cannot break a request.
3. Log the body exactly as sent or received. Mask only secrets: credentials by field name (and any name ending token, secret or
   password), card numbers, and one-time digit codes in SMS and email text. Personal data is logged in full (Haris, 6 Nov 2026 and again 11 Nov 2026: "The risk of not storing PII data is much bigger than not having logs"). A field named `state` is an address in a body and a secret in a URL query.
4. Before deny-listing a field, read the code to learn what it means (Oxygen `pincode` is the postcode, the PIN is `newPIN`).
5. A key-name deny-list cannot catch a secret echoed under an innocent key. If a rule says provider replies must never be logged raw,
   keep it until the owner retires it; the owner did retire it for Clover OAuth refusals on 6 Nov 2026.
6. Any regex that scans log text must be linear: test it on 300000 characters. Keep scanning inside quoted values (a reset link in an
   href holds a token).
7. Existing tests encode old rules. Run the related suites before calling the change safe, and change a test only when the owner has
   decided the new rule; record the decision next to the test change.

## How to apply

Measure volume first (a Lambda polling an internal endpoint 75 times a minute doubled the line count), decide caps for list and
documentation endpoints, and estimate log storage cost before release.
