# The Five Focusing Steps of Theory of Constraints (TOC)

Formulated by Dr. Eliyahu M. Goldratt in *The Goal*, the Theory of Constraints asserts that any manageable system is limited in achieving higher throughput by a very small number of constraints—often only **one single bottleneck** at any given time.

---

## 1. The Core Principle: Local Optima vs System Throughput

- **The Golden Rule**: An hour saved at a non-bottleneck is an illusion. An hour lost at the bottleneck is an hour lost for the entire system.
- Optimizing any stage upstream or downstream of the constraint only creates unmanageable Work-in-Progress (WIP) pileups or idle worker starvation.

---

## 2. The Five Focusing Steps

```
┌────────────────────────────────────────────────────────┐
│  STEP 1: IDENTIFY THE CONSTRAINT                       │
│  Find the single stage governing total throughput      │
└───────────────────────────┬────────────────────────────┘
                            │
                            ▼
┌────────────────────────────────────────────────────────┐
│  STEP 2: EXPLOIT THE CONSTRAINT                        │
│  Maximize output from the bottleneck with zero downtime │
└───────────────────────────┬────────────────────────────┘
                            │
                            ▼
┌────────────────────────────────────────────────────────┐
│  STEP 3: SUBORDINATE EVERYTHING ELSE                   │
│  Pace all non-bottlenecks to match the constraint's rate│
└───────────────────────────┬────────────────────────────┘
                            │
                            ▼
┌────────────────────────────────────────────────────────┐
│  STEP 4: ELEVATE THE CONSTRAINT                        │
│  Invest capital, refactor architecture, or add capacity│
└───────────────────────────┬────────────────────────────┘
                            │
                            ▼
┌────────────────────────────────────────────────────────┐
│  STEP 5: REPEAT (PREVENT INERTIA)                      │
│  Identify the new constraint; never let inertia win    │
└────────────────────────────────────────────────────────┘
```

### Step 1: Identify the Constraint
- Locate the step where work piles up most severely.
- In software development: Code review queues, QA approval gates, database migration lock contention, third-party API rate limits, or sales executive demo availability.

### Step 2: Exploit the Constraint
- Squeeze maximum possible efficiency out of the constraint without spending new capital:
  - Eliminate low-value work reaching the bottleneck (e.g. run automated lint/test suites so code reviewers never spend time on syntax formatting).
  - Ensure the bottleneck never sits idle (e.g. priority review slots, dedicated worker threads).

### Step 3: Subordinate Everything Else to the Constraint
- Align the entire system pace to match the constraint:
  - Restrict upstream work-in-progress (WIP limits) to prevent overwhelming the bottleneck.
  - Do not produce features faster than code reviewers and QA can verify them.

### Step 4: Elevate the Constraint
- If throughput is still insufficient after Steps 2 and 3, invest resources to expand capacity:
  - Add parallel worker pods or read-replicas; hire senior reviewers; upgrade upstream API plan.

### Step 5: Repeat (Watch Out for Inertia)
- Once elevated, the constraint will break and shift to another part of the system (e.g., from Backend Review to Sales Onboarding).
- Return immediately to Step 1.
