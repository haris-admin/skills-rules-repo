# A blind review can reopen an owner choice: record acceptance and a revisit trigger

When an independent review shows that a recorded owner choice creates a Critical risk, put the risk and the options back to the owner. If the owner keeps the choice, record it as accepted risk with the condition that ends the acceptance.

**Scope:** specs where owner answers are binding and a blind adversarial review runs afterwards.

---

## Core Directives

1. **Verify the finding in the code yourself** before reopening anything.
2. **Reopen with the facts**: what the choice exposes, who can use it, what the options cost.
3. **Record the reply verbatim** with the reasoning the owner gave.
4. **Write the revisit trigger into the spec** (for example "when money is processed") and into the security baseline, so the acceptance does not become permanent.
5. **Keep related questions open** (for example whether an owned item may ever be moved) instead of assuming the reply covers them.

## Why this exists

**21 Nov 2026 (HandleDispute):** a review showed that the owner's proof for linking a claim (case number, receipt amount and date) is visible to every business person on the case. The owner kept it, because no money is processed yet, and said to revisit it when payments start. The trigger was written into the customer portal spec and the security baseline.
