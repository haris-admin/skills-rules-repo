---
name: ce-execute
description: "Shortcut for ce-work: executes a plan or concrete work prompt end to end with local verification. Use when the user says ce-execute, execute the plan, or build this plan."
argument-hint: "[plan path, work description, or blank for the latest plan]"
---

# CE Execute (shortcut for ce-work)

A local shortcut, not an upstream skill. It exists so "execute" has a `ce-` name.

1. Invoke the `ce-work` skill through the Skill tool, passing these arguments through unchanged.
2. Follow `ce-work` exactly as loaded. Do not summarise or approximate it from this file.
3. If `ce-work` is not installed, stop and say so. Do not improvise an execution workflow.

Project rules still win: where a repo says pushing or deploying needs a separate go, `ce-work` stops at the local commit and asks.
