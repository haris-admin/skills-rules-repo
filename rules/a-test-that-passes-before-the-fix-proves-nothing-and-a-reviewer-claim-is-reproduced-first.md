# A reviewer's claim is reproduced by a failing test first, and a test that passes before the fix proves nothing

Findings from a blind review, a subagent or a teammate are claims. Reproduce each with a test that fails for the stated reason before changing code.

**Scope:** every agent acting on review findings, in any repo.

## Why this exists

**23 Nov 2026 (HandleDispute):** a reviewer said a later failed close rolled back an earlier case's notice. The first test passed before the fix because it asserted "some job exists for the case"; tightening the assertion to the closure notice's subject turned it red (0 notices, expected 1). Other claims were unconfirmed and were logged as "reported", not fixed.

## Rules

1. Write the test, run it, and confirm it fails for the expected reason (not an import, fixture or typo error) before implementing.
2. If the test passes on the unfixed code, the assertion is too loose: tighten it until it fails, or conclude the claim is wrong.
3. Record each finding as Confirmed (read or reproduced), Reported (reviewer only), Built, Handed or Open, so a later agent does not treat a claim as a fact.
4. Check the claim's anchors in the code (file, line, function) yourself; a subagent's line numbers can be stale.
