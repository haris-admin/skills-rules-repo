#!/usr/bin/env python3
"""
AARRR Pirate Metrics Funnel Calculator

Computes stage-by-stage conversions, cumulative drop-offs, and throughput
across the five customer lifecycle stages:
Acquisition -> Activation -> Retention -> Revenue -> Referral.

Usage:
  python3 growth/aarrr-pirate-metrics/scripts/calculate_aarrr_funnel.py \
    --visitors 10000 \
    --signups 600 \
    --activated 420 \
    --retained 250 \
    --paying 100 \
    --referrals 25
"""

import argparse
import json
import sys

def calculate_funnel(visitors: int, signups: int, activated: int, 
                     retained: int, paying: int, referrals: int) -> dict:
    
    def pct(num: float, den: float) -> float:
        return round((num / den * 100.0), 2) if den > 0 else 0.0

    # Step conversion rates
    acq_to_act_rate = pct(activated, signups)
    signup_conversion = pct(signups, visitors)
    act_to_ret_rate = pct(retained, activated)
    ret_to_rev_rate = pct(paying, retained)
    rev_to_ref_rate = pct(referrals, paying)

    # Cumulative throughput
    overall_paying_conversion = pct(paying, visitors)
    overall_referral_conversion = pct(referrals, visitors)

    stages = [
        {"stage": "1. Acquisition (Visitors)", "count": visitors, "step_conversion": 100.0, "cum_conversion": 100.0},
        {"stage": "2. Activation (Signups)", "count": signups, "step_conversion": signup_conversion, "cum_conversion": pct(signups, visitors)},
        {"stage": "   Activated Users", "count": activated, "step_conversion": acq_to_act_rate, "cum_conversion": pct(activated, visitors)},
        {"stage": "3. Retention (Active)", "count": retained, "step_conversion": act_to_ret_rate, "cum_conversion": pct(retained, visitors)},
        {"stage": "4. Revenue (Paying)", "count": paying, "step_conversion": ret_to_rev_rate, "cum_conversion": overall_paying_conversion},
        {"stage": "5. Referral (Advocates)", "count": referrals, "step_conversion": rev_to_ref_rate, "cum_conversion": overall_referral_conversion},
    ]

    return {
        "funnel_stages": stages,
        "summary": {
            "visitor_to_signup_pct": signup_conversion,
            "signup_to_activated_pct": acq_to_act_rate,
            "activated_to_retained_pct": act_to_ret_rate,
            "retained_to_paying_pct": ret_to_rev_rate,
            "paying_to_referral_pct": rev_to_ref_rate,
            "overall_visitor_to_paying_pct": overall_paying_conversion,
            "overall_referral_rate_pct": overall_referral_conversion
        }
    }

def main():
    parser = argparse.ArgumentParser(description="Calculate AARRR Pirate Metrics Funnel.")
    parser.add_argument("--visitors", type=int, default=5000, help="Total unique website/landing page visitors")
    parser.add_argument("--signups", type=int, default=300, help="Total account signups or leads")
    parser.add_argument("--activated", type=int, default=210, help="Users who completed core initial value action")
    parser.add_argument("--retained", type=int, default=140, help="Users active after 30 days")
    parser.add_argument("--paying", type=int, default=70, help="Total paying customers")
    parser.add_argument("--referrals", type=int, default=15, help="Customers who referred at least one new user")
    parser.add_argument("--json", action="store_true", help="Output raw JSON")

    args = parser.parse_args()

    results = calculate_funnel(
        visitors=args.visitors,
        signups=args.signups,
        activated=args.activated,
        retained=args.retained,
        paying=args.paying,
        referrals=args.referrals
    )

    if args.json:
        print(json.dumps(results, indent=2))
        return

    print("\n=======================================================================")
    print("🏴‍☠️ AARRR Pirate Metrics Funnel Analysis")
    print("=======================================================================")
    print(f"{'Funnel Stage':<30} | {'Users':<10} | {'Step Conv':<12} | {'Cumul Conv':<10}")
    print("-----------------------------------------------------------------------")
    for s in results["funnel_stages"]:
        print(f"{s['stage']:<30} | {s['count']:<10} | {s['step_conversion']:>6.1f}%     | {s['cum_conversion']:>6.2f}%")
    print("=======================================================================")
    print(f"Overall Visitor -> Paying Customer Throughput: {results['summary']['overall_visitor_to_paying_pct']}%")
    print("=======================================================================\n")

if __name__ == "__main__":
    main()
