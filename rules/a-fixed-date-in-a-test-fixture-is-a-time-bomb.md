# A fixed date in a test fixture is a time bomb

A fixture that hardcodes a timestamp and is checked against the real clock passes until the age limit in the code under test expires.

**Scope:** tests of freshness, expiry, signature age, token lifetime or any rule that compares with now.

---

## Core Directives

1. **Build the timestamp from the current time** (or freeze the clock) in the fixture.
2. **Search for literal dates near age limits** whenever a limit test fails on code that did not change.
3. **A test that starts failing with no code change is a clock failure until proven otherwise.**

## Why this exists

**21 Nov 2026 (HandleDispute):** a ClamAV readiness test used the version string `Mon Nov 16 2026` against a 72 hour signature limit. It passed until 19 Nov and failed on every run after, including a clean main. Building the string from the current time fixed it without touching any assertion.
