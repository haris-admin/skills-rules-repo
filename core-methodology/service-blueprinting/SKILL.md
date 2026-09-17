---
name: service-blueprinting
description: >-
  Map end-to-end operational service delivery across five swimlanes (Physical Evidence, Customer Actions, Frontstage, Backstage, and Support Processes). Use when designing multi-tiered software delivery workflows, diagnosing wait points and system failure points, coordinating backstage technical processes with customer touchpoints, or auditing cross-functional service operations.
---

# Service Blueprinting Architecture

A disciplined operational design framework formulated by G. Lynn Shostack and codified by the Nielsen Norman Group to visualize how customer touchpoints connect directly with backstage staff, technical systems, and third-party APIs.

## When to Use

- **Service & Product Redesign**: When mapping how a customer action cascades through frontstage interfaces, backstage human checks, and underlying technical databases.
- **Isolating Latency & Wait Points**: When identifying where customers experience uncommunicated delays or bottlenecks during onboarding and execution.
- **Cross-Functional System Audits**: When aligning engineering, customer support, operations, and external API vendors around a unified delivery timeline.
- **Failure-Mode Prevention**: When analyzing edge-case failure points (e.g. external gateway timeouts, failed verification) to architect automated fallbacks.

---

## The Five-Swimlane Blueprinting Framework

```
  1. PHYSICAL EVIDENCE    Touchpoints, UI screens, PDF reports, emails
  ───────────────────────
  2. CUSTOMER ACTIONS     Every explicit action taken by the end user
  ═══════════════════════ ◄── LINE OF INTERACTION
  3. FRONTSTAGE ACTIONS   Customer-visible responses, automated bot/agent chat
  ─────────────────────── ◄── LINE OF VISIBILITY
  4. BACKSTAGE ACTIONS    Manual reviews, approvals, background admin triage
  ─────────────────────── ◄── LINE OF INTERNAL INTERACTION
  5. SUPPORT PROCESSES    Databases, external APIs (ASIC, Stripe), cron workers
```

### 1. Physical Evidence
- Every tangible artifact the user encounters: signup pages, confirmation toasts, invoices, downloadable compliance certificates, SMS codes.

### 2. Customer Actions
- Chronological steps taken by the user from discovery and onboarding through ongoing retention.

### 3. Frontstage (Onstage) Actions
- Activities performed by customer-facing team members or automated frontstage agents that the user directly observes.

### 4. Backstage Actions
- Operational tasks performed by employees or internal workers behind the **Line of Visibility** (e.g. manual identity check approvals, refund sign-offs).

### 5. Support Processes & Infrastructure
- Technical architecture lying behind the **Line of Internal Interaction**: cloud databases, external vendor APIs, asynchronous queues, and automated workers.

---

## Step-by-Step Blueprint Creation Procedure

1. **Scope the Scenario**: Define the exact user journey (e.g., *Client Onboarding & Due Diligence Scan*).
2. **Plot Customer Actions**: Map sequential user steps horizontally across time.
3. **Map Frontstage Touchpoints**: Detail what the user directly sees or interacts with at each step.
4. **Uncover Backstage Workflows**: Identify what staff or automated agents do behind the scenes.
5. **Attach Support Systems**: Link databases, background queues, and third-party APIs powering each action.
6. **Tag Failure (F) and Wait (W) Points**: Mark vulnerable handoffs and latency bottlenecks; design automatic fallbacks.

---

## References & Case Studies

- [Five-Swimlane Architecture & Boundaries](./references/five-swimlane-architecture.md) — Comprehensive explanation of swimlanes, lines of separation, and failure-point tagging.
- [Applied B2B SaaS Service Blueprint (AMLHive)](./references/b2b-saas-service-blueprint.md) — Production blueprint mapping entity registration, live ASIC query execution, and PDF certificate vaulting.
