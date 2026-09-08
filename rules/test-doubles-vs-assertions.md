# Test doubles vs. assertions — the only case where touching a passing-then-failing test is allowed

**Scope:** every agent, every change that refactors how existing code calls the database or any
collaborator. Narrow exception to
`docs/agent_rules/openspec-tdd-mandate.md`'s "never modify the test to make it pass".

## Why this exists

Added 12 Aug 2026 (C405). The mandate says: *a failing test aligned with the requirement means the
implementation is wrong — fix the implementation, never the test.* That is correct and stays
correct. But it was silent on a real, recurring situation, which made it both **a loophole** ("I
only changed the mock") and **a false block** (an agent stuck, unable to land an approved
refactor).

The situation: a mock simulates the *shape of a call* the code makes. When an approved change
deliberately alters that shape, the test fails **on the double, not on the behaviour**.

C405's approved Decision C2 changed `screening_worker`'s party read from one `scalars()` query per
matter to a single batched `select(MatterParty.id, MatterParty.matter_id)`. The existing
`fake_execute` double returned the old shape, so the code iterated a `MagicMock` and the test
failed — while the behaviour under test was completely correct.

## The rule

Updating a test double to simulate a new call shape is **not** "changing the test", provided
**all four** of these hold. If any one fails, you are weakening a test — stop and fix the
implementation instead.

1. **Every assertion is unchanged** — count, subject, and expected value, byte for byte. In C405:
   `mock_report_exception.assert_called_once()`, `mock_run_client_screen.assert_called_once()`, and
   `assert …kwargs["screened_by"] is None` were all untouched.
2. **The change is forced by an already-approved requirement or design decision, cited by ID.**
   Not by your convenience, and not discovered mid-implementation — if the decision is not already
   approved, that is a plan-gate question first (see the OpenSpec mandate).
3. **The double faithfully simulates the new *real* call shape.** You have not loosened it into a
   bare `MagicMock`, `Any`, or a return value that would satisfy any code at all. A double that
   can no longer fail is not a double.
4. **You state it plainly in the change's `tasks.md` completion log**, labelled as a test-double
   update, with the assertions explicitly noted as unchanged. Never silently.

## Never covered by this exception

Whatever it is called, these are the forbidden act:

- Relaxing an assertion (`assert x == 3` → `assert x >= 1`, or → `assert x`).
- Widening a matcher (`assert_called_once_with(a, b)` → `assert_called()`; a literal → `ANY`).
- Deleting a test case, or an assertion within one.
- Adding `pytest.skip` / `xfail` / `it.skip` / `.only` to route around a failure.
- Changing a test's target path so it inspects a different file than the contract requires (already
  called out in the OpenSpec mandate for `fs.readFileSync` guardrails).
- Changing the *expected* value to whatever the code now produces. This is the most common
  self-deception: it always makes the test pass and never means anything.

## A mock-call-args assertion does not satisfy a "writes a row" / "persists" requirement

Added 7 Sep 2026 (C473, C476 — from the C472–C489 validation batch). A double is for isolating the
code under test from a *collaborator you are not testing*. When the acceptance criterion **is**
about the collaborator's effect — "writes an `audit_entries` row", "persists the record", "the
audit trail entry exists" — asserting `write_entry.assert_called_with(...)` on a mock proves the
call was made, not that the durable row exists. That AC needs a real `select(...)` against the
committed row (the pattern `tests/services/test_deed_parties_audit_attribution.py` uses).
Similarly, a test that greps a `.sql`/`.tf` file's text instead of executing it does not satisfy an
AC whose point is runtime behaviour (`red-for-the-right-reason.md` Rule 3). A task marked `[x]` on
a mock-args or source-grep assertion, where the AC calls for persistence or execution, is a false
completion-log entry — and this is exactly what `openspec-verify` Mode B step 11 re-checks.

## Production code must never be test-double-aware

Added 9 Sep 2026 (C492 Mode B verification). The inverse of everything above: instead of a test
being weakened to match the code, the **shipped code** was written to detect a test double and
skip its real path.

Found in two places in one change's SSRF-hardening work:

- `webhook_sub._post_pinned` imported `unittest.mock.AsyncMock` and returned early —
  bypassing the SNI-pinning connection path — whenever `client.post` was an `AsyncMock`.
- `_resolve_all` branched on `hasattr(socket.gethostbyname, "return_value")` (a Mock-detection
  probe) and carried a hardcoded `example.com/org/net → 93.184.216.34` map, added to make
  pre-existing SSRF regression tests pass without updating them.

Both shipped to `dev`. The effect: the security control (SSRF address pinning) is silently
inert in any process where a test double is present, and the tests that were supposed to prove
the control works are exercising a different code path than production runs.

**The rule:** production code MUST NOT contain any reference to `unittest.mock`, `AsyncMock`,
`MagicMock`, `hasattr(x, "return_value")`, `"pytest" in sys.modules`, an `if TESTING:` shortcut
around real logic, or any other test-environment sniff. If a test can only pass by making the
code aware of the test, the test is at the wrong seam — inject the collaborator (client,
resolver, clock) as a parameter or via a fixture-overridable factory, and let the real code path
run unchanged against it. A real-handshake / real-resource fixture (a local HTTPS server, a
disposable Postgres) is the correct answer when a pure double can't exercise the path honestly.

**The check:** `grep -rn "mock\|Mock\|return_value\|TESTING\|sys.modules" <production dirs>` on any
change that touched code with awkward-to-mock collaborators (network, DNS, TLS, subprocess,
clock). Any hit in non-test code is a finding.

## The check to run on yourself

> If the implementation had a genuine bug, would this test still catch it?

If the answer is no — or "I'm not sure" — you have weakened it. Revert and fix the implementation.

## Related

- `docs/agent_rules/openspec-tdd-mandate.md` — tests come from requirements; never modify a test to
  make it pass
- `docs/agent_rules/red-for-the-right-reason.md` — what counts as valid Red, and proving a guard
  test is not vacuous
