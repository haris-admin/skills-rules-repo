---
name: vulcan-build-protocol
description: Vulcan's build protocol — TDD, OpenSpec, Codex delegation, evidence-based delivery. Use for any product build or test failure triage.
---

# Vulcan Build Protocol

## Trigger
Any coding task: feature build, bug fix, test failure triage, Codex delegation, pilot implementation.

## Method

1. **Read the handoff first**: `docs/current_progress.md` → `docs/context.md` → `docs/product-brief.md`. Never skip.
2. **TDD loop** (mandatory):
   - RED: write failing test that traces to the requirement
   - GREEN: implement to pass
   - REFACTOR: clean, keep tests green
3. **Never fix tests to accommodate code** — fix the implementation.
4. **Codex delegation** for deep work:
   ```bash
   export PATH="$HOME/.nvm/versions/node/v24.18.0/bin:$PATH"
   cd ~/code/amlhive1
   codex exec --json -m gpt-5.6-luna "task"
   ```
   - `gpt-5.6-*` models → Codex CLI (ChatGPT auth). OpenRouter-style IDs rejected.
   - Verify output; never trust claims without evidence.
5. **Evidence closure**: every task ends with command output, test results, verified file paths.

## Pre-flight rules
- External API params validated BEFORE network calls (Dilisense, Veriff, ABR, Stripe).
- 400/401/403/404/409/422 expected client errors → audit-logged, not Sentry noise.

## Delivery
- 🔴ACTION/🟡DECISION/🟢FYI framing.
- No commits/pushes without explicit approval (dev branch only).

## Pilots (2026)
1. Transaction Evidence Packet — 3 agencies, ~$1k credits, matter-trigger rules + evidence timeline + inspection PDF
2. UBO Evidence API — 2 partners, ~$1–2k, tenant-isolated API + review UI + per-claim citations
3. Fleet Settlement Console — 30 days reconcile, zero credits, historical records only
