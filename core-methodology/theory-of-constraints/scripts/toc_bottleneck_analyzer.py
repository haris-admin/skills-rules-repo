#!/usr/bin/env python3
"""
Theory of Constraints (TOC) Bottleneck Analyzer

Models multi-stage pipeline flow, identifies the single governing constraint,
calculates idle waste across non-bottlenecks, and projects throughput gains
from elevating the bottleneck.

Usage:
  python3 core-methodology/theory-of-constraints/scripts/toc_bottleneck_analyzer.py
  python3 core-methodology/theory-of-constraints/scripts/toc_bottleneck_analyzer.py --preset compliance_onboarding
  python3 core-methodology/theory-of-constraints/scripts/toc_bottleneck_analyzer.py --json
"""

import argparse
import json
import sys

PRESETS = {
    "software_delivery": [
        {"stage": "1. Backlog & Spec Design", "capacity": 35, "unit": "stories/wk"},
        {"stage": "2. Implementation (Coding)", "capacity": 28, "unit": "stories/wk"},
        {"stage": "3. Code Review & PR Approval", "capacity": 14, "unit": "stories/wk"},
        {"stage": "4. QA & Staging Verification", "capacity": 22, "unit": "stories/wk"},
        {"stage": "5. Production Deployment", "capacity": 40, "unit": "stories/wk"}
    ],
    "compliance_onboarding": [
        {"stage": "1. Inbound Lead Intake", "capacity": 120, "unit": "entities/mo"},
        {"stage": "2. Document Collection", "capacity": 75, "unit": "entities/mo"},
        {"stage": "3. Manual ASIC / PEP Review", "capacity": 30, "unit": "entities/mo"},
        {"stage": "4. Customer Approval Sign-off", "capacity": 65, "unit": "entities/mo"},
        {"stage": "5. Account Activation", "capacity": 100, "unit": "entities/mo"}
    ]
}

def analyze_pipeline(stages: list) -> dict:
    bottleneck_stage = min(stages, key=lambda x: x["capacity"])
    system_throughput = bottleneck_stage["capacity"]

    annotated = []
    for s in stages:
        utilization = round((system_throughput / s["capacity"]) * 100.0, 1)
        is_bottleneck = (s["stage"] == bottleneck_stage["stage"])
        annotated.append({
            "stage": s["stage"],
            "capacity": s["capacity"],
            "unit": s["unit"],
            "effective_output": system_throughput,
            "utilization_pct": utilization,
            "is_constraint": is_bottleneck
        })

    # Elevate simulation (doubling the bottleneck)
    elevated_capacity = bottleneck_stage["capacity"] * 2
    new_stages = [dict(s) for s in stages]
    for s in new_stages:
        if s["stage"] == bottleneck_stage["stage"]:
            s["capacity"] = elevated_capacity
    new_bottleneck = min(new_stages, key=lambda x: x["capacity"])

    return {
        "current_throughput": system_throughput,
        "constraint_stage": bottleneck_stage["stage"],
        "unit": bottleneck_stage["unit"],
        "stages": annotated,
        "elevation_simulation": {
            "new_throughput": new_bottleneck["capacity"],
            "throughput_increase_pct": round(((new_bottleneck["capacity"] - system_throughput) / system_throughput) * 100.0, 1),
            "new_constraint_stage": new_bottleneck["stage"]
        }
    }

def main():
    parser = argparse.ArgumentParser(description="Analyze pipeline bottlenecks using Theory of Constraints.")
    parser.add_argument("--preset", choices=["software_delivery", "compliance_onboarding"], default="software_delivery",
                        help="Pre-configured pipeline scenario (default: software_delivery)")
    parser.add_argument("--json", action="store_true", help="Output raw JSON")

    args = parser.parse_args()

    stages = PRESETS[args.preset]
    results = analyze_pipeline(stages)

    if args.json:
        print(json.dumps(results, indent=2))
        return

    print("\n================================================================================")
    print(f"⛓️ Theory of Constraints Pipeline Flow: {args.preset.replace('_', ' ').title()}")
    print("================================================================================")
    print(f"{'Stage Name':<35} | {'Capacity':<10} | {'Utilization':<12} | {'Role':<15}")
    print("--------------------------------------------------------------------------------")
    for s in results["stages"]:
        flag = "🚨 CONSTRAINT" if s["is_constraint"] else "  Non-Bottleneck"
        print(f"{s['stage']:<35} | {s['capacity']:>4} {s['unit'][:4]}   | {s['utilization_pct']:>6.1f}%       | {flag}")
    print("================================================================================")
    print(f"Current System Throughput: {results['current_throughput']} {results['unit']}")
    print(f"Governing Constraint:     {results['constraint_stage']}")
    print("--------------------------------------------------------------------------------")
    sim = results["elevation_simulation"]
    print(f"🚀 If constraint is elevated 2x: Throughput jumps {sim['throughput_increase_pct']}% to {sim['new_throughput']} {results['unit']}")
    print(f"   Next constraint shifts to:   {sim['new_constraint_stage']}")
    print("================================================================================\n")

if __name__ == "__main__":
    main()
