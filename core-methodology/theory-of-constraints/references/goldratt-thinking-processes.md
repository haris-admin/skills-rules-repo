# Goldratt's Thinking Processes & The Evaporating Cloud

In addition to physical bottleneck analysis, Goldratt developed the **Thinking Processes** to resolve systemic policy constraints and conflicting business requirements.

---

## 1. The Three Fundamental Management Questions

1. **What to change?** (Identify the core conflict using the Current Reality Tree).
2. **What to change to?** (Develop simple, win-win solutions using the Evaporating Cloud).
3. **How to cause the change?** (Build implementation roadmaps using the Transition Tree).

---

## 2. The Evaporating Cloud (Conflict Resolution Diagram)

Most operational gridlock in software engineering arises from two seemingly irreconcilable requirements serving the same high-level objective:

```
                                 ┌───────────────────────────────┐
                                 │       B. REQUIREMENT 1        │──► D. PREREQUISITE 1
                                 │   Move Fast & Ship Daily      │    Deploy without long tests
 ┌───────────────────────────┐   └───────────────▲───────────────┘             ▲
 │     A. COMMON OBJECTIVE   │                   │                             │ CONFLICT:
 │  Build a High-Growth SaaS │                   │                             │ Must deploy fast vs
 └───────────────────────────┘                   │                             │ Must not break prod
                                 ┌───────────────▼───────────────┐             ▼
                                 │       C. REQUIREMENT 2        │──► D'. PREREQUISITE 2
                                 │ Maintain 99.9% Uptime/Security│    Mandate 3-day manual QA
                                 └───────────────────────────────┘
```

### How to "Evaporate" the Cloud:
Examine the hidden assumptions linking the requirements to the conflicting prerequisites:
- *Assumption*: "To maintain uptime (C), we must mandate 3-day manual QA (D')."
- *Shatter the Assumption*: If we deploy **automated ephemeral integration environments, strict test gates (`validate.py`), and atomic rollback capabilities**, we satisfy Requirement C *without* the 3-day manual delay.
- The conflict evaporates into a superior synthesis.
