# Readiness checklist (every box must be ticked before Todo)

Content
- [ ] The problem still exists today. I re-verified it in the code or by a read-only command, and the evidence is in the ticket.
- [ ] The owner's words are quoted verbatim. Decisions are recorded as question, selected option, description. My own readings are labelled.
- [ ] Every acceptance criterion is observable and testable, with numbers where numbers matter. No "works", "fast", "secure" without a measure.
- [ ] Origin spec and amendment id are named. Requirement and task ids are cited. A fix is its own amendment.
- [ ] No open design question remains. If one does, the ticket stays in Backlog marked "Blocked on decision".

Mechanics
- [ ] Every file to change is listed with an exact path. Every file not to touch is stated.
- [ ] Every step is one action with a command and an expected output. Edits are given as exact before and after text or full code.
- [ ] Tests come first, with names, fixtures, assertions and the expected red reason, including negative and boundary cases.
- [ ] Commands that run only the new test, the related suite and the gates are given, with the expected summary.
- [ ] The preflight and safe local environment are stated. Nothing reads or writes production, secrets or live providers.
- [ ] Constraints, denial of authority, stop points, evidence list and rollback are all present.
- [ ] Size is right: about 15 steps or fewer, about 6 files or fewer, one concern. Otherwise it is split and ordered.
- [ ] Project terms used are defined in the ticket, not only linked.

Verification of the ticket itself
- [ ] A fresh small model, given only the ticket, restated the plan correctly and listed nothing it was unsure about. Twice.
- [ ] The lowest tier that passed the cold-start test is the tier label on the ticket.
- [ ] State is Todo, labels `agent-ready` and `tier-*` are set, and a comment records date, checklist, cold-start result and evidence.
- [ ] The ticket contains no secret, token or customer personal information.
