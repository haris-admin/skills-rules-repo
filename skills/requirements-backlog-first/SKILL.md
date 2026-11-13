---
name: requirements-backlog-first
description: >-
  Use whenever a new requirement, functional or non-functional (security, accessibility, reliability, availability, performance, privacy, observability,
  cost), arrives from the owner, a review, an assessment, an incident or a partner. Every one goes into the backlog first, as a short high-level ticket,
  before any design, spec, code or "quick fix". Trigger on phrases such as "we need", "add a requirement", "can we also", "make sure that", "NFR", "backlog
  item", and when an assessment or review produces findings. Do NOT use to promote a ticket to Todo (use backlog-to-todo-agent-ready) or for a defect that
  is actively breaking production (log a prod issue and fix it, then back-fill the ticket the same day).
---

# Requirements go to the backlog first

One rule: **a requirement is not work until it is a backlog ticket, and it is not ready work until it has been polished** (see the
`backlog-to-todo-agent-ready` skill). This keeps ideas from being lost, stops half-understood work from reaching an implementer, and keeps one system of
record (Plane for the HandleDispute fleet).

## When to use

- The owner states a requirement, in text or from voice (voice text has typos: restate it as your reading and label it an interpretation).
- A review, assessment, audit, red team or incident produces findings or follow-ups.
- A partner, regulator or customer adds an obligation.
- Any non-functional requirement (NFR): security, privacy, accessibility, reliability, availability, performance, scalability, observability,
  maintainability, usability, portability, cost, interoperability.

## Procedure

1. **Capture verbatim.** Copy the owner's words exactly in a quoted block. Add your reading below it, marked "Interpretation". Never record your
   recommendation as the owner's decision.
2. **Check for a duplicate.** Search the backlog (titles and the linked document) before creating. If one exists, add a comment or link, do not create a
   second ticket. Never delete or edit another person's ticket without asking.
3. **Classify.** Decide: feature, NFR, defect, technical debt, decision, task, idea, review finding. Pick one primary label and add the NFR label
   (security, accessibility, reliability, availability, performance, privacy, observability, cost) where it applies.
4. **Create ONE high-level ticket in Backlog.** Title `[ID] short plain title`. Description of at most 10 lines: the problem or need, who is affected,
   the verbatim request, the source link (assessment file, spec, message date), the priority guess (the reviewer's, not a decision), known
   dependencies. Do NOT write the how, the files or the acceptance criteria yet. That happens at promotion.
5. **Group, do not flood.** A review with 40 findings becomes ticket-sized groups (one theme or one component each), each linking to its findings, plus
   one decision ticket for choices that need the owner. Each defect fix in an existing spec still gets its own amendment ticket (rule of the project).
6. **Record in the repository's backlog document** if the project has one (HandleDispute: `docs/product/product.md` section 6 or
   `docs/engineering/technical-debt.md`), with a link to the ticket id. The ticket is the queue, the document is the explanation.
7. **Say what you did.** Report the ticket ids and titles. State that nothing was started, and which ones need an owner decision first.

## Guardrails

- Every ticket starts in **Backlog**. Never create directly in Todo or In Progress, even if the owner sounds urgent: urgency sets priority, not state.
- Do not begin implementation from a backlog ticket. A backlog ticket is a claim that a need exists, nothing more.
- Never include secrets, tokens, customer personal information or production data in a ticket.
- Plane writes are rate limited (about 30 calls then HTTP 429): sleep 3 seconds between calls, retry after 40 seconds, send a browser-like
  User-Agent (a default urllib agent gets Cloudflare error 1010 that looks like a bad key). Read the key from the project's git-ignored env file and
  never print it or any fragment.
- A ticked task or a "done" claim is not evidence. A ticket moves to Done only with release and live verification, and a comment holding the evidence.
- Writing style: plain Australian English, no em dashes, sentence case.

## Checks before you finish

- [ ] The owner's words are in the ticket verbatim, and the interpretation is labelled.
- [ ] No duplicate was created. No ticket was edited or deleted.
- [ ] State is Backlog. Labels and priority set. Source linked.
- [ ] No design, no code, no spec was started.
