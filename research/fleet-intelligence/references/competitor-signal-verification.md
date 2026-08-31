# Competitor Signal Verification

> How the competitor intel pipeline works, its known false-positive problems, and how to validate signals before reporting.

## Pipeline Overview

The `competitor_intel.py` script (at `~/.hermes/scripts/competitor_intel.py`) runs daily at ~5:07 AM AEST via cron `1a13a2d49682`. It:

1. Loads the competitor database (`~/.hermes/data/competitors.json`) — 21 competitors across 7 categories
2. Loads today's research texts (research JSON, synthesis, actions, podcast_insights.json)
3. Searches for competitor **name tokens** in those texts
4. If found, applies regex signal patterns (funding, acquisition, product_launch, etc.)
5. Outputs `competitor_intel_YYYY-MM-DD.json` → consumed by `morning-briefing-*.md`

## Known False-Positive Problem

**Root cause:** The script matches on individual search tokens, not the full company name.

```python
# From competitor_intel.py line 139-142:
name = comp['name'].lower()           # e.g. "Arctic Intelligence"
name_tokens = name.split()            # ["arctic", "intelligence"]  
search_patterns = [name] + [t for t in name_tokens if len(t) >= 4]
```

For a competitor named "First AML", the search patterns become:
```
["first aml", "first", "aml"]
```

The word `"aml"` triggers a hit on ANY text containing "AML" — including "AML Hive" references in portfolio_mappings, research findings about AUSTRAC, or generic AML compliance discussions.

Similarly:
- **"financial"** triggers hits for **Change Financial** whenever "financial services", "financial institutions", "financial crime" appear
- **"change"** triggers on any text with "change" in it  
- **"intelligence"** triggers for **Arctic Intelligence** on AI-related content
- **"first"** triggers for **First AML** on literally anything described as "first"

**The result:** Once a single-word match fires, the pipeline applies funding/acquisition/product_launch regex patterns to the SAME generic text. Common words like "launched", "announced", "new" in any context trigger all three signals simultaneously — producing the characteristic triple-hit (💰🏢🚀) on every tracked competitor in every briefing.

## How to Verify Signals (Before Reporting)

When the briefing shows competitor signals, validate each before treating as real:

### Step 1: Check if it's a false positive
```bash
grep -l "COMPETITOR_NAME" ~/.hermes/research_outputs/*.json ~/.hermes/research_outputs/*.md 2>/dev/null
```

If only the synthetic briefing files (competitor_intel, morning-briefing) match and no source research file does, it's a false positive triggered by generic word matching.

### Step 2: For true mentions, verify the signal type
```bash
# Check competitor_intel JSON for the snippet
cat ~/.hermes/research_outputs/competitor_intel_$(date +%F).json | python3 -c "
import json,sys
d=json.load(sys.stdin)
for s in d['signals']:
    if 'COMPETITOR_NAME' in s['competitor']:
        print(json.dumps(s, indent=2))
"
```

### Step 3: Search news for actual events
Use Google News RSS to verify specific claims:
```bash
curl -sL --max-time 15 -A "Mozilla/5.0" \
  "https://news.google.com/rss/search?q=%22COMPETITOR+NAME%22+%28funding+OR+acqui*+OR+launch%29+2026&hl=en-AU&gl=AU&ceid=AU:en" \
  | grep -oP '<title>(.*?)</title>' | grep -v 'Google News'
```

### Step 4: Signal confidence tiers
| Tier | Criteria | Action in Briefing |
|------|----------|-------------------|
| 🔴 Confirmed | 3+ credible news sources verify the event | Report with source links |
| 🟡 Probable | Single credible source or strong secondary evidence | Report with caveat |
| 🟢 Pipeline only | Only competitor_intel.json has it | Flag as "unverified pipeline signal" or suppress |

## Real Signal Case Study: Change Financial × Paymentology

On April 21, 2026, **Change Financial** (ASX:CCA) partnered with **Paymentology** to bring card processing to Australia. This was a real 🚀 signal:

- **What happened:** Paymentology entered the Australian market through Change Financial, combining its processing platform with Change Financial's BIN sponsorship, Mastercard Principal Issuer status, and regulatory support.
- **Who it impacts:** PayLicence AU — same PSP licensing/acquiring space
- **Why it matters:** Creates a one-stop card issuing + compliance shop for inbound fintechs
- **Signal type:** Partnership/Product Launch (not funding or acquisition)
- **Sources:** IT Brief Australia, PYMNTS.com, Media OutReach Newswire (3 independent sources)

This signal was correctly detected by the pipeline because "Change Financial" appeared in research texts alongside partnership language. But the pipeline ALSO incorrectly tagged it with "funding" and "acquisition" — those were false positives from generic word matching.

## Verification of False Positives (June 10-11, 2026)

As of June 11, 2026, all three flagged competitors (Arctic Intelligence, First AML, Change Financial) showed identical signal patterns (💰 funding + 🏢 acquisition + 🚀 product launch). Investigation confirmed:

- **Arctic Intelligence:** Named in FinCrimeTech50 2026 (legitimate mention) but NO actual funding/acquisition/launch event found in news. The triple-hit was noise.
- **First AML:** Last confirmed funding was $30M Series B (Nov 2021). AU operation launch was March 2025. Named in FinCrimeTech50 2026. No new transactional events found.
- **Change Financial:** Had ONE real signal (Paymentology partnership) but pipeline misclassified it as funding+acquisition+launch instead of just partnership/launch.

## Recommendation

The `competitor_intel.py` script should be patched to:
1. Require **at least 2-word matching** for competitors with single-word name tokens (e.g., "First" AND "AML" must both appear)
2. Exclude competitor names from matching against their OWN portfolio project names (e.g., "AML Hive" should not trigger "First AML")
