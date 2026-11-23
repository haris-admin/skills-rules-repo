# A founder-run production step is a guarded script with plan and apply modes, and health checks before and after

When the owner, not the agent, applies a production change, the agent ships a small script that proves the change is safe before it runs and proves nothing else broke after.

**Scope:** any production step the owner runs: registry push, edge or proxy install, container deploy, DNS or zone settings, secret setting.

---

## Core Directives

1. **Two modes.** `plan` is read-only and prints current versus required; `apply` changes only what differs and re-reads each value. A missing input fails visibly and changes nothing.
2. **Check the neighbours.** Run the other tenant's health check before and after (it must pass the same count both times), and refuse to run if the repository holds uncommitted changes.
3. **A short wrapper.** Give the owner `! ~/name.sh plan` and `! ~/name.sh apply` (a short path calling the real script by absolute path), name the next step at the end, and tell them to delete the wrapper when done.
4. **Say what is production.** The message before `apply` states what it touches, whether it reloads something live, and the exact rollback.
5. **Test it without the network.** Put stub `aws` and `curl` on `PATH`, prove `plan` makes no change and `apply` changes only the differing items, and prove a missing token fails visibly and never appears in a command line.

## Why this exists

**23 Nov 2026 (SonoVantage go-live):** eleven founder steps (Cloudflare settings, image push, edge install, container deploy, four verify gates) ran one after another on a shared production VM next to another product. Each guarded script printed a count (7, 21, 54, 40, 61) that the owner pasted back, and ChargeRail stayed at 7 of 7 before and after every step. Related: [handoff commands as short script files](./handoff-commands-as-short-script-files.md).
