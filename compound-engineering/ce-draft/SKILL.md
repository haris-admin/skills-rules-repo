---
name: ce-draft
description: "Shortcut for ce-brainstorm: drafts a vague or ambitious idea into a requirements-only plan (the WHAT) that ce-plan can build on. Use when the user says ce-draft, draft this, or scope what to build."
argument-hint: "[feature idea or problem to draft]"
---

# CE Draft (shortcut for ce-brainstorm)

A local shortcut, not an upstream skill. It exists so "draft" has a `ce-` name.

1. Invoke the `ce-brainstorm` skill through the Skill tool, passing these arguments through unchanged.
2. Follow `ce-brainstorm` exactly as loaded. Do not summarise or approximate it from this file.
3. If `ce-brainstorm` is not installed, stop and say so. Do not improvise a brainstorm workflow.

The usual chain is `ce-draft`, then `ce-plan`, then `ce-execute`.
