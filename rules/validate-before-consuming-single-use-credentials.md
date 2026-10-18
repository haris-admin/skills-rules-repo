# Validate before consuming single use credentials

Never spend a one-time code, pairing OTP or authorisation code before every cheap check that could fail has run.

**Scope:** any backend or agent flow that calls a service that burns a single-use credential (pairing OTP, OAuth code, magic link, reset token).

## Why this exists

Added 19 Oct 2026 (TapEase POS, C46-R6). The terminal backend asked the Portal to validate the pairing OTP first and compared the terminal's identity afterwards. When the identity check failed, the OTP was already spent, so the driver had to request a new code and could not retry. It looked like "no active OTP" and cost several test rounds.

## Core Directives

1. **Cheap, side-effect-free checks first.** Identity, ownership, merchant, status, format and quota checks run before the call that consumes the credential.
2. **Consume last, once.** The credential-spending call is the last step that can fail for a reason you could have known earlier. Never retry it automatically.
3. **A refusal before consumption must say what is wrong and that the code is still valid.** Name the differing fields, never their values.
4. **Single-use authorisation codes (OAuth `code`) are credentials.** Do not paste them into chat, logs or tickets, and never replay one to "test" an endpoint.

## Patterns to Follow

```text
lookup(serial) -> compare serial + merchant -> validate_otp(serial, otp) -> create session
```

## Patterns to Avoid

```text
validate_otp(serial, otp) -> lookup -> compare identity -> 403   # code already burned
```

## Verification & Guardrails

- A unit test asserts the consuming call is NOT awaited when the pre-check fails (see `test_c46_pairing_identity_first.py`).
- Review any new flow that calls a vendor "validate" or "exchange" endpoint for what runs before it.
