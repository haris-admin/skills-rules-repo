---
name: startup-vc-skeptic
description: >-
  Run a blind, hostile venture-partner review of a startup idea: act as a tier-1 fund partner who has rejected 10,000 pitches and give exactly 10 specific reasons for passing, split into Fixable Execution Risks and Fundamental Structural Flaws (unit economics, distribution traps, regulatory moats, incumbent bundling), each independently validated and tagged. Use when asked for the "idea killer", a skeptical investor view, "why would a VC pass", or a blind second opinion that must not see other reviews.
---

# Startup VC Skeptic (Blind Idea Killer)

A deliberately blunt external review. Its value comes from independence: it must not read any other reviewer's work.

## When to Use

- Before pitching, applying to an accelerator, or committing build time.
- After a pre-mortem, to test whether an unanchored reviewer finds the same fatal issues.
- Do NOT use for encouragement, polishing a pitch, or customer discovery.

## Procedure

1. **Dispatch as a separate subagent** using the brief in [blind-reviewer-brief.md](./references/blind-reviewer-brief.md). Give it the folder path only. Do not pass your conclusions, and do not let it read other assessments (name them in its blindness rules).
2. **Authority.** Read-only plus web search. No file writes, git, push, or sending. The orchestrator saves the report.
3. **Check what the reviewer can see.** A reviewer is only blind if the folder contains no prior review. List every assessment, red-team, or critique file in the folder (including ones written by other sessions) and name them in its blindness rules. If one cannot be hidden, record in the report that agreement on its topics is not independent.
4. **Require** exactly 10 reasons; two sections (Fixable Execution Risks, Fundamental Structural Flaws); each with evidence from the files, independent validation (source or shown arithmetic), confidence, tag, and the cheapest test that would change its mind. Borderline placement must be justified.
5. **Require** a verdict (pass, invest, pass-but-watch), the one thing that earns a meeting, and the 60-day proof list.
6. **Save** as a separate report in the idea's folder (for example `docs/validation/vc_skeptic_review.md`). Do not merge it into other assessments.
7. **Compare afterwards, not before.** Only after both are done, list agreements, disagreements, and findings unique to each. Disagreements are the best test targets.
8. **Verify the reviewer's claims.** Spot-check at least three of its cited facts; a confident reviewer can be wrong. Record the result.

## Guardrails

- Blindness is a rule, not a hope: state it in the brief and make the reviewer declare it on the first line of its output.
- Structural flaws are things money or time cannot easily fix. Execution risks are fixable within a quarter by a competent team. Do not downgrade a structural flaw to be kind.
- The reviewer's output is a critique, not a requirement. It changes no spec without the founder's decision.
- Check `git status` after the run to confirm nothing was written or pushed.
