---
name: deprecation-and-migration
description: >-
  Plans the safe removal or replacement of old systems, APIs, features and schemas, including zero-downtime expand and contract database changes. Use when removing or sunsetting code or an endpoint, migrating consumers from one implementation to another, deciding whether to maintain or retire something, handling code nobody owns, renaming or dropping a column in production, or planning a strangler, adapter or feature-flag migration.
---

# Deprecation and Migration

Source: adapted from `addyosmani/agent-skills` `deprecation-and-migration` (MIT, (c) 2025 Addy Osmani), rewritten for this repo's rules.

Code is a liability: every line costs tests, patches, upgrades and attention. Its value is the function it provides. When the function is no longer needed or a better path exists, removal is a feature. With enough users, though, every observable behaviour is depended on (Hyrum's Law), so removal needs active migration, not an announcement.

## Decide first

1. Does it still give unique value? If yes, maintain it.
2. Who and what depends on it? **Measure** from logs, metrics and a repo search; do not guess.
3. Does a replacement exist and cover every critical use? If not, build it first. Never deprecate with no alternative.
4. What does migration cost each consumer, and can you automate it?
5. What does keeping it cost (security risk, engineer time, complexity)?

Plan the exit at design time: ask how you would remove this in three years.

## Advisory or compulsory

| Type | Use when | Mechanism |
|---|---|---|
| Advisory | Old system is stable, migration optional | Warnings, docs, nudges |
| Compulsory | Security risk, blocks progress, or cost is unsustainable | Hard date, migration tooling, support |

Default to advisory. Compulsory needs tooling, a guide and support; a bare deadline is not a plan. Advisory that has run for years with no progress is a red flag.

## Migration process

1. **Build the replacement** and prove it in production.
2. **Announce** with what is deprecated, why, the replacement, the date, and a worked migration guide.
3. **Migrate incrementally**, consumer by consumer, most critical or simplest first; if the owner of the old system must carry the cost, do the migration for them. Track progress by measured traffic to the old path.
4. **Remove** only after metrics show zero active consumers. Delete the code, tests, docs, config and deprecation notices. Run the deletion precheck for untracked and referenced files (`rules/deletion-precheck-untracked-and-referenced.md`). Remove nothing the owner has not approved.

Freeze new features on the deprecated system; invest in the replacement.

## Migration patterns

- **Strangler:** route a growing slice of traffic to the new system behind a flag or router while the old one shrinks, until it carries none.
- **Adapter:** put the old interface in front of the new implementation so consumers migrate on their own schedule, then retire the adapter.
- **Feature flag:** switch per consumer or percentage, with a one-step rollback and a recorded removal date for the flag.
- **Expand and contract (database):** see below.

## Database schema: expand, backfill, contract

Old and new application versions run together during a deploy, so a schema must be valid for both at every step.

1. **Expand:** add the new column, table or index (additive, nullable or defaulted). Ship.
2. **Dual write or read** in code; **backfill** in throttled batches that do not lock the table. Ship.
3. **Cut over** reads to the new shape. Ship.
4. **Contract:** drop the old column or table in its **own deploy**, after nothing references it.

Never rename or drop in place. Never couple a safe add with a destructive drop in one migration. Every migration has a tested downgrade; rehearse downgrade and upgrade on a populated copy before production. Details: `alembic-migration-hygiene`, `rules/alembic-archive-tables-keep-foreign-keys-rehearse-downgrade.md`, `rules/concurrent-index-migrations-need-a-quiet-window-and-a-repair-runbook.md`, `rules/database-major-upgrade-rehearse-then-cutover.md`.

A dependency major upgrade ships alone (`rules/dependency-major-upgrades-ship-alone.md`).

## Zombie code

Code nobody owns but everyone depends on: no commits for six months with live consumers, no maintainer, failing tests nobody fixes, known vulnerable dependencies. It gets an owner and real maintenance, or a deprecation with a concrete plan. It does not stay in limbo.

## Common rationalizations

| Excuse | Reality |
|---|---|
| "It still works, why remove it?" | Unmaintained code accrues security debt silently. |
| "Someone might need it later" | Rebuilding is cheaper than carrying it. |
| "Users will migrate on their own" | They will not. Provide tooling or do it for them. |
| "We can run both forever" | Double the maintenance, tests and onboarding. |
| "Just rename the column" | During rollout one side queries a column that is gone. |
| "I will write the rollback if we need it" | A migration with no tested down path cannot be reversed. |

## Red flags

- Deprecating with no replacement, no guide, or no usage measurement.
- New features added to a deprecated system.
- Removal without proof of zero consumers.
- A schema change and the code that depends on it in the same deploy.
- A column renamed or dropped in place.
- A migration with no tested downgrade, or a backfill that locks the table.
- Zombie code with live consumers and no owner.

## Verification

After a deprecation:
- [ ] The replacement is proven and covers all critical uses.
- [ ] A migration guide with concrete steps exists.
- [ ] Metrics or logs show zero active consumers on the old path.
- [ ] Old code, tests, docs, config and notices are removed, with the owner's approval.

After a schema migration:
- [ ] It shipped in additive phases (expand, backfill, contract).
- [ ] Both code versions were valid against the schema at every step.
- [ ] The downgrade was tested on a populated copy and the backfill was batched.
- [ ] The destructive step shipped in its own deploy.

## See also

`api-design` (Hyrum's Law, addition over modification), `rules/api-contract-frozen-unless-approved.md`, `rules/isolated-production-release-recipe.md`.
