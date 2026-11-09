# Who decided it: answer from a record, never from a guess (all agents, all repos)

Applies when answering who made an architectural or product decision and when; answer strictly from an explicit decision record, never from guesswork or nearby commit authors.

## Why this exists
**9 Nov 2026, Tap-Ease:** Haris asked when tips were turned off and whether a named colleague had decided it. The code showed tips disabled since the first release, but no document recorded a decision or a decision maker. A commit author is not the decider (the early commits were bulk imports and release preparation).

## Rules
1. Answer "who decided and when" only from a decision record (OpenSpec proposal, ADR, structured answer, dated message). If none exists, say so plainly: no record, here is the earliest code evidence and its commit, and the commit author is not necessarily the decider.
2. Never attach a decision to a person because their name is nearby in the conversation or the history.
3. When the behaviour matters, ask the human the question now and record the answer verbatim with the date (this session: "No tips for now"). Mark any older, unrecorded behaviour as "no recorded decision maker".
4. Keep a decision and its provenance in the project's decision log (AGENTS.md or an ADR) so the next agent does not have to reconstruct it.
