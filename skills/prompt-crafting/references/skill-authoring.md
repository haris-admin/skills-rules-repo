# Skill & Rule Authoring Best Practices

## Frontmatter Guidelines
- `name`: Must match the directory name (lowercase and hyphenated, e.g., `code-review`).
- `description`: Single multiline string (using `>-`). Must clearly state **what** the skill does and **when** to activate it.

## Anatomy of a Skill
```text
skills/<skill-name>/
├── SKILL.md          # Required: Main entry point with frontmatter
├── scripts/          # Optional: Executable shell/Python utilities
├── references/       # Optional: In-depth checklists, API docs, schemas
└── examples/         # Optional: Sample inputs/outputs
```

## Golden Rules
1. **Never explain basic syntax**: Assume the AI model already knows language fundamentals.
2. **Be procedural**: Use numbered steps, checklists, and explicit commands.
3. **Keep it lean**: Less is more. Concise prompts reduce token consumption and improve instruction adherence.
