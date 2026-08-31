---
name: aml-ubo-investigation
description: "AUSTRAC/FATF-compliant UBO investigation methodology using ASIC extracts, ABN Lookup, and corporate structure analysis"
version: 1.1.0
author: Hivey (AML Expert) + Codex Review
tags: [aml, austrac, fatf, ubo, beneficial-ownership, compliance, corporate]
---

# AML UBO Investigation — Methodology

## Trigger Conditions
- User provides an ASIC company extract (PDF)
- User asks to trace UBO (Ultimate Beneficial Owner)
- User asks to check corporate connections between entities
- User mentions AUSTRAC, FATF, KYMAC, Tranche 2

## AUSTRAC Legal Framework

Under AUSTRAC's AML/CTF Rules **Chapter 8** and **FATF Recommendation 24** (Transparency of Beneficial Ownership):

- **UBO Definition:** The natural person(s) who ultimately own or control a legal entity
- **Ownership threshold:** >25% of shares or voting rights
- **Control test:** Power to appoint/remove directors, veto decisions, or exercise significant influence
- **Look-through requirement:** Must examine every layer of ownership, including trusts and nominee arrangements
- **FATF Rec 10:** CDD inquiry — governs how to verify identity and trace ownership
- **FATF Rec 24:** Legal-person transparency — corporate ownership and control structures
- **FATF Rec 25:** Trust transparency — applies when a trust is the beneficial holder

## ⚠️ CRITICAL PITFALL: Do NOT name the director as UBO without tracing the ownership chain

**This is the single most common mistake.** Being the sole director and secretary does NOT by itself establish ultimate ownership or effective control. The registered shareholder's ownership chain must be resolved BEFORE naming a UBO.

Correct approach:
1. First, trace through every corporate layer to find the natural person(s)
2. Only if evidence establishes qualifying ownership (>25% shares or voting rights) OR actual ultimate control, record that person as UBO
3. If the ownership chain cannot be resolved but the person is the sole director/SMO, record them as **Senior Managing Official** (SMO fallback under FATF Rec 10), NOT as UBO
4. Document WHY the chain could not be resolved and what steps were taken

## Investigation Steps

### Step 1: Extract Key Data from ASIC Extract

```
Company Name: [Name] (ACN: [Number])
ABN: [Number]
Status: [Registered/Deregistered]
Type: [Proprietary/Public/etc.]
Registered: [State]
Registration Date: [Date]
```

### Step 2: Identify the Shareholder Chain

From the **Members & Share Structure** section:
- Number of shares issued
- Share class (ORD, etc.)
- Who holds them — look for **beneficially held** flag
- ⚠️ **"Not beneficially held"** — this is a TRACING TRIGGER, not proof of a nominee arrangement. It means the registered member does NOT hold the shares for its own benefit, but it DOES NOT identify the beneficial owner or prove a bare nominee or particular trust arrangement.
- Next step: Obtain the member register and nominee, trust, or custody documents, then trace the principal and any relevant trustee, beneficiaries, appointor, and controllers through to natural persons.

### Step 3: Identify Officeholders

From the **Officeholders** section:
- Directors (name, address, date of birth, place of birth)
- Secretaries
- ⚠️ Birthplace ≠ Citizenship ≠ Automatic ECDD. A foreign birthplace documented on ASIC extract does NOT confirm citizenship, residence, or automatically trigger enhanced cross-border CDD. Verify nationality, residence, identity and address, then apply risk-based country, PEP, sanctions, adverse-media, source-of-funds and product-risk checks.

### Step 4: Map the Corporate Structure

```
Operating Entity (Tier 1)
  └── 100% owned by Holding Entity (Tier 2) — shares "not beneficially held"
       └── MEMBER REGISTER needed → Who are the natural persons?
            ├── If trust: identify trustee, beneficiaries, appointor
            ├── If nominee: identify principal
            └── UBO = Natural person controlling the chain
```

### Step 5: Contextual Factor Assessment (Not "Red Flags")

⚠️ **Codex Correction:** Do NOT treat ordinary features as standalone AML red flags. These are CONTEXTUAL FACTORS that only matter when combined with inconsistencies or another risk nexus:

| Factor | What it actually means | When it matters |
|--------|----------------------|-----------------|
| Shares not beneficially held | Tracing trigger — need documents | Always needs investigation but not automatically suspicious |
| Two-company structure | Standard Pty Ltd + Holding Co structure | Only a flag if combined with opacity, unexplained purpose, or adverse info |
| Accountant's registered office | Common small-business pattern | Only relevant if differs from actual operations without explanation |
| 4.5 years since registration | Normal operating history | Not a flag unless combined with unexplained inactivity |
| Foreign birthplace | Fact to verify | Not a flag — verify nationality + residence first |
| Missing ABN for holding company | Normal — trustee companies often lack ABN | Do NOT infer dormancy. A company can lack ABN while owning assets, receiving passive income, or acting as trustee or nominee. |

**Focus the risk assessment on:** unresolved beneficial holder, opaque control, unexplained purpose or source of funds, and discrepancies between declared and observed activity.

### Step 6: Check Public Records

1. **ABN Lookup** (abr.business.gov.au) — check ABN status, GST registration, entity type
2. **ASIC Connect** (connectonline.asic.gov.au) — pull extracts for all related entities
3. **Check ACN for parent/holding entities** — if ACN exists but no ABN, entity may be a trustee company. Do NOT infer dormancy.
4. **Search director names** — check for other directorships, related entities
5. **Geographic analysis** — check postcodes, proximity to related entities
6. **Trust searches** — if nominee/trust arrangement suspected, search for trust name variations, corporate trustees

### Step 7: UBO Determination (Corrected Methodology)

Apply the four-part test AFTER resolving all layers:

1. **Ownership (>25% shares):** After tracing the chain, does a natural person directly/indirectly own >25%?
2. **Control:** Can the person appoint/remove directors or veto decisions?
3. **Senior management:** Are they the CEO, CFO, or key decision-maker?
4. **Other means:** Do they exercise significant influence through other arrangements?

**Resolution hierarchy:**
1. If ownership chain resolves to a natural person → that person is UBO
2. If nominee/trust exists but documents unavailable → record as **Unresolved beneficial ownership**, document steps taken, record SMO as fallback
3. If sole director with unresolved ownership → record director as **Senior Managing Official** (FATF Rec 10 fallback), NOT as UBO

### Step 8: Documentation Requirements

For EACH layer in the chain, document:
- Source of information (ASIC extract, member register, trust deed, etc.)
- Whether the holder is beneficially held or not
- If not: what documents were requested/obtained to trace the beneficial owner
- If documents could not be obtained: why and what alternative steps were taken
- The natural person identified (or statement that it could not be determined)
- The basis for the UBO/SMO determination

## ASIC Extract Parsing Notes

- ACN format: `XXX XXX XXX` (9 digits)
- ABN format: `XX XXX XXX XXX` (11 digits = ACN + "51" prefix for 656... or other prefix)
- "Beneficially held: no" means the registered holder is NOT the true owner — requires further investigation
- Share classes: ORD = Ordinary
- Director/Secretary can be the same person (common in proprietary companies)
- Registered address `C/- [Accounting Firm]` = standard, but obscures location
- A company can lack an ABN while still actively owning assets or acting as trustee — do NOT infer dormancy from ABN Lookup results

## Common Structures and Their UBO Indicators

| Structure | Where to find UBO |
|-----------|-------------------|
| Individual shareholder | Direct: that individual |
| Parent company | Look through to the parent's shareholders |
| Not beneficially held | Tracing trigger — need trust/nominee documents |
| Corporate trustee | UBO is the appointor or director of trustee company |
| Multiple companies, same director | Likely same UBO controlling all — but verify |
| Unresolved chain | Record SMO fallback, document limitations |

## Key Python Patterns For ASIC Extract Analysis

```python
# Parse ASIC extract sections
def parse_asic_extract(text):
    sections = {}
    current_section = None
    for line in text.split('\n'):
        if line.strip().endswith(':') and len(line.strip()) < 50:
            current_section = line.strip().rstrip(':').strip()
            sections[current_section] = []
        elif current_section:
            sections[current_section].append(line.strip())
    return sections

# Extract ACN from text
import re
def extract_acn(text):
    match = re.search(r'ACN[:\s]*(\d{3}\s*\d{3}\s*\d{3})', text)
    return match.group(1).replace(' ', '') if match else None

# Detect nominee flag
def is_nominee(members_section):
    return 'not beneficially' in members_section.lower()
```
