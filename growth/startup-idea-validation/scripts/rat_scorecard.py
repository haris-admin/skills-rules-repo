#!/usr/bin/env python3
"""
Riskiest Assumption Test (RAT) Scorecard CLI.
Scores venture assumptions across Impact, Uncertainty, and Ease of Test.
Calculates Risk Score and produces an evidence-driven testing schedule.
"""

import argparse
import json
import sys

SAMPLE_ASSUMPTIONS = [
    {
        "id": "A1",
        "category": "Desirability",
        "assumption": "Sole traders will connect their bank account to auto-generate BAS statements rather than using Excel.",
        "impact": 5,      # 1 (low impact if wrong) to 5 (deadly if wrong)
        "uncertainty": 4, # 1 (high evidence exists) to 5 (pure guess)
        "test_effort": 2  # 1 (test in 1 day) to 5 (requires building backend)
    },
    {
        "id": "A2",
        "category": "Viability",
        "assumption": "Target customers will pay at least $39/month for automated pre-dispute resolution.",
        "impact": 5,
        "uncertainty": 5,
        "test_effort": 1
    },
    {
        "id": "A3",
        "category": "Feasibility",
        "assumption": "Bank API open banking webhooks will deliver transaction dispute data within 15 minutes.",
        "impact": 4,
        "uncertainty": 3,
        "test_effort": 2
    },
    {
        "id": "A4",
        "category": "Distribution",
        "assumption": "Accountants will actively refer SMB clients in exchange for free practice dashboard access.",
        "impact": 4,
        "uncertainty": 4,
        "test_effort": 2
    }
]

def calculate_priority(assumption):
    """
    Priority formula: (Impact * Uncertainty) / Test Effort.
    High Impact + High Uncertainty + Low Test Effort = Highest Priority to test immediately.
    """
    impact = assumption["impact"]
    uncertainty = assumption["uncertainty"]
    effort = max(1, assumption["test_effort"])
    
    risk_score = impact * uncertainty
    test_priority = (impact * uncertainty) / effort
    return risk_score, round(test_priority, 2)

def evaluate_assumptions(assumptions):
    scored = []
    for item in assumptions:
        risk_score, priority = calculate_priority(item)
        urgency = "CRITICAL (Test First)" if risk_score >= 20 else "HIGH" if risk_score >= 12 else "MEDIUM"
        scored.append({
            **item,
            "risk_score": risk_score,
            "test_priority": priority,
            "urgency": urgency
        })
    scored.sort(key=lambda x: (x["test_priority"], x["risk_score"]), reverse=True)
    return scored

def main():
    parser = argparse.ArgumentParser(description="Riskiest Assumption Test (RAT) Scorecard CLI")
    parser.add_argument("--demo", action="store_true", help="Run with demonstration venture assumptions")
    parser.add_argument("--file", type=str, help="Path to JSON file containing assumptions list")
    parser.add_argument("--json", action="store_true", help="Output results as JSON")
    args = parser.parse_args()

    if args.file:
        try:
            with open(args.file, "r") as f:
                assumptions = json.load(f)
        except Exception as e:
            print(f"Error reading {args.file}: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        assumptions = SAMPLE_ASSUMPTIONS

    results = evaluate_assumptions(assumptions)

    if args.json:
        print(json.dumps(results, indent=2))
        return

    print("=" * 84)
    print(" 🎯 RISKIEST ASSUMPTION TEST (RAT) SCORECARD")
    print(" Ranked by: (Impact × Uncertainty) / Test Effort")
    print("=" * 84)
    print(f"{'ID':<4} | {'Cat':<13} | {'Risk':<5} | {'Prio':<5} | {'Urgency':<22} | {'Assumption'}")
    print("-" * 84)

    for item in results:
        assump_text = item["assumption"]
        if len(assump_text) > 42:
            assump_text = assump_text[:39] + "..."
        print(f"{item['id']:<4} | {item['category']:<13} | {item['risk_score']:<5} | {item['test_priority']:<5} | {item['urgency']:<22} | {assump_text}")

    print("-" * 84)
    print("💡 ACTION RULE: Run pretotypes for assumptions with Risk Score >= 15 before writing production code.")
    print("=" * 84)

if __name__ == "__main__":
    main()
