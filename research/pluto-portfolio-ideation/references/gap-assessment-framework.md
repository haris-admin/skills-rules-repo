# 88-Point Gap Assessment Framework

A structured scoring methodology for evaluating product readiness across 7 domains. Used in the RegRadar PRD (2026-05-23) to quantify how close an existing pipeline is to being a paid product.

## Scoring System

Each gap scored on a 0-3 scale:

| Score | Label | Meaning |
|-------|-------|---------|
| 0 | 🔴 Critical | Doesn't exist. Blocks launch or creates existential risk. |
| 1 | 🟠 Major | Exists in primitive form. Needs significant work. |
| 2 | 🟡 Minor | Working but incomplete. Polish or edge cases missing. |
| 3 | 🟢 Done | Production-grade. Works reliably. |

Then: subtotals per domain, grand total, and percentage. The percentage is deliberately **not** the story — the *distribution* of scores across domains is.

## The 7 Domains

### 1. Research Pipeline (15 items)
Quality, coverage, sourcing, dedup, personalization, failure recovery.

### 2. Knowledge Storage (12 items)
Vector DB health, search relevance, multi-tenancy, backup, migration path.

### 3. Voice/Media Pipeline (10 items)
Audio quality, personalization, delivery formats, failure handling.

### 4. Subscriber & Business (18 items)
Payments, auth, portal, email, onboarding, compliance, support, analytics.

### 5. Web UI / Delivery (12 items)
Search portal, reading experience, mobile, email templates, API docs, accessibility.

### 6. Marketing & GTM (12 items)
Landing page, samples, personas, competitor analysis, pricing validation, launch plan.

### 7. Operations & DevOps (9 items)
Hosting, monitoring, CI/CD, DR, security, scalability.

## How to Apply

1. List every sub-item under each domain
2. Score honestly — don't round up
3. Calculate subtotals and percentages
4. Read the *distribution*, not just the total

## The Key Pattern

The most revealing pattern: **a high score in Research/Pipeline with near-zero in Business/UI/GTM means the hard part is done and the easy part is weekend work.** This is the ideal "productize existing infrastructure" signal.

The inverse pattern (high Business/UI scores but low Research scores) means you're building a wrapper around nothing — much harder to fix.

## Example: RegRadar (2026-05-23)

| Domain | Score | Max | % |
|--------|-------|-----|---|
| Research Pipeline | 30 | 45 | 67% |
| Knowledge Storage | 20 | 36 | 56% |
| Voice Pipeline | 17 | 30 | 57% |
| Subscriber & Business | 2 | 54 | 4% |
| Web UI / Delivery | 0 | 36 | 0% |
| Marketing & GTM | 6 | 36 | 17% |
| Operations & DevOps | 6 | 27 | 22% |
| **TOTAL** | **81** | **264** | **31%** |

Interpretation: Core intelligence engine is 56-67% ready. Customer-facing layers are 0-22% ready. The 31% we have is the 80/20 — the hard differentiator. The remaining 69% is plumbing that every SaaS boilerplate solves.
