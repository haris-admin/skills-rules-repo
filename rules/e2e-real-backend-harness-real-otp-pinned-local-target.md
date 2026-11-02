# End-to-end tests run against the real local backend, with real one-time codes and a pinned, guarded target

Applies to every Playwright or browser end-to-end suite, on every project.

## Why this exists

**2 Nov 2026, handledispute (OpenSpec 57).** The suite had 13 failing tests, then 23 after one run. The extra failures were environmental: the dev server inherited `NEXT_PUBLIC_API_URL=http://192.168.50.210` from `.env.local`, so calls landed in a mix of places. Twelve specs also typed a hardcoded `123456`, which OpenSpec 38 had removed on purpose (codes are random and stored only as salted hashes). About 19 mocked responses hid a login contract that had changed twice.

## Core Directives

1. **Pin the API target in the test config**, never rely on `.env.local`. Set `webServer.env` for the API base URL and do not reuse an existing dev server (`reuseExistingServer` only on an explicit flag).
2. **Add a global-setup safety guard** that refuses to run unless the API URL is loopback AND the API reports a local or test environment. Unit-test the guard as pure functions.
3. **Never reintroduce a fixed code to make tests pass.** Recover the real OTP in the harness: read the newest unverified challenge (salt and hash) from the LOCAL database and find the 6-digit code by hashing the 1,000,000 candidates (about one second). Only ever against the loopback database, behind the guard. Product code stays unchanged.
4. **Seed demo data idempotently** in global setup, after the guard passes. Use reserved `.invalid` contact addresses so no message can ever be delivered, and force mock email and no SMS for the local run.
5. **Real backend by default; mocks only for fault injection**, each labelled. A mock encodes a contract and goes stale silently.
6. **Triage a failing baseline by cause before editing any test:** (a) environment, (b) stale selector or copy, (c) changed requirement. Fix (a) and (b). For (c), write the new acceptance criteria and get the human's approval first, then update the requirement document and the test together.
7. **Helpers never echo a command line.** Pass the database password in the environment, SQL on stdin (psql does not expand `:'var'` inside `-c`), and throw sanitised errors.
8. **Fresh services for a trustworthy run:** a scanner or other dependency that the flow needs must be running and fresh, or the failure is the environment, not the test.

## Patterns to Avoid

- Hardcoded codes in specs, even "for the test environment".
- A "pass" produced by mocking the endpoint whose contract changed.
- Editing assertions to match behaviour before knowing whether the requirement changed.

## Verification

Run the suite twice from a clean state. The failure list must be identical, and no failure may depend on what a previous run left in the database.
