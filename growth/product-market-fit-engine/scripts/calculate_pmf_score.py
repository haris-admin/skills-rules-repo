#!/usr/bin/env python3
"""
Product-Market Fit (PMF) Engine CLI.
Calculates the Sean Ellis PMF Score from survey responses:
"How would you feel if you could no longer use this product?"
1. Very disappointed (Target: >= 40%)
2. Somewhat disappointed
3. Not disappointed

Segments High-Expectation Customers (HXC) and breaks down feedback for optimization sprints.
"""

import argparse
import json

SAMPLE_SURVEY_DATA = {
    "product": "AML Hive (amlhive.com.au)",
    "responses": {
        "very_disappointed": 46,
        "somewhat_disappointed": 38,
        "not_disappointed": 16
    },
    "feedback_themes": {
        "very_disappointed_loves": [
            "Instant ASIC and PEP search speed without manual PDF downloads",
            "Automatic audit record generation that satisfies AUSTRAC inspectors",
            "Clean and non-intimidating user interface"
        ],
        "somewhat_disappointed_blockers": [
            "Need bulk upload for 200+ clients via CSV",
            "Xero / MYOB accounting integration missing",
            "Pricing for small solo practices feels slightly high"
        ]
    }
}

def compute_pmf(responses):
    total = sum(responses.values())
    if total == 0:
        return 0, "No responses", {}

    very_pct = (responses["very_disappointed"] / total) * 100
    somewhat_pct = (responses["somewhat_disappointed"] / total) * 100
    not_pct = (responses["not_disappointed"] / total) * 100

    status = (
        "🚀 STRONG PMF (>= 40% Target Reached)"
        if very_pct >= 40.0
        else "⚠️ BUILDING PMF (Below 40% - Optimize Core)"
        if very_pct >= 25.0
        else "🛑 NO PMF (< 25% - High Pivot Risk)"
    )

    percentages = {
        "very_disappointed_pct": round(very_pct, 1),
        "somewhat_disappointed_pct": round(somewhat_pct, 1),
        "not_disappointed_pct": round(not_pct, 1),
        "total_respondents": total
    }
    return round(very_pct, 1), status, percentages

def main():
    parser = argparse.ArgumentParser(description="Sean Ellis & Superhuman PMF Score Calculator CLI")
    parser.add_argument("--demo", action="store_true", help="Run with demonstration survey data")
    parser.add_argument("--very", type=int, help="Count of 'Very Disappointed' responses")
    parser.add_argument("--somewhat", type=int, help="Count of 'Somewhat Disappointed' responses")
    parser.add_argument("--not-disappointed", type=int, help="Count of 'Not Disappointed' responses")
    parser.add_argument("--json", action="store_true", help="Output machine-readable JSON")
    args = parser.parse_args()

    if args.very is not None and args.somewhat is not None and args.not_disappointed is not None:
        responses = {
            "very_disappointed": args.very,
            "somewhat_disappointed": args.somewhat,
            "not_disappointed": args.not_disappointed
        }
        product_name = "Custom Venture"
        feedback = {}
    else:
        responses = SAMPLE_SURVEY_DATA["responses"]
        product_name = SAMPLE_SURVEY_DATA["product"]
        feedback = SAMPLE_SURVEY_DATA["feedback_themes"]

    score, status, pcts = compute_pmf(responses)

    output = {
        "product": product_name,
        "pmf_score_pct": score,
        "pmf_status": status,
        "breakdown": pcts,
        "feedback_themes": feedback
    }

    if args.json:
        print(json.dumps(output, indent=2))
        return

    print("=" * 76)
    print(f" 🎯 PRODUCT-MARKET FIT (PMF) ANALYSIS: {product_name}")
    print(" Benchmark: Sean Ellis 40% Rule ('Very Disappointed' >= 40%)")
    print("=" * 76)
    print(f" Total Respondents:     {pcts['total_respondents']}")
    print(f" 'Very Disappointed':    {pcts['very_disappointed_pct']}% ({responses['very_disappointed']} respondents)")
    print(f" 'Somewhat Disappointed':{pcts['somewhat_disappointed_pct']}% ({responses['somewhat_disappointed']} respondents)")
    print(f" 'Not Disappointed':     {pcts['not_disappointed_pct']}% ({responses['not_disappointed']} respondents)")
    print("-" * 76)
    print(f" PMF Health Status:      {status}")
    print("-" * 76)

    if feedback:
        print(" 💡 SUPERHUMAN ENGINE SPRINT PRIORITIES:")
        print("   1. Double Down on What Enthusiasts Love:")
        for item in feedback.get("very_disappointed_loves", []):
            print(f"      • {item}")
        print("   2. Address What Holds Back High-Intent Fence-Sitters:")
        for item in feedback.get("somewhat_disappointed_blockers", []):
            print(f"      • {item}")
    print("=" * 76)

if __name__ == "__main__":
    main()
