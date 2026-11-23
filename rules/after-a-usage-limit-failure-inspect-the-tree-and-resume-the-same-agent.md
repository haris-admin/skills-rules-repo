# After a usage-limit failure, inspect the tree and resume the same agent

A subagent that stops on a usage limit has already saved its work. Do not start a new agent over it.

**Scope:** an orchestrating agent running several background agents.

---

## Core Directives

1. **Inspect each worktree first**: `git log --oneline -3`, `git status --short`, and any test containers it left.
2. **Resume with a message** to the same agent, saying what is saved and telling it not to redo finished work; keep its original limits.
3. **Clean up after.** Its own containers are removed by exact name by that agent; check the lists before and after.

## Why this exists

**23 Nov 2026 (SonoVantage):** three agents (database plan revision 7, shared services, legal pages) failed on a 5-hour limit with commits and uncommitted files on disk; all three were resumed and finished without repeated work.
