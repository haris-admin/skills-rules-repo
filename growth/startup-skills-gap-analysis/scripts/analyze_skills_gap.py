#!/usr/bin/env python3
"""
Startup Skills Gap Analyzer

Audits startup team capabilities against target milestone requirements
and recommends capital-efficient remediation pathways (Automate via AI Agents,
Fractional Experts, Internal Upskilling, or Full-Time Hiring).

Usage:
  python3 growth/startup-skills-gap-analysis/scripts/analyze_skills_gap.py
  python3 growth/startup-skills-gap-analysis/scripts/analyze_skills_gap.py --milestone compliance_audit
  python3 growth/startup-skills-gap-analysis/scripts/analyze_skills_gap.py --json
"""

import argparse
import json
import sys

MILESTONES = {
    "seed": {
        "name": "Seed / Early Revenue Stage",
        "benchmarks": {
            "Engineering & Architecture": 3,
            "Autonomous AI & Agent Ops": 3,
            "Regulatory & Compliance": 3,
            "B2B Sales & GTM": 3,
            "Product & UX": 3,
            "Financial & Runway Modeling": 3,
            "People & Operations": 2
        }
    },
    "compliance_audit": {
        "name": "Regulatory Compliance & Audit Readiness (AUSTRAC / ASIC)",
        "benchmarks": {
            "Engineering & Architecture": 4,
            "Autonomous AI & Agent Ops": 3,
            "Regulatory & Compliance": 5,
            "B2B Sales & GTM": 3,
            "Product & UX": 3,
            "Financial & Runway Modeling": 4,
            "People & Operations": 3
        }
    },
    "series_a": {
        "name": "Series A / Scaling Operations",
        "benchmarks": {
            "Engineering & Architecture": 4,
            "Autonomous AI & Agent Ops": 4,
            "Regulatory & Compliance": 4,
            "B2B Sales & GTM": 4,
            "Product & UX": 4,
            "Financial & Runway Modeling": 4,
            "People & Operations": 4
        }
    }
}

DEFAULT_TEAM_SCORES = {
    "Engineering & Architecture": 3,
    "Autonomous AI & Agent Ops": 3,
    "Regulatory & Compliance": 2,
    "B2B Sales & GTM": 2,
    "Product & UX": 3,
    "Financial & Runway Modeling": 3,
    "People & Operations": 1
}

def analyze_gaps(current_scores: dict, milestone_key: str) -> dict:
    milestone = MILESTONES.get(milestone_key, MILESTONES["seed"])
    benchmarks = milestone["benchmarks"]
    results = []

    for domain, req_score in benchmarks.items():
        curr_score = current_scores.get(domain, 1)
        gap = max(req_score - curr_score, 0)

        # Recommendation logic
        if gap == 0:
            remediation = "Sufficient (Maintain)"
            priority = "Low"
        elif gap == 1:
            remediation = "Upskill Internal Team / AI Agent Support"
            priority = "Medium"
        elif domain in ["Autonomous AI & Agent Ops", "Engineering & Architecture"]:
            remediation = "Automate via AI Agents / Fractional Architect"
            priority = "High"
        elif domain in ["Regulatory & Compliance", "Financial & Runway Modeling"]:
            remediation = "Engage Fractional Expert / Advisor"
            priority = "Critical"
        else:
            remediation = "Full-Time Hire (A-Player Role Scorecard)"
            priority = "High"

        results.append({
            "domain": domain,
            "required": req_score,
            "current": curr_score,
            "gap": gap,
            "priority": priority,
            "remediation": remediation
        })

    return {
        "milestone": milestone["name"],
        "domains": sorted(results, key=lambda x: x["gap"], reverse=True),
        "total_critical_gaps": sum(1 for r in results if r["gap"] >= 2)
    }

def main():
    parser = argparse.ArgumentParser(description="Analyze startup team skills gaps against milestones.")
    parser.add_argument("--milestone", choices=["seed", "compliance_audit", "series_a"], default="seed",
                        help="Target milestone (default: seed)")
    parser.add_argument("--json", action="store_true", help="Output raw JSON")

    args = parser.parse_args()

    analysis = analyze_gaps(DEFAULT_TEAM_SCORES, args.milestone)

    if args.json:
        print(json.dumps(analysis, indent=2))
        return

    print("\n================================================================================")
    print(f"🔍 Startup Skills Gap Audit: {analysis['milestone']}")
    print("================================================================================")
    print(f"{'Functional Domain':<30} | {'Req':<4} | {'Cur':<4} | {'Gap':<4} | {'Action Path':<30}")
    print("--------------------------------------------------------------------------------")
    for d in analysis["domains"]:
        gap_display = f"+{d['gap']}" if d['gap'] > 0 else "0"
        flag = "⚠️ " if d['gap'] >= 2 else "   "
        print(f"{flag}{d['domain']:<27} | {d['required']:<4} | {d['current']:<4} | {gap_display:<4} | {d['remediation']}")
    print("================================================================================")
    print(f"Total High-Priority Gaps (Gap >= 2): {analysis['total_critical_gaps']}")
    print("================================================================================\n")

if __name__ == "__main__":
    main()
