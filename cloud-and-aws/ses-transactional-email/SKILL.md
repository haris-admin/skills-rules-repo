---
name: ses-transactional-email
description: Ensure high email deliverability, MIME RFC-2047 subject encoding, DKIM/SPF verification, and template consistency. Use when sending or reviewing SES transactional email — encoding subject lines, localizing timestamps, masking PII in payloads, or investigating bounce/complaint/deliverability issues.
---

# SES Transactional Email Hygiene

## Core Standards
1. **Header Encoding**: Always encode email Subject lines with RFC-2047 UTF-8 (`=?UTF-8?B?...?=`) to prevent truncation on emoji or special characters.
2. **Timezone Localization**: Render all timestamps in the user's localized timezone (e.g. `AEST`/`AEDT`), never raw UTC.
3. **PII Masking**: Mask sensitive personal identifiers (phone numbers, tax numbers, bank accounts) in notification payloads.
4. **Deliverability**: Maintain clean suppression lists and monitor SES bounce/complaint rates.
5. **Sandbox permissions (14 Nov 2026)**: an IAM send permission must cover the recipient identity and the identity's default configuration set, not only the sender; pin the sender with `ses:FromAddress`. Verify a domain with Easy DKIM (3 CNAMEs, DNS only) and every recipient outside it. Prove the path with one real send, because the alert service never raises. Keep customer mail on its own provider; do not request production access just to email your own addresses.

