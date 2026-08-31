---
name: codebase-memory
description: Build and query a persistent mental model of the codebase — architecture, patterns, dependencies, and conventions — so future work starts informed, not cold.
---

# Codebase Memory Skill

## When to use
Invoke when starting a new session, onboarding to an unfamiliar area of the codebase, or when context about architecture and conventions would prevent mistakes.

## What to capture

### Architecture Map
- Core modules and their responsibilities (SovereignRouter, ExecutiveSpine, HistoryOfThought, LiteralMode, EventBus).
- Component hierarchy and data flow patterns.
- Which modules talk to each other and through what interfaces.

### Conventions
- Naming patterns (files, components, functions, CSS classes).
- Import ordering and module resolution.
- State management approach (localStorage, IndexedDB, React state).
- Error handling patterns used in the codebase.

### Dependencies
- Key npm packages and their roles.
- Internal module dependency graph (who imports whom).
- External service integrations (Ollama, IndexedDB).

### Gotchas
- Known quirks, workarounds, or technical debt.
- Areas where the code does something unexpected.
- Performance-sensitive paths.

## Workflow

1. **Scan.** Read CLAUDE.md, package.json, and the `src/core/` directory to build the top-level map.
2. **Explore.** Use Glob and Grep to trace key patterns — EventBus subscribers, Router routes, Spine event handlers.
3. **Record.** Save findings to the auto-memory system (`~/.claude/projects/.../memory/`) using appropriate memory types:
   - Architecture decisions → `project` type memories.
   - Conventions and patterns → `feedback` type memories (so they guide future behaviour).
   - External references → `reference` type memories.
4. **Query.** When asked about the codebase, check memory first, then verify against current code before answering.

## Rules
- Memory is a cache, not truth. Always verify against the live codebase before acting on a memory.
- Do not memorise things derivable from a quick grep — only save non-obvious insights.
- Keep memories concise. One memory per topic. Update rather than duplicate.
- Never store secrets, credentials, or personal data in memory files.
