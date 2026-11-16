---
name: shipping-and-launch
description: >-
  Prepares and verifies a production launch with a pre-launch checklist, staged rollout thresholds, an error-budget gate and a written rollback plan. Use when preparing to deploy to production, when asked what must be in place before shipping, when planning a canary or percentage rollout behind a feature flag, when defining rollback triggers, or when verifying a release after it went live. Project-specific procedures such as Tap-Ease still take precedence.
---

# Shipping and Launch

Source: adapted from `addyosmani/agent-skills` `shipping-and-launch` (MIT, (c) 2025 Addy Osmani), rewritten for this repo's rules. Faster is safer only when every release is small, reversible and observable; it is never a reason to skip a gate.

**Standing boundaries (all agents):**
- A production push or deploy needs an **explicit ask in the current message and a plain warning** that pushing `main` deploys (`rules/tapease-prod-deploy-boundary.md`). Approval for one release does not extend to the next.
- Run the exact CI gate commands locally first (`rules/ci-gate-commands-run-locally-before-push.md`), read the real exit code, not a background notification.
- Before a fast-forward push, list `git log origin/main..<sha>` and tell the owner what travels with it.
- Prove on staging with live evidence, then production, read-only and by counts, never by printing customer data or secrets.

## Pre-launch checklist

| Area | Confirm |
|---|---|
| Code quality | Full suite green on a fresh scratch database; lint, format, type and contract checks pass; no debug output or TODOs in shipped paths |
| Security | Dependency audit clean at the agreed severity; secrets scan clean; authorization verified on new routes; inputs validated |
| Performance | Budgets met on the real build (see `lighthouse-performance-gate`); no new N+1 or unbounded fetch |
| Accessibility | Keyboard and screen-reader pass on changed screens |
| Infrastructure | Migrations rehearsed on a populated copy with a tested downgrade; config and secrets present in the target environment; backups verified |
| Observability | Alarms, logs and an outside-in probe exist for the new path and can actually fire (`rules/observability-and-error-management.md`) |
| Documentation | Release notes, API docs and runbook updated; held or in-progress work marked "not deployed" |
| Approvals | Owner has approved this release, in this message |

## Feature flags

Ship dark: deploy with the flag off, verify health, then enable in steps. Each flag has an owner and a removal date; clean it up after full rollout. A flag-gated change keeps the legacy path until the flag is retired (`rules/device-flag-gated-behaviour-keeps-legacy-path.md`).

## Staged rollout

```
1 staging         full suite plus smoke test of critical flows
2 production, flag OFF   health check and error monitor clean
3 internal users  flag on for the team, about 24 hours
4 canary 5%       compare against baseline, 24 to 48 hours
5 25% then 50%    same checks at each step, able to step back
6 100%            monitor a week, then remove the flag
```

| Metric | Advance | Hold and investigate | Roll back |
|---|---|---|---|
| Error rate | within 10% of baseline | 10% to 100% above | more than 2x baseline |
| P95 latency | within 20% | 20% to 50% above | more than 50% above |
| Client errors | no new types | new types under 0.1% of sessions | new types over 0.1% |
| Business metric | neutral or better | down under 5% | down over 5% |

Thresholds are defaults with a recorded reason; change them per service in the release plan, not silently. Small projects with no percentage rollout still run steps 1, 2 and a post-deploy read.

## Error-budget gate (where an SLO exists)

Over 20% budget left: ship normally. 0% to 20%: slow rollouts only, no high-risk change. Exhausted: freeze feature work, fix reliability. A canary burning budget faster than baseline is a hold signal.

## Rollback plan (written before the deploy)

```
Trigger conditions: <metrics and thresholds above, data-integrity or security finding>
Steps: <exact commands or flag flips, in order, with absolute paths>
Database: <is the migration reversible? downgrade tested? data written since?>
Time to roll back: <minutes, and who does it>
Verification: <how you will know it worked>
```
Roll back immediately on a 2x error rate, over 50% latency, a spike in user reports, a data-integrity problem or a security issue. Tags are additive: a replaced build gets a new tag, never a moved one (`rules/release-tags-are-additive-never-moved.md`).

## Verify live after the deploy

Three independent reads, not the build log (`rules/deploy-state-needs-independent-reads.md`): the live health version equals the intended full SHA, the served asset or bundle hash changed, and a smoke test against the real host passes. New routes answer as designed (401 or 200). Check error monitoring and logs for new errors over the first hour, then the first day. State plainly what you could not verify.

## Common rationalizations

| Excuse | Reality |
|---|---|
| "It is a small change, skip staging" | Small changes cause outages too. |
| "We will add monitoring after launch" | You cannot tell it broke without it. |
| "The rollback is obvious" | Unwritten rollbacks fail under pressure. |
| "The log says deployed" | A log is not a live read. |
| "Everyone approved earlier" | Approval does not carry to a new release. |

## Red flags

- A push to a deploying branch with no explicit ask.
- No written rollback plan, or a migration with no tested downgrade.
- Status taken from notes or logs rather than a fresh read.
- A flag with no owner or removal date.
- Held work riding along because it was on the integration branch (`rules/isolated-production-release-recipe.md`).
- Alarms that cannot fire.

## Verification

- [ ] The checklist above is complete, or each gap is reported to the owner.
- [ ] A rollback plan is written and its trigger thresholds are stated.
- [ ] Staging was proven, then production checked read-only.
- [ ] Three independent live reads match the intended release.
- [ ] Nothing sensitive was printed; anything not verified is stated.

## See also

`skills/tapease-backend-deploy`, `rules/isolated-production-release-recipe.md`, `rules/github-oidc-immutable-subject-and-free-plan-gate.md`, `skills/session-closeout`, `deprecation-and-migration`.
