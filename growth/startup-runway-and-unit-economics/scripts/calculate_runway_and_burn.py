#!/usr/bin/env python3
"""
Startup Runway, Burn Rate & Cashflow Calculator

Calculates gross burn, net burn, cash runway, Zero Cash Date (ZCD),
and Default Alive / Default Dead status across startup projects.

Usage:
  # Quick calculation
  python3 growth/startup-runway-and-unit-economics/scripts/calculate_runway_and_burn.py \
    --cash 120000 --gross-burn 15000 --revenue 6000 --growth 0.08

  # Using a project preset
  python3 growth/startup-runway-and-unit-economics/scripts/calculate_runway_and_burn.py --preset amlhive
"""

import argparse
import datetime
import json
import sys

PRESETS = {
    "amlhive": {
        "name": "AML Hive (B2B Compliance SaaS)",
        "cash": 95000.0,
        "gross_burn": 12500.0,
        "revenue": 5500.0,
        "growth": 0.10,
        "arpu": 150.0,
        "cogs_per_unit": 25.0
    },
    "tapease": {
        "name": "Tapease (Merchant Payments POS)",
        "cash": 140000.0,
        "gross_burn": 18000.0,
        "revenue": 7200.0,
        "growth": 0.08,
        "arpu": 85.0,
        "cogs_per_unit": 38.0
    },
    "simplifii": {
        "name": "Simplifii-OS (AI Agent Platform)",
        "cash": 80000.0,
        "gross_burn": 11000.0,
        "revenue": 3200.0,
        "growth": 0.12,
        "arpu": 45.0,
        "cogs_per_unit": 12.0
    }
}

def simulate_runway(cash: float, gross_burn: float, revenue: float, growth_rate: float) -> dict:
    net_burn_current = gross_burn - revenue
    static_runway_months = (cash / net_burn_current) if net_burn_current > 0 else 999.0

    # Dynamic Month-by-Month Simulation (up to 48 months)
    sim_cash = cash
    sim_rev = revenue
    month = 0
    break_even_month = None
    default_alive = False

    while month < 48:
        month += 1
        sim_rev = sim_rev * (1.0 + growth_rate)
        monthly_net_cashflow = sim_rev - gross_burn
        sim_cash += monthly_net_cashflow

        if monthly_net_cashflow >= 0 and break_even_month is None:
            break_even_month = month

        if sim_cash <= 0:
            # Ran out of cash
            break

    if break_even_month is not None and sim_cash > 0:
        default_alive = True

    # Estimate Zero Cash Date
    today = datetime.date.today()
    if net_burn_current > 0:
        days_remaining = int(static_runway_months * 30.4)
        zcd_date = today + datetime.timedelta(days=days_remaining)
        zcd_str = zcd_date.strftime("%d %b %Y")
    else:
        zcd_str = "N/A (Cashflow Positive)"

    return {
        "initial_cash_aud": round(cash, 2),
        "monthly_gross_burn_aud": round(gross_burn, 2),
        "monthly_revenue_aud": round(revenue, 2),
        "current_net_burn_aud": round(net_burn_current, 2),
        "monthly_growth_rate_pct": round(growth_rate * 100.0, 1),
        "static_runway_months": round(static_runway_months, 1),
        "zero_cash_date": zcd_str,
        "default_alive": default_alive,
        "break_even_month": break_even_month if break_even_month else "Exceeds 48 months",
        "cash_health_grade": "Comfortable (>18m)" if static_runway_months >= 18 else (
            "Normal (12-18m)" if static_runway_months >= 12 else (
                "Action Window (6-12m)" if static_runway_months >= 6 else "Red Alert (<6m)"
            )
        )
    }

def main():
    parser = argparse.ArgumentParser(description="Calculate startup runway and cashflow burn rate.")
    parser.add_argument("--preset", choices=["amlhive", "tapease", "simplifii"], help="Use portfolio project preset values")
    parser.add_argument("--cash", type=float, help="Available cash balance in AUD")
    parser.add_argument("--gross-burn", type=float, help="Monthly gross operating expenses in AUD")
    parser.add_argument("--revenue", type=float, help="Monthly cash collections/revenue in AUD")
    parser.add_argument("--growth", type=float, default=0.08, help="Monthly revenue growth rate (e.g. 0.08 for 8 percent)")
    parser.add_argument("--json", action="store_true", help="Output raw JSON")

    args = parser.parse_args()

    # Determine baseline values
    if args.preset:
        p = PRESETS[args.preset]
        project_name = p["name"]
        cash = args.cash if args.cash is not None else p["cash"]
        gross_burn = args.gross_burn if args.gross_burn is not None else p["gross_burn"]
        revenue = args.revenue if args.revenue is not None else p["revenue"]
        growth = args.growth if args.growth != 0.08 else p["growth"]
    else:
        project_name = "Custom Project"
        cash = args.cash if args.cash is not None else 100000.0
        gross_burn = args.gross_burn if args.gross_burn is not None else 15000.0
        revenue = args.revenue if args.revenue is not None else 5000.0
        growth = args.growth

    results = simulate_runway(cash, gross_burn, revenue, growth)
    results["project_name"] = project_name

    if args.json:
        print(json.dumps(results, indent=2))
        return

    print("\n=======================================================")
    print(f"💰 Startup Runway & Burn Analysis: {project_name}")
    print("=======================================================")
    print(f"Current Cash Balance:    ${results['initial_cash_aud']:,} AUD")
    print(f"Monthly Gross Burn:      ${results['monthly_gross_burn_aud']:,} AUD")
    print(f"Monthly Revenue:         ${results['monthly_revenue_aud']:,} AUD")
    print(f"Current Net Burn:        ${results['current_net_burn_aud']:,} AUD/mo")
    print(f"Monthly Revenue Growth:  {results['monthly_growth_rate_pct']}%")
    print("-------------------------------------------------------")
    print(f"Static Runway:           {results['static_runway_months']} months")
    print(f"Runway Health Tier:      {results['cash_health_grade']}")
    print(f"Zero Cash Date (ZCD):    {results['zero_cash_date']}")
    print(f"Default Alive Status:    {'✅ Default Alive' if results['default_alive'] else '⚠️ Default Dead'}")
    print(f"Projected Break-Even:    Month {results['break_even_month']}")
    print("=======================================================\n")

if __name__ == "__main__":
    main()
