# A plan's own mutation score is not proof: the reviewer writes fresh mutations, and survivors are findings

A plan that reports every one of its mutations caught has only proved its own tests catch what its author thought of. An independent reviewer must break the rules in new ways.

**Scope:** independent reviews of security or money rules that ship with a test suite and a mutation suite.

---

## Core Directives

1. **Brief the reviewer to write its own mutations** (about 15 per round, aimed at the changed rules), run the whole suite for each, and report every one that passes as a finding.
2. **Fix by adding an assertion per survivor**, prove it caught, and update the counts; never loosen an existing test.
3. **Rounds shrink when the process works.** Expect blockers first, then majors, then missing tests; stop when a round finds no blocker and only named residuals, then approve the hash.
4. **Review the diff, not the whole.** Later rounds review only what changed, against the previous hash, and re-run the earlier reproductions.

## Why this exists

**23 Nov 2026 (SonoVantage database plan):** seven rounds. The author's suites reported 160, 184, 215 and 251 of the same count caught each time, while the reviewer's own mutations still survived (11 of 15, 12 of 17, 15 of 16, 10 of 15). Findings fell from 3 blockers in round 1 to 0 blockers and 1 major in round 7. Related: [independent red and diff review gate](./independent-red-and-diff-review-gate.md).
