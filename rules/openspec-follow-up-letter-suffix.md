# OpenSpec follow-ups carry the original number plus a letter

Every issue or bug raised against work that an OpenSpec change already governs is its own OpenSpec, numbered from the original change with a letter suffix.

**Scope:** every agent, every project that uses `openspec/changes/`.

## The rule

- An issue found in change `39` is OpenSpec `39a`.
- A second issue reported in a later cycle against `39` is `39b`, then `39c`, and so on.
- The letter always attaches to the ORIGINAL requirement's number, never to the previous follow-up. A bug in the fix for `39a` is `39b`, not `39aa`.
- The folder keeps the project's slug style: `openspec/changes/39a-<short-slug>/` (for example `004a-card-authorize-mcc-reject`), with the usual `proposal.md`, `design.md`, `tasks.md` and `.openspec.yaml`.

## Why this exists

Haris, 3 Nov 2026: "All issues are openspecs of that same original requirement i.e. if issue is in 39 then 39a. Another bug reported in later cycle for 39 then 39b." The follow-up stays traceable to the requirement it defends, and the chain of authority (requirement, test, implementation) is not broken by an untracked fix.

## How to apply

1. Find the original change number the defect belongs to (search `openspec/changes/` and the requirement IDs the failing behaviour cites).
2. List existing `<n>a`, `<n>b`, ... folders and take the next unused letter.
3. Write the follow-up OpenSpec first: `proposal.md` cites the original change and the symptom, `design.md` states the corrected requirement, `tasks.md` lists the failing test (Red) before the fix.
4. In `.openspec.yaml` set `parent: <original id>` and link the follow-up from the original change's `tasks.md`.
5. Cite the follow-up ID in the regression test name or docstring (for example `# 004a.01`).
6. Do not use a fresh sequence number for a defect in an existing requirement. A genuinely new requirement still takes the next number.

## Issues linked to more than one original OpenSpec (added 3 Nov 2026)

An issue that touches several originals gets ONE dedicated OpenSpec, linked to all of them.

Haris, 3 Nov 2026, structured question "How should that OpenSpec be numbered?": "Lowest original + letter (Recommended)" ("Number it from the lowest-numbered original plus the next free letter (004 and 003 gives 003c if 003a and 003b exist). `.openspec.yaml` lists every original under `parents:`, and each original's tasks.md links back."). Second question, "Which spec owns the lettering when an issue is linked to several originals?": "Lowest-numbered original (Recommended)" ("The earliest original is the primary parent and supplies the number and letter. The others are secondary parents, linked in `parents:` and back from their tasks.md.").

1. Primary parent is the lowest-numbered original. It supplies the number and the next free letter (original 003 and 004, with 003a and 003b taken, gives `003c-<slug>`).
2. `.openspec.yaml` sets `parents:` as a list of every original, primary first. A single-parent follow-up may keep `parent:`.
3. `proposal.md` names each original, the requirement IDs affected in each, and the symptom.
4. Every original's `tasks.md` gets a link back to the dedicated OpenSpec.
5. Tests cite the dedicated ID and, where they guard an original's requirement, that requirement ID too.
6. Never split one issue into per-original follow-ups with duplicated fixes. One issue, one OpenSpec.

## Guardrails

- A hotfix carve-out does not remove the follow-up OpenSpec. Write it after the hotfix, with the same letter.
- If it is unclear which original requirement owns the defect, ask the human with a structured question. Do not guess.
- Past 26 follow-ups on one change (`z`), stop and ask the human how to continue the sequence.
- This is separate from `prod-issue-numbering` (the `issue-NNN` register for production defects). Cross-link the two when a prod issue also has an OpenSpec follow-up.
