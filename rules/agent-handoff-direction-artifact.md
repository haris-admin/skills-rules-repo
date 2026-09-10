# Agent handoff direction artifact (all agents)

Applies whenever one agent (typically Claude Code) produces feedback, a review, an architecture
direction, or a plan that a **different** agent or session is expected to act on — including
pre-authoring direction for work that does not have a spec folder yet.

## Why this exists

The portfolio runs a spec-author / implementer split (Claude Code authors specs and reviews;
Cursor / Antigravity / Devin build). Direction given only in a chat message is lost the moment the
session ends, arrives without context to the next agent, and cannot be checked later for whether it
was followed. The fix is the same one `implementer-neutral-handover` already applies to build
handovers, generalised: **direction for another agent is a durable, in-repo artifact, not a chat
message.**

Origin: 2026-09-10, HiveCoach/AMLAudio (AMLHive `openspec/changes/496-*`, `497-*`). Claude Code
was asked to review two product ideas and hand direction to another agent without building them.
The direction went into `CLAUDE_FEEDBACK.md` files in each change folder — which is what this rule
codifies as the default.

## Rules

1. **Write the direction to a file in the repo it concerns, not (only) to chat.**
   - Reviewing/directing an existing OpenSpec change → `openspec/changes/<id>/CLAUDE_FEEDBACK.md`.
   - Directing work that has no change folder yet → create the folder (correct next number — check
     the index, don't trust a number quoted in a brief) and put `CLAUDE_FEEDBACK.md` in it; state
     in the file that no spec is authored yet and what the next agent should author.
   - Cross-cutting direction (affects many artifacts, or is about process/skills/rules) → a named
     doc in the relevant repo's `docs/` (or the skills repo), linked from wherever the work is
     tracked. Never a top-level "feedback digest" that aggregates across unrelated artifacts.
2. **Address it to "whichever agent implements this", not one tool by name.** Source the current
   assignment from the change's recorded decision as a fact ("currently Antigravity, per
   `proposal.md`") — the doc must still read correctly if the assignment changes.
3. **Append-only, dated, model-attributed.** Each entry: what was reviewed (files + commit or "no
   implementing commit yet"), a one-line verdict (approve as-is / needs correction before build /
   needs a human decision on X), concrete findings with file:line where possible, and the human
   decisions still needed. Never edit or delete a past entry — supersede it with a new dated one
   and say what changed.
4. **State plainly whether you fixed it or are asking someone else to.** "Applied directly — not a
   request" and "needs correction before build" must not be conflated.
5. **Give instructions, not implementations.** When the task is explicitly review-and-direct, do
   not write the spec or the code. Enumerate what the other agent should produce (which files,
   what each must contain, what tests, what decisions gate it) and stop.
6. **List the open human decisions separately and do not resolve them yourself**
   (`no-fabricated-human-decisions.md`). An open question stays open, flagged for the human.
7. **Tell the user the artifact exists and what it says** — the file is in addition to reporting in
   chat, never instead of it.

## Patterns to Follow

```
openspec/changes/496-hivecoach-voice-training-simulator/CLAUDE_FEEDBACK.md
  # Claude feedback log — C496
  ## 2026-09-10 (Claude Sonnet 5, design review — pre-authoring, no change authored yet)
  **Reviewed:** <one-pager> + <codebase files @ commit>
  **Verdict:** needs human decisions (5, listed) before Claude Code authors proposal/design/tasks
  **Findings:** 1. ... 2. ...
  **Human decisions needed:** 1. ... 2. ...
  (+ explicit "what to author in proposal.md / design.md / tasks.md" instructions)
```

## Patterns to Avoid

```
docs/handoff_<tool>_feedback_2026-09-10.md          # a top-level cross-artifact digest
"For Antigravity: ..."                               # hardcoded to one tool
# editing yesterday's finding in place instead of adding a dated entry
# writing the proposal.md yourself when asked only to review and direct
```

## Related

- `implementer-neutral-handover` skill — the build-handover + in-folder-feedback discipline this
  generalises
- `claude-code-spec-only-implementer-builds.md` — the spec-author / implementer split
- `no-fabricated-human-decisions.md` — open decisions stay open
- `subagent-verification-protocol.md` — verifying a downstream agent actually followed the direction
