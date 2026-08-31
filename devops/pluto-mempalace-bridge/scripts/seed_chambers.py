#!/usr/bin/env python3
"""Seed Pluto's 16-chamber MemPalace with initial knowledge.

Run this to rebuild all chambers from scratch after a ChromaDB reset.
Creates 16 collections and populates 10 previously-empty chambers with
30 seed documents covering portfolio domains.

Usage:
    python3 seed_chambers.py
"""

import chromadb
import json
from chromadb.config import Settings
from chromadb.utils import embedding_functions
from datetime import datetime, timezone

DB = "/mnt/c/Users/habib/.mempalace/palace"

# ── Chamber definitions ──
CHAMBER_SPECS = {
    "regulatory-ai": {"description": "AI Regulation & Compliance — EU AI Act, AU guardrails, global governance", "tags": "ai,regulation,compliance,eu-ai-act,guardrails"},
    "fintech-aml": {"description": "FinTech & AML/CTF — AUSTRAC, Tranche 2, KYC, CDD, BNPL licensing", "tags": "fintech,aml,ctf,austrac,tranche2,kyc"},
    "agentic-security": {"description": "Agentic AI Security — red-teaming, OWASP LLM, A2A protocol, multi-agent attacks", "tags": "agentic,security,red-team,owasp,a2a,multi-agent"},
    "cloud-infra": {"description": "Cloud & Infrastructure — repatriation, AWS/GCP/Azure, colocation, cost optimization", "tags": "cloud,infrastructure,repatriation,aws,gcp,azure"},
    "digital-identity": {"description": "Digital Identity — AGDIS, CDR, TDIF, verifiable credentials, identity verification", "tags": "digital-identity,agdis,cdr,tdif,verifiable-credentials"},
    "data-sovereignty": {"description": "Data Sovereignty & Privacy — CPS 234, SOCI Act, Privacy Act, data residency", "tags": "data-sovereignty,privacy,cps234,soci,residency"},
    "startup-vc": {"description": "Startup & VC Ecosystem — AU startups, funding trends, market opportunities, exits", "tags": "startup,vc,funding,valuation,exit,au"},
    "sovereign-ai": {"description": "Sovereign AI & Government — local AI, gov procurement, AUKUS, defence tech", "tags": "sovereign-ai,government,aukus,procurement,local-ai"},
    "regtech-tools": {"description": "RegTech Platforms — compliance workflow, regulatory monitoring, RegStack", "tags": "regtech,compliance-platform,regstack,workflow"},
    "agent-architecture": {"description": "Agent Architecture & Skills — patterns, SKILL.md ecosystem, tool design, frameworks", "tags": "agent-architecture,skills,tools,patterns,framework"},
    "payments-npp": {"description": "Payments & NPP — PayTo, BNPL, merchant acquiring, real-time payments, NPP reform", "tags": "payments,npp,payto,bnpl,real-time"},
    "insurtech": {"description": "InsurTech & Insurance — distribution reforms, CPS 230, underwriting AI", "tags": "insurtech,insurance,cps230,distribution,underwriting"},
    "agent-observability": {"description": "Agent Observability & SRE — monitoring, reliability, production, AgentSRE", "tags": "agent-observability,sre,monitoring,reliability,agentsre"},
    "critical-infra": {"description": "Critical Infrastructure & OT — mining OT, energy, SOCI, IoT security", "tags": "critical-infra,ot,mining,energy,soci,iot"},
    "legal-professional": {"description": "Legal & Professional Services — LegalTech, accounting compliance, real estate regulation", "tags": "legal,professional,legaltech,accounting,real-estate"},
    "voice-creative": {"description": "Voice, Audio & Creative AI — TTS, AI music, voice overviews, creative tools", "tags": "voice,audio,creative,tts,music,overview"},
}

# ── Seed data for empty chambers ──
SEEDS = {
    "digital-identity": [
        {"title": "AGDIS Integration Ready — Private Sector Deadline November 2026",
         "content": "The Australian Government Digital Identity System (AGDIS) expands to private sector Nov 2026. Key requirements: OAuth 2.0/OIDC PKCE, JWT validation, consent framework, biometric binding. Convergence with CDR (100+ accredited data recipients) creates unified identity+data sharing ecosystem.",
         "confidence": "high", "type": "trend"},
        {"title": "CDR Sunset — Screen-Scraping Phaseout July 2026",
         "content": "CDR screen-scraping sunset July 2026. All data holders must transition to accredited CDR APIs. 100+ recipients, 300% YoY growth. Consulting costs $30-80K, takes 6-12 months. Gap: No self-service accreditation toolkit exists.",
         "confidence": "high", "type": "opportunity"},
        {"title": "Verifiable Credentials — Global Standards Convergence",
         "content": "W3C VC and DID standards converging with government identity frameworks. AU's AGDIS aligns with ISO 18013-5. EU's eIDAS 2.0 mandates Digital Identity Wallets by 2026. AGDIS could become AU node in global interoperable identity network.",
         "confidence": "medium", "type": "trend"},
    ],
    "data-sovereignty": [
        {"title": "APRA CPS 234 — Information Security Mandate",
         "content": "CPS 234 requires all APRA-regulated entities to maintain info security capabilities: board-level roles, detection/response capability, third-party risk, 72-hour incident notification. APRA's April 2026 letter signaled increased enforcement.",
         "confidence": "high", "type": "regulatory"},
        {"title": "SOCI Act — 11 Critical Infrastructure Sectors",
         "content": "SOCI Act covers data storage/processing, financial services, energy, communications, transport. Mandatory incident reporting (12-72hr), asset register, government 'last resort' powers. Cloud repatriation partially driven by SOCI compliance.",
         "confidence": "high", "type": "regulatory"},
        {"title": "Privacy Act Review — Proposed Data Localization",
         "content": "Strengthened data localization, expanded individual rights (GDPR-like), penalties up to $50M or 30% turnover. Key: mandatory PIAs, 'right to erasure', enhanced consent, direct right of action. Aligns AU closer to EU GDPR.",
         "confidence": "high", "type": "regulatory"},
    ],
    "startup-vc": [
        {"title": "AU RegTech Ecosystem — 2026 Landscape",
         "content": "RegTech growth driven by cascading regulatory waves. Key players: FrankieOne (enterprise KYC/AML), ComplyAdvantage ($50K+ AML screening), GreenID (identity verification). 60%+ SMEs use spreadsheets. Gap: $540M AUD SAM with no dominant player.",
         "confidence": "high", "type": "market"},
        {"title": "AU VC Funding — RegTech & Sovereign AI Hot",
         "content": "Pre-seed $300-500K for AI infra, Seed $1-2M for regtech with revenue, Series A at $1M+ ARR. Blackbird, AirTree active. Gov grants: NSW Digital Transformation Fund $50-200K. Exits: Strategic acquisitions $15-50M more likely than IPOs.",
         "confidence": "medium", "type": "market"},
        {"title": "76% Agent Deployments Fail — $3.8B Market Signal",
         "content": "2026 analysis of 847 deployments: 76% fail in production. Agent-specific failures: hallucinations, broken tool chains, context loss, silent errors. Traditional APM can't detect. LangSmith is dev tooling. $3.8B market at 36% CAGR. AgentSRE concept viable.",
         "confidence": "high", "type": "opportunity"},
    ],
    "regtech-tools": [
        {"title": "RegStack — Multi-Regulation SME Platform",
         "content": "TAM: $8.7B globally, $1.2B AU. SAM: $540M (63K SMEs). MVP: 6 months, $80-120K bootstrap viable. Beachhead: real estate (15K agencies, Tranche 2 July 2026). Revenue: $450K ARR Y1 → $5.4M Y3. Exit: $15-30M to FrankieOne/Xero.",
         "confidence": "high", "type": "opportunity"},
        {"title": "Tranche 2 — 35,000 New Entities July 2026",
         "content": "AUSTRAC Tranche 2 brings real estate agents, lawyers, accountants, trust/company providers, precious metal dealers under regulation. Most have zero compliance infrastructure. Solutions: enterprise ($50K+) or spreadsheets. No mid-market. Window: NOW through Sep 2026.",
         "confidence": "high", "type": "regulatory"},
        {"title": "Regulatory Monitoring Automation — Underserved",
         "content": "AUSTRAC/ASIC/APRA/RBA/ACCC issue 200+ guidance docs annually. Compliance officers spend 10-20hrs/week tracking changes manually. Current tools: RSS, newsletters, $5-15K/year legal platforms. Gap: purpose-built regulatory change monitoring with obligation mapping. $199/mo.",
         "confidence": "medium", "type": "opportunity"},
    ],
    "payments-npp": [
        {"title": "RBA NPP Reform — 13 Measures Including PayTo",
         "content": "13-measure package: mandated PayTo for all NPP participants, standardized dispute resolution, PayTo push for recurring payments, enhanced PayID verification. Creates operational compliance for payment providers. PayTo could displace BPAY.",
         "confidence": "high", "type": "regulatory"},
        {"title": "BNPL Mandatory Credit Licensing — Live June 2025",
         "content": "100+ BNPL providers now require ASIC credit licenses, responsible lending obligations, AFCA membership. Compliance burden ongoing: reporting, credit guide maintenance, hardship procedures, audits. Gap: BNPL-specific compliance workflow templates.",
         "confidence": "high", "type": "regulatory"},
        {"title": "Payment Facilitator Landscape — ~450 Providers",
         "content": "ASIC clarifying regulatory perimeter: designated payment systems, non-bank licensing, interchange review. Landscape fragmenting as fintechs enter acquiring, orchestration, embedded finance. ARPU: $499/mo for compliance tools.",
         "confidence": "medium", "type": "market"},
    ],
    "insurtech": [
        {"title": "Insurance Distribution Reforms — ASIC Consultation",
         "content": "~5,000 intermediaries face new compliance: DDO, target market determinations, claims handling as financial service, conflicted remuneration. APRA CPS 230 adds operational risk requirements. Segment: $18M AUD at $299/mo ARPU.",
         "confidence": "medium", "type": "regulatory"},
        {"title": "APRA CPS 230 — Operational Risk for Insurers",
         "content": "CPS 230 requires: operational risk framework, material service provider management with formal agreements, business continuity including scenario testing, incident notification. Opportunity: RegTech tools for vendor management and incident reporting.",
         "confidence": "high", "type": "regulatory"},
        {"title": "InsurTech Dynamics — Underwriting AI & Climate Risk",
         "content": "Trends: parametric insurance with IoT, AI claims processing (weeks→hours), embedded insurance at POS. ASIC monitoring algorithmic underwriting for fairness. Opportunity: AI audit/explainability tools for insurance underwriting models.",
         "confidence": "medium", "type": "market"},
    ],
    "agent-observability": [
        {"title": "AgentSRE — PagerDuty + Datadog for Agents",
         "content": "TAM: $3.8B (2026), projected $18B by 2031 (36% CAGR). Features: agent tracing, hallucination detection, circuit breakers, fallback chains, rollback, cost optimization. MVP: 6-8 months, $100-150K, pre-seed. Open-source + paid platform. Exit: $20-50M.",
         "confidence": "high", "type": "opportunity"},
        {"title": "Agent Failure Modes — Why 76% Fail",
         "content": "Five failure modes: hallucinations (wrong output to downstream), broken tool chains (silent cascade), context loss (state across turns), silent errors (wrong result, no signal), planning failures (suboptimal action sequences). Traditional APM can't detect.",
         "confidence": "high", "type": "technical"},
        {"title": "Agent Observability Stack — Current Gaps",
         "content": "Current: LangSmith (dev LLM tracing), Helicone (cost/proxy), Arize Phoenix (open-source, maturing), PagerDuty/Datadog (generic, not agent-aware). Gaps: circuit breakers, agent rollback, A/B testing, compliance audit, cost-per-task optimization.",
         "confidence": "medium", "type": "technical"},
    ],
    "critical-infra": [
        {"title": "PitGuard — OT Supply Chain Security",
         "content": "Phase 1 complete: 29 files, markdown security framework (vendor risk assessment, procurement checklists, remote access, firmware integrity). Aligned with SOCI Act. ACSC flagged OT/ICS security as 2026 critical priority.",
         "confidence": "high", "type": "opportunity"},
        {"title": "SOCI Act — Energy Sector Cyber Obligations",
         "content": "Energy sector SOCI obligations: register SCADA/ICS/generation assets, incident reporting (12hr critical, 72hr significant), Critical Infrastructure Risk Management Program. AEMO ISP 2026 highlights cyber risk from distributed energy resources.",
         "confidence": "high", "type": "regulatory"},
        {"title": "GridPass — AEMC ERC0394 Compliance Calculator",
         "content": "15% complete — markdown calculator for energy market participants. AEMC ERC0394 adds obligations for grid batteries, VPPs, demand response. 200+ participants need compliance assessment. Gap: no self-service calculator. Phase 1: free → demand → Phase 2: SaaS.",
         "confidence": "medium", "type": "opportunity"},
    ],
    "legal-professional": [
        {"title": "Tranche 2 Impact — 18,000 Legal Practices",
         "content": "18K Australian legal practices become reporting entities July 2026: enrol with AUSTRAC, appoint AML/CTF officer, conduct ML/TF risk assessment, AML/CTF program, CDD on clients, report suspicious matters. Most have never operated under AML/CTF. $75M AUD segment at $349/mo.",
         "confidence": "high", "type": "regulatory"},
        {"title": "Real Estate Compliance — 15,000 Offices",
         "content": "15K agencies become reporting entities. Current state: Word templates + spreadsheets. Key requirements: identity verification for landlords/tenants, source of funds checks, suspicious matter reporting. Beachhead for RegStack at $249/mo. $45M AUD segment.",
         "confidence": "high", "type": "market"},
        {"title": "Accounting Practice Compliance — 25,000 Firms",
         "content": "25K accounting practices become reporting entities. Unique challenge: dual role as designated service providers AND advisors. Market: $60M AUD at $199/mo ARPU. Xero/MYOB integration for automated CDD from existing records.",
         "confidence": "high", "type": "market"},
    ],
    "voice-creative": [
        {"title": "Pluto Voice Overview Pipeline — TTS Research Briefings",
         "content": "Daily cron (c527fed4a1da, 22:15 AEST) converts research JSONs to spoken MP3 via gTTS/Handy TTS. Outputs: ~/.hermes/voice_outputs/. Multi-topic, finding-level granularity, auto-delivery to Telegram as voice bubbles.",
         "confidence": "high", "type": "technical"},
        {"title": "AI Music & Creative Audio — Suno, HeartMuLa, MusicGen",
         "content": "Suno AI: commercial text-to-music. HeartMuLa: custom lyrics+tags pipeline (Hermes skill). AudioCraft/MusicGen: open-source text-to-music. Use cases: product demos, educational content, podcasts, creative experimentation.",
         "confidence": "medium", "type": "technical"},
        {"title": "ASCII Art & Creative Generation Tooling",
         "content": "Fleet creative toolkit: ASCII art (pyfiglet, cowsay, image-to-ascii), ASCII video (colored MP4/GIF), pixel art (NES/Game Boy/PICO-8 palettes), p5.js sketches (gen art/shaders/3D), Manim CE (3Blue1Brown animations).",
         "confidence": "medium", "type": "technical"},
    ],
}

# ── Execute ──
def main():
    client = chromadb.PersistentClient(path=DB, settings=Settings(anonymized_telemetry=False))
    ef = embedding_functions.DefaultEmbeddingFunction()
    ts = datetime.now(timezone.utc).isoformat()

    # Step 1: Create all 16 chambers
    print("=== Creating 16 Chambers ===")
    for chamber_name, spec in CHAMBER_SPECS.items():
        try:
            client.get_collection(chamber_name, embedding_function=ef)
            print(f"[SKIP] {chamber_name}: already exists")
        except:
            client.create_collection(chamber_name, embedding_function=ef, metadata={"description": spec["description"], "tags": spec["tags"]})
            print(f"[OK] {chamber_name}: created")

    # Step 2: Seed empty chambers
    print("\n=== Seeding Chambers ===")
    seeded = {}
    for chamber_name, seeds in SEEDS.items():
        try:
            coll = client.get_collection(chamber_name, embedding_function=ef)
        except:
            coll = client.create_collection(chamber_name, embedding_function=ef,
                metadata=CHAMBER_SPECS.get(chamber_name, {"description": chamber_name, "tags": ""}))

        ids, docs, metas = [], [], []
        for i, seed in enumerate(seeds):
            doc_id = f"seed_{chamber_name}_{i:03d}"
            ids.append(doc_id)
            docs.append(f"# {seed['title']}\n\n{seed['content']}")
            metas.append({
                "chamber": chamber_name, "title": seed["title"],
                "source": "pluto_seed", "confidence": seed.get("confidence", "medium"),
                "url": seed.get("url", ""), "type": seed.get("type", "trend"),
                "date": ts, "seeded": True,
            })

        coll.add(ids=ids, documents=docs, metadatas=metas)
        seeded[chamber_name] = len(ids)

    print(f"\nSeeded {len(seeded)} chambers with {sum(seeded.values())} documents")
    print(json.dumps(seeded, indent=2))

if __name__ == "__main__":
    main()
