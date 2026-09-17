---
name: executive-function-scaffolding
description: >-
  Scaffold executive function, overcome ADHD task paralysis, decompose overwhelming projects into 5 Pareto micro-steps, and engineer shame-free dopamine feedback loops. Use when breaking down complex assignments, structuring workflows for neurodivergent learners, calibrating time-blindness, designing streak-repair mechanics, or building behavioral features for platforms like Simplifii-OS.
---

# Executive Function & Dopamine Scaffolding Architecture

A behavioral engineering methodology designed to help neurodivergent learners and makers overcome task paralysis, manage activation energy, and maintain sustained focus without shame-based mechanics.

## When to Use

- **Simplifii-OS Onboarding & Cockpit**: When auto-decomposing ingested assessment briefs and rubrics into manageable timelines.
- **Task Paralysis Interventions**: When a user or student is frozen by the magnitude of a project, essay, or deliverable.
- **Habit & Streak Engineering**: When building progress tracking that encourages long-term retention without triggering the "all-or-nothing" drop-off.
- **Time Blindness Support**: When designing timers, estimation prompts, and pacing aids for neurodivergent thinkers.

---

## The 4 Pillars of Executive Scaffolding

```
┌─────────────────────────────────────────────────────────────┐
│ 1. THE ACTIVATION HURDLE: Lower initial barrier to <5 mins  │
├─────────────────────────────────────────────────────────────┤
│ 2. PARETO 5-STEP DECOMPOSITION: Maximum 5 micro-actions     │
├─────────────────────────────────────────────────────────────┤
│ 3. SHAME-FREE DOPAMINE LOOPS: Micro-wins and streak repair  │
├─────────────────────────────────────────────────────────────┤
│ 4. TEMPORAL CALIBRATION: Visual elapsed time vs numerical   │
└─────────────────────────────────────────────────────────────┘
```

---

## Pareto Task Decomposer CLI

Run the bundled CLI tool to automatically decompose an overwhelming assignment into 5 low-load micro-steps:

```bash
# Decompose an essay or assessment task
python3 growth/executive-function-scaffolding/scripts/pareto_task_decomposer.py \
  --task "BUS302 Corporate Governance Case Study" \
  --type essay

# Decompose a startup MVP build
python3 growth/executive-function-scaffolding/scripts/pareto_task_decomposer.py \
  --task "Build MVP for Simplifii Concept Visualiser" \
  --type startup_mvp

# Output JSON for agentic pipelines or UI rendering
python3 growth/executive-function-scaffolding/scripts/pareto_task_decomposer.py \
  --task "Quarterly Compliance Filing" \
  --type generic \
  --json
```

See [pareto_task_decomposer.py](./scripts/pareto_task_decomposer.py) for the underlying logic.

---

## Dopamine & Behavioral Guardrails

1. **The 5-Minute Rule for Step 1**: The first action of any task must require fewer than 5 minutes of effort (e.g., creating a file, copy-pasting a rubric, or typing 3 bullet points). Once physical motion begins, activation inertia drops dramatically.
2. **Never Reset Streaks to Zero**: When a user misses a daily check-in, never display red warning badges or zero out their counter. Offer a "grace day" or automatic freeze to preserve self-efficacy.
3. **No Guilt Language**: Replace "You are 3 days late" with "Ready to dive back in? Let's tackle Step 1 together."

For detailed behavioral mechanisms, consult the [Dopamine Architecture Playbook](./references/dopamine-architecture-playbook.md).
