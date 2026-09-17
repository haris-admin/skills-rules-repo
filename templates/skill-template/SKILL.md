---
name: my-skill-name
description: >-
  Describe precisely when the agent should activate this skill. State the triggers and goals clearly in third person (e.g. "Use when...", "Trigger on..."). Limit to 1024 characters.
---

# Skill Name

Brief overview of the skill purpose, core workflow, and outcomes. Keep this file under 500 lines; push heavy specs into `references/`.

## When to Use

- Use when the user asks to...
- Trigger when diagnosing or performing...
- Do NOT use when... (boundary condition)

## Step-by-Step Procedure

1. **Step 1: Preparation & Preflight**
   - Describe initial environment checks, required flags, or read-only commands.
2. **Step 2: Core Execution**
   - Detailed, idempotent instructions for carrying out the task.
3. **Step 3: Verification**
   - How to verify that the task completed accurately without side effects or regressions.

## Best Practices & Guardrails

- **Key Directive 1**: Critical behavior or safety constraint.
- **Key Directive 2**: Edge cases or gotchas.
- **Progressive Disclosure**: Link to [reference guide](./references/guide.md) for full API schemas, error codes, and configuration options.
