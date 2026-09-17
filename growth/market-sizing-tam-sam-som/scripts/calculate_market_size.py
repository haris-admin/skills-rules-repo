#!/usr/bin/env python3
"""
Bottom-Up Market Sizing CLI (TAM / SAM / SOM).
Calculates defensible market scale based on target account universe, ACV,
serviceable geographic/channel penetration, and 24-36 month realistic market share.
Includes sensitivity ranges (Conservative, Base, Aggressive) and JSON export.
"""

import argparse
import json

def calculate_market_sizing(tam_accounts, acv, sam_pct, som_pct, growth_rate=0.0):
    """
    tam_accounts: Total number of entities in broader universe.
    acv: Annual Contract Value ($/year/customer).
    sam_pct: Fraction of TAM that matches product capabilities/geography (0.0 - 1.0).
    som_pct: Fraction of SAM realistically capturable in 2-3 years (0.0 - 1.0).
    """
    tam_value = tam_accounts * acv
    sam_accounts = tam_accounts * sam_pct
    sam_value = sam_accounts * acv
    som_accounts = sam_accounts * som_pct
    som_value = som_accounts * acv

    scenarios = {
        "conservative": {
            "som_pct": som_pct * 0.5,
            "som_accounts": int(som_accounts * 0.5),
            "som_value": som_value * 0.5
        },
        "base": {
            "som_pct": som_pct,
            "som_accounts": int(som_accounts),
            "som_value": som_value
        },
        "aggressive": {
            "som_pct": som_pct * 1.5,
            "som_accounts": int(som_accounts * 1.5),
            "som_value": som_value * 1.5
        }
    }

    return {
        "inputs": {
            "tam_universe_accounts": tam_accounts,
            "annual_contract_value_acv": acv,
            "sam_reach_ratio": sam_pct,
            "som_capture_ratio": som_pct,
        },
        "tam": {
            "total_accounts": tam_accounts,
            "total_value_aud": tam_value
        },
        "sam": {
            "serviceable_accounts": int(sam_accounts),
            "serviceable_value_aud": sam_value
        },
        "som": {
            "obtainable_accounts": int(som_accounts),
            "obtainable_value_aud": som_value
        },
        "sensitivity_scenarios": scenarios
    }

def format_currency(val):
    if val >= 1_000_000_000:
        return f"${val / 1_000_000_000:.2f}B"
    if val >= 1_000_000:
        return f"${val / 1_000_000:.2f}M"
    if val >= 1_000:
        return f"${val / 1_000:.1f}K"
    return f"${val:.2f}"

def main():
    parser = argparse.ArgumentParser(description="Bottom-Up TAM / SAM / SOM Market Sizing CLI")
    parser.add_argument("--tam-accounts", type=int, default=50000, help="Total potential account universe (e.g. 50000)")
    parser.add_argument("--acv", type=float, default=1200.0, help="Annual Contract Value / Average Revenue Per User per year ($)")
    parser.add_argument("--sam-pct", type=float, default=0.30, help="SAM addressable percentage (0.01 to 1.00, default 0.30)")
    parser.add_argument("--som-pct", type=float, default=0.05, help="SOM capture percentage within 3 years (0.01 to 1.00, default 0.05)")
    parser.add_argument("--preset", choices=["amlhive", "tapease", "simplifii", "undispute"], help="Load venture profile presets")
    parser.add_argument("--json", action="store_true", help="Output machine-readable JSON")
    args = parser.parse_args()

    if args.preset == "amlhive":
        # AUSTRAC reporting entities (~17,000 in AU), ~$1,800/yr ACV, 40% initial tranche, 8% 3-yr SOM
        tam_acc = 17000
        acv = 1800.0
        sam_pct = 0.40
        som_pct = 0.08
    elif args.preset == "tapease":
        # AU SMB merchants taking card payments (~250,000), ~$960/yr margin/cut, 20% hospitality/retail, 3% SOM
        tam_acc = 250000
        acv = 960.0
        sam_pct = 0.20
        som_pct = 0.03
    elif args.preset == "simplifii":
        # Neurodivergent student population in AU (~450,000), ~$180/yr sub, 35% reachable via schools/NDIS, 5% SOM
        tam_acc = 450000
        acv = 180.0
        sam_pct = 0.35
        som_pct = 0.05
    elif args.preset == "undispute":
        # Australian merchants facing chargebacks (~85,000), ~$1,200/yr fee savings, 30% online/high-volume, 6% SOM
        tam_acc = 85000
        acv = 1200.0
        sam_pct = 0.30
        som_pct = 0.06
    else:
        tam_acc = args.tam_accounts
        acv = args.acv
        sam_pct = args.sam_pct
        som_pct = args.som_pct

    results = calculate_market_sizing(tam_acc, acv, sam_pct, som_pct)

    if args.json:
        print(json.dumps(results, indent=2))
        return

    print("=" * 72)
    print(" 📊 BOTTOM-UP MARKET SIZING ANALYSIS (TAM / SAM / SOM)")
    print("=" * 72)
    print(f" Account Universe:  {tam_acc:,} accounts")
    print(f" Annual Contract:    ${acv:,.2f} / year (ACV)")
    print(f" SAM Reach Filter:   {sam_pct*100:.1f}%")
    print(f" SOM 3-Year Capture: {som_pct*100:.1f}%")
    print("-" * 72)
    print(f" TAM (Total Addressable):       {format_currency(results['tam']['total_value_aud']):<10} ({results['tam']['total_accounts']:,} accounts)")
    print(f" SAM (Serviceable Addressable): {format_currency(results['sam']['serviceable_value_aud']):<10} ({results['sam']['serviceable_accounts']:,} accounts)")
    print(f" SOM (Serviceable Obtainable):  {format_currency(results['som']['obtainable_value_aud']):<10} ({results['som']['obtainable_accounts']:,} accounts)")
    print("-" * 72)
    print(" 📈 3-YEAR SOM SENSITIVITY RANGES:")
    scen = results['sensitivity_scenarios']
    print(f"   • Conservative (Low):  {format_currency(scen['conservative']['som_value']):<9} ({scen['conservative']['som_accounts']:,} accounts)")
    print(f"   • Base Case (Target):  {format_currency(scen['base']['som_value']):<9} ({scen['base']['som_accounts']:,} accounts)")
    print(f"   • Aggressive (High):   {format_currency(scen['aggressive']['som_value']):<9} ({scen['aggressive']['som_accounts']:,} accounts)")
    print("=" * 72)

if __name__ == "__main__":
    main()
