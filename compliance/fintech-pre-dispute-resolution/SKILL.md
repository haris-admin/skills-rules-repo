---
name: fintech-pre-dispute-resolution
description: >-
  Manage scheme-neutral transaction disputes, 48-hour pre-chargeback resolution workflows, and 3-sided network SLAs across cardholders, merchants, and issuing banks (Visa, Mastercard, Eftpos). Use when building pre-dispute networks, implementing Visa CE 3.0 or Ethoca/Verifi workflows, reducing merchant chargeback penalty fees, or automating dispute refunds for platforms like Undispute.
---

# FinTech Pre-Dispute Resolution & Scheme Neutrality Architecture

An operational and compliance architecture for 3-sided pre-dispute networks connecting **Cardholders**, **Merchants**, and **Issuing Banks** to amicably resolve payment conflicts within a 48-hour pre-chargeback grace period.

## When to Use

- **Undispute Platform Engineering**: When building backend transaction webhook pipelines, dispute state machines, or issuer SLAs.
- **Merchant Chargeback Reduction**: When auditing merchant payment accounts facing excessive chargeback ratio thresholds (>0.9% MID risk).
- **Scheme Integration Workflows**: When integrating Visa Compelling Evidence 3.0 (CE 3.0), Mastercard Ethoca, or Verifi CDRN webhooks.
- **Friendly Fraud Remediation**: When designing automated refund triggers that eliminate the non-refundable $35–$50 scheme fee.

---

## The 3-Sided Pre-Dispute Architecture

```
                    ┌───────────────────────────────────┐
                    │      ISSUING BANK / CARDHOLDER    │
                    │   Flags unrecognised transaction  │
                    └─────────────────┬─────────────────┘
                                      │
                                      ▼
                        ┌───────────────────────────┐
                        │   UNDISPUTE 48H WINDOW    │
                        │ Scheme Neutral Mediation  │
                        └─────────────┬─────────────┘
                                      │
                                      ▼
                    ┌───────────────────────────────────┐
                    │        MERCHANT (MID PROTECTED)   │
                    │ Auto-refund or Compelling Evidence│
                    └───────────────────────────────────┘
```

---

## Financial Savings CLI

Run the bundled calculator to forecast merchant fee savings and dispute ratio mitigation:

```bash
# Run demonstration calculation for average Australian SMB
python3 compliance/fintech-pre-dispute-resolution/scripts/dispute_sla_calculator.py --demo

# Run custom calculation for high-volume merchant
python3 compliance/fintech-pre-dispute-resolution/scripts/dispute_sla_calculator.py \
  --disputes 180 \
  --avg-amount 110.0 \
  --fee 42.0 \
  --resolution-rate 0.78 \
  --json
```

See [dispute_sla_calculator.py](./scripts/dispute_sla_calculator.py) for the underlying savings formula.

---

## Operational Guardrails & SLAs

1. **The 48-Hour Hard Gate**: Merchants must receive notification within 15 minutes of issuer filing, and respond within 48 hours. Any inquiry exceeding 48 hours defaults to standard card scheme arbitration.
2. **True Fraud vs Friendly Fraud**:
   - *True Fraud (Stolen Card)*: Immediate refund; merchant accepts loss to avoid fee.
   - *Friendly Fraud (Unrecognised Descriptor)*: Deliver digital receipt, GPS delivery signature, or prior transaction evidence to cardholder.
3. **MID Ratio Preservation**: Resolving disputes before chargeback filing ensures the transaction does not count toward the card brands' Excessive Chargeback Program (ECP) thresholds.

For detailed card scheme rules, consult the [Card Scheme Pre-Dispute Protocols](./references/card-scheme-pre-dispute-protocols.md).
