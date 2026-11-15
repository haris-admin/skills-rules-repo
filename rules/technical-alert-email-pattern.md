# Technical alert emails follow one shared template and rate limit (all agents, all repos)

Applies whenever a service gets failure, health, job or deploy alerts by email.

## Why this exists

**3 Nov 2026:** Haris asked for professional emails for the technical side too, pointed at the HandleDispute template, and said "we will use the same pattern here" for ChargeRail.

## Rules

1. Reuse the pattern in `devops/technical-alert-emails/SKILL.md`: `(subject, text, html)`, badge per kind, details table with Sydney and UTC time, "What to check first", internal footer, escaped input.
2. Rate limit every alert type: one email per type per 30 minutes with a repeat count. Uptime emails only on first failure and on recovery.
3. Run the checker outside the machines it watches, so a dead box still alerts.
4. Alert text carries no secrets, tokens, PII or raw provider error bodies.
5. The first send, IAM changes and SES identity setup belong to the founder. Prepare short scripts; do not send.
6. Alert failures never fail a deploy.
7. **SES sandbox authorises the send against the sender identity and every recipient identity.** An address identity such as `hello@` counts even when the domain is verified. A Lambda role policy must list the domain and each address identity it sends from or to. Admin-profile test sends hide this: on 15 Nov 2026 a send from the owner's profile worked while every alert from the Lambda role failed for 28 minutes with `AccessDeniedException`. Test with a real invoke of the deployed function and read its log group.
8. **Every planned email uses the same layout, not only alerts (founder, 15 Nov 2026: "all the emails that we are planning to send out should be using a similar kind of pattern").** One shared renderer, a registry of planned emails, and tests for structure, escaping, plain text twin, contrast, dark mode, redaction, time zones, footers and brand leakage (ChargeRail OpenSpec 012, `backend/src/services/email_templates.py`). A new email is a registry entry with tests, never a one-off template. A customer email stays layout and wording only until the owner approves sending.
