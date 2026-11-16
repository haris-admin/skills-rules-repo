# Engineering Lifecycle Collection

Use this collection to find the right skill or rule for a piece of software work, from the first vague ask to a verified production release. It is a discovery map only: it routes to existing items and moves or duplicates nothing. The shape (Define, Plan, Build, Verify, Review, Ship) and the standing behaviours below are adapted from `addyosmani/agent-skills` `using-agent-skills` (MIT, (c) 2025 Addy Osmani).

## Quick selection

| If the work is... | Start with | Then use when needed |
| --- | --- | --- |
| An ask that is vague, conventional or missing who, why, success | [Interview Me](../core-methodology/interview-me/SKILL.md) | [Requirements Backlog First](../skills/requirements-backlog-first/SKILL.md) |
| A new requirement, functional or non-functional | [Requirements Backlog First](../skills/requirements-backlog-first/SKILL.md) | [OpenSpec Workflow](../core-methodology/openspec-workflow/SKILL.md) |
| A spec or change to write and verify | [OpenSpec Workflow](../core-methodology/openspec-workflow/SKILL.md) | [Spec Oracle](../core-methodology/spec-oracle/SKILL.md) |
| A ticket about to move to Todo | [Backlog to Todo, Agent Ready](../skills/backlog-to-todo-agent-ready/SKILL.md) | [Writing Plans](../software-development/writing-plans/SKILL.md) |
| No written quality bar, or an agent weakening checks to reach green | [Constraint-Driven Development](../core-methodology/constraint-driven-development/SKILL.md) | [10-Star Quality Gate](../core-methodology/10-star-quality-gate/SKILL.md) |
| Starting or resuming a session, or quality dropping as it grows | [Context Engineering](../core-methodology/context-engineering/SKILL.md) | [CE Handoff](../compound-engineering/ce-handoff/SKILL.md) |
| Implementing logic or fixing a bug | [TDD Mandate](../core-methodology/tdd-mandate/SKILL.md) | [Test-Driven Development](../software-development/test-driven-development/SKILL.md) |
| Designing an API or public interface | [API Design](../skills/api-design/SKILL.md) | [Deprecation and Migration](../software-development/deprecation-and-migration/SKILL.md) |
| A high-stakes or unfamiliar decision mid-build | [Doubt-Driven Development](../core-methodology/doubt-driven-development/SKILL.md) | [Cross-Model Review](../agent-governance-and-git/cross-model-review/SKILL.md) |
| Something broke | [Systematic Debugging](../software-development/systematic-debugging/SKILL.md) | [CE Debug](../compound-engineering/ce-debug/SKILL.md) |
| Reviewing a diff or pull request | [Code Review](../skills/code-review/SKILL.md) | [Adversarial Reviewer](../core-methodology/adversarial-reviewer/SKILL.md) |
| Code that works but is too complex | [Simplify Code](../software-development/simplify-code/SKILL.md) | [Code Review](../skills/code-review/SKILL.md) |
| Security concerns or a pre-release audit | [Security Audit](../skills/security-audit/SKILL.md) | [Secret and Credential Safety](../cloud-and-aws/secret-and-credential-safety/SKILL.md) |
| Committing, branching or tagging | [Git Workflow](../skills/git-workflow/SKILL.md) | [Incremental Version Bumping](../skills/incremental-version-bumping/SKILL.md) |
| Adding logs, metrics, traces or alerts | [Observability and Instrumentation](../observability-and-sentry/observability-and-instrumentation/SKILL.md) | [Sentry Triage](../observability-and-sentry/sentry-triage/SKILL.md) |
| Removing or replacing an old system, or a schema migration | [Deprecation and Migration](../software-development/deprecation-and-migration/SKILL.md) | [Alembic Migration Hygiene](../backend-and-database/alembic-migration-hygiene/SKILL.md) |
| A release to production | [Shipping and Launch](../devops/shipping-and-launch/SKILL.md) | [Tap-Ease Backend Deploy](../skills/tapease-backend-deploy/SKILL.md) for that project |
| Closing a session | [Session Closeout](../skills/session-closeout/SKILL.md) | [Prod Issue Management](../observability-and-sentry/prod-issue-management/SKILL.md) |

## Standing behaviours (apply across every skill)

1. **Surface assumptions.** Before non-trivial work, list the assumptions and let the owner correct them. Label your reading of free or voice text as an interpretation.
2. **Stop when confused.** Name the conflict, show options with a recommendation, ask. Do not guess.
3. **Push back when warranted.** State the concrete downside and an alternative. Accept the owner's decision when they override with full information. Agreeing with a bad idea is a failure.
4. **Enforce simplicity.** Prefer the boring solution. A thousand lines where a hundred suffice is a failure.
5. **Stay in scope.** Touch only what was asked. Report a good find outside scope instead of acting on it (see the subagent authorization boundary rule).
6. **Verify, do not assume.** "Seems right" is not evidence. Read the real exit code and the real output before saying it is done (`rules/release-claims-and-spec-ticks-need-evidence.md`).

## Typical sequence for a feature

Interview Me, Requirements Backlog First, OpenSpec Workflow, Backlog to Todo, Context Engineering, TDD Mandate (tests first, confirmed red), implementation, Doubt-Driven Development on the risky decisions, Code Review, Security Audit, Git Workflow, Shipping and Launch, Session Closeout. Skip steps that do not apply; do not reorder tests after implementation.
