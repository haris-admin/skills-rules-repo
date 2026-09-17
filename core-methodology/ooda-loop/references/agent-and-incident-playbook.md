# OODA Loop Incident Response & Agent Execution Playbook

This playbook translates Boyd's OODA framework into tactical engineering procedures for live production incidents (SEV-1/SEV-2), multi-agent debate, and stubborn debugging loops.

---

## 1. Live Incident Triage (SEV-1 / SEV-2)

When an outage hits, teams often freeze or thrash because they skip **Orient** and rush from panicked **Observation** into chaotic **Action**.

### Cycle Protocol:
1. **Observe (Empirical Ground Truth)**:
   - What are the cold facts? (HTTP status codes, latency spikes, DB connection pools, Sentry error rates).
   - What changed in the last 60 minutes? (Git commits, config changes, cloud provider health, DNS propagation).
   - *Rule: Do not hypothesize yet. Collect pure signals without interpretation.*

2. **Orient (Shatter Hypotheses & Mitigate Bias)**:
   - Identify prevailing assumptions: *"The database is down."* Verify: Can we connect via psql directly? If yes, shatter the assumption.
   - Separate symptoms from root causes: 504 Gateway Timeout is a symptom; exhausted worker threads is the orientation.
   - Run **Destructive Deduction**: What evidence contradicts our favorite explanation?

3. **Decide (Falsifiable Hypotheses & Rollback Gates)**:
   - Formulate a testable action: *"Rollback migration 49b and restart worker pods."*
   - Define expected outcome: *"Error rates should drop below 1% within 120 seconds."*
   - Define abort trigger: *"If error rate remains elevated at T+120s, revert and isolate traffic."*

4. **Act (Fast, Surgical, Observable Execution)**:
   - Execute the single planned intervention.
   - Avoid making three changes at once (compounds ambiguity).
   - Immediately loop back to **Observe**.

---

## 2. Agentic Problem Solving Loop

Autonomous AI agents frequently get stuck in repetitive failure loops when an action fails. The OODA protocol breaks this cycle:

```
[Tool Output / Error Trace]
            │
            ▼
        OBSERVE: Read exact stdout/stderr, exit code, diff state
            │
            ▼
        ORIENT: What assumption in the prompt or plan proved false?
                • Did the file structure differ from expectations?
                • Did a dependency update change the API surface?
                • Why did the previous tool call fail?
            │
            ▼
        DECIDE: Select a distinct strategy (not the same failed call)
            │
            ▼
        ACT: Execute next tool call with new parameters
```

### The Anti-Thrashing Guardrail
If an agent executes **Act $\rightarrow$ Observe $\rightarrow$ Act** twice with the exact same error:
1. **HALT**: Stop issuing the same tool call or variant.
2. **FORCE ORIENTATION**: Step back and inspect the root assumptions. Read the documentation, inspect filesystem state, or check git diffs before attempting any further edits.
