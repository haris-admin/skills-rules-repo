---
name: git-workflow
description: >-
  Manage git operations, semantic commit generation, atomic branch creation, and PR descriptions. Use when the user asks to create commits, make a branch, craft a pull request, or resolve git operations.
---

# Git Workflow & Commit Generator Skill

Guides the agent in executing clean, atomic, and standardized Git workflows.

## Workflow

1. **Step 1: Check Current Git Status**
   - Run `git status` to identify modified, untracked, or staged files.
   - Run `git diff --staged` (or `git diff`) to review exact line changes.

2. **Step 2: Stage Atomic Changes**
   - Group related files logically instead of indiscriminately doing `git add .`.
   - Ensure temporary, generated, or secret files are not staged.

3. **Step 3: Draft Semantic Commit Messages**
   - Follow the Conventional Commits standard (see [Conventional Commits Guide](./references/conventional-commits.md)).
   - Format: `<type>(<scope>): <short summary in imperative mood>`
   - If the change is non-trivial, include a body explaining the rationale.

4. **Step 4: PR & Branch Management**
   - When preparing a pull request, summarize:
     - **Summary of Changes**
     - **Motivation & Context**
     - **Testing / Verification Performed**
     - **Screenshots / Logs** (if visual or CLI output)

## Reference

- [Conventional Commits Specification Reference](./references/conventional-commits.md)
