# No Hardcoding: Configurable or Admin-Managed by Default

Values a person might later need to change, review or audit are never written as literals in code or tests. They live in an admin-managed store, in configuration with a documented default, or are derived from the source of truth. A hardcode needs a very good, recorded reason.

<!-- IMPORTANT: Do NOT include YAML frontmatter (---) in rules/*.md. Rules must begin with an H1 title on line 1. -->

**Scope:** All agents, all repositories. Widens `rules/no-hardcoded-current-state-literals.md` (checks that write down today's value) to every changeable value in application code, configuration and tests.

---

## Core Directives

1. **Default is not to hardcode.** Place a changeable value, in order of preference: (a) an admin portal backed by a versioned, audited store (thresholds, limits, timings, feature flags, entitlements, provider routing, rosters); (b) configuration resolved from the environment or secret store with a documented default and a startup check; (c) derived from the source of truth (registry, enum, migration chain, route table, settings object). Inside a test, only (c) is acceptable.
2. **A hardcode needs a very good reason, recorded where the code lives** (one comment or a design clause naming the reason and the owner). Accepted reasons: a statutory or compliance-immutable value; a security invariant that must not change at runtime; frozen history such as a database migration; a mathematical or format constant that cannot sensibly vary. "It was quicker" and "nobody has asked to change it yet" are not reasons.
3. **Tests never pin rosters, counts, names or positional indexes of things that grow.** Derive the expectation from the registry under test, or pick a representative by property (the first minute-only job), not by name or position. A test that must name an item cites the requirement that makes it fixed.
4. **If a value belongs in the admin portal and no surface exists, do not hardcode and move on.** Raise the gap in the plan, ship the value as configuration with a documented default, and propose the setting and the page.
5. **Changing an existing hardcode follows the requirement chain.** A test changes only with a recorded requirement change confirmed by the human. The rule is not retroactive across a repository: do not leave new literals because old ones exist, and do not refactor all old ones without a scoped task.

---

## Patterns to Follow

- Parse the registrations (or read the settings object) and assert the built roster equals them, with a non-empty floor so the check cannot pass vacuously.
- A release unit that deliberately omits an item must pass its own tests. Run the unit's tests on the reduced roster before shipping it.
- Record the reason next to any accepted hardcode.

## Patterns to Avoid

- `len(Enum) == 261`, a fixed list of 20 scheduled-job names, `jobs[16]`, an `"AEST"` string asserted against "now".
- A test that fails the moment an unrelated item is added or held.
- Moving a hardcoded number into a constant file and calling it configurable.

---

## Verification & Guardrails

- Before closing a change, search the diff for literals that look like thresholds, timings, limits, names of registered things and counts, and for `len(...) ==`, `EXPECTED_*`, name sets and positional indexes in new tests. State each as configuration, admin-managed, derived, or an accepted reason with its recorded comment.
- Limit: a derived roster cannot catch a deliberate reclassification in source (for example an hour added to a minute-only job). Pin per-job schedules in that job's own requirement, not in a roster test.
- Related: `rules/no-hardcoded-current-state-literals.md`, `rules/openspec-tdd-mandate.md`, `rules/red-for-the-right-reason.md`.
- Origin: 6 Oct 2026, a scheduler change whose contract tests pinned 20 job names and a second roster including a held job, blocking an isolated release unit; the owner approved the revisions and asked for this wider rule.
