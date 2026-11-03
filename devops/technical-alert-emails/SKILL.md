---
name: technical-alert-emails
description: Build professional technical alert emails (uptime, API 5xx, background job failures, deploy results) with rate limiting, a shared HTML and plain-text template, and AWS SES. Use when adding failure or health alerts to a service, designing who gets emailed and how often, or reusing the HandleDispute and ChargeRail alert template.
---

# Technical Alert Emails (HandleDispute pattern, reused in ChargeRail)

Origin: Haris, 3 Nov 2026: "make the professional emails even for the technical side of the things as well", then "check that ideas-handledisute that we have made a template for the professional email. we will use the same pattern here." Reference implementations: `ideas-handledispute` OpenSpec 62 (`render_technical_alert_email`) and `ideas-ev-charging/infra/monitor/handler.py`. AMLHive's table based layout (`docs/auth_email_templates.md`) is the ancestor.

## Template contract (every service uses the same one)
- Returns `(subject, plain_text, html)`. Subject: `[service environment] kind: title`.
- HTML: full document, `role="presentation"` tables, 600px card, hidden preheader, dark-mode aware, brand header, one coloured badge per kind, title, details table, "What to check first" list, optional "N similar alert(s) suppressed" line, internal footer ("Internal technical alert"), no customer footer (no privacy or unsubscribe text).
- Details table always shows Environment, Alert type, Time (Sydney, AEST or AEDT) and Time (UTC).
- Plain text twin has the same facts with no markup. Subject encoded UTF-8 (SES rule `ses-transactional-email`).
- All untrusted text is HTML escaped. No secrets, no PII, no raw provider bodies.
- Kinds and first checks: `api_error` (container logs, readiness URL, rollback), `job_failure` (service status, backups folder, run now), `infra_health` (health script, both boxes), `deploy` (no action on success, rollback on failure), `recovered`.

## Rate limiting
One email per event type per 30 minutes (config value `rate_limit_minutes`), counting repeats and showing the count on the next email. State per type in a small store (ChargeRail: SSM parameter `/chargerail/monitor/event-<type>`). Uptime checks email only on the first failure and on recovery. If the send fails, do not update state, so the next run retries.

## Architecture that survives a dead server
Run the checker outside the machines it watches (ChargeRail: Lambda on a 5 minute schedule). Box-side jobs (backup, API 5xx lines, container restarts) and deploy scripts report events to the same Lambda; it applies the rate limit and sends. Deploy scripts must never fail because an alert could not be delivered.

## Build order (TDD)
1. Write tests from the founder's decisions (decision table, rate-limit window edges, escaping, plain text has no markup, each kind has a badge and checks). Watch them fail for the right reason.
2. Implement the pure functions first (`decide`, `decide_event`, `render_alert_email`), then the thin AWS wrapper.
3. Run the live checks locally without sending.

## Handoffs and approvals
- IAM, SES identity creation and any first email are founder-run short scripts (`~/name.sh`), never run by the agent. Sending the first email needs Haris's approval.
- Record sender, recipients, event types and rate limit as his verbatim decisions in `context.md`.
- Add the IAM policies, Lambda and schedule to Terraform; hand-made resources drift.

## In-process variant (HandleDispute backend, 3 Nov 2026)
Use this when the service is a single FastAPI app and a separate checker is not yet justified (OpenSpec 62).
- **Service:** `AlertService.notify(kind, title, detail, fingerprint)` returns True only when handed to the transport, and **never raises**. Off by default (`ALERT_EMAIL_ENABLED=false`), never sends when `ENVIRONMENT` is `local` or `test`. Sender, recipients (comma list) and rate limit are settings, so "for now" recipients are config, not code.
- **Hooks:** an `Exception` handler for unhandled 5xx (keep the default `500 Internal Server Error` plain-text response; expected 4xx and deliberate 503s do not alert) and the `except` block of each scheduler loop. Bound the send with `asyncio.wait_for(..., 2.0)` and give the AWS client short timeouts so a slow mail service cannot hold up the failing work.
- **No message text:** alert detail is the exception type and innermost `file:line in function`, never the message (messages carry personal data). Redact emails, JWTs, bearer tokens, long hex or base64 and card-like digit runs, and cap the body.
- **Rate limit:** state per `(kind, fingerprint)`; the window starts only on a successful send; suppressed repeats are counted into the next email.
- **Transport:** SESv2 `send_email` with `Text` and `Html` parts, credentials from the instance role (boto3 default chain), IAM `ses:SendEmail` only, resource the sender identity, condition `ses:FromAddress`.
- **Before promising delivery, read the account:** `aws sesv2 get-account` (production access, quota, shared use) and `get-email-identity` (verification). An address identity can send but gives no domain DKIM; mail to Gmail may land in spam, so prefer a domain identity with Easy DKIM records the founder adds.
- **Keep customer email separate:** the alert switch and transport are independent of the customer `EMAIL_PROVIDER`, which can stay `mock` while alerts are live.

## Lessons from the first ChargeRail run (3 Nov 2026)
- The first box check found a real fault: the nightly backup had failed since install because its script lost its quoting. See rule `install-scripts-as-files-not-quoted-strings`.
- Deploy hooks fan in from every session; the 30 minute window suppressed the approved test email. See rule `alert-fanout-and-suppression-check`.
- The timer install on the box was blocked by the auto mode classifier (persistence). Prepare `~/cr-box-events.sh` for the founder instead.
- Check SES identity status (`VerifiedForSendingStatus`) before promising delivery.

