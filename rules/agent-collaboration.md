# Agent Collaboration & Pair Programming Guidelines

Guidelines for AI agents (Antigravity, Claude, Cursor, Windsurf) working with human engineers and multi-agent systems.

## Collaboration Protocols

1. **Context Discovery First**:
   - Always inspect existing project architecture, styling, and coding patterns before writing code.
   - Locate and read `.agents/rules/`, `GEMINI.md`, `AGENTS.md`, or relevant skill definitions.

2. **Progressive Disclosure**:
   - Keep primary instructions lightweight and delegate deep domain runbooks to specialized skills.
   - Load full skill and documentation references only on demand to preserve context window capacity.

3. **Verifiable Execution**:
   - Run tests, builds, and validation checks to verify modifications before concluding tasks.
   - Provide concise, clickable references to modified files and clear next steps for the developer.
