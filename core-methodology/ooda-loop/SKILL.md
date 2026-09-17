---
name: ooda-loop
description: >-
  Apply John Boyd's OODA loop (Observe, Orient, Decide, Act) to engineering decisions, production incident triage, and agentic workflows. Use when navigating complex or ambiguous technical problems, triaging live outages (SEV-1/SEV-2), resolving multi-agent debate, or breaking out of repeated debugging loops through rapid observation, mental model orientation, hypothesis generation, and closed-loop feedback.
---

# OODA Loop Decision Making Architecture

An operational implementation of John Boyd's **OODA Loop (Observe, Orient, Decide, Act)** for AI agents, software engineers, and incident commanders facing complex, dynamic, or high-stakes environments.

## When to Use

- **Incident Response & Outages**: When production services fail and teams need to rapidly isolate root causes without thrashing.
- **Ambiguous Architecture Decisions**: When evaluating trade-offs between competing designs with incomplete information.
- **Agent Loop Recovery**: When an agentic tool execution fails repeatedly and needs to re-orient its assumptions rather than stubbornly re-running similar failed commands.
- **Adversarial & Competitive Strategy**: When moving faster than competing solutions or market changes by compressing decision cycle tempo.

---

## The Four Stages of the OODA Cycle

```
  ┌───────────┐      ┌───────────┐      ┌───────────┐      ┌───────────┐
  │  OBSERVE  │ ───► │  ORIENT   │ ───► │  DECIDE   │ ───► │    ACT    │
  │  (Signals)│      │(Synthesis)│      │(Hypothesis│      │(Execution)│
  └───────────┘      └───────────┘      └───────────┘      └───────────┘
        ▲                  ▲                  │                  │
        │                  └──────────────────┴──────────────────┘
        │                        Feedback / Calibration          │
        └────────────────────────────────────────────────────────┘
```

### 1. Observe (Collect Empirical Facts)
- Gather raw, unvarnished data from the environment: error logs, system telemetry, git histories, user reports, and tool exit codes.
- Resist the urge to jump to conclusions. Separate what you *know* from what you *infer*.

### 2. Orient (The Cognitive Engine)
- Filter observations through Boyd's five forces: genetic constraints, culture, past experience, new info, and active analysis/synthesis.
- Practice **Destructive Deduction**: Identify assumptions that no longer match reality and dismantle them immediately.
- Formulate an updated mental model before choosing an action.

### 3. Decide (Formulate Falsifiable Hypotheses)
- Frame the decision as a testable hypothesis: *"If we apply change X, observable metric Y will respond within Z seconds."*
- Establish explicit abort triggers and rollback thresholds before executing.

### 4. Act (Execute Surgically & Close the Loop)
- Execute the chosen action with minimal blast radius.
- Every action must produce observable output that feeds directly back into the next **Observe** stage.

---

## Best Practices & Guardrails

1. **Never Skip Orient**: Moving directly from Observation to Action without re-evaluating assumptions causes blind thrashing and compounding incidents.
2. **Compress Cycle Time**: In debugging and incident triage, rapid smaller loops beat slow, massive monolithic interventions.
3. **Beware Confirmation Bias**: Actively seek data that disproves your favorite hypothesis.
4. **Reference Depth**: For in-depth cognitive theory and tactical runbooks, see:
   - [Boyd's Cognitive Model & Five Forces](./references/boyd-cognitive-model.md)
   - [Incident Response & Agent Execution Playbook](./references/agent-and-incident-playbook.md)
