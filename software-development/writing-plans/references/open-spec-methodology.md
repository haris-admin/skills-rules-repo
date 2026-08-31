# Open Spec: Component-First Design Methodology

**Version:** 1.0 | **Date:** 2026-05-29 | **Created by:** Pluto (from ExitLens AU build)

## When to Use

Before writing ANY code, produce an Open Spec — a component-by-component breakdown with:
- Component inventory (numbered C1-CN)
- Each component's file path, dependencies, what it does, acceptance criteria
- Dependency graph showing build order
- TDD build order (which component to build first, what tests to write)

## Why Open Spec

Traditional plans describe *tasks* ("build authentication"). Open Spec describes *components* ("C3: Scenario Service — file: backend/app/services/scenario_service.py, depends on C2+C5, acceptance: saves scenario with all fields").

This matters because:
- Components are stable; tasks are fluid
- Dependencies between components dictate build order
- Each component has clear acceptance criteria (testable)
- The dependency graph prevents "I need X but X isn't built yet"

## Open Spec Structure

### Component Inventory

```
Project Name
├── BACKEND — N components
│   ├── C1: Name — File — What it does
│   ├── C2: Name ★ CORE — File — What it does
│   └── ...
├── FRONTEND — N components
│   ├── C8: Name — File — What it does
│   └── ...
└── INFRA — N components
    └── ...
```

### Per-Component Specification

Every component gets:

```markdown
### C{N}: Component Name [★ CORE if critical]

**File:** `exact/path/to/file.py`
**Depends on:** C{X}, C{Y} (or "Nothing" if entry point)
**Tests:** `tests/path/test_file.py`

**What it does:**
One paragraph. Pure function? API endpoint? React component? Database table?

**Acceptance:**
- [ ] Specific, testable criterion
- [ ] Another criterion

**TDD Order:** Write test_first, then implement.
```

### Dependency Graph

```
C17 (Infra)
  └─ C5 (DB Layer)
       ├─ C3 (Service)
       │    ├─ C2 (Engine ★)
       │    └─ C6 (Router)
       │         └─ C9 (Page)
       │              ├─ C10 (Component)
       │              └─ C11 (Component)
       └─ C4 (Generator)
            └─ C7 (Router)
```

### TDD Build Order

Numbered list with time estimates:
```
1. C16 — Types (5 min)
2. C17 — Docker (10 min)
3. C5 — DB Layer (15 min)
4. C2 ★ — Core Engine (30 min)
...
16. C14 — Download Button (10 min)
Total: ~4.5 hours
```

## Example: ExitLens AU Open Spec

ExitLens had 17 components across 3 layers:

| Layer | Count | Example |
|-------|-------|---------|
| Backend | 7 | C2: CGT Calculator Engine ★, C6: Calculator Router |
| Frontend | 9 | C10: Input Form, C11: Comparison Table |
| Infra | 1 | C17: Docker Compose (PG :5436) |

The dependency graph showed C2 (calculator engine) was the critical path — everything else depends on it. So C2 was built first with full TDD (15 tests).

## Relationship to `writing-plans`

`writing-plans` produces bite-sized task lists. Open Spec produces the component architecture that those task lists implement. Use them together:

1. **Open Spec first** — define ALL components, dependencies, build order
2. **Architecture doc** — PlantUML diagrams, tech rationale, data model
3. **Security audit** — OWASP + ASD E8 before any code
4. **Then `writing-plans`** — break each component into bite-sized TDD tasks
