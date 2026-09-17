#!/usr/bin/env python3
"""
Traction Channels & Bullseye ICE Scorer

Scores and ranks candidate customer acquisition channels from Gabriel Weinberg's
19 Traction Channels using the ICE framework (Impact, Confidence, Ease) to select
the 3-5 channels for the Bullseye Middle Ring.

Usage:
  python3 growth/traction-channels-bullseye/scripts/score_traction_channels.py
  python3 growth/traction-channels-bullseye/scripts/score_traction_channels.py --preset amlhive
  python3 growth/traction-channels-bullseye/scripts/score_traction_channels.py --json
"""

import argparse
import json
import sys

DEFAULT_CHANNELS = [
    {"channel": "SEO (Programmatic ASIC pages)", "impact": 9, "confidence": 8, "ease": 7, "notes": "Rank for entity search queries"},
    {"channel": "Engineering as Marketing (Free AML Checker)", "impact": 8, "confidence": 8, "ease": 8, "notes": "Free audit-readiness tool"},
    {"channel": "Direct Sales (Outbound to law firms)", "impact": 9, "confidence": 7, "ease": 6, "notes": "Targeted partner outreach"},
    {"channel": "Content Marketing (Regulatory Guides)", "impact": 7, "confidence": 8, "ease": 8, "notes": "AUSTRAC deadline playbooks"},
    {"channel": "SEM / Google Search Ads", "impact": 7, "confidence": 7, "ease": 7, "notes": "High-intent buyer keywords"},
    {"channel": "Business Development (Practice software)", "impact": 9, "confidence": 6, "ease": 5, "notes": "Integrate with legal practice tools"},
    {"channel": "Email Marketing (Compliance newsletter)", "impact": 6, "confidence": 8, "ease": 8, "notes": "Weekly regulatory briefing"},
    {"channel": "Social & Display Ads (LinkedIn)", "impact": 7, "confidence": 6, "ease": 7, "notes": "Target MLROs and managing partners"},
    {"channel": "Speaking Engagements (Industry webinars)", "impact": 7, "confidence": 7, "ease": 6, "notes": "Present at CPA/Law Society events"},
    {"channel": "Affiliate / Referral (Compliance consultants)", "impact": 8, "confidence": 7, "ease": 6, "notes": "20 percent commission to advisors"}
]

def score_channels(channels: list) -> list:
    scored = []
    for c in channels:
        ice = round((c["impact"] + c["confidence"] + c["ease"]) / 3.0, 2)
        scored.append({
            "channel": c["channel"],
            "impact": c["impact"],
            "confidence": c["confidence"],
            "ease": c["ease"],
            "ice_score": ice,
            "notes": c.get("notes", "")
        })
    return sorted(scored, key=lambda x: x["ice_score"], reverse=True)

def main():
    parser = argparse.ArgumentParser(description="Score traction channels with Bullseye ICE framework.")
    parser.add_argument("--preset", choices=["amlhive", "default"], default="default", help="Preset candidate list")
    parser.add_argument("--top", type=int, default=5, help="Number of channels to highlight for Middle Ring (default 5)")
    parser.add_argument("--json", action="store_true", help="Output raw JSON")

    args = parser.parse_args()

    ranked = score_channels(DEFAULT_CHANNELS)

    if args.json:
        print(json.dumps(ranked, indent=2))
        return

    print("\n================================================================================")
    print("🎯 Bullseye Framework: 19 Traction Channels ICE Ranking")
    print("================================================================================")
    print(f"{'Rank':<5} | {'Traction Channel':<40} | {'Imp':<4} | {'Conf':<4} | {'Ease':<4} | {'ICE':<5}")
    print("--------------------------------------------------------------------------------")
    for idx, c in enumerate(ranked, 1):
        ring_marker = "🎯 Middle Ring" if idx <= args.top else "  Outer Ring"
        print(f"{idx:<5} | {c['channel']:<40} | {c['impact']:<4} | {c['confidence']:<4} | {c['ease']:<4} | {c['ice_score']:<5} ({ring_marker})")
    print("================================================================================")
    print(f"👉 Recommendation: Run 2-week tests on the top {args.top} Middle Ring channels.")
    print("================================================================================\n")

if __name__ == "__main__":
    main()
