# Issue fixes amend the origin OpenSpec: 40 then 40a, 40b (all agents, all repos)

Applies whenever a bug, production issue or review finding needs a specified fix.

## Why this exists

**3 Nov 2026, handledispute.** After a high-priority review, the first set of fix specs was numbered 65a to 65g under a new "65" parent. The owner corrected it twice: "if the issue is in 40 then make 40a if the issue is in 13 and 13a existis then make 13b and so on. Don't make all changes to the 65 only", then "I don't want 65 as parent", then "All issues are openspecs of that same original requriement i.e. if issue is in 39 then 39a. Another bug reported in later cycle for 39 then 39b".

A bug or defect found in a feature is a requirement correction for that feature, so its fix is an amendment of the OpenSpec change where the feature originated: the next free letter on that spec's number.

1. Issue in spec `40` gets `40a`. A later issue in `40` gets `40b`, then `40c`. If `13a` exists, the next one on `13` is `13b`. Find the next letter with `ls openspec/changes | grep '^13[a-z]-'`.
2. Never batch a review's fixes under one new number, and never create an umbrella or parent spec for a set of fixes (the owner rejected that). Several issues from one origin may share one amendment if they are the same defect class; otherwise each gets its own letter.
3. Work with no single origin spec (a new capability) gets a new number as usual.
4. The amendment keeps the numbering style `NNx-short-slug/` with the normal four files, and sets `amends: <origin spec folder>` in `.openspec.yaml`. It records the owner's decision verbatim, requirements, acceptance criteria and tasks. Tests for the amendment cite its task ids (`T40a.01`).
5. The issue file records both ends: `Origin spec: 40` and `Amendment: 40a`. The `prod-issues/README.md` index row links the amendment.
6. If the origin spec is unknown, find it with `git log` or the feature's route and component names; record the reasoning. Ask the owner only when two origins are equally plausible.

## Patterns to Avoid

- A new top-level number or an umbrella spec per review.
- Fixing a defect with no spec trail, or specifying it only in the issue file.
- Renumbering after the fact without updating `amends:`, task ids in tests, and the issue files.

## Verification

`ls openspec/changes | grep -E '^[0-9]+[a-z]-'` shows each letter on its origin number with no gaps, and every issue file names both its origin and its amendment.
