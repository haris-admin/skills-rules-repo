# A setting that lives in a vendor dashboard needs a register row and a live check

A spec can say a feature is removed while a dashboard integration keeps running, because there is no code to delete.

**Scope:** Cloudflare Workers Builds, GitHub apps, DNS owners, any integration configured outside the repository.

---

## Core Directives

1. **Give every dashboard-only task an owner and a register row**: the task id, the exact setting, who may change it, and what breaks if it is changed in the wrong order.
2. **Re-check it live, not from the spec**: a pull request check, a bot comment or the dashboard itself shows what is really connected. A ticked or released spec is a claim.
3. **Do not change the dashboard without the owner's approval**: write the step list, or run an approved browser session.
4. **Order matters for Workers**: records owned by a Worker are read-only, so detach the custom domain before a DNS cutover and before deleting the Worker.

## Why this exists

**8 Nov 2026 (HandleDispute):** spec 59 moved hosting to Docker on EC2, yet T59.01 (disconnect Workers Builds) and T59.07 (delete the Worker) stayed open. A bot reported "Build: Failed" on PR #13, and the owner asked why the Worker still existed.
