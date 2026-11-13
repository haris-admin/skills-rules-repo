---
name: backlog-to-todo-agent-ready
description: >-
  Use when a backlog ticket is about to move to Todo, so that it is detailed and mechanical enough for any agent to implement, including smaller or less
  capable models (Sonnet, Haiku, or agents from other providers) with no prior conversation. Produces an agent-ready ticket: exact files, ordered
  steps, copy-pasteable commands, test-first cases with the expected red reason, acceptance criteria, guardrails, stop conditions and evidence required.
  Trigger on "move to todo", "make it ready", "polish this ticket", "get it ready for an agent", "write the how", "promote from backlog". Do NOT use to
  capture a new requirement (use requirements-backlog-first) or to implement the ticket.
---

# Backlog to Todo: make the ticket agent-ready

A ticket in **Todo** means: *a different agent, with no memory of this conversation and less reasoning power than the author, can pick it up and finish it
correctly without asking anything except at a listed stop point.* If that is not true, the ticket stays in Backlog.

The author does the thinking. The implementer follows. Put every decision, path, command and expected output in the ticket. Do not rely on the
implementer being clever, remembering the project, or guessing intent.

## When to use

- The owner says to bring tickets from Backlog to Todo, or a ticket has been prioritised for the next work.
- Do the promotion for one ticket at a time, in priority order, unless the owner names a set.

## Procedure

1. **Read the ticket and its source.** Open the linked document, finding, spec or message. Re-verify the claim against the code today (open the file,
   run the read-only command). A finding that no longer holds is closed with evidence, not promoted. A ticked task or a past review is not proof.
2. **Resolve decisions first.** If the ticket needs a choice from the owner (design option, scope, version, contract change), ask the owner one question at
   a time with options and a recommendation, record the answer verbatim in the ticket, and only then continue. If the owner has not answered, the ticket
   stays in Backlog with a "Blocked on decision" note. Never decide for the owner.
3. **Find the origin spec.** Work traces to an OpenSpec: a new capability gets the next number; a fix to an existing feature is the next letter on the origin
   spec (`amends:` set), one issue per amendment. Create `.openspec.yaml`, `proposal.md`, `design.md`, `tasks.md` or reference the existing ones.
4. **Fill the agent-ready template** in [references/ticket-template.md](./references/ticket-template.md). Every section is mandatory; write "None" where
   it truly does not apply.
5. **Make it mechanical.** Apply the rules below, then run the readiness checklist in
   [references/readiness-checklist.md](./references/readiness-checklist.md).
6. **Cold-start test.** Dispatch a fresh, small model (for example Haiku) with only the ticket text and this instruction: "Restate the steps you would
   take, name the first command you would run, list every file you would touch, and list anything you are unsure of. Do not do the work." If its answer
   is wrong, vague, or lists an unsure item, fix the ticket and repeat. Two clean passes means ready. Give the test agent a denial of authority (read
   only, no edits, no commits, no pushes, no provider calls).
7. **Move the ticket to Todo** (Plane state Todo) and add a comment with: the date, the readiness checklist result, the cold-start test outcome, the
   recommended implementer tier, and the evidence link. Add the label `agent-ready` and one tier label: `tier-small` (Haiku-class or other small
   models), `tier-medium` (Sonnet-class), `tier-large` (needs a top model or the owner present). Choose the **lowest tier that passed the cold-start test**.
8. **Report** the ticket id, tier, and anything still needing the owner. Do not implement it unless told to.

## Rules that make a ticket small-model-safe

- **Absolute or repo-root-relative paths, always.** Name every file to create or change. Quote the exact function or section and its current line
  range, and say how to find it if lines move (a `grep -n` command).
- **One action per step, in order,** each with the command to run and the exact output that means success. No "as appropriate", no "etc.", no "similar
  to", no "ensure it works".
- **Show, do not describe.** Give the code to add or the exact before and after text for each edit, not a prose description of the change. For a long
  body, give the signature, the full body and a worked example input and output.
- **Test first, spelled out.** Name the test file and test names, the fixture values, the exact assertions, and the failure message the test must show
  while red ("Red for the right reason"). Name the command that runs only that test and the command that runs the related suite. Cite the requirement id in
  each test (`T66c.02`). Include negative cases and boundary cases. A test is never edited to make it pass.
- **Define every project term once,** with a link. Do not assume the agent knows what a "CRR", "APP 6" or "ledger" is.
- **State constraints as prohibitions with reasons:** frozen API contract (no status code or response field changes), no hardcoded tunable values, no
  secrets or tokens in output, provider errors generic for users and detailed for admins, every mutating route needs an audit activity or a written
  exemption, migrations need downgrade and a rehearsal, never invent a fallback for a missing identifier or payment state.
- **Denial-of-authority clause in every ticket:** the implementer may not push, merge, deploy, run a workflow, send any message, call a live provider,
  rotate or print a secret, delete data, or touch files outside the listed set. Silence is a denial. Anything useful found outside the scope is reported in
  a comment, not acted on.
- **Stop points.** List the exact situations where the implementer must stop and ask: a failing test that seems to contradict the requirement, a needed
  change to an API contract, a design choice not recorded, a file outside the list, a command that behaves differently from the ticket.
- **Evidence required to call it done:** the commands and their outputs (summary lines and exit codes read from the log, never inferred from a background
  notification), the commit hash, the files changed list, screenshots for UI at the named widths. "Done" is claimed by the implementer and checked by
  someone else.
- **Rollback:** how to undo the change if the check fails.
- **Right-size it.** If the steps exceed about 15, or touch more than about 6 files, or mix a migration with UI work, split it into several tickets, each
  independently verifiable, with the order and dependencies written down.

## Guardrails

- Only the author of the ticket marks it ready, and only after the cold-start test. A ticket promoted without it is moved back to Backlog.
- Do not change the requirement while polishing. If polishing shows the requirement is wrong or ambiguous, stop and ask the owner.
- Do not push, deploy or release as part of promotion. Promotion edits the ticket and the spec files only.
- Keep the ticket self-contained: paste the needed facts in. Links are for evidence and depth, not for essentials, because a small agent may not follow them.
- Plane limits: about 30 writes before HTTP 429. Sleep 3 seconds between calls, retry after 40 seconds, browser-like User-Agent, key from the git-ignored
  env file, never printed.
- Plain Australian English, no em dashes, sentence case headings.

## Verification before you finish

- [ ] The readiness checklist passes, every box.
- [ ] A cold-start test by a small model passed twice, with no unsure items.
- [ ] Decisions are recorded verbatim, with the question and the selected option.
- [ ] State is Todo, labels `agent-ready` and one tier label are set, and the comment records the evidence.
