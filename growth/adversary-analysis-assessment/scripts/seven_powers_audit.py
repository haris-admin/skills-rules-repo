#!/usr/bin/env python3
"""
Hamilton Helmer's 7 Powers & Adversary Assessment Audit CLI.
Evaluates startup defensibility and incumbent retaliation barriers across:
1. Scale Economies
2. Network Economies
3. Counter-Positioning
4. Switching Costs
5. Branding
6. Cornered Resource
7. Process Power
"""

import argparse
import json

POWERS_METADATA = [
    {
        "id": "scale_economies",
        "name": "Scale Economies",
        "barrier": "High fixed costs deter small entrants from matching unit cost.",
        "benefit": "Reduced cost-per-unit at higher operational volumes."
    },
    {
        "id": "network_economies",
        "name": "Network Economies",
        "barrier": "Winner-take-all dynamics create insurmountable multi-tenant value.",
        "benefit": "Value of service grows with each additional participant."
    },
    {
        "id": "counter_positioning",
        "name": "Counter-Positioning",
        "barrier": "Incumbent cannot copy the model without cannibalizing their core revenue.",
        "benefit": "Superior economic model that freezes legacy competitors."
    },
    {
        "id": "switching_costs",
        "name": "Switching Costs",
        "barrier": "Customer loses data, workflow continuity, or faces migration friction.",
        "benefit": "High customer retention and pricing power over time."
    },
    {
        "id": "branding",
        "name": "Branding & Trust",
        "barrier": "Accumulated reputation and institutional trust take years to replicate.",
        "benefit": "Premium pricing and default selection in compliance/financial decisions."
    },
    {
        "id": "cornered_resource",
        "name": "Cornered Resource",
        "barrier": "Preferential or exclusive access to IP, patents, proprietary data, or regulatory licenses.",
        "benefit": "Sustained competitive moat protected by law or exclusive rights."
    },
    {
        "id": "process_power",
        "name": "Process Power",
        "barrier": "Embedded operational muscle memory and micro-optimizations that cannot be easily copied.",
        "benefit": "Superior speed, quality, and unit margins from accumulated execution."
    }
]

PRESETS = {
    "amlhive": {
        "venture": "AML Hive (amlhive.com.au)",
        "adversaries": ["Legacy manual consultants", "Overseas compliance SaaS", "Status Quo (Excel)"],
        "scores": {
            "scale_economies": 3,
            "network_economies": 2,
            "counter_positioning": 5, # Low-cost SaaS vs $15,000/yr consultant retainers
            "switching_costs": 4,     # Historical AUSTRAC audit records stored in platform
            "branding": 4,            # Top SEO rankings and citation share of voice
            "cornered_resource": 3,   # Direct ASIC register indexing
            "process_power": 4        # Automated daily testing & continuous regulatory sync
        },
        "incumbent_retaliation_risk": "Low (Consultants cannot cut fees 90% without destroying their firm)"
    },
    "tapease": {
        "venture": "Tapease (tapease.com.au)",
        "adversaries": ["Bank EFTPOS terminals (CBA, NAB)", "Tyro", "Square"],
        "scores": {
            "scale_economies": 3,
            "network_economies": 2,
            "counter_positioning": 4, # Transparent low surcharge routing vs opaque bank interchange
            "switching_costs": 3,
            "branding": 3,
            "cornered_resource": 3,
            "process_power": 4        # Automated Clover shift sync and instant daily settlement
        },
        "incumbent_retaliation_risk": "Medium (Big banks are slow to adapt software, but possess immense distribution)"
    },
    "simplifii": {
        "venture": "Simplifii-OS",
        "adversaries": ["Generic LMS (Canvas, Moodle)", "Generic AI (ChatGPT)", "Executive task paralysis"],
        "scores": {
            "scale_economies": 2,
            "network_economies": 3,
            "counter_positioning": 5, # Pure neurodivergent focus vs generic one-size-fits-all education
            "switching_costs": 4,     # Personalized learning profile, Bionic settings, history of thought
            "branding": 4,            # Trusted neuroinclusive safe space
            "cornered_resource": 3,
            "process_power": 5        # Trimodal UI, W3C COGA design system, Pareto task auto-decomposition
        },
        "incumbent_retaliation_risk": "Very Low (Mainstream edtech caters to institutional admins, not neurodivergent students)"
    },
    "undispute": {
        "venture": "Undispute Pre-Dispute Network",
        "adversaries": ["Bank chargeback departments", "Chargebacks911", "Status Quo ($35 penalty fees)"],
        "scores": {
            "scale_economies": 3,
            "network_economies": 5,   # 3-sided network: Cardholders, Merchants, Issuing Banks
            "counter_positioning": 5, # Pre-chargeback 48h settlement eliminates arbitration fees entirely
            "switching_costs": 4,     # Integrated into merchant payment gateway webhooks
            "branding": 3,
            "cornered_resource": 4,   # Direct scheme pre-arbitration webhook agreements
            "process_power": 4        # Automated dispute resolution SLA workflows
        },
        "incumbent_retaliation_risk": "Low (Banks and merchants both want to eliminate deadweight chargeback processing costs)"
    }
}

def evaluate_powers(scores):
    total_score = sum(scores.values())
    max_score = len(scores) * 5
    pct = round((total_score / max_score) * 100, 1)

    # Dominant powers (scores of 4 or 5)
    dominant = [k for k, v in scores.items() if v >= 4]

    moat_tier = "FORTRESS (High Defensibility)" if pct >= 75 else "SOLID (Defensible Moats)" if pct >= 55 else "VULNERABLE (Commodity Risk)"
    return total_score, max_score, pct, dominant, moat_tier

def main():
    parser = argparse.ArgumentParser(description="Hamilton Helmer 7 Powers Defensibility Audit CLI")
    parser.add_argument("--preset", choices=["amlhive", "tapease", "simplifii", "undispute"], default="amlhive", help="Evaluate venture preset")
    parser.add_argument("--demo", action="store_true", help="Run audit on sample venture")
    parser.add_argument("--json", action="store_true", help="Output machine-readable JSON")
    args = parser.parse_args()

    preset_key = args.preset
    data = PRESETS[preset_key]

    total, max_s, pct, dominant, tier = evaluate_powers(data["scores"])

    output = {
        "venture": data["venture"],
        "adversaries": data["adversaries"],
        "scores": data["scores"],
        "total_score": total,
        "max_score": max_s,
        "moat_percentage": pct,
        "dominant_powers": dominant,
        "moat_tier": tier,
        "incumbent_retaliation_risk": data["incumbent_retaliation_risk"]
    }

    if args.json:
        print(json.dumps(output, indent=2))
        return

    print("=" * 80)
    print(f" 🏰 7 POWERS & ADVERSARY ASSESSMENT: {data['venture']}")
    print("=" * 80)
    print(f" Key Adversaries: {', '.join(data['adversaries'])}")
    print(f" Moat Health:     {tier} ({total}/{max_s} points - {pct}%)")
    print(f" Retaliation:     {data['incumbent_retaliation_risk']}")
    print("-" * 80)
    print(f"{'Power':<24} | {'Score':<6} | {'Status':<12} | {'Strategic Mechanism'}")
    print("-" * 80)

    for p in POWERS_METADATA:
        pid = p["id"]
        score = data["scores"].get(pid, 1)
        status = "⭐ Primary Moat" if score >= 4 else "Developing" if score >= 3 else "Weak / Absent"
        print(f"{p['name']:<24} | {score}/5    | {status:<12} | {p['barrier'][:34]}...")

    print("-" * 80)
    print("💡 KEY TAKEAWAY: Early-stage startups must win via Counter-Positioning or Cornered Resources.")
    print("=" * 80)

if __name__ == "__main__":
    main()
