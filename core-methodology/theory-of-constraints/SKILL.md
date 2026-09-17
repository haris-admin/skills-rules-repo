---
name: theory-of-constraints
description: >-
  Apply Dr. Eliyahu Goldratt's Theory of Constraints (TOC) and the Five Focusing Steps to optimize systems throughput, eliminate pipeline bottlenecks, and resolve operational trade-offs. Use when diagnosing delivery bottlenecks in engineering or sales pipelines, subordinating non-bottleneck processes, evaporating conflicting business requirements, or calculating throughput gains from elevating capacity.
---

# Theory of Constraints (TOC) Architecture

An operational and systems-thinking framework formulated by Dr. Eliyahu M. Goldratt in *The Goal* to maximize organizational and software pipeline throughput by focusing relentlessly on the single governing constraint.

## When to Use

- **Software Delivery & CI/CD Bottlenecks**: When code deployment, testing, or review queues stall engineering velocity despite adding more developers.
- **B2B Pipeline & Customer Onboarding Triage**: When customer conversions or compliance reviews back up at a specific manual handoff.
- **Resolving Conflicting Requirements**: When two valid business goals appear irreconcilable (e.g. *speed to ship* vs *99.9% uptime/security*) using the **Evaporating Cloud**.
- **Capital & Resource Allocation**: When deciding where to invest engineering hours or budget to yield maximum measurable throughput increase.

---

## The Core TOC Axiom

> **"An hour saved at a non-bottleneck is a mirage. An hour lost at the bottleneck is an hour lost for the entire system."**

Optimizing any stage other than the governing constraint merely piles up unmanageable Work-in-Progress (WIP) or starves downstream workers.

---

## The Five Focusing Steps

```
  1. IDENTIFY      Find the single stage governing total throughput
  ───────────────
  2. EXPLOIT       Maximize output from the constraint; zero downtime or low-value waste
  ───────────────
  3. SUBORDINATE   Pace all non-bottlenecks to match the constraint's rate; set WIP limits
  ───────────────
  4. ELEVATE       Invest capital, refactor architecture, or add capacity to break constraint
  ───────────────
  5. REPEAT        Identify the new constraint; never succumb to operational inertia
```

### 1. Identify
- Locate the step where inventory/tickets pile up most severely (e.g. manual ASIC reviews, senior developer PR approvals).

### 2. Exploit
- Ensure the constraint never sits idle and never processes defective work (e.g. strict pre-commit test gates, priority review slots).

### 3. Subordinate
- Restrict upstream work-in-progress to match the bottleneck's processing rate. Do not produce features faster than reviewers can verify them.

### 4. Elevate
- If throughput remains insufficient, invest resources: add parallel workers, scale read-replicas, automate manual checks via AI agents.

### 5. Repeat
- Once elevated, the constraint shifts elsewhere. Immediately return to Step 1.

---

## Pipeline Bottleneck Analyzer CLI

Model pipeline stages and simulate throughput gains from elevating constraints:

```bash
# Analyze software delivery pipeline
python3 core-methodology/theory-of-constraints/scripts/toc_bottleneck_analyzer.py --preset software_delivery

# Analyze customer compliance onboarding flow
python3 core-methodology/theory-of-constraints/scripts/toc_bottleneck_analyzer.py --preset compliance_onboarding

# Output JSON for agentic pipelines
python3 core-methodology/theory-of-constraints/scripts/toc_bottleneck_analyzer.py --json
```

---

## References & Thinking Processes

- [The Five Focusing Steps & System Principles](./references/five-focusing-steps.md) — Comprehensive explanation of local optima illusions, WIP controls, and capacity matching.
- [Goldratt's Thinking Processes & The Evaporating Cloud](./references/goldratt-thinking-processes.md) — Conflict resolution diagramming to shatter hidden assumptions and evaporate operational gridlock.
