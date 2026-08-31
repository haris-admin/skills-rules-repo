# Data retention + audit trail — HARD RULE for every check-in (all agents)

> **CORE RULE OF THE SYSTEM.** Every activity — user or system, success or denial (including
> 401/404) — must leave a durable audit row. Sentry noise filters never skip audit. Full text of
> this mandate wins on drift; short always-apply card:
> `.cursor/rules/core-audit-trail-completeness.mdc` · `.agents/rules/core-audit-trail-completeness.md`

**This is a blocking rule, not guidance.** It applies to **every** code change checked in, on every
agent surface — Claude Code, Codex, Cursor, Gemini/Antigravity. A change that adds or modifies a
state-changing path and does not satisfy this rule is **not ready to commit**, regardless of whether
tests pass.

Human decision, 1 Aug 2026, verbatim:

> *"Add these rules for every code that we are checking in. We need to follow these rules. This
> should be a hard rule: 7-year data retention has to be there. Every action that is done, taken by
> any of the users, as well as any action that is taken by the system, should be logged and tracked.
> Audit trail has to be there. The record has to be made for every change that is done, who did
> what, and when. All this information has to be tracked."*

And on boundary calls, same day:

> *"we need to be a bit more conservative about deciding 7-year rules, so if there is any decision
> which is around the boundary, assume that that is actually in the 7-year rule. We want to keep it
> for 7 years, but these kinds of very clear-cut entries, that's fine. We can actually leave it
> out."*

Reaffirmed and tightened, same day:

> *"In case of any ambiguity, we will be keeping a record for seven years. We can't take a risk."*

**Reaffirmed again, 1 Aug 2026 (soft-lock / Sentry confusion + 401/404):**

> *"Add a rule that should be across the board: every activity which happens in the system should be
> logged in the audit. That rule has been broken, and nothing can break this rule. This less than
> 500 is the noise. Everything is not applicable [to] the audit log itself. The audit log should
> contain everything which is happening in the system by users or by anyone, any of the system
> activities as well."*

And (same day) on Sentry vs audit and 401/404:

> Audit cannot be skipped even for 401 or 404; repeated attempts must be audited. Sentry may group
> noisier codes (400/401/404) for signal, but that does not replace the audit trail.

**Read that as an instruction, not a preference. Ambiguity is not a judgement call to be resolved by
the agent — ambiguity resolves to RETAIN, every time.** If you find yourself constructing an
argument for why something probably doesn't need retaining, you have already established that it is
ambiguous, and the answer is retain. Do not weigh storage cost, tidiness, or elegance against this.

---

## CRITICAL SEPARATION — Sentry noise ≠ audit trail

**Never apply Sentry / ops “noise” filters to `audit_entries`.**

| Surface | Purpose | May drop expected UX / &lt;500? |
|---------|---------|----------------------------------|
| **In-app Audit Trail (`audit_entries`)** | Who did what, when, outcome — including **denied / blocked / failed** attempts | **NO** for logged-in Principal/Agent/Auditor/admin (or Bearer session): **any HTTP ≥400** must leave a durable row (`FAILED` / `BLOCKED`). Anonymous bot noise may still be recorded for 401/404/409. |
| **Sentry (and similar ops alerts)** | Ops visibility into what went wrong for **logged-in** sessions | Authenticated ≥400 → **report** (warning). Fingerprints/grouping OK. Never a substitute for audit. |

Concrete failure that broke the rule (1 Aug 2026): `assert_agency_not_soft_locked` returned HTTP **402** and wrote **no** `audit_entries` row. Screening/KYC attempts therefore looked like “nothing happened” on the agency Audit page, while users were actively blocked. Issue-197 (drop “Set up payment…” from Sentry) must **never** be read as permission to skip the audit write. (Separately: issue-197’s browser drop was **reversed** in C368 so logged-in 402s reach Sentry for ops.)

### Implementation map (shipped C367 / C368 — v0.5.71)

| Concern | Where |
|---------|--------|
| Soft-lock 402 audit before raise | `assert_agency_not_soft_locked` + `mark_denial_audited` |
| ABR 403 audit before raise | `assert_agency_abr_verified` |
| Authenticated any ≥400 catch-all + 401/404/409 | `app/services/audit_http_denial.py` + global `HTTPException` handler in `app/main.py` |
| Avoid double audit when gate already wrote | `request.state.audit_denial_recorded` / `mark_denial_audited` |
| Stash identity for handler | `get_current_user` → `request.state.user_id` / `agency_id` |
| Unit tests needing `Request` | `make_test_request()` — FastAPI rejects `Request \| None` on dependencies |
| FE companion (logged-in 4xx → Sentry warning) | `frontend/lib/api.ts` `captureApiError` |
| New action types | migration `a160`; FE labels in `auditTrailDisplay.ts` |
| New mutating routes/workers | register in `backend/audit_contracts.json` (C314 guard) |
### Required pattern for dependency / gate denials

Any guard that raises `HTTPException` (**401 / 402 / 403 / 404 / 409** / etc.) **after** the user
(or system) attempted a compliance or mutating action MUST:

1. `write_entry(...)` with a clear `action_type` and `outcome` of `BLOCKED` / `DENIED` / `FAILED`
   (as appropriate),
2. `await db.commit()` so the row survives the raised exception’s request teardown,
3. **then** raise.

Canonical precedents:
- `require_training_gate` → `TRAINING_GATE_BLOCKED`
- C367 `assert_agency_not_soft_locked` → `BETA_SUNSET_SOFT_LOCKED` / `BLOCKED`

**Forbidden:** raise-and-exit with no audit row because “the mutation didn’t happen”, “it’s only a
4xx”, or “401/404 are noise.” A blocked or not-found attempt **is** an activity; repeated attempts
must leave durable audit evidence (per attempt or an explicit roll-up entry — never silence).

---

## The four hard requirements

Every check-in that touches a state-changing path MUST satisfy all four:

1. **7-year retention.** The record is retained 7 years, soft-delete only, no TTL, no purge.
2. **Every action logged — user *and* system.** Not just human actions. Cron jobs, workers,
   webhooks, AI extractions and maintenance scripts are actors too.
3. **An audit trail entry exists**, append-only and immutable.
4. **Who, what, when** — actor, action, target, timestamp, and outcome are all recorded.

## This is not new machinery — use what exists

`openspec/specs/audit-trail/spec.md` is canonical. It already defines:

```
user_id:         UUID | NULL          (authenticated human actor only)
actor_type:      HUMAN | SYSTEM | AI | EXTERNAL | MAINTENANCE
actor_reference: TEXT                 (stable, PII-safe source code)
action_type:     ENUM
outcome:         ...
```

`actor_type` is exactly the "users **as well as** the system" requirement — `SYSTEM`, `AI`,
`EXTERNAL` and `MAINTENANCE` exist so that a cron, a worker, a Bedrock extraction or a webhook is
never an unattributed change. **Never write an audit entry with a missing or faked actor.** If you
cannot determine the actor, that is a design gap to raise, not a `NULL` to shrug at.

**A known identity stashed only in free-text is the same defect as a missing one** (added 22 Aug
2026, C426). `openspec/changes/425-ubo-evidence-api-pilot`'s evidence-pack readiness audit found
`ownership_review_service.py::yourapp_approve()` had a real, already-resolved `staff_user.id` in
hand and chose to write `user_id=None` on the audit row anyway, with the real ID embedded only in
`notes` (`"yourapp_reviewed_by:{uuid}"`) — a structurally identical failure to a KYB reviewer's
identity landing only in `audit_entries.notes` with nothing on the domain row either. Requirement 4
("who") means a **structured, queryable field** — a column, not a substring inside `notes` a
future export or evidence pack would have to regex out. If the actor's real identity doesn't fit
the existing `user_id`/`actor_type`/`actor_reference` shape (e.g. a platform-staff identity that
isn't a tenant `users` row), add a new structured column for it — following the same pattern
`partner_id` (C425) and `platform_user_id` (C426) already established — rather than falling back to
free text. See `docs/agent_rules/claude-code-spec-only-cursor-implements.md` for who executes that
kind of fix once it's found.

**A `write_entry(...)` call that raises is a bigger trap than a missing call (found 24 Aug 2026,
issue-273/275/276 — three real production instances in one day).** A `SYSTEM`/`MAINTENANCE`-actor
audit write (`agency_id=None`) is itself RLS-protected — it only passes `tenant_isolation_00e` via
`set_platform_bypass()`, and that bypass is scoped to whatever set it: a standalone script's own
session, a request's per-request context, one ARQ worker call. A maintenance script, Alembic
migration, or ARQ worker's finalization step that writes this kind of entry from a session where
that bypass isn't active **crashes instead of silently skipping** — which sounds safer than a
missing-audit-entry bug, but in practice took down an entire operation (a stuck ACR backfill run
that could never durably record its own failure, polling forever) rather than just losing one
audit row. Test coverage for this class of code needs `.claude/skills/rls-test-postgres/`'s real
non-superuser Postgres, not SQLite (no RLS concept) or the shared `db` fixture alone (its own
`"test_fixture_seed"` bypass masks a missing `set_platform_bypass()` call in the code under test —
clear it first with `clear_tenant_context(db)`). Full pattern:
`.claude/skills/rls-test-postgres/SKILL.md`'s "Testing NULL-agency / system-actor writes" section.

The spec's own words: *"immutable, append-only log of every compliance action… cannot be edited or
deleted under any circumstances… must remain queryable for 7 years after each entry is created."*
Enforced by a DB trigger (`kyc-verification/spec.md:602`).

**Enforcement mechanism:** `backend/app/services/audit_contract_enforcement.py` plus the
machine-readable audit contract registry (C314). **C314 AC-07 is the check-in gate** — *"CI fails
for unregistered mutating entry points, untested registry rows"*. Register your mutating entry point
there; do not build a parallel logging path.

> **Status caveat, 1 Aug 2026:** C314 is `status: partial`. The discovery registry is structurally
> 203/203 Green, but semantic per-mutation contracts (T314.06–T314.15, T314.18) and production
> enforcement (`AUDIT_CONTRACT_ENFORCEMENT_ENABLED`, pending ops sign-off) are outstanding. **Until
> CI enforces this, the rule is outstanding — enforced by you.** A green build is not evidence of
> compliance yet.

**Mechanics of registering a new mutating entry point (worked example: C397, 8 Aug 2026).**
`tests/audit/test_audit_contract_guards.py::test_t314_02_every_discovered_mutation_has_a_contract`
AST-scans every `@router.post/put/patch/delete` handler under `app/api/` (plus every ARQ
worker registered in `app/workers/__init__.py`) and fails if its `path::function_name::METHOD`
key isn't present in `backend/audit_contracts.json`. Adding a new mutating route:

1. Run the guard test **first** — it names the exact missing `entrypoint` string to add
   (`app/api/internal/sync.py::trigger_daily_batch_sync::POST` in C397's case). Don't guess the
   key format by hand.
2. Add one object to `audit_contracts.json`'s `contracts` array: `id` (a short `C<nnn>_..._<METHOD>`
   slug), the exact `entrypoint` string from the test failure, `lane` (`agency`/`platform` — match
   a sibling route in the same file if one exists), `actor_type` (one of `HUMAN|SYSTEM|AI|EXTERNAL|
   MAINTENANCE`), `target`, `in_scope: true`, `action_type` (an existing `AuditActionType` — check
   for a fitting one, e.g. the generic `ALERT_SENT`, before adding a new PG enum value; a new enum
   value needs its own migration and is a bigger lift than the registry entry itself), and `test`
   (the guard test's own path — copy a neighboring row).
3. Re-run the guard test to confirm green. This does **not** replace writing the actual
   `write_entry(...)` call in the endpoint — the registry entry declares the obligation, the code
   satisfies it; the guard only proves the two haven't drifted apart.

**FastAPI route-registration-order gotcha, same example:** a new static path (`/sync/daily-batch`)
registered *after* an existing path-param route (`/sync/{dataset}`) in the same router gets
silently swallowed by it (matched as `dataset="daily-batch"`, then 422s on the literal-type check).
Register more-specific/static routes before path-param routes that could shadow them.

## Retention: 7 years is the default, exclusion carries the burden of proof

**When it is not obvious whether something falls under the 7-year obligation, assume it does.**

The burden runs one way: **you must be able to say clearly why something is *excluded*.** "I
couldn't find an obligation" is not an exclusion argument — it is precisely the boundary case that
must be retained. Over-retaining costs storage; under-retaining is a regulatory failure that cannot
be repaired afterwards, because the data is gone.

| Obligation | Scope | Source |
|---|---|---|
| **s.111 AML/CTF Act 2006** | CDD records — 7 years **after the business relationship ends** | `kyc-verification/spec.md:599` |
| **s.116 AML/CTF Act 2006** | Records retained 7 years (cited on training certificates) | `staff-training/spec.md:241` |
| **AML/CTF Rule 15.4** | Staff training records — 7 years | `staff-training/spec.md:425` |
| Program-wide | "All compliance data retained 7 years" | `agency-settings/spec.md:103` |
| DB-level | *"no purges, no TTL on compliance tables"* | `docs/context.md` Critical Callout #10 |

s.111 runs from the **end of the business relationship**, not from row creation — a retention clock
starting at insert is wrong.

### Required patterns — follow, don't reinvent

- **Soft delete only:** `is_archived BOOLEAN (default false)` (`kyc-verification/spec.md:220`,
  `cdd-checklists/spec.md:476`). **Never hard-delete.**
- **Append-only enums:** never remove or repurpose a value; add new ones
  (`kyc-verification/spec.md:844`).
- **Append-only audit:** `audit_entries` may never be modified or deleted.
- **No TTL on compliance tables**, ever.
- **Failed and rejected attempts are retained too** — `FAILED` and `REFER` KYC attempts are
  explicitly in scope (`kyc-verification/spec.md:598`). A negative outcome is still a record of what
  you did.

## The narrow exclusion — transient credentials and infrastructure state

Exclusion requires **both** halves to hold: the data is a transient credential or infrastructure
state carrying no record of a decision, **and** its durable counterpart is captured elsewhere.

**Worked example — signup SMS OTP (C42), assessed 1 Aug 2026: correctly excluded.**

- Redis only, never Postgres (`backend/app/services/signup_otp_service.py`).
- `CODE_TTL = 300`, `COOLDOWN_TTL = 60`, `SEND_COUNT_TTL = 3600`, `VERIFIED_TTL = 900` — longest
  artifact one hour.
- Stored as an **HMAC-SHA256 hash** keyed by `SECRET_KEY`, never plaintext. Writes no audit rows.
- It authenticates a person creating an **YourApp SaaS account**. YourApp is the software provider;
  the designated services, and therefore the CDD obligations, sit with the real estate agencies who
  are its customers. An OTP proving control of a phone number is an authentication credential, not a
  customer identification record.
- **The durable fact is retained separately:** `USER_JOINED` in `backend/app/models/audit_entry.py`
  records who joined and when, in `audit_entries`, under the 7-year regime.

Same reasoning covers session tokens, CSRF tokens, rate-limit counters, idempotency keys, and
read-through caches (`directory_list_cache`, `notification_cache`).

**Do not "play it safe" by moving an excluded item into a retained table.** Putting a
phone-verification secret under a 7-year no-delete policy is worse for both security and privacy.
The correct architecture is: **ephemeral credential in Redis, durable event in Postgres.**

## Decision procedure

**Ambiguity resolves to RETAIN. There is no third outcome.**

1. Does it record a decision, event, identity assertion, customer interaction, or compliance
   outcome? → **Retain, and write an audit entry.** Stop.
2. Is it a transient credential or infrastructure state, **and** is the durable fact captured in
   `audit_entries` or an equivalent retained table? → May be excluded. **Name the durable
   counterpart in the change's `design.md`** — an exclusion with no named counterpart is not
   clear-cut, so it is retained.
3. Anything else — including "I'm not sure", "probably not", "it's only a…", or any argument you
   had to construct → **Retain.** Raise it with the human; do not decide it silently and do not
   treat your own reasoning as sufficient to exclude.

### The two questions are different — do not merge them

The conservative default answers *"is this a **compliance record**?"* — and there, **any doubt means
retain**.

It does **not** answer *"is this a record at all?"* A session token, an OTP hash, a CSRF token or a
rate-limit counter is not an ambiguous compliance record — it is **categorically not a record**,
being a secret or a counter with no informational content about what anyone did. Those are excluded
by kind, not by judgement, which is why the human's own framing allowed it: *"these kinds of very
clear-cut entries, that's fine. We can actually leave it out."*

**Retaining a credential for 7 years is not the safe option — it is a security and privacy
regression.** The conservative rule increases what you *keep a record of*; it must never increase
how long you keep a *secret*. If you are unsure which of the two questions you are answering, that
is itself ambiguity → retain the **record**, and ask the human about the credential.

## Check-in checklist (blocking)

For any change adding or modifying a state-changing path:

- [ ] Mutating entry point registered in the audit contract registry (C314)
- [ ] Audit entry written on **success, failure, and gate denial** (402/403/409 blockers included),
      with `actor_type` set correctly — `SYSTEM` / `AI` / `EXTERNAL` / `MAINTENANCE` for non-human
      actors, never omitted or faked
- [ ] Who / what / when / outcome all present — blocked attempts use `BLOCKED` / `DENIED` / `FAILED`
- [ ] Dependency guards that raise after an attempted action write + commit audit **before** raise
      (mirror `TRAINING_GATE_BLOCKED`)
- [ ] Retention: soft-delete only, no TTL, no hard delete; new enum values appended, never removed
- [ ] A test proves the audit entry is written — an audit path without a test is not implemented
      (per the repo's TDD mandate, error paths get tests like happy paths)
- [ ] Any exclusion is justified **in writing in `design.md`**, naming the durable counterpart
- [ ] Sentry / ops noise filters were **not** used as a reason to skip `audit_entries`

## Adjacent regimes — do not conflate

- **Privacy Act / PII minimisation** pulls the other way. Where the two conflict, the AML/CTF
  obligation wins for in-scope records — but that tension is a **human decision**, never resolved
  silently. Example: the mobile number on the user record (C154).
- **Vendor retention** (TouchSMS, Postmark, Veriff, Stripe) is outside this rule and outside your
  control — a DPA question, not a reason to change what this system stores.
- **Data sovereignty is independent** — all retained data stays in `ap-southeast-2`. Satisfying
  retention does not satisfy residency.
- **Never log credential values** into audit entries — presence or fingerprint only
  (`no-secret-masking.md`, `handling-sensitive-data`).
