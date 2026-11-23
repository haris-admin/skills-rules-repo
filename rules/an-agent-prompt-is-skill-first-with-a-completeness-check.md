# An agent prompt is skill first and carries a completeness check

Applies to any prompt that drives a research or worker agent (HandleDispute Hermes, 18 Nov 2026).

**Scope:** prompts and skills for agents that claim jobs and return structured results.

---

## Why this exists

A Hermes run found the legal entity but left leadership, the dispute contact and the sign-up contact empty without saying so, learned three payload rules by being rejected (`422`), had its claim body cut off by its own terminal capture, and never submitted the full report, so production held a completed job and no report. The long prompt had the detail but the agent did not apply it.

## Core Directives

1. **Keep the prompt short and put procedure in skills.** The prompt tells the agent to load the named skills first, lists the rules that must never be skipped and gives the finish order. Detail lives in the skills, in one place.
2. **Include a completeness check in the prompt.** For each candidate and each area the agent states a coverage state. Any empty area is work the agent has not done: it goes back and does it, or records an honest not-checked or no-evidence state with a reason and the sources searched.
3. **Teach payload rules before submission, not through rejection.** The skill carries a table of the rules the API enforces and a worked example that a test validates against the real validator.
4. **Read the claim from a file.** Never decide from a terminal capture that may be cut off.
5. **A report failure must not lose the job.** Retry, then still complete with a note, so a person sees the gap.
6. **The agent never contacts anyone or prints a secret.** State this in the prompt, not only in a skill.
7. **Test the documents.** Tests read the prompt and skills for the required sections and validate the example report with the backend validator, so a change to either that breaks the contract fails a build.
