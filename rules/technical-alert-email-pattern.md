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
