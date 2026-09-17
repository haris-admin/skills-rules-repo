---
name: market-sizing-tam-sam-som
description: >-
  Calculate, model, and sanity-check Total Addressable Market (TAM), Serviceable Addressable Market (SAM), and Serviceable Obtainable Market (SOM) using bottom-up unit economics, top-down validation, and sensitivity scenarios. Use when sizing market opportunities, preparing investor pitch decks, modeling revenue scale, or evaluating expansion segments for ventures like AML Hive, TAPEase, Undispute, or Simplifii.
---

# Market Sizing Architecture (TAM / SAM / SOM)

A quantitative, defensible framework for bottom-up market sizing, addressable customer filtering, and 3-year revenue capture modeling across startup ventures.

## When to Use

- **Pitch Decks & Investor Memos**: When justifying market scale, upside potential, and near-term revenue targets.
- **New Feature or Segment Evaluation**: When assessing whether an adjacent customer segment (e.g., UK expansion, secondary schools, enterprise tiers) is large enough to justify product development.
- **Pricing & Packaging Strategy**: When simulating how changes to Annual Contract Value (ACV) impact the addressable market ceiling.
- **Venture Due Diligence**: When sanity-checking founder claims against verifiable registrar and industry data.

---

## The Three Tiers of Market Sizing

```
┌─────────────────────────────────────────────────────────────┐
│                 TAM (Total Addressable Market)              │
│       Total Account Universe × Annual Contract Value (ACV)  │
│  ┌───────────────────────────────────────────────────────┐  │
│  │             SAM (Serviceable Addressable Market)      │  │
│  │       TAM Filtered by Geography, Tech Stack, & Reach  │  │
│  │  ┌─────────────────────────────────────────────────┐  │  │
│  │  │          SOM (Serviceable Obtainable Market)    │  │  │
│  │  │       Defensible 24–36 Month Capture (2% – 10%) │  │  │
│  │  └─────────────────────────────────────────────────┘  │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

---

## Rapid Market Sizing CLI

Use the bundled calculator script to model bottom-up scenarios and sensitivity ranges:

```bash
# Model AML Hive compliance market (preset)
python3 growth/market-sizing-tam-sam-som/scripts/calculate_market_size.py --preset amlhive

# Model Tapease merchant payments (preset)
python3 growth/market-sizing-tam-sam-som/scripts/calculate_market_size.py --preset tapease

# Model Simplifii-OS neurodivergent student ecosystem (preset)
python3 growth/market-sizing-tam-sam-som/scripts/calculate_market_size.py --preset simplifii

# Model Undispute pre-dispute resolution network (preset)
python3 growth/market-sizing-tam-sam-som/scripts/calculate_market_size.py --preset undispute

# Custom bottom-up parameters with JSON export
python3 growth/market-sizing-tam-sam-som/scripts/calculate_market_size.py \
  --tam-accounts 120000 \
  --acv 2400 \
  --sam-pct 0.25 \
  --som-pct 0.04 \
  --json
```

See [calculate_market_size.py](./scripts/calculate_market_size.py) for the complete scenario engine.

---

## Methodological Guardrails

1. **Strict Bottom-Up Priority**: Always build calculations from $(\text{Verified Entity Count}) \times (\text{Realistic ACV})$. Never multiply a generic global consulting report by an arbitrary percentage.
2. **Triangulate Against Value Created**: Ensure the proposed ACV captures no more than 20% to 50% of the quantifiable annual financial savings or net revenue generated for the buyer.
3. **Conservative SOM Discipline**: Cap year-3 SOM at realistic sales pipeline bandwidth (typically 2% to 10% of SAM in fragmented markets).

Consult the [TAM / SAM / SOM Methodology Guide](./references/tam-sam-som-methodology-guide.md) for data sources and filtering mechanics, and see [Market Sizing Pitch Templates](./references/market-sizing-pitch-templates.md) for presentation blueprints.
