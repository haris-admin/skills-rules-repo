# Five-Swimlane Service Blueprinting Architecture

Originally developed by G. Lynn Shostack and codified by the Nielsen Norman Group, a **Service Blueprint** visualizes the relationships between customer-facing touchpoints and the backstage technical and human processes required to deliver a service.

---

## 1. The Five Horizontal Swimlanes & Three Lines of Separation

```
┌────────────────────────────────────────────────────────────────────────┐
│ 1. PHYSICAL EVIDENCE / ARTIFACTS                                       │
│    Landing page · Invoices · Search reports · SMS 2FA · UI buttons     │
├────────────────────────────────────────────────────────────────────────┤
│ 2. CUSTOMER ACTIONS                                                    │
│    Visits site · Enters business name · Clicks 'Search' · Pays invoice │
├════════════════════════════════════════════════════════════════════════┤ ◄── LINE OF INTERACTION
│ 3. FRONTSTAGE (ONSTAGE) CONTACT ACTIONS                                │
│    Automated onboarding chat · Live support rep · Email notifications   │
├────────────────────────────────────────────────────────────────────────┤ ◄── LINE OF VISIBILITY
│ 4. BACKSTAGE CONTACT ACTIONS                                           │
│    Manual compliance verification · Exception triage · Refund approval │
├────────────────────────────────────────────────────────────────────────┤ ◄── LINE OF INTERNAL INTERACTION
│ 5. SUPPORT PROCESSES & TECHNICAL INFRASTRUCTURE                         │
│    Stripe API · ASIC DB query · OpenSearch cluster · Aurora Postgres   │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Key Lines of Separation

1. **Line of Interaction**: Divides the customer from the service provider's front-facing systems. Every crossing point represents a primary direct touchpoint.
2. **Line of Visibility**: Divides what the customer can see from what is hidden backstage. If a step lies below this line, the customer has zero direct perception of it (and experiences it only as waiting latency).
3. **Line of Internal Interaction**: Divides operational employees/agents from the underlying databases, software systems, and third-party API providers.

---

## 3. Failure Points & Wait Latencies (Bottleneck Diagnostics)

A service blueprint must explicitly flag:
- **Failure Points (F)**: Steps where omissions, timeouts, or errors are likely to occur (e.g. ASIC API 504 gateway timeout, failed 2FA SMS delivery, invalid credit card).
- **Wait Points (W)**: Delays where the customer is idle waiting for backstage execution (e.g. manual identity check review, batch end-of-day bank transfer sweeps).
- **Remediation Rule**: Every Wait Point $> 30$ seconds must provide transparent UI progress feedback (e.g. live step-by-step progress bar or optimistic UI rendering).
