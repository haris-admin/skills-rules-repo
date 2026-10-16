# Concurrent-Session Decision Conflicts

When more than one agent session shares the same repo/workspace and works on overlapping specs at
the same time, each session can independently ask the same human the same open question — and get
two different answers, because the human didn't realize it was the same question twice.

## Core Directives

1. **Before asking the human a decision, check whether another session already recorded one for
   the same open item** (grep the artifact's own change log / decision section, not just your own
   context). A decision already on record is not yours to re-ask unless you have reason to think
   it's stale.
2. **When you find a decision in a shared artifact that another session recorded and it conflicts
   with an answer you were just given, stop and surface the conflict explicitly** — name both
   answers, name where each came from, and ask the human to pick one. Do not silently prefer either
   side, and do not average or hedge between them.
3. **Once resolved, record the resolution as a new dated entry that supersedes the earlier one** —
   append-only, never edit the superseded entry away — so a third session (or a later read of the
   same one) sees the conflict happened and how it was settled, not just the final answer.

## Patterns to Avoid

```text
# Bad: silently picking your own session's answer when a conflicting
# decision already exists in the artifact you're about to build against.
```

## Patterns to Follow

```text
# Good: "Change X's own decision log says A; you just told me B for the
# same question. Which is correct?" — then record the answer as a new,
# explicitly-superseding entry.
```

## Lessons 16 Oct 2026 (concurrent sessions under the human's identity)

- A concurrent session may commit under the human's git identity (a Codex session committed a re-check report and three status lines while this session ran). Read what it changed before relying on or contradicting it, report it to the human, and never undo or rewrite it. Its verdict is a second opinion, not a substitute for your own independent review.
- Do not delete shared test-service state you cannot attribute. Eight stray queue entries from one run were indistinguishable from forty-nine others in a shared local Redis, so cleanup was withheld and the human asked.
