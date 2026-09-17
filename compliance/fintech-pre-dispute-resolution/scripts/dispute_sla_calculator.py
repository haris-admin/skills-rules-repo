#!/usr/bin/env python3
"""
Undispute 48-Hour Pre-Dispute Resolution SLA & Economics Calculator CLI.
Calculates savings from resolving disputes during the pre-chargeback grace period,
avoiding $35-$50 scheme penalties and card processor ratio breaches.
"""

import argparse
import json

def calculate_dispute_economics(monthly_disputes, avg_tx_amount, chargeback_fee=38.0, resolution_rate=0.72):
    """
    monthly_disputes: Number of transaction inquiries/disputes per month.
    avg_tx_amount: Average transaction value in AUD.
    chargeback_fee: Non-refundable fee charged by bank/processor per formal chargeback ($35-$50).
    resolution_rate: Percentage of disputes resolved amicably in 48h pre-chargeback window.
    """
    resolved_count = int(monthly_disputes * resolution_rate)
    unresolved_count = monthly_disputes - resolved_count

    # Cost without pre-dispute resolution (all go to full chargeback)
    cost_without = monthly_disputes * chargeback_fee
    
    # Cost with Undispute (avoided chargeback fees on resolved inquiries)
    fees_avoided_monthly = resolved_count * chargeback_fee
    fees_avoided_annual = fees_avoided_monthly * 12

    # Preserved merchant processing ratio impact
    ratio_reduction_pct = round(resolution_rate * 100, 1)

    return {
        "inputs": {
            "monthly_disputes": monthly_disputes,
            "avg_transaction_amount_aud": avg_tx_amount,
            "scheme_chargeback_fee_aud": chargeback_fee,
            "pre_dispute_resolution_rate": resolution_rate
        },
        "monthly_outcomes": {
            "total_inquiries": monthly_disputes,
            "resolved_pre_chargeback_48h": resolved_count,
            "escalated_to_formal_chargeback": unresolved_count,
            "fees_saved_monthly_aud": fees_avoided_monthly,
            "fees_saved_annual_aud": fees_avoided_annual,
            "chargeback_ratio_reduction_pct": ratio_reduction_pct
        }
    }

def main():
    parser = argparse.ArgumentParser(description="Undispute Pre-Dispute SLA & Financial Savings Calculator")
    parser.add_argument("--disputes", type=int, default=60, help="Monthly customer dispute/inquiry count (default: 60)")
    parser.add_argument("--avg-amount", type=float, default=85.0, help="Average transaction dispute amount ($)")
    parser.add_argument("--fee", type=float, default=38.0, help="Bank chargeback fee penalty per dispute (default: $38)")
    parser.add_argument("--resolution-rate", type=float, default=0.72, help="Expected pre-chargeback resolution rate (default: 0.72)")
    parser.add_argument("--demo", action="store_true", help="Run with standard Australian merchant numbers")
    parser.add_argument("--json", action="store_true", help="Output machine-readable JSON")
    args = parser.parse_args()

    results = calculate_dispute_economics(args.disputes, args.avg_amount, args.fee, args.resolution_rate)

    if args.json:
        print(json.dumps(results, indent=2))
        return

    m = results["monthly_outcomes"]
    print("=" * 76)
    print(" 💳 UNDISPUTE PRE-CHARGEBACK RESOLUTION ECONOMICS")
    print(" Scheme Neutrality: Visa CE 3.0 / Mastercard Ethoca / Eftpos")
    print("=" * 76)
    print(f" Monthly Transaction Inquiries: {results['inputs']['monthly_disputes']}")
    print(f" Scheme Penalty per Chargeback:  ${results['inputs']['scheme_chargeback_fee_aud']:.2f}")
    print(f" 48h Resolution Rate:            {results['inputs']['pre_dispute_resolution_rate']*100:.1f}%")
    print("-" * 76)
    print(f" Resolved Within 48h Window:     {m['resolved_pre_chargeback_48h']} disputes/month")
    print(f" Formal Chargebacks Prevented:   {m['chargeback_ratio_reduction_pct']}% reduction in dispute ratio")
    print(f" Direct Fee Penalties Saved/Mo:  ${m['fees_saved_monthly_aud']:,.2f} / month")
    print(f" Projected Annual Fee Savings:   ${m['fees_saved_annual_aud']:,.2f} / year")
    print("=" * 76)
    print("💡 STRATEGY: Resolving disputes under 48h protects merchant acquirer MID standing.")
    print("=" * 76)

if __name__ == "__main__":
    main()
