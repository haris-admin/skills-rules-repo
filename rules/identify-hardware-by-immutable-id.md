# Identify hardware by immutable id

Identify a physical device by its immutable hardware identifier (serial number) plus its owner; treat vendor-issued ids as mutable attributes that are stored, never compared.

**Scope:** any system that registers physical terminals, handhelds, tablets or readers against a third-party platform id.

## Why this exists

Added 19 Oct 2026 (TapEase POS, C46-R9, Haris). A Clover Flex 4 moved merchants and its Clover device id changed. The backend compared serial, device id and merchant with the Portal's record and refused pairing, then start-up, on a stale device id. Haris: "device IDs come and go, but the serial number remains the same."

## Core Directives

1. **The serial number plus the merchant (owner) identify the terminal.** These are the only identity comparisons.
2. **Platform-issued ids (device id, UUID) are stored as reported**, with a warning log when one changes. Never refuse because they differ.
3. **Foreign keys follow the stored id**, so a changed id writes a new row and leaves the old one for history.
4. **Open work must not be silently moved or lost** when the id changes. Warn an operator about an open shift for the same serial; do not rebind it without a decision.
5. **The external system of record should be updated too**, but our service must not depend on that to keep working.

## Verification & Guardrails

- Tests: serial or merchant mismatch refuses, naming only those fields; a device id mismatch is accepted and stored.
