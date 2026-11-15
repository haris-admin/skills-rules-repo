# Design approval comes before RED tests, and only the owner approves (all agents, all repos)

**Origin (Tap-Ease, 15 Nov 2026, card-data-local-store).** Asked to "create the tables first, create the OpenSpec", an agent wrote a RED test file, started a database container and wrote "approved to build" in its own spec. The owner objected: "Follow our standard. We do the open specs first, then we expand it, decide about the design. Once we are happy with the design, then we follow the TDD approach." The wording was withdrawn, the order was reset, and the incident was recorded in the change folder's `CLAUDE_FEEDBACK.md`.

## Rules

1. **Order is fixed:** OpenSpec drafts, then design decisions with the owner, then the owner says to start building, then RED, GREEN, REFACTOR. A request to "create the tables" or "build X" starts the spec, not the tests.
2. **Only the owner writes "approved".** An agent never marks a spec, design or task as approved, ready or "approved to build". Use "DRAFT, nothing approved" banners until the owner's dated entry exists.
3. **No test files, containers, migrations or scratch databases before that entry.** A draft test written early stays untracked, is not committed, and is re-derived from the approved spec by the implementer.
4. **A free-text or voice answer is the agent's reading, labelled as such.** Record the question and the selected option verbatim; record a free-text answer verbatim plus a separate line "reading (agent interpretation, awaiting confirmation)". Ask one decision at a time with a recommendation.
5. **When a decision changes scope, mark every dependent draft "NEEDS REDRAFT" the same day** so a handover brief is never built from a stale assumption.
6. **Handover briefs are implementer-neutral** and carry a gate section stating which decisions are still open.

Related: `openspec-tdd-mandate`, `no-fabricated-human-decisions`, `claude-code-spec-only-implementer-builds`.
