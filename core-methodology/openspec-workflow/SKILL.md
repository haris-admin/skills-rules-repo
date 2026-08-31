---
name: openspec-workflow
description: Structure complex multi-agent features into structured proposals, design documents, executable tasks, and verification gates.
---

# OpenSpec Workflow

## Standard Lifecycle
1. **`proposal.md`**: Problem statement, scope boundaries, user value, observability requirements, and breaking changes.
2. **`design.md`**: Architectural diagram, data models, API contracts, migration strategy, error handling, and alternative options evaluated.
3. **`tasks.md`**: Atomically sequenced checklist with clear acceptance criteria and verification commands.
4. **Implementation Plan Gate**: For significant changes, author `implementation_plan.md`, present 2-3 evaluated options, and obtain user approval before writing code.
5. **Closeout & Verification**: Verify all task criteria with real command output and evidence before marking a change implemented.

