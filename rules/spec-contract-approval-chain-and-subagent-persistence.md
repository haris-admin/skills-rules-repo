# Spec Contract Approval Chain, Digest Supersede, and Subagent Persistence

How a spec-driven change goes from drafted contract to "ready for the implementer" through subagents, independent reviewers and the human, and the housekeeping that keeps that chain honest.

<!-- IMPORTANT: Do NOT include YAML frontmatter (---) in rules/*.md. Rules must begin with an H1 title on line 1. -->

**Scope:** All agents, all repositories that use a pinned, hashed test contract and an independent review gate before an implementer builds.

---

## Core Directives

1. **Pin the contract digest only after the contract's final edit.** Compute it with `shasum -a 256`, state the method, never invent a value, and label it CANDIDATE until an independent reviewer accepts it.
2. **Any edit to the contract bytes voids the pin, even a wording change.** Keep the old digest in a supersede chain marked SUPERSEDED, pin the new one, and have a fresh reviewer do a narrow re-acceptance of only the changed rows, classifying every changed line from `git diff <old>..HEAD` as in scope or unexpected. Prefer design-only fixes when the contract defers to the design, and say which edits change the hash.
3. **The human approves the final pinned digest as its own gate.** Approving a plan, a slice or an option is not approving a digest. Use a structured question that names the digest and lists every detail the spec author specified on its own.
4. **Record the human's decisions verbatim.** Write the question, the selected option and its description, then map precisely what it decides and record nothing else as decided. A structured-question selection is the human's real answer; an agent's recommendation is not. A decision about one slice does not approve another.
5. **The implementer brief comes after the gates.** Quote the authority verbatim, make the first action recomputing the contract hash and stopping on a mismatch, require Red then a stop for independent Red acceptance, Green then a stop for independent diff review, list allowed files and a not-authorised list, and allow local pathspec commits only.
6. **The author never reviews its own contract and never writes the risk review.** An independent reviewer verifies each Red reason against the live code with a scratch probe, not by reading the spec.
7. **Commit each spec folder the moment its author finishes**, with a pathspec commit and the pinned hash re-verified first. Unexplained reverts hit three authors in one session and left no reflog trace.
8. **After a usage-limit failure, inspect the tree for what reached disk and resume the same agent with `SendMessage`.** Never cold re-dispatch over partial work.
9. **A read-only reviewer's report goes into the repo by one of two routes:** a follow-up that lifts the rule for exactly two named report files, or the orchestrator appends the reviewer's text and says so. The text is the reviewer's, quoted, not rewritten.
10. **Give the human short symlinks for handoff scripts.** A long path wraps in a terminal and splits into two commands. One command per message, the symlink target stays the SHA-pinned script.
11. **A push you did not make is reported, not undone.** After a session compare `git ls-remote origin refs/heads/<branch>` with local `HEAD`; if they match and you did not push, say so, list what was published, and ask whether it was intended. Never force-push to fix it.
12. **Ask, do not assume.** List every open decision as a structured question with options and a recommendation. Restate free or voice text as your reading, label it an interpretation, and let the human confirm it (a voice transcript can carry a wrong word). When two answers conflict, ask which governs and record both; the later confirmed answer supersedes the earlier one, which stays visible.
13. **A requirement change after a review voids the reviews of the changed scope.** Record the earlier risk review, contract acceptance and digest approval as SUPERSEDED, renew them for the new scope, and split a change that has grown into slices with their own contracts, digests, reviews and briefs.
14. **Hiding a value and keeping a record of it are separate requirements.** When a privacy fix hides values from logs or a vendor, ask what auditors and authorities still need to see and where the controlled copy lives.

---

## Patterns to Follow

- A supersede chain table in the plan: digest, commit, status (SUPERSEDED, CANDIDATE, ACCEPTED, APPROVED).
- A narrow re-acceptance report that lists in-scope rows, the diff classification and what the human must still do.
- A verified-versus-unverified list in every review report.

## Patterns to Avoid

- Pinning a digest before the last edit, or reusing a pin after an edit.
- Treating ACCEPT-WITH-CONDITIONS as a pass before the conditions are applied and recorded.
- Starting the implementer before the final digest is approved and the brief exists.
- Recording an approval, answer or hash that the human did not give or the shell did not produce.

---

## Verification & Guardrails

- Recompute every pinned digest from the file on disk before relaying it, and confirm `git status --short` shows only the paths the agent was scoped to.
- Related: `rules/independent-red-and-diff-review-gate.md`, `rules/no-fabricated-human-decisions.md`, `rules/subagent-dispatch-authorization-boundary.md`, `rules/subagent-verification-protocol.md`, `rules/isolated-production-release-recipe.md`.
- Origin: six to eight Oct 2026, four spec-driven Sentry changes taken from proposal to ready-for-implementer by subagents and reviewers.

## Lessons 16 Oct 2026 (C531 slice 1 revision 3.9, five passes)

- **Sweep every Red/Green classification against the code in one pass.** A reviewer found one wrong "already Green" cell per round (an assertion on a counter, then on a property that did not exist yet) until the author grepped every identifier each case names (fields, constants, files, migrations) against the code under test and listed the result in the changed-lines file. Do the whole sweep before the first re-acceptance.
- **A contract oracle must be able to pass on a correct implementation.** Reason each oracle through against the code and the database profile: a reject-first trigger whose counter rolls back with the aborted transaction refuses every later insert; an enum injection on a column that is plain `text` in the test profile never fails. Match on the text form of a column so the injection works for either type.
- **State which answers a candidate digest assumes.** When the human answers a question differently from the recommendation the candidate assumed, the digest is void: list every voided digest in the supersede chain and batch all open questions into one round before the narrow re-acceptance.
- **When the approved file must stay byte-identical, write the revision as a new file** and point the implementer brief's hash check at it only after the human approves the new digest; keep a changed-lines file that classifies every line against the approved base and reproduces the diff hunk headers.
- **Label author-drafted values.** A range, literal or name the human did not decide gets an author-specification number, and the digest approval names it, so a drafted default is accepted on purpose.
- **A second reviewer is a second opinion.** A concurrent session may record its own independent verdict on the same digest; keep both, check that each is independent of the author and builder, and never undo either.
