# Provider errors: admins see them, end users get a general message, logs keep the body (all agents, all repos)

Applies wherever an app calls a third-party provider (payments, cards, OAuth) and reports its failures.

## Why this exists

**26 Oct 2026, Tap-Ease RCA0046:** a card KYC refused by the provider ("Maximum number of attempts failed") showed the admin only
"An unexpected error occurred", while driver routes returned the provider's raw text. Haris: on the admin side send exactly what
we see; on the user side "it should not be the exact error message passed through, because that exposes a risk of finding out
about the system and figuring out how to break that system"; and "I don't mind adding the error body to the logs ... It should be
allowed for an admin or engineer to investigate later." A user may still see their own data.

## Rules

1. Admin responses carry the provider's message as received. Keep any existing project rule that removes vendor names from text.
2. End-user responses carry a fixed general message per action. Never repeat the provider's text or name.
3. Log every provider error: status, endpoint, the provider's message and the body cut to a safe length (500 characters). Never log
   credentials or request payloads.
4. Where an existing test says the provider body must not be logged, treat that as a requirement change: confirm with the owner, then change
   the test and the docs together.
5. When logging an error from a flow with secrets (OAuth), log only a whitelist of reason fields and mask the known secret values.
6. Keep a catalogue of seen provider errors with date, evidence and owner of the fix (Tap-Ease: `docs/oxygen_provider_errors.md`).
