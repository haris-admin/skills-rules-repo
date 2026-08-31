# Google News RSS Search Patterns

## Why
Google News RSS provides broad discovery without delegation failures, CAPTCHAs, or empty tool_traces. 62-100 results per query across regions. Use as discovery layer; confirm via direct publication RSS feeds when possible.

## Template
```bash
curl -sL --max-time 15 -A "Mozilla/5.0" \
  "https://news.google.com/rss/search?q=ENCODED+QUERY&hl=en-US&gl=US&ceid=US:en"
```

Parse: `re.findall(r'<item>(.*?)</item>', rss, re.DOTALL)` then extract `<title>`, `<link>`, `<pubDate>`.

## Proven Query Patterns

### AI Regulation — Enhanced Multi-Angle Pattern (validated June 25, 2026 — 376 headlines, 5 queries, 213 sources, AU locale)

Use AU locale (`hl=en-AU&gl=AU&ceid=AU:en`) for Australian AI regulatory coverage — this surfaces Gilbert+Tobin, ABC, The Guardian, The Saturday Paper, SmartCompany, Capital Brief, and law firm publications (Ashurst, Dentons, NRF, White & Case) alongside global sources (OECD, IAPP, Brookings, Reuters).

**5-angle query set (all proven sequential):**
```bash
# Angle 1: EU AI Act — Omnibus deal, enforcement, compliance deadlines
EU+AI+Act+enforcement+compliance+2026

# Angle 2: Australia AI guardrails — mandatory vs voluntary, AI Safety Institute
Australia+AI+guardrails+mandatory+regulation+2026

# Angle 3: Global AI governance — OECD, fragmentation, multi-country
AI+governance+global+OECD+regulation+2026

# Angle 4: AI safety standards — compliance frameworks, tooling market
AI+safety+standards+compliance+framework+2026

# Angle 5: Australian financial services AI — ASIC, AFSL accountability
Australian+financial+services+AI+regulation+ASIC+2026
```

**What each query surfaces:**
- `EU+AI+Act+enforcement+compliance` — Omnibus deal details (White & Case, IAPP, Dentons, Latham & Watkins), compliance deadlines (August 2, 2026 transparency rules; 2027 high-risk), Ireland's 9 enforcement authorities, Germany court tightening, Modulos CHF 8.7M raise, industry readiness gaps (~70 headlines, dominant signal)
- `Australia+AI+guardrails+mandatory` — Mandatory→voluntary pivot (ABC, The Guardian, The Saturday Paper), AI Safety Institute launch ($188K/15-month advisory body scrapped), IBM "no sweeping laws" position, Labor self-regulation framing, Home Affairs internal tension, OAIC privacy guidance, NSW workplace AI bill (~45 headlines)
- `AI+governance+global+OECD` — OECD AI Principles update, Global Safe AI Reporting Framework, 12+ countries enacting laws (South Korea, Vietnam, Kenya, China, Singapore, India), Brookings "converging on paper, diverging on ground", Lawfare 3-layer governance framework, Africa writing rules faster than noticed (~65 headlines)
- `AI+safety+standards+compliance+framework` — ISO/IEC 42001 comparisons, NIST AI RMF, compliance tooling market ($5.88B by 2035), enterprise governance frameworks (Databricks, Eltropy for credit unions), healthcare AI governance (HAARF, Nature systematic review), AI compliance cost statistics (~70 headlines)
- `Australian+financial+services+AI+regulation+ASIC` — ASIC 2026 Risk Radar (AI front and center), "year of accountability" for AFSLs (moneymanagement.com.au), APRA+ASIC joint board alarm, NRF compliance primer, AI-powered mortgage fraud, investment scams (ASIC 26-063MR), crypto+AI regulatory perimeter risks (~126 headlines from Gilbert+Tobin weekly recaps, Ashurst snapshots, broker publications)

**Signal patterns to watch for when synthesizing:**
- **EU Omnibus + "delay" / "2027" / "simplification"** — THE dominant signal. 10+ law firms publishing simultaneously means clients are demanding guidance. The compliance window extension is a BUILD signal, not a WAIT signal.
- **Australia + "voluntary" / "scrapped" / "self-regulation"** — government pivot from 2025's interventionist stance. BUT cross-reference with ASIC's independent tightening — the regulatory vacuum is being filled by the enforcement agency, not the policy arm.
- **ASIC + "accountability" / "risk radar" / "AFSL"** — financial services AI governance is the most urgent Australian regulatory signal. NRF's compliance primer is the definitive industry resource.
- **OECD + "fragmentation" / "converging" / "diverging"** — the meta-narrative. Global coordination is struggling. Multi-jurisdiction compliance mapping = market opportunity.
- **Anthropic/Mythos + "regulator" / "banking"** — live case study in frontier model regulation. APAC regulator response will set precedent.

**Confidence-tiering for this topic:**
- **high** = 3+ distinct credible publications (law firms, national broadcasters, regulatory bodies) covering the same event
- **medium** = single credible publication or OECD/think-tank analysis without cross-reference
- **low** = speculation, vendor content marketing, single-source reports

**Publishers discovered as curl-accessible (positive list for article-level detail):**
- **Law Society Journal (LSJ)** — `lsj.com.au/articles/...` — full analysis, no paywall. Verified June 11, 2026.
- **ASPI Strategist** — `aspistrategist.org.au/...` — full analysis, no paywall. Verified June 11, 2026.
- **iTWire** — `itwire.com/...` — full editorial content. Verified June 11, 2026.
- **AdNews Australia** — `adnews.com.au/...` — regulatory/policy articles, no paywall. Verified June 13, 2026.

**Publishers behind JS/paywalls (curl returns empty or stub — headline synthesis only):**
Forbes, Bloomberg, AFR, The Australian, Capital Brief, Lexology, Reuters (metered), CIO.com, Computerworld. The headline + source attribution from Google News RSS alone provides enough signal for medium-to-high confidence findings when cross-referenced across 3+ sources. Law firm publications (White & Case, Dentons, Ashurst, Gilbert+Tobin) are the most reliable primary sources — they have the strongest incentive to publish accurate, timely regulatory analysis.

### Cloud & Infrastructure — Enhanced Multi-Angle Pattern (validated June 6, 2026 — 193 headlines, 5 queries, AU locale)

Use AU locale (`hl=en-AU&gl=AU&ceid=AU:en`) for Australian cloud/infrastructure coverage — this surfaces AFR DC energy warnings, Climate Council analysis, and CSIRO AI infra stories that US locale misses.

**5-angle query set (all proven concurrent):**
```
# Angle 1: Cloud repatriation — enterprises moving workloads back from public cloud
cloud repatriation trend 2026 enterprises moving workloads private cloud

# Angle 2: Hyperscaler competition — AWS/Azure/GCP market share shifts
AWS Azure GCP cloud provider shift competition 2026

# Angle 3: FinOps maturation — cost optimization → AI unit economics
cloud cost optimization FinOps 2026 enterprises

# Angle 4: Australian data centre boom — energy, approvals, community
Australia cloud infrastructure data centre 2026

# Angle 5: Sovereign cloud & data residency — Nadella, IBM, government surge
sovereign cloud data residency Australia hyperscaler 2026
```

**What each query surfaces:**
- `cloud repatriation` — ANZ workload shifts (IT Brief Australia), Broadcom private cloud predictions, Shopify "Cloud Reset" repatriation strategy guide, Acronis workload migration analysis, Dell APJ multi-hybrid study, TechRepublic enterprise IT trends
- `AWS Azure GCP competition` — VentureBeat Microsoft/OpenAI deal restructure (OpenAI free on AWS/GCP), Statista Big Three dominance reports, CRN Q1 market share, Google Wiz acquisition EU cloud sovereignty questions, CIO.com "AI gravity" analysis
- `cloud cost optimization` — Flexera 2026 State of the Cloud (cost-cutting→value pivot), SiliconANGLE cloud cost unlocking AI economics, TechTarget FinOps maturation, MSN "AI unit economics replace FinOps", Fortune Business Insights FinOps market forecast
- `Australia cloud infra` — IREN 800MW Bundey campus (W.Media), AFR Victoria DC energy demand doubling, Climate Council "do data centres right", The Guardian Perth DC community opposition, CSIRO real-time AI infrastructure, Motley Fool ASX DC boom stocks, US Studies Centre grid impact
- `sovereign cloud` — Computerworld Nadella sovereignty redefinition, Microsoft A$25B AU 140% cloud push, IBM sovereign multi-cloud stack, Australian Government Cloud sovereign surge report, IDM Magazine sovereignty challenges, Sebastian Barros "telcos have a right to play"

**Signal patterns to watch for when synthesizing:**
- **Repatriation + "private cloud" + "cost"** — multi-source confirmed trend (high confidence). Watch for vendor blog patterns (Broadcom, Shopify, Acronis all published week of June 1-5 2026 — coordinated narrative?)
- **"FinOps" + "AI unit economics"** — the 2026 pivot from cost-cutting to value-driven cloud strategy. Flexera report is the anchor data point.
- **OpenAI + "AWS" / "GCP" / "exclusive deal"** — partnership restructure is a seismic market signal. VentureBeat behind Vercel captcha but cross-referenced by CRN/Statista cloud market share data.
- **"Nadella" + "sovereignty"** — Microsoft redefining the term for AI era is a regulatory framing battle. IBM's counter-position (fully sovereign software stack) provides competitive contrast.
- **"data centre" + "energy" / "community opposition" / "grid"** — Australia-specific infrastructure constraint signals. High confidence due to AFR, The Guardian, Climate Council multi-source cross-reference.

**Publishers discovered as JS-rendered (not curl-accessible for article-level detail):** CIO.com (214KB shell), Computerworld (216KB shell), W.Media (183KB shell). All three return large HTML files but 0 extractable paragraphs — content is JavaScript-rendered. Use RSS headline synthesis only for these sources.

**Signal Evolution (June 26, 2026 — 286 headlines, 5 queries, 43+ unique sources per angle):**

As of late June 2026, the Cloud topic has shifted structurally. The original June 6 query set (repatriation→hyperscaler competition→FinOps→data centres→sovereign cloud) captured a market in tension. By June 26, the balance has resolved decisively:

- **Sovereign cloud is now the dominant signal by volume (78 items, 43 sources vs 10-76 for other angles).** SAP GA (70 jobs), Microsoft in-country Copilot, Equinix network enforcement, Macquarie $200m govt, Yurika/RackCorp, Commvault Geo Shield, Rubrik, SUSE self-assessment, SCX+SambaNova ASIC-powered cloud, HPE+2degrees — all launching in Q2-Q3 2026. This is no longer one theme among many; it IS the cloud story in Australia.
- **Sovereign AI infrastructure recognised as new institutional asset class** — A&O Shearman landmark analysis, Gilbert+Tobin "race to prioritisation", IDC "high cost of sovereignty" analysis. Microsoft A$25B Australia AI bet.
- **Gartner warns of regional AI stack lock-in** — the sole high-credibility counter-signal to the sovereign cloud boom. IDC confirms sovereignty increases costs and limits portability.
- **Multi-cloud mainstreaming** confirmed — AWS 31% vs Azure 24% with 75% cost gap. "Just Pick AWS" now considered bad advice. FinOps maturing to CFO-level priority ($26.91B by 2030).
- **Repatriation discourse growing but not yet revenue-visible** — AWS acknowledges trend; Gartner says not widespread. Colocation growing faster than on-prem returns. Inference economics may shift optimal hosting.

**Signal evolution (July 5, 2026 — 262 headlines, 126 sources, AU locale):**

The June 26 structural patterns continue: sovereign cloud dominance persists (Australia-specific queries produced 152 of 262 headlines), repatriation discourse is maturing from discourse to action (InfoWorld "hits its stride", BBC "rainy days", GEICO case study, Shopify repatriation guide), and the FinOps market is consolidating at $41.89B projected. The signal balance has tightened to 1:1 (3 pro-growth vs 3 caution/cost) — more balanced than June 26's 13:8. Cloud & Infrastructure is naturally self-balancing: the repatriation and cost-concern narratives are inherently strong enough that counter-sweeps are unnecessary. Key new signals since June 26: Australia's $73.3B green-powered 4-city AI DC project (Startup Daily), Oracle 30,000 layoffs to fund AI data centers, and Microsoft eliminating Azure egress fees in competitive response to repatriation pressure.

**Proven concise query set (June 26, 2026 — 5 queries, all AU locale):**
```bash
cloud+repatriation+trends+AWS+datacenter+2026
cloud+cost+optimization+FinOps+multicloud+2026
AWS+Azure+GCP+market+share+enterprise+cloud+2026
Australia+cloud+sovereign+data+regulatory+2026
edge+computing+cloud+infrastructure+hybrid+2026
```

**Signal balance for this topic (June 26 validation):** 13:8 pro-growth vs caution (below 5:1 threshold). Dimensions: pro_growth_hyperscaler vs caution_repatriation_cost_concern. Sovereign cloud launches and AI-driven expansion outnumber lock-in warnings and repatriation discourse but not overwhelmingly. The balance is credible without counter-sweep.

### FinTech Regulation — Enhanced Multi-Angle Pattern (validated June 12, 2026 — 238 headlines, 5 queries, 93 sources, AU locale)

Use AU locale (`hl=en-AU&gl=AU&ceid=AU:en`) for Australian fintech regulatory coverage — this surfaces LSJ, Startup Daily, SmartCompany, ABC, AFR, Australian Broker News, and law firm publications (Gilbert+Tobin, Dentons, NRF, Ashurst, HSF) that US locale misses.

**5-angle query set (all proven sequential — the `&` backgrounding operator is blocked by Hermes security scanner):**
```bash
# Angle 1: AML/CTF Tranche 2 — AUSTRAC compliance deadlines, Program Starter Kits
AUSTRAC+AML+Tranche+2+compliance+Australia+2026

# Angle 2: Digital assets & crypto — AFSL licensing, ASIC roadmap
Australia+digital+assets+cryptocurrency+ASIC+2026

# Angle 3: ASIC AI in financial services — risk radar, compliance primers
ASIC+AI+financial+services+regulation+Australia+2026

# Angle 4: PSP/payments licensing — Treasury Tranche 1 consultation
Australia+PSP+payment+provider+licensing+reform

# Angle 5: CGT/startup policy — Senate inquiry, ESOP impact
Australia+CGT+startup+Senate+inquiry+2026
```

**What each query surfaces:**
- `AUSTRAC+AML+Tranche+2` — LSJ Program Starter Kit analysis, Dentons transitional rules, Gilbert+Tobin AML/CTF reform hub, NSW Small Business Commissioner warnings, PEXA Clear property AML tool, OAIC privacy guidance for reporting entities, FinTech Global deadline reporting (~34 headlines)
- `digital+assets+cryptocurrency+ASIC` — Digital assets bill passage (CoinDesk, LSJ), Coinbase AFSL licence, ASIC roadmap (Lexology), Norton Rose Fulbright dispute review, crypto scam warnings (ABC, CoinGeek), Finance Magnates 10% penalty analysis (~75 headlines)
- `ASIC+AI+financial+services` — NRF compliance primer, Australian Broker News risk radar, Gilbert+Tobin weekly regulatory recaps, Dentons/Ashurst boardroom briefs, ifa.com.au "tougher in 2026" analysis, ASIC "lost generation" warning (~71 headlines)
- `PSP+payment+provider+licensing` — Treasury Tranche 1 consultation (Gilbert+Tobin, Ashurst, Dentons, HSF, NRF, PwC), surcharging ban prep (Westpac IQ), payments modernisation regime, Colin Biggers & Paisley licence overview (~16 headlines, highest signal density)
- `CGT+startup+Senate+inquiry` — Senate hearings June 15-19/findings June 19 (Startup Daily, SmartCompany, ABC, AFR), Labor narrow carve-outs for tech, Greens demands, "toxic" bill analysis, submissions deadline June 9 (~42 headlines)

**Signal patterns to watch for when synthesizing:**
- **AML Tranche 2 + "July 1" / "deadline"** — time-sensitive compliance event. Every law firm publication is a signal of client demand. LSJ and Dentons articles are curl-accessible for full-text extraction.
- **Digital assets + "AFSL" / "licence"** — regulatory framework now law. Coinbase getting first AFSL is the anchor event. Multiple international crypto publications confirm global attention on Australia's approach.
- **ASIC + "risk radar" / "AI"** — ASIC explicitly naming AI as 2026 priority. NRF's compliance primer is the definitive industry resource. Gilbert+Tobin's weekly recaps provide ongoing signal.
- **PSP + "Tranche 1" / "consultation"** — draft legislation stage means input window is open. Every law firm publishing means clients are asking. PwC's "prepare now" framing is the strongest signal.
- **CGT + "Senate" / "June 19"** — next week is the critical decision window. Startup Daily's 17-page submission is the most detailed source. Labor's "narrow carve-outs" language signals possible compromise.

**Curl-accessible publishers for FinTech Regulation (positive list):**
- **Law Society Journal (LSJ)** — `lsj.com.au/articles/...` — full analysis, no paywall. Verified June 11 + June 12, 2026 (AUSTRAC Program Starter Kits).
- **Startup Daily** — `startupdaily.net/...` — full content, ~800KB. Verified June 12, 2026 (CGT Senate submission).
- **SmartCompany** — `smartcompany.com.au/...` — metered, sometimes full content. ~720KB when accessible. Verified June 12, 2026.
- **ASPI Strategist** — `aspistrategist.org.au/...` — full analysis, no paywall. Verified June 11, 2026.
- **iTWire** — `itwire.com/...` — full editorial content. Verified June 11, 2026.

**Publishers behind JS/paywalls (curl returns empty or stub):** AFR, The Australian, Capital Brief, Lexology, FinTech Global, Finance Magnates, CoinDesk, TradingView. Use headline synthesis only for these sources — the headline + source attribution alone provides enough signal for medium-confidence findings when cross-referenced across 3+ sources.

### Agentic AI & Security — Enhanced Multi-Angle Pattern (validated July 2, 2026 — 370 headlines, 164 sources, AU locale)

Use AU locale (`hl=en-AU&gl=AU&ceid=AU:en`) for agentic AI security coverage — this surfaces SecurityBrief Australia, IT Brief Australia, Ping Identity, and local vendor coverage alongside global sources (Microsoft, NIST, OWASP, IBM, VentureBeat, Help Net Security, Infosecurity Magazine, Dark Reading).

**5-angle query set (all proven sequential):**
```bash
# Angle 1: Multi-agent security — attack surfaces, defenses, Microsoft taxonomy
agentic+AI+multi-agent+security+2026

# Angle 2: Red teaming & vulnerabilities — prompt injection, RCE, exploitation
AI+agent+vulnerabilities+red+teaming+2026

# Angle 3: Governance & standards — NIST, OWASP, multi-agency guidance
LLM+agent+orchestration+safety+governance

# Angle 4: Enterprise deployment risks — identity, authorization, adoption blockers
autonomous+AI+agents+enterprise+security+risks

# Angle 5: Frameworks & best practices — OWASP maturity, AEGIS, DASF, Agent Threat Rules
AI+agent+framework+security+best+practices+2026
```

**What each query surfaces:**
- `agentic+AI+multi-agent+security` — Microsoft failure taxonomy (year of red teaming), multi-agent defense system topping Anthropic Mythos benchmarks, Infosys layered security strategy, KnowBe4 security overview, Mayer Brown multi-agency guidance, InfoWorld best practices (~97KB, dominant signals from Microsoft/enterprise sources)
- `AI+agent+vulnerabilities+red+teaming` — AutoJack single-page RCE (Microsoft), AI red teaming agents evolution (csoonline, Help Net Security), zero-click human-in-the-loop bypass (CyberSecurityNews), coding agent secret leaks via prompt injection (VentureBeat), Snyk OpenClaw shell access warning, OpenAI Daybreak launch, red team tool vulnerabilities (API key exfiltration) (~101KB)
- `LLM+agent+orchestration+safety+governance` — NIST AI Agent Standards RFI (IT Brew, Pillsbury), OWASP Agentic AI Security Maturity Framework (Infosecurity Magazine), EY governance frameworks for enterprises, Forrester AEGIS framework, Databricks DASF v3.0, America First Policy Institute adoption acceleration paper (~81KB, highest governance signal density)
- `autonomous+AI+agents+enterprise+security+risks` — IBM identity problem at heart of agentic security, RSAC 2026 5 agent identity frameworks + 3 critical gaps (VentureBeat), enterprise adoption complexity (Help Net Security), Recorded Future emerging risks, ZeroID open-source identity platform, Palo Alto Networks secure agent capabilities (~129KB, largest file — enterprise coverage dominates)
- `AI+agent+framework+security+best+practices` — OWASP Agentic Research Council formation, Agent Threat Rules open detection format (Help Net Security), AEGIS enterprise guardrails, DASF v3.0, AWS security scoping, Ping Identity agent authorization risks (SecurityBrief Australia), Proofpoint AI intent security (~91KB)

**Signal patterns to watch for when synthesizing:**
- **Microsoft + "failure taxonomy" / "AutoJack" / "open-sourced"** — Microsoft is the dominant thought leader in agentic AI security. Their taxonomy + tools release + multi-agent defense benchmark all point to an emerging platform play. Every Microsoft headline is cross-referenced by Help Net Security, Dark Reading, and VentureBeat — high confidence.
- **NIST + "RFI" / "standards"** — the standards clock is ticking. 12-18 month timeline means agentic AI governance frameworks will be formalized by late 2027. Any AU standard should align with NIST to avoid fragmentation.
- **OWASP + "maturity framework" / "research council"** — OWASP's entry into agentic AI mirrors their web application security history (Top 10 became industry standard). The maturity framework is a leading indicator of formalized compliance requirements.
- **"identity" + "gap" / "crisis" / "framework"** — the recurring theme across enterprise, governance, and vulnerability queries. Agent identity (non-human actors with delegated authority) is the unsolved problem. RSAC's 3 gaps (cross-org trust, delegation audit, credential revocation) are the roadmap.
- **"prompt injection" + "RCE" / "shell" / "secret leak"** — the attack vector is maturing from theoretical to demonstrated. AutoJack (single page → RCE) and coding agent secret leaks are the concrete examples. Snyk's explicit OpenClaw warning makes this directly relevant to Haris's agent fleet.
- **Australian vendor coverage + no regulator** — Ping Identity, F5, Proofpoint, BeyondTrust, TrendAI all shipping agentic security products to AU market. But ASIC/AUSTRAC/eSafety silent. Gap = opportunity.

**Confidence-tiering for this topic:**
- **high** = 3+ distinct credible publications (Microsoft, NIST, OWASP, IBM, VentureBeat) covering the same event
- **medium** = single credible publication or vendor content with cross-reference potential
- **low** = speculation, vendor marketing content, single-source without verification

**Signal balance for this topic:** Use threat-escalation vs defense-innovation as polarity dimensions. Threat-escalation = vulnerabilities found, attacks demonstrated, gaps identified. Defense-innovation = frameworks published, tools released, benchmarks topped, standards launched. July 2 validation: 2:4 (below 5:1 threshold). Balanced enough to be credible without counter-sweep.

**Publishers discovered as key sources for this topic:**
- **Help Net Security** — consistently the highest-volume source (24 headlines July 2). Covers product launches, week-in-review, and analysis. Not curl-accessible but headline synthesis provides rich signal.
- **Microsoft** — primary source for red teaming, failure taxonomy, and AutoJack. 21 headlines. Official publications are curl-accessible.
- **VentureBeat** — RSAC coverage, vendor analysis. JS-rendered but headline attribution is reliable.
- **SecurityBrief Australia / IT Brief Australia** — Australian-specific vendor and security coverage. Curl-accessible.
- **Infosecurity Magazine** — OWASP coverage, Infosecurity Europe reporting. Not curl-accessible.
- **Palo Alto Networks, IBM, AWS** — vendor frameworks and analysis. Official blogs are curl-accessible.

**Legacy query sets (kept for historical reference):**

Primary (validated June 3, 2026 — 286 headlines):
```
agentic AI security threats vulnerability 2026
multi-agent AI system security red teaming
AI agent prompt injection tool poisoning safeguard
autonomous AI agent governance safety alignment
LLM agent security supply chain attack defense
```

Alternative (validated June 13, 2026 — 330 headlines, 172 sources):
```
multi-agent AI security vulnerabilities 2026
AI agent red-teaming adversarial attacks
autonomous AI agent safety regulation guardrails
LLM agent security OWASP prompt injection
AI agent orchestration security best practices
```

**Key difference between old and new query sets:** The July 2026 set shifts from security-general queries toward specific attack vectors (red teaming, prompt injection), governance artifacts (NIST RFI, OWASP frameworks), and enterprise deployment blockers (identity crisis, adoption complexity). This reflects the topic's maturation from broad threat awareness to concrete standards, tools, and deployment patterns.

**Article-level queries for deeper signal:**
```
OpenClaw security risks agentic AI OR autonomous AI
Snyk ToxicSkills agent skills supply chain prompt injection
Sysdig LLM agent intrusion in-the-wild
```

**Cross-file article search technique:** When you see an interesting headline in the aggregated extraction output and want to find its source, search across all `/tmp/gn_*.xml` files for that title using Python's `re.findall(r'<item>(.*?)</item>', data, re.DOTALL)`, then extract the `<link>` for that specific item. Google News RSS links can't be curled (HTTP 400), but the publisher attribution and headline alone provide enough signal for medium-confidence findings when cross-referenced.

**Publisher URL guessing:** Some niche publishers (MarkTechPost, Intelligent Living) use slug-based URL patterns. For MarkTechPost: `https://www.marktechpost.com/YYYY/MM/DD/slugified-title/`. Try this when the Google News link is unfetchable — success rate is ~50% and pages can be 280KB+. Note that many publisher pages are JS-rendered (React/Gatsby) and curl returns navigation-only content even when the URL resolves.

### Startup & VC — Enhanced Multi-Angle Pattern (validated June 4, 2026 — 62 headlines, 5 queries, 12+ publications)

Use AU locale (`hl=en-AU&gl=AU&ceid=AU:en`) for Australian startup/VC coverage — this surfaces AFR, SmartCompany, Startup Daily, Capital Brief, FinTech Global, and Business News Australia which US locale misses.

```bash
# General ecosystem + funding
Australian+startup+funding+venture+capital+2026
# Fintech-specific funding
fintech+funding+Australia+2026
# VC investment trends + ecosystem health
Australian+VC+investment+startup+ecosystem
# CGT/ESOP policy (ExitLens AU relevance — live Senate inquiry)
Australia+CGT+ESOP+startup+Senate+inquiry
# IPO and exit market
ASX+tech+IPO+Australia+startup+listing
```

**What each query surfaces:**
- `startup+funding+venture+capital` — aggregate funding figures ($5.1B), deal count trends, weekly roundups (SmartCompany, Startup Daily), government VC policy (Industry Minister statements)
- `fintech+funding+Australia` — fintech-specific deals, ASIC innovation stance, FinTech Australia policy warnings, Airwallex IPO timelines, international expansion (Vietnam fintech ties)
- `VC+investment+startup+ecosystem` — VC fund launches (FB Ventures Fund of Funds), unicorn creation metrics per VC dollar, women in VC trends, Sydney startup rankings, US founders seeking Australian investment
- `CGT+ESOP+startup+Senate+inquiry` — targeted policy query hitting Capital Brief, AFR coverage of CGT changes affecting ESOPs, industry minister statements. This is a low-volume query (2-5 results) but high-signal — every result is directly relevant to ExitLens AU thesis
- `tech+IPO+Australia+startup+listing` — ASX IPO pipeline (Firmus $7B, Sea Forest, Airtasker), exit values report (AFR: $US3.5B, +62%), ASX rethink analysis (Capital Brief)

**Signal patterns to watch for when synthesizing:**
- **$5.1B + deal count decline** — funding concentration (high, multiple sources confirmed)
- **"missing middle"** — growth capital gap, appears in both SmartCompany and Startup Daily
- **CGT/ESOP + "Husic" + "uncertainty"** — live policy debate, appears in Capital Brief
- **"IPO" + "revival" / "debut" / "soars"** — ASX reopening with quality filter
- **"FinTech Australia" + "warns"** — industry body raising red flags

### Startup & VC — July 13 Refresh (validated July 13, 2026 — 355 headlines, 5 queries, 93 sources, AU locale)

The June 29 set produced 289 headlines; the July 13 set produced 355 (+23%). Key improvement: adding dedicated IPO/exit market and ESOP angles surfaced unique content the earlier set missed — Canva IPO coverage (Fortune, Crunchbase, The Guardian), ASX IPO surge (investordaily.com.au, Ashurst), and BDO ESS compliance reporting. The counter-sweep confirmed that bearish signals for this topic are overwhelmingly global (US AI bubble concerns, Reuters tech selloff) — not AU-specific startup decline. One counter-sweep is sufficient; do not loop.

**5-angle query set (all proven sequential, AU locale):**
```bash
# Angle 1: Ecosystem + fintech funding — broad discovery
Australia+startup+ecosystem+funding+fintech+2026

# Angle 2: VC investment — deal flow, fund launches
Australia+venture+capital+investment+startup+funding+2026

# Angle 3: CGT reform — Senate inquiry, carve-outs (ExitLens AU critical)
Australia+CGT+capital+gains+tax+reform+startup+2026

# Angle 4: IPO/exit market — Canva, ASX pipeline, dual-track exits (NEW — not in June 29 set)
Australian+tech+startups+IPO+exit+market+2026

# Angle 5: ESOP policy — employee share schemes, ESS compliance (NEW — not in June 29 set)
Australia+ESOP+employee+share+scheme+government+2026
```

**Counter-sweep queries (bearish/correction — for signal balance when ratio > 5:1):**
```bash
Australia+startup+funding+decline+correction+slowdown+2026
Australia+venture+capital+bubble+risk+overvalued+2026
Australian+startup+layoffs+failure+bankruptcy+2026
```
**Counter-sweep result (July 13):** All 3 returned global AI bubble / US market concerns (The Atlantic, Reuters, Morningstar, CommBank), NOT AU-specific startup decline. This confirms topic skew — the Australian ecosystem was genuinely bullish in July 2026 (Canva IPO imminent, Eucalyptus $1B exit, Square Peg $1.1B returns, AI $5B funding boom). One sweep documented in `signal_balance.note` is sufficient; do not loop.

**Signal balance (July 13):** 97:11 bullish:bearish (8.8:1). Above threshold but confirmed as topic skew post one counter-sweep. Dimensions: bullish_funding vs bearish_correction.

**What each query surfaces (July 13 results):**
- `ecosystem+funding+fintech` (79 headlines, 93 sources total) — Startup Daily cheque-in roundups ($193M/week, $393.3M/quarter), Airwallex $100K AI founder grants, Pay.com.au $633M valuation, Adelaide VC Eastend Ventures $5M from Funds SA, Peter Thiel backing Halter at $2B, VC gender gap analysis, Startup Muster 2026 revival
- `venture+capital+investment+startup+funding` (77 headlines) — Square Peg $1.1B returns + 6th fund, Australia world's fastest-growing VC ecosystem, Eucalyptus billion-dollar exit, Blackbird/Barrenjoey winners, Marbruck secretive VC fund, "missing middle" investment architecture gap, Go1 cofounder exit after 10 years
- `CGT+capital+gains+tax+reform+startup` (82 headlines) — Chalmers/Husic carve-out pledges (AFR, Capital Brief), Senate committee hearings, "catastrophic" warnings (AFR), "disastrous" (ABC), $500M annual compliance "shitshow" (Startup Daily), NZ zero-CGT comparison, Tech Council outlier warning, Labor tightrope on tax overhaul, biotech sector alarm, Labor ignoring call for pause
- `tech+startups+IPO+exit+market` (72 headlines) — Canva IPO impending + employee share sale minting millionaires (Fortune, Crunchbase), ASX bracing for second-half surge (investordaily.com.au), dual-track exits making comeback (AFR/HSFK), hectocorn companies floating in 2026 (The Guardian), Guzman y Gomez founder rues US exit mistakes, secondaries market as liquidity solution (Startup Daily), family offices positioning for IPO rebound (Crain Currency)
- `ESOP+employee+share+scheme+government` (45 headlines) — BDO ESS reporting obligations compliance, PwC Federal Budget investment analysis, William Buck dealmaking insights, Budget India ESOP tax certainty demands, M&A outlook 2026 (PwC, Bain, KPMG Venture Pulse Q4 2025)

**Signal patterns (July 13):**
- **CGT + "carve-out" + "Chalmers pledges"** — THE dominant narrative. Government backpedaling from initial position. Multiple credible sources confirming undefined carve-outs. ExitLens AU directly impacted (critical).
- **Canva + "IPO" / "hectocorn" / "employee share sale"** — impending liquidity event that will define Australian tech ecosystem maturity. Fortune + Crunchbase + The Guardian multi-source confirmation. Secondaries market + dual-track exits as complementary trend.
- **Eucalyptus + "billion" / "Square Peg" / "$1.1B"** — exit returns validating Australian VC model, but "patient capital" framing suggests long holds are the new normal.
- **"Missing middle" + "investment architecture"** — structural gap persists despite record funding. R&D reforms praised but CGT overshadows.
- **AI + "$5B" / "funding boom"** — AI startups attracting disproportionate capital. Non-AI startups facing cash crunch (CFOtech Australia).

### Startup & VC — Refresh (validated June 29, 2026 — 289 headlines, 5 queries, 50+ sources, AU locale)

The June 4 query set was validated at 62 headlines. The refined June 29 set yields 289 headlines — a 4.7× improvement by shifting from generic ecosystem queries to specific event-driven angles (CGT Senate deal, Airwallex $11B raise, Blackbird/Baseten $13B, SA Budget R&D fund, gender gap).

**5-angle query set (all proven sequential, AU locale):**
```bash
# Angle 1: General startup funding + VC — captures broad ecosystem funding
Australia+startup+funding+venture+capital+2026

# Angle 2: CGT reform — Senate inquiry, carve-outs, founder backlash (ExitLens AU critical)
Australia+CGT+startup+Senate+inquiry+reform+2026

# Angle 3: Fintech-specific — Airwallex, Shaype, Earlytrade, NAB Banked deals
Australian+fintech+funding+investment+rounds+2026

# Angle 4: Ecosystem + innovation trends — deep tech, SA R&D, government programs
Australia+startup+ecosystem+tech+innovation+trends+2026

# Angle 5: VC deals + ESOP policy — low volume (9 headlines) but high signal density
Australian+venture+capital+deals+ESOP+policy+2026
```

**What each query surfaces (June 29 results):**
- `startup+funding+venture+capital` (77 headlines) — Forbes Australia "VC fastest growing but pool drying", Capital Brief gender gap, Baseten $13B/Blackbird record bet (Reuters), SA Budget $50M R&D fund (SmartCompany), Fishburners $250B warning (Startup Daily), Government VC cap limits raised, Eucalyptus billion-dollar exit
- `CGT+startup+Senate+inquiry+reform` (48 headlines) — Labor-Greens CGT deal passes (ABC), fast-tracked Senate report (SmartCompany), Albanese "generous" exemptions (The Guardian), founder flight fears (InDaily), Startup Daily Senate testimony, Chalmers carve-out pledge (AFR), $500M annual compliance "shitshow" (Startup Daily), Tech Council outlier warning
- `fintech+funding+investment+rounds` (78 headlines) — Airwallex $11B valuation + AI pivot (AFR, CNBC), Shaype A$33M Series C (FF News), Earlytrade $14.2M agentic AI raise (SmartCompany), NAB acquires Banked, 4 startups raised $87.3M week (SmartCompany), Up Bank alumni $4M AI finance raise (Startup Daily), $5.1B 2025 funding (Forbes Australia)
- `startup+ecosystem+tech+innovation+trends` (77 headlines) — Deep tech as Australia's future (Forbes Australia), SA budget startups (Investor Strategy News), BHP Xplor 2026 mining accelerator, EdTech + AI market reports, death tech/decarbonization/foodtech trend pieces
- `venture+capital+deals+ESOP+policy` (9 headlines — **lowest volume, highest signal density**) — PwC Budget investment analysis, CGT "disastrous" for startups (ABC), Husic quelling uncertainty (Capital Brief), "catastrophic" startup warnings (AFR), Eucalyptus exit winners (Capital Brief, Startup Daily), Gilbert+Tobin VC report

**Signal patterns to watch for when synthesizing (June 29):**
- **CGT + "deal" / "passes" / "carve-out undefined"** — THE dominant narrative. Multiple credible sources (ABC, The Guardian, AFR, SmartCompany, Startup Daily, Capital Brief) confirm the deal is done but startup protections are NOT defined. ExitLens AU directly impacted.
- **Airwallex + "$11B" / "AI agents" / "no IPO"** — Australian fintech choosing AI over public markets is a structural signal for the entire ecosystem. PayLicence AU thesis validated.
- **Blackbird + "Baseten" / "$13B"** — Australian VC making its largest-ever bet on AI infrastructure. TokenPilot AU: DLT/AFSL demand from AI-native fintechs.
- **"$500M annual shitshow"** — accountants' compliance burden warning. Repeated across Startup Daily and SmartCompany. Directly relevant to ExitLens AU's CGT advisory positioning.
- **Gender gap + "2%" / "capital warning"** — persists despite record funding. Capital Brief + Women's Agenda multi-source confirmation.
- **SA Budget $50M R&D** — state-level competition for startup talent intensifying. CloudProof AU opportunity.

**Signal balance (June 29):** 12 bullish vs 7 bearish (1.7:1), below 5:1 threshold. Dimensions: bullish_funding vs bearish_correction. Balanced enough to be credible without counter-sweep.

**What changed from June 4 to June 29:**
- Query specificity improved: generic "ecosystem" queries replaced with event-driven angles (CGT Senate deal, specific funding rounds)
- CGT reform dominated — was nascent June 4, now post-deal with undefined carve-outs
- Airwallex/Baseten megadeals appeared — not present in June 4 headlines
- Volume: 62 → 289 headlines (4.7× improvement)

## Competitive & Market Research Queries

Use these patterns when doing deep-dive investigations (competitor mapping, market landscape, regulatory impact assessment). Always use `gl=AU` for Australian-market queries.

### Competitor Discovery
```bash
# Single-competitor deep dive
"COMPETITOR_NAME+compliance+platform+AUSTRAC"

# Multi-competitor landscape sweep
"AMLHive+OR+FrankieOne+OR+ComplyAdvantage+Australian+compliance+SME"

# Category-wide discovery
"Australian+regtech+compliance+platform+SME+2026"
```

### Regulation-Specific (by deadline/event)
```bash
"AUSTRAC+Tranche+2+compliance+deadline+2026"
"AUSTRAC+Program+Starter+Kit+Tranche+2+lawyers+accountants"
"AUSTRAC+risk+snapshot+2026"
```

### Sector-Specific Compliance Readiness
```bash
# Real estate
"Tranche+2+real+estate+compliance+AUSTRAC+deadline+2026"

# Legal
"Tranche+2+legal+firms+AML+CTF+compliance+Australia"

# Accounting
"AUSTRAC+Tranche+2+accountants+SMSF+compliance"
```

### Pattern: Competitor → Validation Signal
When a competitor is found actively marketing (e.g., APLYiD in Elite Agent, May 2026), it validates market demand. Search for their coverage:
```bash
"COMPETITOR_NAME+compliance+platform"           # General presence
"COMPETITOR_NAME+AUSTRAC"                       # Regulatory positioning
"COMPETITOR_NAME+partnership+OR+funding"        # Growth signals
```

## Limitations
- Article links (`news.google.com/rss/articles/...`) redirect to publishers but return HTTP 400 when followed with `curl -L`. Use headlines only; fetch confirming articles from publisher RSS feeds.
- Results are Google News-ranked; relevance drops after ~20 items per query.
- Use `&hl=en-US&gl=US&ceid=US:en` for English results. Change `gl=` for region-specific (e.g., `gl=AU` for Australian sources).
- Competitive queries often return few results (<10). This is expected — the AU regtech market is nascent. Low result counts are themselves a signal: greenfield opportunity.
