# Card Scheme Pre-Dispute Protocols & Dispute Lifecycle

Technical specifications for managing transaction disputes across Visa, Mastercard, and Eftpos before they escalate into formal, non-refundable chargebacks.

---

## 1. The 3-Sided Network Stakeholder Balance

Undispute mediates across three distinct participants:
1. **Cardholder / Consumer**: Demands immediate clarity, fast refund, or transaction explanation without having to wait 30 days on hold with bank support.
2. **Merchant**: Wants to avoid the $35–$50 chargeback fee, prevent merchant account (MID) termination from exceeding the 0.9% chargeback threshold, and retain the customer relationship.
3. **Issuing Bank**: Wants to reduce call-center operating costs, prevent friendly-fraud dispute filings, and maintain customer satisfaction.

---

## 2. The 48-Hour Amicable Window

When an inquiry is filed by an issuer or cardholder:
- **T0: Alert Generated**: Webhook delivered to Undispute from Ethoca, Verifi, or Issuer API.
- **T0 to T+24 Hours: Merchant Evidence / Auto-Refund**:
  - If recognizable friendly fraud (e.g. recurring subscription forgotten by spouse): Merchant issues 1-click full refund or provides compelling digital receipt.
  - If recognized delivery issue: Merchant issues instant store credit or replacement tracking.
- **T+48 Hours: SLA Gate**: If resolved before 48 hours, the issuer cancels the dispute filing. **Zero chargeback fee is assessed, and the merchant's chargeback ratio remains 0.00%.**
- **Post T+48 Hours**: Unresolved disputes escalate into formal card scheme arbitration.

---

## 3. Scheme Alignment Protocols

### A. Visa Compelling Evidence 3.0 (CE 3.0)
- Allows merchants to deflect fraud claims (Reason Code 10.4) by proving that the cardholder previously made at least two undisputed transactions on the same payment credential older than 120 days.
- Required evidence: IP address, device fingerprint, shipping address, or account login history.

### B. Mastercard Ethoca & Verifi CDRN
- Pre-dispute network integration that pauses chargeback processing for 24 to 72 hours, providing merchants a window to issue refunds directly to the cardholder.
