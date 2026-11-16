# A contract digest is voided by any edit and needs its own acceptance

Applies when an owner accepts a requirements contract by its file hash before a build, and the build later finds gaps.

**Scope:** all agents building from an accepted contract; HandleDispute spec 85 (D115 to D118).

---

## Why this exists

Spec 85 pinned `contract.md` and `report.schema.json` by sha256 (D115). The build found ten gaps (two requirements that contradicted each other, a missing audit outcome, a link form the static export cannot serve, a log rule that conflicted with the owner's own audit decision). Each fix changed the contract, so the first acceptance was void; a second digest was pinned only after the last edit and accepted on its own (D118).

## Core Directives

1. **Never edit an accepted contract silently.** List each change with a recommendation, get the owner's answer verbatim, then edit.
2. **Pin the digest after the last edit,** with the full hashes in a file inside the spec folder, and record the owner's acceptance of that digest as its own question, separate from approving a plan or a release.
3. **Say what voids it:** any edit to the pinned files. Record the superseded digest and keep the chain of records (D115, D118).
4. **An implementer stops at a contract gap.** It records the gap and does not work around it; the coordinator batches the gaps for the owner.
5. **A test that pins an old requirement changes with the requirement,** in the same commit, citing the owner decision (the identity lease default moved from 30 to 120 minutes under D73).
6. **When free text conflicts with an earlier answer,** ask which governs and record both.
