---
name: subagent-verification
description: Verification protocol for orchestrator agents when managing parallel worker subagents.
---

# Subagent Verification Protocol

## Protocol
1. **Never Trust Self-Reports Alone**: When a subagent reports completion, verify its work directly via `git status --short -- <paths>` and by running the tests yourself.
2. **Scope Verification**: Verify that the subagent modified ONLY files within its assigned scope. Revert out-of-lane edits immediately.
3. **Evidence-Based Completion**: A task is done only when real test command execution output confirms it passes.

