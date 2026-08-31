# Anti-Regulation Signal Sources

Proven Google News RSS query patterns for finding deregulation, opposition, and counter-narrative signals. Use these when the Signal Balance Check detects >5:1 pro-regulation bias.

## Query Catalog

### Australian Deregulation / Red Tape
```
curl -sL --max-time 15 -A "Mozilla/5.0" \
  "https://news.google.com/rss/search?q=Liberal+Party+Australia+deregulation+agenda+red+tape+2026&hl=en-AU&gl=AU&ceid=AU:en"
```
**Proven hits:** Liberal Party "Red Tape Emergency" agenda, AFR "$44B war on red tape", "3 pieces of red tape CEOs hate most"

### CEO / Business Pushback
```
curl -sL --max-time 15 -A "Mozilla/5.0" \
  "https://news.google.com/rss/search?q=Australian+CEOs+regulatory+burden+compliance+costs+pushback&hl=en-AU&gl=AU&ceid=AU:en"
```
**Proven hits:** Directors bracing for rising costs (Roy Morgan), compliance cost surveys

### CGT Reform Opposition
```
curl -sL --max-time 15 -A "Mozilla/5.0" \
  "https://news.google.com/rss/search?q=CGT+capital+gains+tax+reform+criticism+opposition+Australia+2026&hl=en-AU&gl=AU&ceid=AU:en"
```
**Proven hits:** Coalition repeal pledge, "Labor burns political capital", "limit CGT to house flipping", voter backlash

### AI / Innovation Deregulation
```
curl -sL --max-time 15 -A "Mozilla/5.0" \
  "https://news.google.com/rss/search?q=AI+deregulation+innovation+stifling+overreach&hl=en-AU&gl=AU&ceid=AU:en"
```
**Proven hits:** EU "Between Deregulation and Innovation" (Carnegie), JD Vance AI Doctrine, India deregulation

### Global Deregulation Trends
```
curl -sL --max-time 15 -A "Mozilla/5.0" \
  "https://news.google.com/rss/search?q=deregulation+trend+innovation+competitiveness+2026&hl=en-AU&gl=AU&ceid=AU:en"
```
**Proven hits:** US G20 deregulation priorities, global competitiveness angle

### Fintech / Startup Regulatory Burden
```bash
curl -sL --max-time 15 -A "Mozilla/5.0" \
  "https://news.google.com/rss/search?q=fintech+startup+Australia+regulatory+burden+opposition&hl=en-AU&gl=AU&ceid=AU:en"
```

### AML/CTF Compliance Cost & Burden (NEW July 12, 2026 — 48 headlines, 59KB)
```bash
curl -sL --max-time 15 -A "Mozilla/5.0" \
  "https://news.google.com/rss/search?q=AML+compliance+costs+Australia+small+business+burden&hl=en-AU&gl=AU&ceid=AU:en"
```
**Proven hits (July 12, 2026):** This is the SINGLE MOST PRODUCTIVE counter-sweep query for FinTech Regulation topics. Surfaces industry pushback from multiple sectors simultaneously: "CPA launches review into rising regulatory burden" (Accountants Daily), "Professional services face crippling new anti-money laundering fines" (AFR), "AUSTRAC tranche 2: Australia's toughest regulator to become its most hated?" (Independent Australia), "Insurers warn regulatory drag costing industry hundreds of millions a year" (Insurance Business), "Money laundering bill to 'burden' accountants, warns Coalition" (Accountants Daily), "Brokers 'burdened' by anti-money laundering regulation" (The Adviser), "New financial-year reforms will squeeze SMEs, HIA warns" (Broker Daily), "Anti-money laundering rules 'inflexible' for sole practitioners, small firms" (Accountants Daily). **Use this query FIRST for any FinTech Regulation topic** — it consistently produces the highest-volume counter-signal feed. Contrast with less productive AML counter-queries: `Australia+AML+CTF+compliance+burden+cost+overreach` (1KB, ~2 headlines) and `Australia+deregulation+fintech+innovation+red+tape` (6KB, ~10 headlines) — narrow AML burden terms (compliance costs + small business) outperform broad deregulation terms.

### Financial Deregulation / Red Tape Productivity Burden (NEW June 7, 2026 — 16 headlines)
```bash
curl -sL --max-time 15 -A "Mozilla/5.0" \
  "https://news.google.com/rss/search?q=Australia+financial+deregulation+red+tape+business+burden+2026&hl=en-AU&gl=AU&ceid=AU:en"
```
**Proven hits (June 7, 2026):** Liberal Party "Red Tape Emergency" formal policy agenda (primary source), AFR "Sussan Ley targets Chalmers with $44B war on red tape", Productivity tsar "red tape hairballs choking growth" (ABC/AFR), "The 'Canberra fix' killing growth" (ABC), Coalition "red tape assault" (AFR), Morrison $120M deregulation package (SmartCompany). **This query is critical for political-risk assessment** — it surfaces the deregulation agenda as a formal government-in-waiting policy platform, not just business complaining.

### CDR / Open Banking Cost Burden & Industry Backlash (NEW June 7, 2026 — 17 headlines)
```bash
curl -sL --max-time 15 -A "Mozilla/5.0" \
  "https://news.google.com/rss/search?q=Australia+CDR+open+banking+cost+compliance+burden+business+criticism&hl=en-AU&gl=AU&ceid=AU:en"
```
**Proven hits (June 7, 2026):** Capital Brief "Treasury quietly cuts CDR team in half", AFR "Banks spent $1.5B on account switching. No one is using it", Consultancy.com.au "Banks argue CDR costs too high for limited consumer uptake", SmartCompany "new open banking limits could hurt Australian fintechs", AFR "Mastercard's call to save open banking", mpamag.com "CDR is ineffective and costly", Banking Day "Fintechs tell Data Standards Body 'clarity and consistency are paramount'", Information Age "CDR to get a 'reset'", Dentons "meagre cost/benefit outcomes". **This is the strongest counter-signal query for open banking** — it surfaces both industry pushback AND government retrenchment simultaneously.

## Australian RSS Feeds (direct discovery)

These feeds occasionally carry anti-regulation / innovation-freedom pieces:
- `https://www.startupdaily.net/feed/` — Australian startup ecosystem, founder perspective
- `https://www.innovationaus.com/feed/` — Tech policy, innovation strategy criticism
- `https://www.smartcompany.com.au/feed/` — SME/business regulation perspective

## Key Anti-Regulation Voices / Sources

| Voice/Source | Position | Example Signal |
|---|---|---|
| Deepak Singh (Startup Daily) | Startup messaging strategist | "Founders losing the room on CGT" (May 26, 2026) |
| Angus Taylor / Coalition | Opposition deregulation | Repeal pledge, permanent tax cuts |
| Sussan Ley | $44B deregulation agenda | "War on red tape" |
| AFR editorial | Business press | "Australia must catch up on cutting red tape" |
| JD Vance / US administration | AI deregulation | America's AI Doctrine |
| Carnegie Endowment | Think tank | EU deregulation vs innovation tension |

## Methodology Note

These queries were discovered and validated on May 30, 2026 when Haris flagged a 35:3 pro-to-anti-regulation imbalance. The sweep found 8 new anti-regulation signals in ~15 minutes using only these RSS queries.

**CRITICAL:** Google News RSS parsing via Python `subprocess` may silently return 0 results (encoding issue with curl in subprocess). Use the `terminal` tool directly with `grep -oP '<title>(.*?)</title>'` instead. See SKILL.md pitfalls for the full `execute_code` → `terminal` guidance.
