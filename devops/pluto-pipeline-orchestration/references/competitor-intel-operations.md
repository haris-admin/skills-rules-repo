# Competitor Intel Pipeline Operations

## Cron: `1a13a2d49682` — 5:07 AM AEST daily

This stage runs between Morning Research (05:05) and Cross-Chamber Synthesis (05:10).

## Script

`competitor_intel.py` (9,348 bytes) in `~/.hermes/scripts/`

## Output

`competitor_intel_YYYY-MM-DD.json` in `~/.hermes/research_outputs/`

## What It Tracks

**21 competitors across categories:**

| Category | Competitors | Portfolio Project |
|----------|-------------|-------------------|
| AML/AUSTRAC | Arctic Intelligence, First AML | AML Hive |
| PSP Licensing | Change Financial, others | PayLicence AU |
| CGT/Digital Assets | Various | ExitLens AU |
| InsurTech | Various | Portfolio monitoring |

## Signal Types

- `funding` — capital raises, M&A activity
- `acquisition` — company acquisitions
- `product_launch` — new products or features
- `partnership` — strategic alliances
- `regulatory` — compliance actions, licensing

## Output JSON Schema

```json
{
  "date": "YYYY-MM-DD",
  "generated_at": "2026-06-10T05:07:21.338129",
  "competitors_tracked": 21,
  "hits": 4,
  "signals": [
    {
      "competitor": "Arctic Intelligence",
      "category": "aml_austrac",
      "portfolio_project": "AML Hive",
      "signals": ["funding", "acquisition", "product_launch"],
      "snippet": "truncated source text from the episode that triggered the signal"
    }
  ]
}
```

## Downstream Consumers

1. **Morning Briefing** (`morning-briefing-YYYY-MM-DD.md`) — "Competitor Watch" section with🔥/🌤/❄️ indicators
2. **Cross-Chamber Synthesis** (05:10) — competitor signals inform chamber confidence ratings

## Verification

```bash
cat ~/.hermes/research_outputs/competitor_intel_$(date +%Y-%m-%d).json | \
  python3 -c "import json,sys; d=json.load(sys.stdin); print(f'Hits: {d[\"hits\"]}/{d[\"competitors_tracked\"]} competitors, {len(d[\"signals\"])} signals')"
```

## Pitfalls

- Web scraping reliability: may not find hits for all 21 competitors every day
- Signal deduplication: the same news story could trigger multiple competitor categories
- Empty runs: the script handles this gracefully (generates valid JSON with hits=0)
- 401 auth failures: if the Hermes Gateway auth is down, competitor intel will fail alongside other pipeline stages (documented systemic failure)
