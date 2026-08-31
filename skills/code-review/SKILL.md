---
name: code-review
description: >-
  Conduct thorough, structured code reviews and diff analysis. Use when the user asks for a code review, PR audit, pull request feedback, or code quality inspection.
---

# Code Review & Quality Audit Skill

This skill guides the agent in conducting thorough, professional, and actionable code reviews across pull requests or modified files.

## Workflow

1. **Step 1: Inspect Changes & Context**
   - Run `git diff` or `git status` to identify modified, added, or deleted files.
   - Read the relevant source code and its surrounding context to understand the intent.

2. **Step 2: Evaluate Against Review Dimensions**
   - **Correctness & Logic**: Are there potential bugs, null pointers, off-by-one errors, or concurrency race conditions?
   - **Security**: Check for unvalidated inputs, SQL/command injection, hardcoded secrets, or insecure dependencies. (Consult [Review Checklist](./references/checklist.md)).
   - **Performance & Scalability**: Are there N+1 queries, memory leaks, unindexed database queries, or unneeded heavy iterations?
   - **Maintainability & Readability**: Is the code modular? Are variable and function names self-explanatory? Is dead code removed?
   - **Testing & Verification**: Are unit or integration tests included? Do they cover edge cases and failure paths?

3. **Step 3: Structure Review Feedback**
   - Categorize comments by severity:
     - 🔴 **Critical / Blocker**: Bugs, security vulnerabilities, breaking changes without migration.
     - 🟡 **Warning / Suggestion**: Performance improvements, test gaps, potential edge cases.
     - 🟢 **Nitpick / Optional**: Formatting, stylistic preference, minor naming improvements.
   - Always explain the reasoning and provide concrete code suggestions.

## Reference

- [Comprehensive Code Review Checklist](./references/checklist.md)
