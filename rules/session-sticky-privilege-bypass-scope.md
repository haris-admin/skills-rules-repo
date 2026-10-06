# Session-Sticky Privilege Bypass Must Be Scoped And Restored

When a database session stores a privilege bypass (for example a row-level-security platform bypass reason) in session state that a hook re-applies on every new transaction, the bypass is sticky for the whole session, so it must be scoped to the write and the previous state restored in `finally`. Applies to any code that elevates a session's privileges, and to the audit actor used for those actions.

**Scope:** backend services using session-level security context (worked example: AMLHive `set_platform_bypass`, C522/C523, 6 Oct 2026).

---

## Why this exists

AMLHive's `set_platform_bypass(session, reason)` stores the reason in `session.sync_session.info`, and an `after_begin` hook re-applies it on every new transaction. A bypass set for one write therefore stayed active for the rest of the request or worker call, silently widening every later query on that session.

## Core Directives

1. **Scope the bypass to the write.** Read the previous reason from session state, set the bypass immediately before the write, and restore the previous reason (or clear it if there was none) in `finally`, on success and on exception.
2. **Use only pinned reasons.** Bypass reasons come from a reviewed list; a drift-guard test fails on a reason outside it.
3. **Prove the restore and the denial** on the real database engine (not a test double that has no security policy): the reason after the block equals the reason before it on both paths, and a cross-tenant read under the same session fails closed afterwards.
4. **Admin actions are audited as a human actor with the admin identity** (AMLHive: `actor_type=HUMAN` plus `platform_user_id`; a `PLATFORM` actor type is rejected). Platform-scope rows have a NULL tenant column and carry the target tenant in the payload. Never write a NULL or faked actor to dodge this.
5. **Test every outcome path** (success, no-op, failure, denial) for who, what, when and outcome.

---

## Patterns to Follow

```python
prev = session.sync_session.info.get(_KEY)
await set_platform_bypass(session, "pinned_reason")
try:
    await write_audit_and_data(session)
finally:
    restore(session, prev)          # pop the key when prev is None
```

## Patterns to Avoid

```python
await set_platform_bypass(session, "pinned_reason")   # never restored: sticky for the session
await write_audit_and_data(session)
```

---

## Verification & Guardrails

- Integration tests on a real RLS-enforcing Postgres cover restore, denial and the pinned-reason guard.
- Related: `rules/data-retention-and-audit-trail-mandate.md`, `rules/privilege-change-blast-radius-audit.md`, the `postgres-rls-isolation` skill.
