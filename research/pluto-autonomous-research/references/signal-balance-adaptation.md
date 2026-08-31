# Signal Balance Adaptation — Per-Topic Polarity Frameworks

The Signal Balance Check (Phase 2, Step 1) requires adapting polarity dimensions to the research topic. Do NOT force regulation-specific counts onto non-regulation topics.

## Topic → Polarity Dimensions

### AI Regulation & Compliance
- **Axis 1:** pro-regulation vs anti-regulation/deregulation
- **Axis 2:** pro-intervention/government-control vs market-freedom/self-regulation
- **Axis 3:** incumbent-favoring (Big Tech compliance can afford) vs disruptor-favoring (open-source, startups)
- **Sweep threshold:** 5:1 imbalance on any axis

### Cloud & Infrastructure
- **Axis 1:** pro-cloud-growth/hyperscaler vs caution/repatriation/cost-concern
- **Axis 2:** centralized-public-cloud vs sovereign-local-cloud
- **Axis 3:** cloud-adoption-accelerating vs security-risk-slowing
- **Sweep threshold:** 5:1 imbalance on any axis
- **Example (May 31, 2026):** 8 pro-growth vs 12 caution = 0.67:1 — balanced, no sweep needed

### FinTech Regulation
- **Axis 1:** pro-regulation/compliance-tightening vs anti-regulation/burden-reduction
- **Axis 2:** incumbent-bank-favoring vs fintech-disruptor-favoring
- **Axis 3:** AML/KYC-expansion vs privacy/cost-concern
- **Axis 4 (Backlash/Political):** regulatory-expansion vs deregulation-pushback — tracks the political trajectory, not just business sentiment. A deregulation push from a government-in-waiting (e.g., Liberal Party formal red tape agenda, Productivity tsar criticism) is a DISTINCT signal from compliance-burden complaints. It indicates regulatory trajectory could reverse under a change of government.
- **Sweep threshold:** 5:1 imbalance on any axis

**Example (June 7, 2026):** 25 pro-regulation vs 12 market-freedom/deregulation = 2.1:1. Well within threshold. The counter-signal sweep confirmed a real political deregulation push backed by named sources (Liberal Party formal agenda, AFR, ABC, Productivity tsar). No further sweep needed. The CDR cost-burden query alone returned 17 substantive headlines — making it the single most productive counter-signal query for Australian fintech regulation research.

### Agentic AI & Security
- **Axis 1:** threat-escalation/alarm vs defense-innovation/optimism
- **Axis 2:** regulation-needed vs self-regulation-sufficient
- **Axis 3:** centralized-control vs decentralized-resilience
- **Sweep threshold:** 5:1 imbalance on any axis
- **Example (June 3, 2026):** 2:4 threat vs defense-innovation = 0.5:1; 1:3 regulation vs self-governance = 0.33:1 — both naturally balanced, no sweep needed. When the signal ratio is already < 1:1 on all axes, skip the counter-signal sweep and document the natural balance.

### Startup & VC Trends
- **Axis 1:** bullish/funding-growth vs bearish/correction/downturn
- **Axis 2:** Australian-ecosystem-strong vs Australian-lagging
- **Axis 3:** fintech/tech-focus vs diversified-sector
- **Sweep threshold:** 5:1 imbalance on any axis

**⚠️ Keyword-based counting is unreliable for this topic (July 3, 2026):** Words like "million", "raise", "capital", "funding", "invest", "exit" appear in factual reporting of BOTH positive and negative stories. A naive keyword count on 339 startup/VC headlines produced 183:9 (20:1 ratio) — a pure artifact. The substantive finding-level review revealed a genuine 3:3 balance (3 bearish-coded, 3 bullish-coded findings). **When the raw keyword ratio exceeds 5:1, do NOT immediately trigger a counter-signal sweep.** Instead, perform a substantive review: manually categorize the top 20-30 headlines and your synthesized findings. If the substantive balance is within 5:1, document the keyword artifact in `meta.signal_balance.note` and set `below_5_1_threshold: true`. Only trigger the sweep if BOTH the keyword count AND the substantive review show imbalance. The `note` field must explain the discrepancy: how many findings are genuinely bullish vs bearish, and why the keyword count is misleading.

## Counter-Signal Sweep Pattern

When imbalance exceeds 5:1:
1. Identify which axis is most imbalanced
2. Craft 3-4 Google News RSS queries using OPPOSITE-angle terms
3. Run the sweep — do not modify existing findings, add new counter-signals
4. Document before/after counts in `meta.signal_balance`

For regulation topics, use `references/anti-regulation-signal-sources.md` for proven query patterns. For other topics, craft queries that explicitly seek the minority viewpoint using opposition keywords.

## Why This Matters

On May 30, 2026, Haris flagged a 35:3 pro-to-anti-regulation blind spot. The pipeline was amplifying the dominant narrative (more coverage → more signals found) without checking for balance. On May 31, the adapted framework for Cloud produced a naturally balanced 0.67:1 ratio — validating that different topics have different natural signal distributions and the framework should accommodate them.
