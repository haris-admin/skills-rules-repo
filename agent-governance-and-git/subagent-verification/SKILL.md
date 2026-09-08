---
name: subagent-verification
description: Verification protocol for orchestrator agents when managing parallel worker subagents.
---

# Subagent Verification Protocol

## Protocol
1. **Never Trust Self-Reports Alone**: When a subagent reports completion, verify its work directly via `git status --short -- <paths>` and by running the tests yourself.
2. **Scope Verification**: Verify that the subagent modified ONLY files within its assigned scope. Revert out-of-lane edits immediately.
3. **Evidence-Based Completion**: A task is done only when real test command execution output confirms it passes.
4. **A consistency-scanner's "majority" is a display heuristic, not a verdict.** A tool that flags
   outliers-vs-majority within a group can have the direction backwards — if the bug itself has
   become common enough, the tool reports the *correct* remaining cases as the outliers and the
   *buggy* cases as "the majority." Cross-check against the actual documented rule, not the vote
   count.
5. **Re-verify every cited file:line before trusting it, and check every place a rule can live.**
   A subagent's citation can be stale (the code moved), fabricated (the function never existed), or
   incomplete (it checked one enforcement location — e.g. a function's default parameter — and
   missed a second one — e.g. the same guard applied via a decorator/wrapper instead). Confirm
   against live source, not the subagent's confidence.
6. **A rate-limited / `failed` subagent has usually already written most of its files — resume it,
   don't cold re-dispatch.** Check disk first (`git status --short` + `wc -l` on its scoped paths),
   then `SendMessage` to its id with a "finish exactly these gaps" instruction. Full detail:
   `rules/subagent-verification-protocol.md` rule 6.
7. **A parallel session may have committed the same work while your subagents ran** (multi-device,
   Remote Control, teammates). Before you write or commit a rollup/index doc (README, CHANGELOG,
   a master index), run `git log --oneline -5` and `git show HEAD:<path>` for anything you're
   about to overwrite. Converged per-target subagent outputs are usually byte-identical and safe;
   the hand-authored rollups are where a thinner write clobbers a richer committed one — if that
   happens, `git checkout HEAD -- <path>` and re-apply only your genuine additions. See also
   `rules/shared-file-commit-resolution.md`.

