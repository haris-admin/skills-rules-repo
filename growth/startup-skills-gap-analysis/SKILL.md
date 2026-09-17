---
name: startup-skills-gap-analysis
description: >-
  Audit, map, and remediate startup team capabilities against strategic milestone requirements (MVP, Seed, Series A, Compliance Audit). Use when assessing founder/team competency gaps, identifying bus-factor vulnerabilities, deciding between hiring, upskilling, fractional experts, or AI agent automation, or building a headcount roadmap for venture milestones.
---

# Startup Skills Gap Analysis & Capability Architecture

A diagnostic framework for assessing startup team competencies, isolating single-point-of-failure vulnerabilities, and selecting capital-efficient remediation pathways (**Automate via AI Agents**, **Fractional Experts**, **Upskilling**, or **Full-Time Hiring**).

## When to Use

- **Milestone Preparation**: When planning headcount and competencies required to reach the next venture milestone (e.g. Seed round, AUSTRAC compliance audit, Series A).
- **Key-Person Risk Audits**: When identifying single points of failure (bus factor = 1) across critical infrastructure, regulatory compliance, or sales operations.
- **Build vs. Buy vs. Automate Decisions**: When deciding whether an operational gap warrants a senior full-time salary or can be solved via autonomous agent fleets or fractional experts.
- **Fundraising Due Diligence**: When articulating team capability roadmaps to venture capital investors or board directors.

---

## The 4-Step Capability Audit Workflow

```
  ┌────────────────────────────────────────────────────────┐
  │         1. DEFINE MILESTONE CAPABILITY BENCHMARKS      │
  │     Seed · Series A · Regulatory Compliance Audit      │
  └───────────────────────────┬────────────────────────────┘
                              │
                              ▼
  ┌────────────────────────────────────────────────────────┐
  │         2. EVALUATE CURRENT TEAM MATURITY (1–5)        │
  │    Engineering · AI Ops · Compliance · GTM · Finance   │
  └───────────────────────────┬────────────────────────────┘
                              │
                              ▼
  ┌────────────────────────────────────────────────────────┐
  │         3. QUANTIFY DELTAS & ISOLATE CRITICAL GAPS     │
  │           Prioritize Gaps ≥ 2 as Vulnerabilities       │
  └───────────────────────────┬────────────────────────────┘
                              │
                              ▼
  ┌────────────────────────────────────────────────────────┐
  │         4. SELECT REMEDIATION PATHWAY                  │
  │    Automate (AI) · Fractional · Upskill · Full-Time    │
  └────────────────────────────────────────────────────────┘
```

### 1. Score Maturity Levels (1 to 5)
- **1**: Absent (Critical blind spot)
- **2**: Basic (Ad-hoc, high oversight required)
- **3**: Competent (Independent daily execution)
- **4**: Advanced (Deep mastery, high velocity)
- **5**: World-Class (State-of-the-art capability)

### 2. Apply the Remediation Matrix
- **Automate with AI Agents**: High repetition, code/text tasks, data extraction, test suites $\rightarrow$ deploy agent tooling (Hermes, Codex, Antigravity) at near-zero variable headcount cost.
- **Engage Fractional Specialist**: High technical/regulatory complexity with low ongoing volume (e.g. AML/CTF legal review, tax structuring) $\rightarrow$ retain 10–20 hrs/mo expert.
- **Upskill Internal Talent**: Strategic capability where internal talent already possesses 60%+ prerequisite context $\rightarrow$ dedicated 2-4 week sprint.
- **Full-Time Hire**: Permanent, core competitive moat of the company $\rightarrow$ draft formal role scorecard.

---

## Capability Gap Analyzer CLI

Run the audit tool to benchmark team capabilities against milestone profiles:

```bash
# Audit against compliance audit readiness
python3 growth/startup-skills-gap-analysis/scripts/analyze_skills_gap.py --milestone compliance_audit

# Audit against Series A scaling requirements
python3 growth/startup-skills-gap-analysis/scripts/analyze_skills_gap.py --milestone series_a

# Output JSON for executive dashboards
python3 growth/startup-skills-gap-analysis/scripts/analyze_skills_gap.py --json
```

---

## References & Frameworks

- [Startup Capability Matrix Template](./references/capability-matrix-template.md) — Scoring rubric across 7 core functional startup domains.
- [Gap Remediation Decision Framework](./references/gap-remediation-framework.md) — 4-quadrant criteria for choosing between AI agents, fractional specialists, upskilling, and full-time hiring.
