#!/usr/bin/env python3
"""
AMLHive a16z Startup Metrics Calculator

Calculates canonical Andreessen Horowitz (a16z) SaaS metrics tailored
specifically for AMLHive: ARR, MRR, Gross Margin, Blended CAC, CAC Payback,
LTV, and LTV/CAC ratio.

Usage:
  python3 growth/a16z-startup-metrics/scripts/compute_amlhive_metrics.py --mrr 15000 --entities 100 --sales-spend 3000 --new-entities 12 --cogs-per-entity 25 --churn-rate 0.02
"""

import argparse
import json
import sys

def compute_metrics(mrr: float, active_entities: int, monthly_sm_spend: float, 
                    new_entities: int, cogs_per_entity: float, monthly_churn_rate: float) -> dict:
    arr = mrr * 12.0
    arpu = mrr / max(active_entities, 1)
    
    # Gross Margin
    monthly_cogs = active_entities * cogs_per_entity
    gross_profit = max(mrr - monthly_cogs, 0.0)
    gross_margin_pct = (gross_profit / mrr * 100.0) if mrr > 0 else 0.0
    gross_margin_frac = gross_margin_pct / 100.0

    # CAC
    blended_cac = (monthly_sm_spend / new_entities) if new_entities > 0 else 0.0

    # CAC Payback (Months)
    monthly_gp_per_entity = arpu * gross_margin_frac
    cac_payback_months = (blended_cac / monthly_gp_per_entity) if monthly_gp_per_entity > 0 else 0.0

    # LTV
    ltv = (arpu * gross_margin_frac / monthly_churn_rate) if monthly_churn_rate > 0 else 0.0

    # LTV / CAC Ratio
    ltv_cac_ratio = (ltv / blended_cac) if blended_cac > 0 else 0.0

    return {
        "mrr_aud": round(mrr, 2),
        "arr_aud": round(arr, 2),
        "arpu_aud": round(arpu, 2),
        "gross_margin_pct": round(gross_margin_pct, 1),
        "blended_cac_aud": round(blended_cac, 2),
        "cac_payback_months": round(cac_payback_months, 1),
        "ltv_aud": round(ltv, 2),
        "ltv_cac_ratio": round(ltv_cac_ratio, 2),
        "health_checks": {
            "gross_margin_healthy": gross_margin_pct >= 75.0,
            "cac_payback_healthy": cac_payback_months <= 12.0,
            "ltv_cac_healthy": ltv_cac_ratio >= 3.0,
        }
    }

def main():
    parser = argparse.ArgumentParser(description="Calculate a16z startup metrics for AMLHive.")
    parser.add_argument("--mrr", type=float, default=12000.0, help="Monthly Recurring Revenue in AUD")
    parser.add_argument("--entities", type=int, default=80, help="Total active reporting entities")
    parser.add_argument("--sales-spend", type=float, default=2500.0, help="Total monthly sales & marketing spend AUD")
    parser.add_argument("--new-entities", type=int, default=10, help="New entities acquired this month")
    parser.add_argument("--cogs-per-entity", type=float, default=20.0, help="Estimated monthly search/API COGS per entity")
    parser.add_argument("--churn-rate", type=float, default=0.015, help="Monthly logo churn rate (e.g. 0.015 for 1.5 percent)")
    parser.add_argument("--json", action="store_true", help="Output raw JSON")

    args = parser.parse_args()

    results = compute_metrics(
        mrr=args.mrr,
        active_entities=args.entities,
        monthly_sm_spend=args.sales_spend,
        new_entities=args.new_entities,
        cogs_per_entity=args.cogs_per_entity,
        monthly_churn_rate=args.churn_rate
    )

    if args.json:
        print(json.dumps(results, indent=2))
        return

    print("\n=======================================================")
    print("📊 AMLHive a16z Startup Metrics Summary")
    print("=======================================================")
    print(f"ARR (Annualized):        ${results['arr_aud']:,} AUD")
    print(f"MRR (Monthly):           ${results['mrr_aud']:,} AUD")
    print(f"ARPU (Average/Entity):   ${results['arpu_aud']:,} AUD/mo")
    print(f"Gross Margin:            {results['gross_margin_pct']}% {'✅' if results['health_checks']['gross_margin_healthy'] else '⚠️'}")
    print(f"Blended CAC:             ${results['blended_cac_aud']:,} AUD")
    print(f"CAC Payback Period:      {results['cac_payback_months']} months {'✅' if results['health_checks']['cac_payback_healthy'] else '⚠️'}")
    print(f"Customer LTV:            ${results['ltv_aud']:,} AUD")
    print(f"LTV / CAC Ratio:         {results['ltv_cac_ratio']}x {'✅' if results['health_checks']['ltv_cac_healthy'] else '⚠️'}")
    print("=======================================================\n")

if __name__ == "__main__":
    main()
