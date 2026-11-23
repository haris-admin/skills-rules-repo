---
name: guarded-go-live-sequence
description: >-
  Take a containerised web product live on shared cloud VMs behind a proxy such as
  Cloudflare: patched images, registry push, edge install, container deploy, verify gates
  with expected counts, and DNS last. The owner runs every production step through guarded
  plan and apply scripts; the agent prepares and verifies. Use when asked to deploy,
  go live, cut over, or sequence a first production release.
---

# Guarded go-live sequence

The agent prepares scripts and checks evidence. The owner runs every production step.

## Order (each step names its own count; never skip ahead)
1. **Patch and scan the images** before anything is pushed (0 critical, highs reported). Pin base images by digest, with the owner confirming each digest.
2. **Zone settings**: strict TLS, Always Use HTTPS on, minimum TLS 1.2; verify read-only in the dashboard and keep screenshots. HSTS stays off until the live checks pass.
3. **Build from the final commit, scan, then push**: one script builds, scans and runs the push plan; the push is a separate apply. Do not let a commit land between the two (the tag comes from the commit).
4. **Edge install** (reload of the live proxy) with the neighbour's health check before and after.
5. **Container deploy**: plan, then apply; confirm the tag in the release file matches the digests the build printed.
6. **Verify the box**, then **the TLS gate** (all hostnames, certificate, refused old TLS). The gate must pass in full.
7. **DNS records last**, one at a time, proxied; count the records before and after; mail and verification records untouched.
8. **Public check, then the full check**; record the result in `docs/history/` and on the ticket.
9. Delete the wrapper scripts only after the next redeploy.

## Rules
- Each step is a guarded script with `plan` and `apply`; read [founder-run steps](../../rules/founder-run-production-steps-are-guarded-scripts-with-plan-and-apply-and-health-checks-before-and-after.md).
- Never read the owner's secret store; see [the secret rule](../../rules/an-agent-does-not-read-a-secret-store-the-owners-script-reads-the-key-inside-the-owners-shell.md).
- Test a new record through a public resolver; see [resolver cache](../../rules/a-local-resolver-caches-not-found-so-test-a-new-dns-record-through-a-public-resolver.md).
- A push or deploy needs the owner's explicit ask and a plain warning that it touches production.
