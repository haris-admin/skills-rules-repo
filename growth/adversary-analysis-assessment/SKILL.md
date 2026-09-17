---
name: adversary-analysis-assessment
description: >-
  Conduct adversary assessments, competitive threat analyses, and defensibility audits using Hamilton Helmer's 7 Powers framework, incumbent retaliation modeling ('Can't vs Won't' test), and competitive battlecards. Use when mapping competitor landscapes, evaluating defensibility against market incumbents, positioning against customer inertia or Excel, or preparing strategic counter-arguments for sales and investor pitches.
---

# Adversary Analysis & Strategic Defensibility Architecture

A rigorous diagnostic framework to analyze competitors, incumbents, and customer inertia using Hamilton Helmer's **7 Powers**, incumbent retaliation economics, and asymmetric attack positioning.

## When to Use

- **Competitive Landscape Mapping**: When identifying who currently solves the customer's problem (direct rivals, indirect substitutes, and status quo workarounds).
- **Defensibility Audits (7 Powers)**: When determining what prevents an incumbent or well-funded clone from copying your product.
- **Sales Battlecards & Positioning**: When equipping go-to-market teams to win against established category leaders.
- **Investor Due Diligence**: When articulating your startup's sustainable economic moat beyond superficial feature comparisons.

---

## The Adversary Spectrum

In early-stage startups, your most dangerous competitor is rarely another startup; it is **Customer Inertia**:

```
┌─────────────────────────────────────────────────────────────┐
│                 THE PRIMARY ADVERSARIES                     │
├─────────────────────────────────────────────────────────────┤
│ 1. THE STATUS QUO: Excel, paper, email, or "doing nothing"  │
│ 2. LEGACY INCUMBENTS: Bloated platforms with high fees      │
│ 3. DIRECT ENTRANTS: Clones and adjacent venture-backed tools│
└─────────────────────────────────────────────────────────────┘
```

---

## The 7 Powers Defensibility Audit

Run the bundled CLI audit to evaluate venture defensibility across all 7 Powers:

```bash
# Run audit on AML Hive compliance preset
python3 growth/adversary-analysis-assessment/scripts/seven_powers_audit.py --preset amlhive

# Run audit on Tapease payments preset
python3 growth/adversary-analysis-assessment/scripts/seven_powers_audit.py --preset tapease

# Run audit on Simplifii-OS neuroinclusive workspace
python3 growth/adversary-analysis-assessment/scripts/seven_powers_audit.py --preset simplifii

# Run audit on Undispute pre-dispute resolution network
python3 growth/adversary-analysis-assessment/scripts/seven_powers_audit.py --preset undispute

# Export machine-readable audit JSON
python3 growth/adversary-analysis-assessment/scripts/seven_powers_audit.py --preset undispute --json
```

See [seven_powers_audit.py](./scripts/seven_powers_audit.py) for scoring mechanics.

---

## Incumbent Retaliation: The "Can't vs Won't" Rule

When evaluating why an incumbent will or will not crush your startup:
1. **The "Can't" Barrier**: Incumbents are paralyzed by legacy tech debt, regulatory approvals, or bloated processes.
2. **The "Won't" Barrier (Counter-Positioning)**: An incumbent refuses to match your model because doing so would destroy their high-margin cash cow (e.g., banks abandoning dispute penalties or law firms abandoning hourly billing).

For the complete theoretical breakdown, consult the [7 Powers Framework Guide](./references/seven-powers-framework-guide.md). For tactical sales battlecards and objection handling, see the [Competitive Battlecard Template](./references/competitive-battlecard-template.md).
