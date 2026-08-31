# Observability And Error Management (all agents)

**Canonical rule.** Mirrors: `.cursor/rules/observability-and-error-management.mdc` (Cursor),
`.agents/rules/observability-and-error-management.md` (Antigravity). Summarised in `AGENTS.md`
(Codex), `CLAUDE.md` (Claude Code), `GEMINI.md` (Gemini). If mirrors drift, this file wins.

**Why this rule exists:** issue-148 — nginx rejected customer requests with hard 400s for 3–4 days
after the AWS migration with **zero** visibility (requests died before app code ran, so no Sentry
event; nobody watched origin status codes; one customer was lost). And in the same session,
`yourapp-rds-low-freeable-memory` was found stuck on `INSUFFICIENT_DATA` since creation — an alarm
that could never fire. Both failure classes are now forbidden by construction.

## 1. Observability is a deliverable, not an afterthought

- Every OpenSpec `proposal.md` must contain an **Observability** section answering: *how will we
  know in production if this change works, and how will we know if it breaks?* (logs, metrics,
  CloudWatch alarms, Sentry, synthetic probes — whichever apply). Matching acceptance criteria are
  required. A proposal without an observability answer is not ready for human approval.
- Everything implemented must be observable in production: **if it can fail, its failure must be
  visible without a customer reporting it.** Failure modes that are invisible from inside the app
  (e.g. the proxy layer rejecting requests before app code runs) need outside-in probes — see
  `.github/workflows/prod-cookie-probe.yml` for the pattern.

## 2. Exceptions: never swallowed, always logged, always surfaced

- Every `except` / `catch` must either handle the error meaningfully or **log it with context and
  surface it**. Bare `except: pass`, empty `catch {}`, and silent fallbacks that discard the error
  are forbidden — a swallowed exception is a defect regardless of whether the code "works".
- Errors must reach the log files that ship to CloudWatch (backend `/yourapp/backend*`, frontend
  `/yourapp/frontend*` log groups) and Sentry where an SDK is present. Local-dev noise stays out of
  the shared prod Sentry project (the issue-138 `ENVIRONMENT` guard pattern).
- **Do not conflate Sentry noise filters with the audit trail.** Skipping `audit_entries` for
  any logged-in denial/failure is **forbidden** — see
  `docs/agent_rules/data-retention-and-audit-trail-mandate.md` § CRITICAL SEPARATION. A blocked
  402/403/409 (and any authenticated ≥400) must still write an audit row.
- **Logged-in errors must reach Sentry too (C368, 1 Aug 2026).** Authenticated Principal / Agent /
  Auditor / admin (Bearer) HTTP ≥400 → Sentry **warning**; 5xx → **error**. FastAPI/Starlette do
  **not** auto-capture `HTTPException` (they are “handled”) — use the global handler in
  `backend/app/main.py` plus FE `fetchWithAuth*` `captureApiError`. Do **not** drop billing
  soft-lock (“Set up payment…”) from the browser `beforeSend` path (issue-197 drop was reversed).
  Fingerprints/grouping OK; Sentry is never a substitute for audit.
- **Error paths get tests like happy paths.** TDD applies to failure modes: what must NOT happen,
  what must be logged, what must be surfaced — each has a test citing its requirement.
- Never mask or transform credential-shaped values while logging; log presence/fingerprint only
  (existing standing rule).
- **Deploy after-action SES email:** only via `python3 scripts/send_after_action_email.py` — see
  `docs/agent_rules/ses-after-action-email-encoding.md`. Never `json.dumps(html)` into
  `--message "Body={Html={Data=…}}"` (literal `\n` / `\u2014` in Gmail). That CLI script is for
  **terminal/ad hoc sends only** (it exists to dodge AWS-CLI string-escaping bugs).
- **In-app internal SES alerts (C397, 8 Aug 2026):** for an alert the *backend itself* triggers
  (job-completion, admin notification), don't shell out to the CLI script — call
  `app/services/ses_alert_service.send_ses_email()` directly (`boto3`, no CLI/escaping layer to
  dodge in the first place) and build the HTML with the existing shared
  `app/services/email_template_service.render_email_template()` rather than new markup. See
  `app/api/internal/sync.py`'s `/sync/daily-batch` handler for the worked pattern: reused,
  unmodified template; sender at a dedicated `@yourapp.com.au` address (domain is already a
  verified SES identity — no new per-address verification needed); a failed send is logged with
  context and still writes an `ALERT_SENT` audit row (`outcome=FAILED`) rather than failing the
  triggering action.
## 3. Infrastructure is monitored at all times

- Infra changes ship **with their monitoring in the same change**: CloudWatch metric filters and
  alarms wired to the existing SNS topic, plus synthetic probes where the failure is invisible
  from inside AWS. Monitoring is part of the acceptance criteria, not a follow-up.
- Active monitoring surfaces already exist — Fleet Monitor/Pluto, CloudWatch alarms, scheduled
  GitHub Actions probes. **A production issue is not Resolved while its failure class is still
  unmonitored** — the incident's detection gap must be closed (new alarm/probe/filter) before the
  issue is marked done.
- A silent alarm is a defect: any alarm sitting in `INSUFFICIENT_DATA` (or otherwise unable to
  fire) is treated as a production issue in its own right, with the standard `/prod-issue` flow.
- **A falsely-`OK` alarm is worse than `INSUFFICIENT_DATA` and easy to miss** (issue-217,
  2026-08-03): `yourapp-backend-disk-high` and `yourapp-frontend-disk-high` were each defined with
  only `InstanceId`+`path` dimensions, but the real CWAgent `disk_used_percent` metric publishes
  `InstanceId`+`path`+`device`+`fstype`. The mismatch meant neither alarm ever matched a real
  datapoint, so `TreatMissingData: notBreaching` kept both reporting `OK` indefinitely while actual
  disk usage sat at 93%/24% — since 2026-07-06, invisibly. Before trusting any CloudWatch alarm's
  `OK` state, verify its `Dimensions` in `aws cloudwatch describe-alarms` actually match a real
  emitted metric in `aws cloudwatch list-metrics --metric-name <name>` for the same namespace — an
  `OK` alarm with no matching metric is not evidence of health, it's evidence of nothing.
- Application quality is read from this monitoring plus the TDD suites: test runs gate every
  deploy (the pipeline's test job blocks build/deploy on failure — never bypass it), and the
  monitoring tells us how the shipped code actually behaves. Both signals are required; neither
  substitutes for the other.
