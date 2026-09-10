---
name: implementer-neutral-handover
description: Write build-handover notes addressed to "whichever agent implements this," and file your own review/critique findings inside the artifact's own folder — never a separate cross-cutting digest doc.
---

# Implementer-Neutral Handover + In-Folder Feedback

## Directives

1. **Never address a handover doc to one named tool.** When more than one agent/tool can end up
   building a given spec (e.g. Cursor or Antigravity, depending on assignment), write "for
   whichever agent implements this (currently `<tool>`, per the recorded decision)" instead of
   "For Antigravity." The assignment can change after the doc is written; the doc shouldn't go
   stale or read wrong when it does.
2. **File review/critique findings inside the artifact's own folder**, e.g.
   `<change-folder>/CLAUDE_FEEDBACK.md` or `<PR-branch>/REVIEW_NOTES.md` — never a separate
   top-level digest doc aggregating feedback across many artifacts. A cross-cutting digest is
   another thing to find, keep in sync, and go stale; feedback belongs next to what it's about.
3. **Make the feedback file append-only and dated.** Never edit or delete a past entry — add a new
   dated entry if a later pass supersedes an earlier finding, and say explicitly what changed and
   why. This preserves the audit trail of who found what, when, and whether it was actually fixed.
4. **State plainly whether you fixed it yourself or are asking someone else to.** "Already applied
   directly — not a request" reads very differently from "needs correction before build," and
   conflating them wastes the next reader's time re-deriving which is true.
5. **Direction for another agent is a durable artifact, not a chat message** — this holds even
   before a spec folder exists. Asked to review-and-direct without building: create the change
   folder at the correct next number (check the index — never trust a number quoted in a brief),
   drop a `CLAUDE_FEEDBACK.md` in it stating no spec is authored yet, and enumerate what the next
   agent must author (which files, what each contains, gating tests and decisions). Give
   instructions, not implementations. Cross-cutting direction (process, skills, rules) goes in a
   named `docs/` doc. See the `agent-handoff-direction-artifact` rule for the full contract.
