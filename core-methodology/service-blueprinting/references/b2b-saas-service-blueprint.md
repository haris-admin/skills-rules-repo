# Applied B2B SaaS Service Blueprint: AMLHive Verification Engine

A concrete end-to-end service blueprint mapping customer onboarding and instant AML/CTF due diligence check execution in **AML Hive (amlhive.com.au)**.

---

## 1. End-to-End Blueprint Table

| Swimlane | Step 1: Account Registration | Step 2: Query Submission | Step 3: Automated Verification | Step 4: Certificate Generation | Step 5: Ongoing Monitoring |
|:---|:---|:---|:---|:---|:---|
| **Physical Evidence** | Signup page, welcome email, magic login link | Search input bar, Australian entity dropdown | Real-time scan progress spinner, status toast | Downloadable audit-ready PDF, verification hash badge | Weekly email digest, Slack alert notification |
| **Customer Actions** | Enters practice email, creates password | Types company name or ACN; clicks "Verify Entity" | Watches live progress indicator | Downloads compliance certificate for client file | Reviews monthly compliance dashboard |
| *Line of Interaction* | ═══════════════════════ | ═══════════════════════ | ═══════════════════════ | ═══════════════════════ | ═══════════════════════ |
| **Frontstage Actions** | Authenticates session via NextAuth/JWT | Validates input format (ACN/ABN regex) | Streams step-by-step progress via SSE/WebSocket | Renders signed PDF preview in browser | Sends automated weekly summary email via Brevo |
| *Line of Visibility* | ─────────────────────── | ─────────────────────── | ─────────────────────── | ─────────────────────── | ─────────────────────── |
| **Backstage Actions** | Verifies firm email domain against whitelist | Checks customer credit balance in Stripe | *(Optional)* Human compliance officer review if high-risk match flagged | Logs permanent audit row in immutable audit vault | Scans AUSTRAC & ASIC register deltas via nightly cron |
| *Line of Int. Interaction*| ─────────────────────── | ─────────────────────── | ─────────────────────── | ─────────────────────── | ─────────────────────── |
| **Support Processes** | AWS Aurora DB user record creation | Stripe Billing API checks active plan | ASIC Registry API + Sanctions OpenSearch DB query | PDF generation worker (Puppeteer/Chrome headless) | Nightly Celery/Redis batch sync worker |

---

## 2. Identified Vulnerabilities & Failure Remediation

1. **Failure Point (Step 2 - ASIC API Downtime)**:
   - *Risk*: Upstream ASIC register API throws 503 or takes $> 15$ seconds to respond.
   - *Architecture Fix*: Cache previous company extracts in local Redis/Aurora with TTL $= 24$ hours; provide cached snapshot with clear timestamp if live gateway times out.
2. **Wait Point (Step 3 - High-Risk Match)**:
   - *Risk*: A false-positive politically exposed person (PEP) name match freezes user onboarding.
   - *Architecture Fix*: Return partial clearance certificate immediately; flag ambiguous entity for one-click manual secondary confirmation.
