# Check for a parallel session before building a fix in a shared repo (all agents)

Applies before an agent creates a branch or worktree to fix an incident in a repository that other agents or sessions also use.

## Why this exists

Tap-Ease, 9 Nov 2026. While the backend session investigated the Clover 403, another session was building the Lambda fix. Both reached the same one-field change. The
other session released it as Lambda 0.10.15 (`cc209a2`, with its own spec, tests and RCA) while this session built a duplicate in a new worktree. Nothing broke,
because the owner deployed the other one, but the duplicate was wasted work and a second set of docs. `git worktree list` and `git fetch` would have shown the other session's
`release/0.10.15-extended-expand` worktree and branch before any code was written.

## Rule

1. Before building a fix: `git fetch`, `git worktree list`, `git branch -a`, and `git log origin/<main> -5`. Look for a branch, worktree or commit on the same topic.
2. If another session is on it, say so and ask Haris who owns it. Offer verification and review instead of a second implementation.
3. If the owner says "I'm deploying it" or similar, stop and verify theirs (version in the live log, the failing lines gone, payments processed) rather than shipping a copy.
4. At closeout, compare any duplicate with the released version and remove only your own, once the equivalence is shown.

## How to apply

Run the three git commands at the start of any incident fix in a repo that is not yours alone. Related: `subagent-branch-verification-and-merge-hygiene.md`, `deletion-precheck-untracked-and-referenced.md`.
