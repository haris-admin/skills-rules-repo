# Prove new security tests bite, with mutations (all agents)

Applies after tests go green for code whose job is a guarantee: authentication, single-use tokens, redaction, locks, encryption,
authorisation, "never logs a secret", "refuses X".

## Why this exists

14 Oct 2026, Tap-Ease Clover OAuth. All 208, then 325, tests passed on the first run. A mutation pass (deliberately breaking the code 36
ways and re-running the tests) showed what the green run hid:

- no test checked that a staff link is **not consumed** when OAuth is not configured (a survivor, fixed with a new test);
- a rollback-ordering bug (raising inside a database lock undoes the status write) is invisible to an in-memory fake, so it was only caught by
  an added real-Postgres test;
- two "survivors" were false alarms: the anchor text matched a docstring instead of the code, or the formatter had rewritten the anchor.

## Rules

1. **After GREEN, mutate.** Script each mutant as `(file, exact old text, new text)`: remove a check, flip a comparison, skip the
   redaction, log the secret, store the plain value, drop a guard.
2. **Restore byte for byte and assert it** at the end of the script. A mutation script that leaves a file changed is a bug.
3. **Every mutant must make at least one test fail.** A survivor is either a missing test (add it, watch it go red, then green) or an
   equivalent mutant (record why it cannot be observed, for example a check made redundant by a stricter one).
4. **Verify the mutation applied.** Count the anchor, and prefer anchoring on a unique code line over text that also appears in docstrings.
   Re-run mutants after a formatter changes the layout.
5. **In-memory fakes cannot prove transactional behaviour.** For locks, rollbacks and uniqueness add at least one test against a real
   local database.
6. **Treat a first-run pass as unproven**, and a test that passes before the code exists as vacuous unless it is a deliberate guard.

## Related

- Rules: `openspec-tdd-mandate.md`, `red-for-the-right-reason.md`, `test-doubles-vs-assertions.md`
- Skills: `test-driven-development`, `verification-loop`
