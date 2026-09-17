#!/usr/bin/env python3
"""
BCP Resilience Auditor CLI
Evaluates business continuity, disaster recovery, and operational resilience readiness
against ISO 22301, APRA CPS 230, and SOC 2 CC9.1 criteria.
"""

import argparse
import json
import sys
from typing import Any, Dict, List


def get_demo_inventory() -> Dict[str, Any]:
    """Returns a realistic B2B SaaS / RegTech disaster recovery and BCP inventory."""
    return {
        "organization": "AMLHive B2B RegTech & Compliance Platform",
        "jurisdiction": "Australia (APRA CPS 230 / AUSTRAC / Privacy Act)",
        "incident_command": {
            "incident_commander": {"primary": "Lead Solutions Architect", "alternate": "Head of Engineering"},
            "technical_ops_lead": {"primary": "Senior DevOps Engineer", "alternate": "Staff Backend Engineer"},
            "communications_lead": {"primary": "Head of Product", "alternate": "Customer Success Director"},
            "legal_compliance_lead": {"primary": "Compliance Officer", "alternate": "External Legal Counsel"},
            "out_of_band_channel_configured": True,
            "independent_statuspage_configured": True,
        },
        "services": [
            {
                "id": "CBF-01",
                "name": "Real-Time AML/PEP Screening API",
                "tier": 0,
                "mtd_minutes": 60,
                "rto_minutes": 15,
                "rpo_minutes": 5,
                "multi_region_failover": True,
                "backup_tested_days_ago": 7,
                "single_points_of_failure": [],
                "vendor_dependencies": [
                    {"name": "AWS Sydney Primary", "has_redundancy": True},
                    {"name": "Auth0 / JWT Provider", "has_redundancy": True},
                ],
            },
            {
                "id": "CBF-02",
                "name": "Entity Onboarding & UBO Graph Verification",
                "tier": 1,
                "mtd_minutes": 240,
                "rto_minutes": 60,
                "rpo_minutes": 15,
                "multi_region_failover": True,
                "backup_tested_days_ago": 14,
                "single_points_of_failure": [],
                "vendor_dependencies": [
                    {"name": "ASIC Registry API", "has_redundancy": False, "has_offline_fallback": True},
                    {"name": "ABN Lookup API", "has_redundancy": True},
                ],
            },
            {
                "id": "CBF-03",
                "name": "Customer Reporting & PDF Certificate Generator",
                "tier": 1,
                "mtd_minutes": 720,
                "rto_minutes": 180,
                "rpo_minutes": 30,
                "multi_region_failover": False,
                "backup_tested_days_ago": 45,
                "single_points_of_failure": ["Single S3 Bucket in ap-southeast-2"],
                "vendor_dependencies": [
                    {"name": "SendGrid Transactional Email", "has_redundancy": False, "has_offline_fallback": False}
                ],
            },
            {
                "id": "CBF-04",
                "name": "Daily RegTech Reference DB & Sanctions Sync",
                "tier": 2,
                "mtd_minutes": 1440,
                "rto_minutes": 360,
                "rpo_minutes": 60,
                "multi_region_failover": False,
                "backup_tested_days_ago": 20,
                "single_points_of_failure": [],
                "vendor_dependencies": [
                    {"name": "AUSTRAC / DFAT Sanctions Feeds", "has_redundancy": False, "has_offline_fallback": True}
                ],
            },
            {
                "id": "CBF-05",
                "name": "Monthly Billing & Subscriptions Engine",
                "tier": 2,
                "mtd_minutes": 2880,
                "rto_minutes": 720,
                "rpo_minutes": 1440,
                "multi_region_failover": False,
                "backup_tested_days_ago": 60,
                "single_points_of_failure": [],
                "vendor_dependencies": [
                    {"name": "Stripe Payments", "has_redundancy": True}
                ],
            },
        ],
    }


def audit_bcp(inventory: Dict[str, Any]) -> Dict[str, Any]:
    """Runs a complete resilience audit on the provided inventory."""
    findings: List[Dict[str, Any]] = []
    total_score = 100
    deductions = 0

    # 1. Audit Incident Command Readiness
    ic = inventory.get("incident_command", {})
    required_roles = ["incident_commander", "technical_ops_lead", "communications_lead", "legal_compliance_lead"]
    for role in required_roles:
        role_data = ic.get(role, {})
        if not role_data.get("primary"):
            deductions += 10
            findings.append({
                "severity": "CRITICAL",
                "category": "Incident Command",
                "target": role,
                "issue": f"Primary contact for {role.replace('_', ' ').title()} is not assigned.",
                "remediation": f"Designate a primary contact for {role}.",
            })
        if not role_data.get("alternate"):
            deductions += 5
            findings.append({
                "severity": "HIGH",
                "category": "Incident Command",
                "target": role,
                "issue": f"No alternate (deputy) assigned for {role.replace('_', ' ').title()}.",
                "remediation": f"Assign a backup/alternate responder for {role} to avoid single person risk.",
            })

    if not ic.get("out_of_band_channel_configured"):
        deductions += 10
        findings.append({
            "severity": "HIGH",
            "category": "Communications",
            "target": "Out-of-Band Channels",
            "issue": "No out-of-band communication channel (e.g. Signal) configured for emergency response.",
            "remediation": "Establish a verified out-of-band emergency channel isolated from corporate SSO.",
        })

    if not ic.get("independent_statuspage_configured"):
        deductions += 5
        findings.append({
            "severity": "MEDIUM",
            "category": "Communications",
            "target": "Public Statuspage",
            "issue": "Public statuspage is hosted on internal infrastructure or relies on primary auth.",
            "remediation": "Deploy a hosted external status page with hardware-key authentication.",
        })

    # 2. Audit Services & Critical Business Functions (CBFs)
    services = inventory.get("services", [])
    for s in services:
        sid = s.get("id", "UNKNOWN")
        name = s.get("name", "Unnamed")
        tier = s.get("tier", 2)
        rto = s.get("rto_minutes", 0)
        mtd = s.get("mtd_minutes", 0)
        backup_days = s.get("backup_tested_days_ago", 999)
        spofs = s.get("single_points_of_failure", [])
        vendors = s.get("vendor_dependencies", [])

        # Check RTO <= MTD
        if rto > mtd:
            deductions += 20
            findings.append({
                "severity": "CRITICAL",
                "category": "Recovery Targets",
                "target": f"{sid}: {name}",
                "issue": f"Recovery Time Objective ({rto} min) exceeds Maximum Tolerable Downtime ({mtd} min).",
                "remediation": f"Architectural violation: lower RTO below {mtd} min or elevate MTD.",
            })
        elif rto == mtd:
            deductions += 5
            findings.append({
                "severity": "MEDIUM",
                "category": "Recovery Targets",
                "target": f"{sid}: {name}",
                "issue": f"Zero Work Recovery Time (WRT) safety margin (RTO = MTD = {rto} min).",
                "remediation": "Target RTO at <= 50 percent of MTD to allow for validation and data catch-up.",
            })

        # Tier 0/1 Multi-Region Requirement
        if tier == 0 and not s.get("multi_region_failover"):
            deductions += 15
            findings.append({
                "severity": "CRITICAL",
                "category": "Infrastructure Resilience",
                "target": f"{sid}: {name}",
                "issue": f"Tier 0 mission-critical service lacks automated multi-region failover.",
                "remediation": "Implement cross-region active-active or hot-standby replication.",
            })

        # Backup Testing Recency
        max_allowed_days = 30 if tier in (0, 1) else 90
        if backup_days > max_allowed_days:
            deductions += 8
            findings.append({
                "severity": "HIGH",
                "category": "Data Recovery",
                "target": f"{sid}: {name}",
                "issue": f"Backup restoration drill last conducted {backup_days} days ago (exceeds {max_allowed_days}-day limit).",
                "remediation": "Execute automated snapshot restoration test in isolated sandbox.",
            })

        # Single Points of Failure
        for spof in spofs:
            deductions += 8
            findings.append({
                "severity": "HIGH",
                "category": "Single Point of Failure",
                "target": f"{sid}: {name}",
                "issue": f"Identified SPOF: {spof}",
                "remediation": f"Introduce replication, multi-AZ clustering, or automated fallback for {spof}.",
            })

        # Unbuffered Vendor Dependencies
        for v in vendors:
            if not v.get("has_redundancy") and not v.get("has_offline_fallback"):
                deductions += 6
                findings.append({
                    "severity": "MEDIUM",
                    "category": "Third-Party Risk (CPS 230)",
                    "target": f"{sid}: {name} -> {v.get('name')}",
                    "issue": f"Critical vendor dependency '{v.get('name')}' has no redundancy and no offline fallback.",
                    "remediation": f"Implement degraded queueing mode, secondary vendor contract, or cached fallback.",
                })

    final_score = max(0, total_score - deductions)

    # Determine readiness level
    if final_score >= 85:
        status = "EXEMPLARY (Audit Ready)"
    elif final_score >= 70:
        status = "SUBSTANTIAL (Minor Gaps to Remediate)"
    elif final_score >= 50:
        status = "VULNERABLE (Requires High-Priority Remediation)"
    else:
        status = "CRITICAL NON-COMPLIANCE (Fails APRA CPS 230 / ISO 22301)"

    return {
        "organization": inventory.get("organization", "Unknown"),
        "jurisdiction": inventory.get("jurisdiction", "Global"),
        "score": final_score,
        "readiness_status": status,
        "total_deductions": deductions,
        "findings_count": len(findings),
        "findings": findings,
    }


def print_report(audit_result: Dict[str, Any]) -> None:
    """Prints a formatted human-readable terminal report."""
    print("=" * 72)
    print("🛡️  BUSINESS CONTINUITY IN A BOX — OPERATIONAL RESILIENCE AUDIT")
    print("=" * 72)
    print(f"Organization:  {audit_result['organization']}")
    print(f"Jurisdiction:  {audit_result['jurisdiction']}")
    print(f"BCP Score:     {audit_result['score']} / 100")
    print(f"Readiness:     {audit_result['readiness_status']}")
    print(f"Total Findings:{audit_result['findings_count']}")
    print("-" * 72)

    if not audit_result["findings"]:
        print("✅ No resilience gaps detected. System meets strict BCP/DR standards.")
    else:
        print("Identified Resilience & Compliance Gaps:\n")
        severity_order = {"CRITICAL": 1, "HIGH": 2, "MEDIUM": 3, "LOW": 4}
        sorted_findings = sorted(
            audit_result["findings"],
            key=lambda x: severity_order.get(x["severity"], 99)
        )

        for idx, f in enumerate(sorted_findings, 1):
            severity_icon = {
                "CRITICAL": "🚨 [CRITICAL]",
                "HIGH": "⚠️  [HIGH]",
                "MEDIUM": "⚡ [MEDIUM]",
                "LOW": "ℹ️  [LOW]",
            }.get(f["severity"], "[UNKNOWN]")

            print(f"{idx}. {severity_icon} {f['category']} | {f['target']}")
            print(f"   Issue:       {f['issue']}")
            print(f"   Action:      {f['remediation']}")
            print()

    print("=" * 72)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Business Continuity in a Box: Resilience and BCP Auditor"
    )
    parser.add_argument(
        "--demo",
        action="store_true",
        help="Run audit against realistic demo RegTech / SaaS platform (AMLHive)",
    )
    parser.add_argument(
        "--inventory",
        type=str,
        help="Path to JSON file containing BCP service inventory",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results in machine-readable JSON format",
    )

    args = parser.parse_args()

    if args.demo or not args.inventory:
        data = get_demo_inventory()
    else:
        try:
            with open(args.inventory, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            print(f"Error loading inventory file: {e}", file=sys.stderr)
            sys.exit(1)

    result = audit_bcp(data)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print_report(result)


if __name__ == "__main__":
    main()
