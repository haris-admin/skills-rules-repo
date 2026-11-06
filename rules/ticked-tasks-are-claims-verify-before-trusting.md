# A ticked task is a claim, not evidence

A checked box in `tasks.md`, a `Resolved` status or an agent's report is a claim. Verify it against a test, a file path or a command before relying on it or building on it.

**Scope:** all agents and reviewers working from OpenSpec tasks, issue files, release notes and subagent reports.

---

## Core Directives

1. **Check the artefact**: for each ticked task, find the test that cites it or the file that implements it; if neither exists, reopen the task and say so.
2. **Reopen, do not rewrite history**: mark undelivered tasks "NOT DELIVERED" with a pointer to the amendment that delivers them.
3. **Re-run, do not trust a self-report**: re-run the cited verification command on the merged tree before saying "done".
4. **Say what you could not verify**: name the check that was blocked and who can run it.

## Why this exists

**6 Nov 2026 (HandleDispute):** OpenSpec 31 tasks 2.4 to 2.6 (verify endpoint, admin audit screen, self-service views) were ticked, but a read-only comparison found no code behind them. The merchant screen showed hard-coded sample data with fake hashes.
